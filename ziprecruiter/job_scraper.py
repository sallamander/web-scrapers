"""A module for scraping ZipRecruiter for jobs. 

This module is the driver for a ZipRecruiter scraper. It controls the process of
issuing requests, parsing the contents of those requests, and storing the results. 
It also handles the threading and multiprocessing that is used to speed up the
scraping process. 

Usage: 

    python job_scraper.py <job title> <job location> <radius>
"""

import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import multiprocessing
import datetime
import pytz
from functools import partial
from general_utilities.query_utilities import get_html, format_query
from general_utilities.storage_utilities import store_in_mongo
from general_utilities.parsing_utilities import parse_num
from request_threading import RequestInfoThread

def multiprocess_pages(base_URL, job_title, job_location, page_num): 
    """Grab the URLs and other relevant info. from job postings on the page. 

    The ZipRecruiter URL used for job searching takes an additional parameter,   
    `page`, that allows you to start the job search at page 0-20 (20 is the max). 
    Use this to grab job results from multiple pages at once, and then pass jobs
    on to threads to grab relevant info. 

    Args: 
    ----
        base_URL: str 
        job_title: str 
        job_location: str 
        page_start: int 
    """

    url = query_URL + '&page=' + str(page_num)
    html = get_html(url)
    rows = html.select('.job_result')
    threads = []
    mongo_update_lst = []
    for row in rows: 
        thread = RequestInfoThread(row, job_title, job_location)
        thread.start()
        threads.append(thread)
    for thread in threads: 
        thread.join()
        mongo_update_lst.append(thread.json_dct)

    store_in_mongo(mongo_update_lst, 'job_postings', 'ziprecruiter')
    
if __name__ == '__main__': 
    try: 
        job_title = sys.argv[1]
        job_location = sys.argv[2]
        radius = sys.argv[3]
    except IndexError: 
        raise Exception('Program needs a job title, job location, and radius inputted!')

    base_URL = 'https://www.ziprecruiter.com/candidate/search?'
    query_parameters = ['search={}'.format('+'.join(job_title.split())),
            '&location={}'.format('+'.join(job_location.split())), 
            '&radius={}'.format(radius), '&days=5', 
            '&include_near_duplicates=1']

    query_URL = format_query(base_URL, query_parameters)
    html = get_html(query_URL)

    try: 
        num_jobs_txt = str(html.select('#job_results_headline')[0].text)
        num_jobs = int(parse_num(num_jobs_txt, 0))
    except: 
        print('No jobs for search {} in {}'.format(job_title, job_location))
        sys.exit(0)

    current_date = str(datetime.datetime.now(pytz.timezone('US/Mountain')))
    storage_dct = {'job_site': 'ziprecruiter', 'num_jobs': num_jobs, 
            'date': current_date, 'title': job_title, 'location': job_location}
    store_in_mongo([storage_dct], 'job_numbers', 'ziprecruiter')
    
    # Cycle through the pages of jobs to grab all of the info. that we want. Each
    # page holds 20 jobs, so the number of pages we'll cyle through will be
    # num_jobs / 20. The caveat, though is that they only give 20 pages to look
    # through at maximum (hence the min below). 
    pages = min(20, num_jobs // 20 + 1)
    page_positions = range(1, pages + 1)
    execute_queries = partial(multiprocess_pages, query_URL,
            job_title, job_location)
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(execute_queries, page_positions)
