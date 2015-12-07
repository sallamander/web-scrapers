from general_utilities import get_html, select_soup

if __name__ == '__main__':
    URL = 'http://www.albumoftheyear.org/list/summary/2015/'
    soup = get_html(URL) 

    css_selectors = ['.artistTitle', '.albumTitle', '.summaryPoints', '.summaryPointsMisc']
    desired_contents = select_soup(soup, css_selectors)

