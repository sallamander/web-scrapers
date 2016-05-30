"""A module for grabbing album information. 

This module can be used to grab all available album information from all albums 
on the End Year Critic List. It only grabs information that is available on one 
of the pages at albumoftheyear.org/list/summary/<year>/. For other information, 
specifically User and Critic scores for each of these albums, see 
`albums_of_the_year_lst_full.py`. 
"""

import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
from special_utilities import select_soup, grab_contents_key
from general_utilities.query_utilities import get_html, format_query
from general_utilities.storage_utilities import store_in_mongo

def rename_keys(input_dct): 
    """Rename keys in the dictionary to a more readable format. 

    Args: 
    ----
        input_dct: dct 
            Holds key-value pairs corresponding to a particular album's information. 

    Return: 
    ------
        renamed_input_dct: dct 
    """

    renaming_dct = {'.artistTitle': "Artist Title", '.albumTitle': "Album Title", 
            '.summaryPoints': "Summary Points", 
            '.summaryPointsMisc': "Summary Points Misc"}
    renamed_input_dct = {renaming_dct[k]: v for k, v in input_dct.items()}

    return renamed_input_dct 

def parse_contents(desired_contents): 
    """Parse each album out of the inputted dictionary of lists. 

    The desired contents of album information comes back as a JSON dictionary, 
    where each pair corresponds to a list of values that we desire (e.g. a list 
    of "Artist Title", a list of the "Album Title", etc.). This function will 
    effectively flatten this dictionary of lists into a list of dictionaries,
    where there are as many entries as the length of one of the values lists 
    (i.e. each album gets its own dictionary). 

    Args: 
    ----
        desired_contents: dct
            Dictionary of album titles, album artists, etc. 

    Return: 
    ------
        final_lst: list of dictionaries 
    """
    final_lst = []
    
    lst_idx = 0 # Holds what index to start at in each value list. 
    points_misc_idx = 0 # This one has a slightly different format 
                        # (potentially multiple values per artist/album). 

    while lst_idx < 50: 
        json_dict = {}
        for k, v in desired_contents.items(): 
            values, points_misc_idx = \
                    parse_keys_contents(k, v, points_misc_idx, lst_idx)
            json_dict.update(values)
            
        lst_idx += 1
        final_lst.append(json_dict)

    return final_lst

def parse_keys_contents(k, v, points_misc_idx, lst_idx): 
    """Parse the values for the inputted key. 

    Args: 
    ----
        k: str 
        v: list 
        points_misc_idx: int
            Holds an index to use if the key is equal to "Summary Points Misc"
        lst_idx: int
            Holds the index to use if the key is not equal to "Summary Points Misc"

    Return: 
    ------
        values: dct 
        points_misc_idx: int
            Holds an updated points_misc_idx
    """

    if k == 'Summary Points Misc':
        values, points_misc_idx = parse_points_misc(v, points_misc_idx)
    elif k == 'Summary Points': 
        value = v[lst_idx].split()[0]
        values = {k: value}
    else: 
        values = {k: v[lst_idx]}

    return values, points_misc_idx 

def parse_points_misc(sum_points_misc_lst, points_misc_idx):
    """Parse the "Summary Points Misc" attribute. 

    The summary points misc attribute is a little different in that it can have
    multiple values per artist. This function will take all of these and store 
    them separately as key value pairs in our final output. For the inputted
    possibilities list, grab each one of the possible values that are present 
    and output them as a dictionary.                

    Args: 
    ----
        sum_points_misc_lst: list 
            Holds all of the summary points information for our artists. 
        points_misc_idx: int 

    Return: dct of points values, updated points_misc_idx (int)
    """

    values = {} 
    split_text = sum_points_misc_lst[points_misc_idx].split()
    attribute = ' '.join(split_text[:-1])
    value = split_text[-1].replace('(', '').replace(')', '')

    # We know the last possible attribute for each author is "Other", at which 
    # point we need to move on to grabbing the next author's information.
    while attribute.find('Other') == -1:
        values[attribute] = value
        points_misc_idx += 1
        # The value is always the last item present, surrounded by (), and the 
        # 1+ items before that are the attributes to which those points belong. 
        split_text = sum_points_misc_lst[points_misc_idx].split()
        attribute = ' '.join(split_text[:-1])
        value = split_text[-1].replace('(', '').replace(')', '')
    values[attribute] = value
    points_misc_idx += 1

    return values, points_misc_idx 

if __name__ == '__main__':
    try: 
        year = sys.argv[1]
    except Exception as e: 
        print(e)
        raise Exception('<Usage> Input a year to grab music data for.')

    URL = 'http://www.albumoftheyear.org/list/summary/' + year + '/'
    soup = get_html(URL) 

    css_selectors = ['.artistTitle', '.albumTitle', '.summaryPoints', 
                     '.summaryPointsMisc']
    desired_contents = select_soup(soup, css_selectors)
    desired_contents_text = grab_contents_key(desired_contents, "text")
    desired_contents_renamed = rename_keys(desired_contents_text)
    final_lst = parse_contents(desired_contents_renamed)
    store_in_mongo(final_lst, 'music', 'music_lists')
