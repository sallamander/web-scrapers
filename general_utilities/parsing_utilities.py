import re

def parse_num(input_txt, desired_idx): 
    """Parse the text to pull out any numbers. 

    This will use a regex to find any numbers that are in the inputted
    text. As a caveat, it will also search for an additional '+' at the 
    end of those numbers. This is because one current use case for this
    is to search for either the number of total job postings (for the 
    job related web-scrapers), which sometimes contains a '+' (i.e. in 
    the case that we see 1000+ for the number of jobs). 

    Args: 
        input_txt: str
            Contains the string that we want to search for numbers. 
        desired_idx: int
            Holds the idx of what to grab from the regex result list. 
    """

    regex = re.compile('\d*[,]?\d+')
    search_results = re.findall(regex, input_txt)

    # We don't want the comma in any of our numbers 
    # (we want 1000 instead of 1,000). 
    if search_results: 
        desired_num = search_results[desired_idx].replace(',','')
        return desired_num
    else: 
        print 'Empty list returned from parse_num'
        return []

def find_visible_texts(element): 
    """If the element is of the type we want to keep, return True. 

    We want to filter out certain elements from the text that we will 
    get back. We only want to keep text that is visible on the web page, 
    and we'll use this function to do this. 

    Args: 
        element: bs4 Element tag 
    """
    if element.parent.name in ['style', '[document]', 'head', 'title']:
        return False
    else: 
        return True
