import os
import pandas as pd
import requests
import json

# Project root
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def import_dataset(filename=None, encoding=None):
    """
    Imports dataset in csv format from scrapers/data/
    """
    csv_path = os.path.join(_PROJECT_ROOT, 'scrapers', 'data', filename + '_articles.csv')
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Dataset not found: {csv_path}")
    with open(csv_path, encoding=encoding or 'utf-8') as inputfile:
        df = pd.read_csv(inputfile)
    return df


def main():

    news_source = 'efsyn'
    articles_df = import_dataset(news_source)
    articles_df = articles_df.reset_index(drop=True)  # make sure indexes pair with number of rows
    articles_classes = []

    for index, row in articles_df.iterrows():

        url = 'http://127.0.0.1:1234/v1/chat/completions'
        text = row['Article']

        data = {
            "model": "ilsp_llama-krikri-8b-instruct",
            "messages": [
                    {
                        "role": "system",
                        "content": "You are an AI article classifier. The output you give needs to be a single string in order to be processed by a software. The user will be sending you news articles in the Greek language about the delivery platform company efood that need to be classified. You need to analsyze each particular news article seperately and tell if it is positive or negative about the company. You need to answer strictly in a single word: positive or negative. Do not send any thoughts."
                    },
                    {
                        "role": "user",
                        "content": "I want to know whether the following news article in greek is positive or negative about the delivery platform company efood. I want an answer in a single word only (positive or negative) and only about the following article. The article is here:"+text
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
    articles_df.to_csv(r'data/'+news_source+'_articles_classified.csv', index=False, sep=',', header=True)


# Run
if __name__ == '__main__':
    main()









