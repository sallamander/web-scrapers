import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
from general_utilities.query_utilities import format_query

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

    base_URL = 'http://www.simplyhired.com/search?'
    query_parameters = ['q={}'.format('+'.join(job_title)), 
            '&l={}'.format('+'.join(job_location)), '&mi={}'.format(radius),
            '&fdb=7', '&sb=dd']
    
    query_URL = format_query(base_URL, query_parameters)
