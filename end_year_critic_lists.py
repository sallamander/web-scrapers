from general_utilities import get_html, select_soup, \
        grab_contents_key, output_data_to_mongo
from albums_of_year_lst_ind import find_score
from collections import defaultdict
import re

def grab_critics_info(critics_names, critics_hrefs):
    '''
    Input: Dictionary, Dictionary
    Output: List of Dictionaries 

    For each of the critic lists, pull all of the relevant information 
    from their page. Return the information in a list of dictionary, 
    where there is one dictionary for each critic list. 
    '''

    critics_hrefs_values = critics_hrefs.values()[0]

    json_dct = defaultdict(list)
    # Compile this here since we only need to do this once.
    regex = re.compile("^\d+\.")
    # Cycle through each one of the critics. 
    for idx, critic_name in enumerate(critics_names.values()[0]): 
        
        critic_lst_content_vals, soup = \
                get_critic_lst_content(critics_hrefs_values, idx)
        num_albums_idx = len(critic_lst_content_vals) 
        # Cycle through each one of the ablums on the critics lists. 
        for idx2, values in enumerate(critic_lst_content_vals, 1):
            # Each album is stored in a separate "Post-#". 
            post = soup.select('#post-' + str(num_albums_idx))[0]

            album_title, album_title_txt = get_album_title(post)            
            '''
            critic_score = find_score(post, 'Critic Score') 
            user_score = find_score(post, 'User Score')
            '''

            rating_text = regex.findall(album_title_txt)
            rating = parse_rating(rating_text, idx2)

            critic_dct = {'Critic' : critic_name, 'Rating' : rating}
            # 'User Score': user_score, 'Critic Score': critic_score}
            json_dct[album_title].append(critic_dct)
            num_albums_idx -= 1

    return json_dct 

def get_critic_lst_content(critics_hrefs_values, idx):
    '''
    Input: List, Integer
    Output: List, BeautifulSoup object

    For the critic href at the inputted idx in the critics_hrefs_values, grab
    all of the items with the class '.listLargeTitle'. This will then be used 
    to cycle through each one of them and grab information from them. 
    '''

    base_individual_list_url = 'http://www.albumoftheyear.org'
    css_selectors = ['.listLargeTitle']

    critic_url = base_individual_list_url + critics_hrefs_values[idx]
    soup = get_html(base_individual_list_url + critics_hrefs_values[idx]) 

    critic_lst_content_vals = select_soup(soup, css_selectors).values()[0]
    # We reverse them because they are posted from the highest ranked 
    # (worst album) to the lowest rank (i.e. Post-1 is the highest ranked 
    # album on the critic list).
    critic_lst_content_vals.reverse()

    return critic_lst_content_vals, soup

def get_album_title(post): 
    '''
    Input: bs4.element.Tag
    Output: String, String

    Grab the album title from our inputted post. We are returning
    the full text in addition to just the album title because the 
    full text potentially has the rating in it. 
    '''

    album_title_txt = post.select('.listLargeTitle')[0].text
    split_album_title_txt = album_title_txt.split('-')

    if len(split_album_title_txt) == 2 or 'Sleater' in split_album_title_txt:
        album_title = split_album_title_txt[-1]\
                .encode('ascii', 'xmlcharrefreplace').strip()
    else: 
        album_title = '-'.join(split_album_title_txt[1:])\
                .encode('ascii', 'xmlcharrefreplace').strip()

    return album_title, album_title_txt

def parse_rating(rating_txt, idx): 
    '''
    Input: String, Integer
    Output: Integer

    Get the rating for the current album that we are looking at on the critics
    list. This falls into one of two scenarios: (1). Either the rating is 
    already in the inputted rating_txt, and we just need to parse it, or (2). 
    It's not there, and we need to assign it the inputted idx (this why we 
    reversed the list in the get_critic_lst_content() function - the idx 
    starts from one but the lists starts from the highest ranked (worst album). 
    '''

    if len(rating_txt) >= 1: 
        rating = int(rating_txt[0].replace('.', ''))
    else: 
        rating = idx

    return rating

def format_output(raw_output): 
    '''
    Input: Dictionary
    Output: List

    Reformat the dictionary so that we can easily insert it into our Mongo
    database. Basically, right now the dictionary consists of album titles 
    as the keys, and lists of their ratings on critics lists as the values. 
    We need it to be a list of dictionaries in the format: 
    
    {'Album Title': album_title, 'Critics Scores' : critics_scores_lst}
    '''

    output_lst = [{"Album Title": k, "Critics Scores": v} for \
            k, v in raw_output.iteritems()]
    return output_lst

if __name__ == '__main__':
    lists_url = 'http://www.albumoftheyear.org/lists.php'

    soup = get_html(lists_url)
    critics_content = select_soup(soup, '.criticListBlockTitle')
    critics_names = grab_contents_key(critics_content, "text")
    critics_links = grab_contents_key(critics_content, 'a')
    critics_hrefs = grab_contents_key(critics_links, 'href')

    raw_output = grab_critics_info(critics_names, critics_hrefs)
    formatted_output = format_output(raw_output)
    output_data_to_mongo(formatted_output, 'music', 'music_lists', 
                        key="Album Title")

