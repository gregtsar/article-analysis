import os
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
from dotenv import load_dotenv

import pandas as pd


# Make a http query from url and create soup to parse
def create_soup_from_url(url):
    # To avoid 403-error using User-Agent
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    response = urllib.request.urlopen(req)

    html = response.read()

    # Parsing response
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def main():
    # List with queries

    # Load keywords to search
    load_dotenv()
    search_keywords = os.getenv('KEYWORDS')
    desired_queries = search_keywords.split(',')

    # Search scope
    source = "newsbomb.gr"
    search_page_url = 'https://www.newsbomb.gr/search?q='
    page = 0
    end_page = 4

    # Set storage
    link_results = []
    article_results = []
    title_results = []
    date_results = []
    link_results_processed = []

    # Scrape for links in website database given the queries
    for query in desired_queries:
        # Scrape n pages
        for i in range(end_page):
            page = page + i

            # Get search page items
            soup = create_soup_from_url(url=search_page_url + quote(query) + '&page=' + str(page))

            # Extracting number of link_results
            search = soup.find('div', attrs={'class': 'news-items'}).findAll('div', attrs={'class': 'flat-card'})

            # Search for articles within given tag:
            for s in search:
                articles = soup.find('div', attrs={'class': 'news-items'}).findAll('div', attrs={'class': 'flat-card'})

                # Extract the link of each article:
                for a in articles:

                    links = "https://www.newsbomb.gr"+a.find('h3', attrs={'class': 'item-title'}).find('a').get('href')
                    # print(links)
                    link_results.append(links)

    # Scrape inside individual search results
    for i in range(len(link_results)):

        # Get single article
        soup = create_soup_from_url(url=link_results[i])

        # Get article body
        try:
            article_body = soup.find('div', attrs={'class': 'main-text'}).findAll('p', recursive=False)
        except:
            # Process article only if body is available
            continue

        list_paragraphs = []
        complete_article = ""
        for paragraph in article_body:
            list_paragraphs.append(paragraph.text)
            complete_article = " ".join(list_paragraphs)

        article_results.append(complete_article)

        # Get article url
        link_results_processed.append(link_results[i])

        # Get article title
        try:
            article_title = soup.find('div', attrs={'class': 'item-title-area'}).find('h1', recursive=False)
            title_results.append(article_title.text)
        except:
           article_title = 'N/A'
           title_results.append(article_title)

        # Get article date
        try:
            article_date = soup.find('div', attrs={'class': 'main-meta'}).find('time')
            # Custom process date to YY-M-D
            date_raw = article_date['datetime']
            date_processed = date_raw[: 10]
            date_results.append(date_processed)
        except:
           article_date = 'N/A'
           date_results.append(article_date)

    # Add data from articles in pandas dataframe
    articles_list = {'Title': title_results, 'Source': source, 'Date': date_results, 'Link': link_results_processed,
                     'Scraped': datetime.now(), 'Article': article_results}
    articles_df = pd.DataFrame(data=articles_list)
    cols = ['Title', 'Source', 'Date', 'Link', 'Scraped', 'Article']
    articles_df = articles_df[cols]

    # Check for duplicates in df:
    # articles_df = articles_df[articles_df.duplicated()]

    # Drop duplicates in df:
    articles_df = articles_df.drop_duplicates()
    print(articles_df)

    # Save to CSV
    articles_df.to_csv(r'data/newsbomb_articles.csv', index=False, sep=',', header=True)

    # Development sanity checks:
    print(link_results)
    print(len(link_results))

    # Check if link_results are unique:
    if len(link_results) > len(set(link_results)):
        print("not unique")
    else:
        print("unique")

    print(articles_df)


# Run
if __name__ == '__main__':
    main()
