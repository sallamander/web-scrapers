# AlbumOfTheYear Web-Scraper

This folder contains a web-scraper built to scrape [albumoftheyear](http://www.albumoftheyear.org/), and more specifically the end of the year music lists available at this site (see [here](http://www.albumoftheyear.org/list/summary/2016/)). By default that link to the end of the year lists is set to the current year (now 2016), but you can just change that year to look at previous years. 

This scraper is built to grab a number of pieces of info. for all of the albums that are on the `Music Year End List Aggregate` for the inputted year. The first thing it will do is go through and grab all of the information available at the `albumoftheyear.org/list/summary/{year}/` page. This includes the album title, artist, total points for the year, and the number of votes it received in certain categories (1st place, 2nd place, etc.). The second thing it will do is grab the overall user and critic score for each album (it'll do this by clicking on the href and scraping from that href). The third thing it will grab is where each of these albums fell on various critic lists. This is only available for the most recent year once it is outputted, though (so for now this is 2015). As a result of this last point, if a year prior to 2015 is inputted, only the first two pieces of info. (all but the critic list info.) from above will be grabbed. 

## Usage

It's mentioned above that there are three pieces of info. that are grabbed for all of the albums that are on the `Music Year End List Aggregate` for a user inputted year. These three pieces are all grabbed via three separate python scripts in this folder (the first piece via `albums_of_the_year_lst_ind.py`, the second piece via `albums_of_the_year_lst_full.py`, and the third via `end_year_critic_lists.py`) and then stored in a Mongo database. You can run each of these pieces individually (in order), or you can run the bash script stored in this folder (`grab_music_info.sh`), which will run all three, and take care of only running the third if the year is not 2015 (see above for why).  

No matter how you run it, you have to input a year (except for the `end_year_critic_lists.py` file). If you're running it via the individual scripts themselves, then you would type in the following: 

```python 
python albums_of_the_year_lst_ind.py 2015
python albums_of_the_year_lst_full.py 2015
python end_year_critic_lists.py 
```

**Note**: Remember the `end_year_critic_lists.py` is run for the most recent list posted to the site, and as such doesn't require an inputted year. 

If you wanted to run it via the bash script, you would type in the following: 

```bash 
bash grab_music_info.sh 2015
```

**Note**: This will run the first two python scripts above with the inputted year, and only run the third if the inputted year matches the most recent list posted to the site (2015). 

Usage Notes:  

* This scraper is built to store the resulting data in Mongo. As such, it expects that a Mongo server is up and running. By default, it will store the results in a database named `music`, and a collection called `music_lists`. If you would like to change this, you can change the argument values passed to the `store_in_mongo` function call in the three python files. 
