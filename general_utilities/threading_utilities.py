"""A module for threading requests and storing their results. 

This module currently provides one class - `HrefQueryThread`. It is meant to help
issue get requests using threading, but avoid creating a new connection to a db 
for each thread. It does this by storing the results of the get request as an 
attribute on the class. 
"""
from threading import Thread
from general_utilities.query_utilities import get_html
from general_utilities.parsing_utilities import find_visible_texts

class HrefQueryThread(Thread): 
    """Threading based class to issue a get request and store the results.  
    
    HrefQueryThread issues a get request on an inputted URL, parses the results 
    using BeautifulSoup, and then stores the results as an attribute available 
    for later access. Motivation for using a class instead of simply passing a
    function to ThreadPool was to avoid creating a new connection with the database   
    (here Mongo) for each get request (this would most likely overwhelm the comp 
    with thread). HrefQueryThread allows for later access of the results of the 
    get request in order to perform multiple uploads/updates to the db. 

    Args: 
    ----
        href: str
            Holds the URL to issue a get request against. 
    """

    def __init__(self, href): 
        super(HrefQueryThread, self).__init__()
        self.href = href

    def run(self): 
        if self.href: 
            self.posting_txt = self._query_href()
        else: 
            self.posting_txt = ''

    def _query_href(self): 
        """Grab the text from the href. 

        Returns: str of visible text from the href. 
        """
        try:
            soup = get_html(self.href)

            texts = soup.findAll(text=True)
            visible_texts = filter(find_visible_texts, texts)
        except Exception as e: 
            print(e)
            visible_texts = ['SSLError', 'happened']

        return ' '.join(visible_texts)

