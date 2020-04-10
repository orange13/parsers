import urllib.parse

import datetime
import requests
from bs4 import BeautifulSoup


def download_url(url):
    s = requests.session()
    headers = {}
    response = s.get(url,
                     headers=headers,
                     verify=False)
    return BeautifulSoup(response.text, 'html.parser')


def download_jobs():
    keywords = [
        'Data',
        'Engineer',
    ]
    res = {}

    for keyword in keywords:

        cards = []

        search_url = f'https://jobs.boeing.com/search-jobs/{urllib.parse.quote(keyword)}/185-18469/1'

        source = download_url(search_url)
        listings = source.find('section', {"id": "search-results-list"}).findAll("li")
        for listing in listings:
            raw_date = listing.find('span', {"job-date-posted"}).text
            url = f'https://jobs.boeing.com{listing.a["href"]}'
            details = download_url(url)
            raw_job_id = details.find("span", {"class": "job-id"})
            raw_job_id.b.decompose()
            descr = details.find("div", {"class": "job-description-wrap"})

            cards.append(
                {
                    "title": listing.h3.text,
                    "location": listing.find('span', {"class": "job-location"}).text,
                    "posted": datetime.datetime.strptime(raw_date, "%m/%d/%Y"),
                    "url": url,
                    "job_id": raw_job_id.text.replace(" ",""),
                    "description":descr.text
                }
            )
        res[keyword] = cards

    return res

print(download_jobs())