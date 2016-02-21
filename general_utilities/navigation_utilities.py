import time 
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def issue_driver_query(query_URL, query_params=None):
    """Issue the initial job search query so we can start scraping.

    Here, we'll do two things. We'll first just issue a `.get()` request
    on the `query_URL` - this will either hold the homepage from which 
    we will need to use the driver program to perform a search, or 
    will be the query_URL of the final search (we might not need to use 
    a Selenium Driver). If the former, then we'll use the `query_params` 
    to grab the search boxes and enter the query parameters. If the latter, 
    then we're done, and we'll return the Selenium driver. 

    Args: 
        query_URL: str
            Holds the homepage of the job search, or the URL of the final 
            search (i.e. with the query params concatenated in). 
        query_params: dictionary (optional)
            Holds a tuple of two tuples. The first tuple contains the CSS ID
            selector to find the job title search box and the job title we 
            want to search for (in that order), and the second holds the 
            same for the job location. 
    """
    
    driver = webdriver.Firefox()
    driver.get(query_URL)

    # Wait for the page to render. 
    time.sleep(random.randint(7, 15))
    
    if query_params: 
        # Find search boxes. 
        title_search = driver.find_element_by_id(query_params[0][0])
        location_search = driver.find_element_by_id(query_params[1][0])

        # Clear search boxes and enter text. 
        title_search.clear()
        location_search.clear()
        title_search.send_keys(query_params[0][1])
        location_search.send_keys(query_params[1][1])

        # Execute that query! 
        location_search.send_keys(Keys.ENTER)

    return driver
