from general_utilities import get_html, select_soup, \
                output_data_to_mongo, grab_contents_key

def process_album_title_hrefs(album_title_hrefs, album_titles): 
    '''
    Input: List
    Output: Dictionary

    For each of the inputted hrefs, go to the href and grab the overall 
    critic and user scores. 
    '''
    base_url = 'http://www.albumoftheyear.org'
    final_json_lst = []
    for idx, href in enumerate(album_title_hrefs.values()[0]):
        soup = get_html(base_url + href)
        center_content = select_soup(soup, '#centerContent').values()[0][0]
        user_score = int(find_score(center_content, 'USER SCORE'))
        critic_score = int(find_score(center_content, 'CRITIC SCORE'))
        json_dct = {'Album Title': album_titles[idx], "User Score": user_score, 
                    "Critic Score": critic_score}

        final_json_lst.append(json_dct)

    return final_json_lst

def find_score(content, score_str): 
    '''
    Input: bs4.element.Tag
    Output: Integer

    Parse the elements in the inputted bs4.element.Tag to grab the 
    average user score for the inputted album. 
    '''

    content_txt = content.text
    score_idx = content_txt.find(score_str) 
    score_str_len = len(score_str)
    beg_idx = score_idx + score_str_len
    end_idx = beg_idx + 2    
    score = content_txt[beg_idx:end_idx]

    return score

if __name__ == '__main__': 
    URL = 'http://www.albumoftheyear.org/list/summary/2015/'
    soup = get_html(URL) 

    css_selectors = ['.albumTitle']
    album_titles_contents = select_soup(soup, css_selectors)
    album_titles = grab_contents_key(album_titles_contents, 'text').values()[0]
    album_title_links = grab_contents_key(album_titles_contents, 'a')
    album_title_hrefs = grab_contents_key(album_title_links, 'href')

    final_json_lst = process_album_title_hrefs(album_title_hrefs, album_titles)
    output_data_to_mongo(final_json_lst, 'music', 'music_lists', 
            keys=["Album Title"])

