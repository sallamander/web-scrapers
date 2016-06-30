"""A module for querying for articles from the NYTimes."""

import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
from requests import get
from time import sleep
from general_utilities.query_utilities import check_response_code

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
        article_urls: list
    """
    
    article_urls = []
    initial_response = scrape_single_page(api_key, start_dt, end_dt)
    num_results = initial_response['response']['meta']['hits']

    article_urls = [doc['web_url'] for doc in initial_response['response']['docs']]
    if num_results > 10: 
        # They don't allow querying past the 100th page. 
        max_pages_to_search = min(100, num_results // 10)
        for page in range(1, max_pages_to_search): 
            sleep(1/5) # Use to avoid hitting the rate limit. 
            response = scrape_single_page(api_key, start_dt, end_dt, page=page)
            article_urls = add_page_urls(article_urls, response)

    return article_urls

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

    params = {'begin_date' : start_dt, 
              'end_dt' : end_dt, 
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

def add_page_urls(article_urls, response): 
    """Append any article URL's found in the inputted reponse to the `article_urls`.

    Args: 
    ----
        article_urls: list
        response: requests.models.Response object
            Expected to have a 'response' attribute, with a 'docs' attribute. 

    Return: 
    ------
        article_urls: list
    """

    for doc in response['response']['docs']: 
        article_urls.append(doc['web_url'])

    return article_urls

if __name__ == '__main__':
    try: 
        start_dt = sys.argv[1]
        end_dt = sys.argv[2]
    except: 
        raise Exception("Usage: python article_scraper.py start_dt end_dt")

    api_key = os.environ['NYTIMES_API_KEY']
    article_urls = scrape_nyt(api_key, start_dt, end_dt)

