"""A module for grabbing user and critic scores of albums. 

This module can be used to grab the user and critic scores for all albums on the 
End Year Critic List on albumoftheyear.org.
"""

import os
import sys
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
from special_utilities import select_soup, grab_contents_key
from general_utilities.query_utilities import get_html, format_query
from general_utilities.storage_utilities import store_in_mongo

def process_album_title_hrefs(album_title_hrefs, album_titles): 
    """Grab the critic and user scores for each inputted href. 

    Loop over the hrefs in `album_title_hrefs`, issue a get request on the URL 
    associated with that href, and then parse the content to grab the User and 
    Critic scores for that album. Store the User and Critic scores in a dictionary
    along with the Album title. Output it all in a list, with one entry per href. 

    Args: 
    ----
        album_title_hrefs: list of strings 
        album_titles: list of strings

    Return: 
    ------
        final_json_lst: list
    """

    base_url = 'http://www.albumoftheyear.org'
    final_json_lst = []
    album_title_hrefs_lst = list(album_title_hrefs.values())
    for idx, href in enumerate(album_title_hrefs_lst[0]):
        soup = get_html(base_url + href)

        center_content_lst = list(select_soup(soup, '#centerContent').values())
        center_content = center_content_lst[0][0]
        user_score = int(find_score(center_content, 'USER SCORE'))
        critic_score = int(find_score(center_content, 'CRITIC SCORE'))

        json_dct = {'Album Title': album_titles[idx], "User Score": user_score, 
                    "Critic Score": critic_score}
        final_json_lst.append(json_dct)

    return final_json_lst

def find_score(content, score_str): 
    """Parse the inputted content to grab the inputted score. 

    Args: 
    ---- 
        content: bs4.element.Tag
        score_str: str
            Holds the CSS selector used to identify and grab the score from the page. 

    Return: 
    ------
        score: str
    """    

    content_txt = content.text
    score_idx = content_txt.find(score_str) 
    score_str_len = len(score_str)
    beg_idx = score_idx + score_str_len
    end_idx = beg_idx + 2    
    score = content_txt[beg_idx:end_idx]

    return score

if __name__ == '__main__': 
    try: 
        year = sys.argv[1]
    except Exception as e: 
        print(e)
        raise Exception('<Usage> Input a year to grab data music data for.')

    URL = 'http://www.albumoftheyear.org/list/summary/' + year + '/'
    soup = get_html(URL) 

    css_selectors = ['.albumTitle']
    album_titles_contents = select_soup(soup, css_selectors)
    album_titles_lst = list(grab_contents_key(album_titles_contents, 'text').values())
    album_titles = album_titles_lst[0]
    album_title_links = grab_contents_key(album_titles_contents, 'a')
    album_title_hrefs = grab_contents_key(album_title_links, 'href')

    final_json_lst = process_album_title_hrefs(album_title_hrefs, album_titles)
    store_in_mongo(final_json_lst, 'music', 'music_lists', key="Album Title")

