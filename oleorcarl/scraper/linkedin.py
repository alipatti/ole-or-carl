from urllib.parse import urlencode

import scrapy
from scrapy.http import TextResponse, Request
import jmespath
import yaml

from ..settings import LINKEDIN_API_URL, LINKEDIN_HEADER_PATH


class LinkedInSpider(scrapy.Spider):
    name = "LinkedIn Scraper"
    allowed_domains = ["linkedin.com"]

    school_number: int
    n_per_page = 50

    def start_requests(self):

        with open(LINKEDIN_HEADER_PATH, "rt", encoding="utf8") as f:
            headers = yaml.full_load(f)

        for n_page in range(0, 100, self.n_per_page):

            params = dict(
                start=n_page * self.n_per_page,
                count=self.n_per_page,
                facetSchool=f"List({self.school_number})",
                origin="organization",
                q="people",
            )

            url = f"{LINKEDIN_API_URL}?{urlencode(params, safe='()')}"

            yield Request(url, headers=headers)

    def parse(self, response: TextResponse, **kwargs):
        del kwargs  # unused

        self.log(f"Scraping LinkedIn API for {self.school_number} ")

        img_urls = jmespath.search(
            "included[].picture[].join(``, [rootUrl, artifacts[-1].fileIdentifyingUrlPathSegment])",
            response.json(),
        )

        yield from img_urls


class CarletonLinkedInSpider(LinkedInSpider):
    name = "Carleton LinkedIn Scraper"
    school_number = 20029


class OlafLinkedInSpider(LinkedInSpider):
    name = "Olaf LinkedIn Scraper"
    school_number = ...
