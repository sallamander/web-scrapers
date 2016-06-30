"""A module for querying for articles from the NYTimes."""

import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
from requests import get
from general_utilities.query_utilities import check_response_code

def issue_single_query(api_key, start_dt, end_dt, page=0): 
    """Issue a query on the NYTimes API given the inputted parameters. 

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

if __name__ == '__main__':
    try: 
        start_dt = sys.argv[1]
        end_dt = sys.argv[2]
    except: 
        raise Exception("Usage: python article_scraper.py start_dt end_dt")

    api_key = os.environ['NYTIMES_API_KEY']
    response = issue_single_query(api_key, start_dt, end_dt)

