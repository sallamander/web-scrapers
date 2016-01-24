import sys

def format_query(job_title, job_location, radius=25): 
    """Structure the Indeed URL to query. 

    The format of the URL used for searching is: 

    www.indeed.com/jobs?q={job_title}&l={location}&radius={radius}

    Args: 
        job_title: String of the job title to search for. 
        job_location: City of where to search for jobs. 
        radius: Within distance to search around the inputted job_location.
    """

    URL='www.indeed.com/jobs?q={}&l={}&radius={}'.format(job_title, 
            job_location, radius)

    return URL

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

