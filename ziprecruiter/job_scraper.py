import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
from general_utilities.query_utilities import get_html, format_query

if __name__ == '__main__': 
    # I expect that at the very least a job title, job location, and radius
    # will be passed in, so I'll attempt to get both of those within
    # a try except and throw an error otherwise. 
    try: 
        job_title = sys.argv[1].split()
        job_location = sys.argv[2]
        radius = sys.argv[3]
    except IndexError: 
        raise Exception('Program needs a job title, job location, and radius inputted!')

    base_URL = 'https://www.ziprecruiter.com/candidate/search?'
    query_parameters = ['search={}'.format('+'.join(job_title)),
            '&location={}'.format(job_location), '&radius={}'.format(radius), 
            '&days=5']

    query_URL = format_query(base_URL, query_parameters)

    # Get HTML for base query. 
    html = get_html(query_URL)

    
