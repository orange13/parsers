import requests
from bs4 import BeautifulSoup

def process(job_title):
    res = []
    session = requests.Session()
    search_data = {"act": "search",
                   "org": "COSTO",
                   "cws": 41,
                   "WebPage": "JSRCH_V2",
                   "WebVersion": 2,
                   "keywords": job_title}

    first_req = session.post("https://chm.tbe.taleo.net/chm02/ats/careers/v2/searchResults?org=COSTCO&cws=41",
                             data=search_data)
    soap = BeautifulSoup(first_req.text, 'html.parser')
    soaped_links = soap.findAll("div", {"class": "oracletaleocwsv2-accordion-head-info"})
    soaped_next = soap.findAll("a", {"class": "jscroll-next"})

    for soap_link in soaped_links:
        divs = [x.text for x in soap_link.findChildren("div")]
        res.append(
            {"url": soap_link.h4.a["href"],
             "category": divs[0],
             "location": divs[1],
             "title": soap_link.h4.text
             })

    if soaped_next:
        url = "{}{}".format("https://chm.tbe.taleo.net", soaped_next[0]["href"])
        while soaped_next:
            url_data = session.get(url).text
            soap = BeautifulSoup(url_data, 'html.parser')
            soaped_next = soap.findAll("a", {"class": "jscroll-next"})
            soaped_links = soap.findAll("div", {"class": "oracletaleocwsv2-accordion-head-info"})

            for soap_link in soaped_links:
                divs = [x.text for x in soap_link.findChildren("div")]
                res.append(
                    {"url": soap_link.h4.a["href"],
                     "category": divs[0],
                     "location": divs[1],
                     "title": soap_link.h4.text
                     })

            if soaped_next:
                url = "{}{}".format("https://chm.tbe.taleo.net", soaped_next[0]["href"])

    for item in res:
        data = session.get(item["url"]).text
        one_link_soap = BeautifulSoup(data, 'html.parser')
        pre_number_soap = one_link_soap.findAll("div", {"class": "well oracletaleocwsv2-job-description"})
        number = one_link_soap.findAll(
            "div", {"class": "col-xs-12 col-sm-4 col-md-12"}, pre_number_soap[0])[1].strong.text

        pre_description = one_link_soap.findAll("div", {"class": "col-xs-12 col-sm-12 col-md-8"})
        pre_res = pre_description[0]

        # Remove all scripts from description
        for _ in pre_res.findChildren("script"):
            pre_res.script.decompose()

        # Remove all buttons and shares from description
        for match in pre_res.findAll("div", {
            "class": "oracletaleocwsv2-button-navigation oracletaleocwsv2-job-description clearfix"}):
            match.decompose()

        desc = pre_res.text

        item["order_number"] = number.replace('\n', '')
        item["description"] = desc

    return res