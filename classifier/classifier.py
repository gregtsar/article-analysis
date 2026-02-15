import os
from dotenv import load_dotenv
import pandas as pd
import requests
import json

# Assumes run from project root (e.g. PyCharm run config with Working directory = project root)


def import_dataset(filename=None, encoding=None):
    """
    Imports dataset in csv format from scrapers/data/
    """
    csv_path = os.path.join('scrapers', 'data', filename + '_articles.csv')
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Dataset not found: {csv_path}")
    with open(csv_path, encoding=encoding or 'utf-8') as inputfile:
        df = pd.read_csv(inputfile)
    return df


def main():

    load_dotenv()
    news_source = 'news247'
    articles_df = import_dataset(news_source)
    articles_df = articles_df.reset_index(drop=True)  # make sure indexes pair with number of rows
    articles_classes = []

    for index, row in articles_df.iterrows():

        url = 'http://127.0.0.1:1234/v1/chat/completions'
        text = row['Article']

        data = {
            "model": os.getenv('MODEL'),
            "messages": [
                    {
                        "role": "system",
                        "content":  os.getenv('PROMPT_SYSTEM')
                    },
                    {
                        "role": "user",
                        "content": os.getenv('PROMPT_USER')+text
                    }
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        }

        response = requests.post(url, json=data)
        res = json.loads(response.text)
        articles_class = res.get('choices')[0].get('message').get('content')
        print(articles_class)
        articles_classes.append(articles_class)

    # Column length must match dataframe length
    articles_df['Class'] = articles_classes
    print(articles_df)
    articles_df.to_csv(r'classifier/data/'+news_source + '_articles_classified.csv', index=False, sep=',', header=True)

# Run
if __name__ == '__main__':
    main()









