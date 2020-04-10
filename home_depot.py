import urllib.parse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def get_driver():
    chrome_options = Options()
    return webdriver.Chrome(chrome_options=chrome_options)


def download_jobs():
    keywords = [
        'Data',
        'Engineer',
    ]
    res = {}

    driver = get_driver()
    for keyword in keywords:

        cards = []

        search_url = f'https://careers.homedepot.com/job-search-results/?keyword={urllib.parse.quote(keyword)}'

        driver.get(search_url)

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'jobTitle')))
            first_page_source = driver.page_source
        except TimeoutException:
            continue

        source = BeautifulSoup(first_page_source, "html.parser")
        listings = source.findAll("div", {"role": "row"})
        for listing in listings[1:]:
            title_obj = listing.find("div", {"class": "jobTitle"})
            title = title_obj.text
            cells = listing.findAll("div", {"role": "cell"})

            url = f'https://careers.homedepot.com/{title_obj.a["href"]}'
            cards.append(
                {"title": title,
                 "url": url,
                 "job_type": cells[1].text,
                 "category": cells[2].text,
                 "location": cells[3].text
                 })

        for card in cards:
            card_detailed = requests.get(card["url"])
            detailed_source = BeautifulSoup(card_detailed.text, "lxml")

            id_obj = detailed_source.find("div", {"class": "id2 ejd-bullet"})
            id_obj.b.decompose()

            card["job_id"] = id_obj.text.replace(" ","")
            desc_obj = detailed_source.find("div", {"data-field": "Position_Description"})
            card["description"] = desc_obj.text

        res[keyword] = cards

    driver.close()

    return res