import urllib.parse

import arrow
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

    result = {}

    for keyword in keywords:

        cards = []

        search_url = f'https://jobs.lowes.com/search-jobs/{urllib.parse.quote(keyword)}'

        source = download_url(search_url)
        listings = source.find('section',{"id":"search-results-list"}).findAll("li")
        for listing in listings:
            url = f'https://jobs.lowes.com{listing.a["href"]}'
            details = download_url(url)
            pre_date = details.find('span',{"class":"job-date job-info"})
            pre_date.b.decompose()

            pre_job_id = details.find('span', {'class':'job-id job-info'})
            pre_job_id.b.decompose()

            timestamp = arrow.get(details.find(pre_date.text, 'MM/DD/YYYY')).datetime

            card = {
                'title': listing.h2.text,
                'location': " ".join([x.text for x in listing.findAll("span", {"class": "job-location"})][:-1]),
                'job_id': pre_job_id.text,
                'posted': timestamp,
                'url': url,
                'description': details.find('div', {'class': 'ats-description'}).text
            }
            cards.append(card)
        result[keyword] = cards

    return result