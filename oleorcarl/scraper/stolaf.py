import logging
import re
import typing
import scrapy
from scrapy.http import FormRequest

from .pipelines import GrownupFilter, UniqueFilter, FaceEmbedder, DBSaver
from .items import ModelItem
from ..database import Student
from ..settings import OLAF_DIRECTORY_URL


if typing.TYPE_CHECKING:
    from scrapy.http import HtmlResponse
    from scrapy.selector import Selector


class OlafDirectorySpider(scrapy.Spider):
    name = "St. Olaf Directory Scraper"
    allowed_domains = ["stolaf.edu"]

    custom_settings = {
        "ITEM_PIPELINES": {
            GrownupFilter: 100,
            UniqueFilter: 101,
            FaceEmbedder: 300,
            DBSaver: 1000,
        }
    }

    def start_requests(self):
        yield FormRequest(
            OLAF_DIRECTORY_URL,
            formdata={"title": "student"},
            method="POST",
            callback=self.parse,
        )

    def parse(self, response: "HtmlResponse", **kwargs):
        del kwargs  # unused

        pre = ".c-faculty__"  # wordpress css prefix

        students = list(response.css(".student"))
        self.log(f"Found {len(students)} Olaf students. Scraping...", logging.INFO)

        for div in students:
            div: "Selector"  # for intellisense

            item = ModelItem(Student())

            item["name"] = div.css(f"{pre}name::text").get()
            item["email"] = div.css(f"{pre}email::text").get()
            item["year"] = (
                int(yr[0]) 
                if (yr := div.css(f"{pre}title::text").re("\d{2}")) 
                else None
            )  # fmt: skip
            item["departments"] = div.css(f"{pre}department::text").getall()
            item["pronouns"] = div.css(f"{pre}pronouns::text").get([])
            item["school"] = "stolaf"
            item["source"] = self.name

            if item["pronouns"]:
                item["pronouns"] = re.split(r",|/ ?", item["pronouns"].strip("()"))

            yield item

            self.log(f"{item['email']} sent to pipeline", logging.DEBUG)
