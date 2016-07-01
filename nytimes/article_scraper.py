"""A module for querying for articles from the NYTimes."""

import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import pandas as pd
from datetime import timedelta
from requests import get
from time import sleep
from general_utilities.query_utilities import check_response_code, get_html

def scrape_nyt(api_key, start_dt, end_dt): 
    """Scrape the NYTimes for all results within an inputted start and end date.

    Issue a single query for the inputted date range, and then cycle through all
    pages of results that are returned, if there are mutiple pages (each page stores
    10 results, so if there are more than 10 results, there is more than 1 page).

    Args:
    ----
        api_key: str
        start_dt: str
        end_dt: str

    Return: 
    ------
        articles: list
    """
    
    articles = []
    initial_response = scrape_single_page(api_key, start_dt, end_dt)
    articles = parse_page_results(initial_response, articles)

    num_results = initial_response['response']['meta']['hits']
    if num_results > 10: 
        # They don't allow querying past the 100th page. 
        max_pages_to_search = min(100, num_results // 10)
        for page in range(1, max_pages_to_search): 
            sleep(1/5) # Use to avoid hitting the rate limit. 
            response = scrape_single_page(api_key, start_dt, end_dt, page=page)
            articles = parse_page_results(response, articles) 

    return articles

def scrape_single_page(api_key, start_dt, end_dt, page=0): 
    """Issue a query against a single page of the NYTimes API for the inputted dates.

    This will largely be called as a helper function to `scrape_nyt`. 

    Args:
    ----
        api_key: str
        start_dt: str
        end_dt: str
        page (optional): int

    Returns:
    -------
        response_json: dct
    """


    params = {'fq' : """section_name : ("Sports" "World" "U.S" "Technology" 
                                        "Health" "Business" "Arts" "Science"
                                        "Style" "Movies" "Travel" )""", 
              'begin_date' : start_dt, 
              'end_date' : end_dt, 
              'page': page, 
              'api-key': api_key
             }

    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'
    response = get(url, params=params)

    good_response = check_response_code(response)
    if not good_response: 
        # Check the bad_url to see what happened.
        print('Bad URL: {}'.format(response.url))

    return response.json()

def parse_page_results(response, articles):
    """Parse a single page of results, grabbing each article's desired attributes.

    Args: 
    ----
        response: dct
        articles: list of dcts

    Return: 
    ------
        articles: list of dcts
            Inputted articles list with additional parsed articles added to it 
    """
     
    # Special attributes that require no post-processing.
    desired_attributes = ('source', 'subsection_name', 'section_name', 'web_url', 
                          'news_desk', 'type_of_material', 'document_type')
    for doc in response['response']['docs']: 
        article_dct = {}
        for attr in desired_attributes: 
            article_dct[attr] = doc.get(attr, None)
        
        keywords = doc.get('keywords', None)
        headline_dct = doc.get('headline', None) 

        if keywords:
            keywords_lst = [keywords_dct['value'] for keywords_dct in keywords]
            article_dct['keywords'] = keywords_lst
        if headline_dct: 
            headline = headline_dct['main']
            article_dct['headline'] = headline

        articles.append(article_dct)

    return articles

if __name__ == '__main__':
    try: 
        start_dt = sys.argv[1]
        end_dt = sys.argv[2]
    except: 
        raise Exception("Usage: python article_scraper.py start_dt end_dt")

    dt_range = pd.date_range(start_dt, end_dt)
    api_key = os.environ['NYTIMES_API_KEY']

    for start_dt in dt_range:
        end_dt = start_dt + timedelta(days=1)
        start_dt, end_dt = start_dt.strftime('%Y%m%d'), end_dt.strftime('%Y%m%d')
        articles = scrape_nyt(api_key, start_dt, end_dt)


