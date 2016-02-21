import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import time
import random
import re
from general_utilities.navigation_utilities import issue_driver_query

def parse_num_jobs_txt(num_jobs_txt): 
    """Parse the text that holds the number of jobs to get the number. 


    This will use a regex to find the number of jobs that match our 
    search query. There should only be one number in the num_jobs_txt, 
    and so it should be fairly easy to find. 

    Args: 
        num_jobs_txt: String that contains the number of jobs matching
            the search query. 
    """

    regex = re.compile('\d*[,]?\d+[+]*')
    search_results = re.findall(regex, num_jobs_txt)
    num_jobs = search_results[0].replace(',', '')

    return num_jobs

if __name__ == '__main__':
    # I expect that at the very least a job title and job location
    # will be passed in, so I'll attempt to get both of those within
    # a try except and throw an error otherwise. 
    try: 
        job_title = sys.argv[1]
        job_location = sys.argv[2]
    except IndexError: 
        raise Exception('Program needs a job title and job location inputted!')

    
    # Navigate to the base URL
    base_URL = 'http://www.careerbuilder.com/'
    query_params = (('search-key', job_title), ('search-loc', job_location))
    driver = issue_driver_query(base_URL, query_params)

    # Grab num. jobs
    num_jobs_txt = driver.find_element_by_id('n_pnlJobResultsCount').text
    num_jobs = parse_num_jobs_txt(num_jobs_txt) 
    print num_jobs
