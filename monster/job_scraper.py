import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from general_utilities.storage_utilities import store_in_mongo
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

def scrape_job_page(driver):
    """Scrape a page of jobs from Monster.

    We will grab everything that we can (or is relevant) for each 
    of the jobs posted for a given page. This will include the job title, 
    job location, posting company, and the date posted. Lastly, we will 
    click the job posting link itself and grab the text from that URL/page. 

    Args: 
        driver: Selenium webdriver
    """

    jobs = driver.find_elements_by_class_name('js_result_row')
    threads = []
    mongo_update_lst = []
    for job in jobs: 
        thread = RequestInfoThread(job, job_title, job_location)
        thread.start()
        threads.append(thread)
    for thread in threads: 
        thread.join()
        mongo_update_lst.append(thread.json_dct)

    store_in_mongo(mongo_update_lst, 'job_postings', 'monster')

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
    scrape_job_page(driver)
