"""A module for scraping CareerBuilder for jobs. 

This module is the driver for a CareerBuilder scraper. It controls the process 
of instantiating a Selenium browser to scrape, and controlling that browser 
throughout the entire process. It also handles the Threading, parsing, and 
storage that takes place. 

Usage: 

    python job_scraper.py <job title> <job location>
"""

import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import time
import random
import datetime
import pytz
from selenium.webdriver.common.keys import Keys
from general_utilities.navigation_utilities import issue_driver_query
from general_utilities.parsing_utilities import parse_num
from general_utilities.storage_utilities import store_in_mongo
from general_utilities.threading_utilities import HrefQueryThread

def scrape_job_page(driver, job_title, job_location): 
    """Scrape a page of jobs from CareerBuilder.

    Grab all relevant information possible for each of the jobs posted on a 
    given page. This typically includes the job title, job location, posting 
    company, and date posted. 

    Args: 
    ----
        driver: Selenium webdriver
        job_title: str
        job_location: str
    """
    titles, locations, companies, dates, hrefs = query_for_data(driver)

    current_date = str(datetime.datetime.now(pytz.timezone('US/Mountain')))
    json_dct = {'search_title': job_title, \
            'search_location': job_location, \
            'search_date': current_date, 'job_site': 'careerbuilder'}

    thread_lst = []
    for href in hrefs:  
        try: 
            thread = HrefQueryThread(href.get_attribute('href'))
        except: 
            print('Exception in href thread builder')
            thread = HrefQueryThread('')
        thread_lst.append(thread)
        thread.start()
    mongo_update_lst = []
    for title, location, company, date, thread, idx in \
            zip(titles, locations, companies, dates, thread_lst, range(len(hrefs))): 
        try: 
            mongo_dct = gen_output(json_dct.copy(), title, location, 
                    company, date, thread, idx)
            mongo_update_lst.append(mongo_dct)
        except: 
            print('Missed element in careerbuilder!')

    store_in_mongo(mongo_update_lst, 'job_postings', 'careerbuilder')

def query_for_data(driver): 
    """Grab all the relevant data on a jobs page. 
    
    Args: 
    ----
        driver: Selenium webdriver

    Return: 
    ------
        job_titles: list
        job_locations: list 
        posting_companies: list 
        dates: list
        hrefs: list 
    """

    job_titles = driver.find_elements_by_class_name('job-title')
    job_texts = driver.find_elements_by_class_name('job-text')
    posting_companies = job_texts[2::3]
    job_locations = job_texts[::3] 
    dates = driver.find_elements_by_css_selector('div .time-posted')
    hrefs = driver.find_elements_by_xpath("//h2//a")
        
    return job_titles, job_locations, posting_companies, dates, hrefs 

def gen_output(json_dct, title, location, company, date, thread, idx): 
    """Format the output dictionary that will end up going into Mongo. 

    Args: 
        json_dct: dict
        title: Selenium WebElement 
        location: Selenium WebElement 
        company: Selenium WebElement
        date: Selenium WebElement
        thread: RequestThreadInfo object

    Return:
    ------
        json_dct: dct
    """

    # Need to make sure that the thread is done first. 
    thread.join()

    json_dct['job_title'] = title.text
    json_dct['location'] = location.text
    json_dct['company'] = company.text
    json_dct['date'] = date.text

    json_dct['posting_txt'] = thread.posting_txt

    return json_dct
    
def check_if_next(driver):
    """Check if there is a next page of job results to grab. 

    Grab the clickable job links on the bottom of the page, and check if one reads
    'Next'. If so, click it and return True. Otherwise, return False. 

    Args: 
    ----
        driver: Selenium webdriver

    Return: bool 
    """

    # If the following class name is not found, then the next button doesn't exist
    # and it will fail. The except block will then catch it and return a False. 
    try: 
        last_link = driver.find_element_by_xpath("//a[@aria-label='Next Page']")
        last_link.send_keys(Keys.ENTER)
        return True
    except: 
        return False

if __name__ == '__main__':
    try: 
        job_title = sys.argv[1]
        job_location = sys.argv[2]
    except IndexError: 
        raise Exception('Program needs a job title and job location inputted!')
    
    # Navigate to the base URL and issue the original search query. 
    base_URL = 'http://www.careerbuilder.com/'
    query_params = (('keywords', job_title), ('location', job_location))
    driver = issue_driver_query(base_URL, query_params)

    # Grab num. jobs
    try: 
        num_jobs_txt = driver.find_element_by_css_selector('div .count').text
        num_jobs = int(parse_num(num_jobs_txt, 0)) 
    except: 
        print('No jobs for search {} in {}'.format(job_title, job_location))
        sys.exit(0)

    current_date = str(datetime.datetime.now(pytz.timezone('US/Mountain')))
    storage_dct = {'job_site': 'careerbuilder', 'num_jobs': num_jobs, 
            'date': current_date, 'title': job_title, 'location': job_location}
    store_in_mongo([storage_dct], 'job_numbers', 'careerbuilder')

    is_next = True
    while is_next: 
        jobs = scrape_job_page(driver, job_title, job_location)
        is_next = check_if_next(driver)
    driver.close()
