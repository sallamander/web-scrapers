# Monster Web-Scraper

This folder contains a web-scraper to scrape [Monster](http://www.monster.com/) for jobs. With the way it is built, it will scrape all the jobs that Monster will provide for a given job title, job location, and radius. It will give back all of the information that you get for each job (title, location, date posted, posting company, etc.), and the actual job posting text at the post's URL (if you can get it - a very small number of places hide it from requests).  

## Usage 

This scraper is built to scrape Monster for an inputted job title, job location, and radius (in that order). To use it, you can simply call it from the command line as follows: 

```python 
python job_scraper.py 'Data Science' 'Denver' 30
```

Usage notes: 

* Note the quotation marks around both 'Data Science' and 'Denver'. `job_scraper.py` expects three arguments, and without quotes would interpret the above as 4 arguments. The bottom line here is that if you are going to put in multiple words for either the job title or job location, they need to be quoted (so note here that Denver doesn't actually need to be quoted). Otherwise, the quotes are optional. 
* This scraper is built to store the resulting data in Mongo. As such, it expects that a Mongo server is up and running. By default, it will store the results in a database named `job_postings`, and a collection called `monster`. If you would like to change this, you can change the argument values passed to the `store_in_mongo` function call in the `job_scraper.py` file.  
* This scraper is built to multithread requests. If you'd like to change that, then you can alter the way it is run in the `job_scraper.py` file. Specifically, you'd have to alter it in the `scrape_job_page` function. 
* Monster only allows an inputted radius to be a factor of 10 (so something like 25 wouldn't work - it'll just round it down to 20, from what I've seen). 
* This scraper is a little different than others in this repo., in the sense that it uses Selenium to scrape. Selenium is actually going to fire up a web browser from wherever you are running this program, and then use that browser to scrape. As such, a browser will pop up when you run this scraper. By default, it will use Firefox (so you'll have to have that installed). If you'd like to change it, you can do that in the `__main__` block in the `job_scraper.py` file.  
