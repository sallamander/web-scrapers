import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import datetime
import re
from threading import Thread
from requests import get
from bs4 import BeautifulSoup
from general_utilities.query_utilities import get_html

class RequestInfoThread(Thread): 
    """Inherits from Thread so I can store results of my threading. 

    I want to be able to return something from my threading. This 
    class will allow me to do that - perform all of the requesting 
    and data gathering that I want to do, but store the results on 
    the class so that I can access them later. 
    """

    def __init__(self, href): 
        super(RequestInfoThread, self).__init__()
        self.href = href.get_attribute('href')

    def run(self): 
        self.posting_txt = self._query_href()

    def _query_href(self): 
        """Grab the text from the href. 

        Now we want to actually follow the href that is given in the 
        job posting, and grab the posting text from there. 

        Args: 
            href: String of the href to the job posting. 
        """
        try:
            soup = get_html(self.href)

            texts = soup.findAll(text=True)
            visible_texts = filter(self._visible, texts)
        except Exception as e: 
            print e 
            visible_texts = ['SSLError', 'happened']

        return ' '.join(visible_texts)

    def _visible(self, element): 
        """If the element is of the type we want to keep, return True. 

        We want to filter out certain elements from the text that we will 
        get back. We only want to keep text that is visible on the web page, 
        and we'll use this function to do this. 

        Args: 
            element: String element to keep in or filter out. 
        """
        if element.parent.name in ['style', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', element):
            return False
        return True
