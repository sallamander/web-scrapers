import datetime
import re
from threading import Thread
from requests import get
from bs4 import BeautifulSoup


class RequestInfoThread(Thread): 
    """Inherits from Thread so I can store results of my threading. 

    I want to be able to return something from my threading. This 
    class will allow me to do that - perform all of the requesting 
    and data gathering that I want to do, but store the results on 
    the class so that I can access them later. 
    """

    def __init__(self, row, job_title, job_location): 
        super(RequestInfoThread, self).__init__()
        self.row = row
        self.job_title = job_title
        self.job_location = job_location
        self.json_dct = {}

    def run(self): 
        self.json_dct = self._request_info()

    def _request_info(self): 
        """Grab relevant job posting info. from a jobs page on Monster. 

        We will grab everything that we can (or is relevant) for each 
        the inputted job posted on a one of the jobs pages from our search. 
        This will include the job title, job location, posting company, and 
        the date posted. Lastly, we will click the job posting link itself 
        and grab the text from that URL/page (we'll use the webdriver to 
        do this). 
        """

        current_date = datetime.date.today().strftime("%m-%d-%Y")
        json_dct = {'search_title': self.job_title, \
                'search_location': self.job_location, \
                'search_date': current_date}
        
        job_title = self.job.find_element_by_xpath(
                "//span[@itemprop='title']").text
        job_location = self.job.find_element_by_xpath(
            "//div[@itemprop='jobLocation']").text
        posting_company = self.job.find_element_by_xpath(
            "//span[@itemprop='name']").text
        time = self.job.find_element_by_xpath(
            "//time[@itemprop='datePosted']").text
        
        href = self.job.find_element_by_tag_name('a').get_attribute('href')
        json_dct['href'] = href
        
        return json_dct


