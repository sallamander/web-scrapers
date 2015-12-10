from general_utilities import get_html, select_soup, \
        output_data, grab_contents_key

if __name__ == '__main__':
    lists_url = 'http://www.albumoftheyear.org/lists.php'

    soup = get_html(lists_url)
    critics_content = select_soup(soup, '.criticListBlockTitle')
    critics_names = grab_contents_key(critics_content, "text")
    critics_links = grab_contents_key(critics_content, 'a')
    critics_hrefs = grab_contents_key(critics_links, 'href')

