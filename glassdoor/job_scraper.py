import sys
from selenium import webdriver

def issue_query(driver, job_title, job_location): 
    """
    """
    pass

if __name__ == '__main__':
    # I expect that at the very least a job title and job location
    # will be passed in, so I'll attempt to get both of those within
    # a try except and throw an error otherwise. 
    try: 
        job_title = sys.argv[1].split()
        job_location = sys.argv[2].split()
    except IndexError: 
        raise Exception('Program needs a job title and job location inputted!')

    base_URL = 'https://www.glassdoor.com/index.htm'
    driver = webdriver.Firefox()
    driver.get(base_URL)
    issue_query(driver, job_title, job_location)
