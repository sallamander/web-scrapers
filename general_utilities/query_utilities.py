from bs4 import BeautifulSoup
import requests

def format_query(base_url, query_parameters): 
    """Structure a URL query given inputted parameters. 

    Take the inputted base_url, and add the inputted query_parameters
    to it. 

    Args: 
        base_url: String holding the base_url (mostly the domain)
        query_parameters: List of strings. 
    """

    for query_param in query_parameters: 
        base_url += query_param

    return base_url

def get_html(url): 
    '''
    Take in a URL, issue a get request on that HTML, and then return the 
    parsed content from the response using BeautifulSoup. 

    Args: 
        url: str
            Holds the URL to get the HTML from.
    '''

    try: 
        response = requests.get(url)
        good_response = check_response_code(response)
        if not good_response: 
            # I want to be able to check the bad_url to see what happened.
            print url
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except: 
        error = "Error in contacting the URL - check that it is a valid URL!"
        raise RuntimeError(error)

def check_response_code(response): 
    """Check response status code. 

    Args: 
        response: requests.models.Response
            Holds the response from issuing a `get` request. 
    """

    status_code = response.status_code
    if status_code == 200: 
        return True
    else: 
        print "Status code is not 200, it's {}".format(status_code)
        return False
