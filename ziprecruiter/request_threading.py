import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import datetime
import re
from threading import Thread
from requests import get
from bs4 import BeautifulSoup
from general_utilities.parsing_utilities import find_visible_texts

class RequestInfoThread(Thread): 
    """Inherits from Thread so I can store results of my threading.     

    I want to be able to return something from my threading. This 
    class will allow me to do that - it will perform all of the 
    requesting and data gathering that I want to do, but store the 
    results on the class so that I can access them later. 
    """

    def __init__(self, job_result, job_title, job_location): 
        super(RequestInfoThread, self).__init__()
        self.job_result = job_result
        self.job_title = job_title
        self.job_location = job_location

    def run(self): 
        self.json_dct = self._request_info()

    def _request_info(self): 
        """Grab relevant information from the job result and store it in Mongo. 

        Each job_result will contain a number of features that we will
        want to grab. Then, we'll grab it's href attribute, which will
        actually hold a link to the job posting. We'll query that link and 
        grab all the text that is there. 
        """

        current_date = datetime.date.today().strftime('%m-%d-%Y')
        json_dct = {'search_title': self.job_title, \
                'search_location': self.job_location, \
                'search_date': current_date}

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

        Now we want to actually follow the href that is given in the 
        job posting, and grab the posting text from there. 

        Args: 
            href: String of the href to the job posting. 
        """
        try:
            html = get('http://www.ziprecruiter.com' + href) if href.startswith('/') \
                    else get(href)
            soup = BeautifulSoup(html.content, 'html.parser')

            texts = soup.findAll(text=True)
            visible_texts = filter(find_visible_texts, texts)
        except Exception as e: 
            print e 
            visible_texts = ['SSLError', 'happened']

        return ' '.join(visible_texts)

