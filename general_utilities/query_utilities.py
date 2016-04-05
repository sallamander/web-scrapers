"""A module to help out with web requests. 

This module currently provides a couple of helper
functions for web requests - `format_query`, `get_hmtl`, 
and `check_response_code`. Each is pretty simplistic. 
"""

from bs4 import BeautifulSoup
import requests

def format_query(base_url, query_parameters): 
    """Structure a URL query given inputted parameters. 

    Take the inputted `base_url`, and add the inputted 
    `query_parameters` to it. 

    Args: 
    ----
        base_url: str holding the base_url (mostly the domain)
        query_parameters: list of strings. 

    Returns: str holding the formatted query URL.
    """

    for query_param in query_parameters: 
        base_url += query_param

    return base_url

def get_html(url): 
    """Issue a get request on the inputted URL and parse the results.  

    Issue a get request on the inputted `url`, and then parse the 
    content using BeautifulSoup. 

    Args: 
    ----
        url: str
            Holds the URL to get the HTML from.
    
    Returns: bs4.BeautifulSoup object of parsed html
    """

    try: 
        response = requests.get(url)
        good_response = check_response_code(response)
        if not good_response: 
            # Check the bad_url to see what happened.
            print 'Bad URL: {}'.format(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except: 
        error = "Error in contacting the URL - check that it is a valid URL!"
        raise RuntimeError(error)

def check_response_code(response): 
    """Check the response status code. 

    Args: 
    ----
        response: requests.models.Response
            Holds the response from issuing a `get` request. 

    Returns: bool
    """

    status_code = response.status_code
    if status_code == 200: 
        return True
    else: 
        print "Status code is not 200, it's {}".format(status_code)
        return False
