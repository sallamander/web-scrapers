# ZipRecruiter Web-Scraper

This folder contains a web-scraper to scrape [ZipRecruiter](https://www.ziprecruiter.com/) for jobs. With the way it is built, it will scrape all of the jobs that ZipRecruiter returns for a given job title, job location, and radius. In order to get all jobs that it returns (rather than being limited by the first 20 pages), it by default searches for only those jobs posted in the last 5 days (I'll describe in the usage how to change this). The scraper will give back all of the information that you could get for every job within the search query (title, location, easy apply (if it is)), and the actual job posting text at the post's URL (if you can get it - a very small number of places hide it from requests).

## Usage

This scraper is built to scrape ZipRecruiter for an inputted job title, job location, and radius (in that order). To use it, you can simply call it from the command line as follows: 

```python 
python job_scraper.py 'Data Science' 'Denver' 25
```

Usage notes: 

* Note the quotation marks around both 'Data Science' and 'Denver'. `job_scraper.py` expects three arguments, and without quotes would interpret the above as 4 arguments. The bottom line here is that if you are going to put in multiple words for either the job title or job location, they need to be quoted (so note here that Denver doesn't actually need to be quoted). Otherwise, the quotes are optional. 
* This scraper is built to store the resulting data in Mongo. As such, it expects that a Mongo server is up and running. By default, it will store the results in a database named `job_postings`, and a collection called `zip_recruiter`. If you would like to change this, you can change the argument values passed to the `store_in_mongo` function call in the `job_scraper.py` file.  
* This scraper is built to multiprocess and multithread the requests. By default it is set to use all available cores. If you would like to change this, you can alter the argument passed to the `multiprocessing.Pool()` constructor in the `__main__` block of the `job_scraper.py` file. 
* As mentioned above, this defaults to only grabbing those job postings in the last 5 days. If you'd like, you can change this in the `job_scraper.py` file, where the `query_parameters` list variable is created. You would simply need to adjust the `&days=5` parameter to some other number (you might need to check the ZipRecruiter site to see what numbers it actually accepts). 


