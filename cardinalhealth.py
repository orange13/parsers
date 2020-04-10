import requests
import re
from bs4 import BeautifulSoup


def process(job_title):
    res = []
    known_ids = []
    page_num = 1

    is_search_ended = False

    search_data = {"keyword": job_title}
    session = requests.Session()

    initial = session.post("https://jobs.cardinalhealth.com/search/searchresults?jtStartIndex=0&jtPageSize=12",
                           data=search_data)
    data_init = initial.json()["Records"]

    for init_record in data_init:
        jsoned_record = init_record["TrackingObject"]
        id = init_record["ID"]
        if id in known_ids:
            continue

        known_ids.append(id)
        country = jsoned_record["CountryNamesJson"][0]
        title = jsoned_record["TitleJson"]
        if country == "United States":
            slug = re.sub("[^a-zA-Z0-9_\u3400-\u9FBF\s-]", "", re.sub(" ", "-", title.lower()))

            url = "{}/{}/{}".format(
                "https://jobs.cardinalhealth.com/search/jobdetails",
                slug,
                id
            )
            res.append({
                "title": title,
                "reference_number": jsoned_record["ReferenceNumberJson"],
                "posted_date": jsoned_record["PostedDateJson"],
                "location": jsoned_record["LocationNamesJson"][0],
                "type": jsoned_record["TypeNameJson"],
                "country": country,
                "url": url
            })

    while not is_search_ended:
        is_search_ended = True

        url = "https://jobs.cardinalhealth.com/search/searchresults?jtStartIndex={}&jtPageSize=12".format(page_num * 12)
        page_num += 1

        iterate_request = session.post(url, data=search_data)
        data_iterate_req = iterate_request.json()["Records"]
        for iter_record in data_iterate_req:
            jsoned_record = iter_record["TrackingObject"]
            id = iter_record["ID"]

            if id in known_ids:
                continue

            is_search_ended = False
            known_ids.append(id)

            country = jsoned_record["CountryNamesJson"][0]
            title = jsoned_record["TitleJson"]
            if country == "United States":
                ##Slug method from JS script of the site
                slug = re.sub("[^a-zA-Z0-9_\u3400-\u9FBF\s-]", "", re.sub(" ", "-", title.lower()))

                url = "{}/{}/{}".format(
                    "https://jobs.cardinalhealth.com/search/jobdetails",
                    slug,
                    id
                )
                res.append({
                    "title": title,
                    "reference_number": jsoned_record["ReferenceNumberJson"],
                    "posted_date": jsoned_record["PostedDateJson"],
                    "location": jsoned_record["LocationNamesJson"][0],
                    "type": jsoned_record["TypeNameJson"],
                    "country": country,
                    "url": url
                })

    for item in res:
        url = item["url"]

        data = session.get(url).text
        soaped = BeautifulSoup(data, "html.parser")

        raw_desc = soaped.find_all("div", {"class": "Description"})
        soaped_desc = raw_desc[0]

        for match in soaped_desc.findAll("div", {"class": "Apply Bottom"}):
            match.decompose()

        item["description"] = soaped_desc.text

    return res

#Example : process("analyst")
