# Indeed Web-Scraper

This folder contains a web-scraper to scrape [Indeed](http://www.indeed.com/) for jobs. With the way it is built, it will scrape all the jobs that Indeed will allow you to for a given job title, job location, and radius (I say 'all that it will allow you' because they won't show more than 1000 results). It will give back all of the information that you could get for every job within a search query (title, location, date posted, salary (if available), etc.), and the actual job posting text at the post's URL (if you can get it - a very small number of places hide it from requests). 

## Usage 

This scraper is built to scrape Indeed for an inputted job title, job location, and radius (in that order). To use it, you can simply call it from the command line as follows: 

```python 
python job_scraper.py 'Data Science' 'Denver' 25
```

Usage notes: 

* Note the quotation marks around both 'Data Science' and 'Denver'. `job_scraper.py` expects three arguments, and without quotes would interpret the above as 4 arguments. The bottom line here is that if you are going to put in multiple words for either the job title or job location, they need to be quoted (so note here that Denver doesn't actually need to be quoted). Otherwise, the quotes are optional. 
* This scraper is built to store the resulting data in Mongo. As such, it expects that a Mongo server is up and running. By default, it will store the results in a database named `job_postings`, and a collection called `indeed`. If you would like to change this, you can change the argument values passed to the `store_in_mongo` function call in the `job_scraper.py` file.  
* This scraper is built to multiprocess and multithread the requests. By default it is set to use all available cores. If you would like to change this, you can alter the argument passed to the `multiprocessing.Pool()` constructor in the `__main__` block of the `job_scraper.py` file. 


