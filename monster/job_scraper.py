import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

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
    for job in jobs: 
        scrape_job(job, driver)

def scrape_job(job, driver): 
    """Scrape an individual job posting from a jobs page on Monster. 

    We will grab everything that we can (or is relevant) for each 
    the inputted job posted on a one of the jobs pages from our search. 
    This will include the job title, job location, posting company, and 
    the date posted. Lastly, we will click the job posting link itself 
    and grab the text from that URL/page (we'll use the webdriver to 
    do this). 

    Args: 
        job: Selenium WebElement (holds a job posting)
        driver: Selenium webdriver.
    """
    
    job_title = job.find_element_by_xpath(
            "//span[@itemprop='title']").text
    job_location = job.find_element_by_xpath(
        "//div[@itemprop='jobLocation']").text
    posting_company = job.find_element_by_xpath(
        "//span[@itemprop='name']").text
    time = job.find_element_by_xpath(
        "//time[@itemprop='datePosted']").text
    
    job_href = job.find_element_by_tag_name('a').get_attribute('href')
    
    
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
