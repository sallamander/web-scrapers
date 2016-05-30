# Glassdoor Web-Scraper

This folder contains a web-scraper to scrape [Glassdoor](https://www.glassdoor.com/index.htm) for jobs. It will scrape all the jobs that Glassdoor will allow you to for a given job title and job location (Glassdoor fairly aggressively prevents scrapers, and so you won't get much if you try). It will give back all of the information that you could get for every job within a search query (title, location, date posted, stars, etc.), and the actual job posting text at the post's URL (if you can get it - a very small number of places hide it from requests). 

## Usage

This scraper is built to scape Glassdoor for an inputted job title and job location. To use it, you can simply call it from the command line as follows: 

```python 
python job_scraper.py 'Data Science' 'Denver'
```

Usage notes: 
* Note the quotation marks around both 'Data Science' and 'Denver'. `job_scraper.py` expects three arguments, and without quotes would interpret the above as 4 arguments. The bottom line here is that if you are going to put in multiple words for either the job title or job location, they need to be quoted (so note here that Denver doesn't actually need to be quoted). Otherwise, the quotes are optional. 
* This scraper is built to store the resulting data in Mongo. As such, it expects that a Mongo server is up and running. By default, it will store the results in a database named `job_postings`, and a collection called `glassdoor`. If you would like to change this, you can change the argument values passed to the `store_in_mongo` function call in the `job_scraper.py` file.  
* This scraper is a little different than others in this repo., in the sense that it uses Selenium to scrape. Selenium is actually going to fire up a web browser from wherever you are running this program, and then use that browser to scrape. As such, a browser will pop up when you run this scraper. By default, it will use Firefox (so you'll have to have that installed). If you'd like to change it, you can do that in the `__main__` block in the `job_scraper.py` file.  

**Note**: This one is not as maintained as others in this repository. Glassdoor does a pretty decent job of blocking scrapers, and as a result I focused my efforts elsewhere in terms of job posting sites to scrape. 
