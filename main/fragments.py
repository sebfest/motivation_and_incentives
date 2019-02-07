import os
import pandas as pd

FRAGMENTS = os.path.join(os.getcwd(), 'source', 'fragments.xlsx')

def get_correct_fragments():
    """
    Prepare dataframe with correct solutions for fragments
    
    return: A pandas dataframe object
    """
    df = pd.read_excel(
        FRAGMENTS,
        header=None,
        names=["Keyword", "Solution"],
        encode='utf8',
    )
    df = df.applymap(lambda x: x.strip())
    df = df.drop('Keyword', axis=1)
    return df
