import requests
import pandas as pd
from pymongo import MongoClient
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
    
    css_selectors = mk_list(css_selectors)
    
    contents = {selector: soup.select(selector) \
                for selector in css_selectors}
    return contents

def mk_list(potential_lst): 
    '''
    Input: Varied
    Output: List

    If the inputted type is not a list, then throw it into a list. 
    '''

    if isinstance(potential_lst, list): 
        return potential_lst
    else: 
        return [potential_lst]

def grab_contents_key(contents, key): 
    '''
    Input: Dictionary, String
    Output: Dictionary

    For the inputted contents, grab the desired key from each soup item 
    in the values lists of the dictionary.
    '''
    if key == 'text': 
        contents_dct = {k: [html.text.encode('ascii', 'xmlcharrefreplace') \
                for html in v] for k, v in contents.iteritems()}
    elif key == 'a': 
        contents_dct = {k: [tag.find(key) for tag in v if tag is not None] \
                for k, v in contents.iteritems()}
    elif key == 'href': 
        contents_dct = {k: [tag.get(key) for tag in v if tag is not None] \
                for k, v in contents.iteritems()}

    return contents_dct

def output_data_to_file(lst, filepath, file_format="csv", replace_nulls=None):
    '''
    Input: List of dictionaries, String, String, Object
    Output: Saved file

    Save the list of dictionaries to the filepath location, 
    using the inputted format (default is csv). Fill nulls with 
    the passed in argument if specified.
    '''

    df = pd.DataFrame(lst)
    if replace_nulls is not None: 
        df = df.fillna(replace_nulls)

    if file_format=="json": 
        df.to_json(filepath)
    else: 
        df.to_csv(filepath, index=False)

def output_data_to_mongo(data, database_name, table_name, key=None): 
    '''
    Input: List, String, String, List
    Output: Data saved to Mongo

    Save each of the json dictionaires to the inputted table_name in a Mongo
    database and datatable. 
    '''

    mongo_client = MongoClient()
    database = mongo_client[database_name]
    datatable = database[table_name]
    
    if key is not None: 
        output_data_to_mongo_by_key(data, datatable, key) 
    else: 
        datatable.insert_many(data)

def output_data_to_mongo_by_key(data, table_name, key):
    '''
    Input: List, String, List
    Output: Data saved to Mongo
    '''

    for album in data: 
        key_value = album[key]
        # Not the most efficient way to do this, but this allows it 
        # to be really general. 
        for k, v in album.iteritems():
            table_name.update_one({key: key_value}, {'$set': {k :v}})
