# CareerBuilder Web-Scraper

This folder contains a web-scraper to scrape [CareerBuilder](http://www.careerbuilder.com/) for jobs. With the way it is built, it will scrape all the jobs that Career Builder will allow you to for a given job title and job location. It will give back all of the information that you could get for every job within a search query (title, location, date posted, etc.), and the actual job posting text at the post's URL (if you can get it - a very small number of places hide it from requests). 

## Usage 

This scraper is built to scrape CareerBuilder for an inputted job title, job location, and radius (in that order). To use it, you can simply call it from the command line as follows: 

```python 
python job_scraper.py 'Data Science' 'Denver' 
```

Usage notes: 

* Note the quotation marks around both 'Data Science' and 'Denver'. `job_scraper.py` expects three arguments, and without quotes would interpret the above as 4 arguments. The bottom line here is that if you are going to put in multiple words for either the job title or job location, they need to be quoted (so note here that Denver doesn't actually need to be quoted). Otherwise, the quotes are optional. 
* This scraper is built to store the resulting data in Mongo. As such, it expects that a Mongo server is up and running. By default, it will store the results in a database named `job_postings`, and a collection called `careerbuilder`. If you would like to change this, you can change the argument values passed to the `store_in_mongo` function call in the `job_scraper.py` file.  
* This scraper is a little different than others in this repo., in the sense that it uses Selenium to scrape. Selenium is actually going to fire up a web browser from wherever you are running this program, and then use that browser to scrape. As such, a browser will pop up when you run this scraper. By default, it will use Firefox (so you'll have to have that installed). If you'd like to change it, you can do that in the `__main__` block in the `job_scraper.py` file.  
