"""A module for threading requests and storing their results. 

This module currently provides one class - `RequestInfoThread`. 
It is meant to help issue get requests using threading, but 
avoid creating a new connection to a db for each thread. It 
does this by storing the results of the get request as an 
attribute on the class. 
"""
import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import datetime
import pytz
import re
from threading import Thread
from requests import get
from bs4 import BeautifulSoup
from general_utilities.parsing_utilities import find_visible_texts


class RequestInfoThread(Thread): 
    """Threading based class to issue get requests and store the results.  
    
    RequestInfoThread issues a get request on the href from an 
    inputted row (which represents a job), after grabbing all of its
    relevant information. It then stores the results as an attribute 
    available for later access. The motivation for using a class 
    instead of simply passing a function to ThreadPool was to 
    avoid creating a new connection with the database (here Mongo) 
    for each get request (this would most likely overwhelm the db 
    with connections). RequestInfoThread allows for later access of 
    the results of the get request in order to perform multiple 
    uploads/updates to the db. 


    Args: 
    ----
        row: bs4.BeautifulSoup object.
            Holds a job, including all of the info. that we want 
            to parse from it. 
        job_title: str
            Holds the job title used in the search query. 
        job_location: str
            Holds the job location used in the search query. 
    """

    def __init__(self, row, job_title, job_location): 
        super(RequestInfoThread, self).__init__()
        self.row = row
        self.job_title = job_title
        self.job_location = job_location

    def run(self): 
        self.json_dct = self._request_info()

    def _request_info(self): 
        """Grab relevant information from the row.

        Each row will contain a number of features to grab. Grab these, 
        and then its href attribute. Use that href to actually issue a request
        for the job posting's text. 

        Return: dct
        """
        
        current_date = str(datetime.datetime.now(pytz.timezone('US/Mountain')))
        json_dct = {'search_title': self.job_title, \
                'search_location': self.job_location, \
                'search_date': current_date, 'job_site': 'indeed'}
        # Holds the actual CSS selector as the key and the label I want to store
        # the info. as as the key. 
        possible_attributes = {'.jobtitle': "job_title", '.company': "company", \
                '.location': "location", '.date': "date", \
                '.iaLabel': "easy_apply"}
        for k, v in possible_attributes.iteritems(): 
            res = self.row.select(k)
            if res: 
                json_dct[v] = res[0].text
        # Now let's grab the href and pass that on to another function to 
        # get that info. 
        href = self.row.find('a').get('href')
        json_dct['href'] = href
        json_dct['posting_txt'] = self._query_href(href)

        return json_dct

    def _query_href(self, href): 
        """Grab the text from the href. 

        Follow the href that is given in the job posting, and grab 
        the posting text from there. 

        Args: 
        ----
            href: str 
                Holds the href to the job posting. 

        Return: str
        """
        try:
            html = get('http://www.indeed.com' + href) if href.startswith('/') \
                    else get(href)
            soup = BeautifulSoup(html.content, 'html.parser')

            texts = soup.findAll(text=True)
            visible_texts = filter(find_visible_texts, texts)
        except Exception as e: 
            print e 
            visible_texts = ['SSLError', 'happened']

        return ' '.join(visible_texts)

