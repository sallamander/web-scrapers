from bs4 import BeautifulSoup 
import requests

if __name__ == '__main__':
    response = requests.get('http://www.albumoftheyear.org/list/summary/2015/')
    soup = BeautifulSoup(response.content, 'html.parser')
    artist_titles = soup.select('.artistTitle')
    album_titles = soup.select('.albumTitle')
    album_points = soup.select('.summaryPoints')
    album_places = soup.select('.summaryPointsMisc')

    artist_titles_contents = [soup.text for soup in artist_titles]
    album_titles_contents = [soup.text for soup in album_titles]
    album_points_contents = [soup.text for soup in album_points]
    album_places_contents = [soup.text for soup in album_places]

    # print artist_titles_contents
    # print album_titles_contents
    # print album_points_contents
    print album_places_contents
