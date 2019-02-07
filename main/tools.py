from pandas import DataFrame, Series, concat
from linearmodels.panel.results import PanelModelComparison
from linearmodels.compat.statsmodels import Summary
from linearmodels.iv.results import default_txt_fmt, stub_concat, table_concat
from linearmodels.utility import (_ModelComparison, _SummaryStr, _str, pval_format)
from statsmodels.iolib.summary import SimpleTable, fmt_2cols, fmt_params

class MyPanelModelComparison(PanelModelComparison):

    def __init__(self, results):
        super(MyPanelModelComparison, self).__init__(results)
        
    @property
    def summary(self):
        """Summary table of model comparison"""
        smry = Summary()
        models = list(self._results.keys())
        title = 'Model Comparison'
        stubs = ['Dep. Variable', 'Estimator', 'No. Observations', 'Cov. Est.', 'R-squared',
                 'R-Squared (Within)', 'R-Squared (Between)', 'R-Squared (Overall)',
                 'F-statistic', 'P-value (F-stat)']
        dep_name = {}
        for key in self._results:
            dep_name[key] = self._results[key].model.dependent.vars[0]
        dep_name = Series(dep_name)

        vals = concat([dep_name, self.estimator_method, self.nobs, self.cov_estimator,
                       self.rsquared, self.rsquared_within, self.rsquared_between,
                       self.rsquared_overall, self.f_statistic], 1)
        vals = [[i for i in v] for v in vals.T.values]
        vals[2] = [str(v) for v in vals[2]]
        for i in range(4, len(vals)):
            f = _str
            if i == 9:
                f = pval_format
            vals[i] = [f(v) for v in vals[i]]

        params = self.params
        std_errors = self._get_series_property('std_errors')
        params_fmt = []
        params_stub = []
        for i in range(len(params)):
            params_fmt.append([_str(round(v, 3))[:-1] for v in params.values[i]])
            std_errors_fmt = []
            for v in std_errors.values[i]:
                v_str = _str(round(v, 3))[:-1]
                v_str = '({0})'.format(v_str) if v_str.strip() else v_str
                std_errors_fmt.append(v_str)
            params_fmt.append(std_errors_fmt)
            params_stub.append(params.index[i])
            params_stub.append(' ')

        vals = table_concat((vals, params_fmt))
        stubs = stub_concat((stubs, params_stub))

        all_effects = []
        for key in self._results:
            res = self._results[key]
            effects = getattr(res, 'included_effects', [])
            all_effects.append(effects)

        neffect = max(map(lambda l: len(l), all_effects))
        effects = []
        effects_stub = ['Effects']
        for i in range(neffect):
            if i > 0:
                effects_stub.append('')
            row = []
            for j in range(len(self._results)):
                effect = all_effects[j]
                if len(effect) > i:
                    row.append(effect[i])
                else:
                    row.append('')
            effects.append(row)
        if effects:
            vals = table_concat((vals, effects))
            stubs = stub_concat((stubs, effects_stub))

        txt_fmt = default_txt_fmt.copy()
        txt_fmt['data_aligns'] = 'r'
        txt_fmt['header_align'] = 'r'

        table = SimpleTable(vals, headers=models, title=title, stubs=stubs, txt_fmt=txt_fmt)
        smry.tables.append(table)
        return smry
  
