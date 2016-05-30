"""A module to use for navigating the JS in webpages. 

This module currently provides a single function (`issue_driver_query`), which 
opens up a Selenium Browser to help navigate around the JS in web page searches.
"""

import time 
import random
import os
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def issue_driver_query(query_URL, query_params=None):
    """Issue the initial query in order to start scraping.

    First, issue a `.get()` request on the `query_URL` - this will either hold 
    the homepage from which we will need to use the driver program to perform a 
    search, or will be the query_URL of the final search (a Selenium Driver might 
    not be necessary for the initial query). If the former, then use the
    `query_params` to grab the search boxes and enter the query parameters. If 
    the latter, then simply return the Selenium driver. 

    All of the `time.sleep()` calls are used in an attempt to appear as an 
    actual user (e.g. not a bot). 

    Args: 
    ----
        query_URL: str
        query_params (optional): tuple 
            Holds a tuple of two tuples. The first tuple contains the CSS ID
            selector to find the job title search box and the job title we 
            want to search for (in that order), and the second holds the 
            same for the job location. 

    Returns: 
    -------
        driver: Selenium webdriver 
    """
    
    # Allows us to run Selenium in a headless fashion (on AWS, for example). 
    if os.environ['USER'] == 'ubuntu': 
        display = Display(visible=0, size=(800, 600))
        display.start()
    
    driver = webdriver.Firefox()
    # Wait long enough for page rendering before searching for an element. 
    driver.implicitly_wait(10)
    driver.get(query_URL)
    time.sleep(3)

    # Monster has started using a `beta` version of the site, and the Monster scraper
    # is not built for it. Here, keep issuing the query to get the non-beta version. 
    while 'beta' in driver.current_url: 
        driver.close()
        driver = webdriver.Firefox()
        driver.implicitly_wait(10)
        driver.get(query_URL)

    # Wait extra time for the page to render. 
    time.sleep(random.randint(7, 15))
    
    if query_params: 
        # Find search boxes. 
        title_search = driver.find_element_by_id(query_params[0][0])
        location_search = driver.find_element_by_id(query_params[1][0])

        # Clear search boxes and enter text. 
        title_search.clear()
        location_search.clear()
        title_search.send_keys(query_params[0][1])
        time.sleep(random.randint(3, 5))
        location_search.send_keys(query_params[1][1])

        # Execute that query! 
        location_search.send_keys(Keys.ENTER)

    return driver
