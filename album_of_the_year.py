from general_utilities import get_html, select_soup, output_data

def rename_keys(input_dct): 
    '''
    Input: Dictionary
    Output: Dictionary

    Rename keys in dictionary to be in readable format for our csv/json output.
    '''

    renaming_dct = {'.artistTitle': "Artist Title", '.albumTitle': "Album Title", 
            '.summaryPoints': "Summary Points", 
            '.summaryPointsMisc': "Summary Points Misc"}
    renamed_input_dct = {renaming_dct[k]: v for k, v in input_dct.iteritems()}
    return renamed_input_dct 

def parse_contents(desired_contents): 
    '''
    Input: Dictionary
    Output: List of Dictionaries

    Essentially flatten the dictionary. Right now, the desired contents
    is a dictionary where each value is a list, and I want to flatten this
    so that there is only 1 value for each key (i.e. a bunch of JSON looking 
    objects). 
    '''
    final_lst = []
    
    lst_idx = 0 # Holds what index to start at in each value list. 
    points_misc_idx = 0 # This one has a slightly different format 
                                # (potentially multiple values per artist/album). 
    while lst_idx < 50: 
        json_dict = {}
        for k, v in desired_contents.iteritems(): 
            values, points_misc_idx = \
                    parse_keys_contents(k, v, points_misc_idx, lst_idx)
            json_dict.update(values)
            
        lst_idx += 1
        final_lst.append(json_dict)

    return final_lst

def parse_keys_contents(k, v, points_misc_idx, lst_idx): 
    '''
    Input: String, List, Integer, Integer
    Output: Dictionary, Integer

    For each of the keys, parse the values for each artist and return 
    a dictionary holding them. 
    '''

    if k == 'Summary Points Misc':
        values, points_misc_idx = parse_points_misc(v, points_misc_idx)
    elif k == 'Summary Points': 
        value = v[lst_idx].split()[0]
        values = {k: value}
    else: 
        values = {k: v[lst_idx]}

    return values, points_misc_idx 

def parse_points_misc(sum_points_misc_lst, points_misc_idx):
    '''
    Input: List, Integer
    Output: Dict, Integer

    The summary points misc attribute is a little different in that it can have
    multiple values per artist. We want to take all of these and store them 
    separately as key value pairs in our final output. For the inputted 
    possibilities list, we are going to grab each one of the possible values 
    that are present for the given artist and output them as a dictionary.                
    ''' 

    values = {} 
    split_text = sum_points_misc_lst[points_misc_idx].split()
    attribute = ' '.join(split_text[:-1])
    value = split_text[-1].replace('(', '').replace(')', '')

    # We know the last possible attribute for each author is "Other", 
    # at which point we need to move on to grabbing the next author's
    # information.
    while attribute.find('Other') == -1:
        values[attribute] = value
        points_misc_idx += 1
        # The value is always the last item present, surrounded by (),
        # and the 1+ items before that are the attributes to which 
        # those points belong. 
        split_text = sum_points_misc_lst[points_misc_idx].split()
        attribute = ' '.join(split_text[:-1])
        value = split_text[-1].replace('(', '').replace(')', '')
    values[attribute] = value
    points_misc_idx += 1

    return values, points_misc_idx 

if __name__ == '__main__':
    URL = 'http://www.albumoftheyear.org/list/summary/2015/'
    soup = get_html(URL) 

    css_selectors = ['.artistTitle', '.albumTitle', '.summaryPoints', '.summaryPointsMisc']
    desired_contents = select_soup(soup, css_selectors)
    desired_contents_renamed = rename_keys(desired_contents)
    final_lst = parse_contents(desired_contents_renamed)
    output_data(final_lst, 'data/test_csv.csv', replace_nulls=0)
