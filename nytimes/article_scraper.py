"""A module for querying for articles from the NYTimes."""

import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import pandas as pd
import numpy as np
from datetime import timedelta
from requests import get
from time import sleep
from os.path import exists
from pymongo import MongoClient
from general_utilities.query_utilities import check_response_code, get_html
from general_utilities.storage_utilities import store_in_mongo

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
        queries_path (optional): str
            Holds a filepath location to keep track of successfully issued queries.
            Expected to be pointed at a `.csv` file. 
    """

    def __init__(self, queries_path='work/queries.csv'): 
        self.articles = [] 
        self.queries_path = queries_path
        self.base_url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'
        self.scrape = True 

    def __enter__(self): 
        """Set up to make sure there is no duplicate scraping/storing.""" 
        if exists(self.queries_path): 
            # Use to ensure that there is no duplicate scraping in terms of dates. 
            self.queries_df = pd.read_csv(self.queries_path, index_col=0, 
                                          parse_dates=True)
        else: 
            self.queries_df = pd.DataFrame()

        # Use to ensure that there are no duplicate web_urls grabbed. 
        client = MongoClient()
        db = client['nytimes']
        collection = db['gen_articles']

        res = collection.find({'web_url': {'$exists': 'true'}}, {'web_url': True, 
                               '_id': False})
        res_lst = list(res)
        self.web_urls = set(article['web_url'] for article in res_lst)
        client.close()

        return self

    def __exit__(self, *args): 
        """Save the `queries_df` for later use."""
        self.queries_df.sort_index(inplace=True)
        self.queries_df.to_csv(self.queries_path)

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
        
        self.update_queries_df(begin_date, insert=True)

        if self.scrape: 
            initial_response = self.scrape_single_page(params)

            num_results = initial_response['response']['meta']['hits']
            if num_results > 10: 
                max_pages_to_search = min(100, num_results // 10 + 1)
                for page in range(1, max_pages_to_search): 
                    sleep(1/5) # Use to avoid hitting the rate limit. 

                    params['page'] = page
                    self.scrape_single_page(params)
        
            self.dump_articles()
            self.update_queries_df(begin_date, insert=False)

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
        status_code = response.status_code

        if status_code != 200 and status_code != 429: 
            print('Bad URL: {}'.format(response.url))
        elif status_code == 429: 
            print('Rate limits hit for the day.')
            sys.exit(0)
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
                              'news_desk', 'type_of_material', 'document_type',
                              'pub_date')

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

            if article_dct['web_url'] not in self.web_urls: 
                self.articles.append(article_dct)

    def dump_articles(self): 
        """Dump articles list into Mongo."""

        if self.articles: 
            client = MongoClient()
            db = client['nytimes']
            collection = db['gen_articles']
            collection.insert_many(self.articles)
            client.close()

            self.articles = [] # Start each day of scraping with an empty list. 

    def update_queries_df(self, update_dt, insert=True): 
        """Modify `self.queries_df` for the inputted dates. 

        `self.queries_df` will be used to keep track of dates that have already been
        scraped. It is indexed by date, and has one column (`scraped`) that holds a 1
        if the date has already been scraped for and a 0 otherwise. 

        If `insert` is True, check if the inputted date is already in 
        `self.queries_df`. If it isn't, insert a new observation with a 0 value to
        denote that the date has not been scraped yet. If `insert` is False, update
        the value of the inputted date in `self.queries_df` with a 1. 

        Args:
        ----
            update_dt: str
            insert (optional): bool

        """

        update_value = 0 if insert else 1
        update_dt = pd.to_datetime(update_dt)
        
        if update_dt in self.queries_df.index: 
            self.scrape = not self.queries_df.loc[update_dt, 'scraped']
        else: 
            self.scrape = 1

        if self.scrape:
            self.queries_df.loc[update_dt, 'scraped'] = update_value

class NYTArticleScraper(object): 
    """Scraper for URLs pointing at New York Times articles.

    Args: 
    ----
        db_name: str
        coll_name: str
    """

    def __init__(self, db_name, coll_name): 
        self.db_name = db_name
        self.coll_name = coll_name

    def __enter__(self): 
        """Set up URL list for scraping."""

        client = MongoClient()
        db = client[self.db_name]
        collection = db[self.coll_name]

        res = collection.find({'web_url': {'$exists': True}, 
                                    'text' : {'$exists': False}}, 
                               {'web_url': True, '_id': False})

        self.articles_to_scrape = list(res)
        client.close()

        return self

    def __exit__(self, *args): 
        """Ensure that any URLs scraped for get their text attributes updated."""
        
        store_in_mongo(self.articles_to_scrape, self.db_name, self.coll_name, 
                       key='web_url')

    def scrape_pages(self):
        """Scrape all pages stored in `self.web_urls`."""

        for article in self.articles_to_scrape:
            url = article['web_url']
            
            if url.startswith('/'):
                url = 'http://www.nytimes.com' + url
            sleep(1/20)
            soup = get_html(url)
            article_txt = self._parse_soup(soup)

            if article_txt: 
                article['text'] = article_txt

    def _parse_soup(self, soup):
        """Parse the inputted `soup`.

        Args:
        ----
            soup: bs4.BeautifulSoup object
            type_of_material: str
        
        Returns: 
        -------
            article_txt: str
        """

        content = soup.find('div', attrs={'class': 'story-body'})

        if content: 
            lines = content.findAll('p')
            article_txt = ' '.join([line.text for line in lines])
        else: 
            article_txt = None

        return article_txt

if __name__ == '__main__':
    if len(sys.argv) >= 2: 
        try: 
            start_dt = sys.argv[1]
            end_dt = sys.argv[2]
        except: 
            error_msg = "Must pass in both a starting and ending date!"
            raise Exception(error_msg)
    else: 
        start_dt, end_dt = None, None

    extra_params = {'fq' : """source:("The New York Times") AND type_of_material:("News")"""}

    api_key = os.environ['NYTIMES_API_KEY']
    extra_params['api-key'] = api_key
    if start_dt and end_dt: 
        with NYTPageScraper(queries_path='work/general.csv') as page_scraper: 
            page_scraper.scrape_dts(start_dt, end_dt, extra_params)

    with NYTArticleScraper('nytimes', 'gen_articles') as article_scraper: 
        article_scraper.scrape_pages()
