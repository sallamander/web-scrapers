import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import time
import random
from general_utilities.navigation_utilities import issue_driver_query
from general_utilities.parsing_utilities import parse_num

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
    num_jobs = int(parse_num(num_jobs_txt, 0)) 
