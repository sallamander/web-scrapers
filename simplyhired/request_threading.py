import datetime
import re
from threading import Thread
from requests import get
from bs4 import BeautifulSoup


class RequestInfoThread(Thread): 
    """Inherits from Thread so I can store results of my threading. 

    I want to be able to return something from my threading. This 
    class will allow me to do that - perform all of the requesting 
    and data gathering that I want to do, but store the results on 
    the class so that I can access them later. 
    """
    pass
