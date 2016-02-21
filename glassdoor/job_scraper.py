import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import random
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from general_utilities.navigation_utilities import issue_driver_query
from general_utilities.parsing_utilities import parse_num

def parse_num_jobs_txt(num_jobs_txt): 
    """Parse the text that holds the number of jobs to get the number. 


    This will use a regex to find the number of jobs that match our 
    search query. There should only be two numbers in the num_jobs_txt, 
    and so it should be fairly easy to find. 

    Args: 
        num_jobs_txt: String that contains the number of jobs matching
            the search query. 
    """

    regex = re.compile('\d*[,]?\d+[+]*')
    search_results = re.findall(regex, num_jobs_txt)
    num_jobs = search_results[0].replace(',', '')

    return num_jobs

def parse_num_pages_txt(num_pages_txt): 
    """Parse the text that holds the number of pages to see how many pages
    we have to iterate over. 

    This will use a regex to find the number of pages of job search results 
    that we obtained in our job search. The number of pages can be found by 
    parsing the text telling us what page of the total we are on (i.e. 
    Page 1 of 10, or something like that). 

    Args: 
        num_pages_txt: Str
            Contains the text that holds the total number of pages that
            are returned from our job search. 
    """

    regex = re.compile('\d*[,]?\d+[+]*')
    search_results = re.findall(regex, num_pages_txt)
    num_pages = search_results[1].replace(',', '')

    return num_pages

if __name__ == '__main__':
    # I expect that at the very least a job title and job location
    # will be passed in, so I'll attempt to get both of those within
    # a try except and throw an error otherwise. 
    try: 
        job_title = sys.argv[1]
        job_location = sys.argv[2]
    except IndexError: 
        raise Exception('Program needs a job title and job location inputted!')
    
    # Issue the job query. 
    base_URL = 'https://www.glassdoor.com/index.htm'
    query_params = (('KeywordSearch', job_title), 
            ('LocationSearch', job_location))
    driver = issue_driver_query(base_URL, query_params)

    # Find the text holding the number of jobs, and parse it. 
    time.sleep(random.randint(7, 15))
    num_jobs_txt = driver.find_elements_by_xpath('//header')[1].text
    num_jobs = int(parse_num_jobs_txt(num_jobs_txt))
    print num_jobs
    
    # Find the text holding the number of pages in the job search. 
    time.sleep(random.randint(2, 6))
    num_pages_txt = driver.find_element_by_id('ResultsFooter').text
    num_pages = int(parse_num_pages_txt(num_pages_txt))
    print num_pages
