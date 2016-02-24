import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import time
import random
import datetime
from general_utilities.navigation_utilities import issue_driver_query
from general_utilities.parsing_utilities import parse_num

def scrape_job_page(driver, job_title, job_location): 
    """Scape a page of jobs from CareerBuilder.

    We will grab all the relevant information that we can for each of 
    the jobs posted on a given page. This will include the job title, 
    job location, posting company, and date posted. 

    Args: 
        driver: Selenium webdriver
        job_title: str
            String holding the job title we searched for. 
        job_location: str
            String holding the job location we searched for. 
    """

    titles, locations, companies, dates, hrefs = query_for_data()

    current_date = datetime.date.today().strftime("%m-%d-%Y")
    json_dct = {'search_title': job_title, \
            'search_location': job_location, \
            'search_date': current_date}

    jobs = driver.find_elements_by_class_name('gs-job-result-abstract')
    return jobs

def query_for_data(): 
    """Grab all the relevant data on a jobs page. 
    
    For each page of jobs, we will ultimately want to grab each of 
    the jobs title, location, posting company, and dates posted. Finally, 
    we'll want to grab the href of the job posting, and use that to get 
    the all of the jobs posting. 
    """
    pass
    
def check_if_next(driver):
    """
    """
    return False 

if __name__ == '__main__':
    # I expect that at the very least a job title and job location
    # will be passed in, so I'll attempt to get both of those within
    # a try except and throw an error otherwise. 
    try: 
        job_title = sys.argv[1]
        job_location = sys.argv[2]
    except IndexError: 
        raise Exception('Program needs a job title and job location inputted!')

    
    # Navigate to the base URL
    base_URL = 'http://www.careerbuilder.com/'
    query_params = (('search-key', job_title), ('search-loc', job_location))
    driver = issue_driver_query(base_URL, query_params)

    # Grab num. jobs
    num_jobs_txt = driver.find_element_by_id('n_pnlJobResultsCount').text
    num_jobs = int(parse_num(num_jobs_txt, 0)) 

    # This loop will be used to keep clicking the next button after
    # scraping jobs on that page. 
    is_next = True
    while is_next: 
        jobs = scrape_job_page(driver, job_title, job_location)
        is_next = check_if_next(driver)
