import sys
import multiprocessing
import re
from pymongo import MongoClient
from general_utilities import get_html
from functools import partial
from request_threading import RequestInfoThread 

def format_query(job_title, job_location, radius=25): 
    """Structure the Indeed URL to query. 

    The format of the URL used for searching is: 

    www.indeed.com/jobs?q={job_title}&l={location}&radius={radius}

    Args: 
        job_title: String of the job title to search for. 
        job_location: City of where to search for jobs. 
        radius: Within distance to search around the inputted job_location.
    """

    URL='http://www.indeed.com/jobs?q={}&l={}&radius={}&fromage=last&sort=date'.\
        format(job_title, job_location, radius)

    return URL

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
    num_jobs = search_results[2].replace(',', '')
    return num_jobs

def multiprocess_pages(base_URL, job_title, job_location, page_start): 
    """Grab the URLS and other relevant info. from job postings on the page. 

    The Indeed URL used for job searching takes another parameter, 
    `start`, that allows you to start the job search at jobs 10-20, 
    20-30, etc. I can use this to grab job results from multiple pages at
    once. This function takes in the base_URL and then adds that
    start={page_start} parameter to the URL, and the queries. It will grab
    all of the URLS to the actual postings, along with the job title, company, 
    etc. 

    Args: 
        base_URL: String that holds the base URL to add the page_start 
            parameter to. 
        job_title: String holding the job title used for the search
        job_location: String holding the job location used for the search 
        page_start: Integer of what the `start` parameter in the URL should
            be set to. 
    """

    url = base_URL + '&start=' + str(page_start)
    html = get_html(url)
    # Each row corresponds to a job. 
    rows = html.select('.row')
    threads = []
    mongo_update_lst = []
    for row in rows: 
        thread = RequestInfoThread(row, job_title, job_location)
        thread.start()
        threads.append(thread)
    for thread in threads: 
        thread.join()
        mongo_update_lst.append(thread.json_dct)

    store_in_mongo(mongo_update_lst)

def store_in_mongo(lst_of_dcts): 
    """Store the list of dictionaries in Mongo

    Args: 
        lst_of_dicts: List of dictionaries to insert into Mongo. 
    """
    
    client = MongoClient()
    db = client['job_postings']
    collection = db['indeed']
    
    if len(lst_of_dcts) == 1: 
        collection.insert_one(lst_of_dcts)
    else: 
        collection.insert_many(lst_of_dcts)
    
if __name__ == '__main__':
    # I expect that at the very least a job title and job location
    # will be passed in, so I'll attempt to get both of those within
    # a try except and throw an error otherwise. 
    try: 
        job_title = sys.argv[1]
        job_location = sys.argv[2]
    except IndexError: 
        raise Exception('Program needs a job title and job location inputted!')

    # I don't expect a radius, so I'll just check the length first and
    # grab it if its there. 
    if len(sys.argv) == 4: 
        radius = sys.argv[3]
        base_URL = format_query(job_title, job_location, radius)
    else: 
        base_URL = format_query(job_title, job_location)
    
    print base_URL
    # Get HTML for base query.
    html = get_html(base_URL)
    num_jobs_txt = str(html.select('#searchCount'))
    num_jobs = int(parse_num_jobs_txt(num_jobs_txt))
    # Now we need to cycle through all of the job postings that we can and 
    # grab the url pointing to it, to then query it. All of the jobs should 
    # be available via the .turnstileLink class, and then the href attribute
    # will point to the URL. I'm going to multiprocess and multithread this.  
    max_start_position = 1000 if num_jobs >= 1000 else num_jobs
    # I'll need to be able to pass an iterable to the multiprocessing pool. 
    start_positions = range(0, max_start_position, 10)
    execute_queries = partial(multiprocess_pages, base_URL, \
            job_title, job_location)
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(execute_queries, start_positions)
