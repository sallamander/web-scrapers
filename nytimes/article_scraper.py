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

class NYTPageScraper(object): 
    """Scraper for pages of results returned by the Article Search API from NYTimes.

    Provides an interface to search for results by inputted parameters over a
    single date or multiple dates, as well as returning multiple pages from the 
    search or one page in particular. Searching is limited by the rate limits 
    applied by the API (developer.nytimes.com/article_search_v2.json).

    Limits in terms of the returned results are determined by the search parameters. 
    Results are returned in batches of 10, and additional results are accessible via
    a `page` parameter. The `page` parameter is capped at 100, which caps the
    total number of results at 1000 for a single query. The total number of results
    can be limited by adding aditional search parameters. This can be a way to ensure
    that all possible results are captured for a given query.

    Args: 
    ----
        api_key: str
    """

    def __init__(self, api_key): 
        self.api_key = api_key
        self.articles = [] 
        self.base_url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'

    def scrape_dts(self, start_dt, end_dt, extra_params=None): 
        """Scrape the NYTimes for multiple dates, using the inputted parameters.

        Loop over each date from the `start_dt` to `end_dt`, calling 
        `self.scrape_dt`. Scraping over a single day at a time helps to avoid 
        missing possible search results (see the class docstrings for an explanation).
        
        Args: 
        -----
            start_dt: str
            end_dt: str
            extra_params (optional): dct
                Potential extra parameters to pass in the URL when querying the 
                API (see params at developer.nytimes.com/article_search_v2.json)).
        """
        
        dt_range = pd.date_range(start_dt, end_dt)

        for begin_date in dt_range:
            begin_date = begin_date.strftime('%Y%m%d') 
            end_date = begin_date 
            self.scrape_dt(begin_date, end_date, extra_params)
            
    def scrape_dt(self, begin_date, end_date, extra_params=None): 
        """Scrape the NYT for a single date, using the inputted parameters.

        Scrape over as many pages are returned, subject to the page cap at 100.

        Args: 
        -----
            begin_date: str
            end_date: str
            extra_params (optional): dct
                Potential extra parameters to pass in the URL when querying the 
                API (see params at developer.nytimes.com/article_search_v2.json)).
        """

        params = None if not extra_params else extra_params.copy()
        # Issue the intial query with page equal to 0. 
        params['page'] = 0
        params['begin_date'] = begin_date
        params['end_date'] = end_date

        initial_response = self.scrape_single_page(params)

        num_results = initial_response['response']['meta']['hits']
        if num_results > 10: 
            max_pages_to_search = min(100, num_results // 10 + 1)
            for page in range(1, max_pages_to_search): 
                sleep(1/5) # Use to avoid hitting the rate limit. 

                params['page'] = page
                self.scrape_single_page(params)

    def scrape_single_page(self, params):
        """Scrape the NYT for a single page, using the inputted params. 

        Args: 
        ----
            params: dct

        Return: 
        ------
            response_json: dct
        """

        if 'page' not in params: 
            print('No `page` paramter pased in, using 0...')
            params['page'] = 0
            
        response = get(self.base_url, params=params)

        good_response = check_response_code(response)
        if not good_response: 
            # Check the bad_url to see what happened.
            print('Bad URL: {}'.format(response.url))
        else: 
            response_json = response.json()
            self.parse_page_results(response_json)
            return response_json

    def parse_page_results(self, response_json):
        """Parse a single page of results, grabbing each article's desired attributes.

        Args: 
        ----
            response_json: dct
        """
         
        # Attributes that require no post-processing/farther parsing. 
        desired_attributes = ('source', 'subsection_name', 'section_name', 'web_url', 
                              'news_desk', 'type_of_material', 'document_type')

        for doc in response_json['response']['docs']: 
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

            self.articles.append(article_dct)

if __name__ == '__main__':
    try: 
        start_dt = sys.argv[1]
        end_dt = sys.argv[2]
    except: 
        raise Exception("Usage: python article_scraper.py start_dt end_dt")

    extra_params = {'fq' : """section_name : ("Sports" "World" "U.S" "Technology" 
                                               "Health" "Business" "Arts" "Science"
                                               "Style" "Movies" "Travel" )""", 
                    }

    api_key = os.environ['NYTIMES_API_KEY']
    nyt_scraper = NYTPageScraper(api_key)
    nyt_scraper.scrape_dts(start_dt, end_dt, extra_params)

