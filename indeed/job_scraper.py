import sys
import re
from general_utilities import get_html

def format_query(job_title, job_location, radius=25): 
    """Structure the Indeed URL to query. 

    The format of the URL used for searching is: 

    www.indeed.com/jobs?q={job_title}&l={location}&radius={radius}

    Args: 
        job_title: String of the job title to search for. 
        job_location: City of where to search for jobs. 
        radius: Within distance to search around the inputted job_location.
    """

    URL='http://www.indeed.com/jobs?q={}&l={}&radius={}'.format(job_title,
            job_location, radius)

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
    
    # Get HTML for base query.
    html = get_html(base_URL)
    num_jobs_txt = str(html.select('#searchCount'))
    num_jobs = parse_num_jobs_txt(num_jobs_txt)
