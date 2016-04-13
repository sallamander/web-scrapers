"""A module to use for parsing text from websites.

This module currently provides three functions.The first for 
parsing numbers out of text, the second for parsing 
out and returning the "visible" parts of a web page (e.g.
there are certain tags that we want to avoid pretty much 
all the time), and the third for parsing out an inputted
regex out of inputted text. 
"""

import re

def parse_num(input_txt, desired_idx): 
    """Parse the text to pull out any numbers. 

    Use a regex to find any numbers that are in the inputted text. It 
    will also search for an additional '+' at the end of those numbers,
    since a current use case for this is to search for either the number 
    of total job postings (for the job related web-scrapers), which 
    sometimes contains a '+' (e.g. in  the case that we see 1000+ for 
    the number of jobs). 

    Args: 
    ----
        input_txt: str
            Contains the string that we want to search for numbers. 
        desired_idx: int
            Holds the idx of what to grab from the regex result list. 

    Returns: str holding number of jobs, or empty list
    """

    regex = re.compile('\d*[,]?\d+')
    search_results = re.findall(regex, input_txt)

    # We don't want the comma in any of our numbers 
    if search_results: 
        desired_num = search_results[desired_idx].replace(',','')
        return desired_num
    else: 
        print 'Empty list returned from parse_num'
        return []

def find_visible_texts(element): 
    """Parse the element to figure out whether or not to keep it.  

    Filter out certain elements from the text. Keep only text that 
    is visible on the web page, returning True if it is or False 
    if it isn't. 

    Args: 
    ----
        element: bs4 Element tag 
            Holds the element to keep or discard. 

    Returns: bool
    """

    if element.parent.name in ['style', '[document]', 'head', 'title']:
        return False
    else: 
        return True

def parse_regex(regex, input_txt): 
    """Parse the inputted text using the inputted regex. 

    Args: 
    ----
        regex: str
            Text to use as the regular expression to search for. 
        input_text: str
            Text to search over for the regular expression. 

    Return: 
    ------
        matches: list 
           This may be empty, depending on whether not any matches to 
           the `regex` is found. 
        parsed_txt: str
            `input_txt` with any text matching the `regex` removed. 
    """

    matches = re.findall(regex, input_txt)
    parsed_txt = re.sub(regex, '', input_txt)

    return matches, parsed_txt
