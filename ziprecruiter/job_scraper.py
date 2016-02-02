import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import re
import multiprocessing
from functools import partial
from general_utilities.query_utilities import get_html, format_query
from general_utilities.storage_utilities import store_in_mongo
from request_threading import RequestInfoThread

def parse_num_jobs_txt(num_jobs_txt): 
    """Parse the text that holds the number of jobs to get the number. 

    This will use a regex to find the number of jobs that match 
    our search query. There will be three numbers in the search query - 
    the first two will refer to the page results that we are on (e.g. 
    1 of 10, 10 to 20, etc.), whereas the third number will be the 
    actual number of jobs. It will then perform any parsing (i.e. remove
    a comma if it is 4 digits). 

    Args: 
        num_jobs_txt: String that contains the number of jobs matching 
            the search query.   
    """

    regex = re.compile('\d*[,]?\d+')
    search_results = re.findall(regex, num_jobs_txt)
    num_jobs = search_results[0].replace(',', '')
    return num_jobs

def multiprocess_pages(base_URL, job_title, job_location, page_num): 
    """Grab the URLs and other relevant info. from job postings on the page. 

    The ZipRecruiter URL used for job searching takes an additional 
    parameter, `page`, that allows you to start the job search at page 
    0-20 (20 is the max). I can use this to grab job results from multiple
    pages at once. This function here takes in the base_URL, and then 
    adds that page={page_num} parameter to the URL, and then queries it. 
    It passes the results on to a thread to grab the details from each 
    job posting. 

    Args: 
        base_URL: String that holds the base URL to add the page_num 
            parameter to. 
        job_title: String holding the job title used for the search 
        job_location: String holding the job location used for the search
        page_num: Integer of what the `page` paramter in the URL should 
            be set to. 
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
    # I expect that at the very least a job title, job location, and radius
    # will be passed in, so I'll attempt to get both of those within
    # a try except and throw an error otherwise. 
    try: 
        job_title = sys.argv[1].split()
        job_location = sys.argv[2].split()
        radius = sys.argv[3]
    except IndexError: 
        raise Exception('Program needs a job title, job location, and radius inputted!')

    base_URL = 'https://www.ziprecruiter.com/candidate/search?'
    query_parameters = ['search={}'.format('+'.join(job_title)),
            '&location={}'.format('+'.join(job_location)), 
            '&radius={}'.format(radius), '&days=5', 
            '&include_near_duplicates=1']

    query_URL = format_query(base_URL, query_parameters)

    # Get HTML for base query. 
    html = get_html(query_URL)
    num_jobs_txt = str(html.select('#job_results_headline')[0].text)
    num_jobs = int(parse_num_jobs_txt(num_jobs_txt))
    
    # Here we'll cycle through the pages of jobs to grab all of the 
    # info. that we want. Each page holds 20 jobs, so the number of 
    # pages we'll cyle through will be num_jobs / 20. The caveat, though
    # is that they only give 20 pages to look through at maximum (hence 
    # the min below). 
    pages = min(21, num_jobs / 20 + 1)
    page_positions = range(0, pages)
    for page_position in page_positions: 
        multiprocess_pages(query_URL, job_title, job_location, page_position)
    '''
    execute_queries = partial(mutliprocess_pages, query_URL,
            job_title, job_location)
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(execute_queries, page_positions)
    '''
