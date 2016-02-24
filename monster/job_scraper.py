import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import datetime
from itertools import izip
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from general_utilities.storage_utilities import store_in_mongo
from general_utilities.query_utilities import get_html, format_query
from general_utilities.navigation_utilities import issue_driver_query
from general_utilities.parsing_utilities import parse_num
from general_utilities.threading_utilities import HrefQueryThread

def scrape_job_page(driver, job_title, job_location):
    """Scrape a page of jobs from Monster.

    We will grab everything that we can (or is relevant) for each 
    of the jobs posted for a given page. This will include the job title, 
    job location, posting company, and the date posted. Lastly, we will 
    click the job posting link itself and grab the text from that URL/page. 

    Args: 
        driver: Selenium webdriver
        job_title: str
        job_location: str
    """

    titles, locations, companies, dates, hrefs = query_for_data()


    current_date = datetime.date.today().strftime("%m-%d-%Y")
    json_dct = {'search_title': job_title, \
            'search_location': job_location, \
            'search_date': current_date}

    thread_lst = []
    for href in hrefs: 
        thread = HrefQueryThread(href)
        thread_lst.append(thread)
        thread.start()
    mongo_update_lst = []
    for title, location, company, date, thread in \
            izip(titles, locations, companies, dates, thread_lst): 
        mongo_dct = gen_output(json_dct.copy(), title, location, 
                company, date, thread)
        mongo_update_lst.append(mongo_dct)

    store_in_mongo(mongo_update_lst, 'job_postings', 'monster')

def query_for_data(): 
    """Grab all relevant data on a jobs page. 

    For each page of jobs, we will utlimately want to grab each of the 
    jobs title, location, posting companies, and dates posted. Finally, 
    we'll want to grab the href of the job posting, and use that to get 
    the times, and all of the hrefs at once. We'll return those and 
    then work on actually grabbing the text from them. 
    """

    job_titles = driver.find_elements_by_xpath(
            "//span[@itemprop='title']")
    job_locations = driver.find_elements_by_xpath(
        "//div[@itemprop='jobLocation']")
    posting_companies = driver.find_elements_by_xpath(
        "//span[@itemprop='name']")
    dates = driver.find_elements_by_xpath(
        "//time[@itemprop='datePosted']")
    hrefs = driver.find_elements_by_xpath("//div//article//div//h2//a")

    return job_titles, job_locations, posting_companies, dates, hrefs

def gen_output(json_dct, title, location, company, date, thread): 
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
    so that we can stop grabbing results from Monster. 

    Args: 
        driver: Selenium webdriver
    """
    
    page_links = driver.find_elements_by_class_name('page-link')
    # page_links will now hold a list of all the links. The last 
    # link in that list will hold 'Next' for the text, if we aren't
    # on the last page of jobs. 
    last_link = page_links[-1]
    if last_link.text == 'Next': 
        last_link.send_keys(Keys.ENTER)
        return True
    else: 
        return False
        
if __name__ == '__main__':
    # I expect that at the very least a job title, job location, and radius
    # will be passed in, so I'll attempt to get both of those within
    # a try except and throw an error otherwise. 
    try: 
        job_title = sys.argv[1].split()
        job_location = sys.argv[2].split()
        radius = sys.argv[3]
    except IndexError: 
        raise Exception('Program needs a job title, job location, and radius inputted!')

    base_URL = 'http://jobs.monster.com/search/?'
    query_parameters = ['q={}'.format('-'.join(job_title)), 
            '&where={}'.format('-'.join(job_location)), '&sort=dt.rv.di', 
            '&rad={}'.format(radius)]

    query_URL = format_query(base_URL, query_parameters)
    driver = issue_driver_query(query_URL)

    num_jobs_txt = driver.find_elements_by_class_name('page-title')[0].text
    num_jobs = int(parse_num(num_jobs_txt, 0))
    
    # This loop will be used to keep clicking the next button after
    # scraping jobs on that page. 
    is_next = True
    while is_next: 
        scrape_job_page(driver, job_title, job_location)
        is_next = check_if_next(driver)
    driver.close()
