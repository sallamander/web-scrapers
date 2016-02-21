import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import random
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from general_utilities.navigation_utilities import issue_driver_query
from general_utilities.parsing_utilities import parse_num

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
    num_jobs = int(parse_num(num_jobs_txt, 0)) 
    
    # Find the text holding the number of pages in the job search. 
    time.sleep(random.randint(2, 6))
    num_pages_txt = driver.find_element_by_id('ResultsFooter').text
    num_pages = int(parse_num(num_pages_txt, 1))
