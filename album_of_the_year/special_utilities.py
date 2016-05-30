"""A module for special utilites used for scraping albumoftheyear.org

This module contains helper functions used in during the scraping of albumoftheyear.org. 
"""
import requests
import pandas as pd
from pymongo import MongoClient
from bs4 import BeautifulSoup

def select_soup(soup, css_selectors): 
    """Return a list of all inputs matching the inputted CSS selectors. 

    Args: 
    ----
        soup: bs4.BeautifulSoup Object
        css_selectors: list of strings

    Return: 
    ------
        contents: dct
    """
    
    css_selectors = mk_list(css_selectors)
    
    contents = {selector: soup.select(selector) \
                for selector in css_selectors}
    return contents

def mk_list(potential_lst): 
    """Throw the input into a list of it is not already a list. 

    Args: 
    ----
        potential_lst: varied 
            May or may not be a list. 

    Return: list 
    """

    if isinstance(potential_lst, list): 
        return potential_lst
    else: 
        return [potential_lst]

def grab_contents_key(contents, key): 
    """Grab the desired key from each soup item in contents values list. 

    Args:
    ----
        contents: dct 
            Holds soup items grabbed form a page. 
        key: str
            Holds what part of each soup item to grab. 

    Return: 
    ------
        contents_dct: dct
    """

    if key == 'text': 
        contents_dct = {}
        for k, v in contents.items(): 
            contents_dct[k] = [html.text.encode('ascii', 'xmlcharrefreplace') 
                                   .decode('utf-8') for html in v] 
    elif key == 'a': 
        contents_dct = {k: [tag.find(key) for tag in v if tag is not None] \
                for k, v in contents.items()}
    elif key == 'href': 
        contents_dct = {k: [tag.get(key) for tag in v if tag is not None] \
                for k, v in contents.items()}

    return contents_dct

def output_data_to_file(lst, filepath, file_format="csv", replace_nulls=None):
    """Save the inputted lst to the filepath. 

    Save the list of dictionaries to the filepath location, using the inputted 
    format (default is csv). Fill nulls with the passed in argument if specified.

    Args: 
    ----
        lst: list of dictionaries
        filepath: str
        file_format (optional): str
        replace_nulls (optional): varied
    """

    df = pd.DataFrame(lst)
    if replace_nulls is not None: 
        df = df.fillna(replace_nulls)

    if file_format=="json": 
        df.to_json(filepath)
    else: 
        df.to_csv(filepath, index=False)

