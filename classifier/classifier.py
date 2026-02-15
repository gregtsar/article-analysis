import glob
import pandas as pd

def import_dataset(filename=None,encoding=None):
    """
    Imports dataset in csv format
    """
    file = glob.glob('scrapers/data/'+filename+'.csv')
    file = ' '.join(file)
    with open(file, encoding='utf-8') as inputfile:
        df = pd.read_csv('scrapers/data/'+filename+'.csv')
    return df

def main():

    df = import_dataset('lifo_articles')
    df = df.reset_index()  # make sure indexes pair with number of rows

    for index, row in df.iterrows():

        text = row['Article']






