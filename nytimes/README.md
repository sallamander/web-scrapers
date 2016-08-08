# NYTimes Web-Scraper

This folder contains a web-scraper to scrape the [New York Times](http://www.nytimes.com/). With an [API Key](https://developer.nytimes.com/), it is built to use the [Article Search API](https://developer.nytimes.com/article_search_v2.json) and pull article metadata as well as article text for a given set of specified parameters (see [parameter options](https://developer.nytimes.com/article_search_v2.json#/README)). 

## Usage

This scraper is built to scrape all article metadata and text for an inputted date range. To use it, you can simply call it from the command line as follows: 

```python
python article_scraper.py 20121230 20121231
```

Usage Notes: 

* This script is built to store the resulting data in Mongo. As such, it expects that a Mongo server is up and running when the script is run. By default, it will store all of the article metadata as well as the article text in a database named `nytimes`, and a collection named `gen_articles`. If you would like to change this, you'll have to change multiple pieces of the script: 
    1. The `__enter__` method of `NYTPageScraper`
    2. The `dump_articles` method of `NYTPageScraper`
    3. The `db_name` and `coll_name` arguments passed into the `NYTArticleScraper` 
       in the `__main__` block. 
* This script contains two classes for scraping - `NYTPageScraper` for grabbing article metadata and `NYTArticleScraper` for grabbing article text. If the script is run with a starting and ending date (as it is above), then both classes are used, and the article metadata and text is scraped for the inputted date range. If neither a starting or ending date is inputted (which is a valid use case for the script), then it is assumed that there is article metadata in the `nytimes` Mongo collection that does not have associated article text, and just the `NYTArticleScraper` is run. 
* This scraper is not currently built to take advantage of multithreading, but is something that could be built in. 
