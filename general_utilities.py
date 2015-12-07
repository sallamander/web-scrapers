import requests
from bs4 import BeautifulSoup

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

def select_soup(soup, css_selectors): 
    '''
    Input: Beautiful Soup parsedHTML, List of Strings 
    Output: Dictionary 

    For the given css_selectors, return a list for all of the inputs
    matching those results. 
    '''

    contents_dict = {selector: soup.select(selector) \
            for selector in css_selectors}
    contents_dict = {k: [html.text for html in v] \
            for k, v in contents_dict.iteritems()}
    return contents_dict

