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
        job_title = sys.argv[1]
        job_location = sys.argv[2]
    except IndexError: 
        raise Exception('Program needs a job title and job location inputted!')

    # Navigate to the base URL
    base_URL = 'http://www.careerbuilder.com/'
    driver = webdriver.Firefox()
    driver.get(base_URL)

    # Wait for everything to render, and then perform the job search.
    time.sleep(random.randint(7, 15))
    issue_query(driver, job_title, job_location)
