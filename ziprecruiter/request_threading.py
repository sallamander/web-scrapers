"""A module for threading requests and storing their results. 

This module currently provides one class - `RequestInfoThread`. It is meant to help
issue get requests using threading, but avoid creating a new connection to a db for each thread. It does this by storing the results of the get request as an attribute
on the class. 
"""

import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import datetime
import re
import pytz
from threading import Thread
from requests import get
from bs4 import BeautifulSoup
from general_utilities.parsing_utilities import find_visible_texts

class RequestInfoThread(Thread): 
    """Threading based class to issue get requests and store the results.  
    
    RequestInfoThread issues a get request on the href from an inputted row (which
    represents a job), after grabbing all of its relevant information. The 
    motivation for using a class instead of simply passing a function to 
    ThreadPool was to avoid creating a new connection with the database (here Mongo) 
    for each get request (this would most likely overwhelm the comp. with threads). 

    Args: 
    ----
        job_result: bs4.BeautifulSoup object.
        job_title: str
        job_location: str
    """

    def __init__(self, job_result, job_title, job_location): 
        super(RequestInfoThread, self).__init__()
        self.job_result = job_result
        self.job_title = job_title
        self.job_location = job_location

    def run(self): 
        self.json_dct = self._request_info()

    def _request_info(self): 
        """Grab relevant information from the job result. 

        Return: 
        ------
            json_dct: dct
        """

        current_date = str(datetime.datetime.now(pytz.timezone('US/Mountain')))
        json_dct = {'search_title': self.job_title, \
                'search_location': self.job_location, \
                'search_date': current_date, 'job_site': 'ziprecruiter'}

        json_dct['job_title'] = self.job_result.select('.job_title')[0].text

        try: 
            posting_company = self.job_result.find('span', 
                    {'itemprop': 'hiringOrganization'}).text
        except: 
            posting_company = ''
        try: 
            job_location = self.job_result.find('span', 
                {'itemprop': 'addressLocality'}).text
        except: 
            job_location = ''
        try: 
            job_region = self.job_result.find('span', 
                {'itemprop': 'addressRegion'}).text
        except: 
            job_region = ''
        easy_apply = self.job_result.select('.job_apply')

        json_dct['company'] = posting_company
        json_dct['location'] = job_location + ',' + job_region
        if easy_apply: 
            json_dct['easy_apply'] = easy_apply[0].text

        # Now let's grab the href and pass that on to another function to 
        # get that info. 
        href = self.job_result.find('a').get('href')
        json_dct['href'] = href
        json_dct['posting_txt'] = self._query_href(href)

        return json_dct
        
    def _query_href(self, href): 
        """Grab the text from the href. 

        Args: 
        ----
            href: str 
                Holds the href to the job posting. 

        Return: str
        """

        try:
            html = get('http://www.ziprecruiter.com' + href) if href.startswith('/') \
                    else get(href)
            soup = BeautifulSoup(html.content, 'html.parser')

            texts = soup.findAll(text=True)
            visible_texts = filter(find_visible_texts, texts)
        except Exception as e: 
            print(e)
            visible_texts = ['SSLError', 'happened']

        return ' '.join(visible_texts)

