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
    Input: String
    Output: HTML content 

    Take in a URL, issue a get request on that HTML, and then return the 
    parsed content from the response using BeautifulSoup. 
    '''

    try: 
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except: 
        error = "Error in contacting the URL - check that it is a valid URL!"
        raise RuntimeError(error)
