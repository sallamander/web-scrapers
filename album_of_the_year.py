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
    points_misc_keys_set = get_points_misc_keys(desired_contents["Summary Points Misc"])
    while lst_idx < 50: 
        json_dict = {}
        for k, v in desired_contents.iteritems(): 
            if k == 'Summary Points Misc':
                values, points_misc_idx = parse_points_misc(v, 
                        points_misc_keys_set, points_misc_idx)
            else: 
                values = {k: v[lst_idx]}
        
            json_dict.update(values)
        lst_idx += 1
        final_lst.append(json_dict)

    return final_lst

def get_points_misc_keys(points_misc_lst): 
    '''
    Input: List
    Output: Set 
    
    Parse the potential names for the values of points misc (i.e. Top 10, 
    Top 25, 3rd Place, etc.), and output them in a list.
    '''
    
    # Each potential name for the values is some number of words followed by the 
    # number of points it got in that category. So we want to just grab all of the
    # words before the number, which is the last thing. 

    points_misc_keys = set([' '.join(val.split()[:-1]) for val in points_misc_lst])
    return points_misc_keys

def parse_points_misc(sum_points_misc_lst, possibilities_lst, 
        sum_points_misc_idx):
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
    split_text = sum_points_misc_lst[sum_points_misc_idx].split()
    attribute = ' '.join(split_text[:-1])
    value = split_text[-1].replace('(', '').replace(')', '')

    # We know the last possible attribute for each author is "Other".
    while attribute.find('Other') == -1:
        values[attribute] = value
        sum_points_misc_idx += 1
        split_text = sum_points_misc_lst[sum_points_misc_idx].split()
        attribute = ' '.join(split_text[:-1])
        value = split_text[-1].replace('(', '').replace(')', '')
    values[attribute] = value
    sum_points_misc_idx += 1

    return values, sum_points_misc_idx 

if __name__ == '__main__':
    URL = 'http://www.albumoftheyear.org/list/summary/2015/'
    soup = get_html(URL) 

    css_selectors = ['.artistTitle', '.albumTitle', '.summaryPoints', '.summaryPointsMisc']
    desired_contents = select_soup(soup, css_selectors)
    desired_contents_renamed = rename_keys(desired_contents)
    final_lst = parse_contents(desired_contents_renamed)
    output_data(final_lst, 'test_csv.csv')
