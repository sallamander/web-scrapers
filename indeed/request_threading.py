from threading import Thread

class RequestInfoThread(Thread): 
    """Inherits from Thread so I can store results of my threading. 

    I want to be able to return something from my threading. This 
    class will allow me to do that - perform all of the requesting 
    and data gathering that I want to do, but store the results on 
    the class so that I can access them later. 
    """

    def __init__(self, row): 
        super(RequestInfoThread, self).__init__()
        self.row = row

    def run(self): 
        self.json_dct = self._request_info()

    def _request_info(self): 
        """Grab relevant information from the row and store it in mongo.

        Each row will contain a number of features that we will want to 
        grab. Then, we'll grab its href attribute, which will actually hold 
        a link to the job posting. We'll query that link and grab all the 
        text that is there. 

        Args: 
            row: bs4 Tag holding relevant info. 
        """

        json_dct = {}
        # Holds the actual CSS selector as the key and the label I want to store
        # the info. as as the key. 
        possible_attributes = {'.jobtitle': "job_title", '.company': "company", \
                '.location': "location", '.date': "date", \
                '.iaLabel': "easy_apply"}
        for k, v in possible_attributes.iteritems(): 
            res = self.row.select(k)
            if res: 
                json_dct[v] = res[0].text
        # Now let's grab the href and pass that on to another function to 
        # get that info. 
        href = self.row.find('a').get('href')
        json_dct['href'] = href
        json_dct['posting_txt'] = self._query_href(href)

        return json_dct

    def _query_href(self, href): 
        """Grab the text from the href. 

        Now we want to actually follow the href that is given in the 
        job posting, and grab the posting text from there. 

        Args: 
            href: String of the href to the job posting. 
        """
        try:
            html = get('http://www.indeed.com' + href) if href.startswith('/') \
                    else get(href)
            soup = BeautifulSoup(html.content, 'html.parser')

            texts = soup.findAll(text=True)
            visible_texts = filter(self._visible, texts)
        except: 
            visible_texts = ['SSLError', 'happened']

        return ' '.join(visible_texts)

    def _visible(self, element): 
        """If the element is of the type we want to keep, return True. 

        We want to filter out certain elements from the text that we will 
        get back. We only want to keep text that is visible on the web page, 
        and we'll use this function to do this. 

        Args: 
            element: String element to keep in or filter out. 
        """
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', element):
            return False
        return True