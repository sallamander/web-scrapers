import sys
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

def issue_query(driver, job_title, job_location): 
    """Issue the initial job search query so we can start scraping.

    Here, we'll search for the input boxes through which we need to input
    a job title and job location. We'll input a job title and job location, 
    and then hit the enter button to perform the search. After that, we'll
    make sure to limit the radius of the job search, and sort by date. 

    Args: 
        driver: Selenium webdriver
        job_title: str
            A string holding the job title we're using in the search. 
        job_location: str
            A string holding the job location we're using in the search. 
    """


    title_search = driver.find_element_by_id('KeywordSearch')
    location_search = driver.find_element_by_id('LocationSearch')

    title_search.send_keys(job_title)
    location_search.clear()
    location_search.send_keys(job_location)

    location_search.send_keys(Keys.ENTER)

if __name__ == '__main__':
    # I expect that at the very least a job title and job location
    # will be passed in, so I'll attempt to get both of those within
    # a try except and throw an error otherwise. 
    try: 
        job_title = sys.argv[1]
        job_location = sys.argv[2]
    except IndexError: 
        raise Exception('Program needs a job title and job location inputted!')

    base_URL = 'https://www.glassdoor.com/index.htm'
    driver = webdriver.Firefox()
    driver.get(base_URL)
    driver.implicitly_wait(10)
    issue_query(driver, job_title, job_location)

