import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import random
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from general_utilities.navigation_utilities import issue_driver_query
from general_utilities.parsing_utilities import parse_num
from general_utilities.storage_utilities import store_in_mongo

def scrape_job_page(driver, job_title, job_location):
    """Scrape a page of jobs from Glassdoor. 

    Here, we'll grab everything that we can (or is relevant) for each 
    of the jobs posted for a given page. This will include the job title, 
    the job location, the posting company, the date posted, and then any 
    stars assigned (if any).

    Args: 
        driver: Selenium webdriver
        job_title: str
        job_location: str
    """
    
    current_date = datetime.date.today().strftime("%m-%d-%Y")
    json_dct = {'search_title': job_title, \
            'search_location': job_location, \
            'search_date': current_date}

    jobs = driver.find_elements_by_class_name('jobListing')

    mongo_update_lst = [query_for_data(driver, json_dct, job, idx) for 
            idx, job in enumerate(jobs[:-1])]

    store_in_mongo(mongo_update_lst, 'job_postings', 'glassdoor')

def query_for_data(driver, json_dct, job, idx): 
    """Grab all info. from the job posting
    
    This will include the job title, the job location, the 
    posting company, the date posted, and then any stars assigned 
    (if any). We'll also then click and get the job postings 
    actual text. 

    Args: 
        driver: Selenium webdriver
        json_dct: dict 
            Dictionary holding the current information we're storing for 
            that job posting. 
        job: Selenium WebElement
        idx: int
            Holds the # of the job posting we are on (0 indexed here). 
    """

    posting_title = job.find_element_by_class_name('title').text
    split_posting_company = job.find_element_by_class_name(
            'companyInfo').text.split()
    posting_location = job.find_element_by_xpath(
            "//div//span[@itemprop='jobLocation']").text
    try: 
        posting_date = job.find_element_by_class_name('minor').text
    except: 
        posting_date = ''

    # I couldn't think of any clearly better way to do this. If they have 
    # a number of stars, it comes in the posting companies text. I guess
    # I could have done a search and replace, but I'd rather slightly adjust
    # some functionality I already have (i.e. parse_num) than build another
    # function to find the number of stars, store it, and then replace it with
    # empty text. 
    if parse_num(' '.join(split_posting_company), 0):
        num_stars = split_posting_company[0]
        posting_company = ' '.join(split_posting_company[1:])
        out_json_dct = gen_output(json_dct.copy(), posting_title, 
                posting_location, posting_date, posting_company, num_stars)
    else: 
        posting_company = ' '.join(split_posting_company)
        out_json_dct = gen_output(json_dct.copy(), posting_title, 
                posting_location, posting_date, posting_company)
    
    out_json_dct['posting_txt'] = grab_posting_txt(driver, job, idx)
    return out_json_dct
    
def gen_output(json_dct, *args): 
    """Prep json_dct to be stored in Mongo. 

    Add in all of the *args into the json_dct so that we can store it 
    in Mongo. I'm expecting that the *args come in a specific order, 
    given by the tuple of strings below (it'll hold the keys that we 
    want to use to store these things in the json_dct). Also, the 
    'num_stars' isn't necessarily expected to be passed in (whereas 
    everything else is). 

    Args: 
        json_dct: dict
            Dictionary that currently stores a couple of things, to be 
            added to using *args. 
        *args: Tuple
            Holds what to add to the json_dct. 
    """
    keys_to_add = ('job_title', 'location', 'date', 'company', 'num_stars')
    for arg, key in zip(args, keys_to_add): 
        if arg: 
            json_dct[key] = arg

    return json_dct

def grab_posting_txt(driver, job, idx): 
    """Grab the job posting's actual text. 

    Here well have to click the job posting and then actually grab 
    it's text. 

    Args: 
        job: Selenium WebElement
    """

    job_link = job.find_element_by_class_name('jobLink')
    job_link.send_keys(Keys.ENTER)
    job_link.send_keys(Keys.ESCAPE)

    try: 
        print job.find_element_by_class_name('reviews-tab-link').text
    except: 
        pass

    time.sleep(random.randint(3, 7))
    texts = driver.find_elements_by_class_name('jobDescriptionContent')
    return texts[idx].text

def check_if_next(driver, num_pages): 
    """Check if there is a next page of job results to grab. 

    Here, we'll see if there is another page we can click to. If so, 
    we'll return `True`, otherwise `False`. 

    Args: 
        driver: Selenium webdriver 
    """
    
    try: 
        next_link = driver.find_element_by_xpath("//li[@class='next']")
        page_links = driver.find_elements_by_xpath(
                "//li//span[@class='disabled']")
        last_page = check_if_last_page(page_links, num_pages)
        if last_page:  
            return False
        time.sleep(random.randint(3, 6))
        next_link.click()
        return True
    except Exception as e:
        print e
        return False

def check_if_last_page(page_links, num_pages): 
    """Parse page links list. 

    Figure out if the page we're on is our last page or not. 

    Args: 
        page_links: list
            Holds Selenium WebElements
        num_pages: int
    """

    if len(page_links) == 1: 
        return False
    else: 
        elem1_text = page_links[0].text
        elem2_text = page_links[1].text
        if elem1_text: 
            return int(elem1_text) == num_pages
        elif elem2_text: 
            return int(elem2_text) == num_pages

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
    current_date = datetime.date.today().strftime("%m-%d-%Y")
    storage_dct = {'job_site': 'glassdoor', 'num_jobs': num_jobs, 
            'date': current_date}
    store_in_mongo([storage_dct], 'job_numbers', 'glassdoor')

    # Find the text holding the number of pages in the job search. 
    time.sleep(random.randint(2, 6))
    num_pages_txt = driver.find_element_by_id('ResultsFooter').text
    num_pages = int(parse_num(num_pages_txt, 1))

    # Find all the jobs. 
    time.sleep(random.randint(6, 12))

    # This loop will be used to keep clicking the next button after
    # scraping jobs on that page. 
    is_next = True
    while is_next: 
        jobs = scrape_job_page(driver, job_title, job_location)
        time.sleep(random.randint(5, 8))
        is_next = check_if_next(driver, num_pages)
    driver.close()
