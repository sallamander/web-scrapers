import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import datetime
from itertools import izip
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from general_utilities.storage_utilities import store_in_mongo
from general_utilities.query_utilities import get_html
from request_threading import RequestInfoThread 

def issue_query(driver, job_title, job_location): 
    """Instantiate and issue query on selenium webdriver. 

    In order to search Monster, we have to use an actual web 
    browser in order to click through the pages (they won't just
    let us pass a page parameter). Here we'll instantiate a webdriver 
    (brower), and then find the search boxes on monster.com that we
    need to input a job location and job title into to find jobs.

    Args: 
        driver: Selenium webdriver
        job_title: String holding the job title to query for. 
        job_location: String holding the job location to query for. 
    """

    driver.get('http://www.monster.com')

    job_title_box = driver.find_element_by_id('mq1')
    job_location_box = driver.find_element_by_id('where1')
    
    # Insert the search times into the boxes.
    job_title_box.send_keys(job_title)
    job_location_box.send_keys(job_location)

    # Locate and click the search button.
    search_button = driver.find_element_by_id('doQuickSearch')
    search_button.send_keys(Keys.ENTER)

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
        thread = RequestInfoThread(href)
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
    the job posting text. In this function, we'll just grab all of the 
    titles, all of the locations, all of the posting companies, all of 
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
    pass

if __name__ == '__main__':
    # I expect that at the very least a job title and job location 
    # will be passed in, so I'll attempt to get both of those within
    # a try except and throw an error otherwise. 
    try: 
        job_title = ' '.join(sys.argv[1].split())
        job_location = ' '.join(sys.argv[2].split())
    except IndexError: 
        raise Exception('Program needs a job title and job location inputted!')

    driver = webdriver.Firefox() 
    issue_query(driver, job_title, job_location)
    # This loop will be used to keep clicking the next button after
    # scraping jobs on that page. 
    is_next = True
    while is_next: 
        scrape_job_page(driver, job_title, job_location)
        is_next = check_if_next(driver)
