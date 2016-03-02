import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import time
import random
import datetime
import pytz
from itertools import izip
from selenium.webdriver.common.keys import Keys
from general_utilities.navigation_utilities import issue_driver_query
from general_utilities.parsing_utilities import parse_num
from general_utilities.storage_utilities import store_in_mongo
from general_utilities.threading_utilities import HrefQueryThread

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

    current_date = str(datetime.datetime.now(pytz.timezone('US/Mountain')))
    json_dct = {'search_title': job_title, \
            'search_location': job_location, \
            'search_date': current_date, 'job_site': 'careerbuilder'}

    thread_lst = []
    for href in hrefs:  
        try: 
            thread = HrefQueryThread(href.get_attribute('href'))
        except: 
            print 'Exception in href thread builder' 
            thread = HrefQueryThread('')
        thread_lst.append(thread)
        thread.start()
    mongo_update_lst = []
    for title, location, company, date, thread, idx in \
            izip(titles, locations, companies, dates, thread_lst, range(len(hrefs))): 
        try: 
            mongo_dct = gen_output(json_dct.copy(), title, location, 
                    company, date, thread, idx)
            mongo_update_lst.append(mongo_dct)
        except: 
            print 'Missed element in careerbuilder!'

    store_in_mongo(mongo_update_lst, 'job_postings', 'careerbuilder')

def query_for_data(): 
    """Grab all the relevant data on a jobs page. 
    
    For each page of jobs, we will ultimately want to grab each of 
    the jobs title, location, posting company, and dates posted. Finally, 
    we'll want to grab the href of the job posting, and use that to get 
    the all of the jobs posting. 
    """

    job_titles = driver.find_elements_by_class_name('prefTitle')
    posting_companies = driver.find_elements_by_xpath(
            "//td[@itemprop='hiringOrganization']")
    job_locations = driver.find_elements_by_xpath(
            "//div[@itemprop='jobLocation']") 
    dates = driver.find_elements_by_xpath("//span[@class='time_posted']") 
    hrefs = driver.find_elements_by_xpath("//h2//a")

    return job_titles, job_locations, posting_companies, dates, hrefs

def gen_output(json_dct, title, location, company, date, thread, idx): 
    """Format the output dictionary that will end up going into Mongo. 

    Basically, here I just want to actually store things in a dictionary 
    via certain keys. I found this cleaner than putting it in the
    scrape_job_page function. 

    Args: 
        json_dct: dict
        title: Selenium WebElement 
        location: Selenium WebElement 
        company: Selenium WebElement
        date: Selenium WebElement
        thread: RequestThreadInfo object
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

    Here, we'll grab the clickable job links on the bottom of
    the page, and check if one of those reads 'Next', at which 
    point we can click it. Otherwise, we'll just return `False` 
    so that we can stop grabbing results from CareerBuilder. 

    Args: 
        driver: Selenium webdriver
    """

    # If the following class name is not found, then the next button
    # doesn't exist and it will fail. The except block will then catch
    # it and return a False (i.e. there is no next page). 
    try: 
        last_link = driver.find_element_by_class_name(
                'JL_MXDLPagination2_next')
        last_link.send_keys(Keys.ENTER)
        return True
    except: 
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
    try: 
        num_jobs_txt = driver.find_element_by_id('n_pnlJobResultsCount').text
        num_jobs = int(parse_num(num_jobs_txt, 0)) 
    except: 
        print 'No jobs for search {} in {}'.format(job_title, job_location)
        sys.exit(0)

    current_date = str(datetime.datetime.now(pytz.timezone('US/Mountain')))
    storage_dct = {'job_site': 'careerbuilder', 'num_jobs': num_jobs, 
            'date': current_date, 'title': job_title, 'location': job_location}
    store_in_mongo([storage_dct], 'job_numbers', 'careerbuilder')

    # This loop will be used to keep clicking the next button after
    # scraping jobs on that page. 
    is_next = True
    while is_next: 
        jobs = scrape_job_page(driver, job_title, job_location)
        is_next = check_if_next(driver)
    driver.close()
