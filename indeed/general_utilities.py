import requests
from bs4 import BeautifulSoup

def get_html(URL): 
    """Issue a get request on the inputted URL

    Args: 
        URL: String to issue a get request with. 
    """
    try: 
        response = requests.get(URL)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except: 
        error = "Error in contacting the URL - check that it is valid!"
        raise RuntimeError(error)
