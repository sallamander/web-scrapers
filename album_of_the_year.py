from general_utilities import get_html, select_soup, output_data

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
    summary_points_misc_idx = 0 # This one has a slightly different format 
                                # (potentially multiple values per artist/album). 
    while lst_idx < 50: 
        json_dict = {}
        for k, v in desired_contents.iteritems(): 
            if k == 'Summary Points Misc':
                values = []
                value = v[summary_points_misc_idx]
                while value.find('Other') == -1:
                    values.append(value)
                    summary_points_misc_idx += 1
                    value = v[summary_points_misc_idx]
                values.append(value)
                summary_points_misc_idx += 1
            else: 
                values = v[lst_idx]
        
            json_dict[k] = values
        lst_idx += 1
        final_lst.append(json_dict)

    return final_lst

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

if __name__ == '__main__':
    URL = 'http://www.albumoftheyear.org/list/summary/2015/'
    soup = get_html(URL) 

    css_selectors = ['.artistTitle', '.albumTitle', '.summaryPoints', '.summaryPointsMisc']
    desired_contents = select_soup(soup, css_selectors)
    desired_contents_renamed = rename_keys(desired_contents)
    final_lst = parse_contents(desired_contents_renamed)
    output_data(final_lst, 'test_csv')
