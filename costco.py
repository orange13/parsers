import requests
from bs4 import BeautifulSoup

URL = "https://chm.tbe.taleo.net/chm02/ats/careers/v2/searchResults?org=COSTCO&cws=41"
BASE_URL = "https://chm.tbe.taleo.net"

DEBUG = False


class Parser:
    def __init__(self):
        self.html_text = ""
        self.session = requests.Session()

    def open_local_html(self, name):
        with open(name, "r") as file:
            return file.read()

    def post(self, url, data):
        res = self.session.post(url, data=data)
        res.raise_for_status()

        if DEBUG:
            with open("debug.html", "w") as file:
                file.write(res.text)
        self.soup = BeautifulSoup(res.text, "html.parser")
        return res.content

    def get(self, url, **kwargs):
        res = self.session.get(url, **kwargs)
        res.raise_for_status()

        if DEBUG:
            with open("debug_get.html", "w") as file:
                file.write(res.text)
        self.soup = BeautifulSoup(res.text, "html.parser")

        return res.text

    def find_selectors(self, el, config, soup=None):
        if not soup:
            soup = self.soup
        classes = soup.findAll(el, config)
        return classes


class CostcoPaser:
    def __init__(self, job_title):
        self.parser = Parser()
        self.search_data = {"act": "search",
                            "org": "COSTO",
                            "cws": 41,
                            "WebPage": "JSRCH_V2",
                            "WebVersion": 2,
                            "keywords": job_title}
        self.res = []

    def _html_to_links(self):
        soaped_links = self.parser.find_selectors("div", {"class": "oracletaleocwsv2-accordion-head-info"})
        soaped_next = self.parser.find_selectors("a", {"class": "jscroll-next"})

        for soap_link in soaped_links:
            divs = [x.text for x in soap_link.findChildren("div")]
            self.res.append(
                {"url": soap_link.h4.a["href"],
                 "category": divs[0],
                 "location": divs[1],
                 "title": soap_link.h4.text
                 })

        return soaped_next

    def _one_job_html_to_json(self):
        pre_number_soap = self.parser.find_selectors("div", {"class": "well oracletaleocwsv2-job-description"})
        number = self.parser.find_selectors(
            "div", {"class": "col-xs-12 col-sm-4 col-md-12"}, pre_number_soap[0])[1].strong.text

        pre_description = self.parser.find_selectors("div", {"class": "col-xs-12 col-sm-12 col-md-8"})
        res = pre_description[0]

        # Remove all scripts from description
        for _ in res.findChildren("script"):
            res.script.decompose()

        # Remove all buttons and shares from description
        for match in self.parser.find_selectors("div", {
            "class": "oracletaleocwsv2-button-navigation oracletaleocwsv2-job-description clearfix"}, soup=res):
            match.decompose()

        desc = res.text

        return {"number": number,
                "description": desc}

    def analyze_job_links(self):
        """Iterate through links and extract data to self.res"""
        for item in self.res:
            self.parser.get(item["url"])
            add_info = self._one_job_html_to_json()
            item["order_number"] = add_info["number"].replace('\n', '')
            item["description"] = add_info["description"]

    def process(self):
        self.parser.post(url=URL, data=self.search_data)
        soaped_next = self._html_to_links()

        # Collect links to jobs to self.job_links
        if soaped_next:
            url = "{}{}".format(BASE_URL, soaped_next[0]["href"])
            while soaped_next:
                self.parser.get(url)
                soaped_next = self._html_to_links()
                if soaped_next:
                    url = "{}{}".format(BASE_URL, soaped_next[0]["href"])

        self.analyze_job_links()
        return self.res


def main(job_title):
    return CostcoPaser(job_title=job_title).process()

#Example: main("software engineer")