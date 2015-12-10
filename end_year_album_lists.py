from general_utilities import get_html, select_soup, \
        output_data, grab_contents_key

if __name__ == '__main__':
    url = 'http://www.albumoftheyear.org/lists.php'

    soup = get_html(url)
    desired_content = select_soup(soup, '.criticListBlockTitle')
    desired_links = grab_contents_key(desired_content, 'a')
    desired_hrefs = grab_contents_key(desired_links, 'href')
