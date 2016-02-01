import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import re
from general_utilities.query_utilities import get_html, format_query

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
    
