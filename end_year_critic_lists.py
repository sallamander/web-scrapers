from general_utilities import get_html, select_soup, grab_contents_key
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

    base_individual_list_url = 'http://www.albumoftheyear.org'
    critics_hrefs_values = critics_hrefs.values()[0]

    final_lst = []
    css_selectors = ['.listLargeTitle']
    json_dct = defaultdict(list)
    regex = re.compile("^\d+\.")
    for idx, critic_name in enumerate(critics_names.values()[0]): 

        critic_url = base_individual_list_url + critics_hrefs_values[idx]
        soup = get_html(base_individual_list_url + critics_hrefs_values[idx]) 
        critic_list_content = select_soup(soup, css_selectors)
        critic_lst_content_vals = critic_list_content.values()[0]
        num_albums_idx = len(critic_lst_content_vals) 
        critic_lst_content_vals.reverse()
        for idx2, values in enumerate(critic_lst_content_vals, 1):
            post = soup.select('#post-' + str(num_albums_idx))[0]
            album_title_text = post.select('.listLargeTitle')[0].text
            critic_score_idx = post.text.find('Critic Score')
            beg_idx, end_idx = critic_score_idx + 12, critic_score_idx + 14
            critic_score = post.text[beg_idx:end_idx]
            user_score_idx = post.text.find('User Score')
            beg_idx, end_idx = user_score_idx + 10, user_score_idx + 12
            user_score = post.text[beg_idx:end_idx]
            value_text = values.text
            rating = regex.findall(album_title_text)
            if len(rating) >= 1: 
                rating = int(rating[0].replace('.', ''))
                album_title = album_title_text.split('-')[-1]\
                        .encode('ascii', 'xmlcharrefreplace').strip()
                critic_dct = {'Critic' : critic_name, 'Rating' : rating, 
                        'User Score': user_score, 'Critic Score': critic_score}
                json_dct[album_title].append(critic_dct)
                num_albums_idx -= 1
            else: 
                rating = idx2
                album_title = album_title_text.split('-')[-1]\
                        .encode('ascii', 'xmlcharrefreplace').strip()
                critic_dct = {'Critic' : critic_name, 'Rating' : rating, 
                        'User Score': user_score, 'Critic Score': critic_score}
                json_dct[album_title].append(critic_dct)
                num_albums_idx -= 1

    return json_dct 

if __name__ == '__main__':
    lists_url = 'http://www.albumoftheyear.org/lists.php'

    soup = get_html(lists_url)
    critics_content = select_soup(soup, '.criticListBlockTitle')
    critics_names = grab_contents_key(critics_content, "text")
    critics_links = grab_contents_key(critics_content, 'a')
    critics_hrefs = grab_contents_key(critics_links, 'href')

    output = grab_critics_info(critics_names, critics_hrefs)
