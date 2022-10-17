import re
import typing
import scrapy
from scrapy.http import FormRequest
from scrapy.selector import Selector

from ..scraper.items import ModelItem
from ..database import Student
from ..settings import OLAF_DIRECTORY_URL


if typing.TYPE_CHECKING:
    from scrapy.http import HtmlResponse


class OlafDirectorySpider(scrapy.Spider):
    name = "stolaf"
    allowed_domains = ["stolaf.edu"]

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

        for div in response.css(".student"):
            div: Selector  # for intellisense

            item = ModelItem(Student())

            item["name"] = div.css(f"{pre}name::text").get()
            item["email"] = div.css(f"{pre}email::text").get()
            item["year"] = int(f"20{div.css(f'{pre}title::text').get()[-2:]}")
            item["departments"] = div.css(f"{pre}department::text").getall()
            item["pronouns"] = div.css(f"{pre}pronouns::text").get([])
            item["school"] = "stolaf"

            if item["pronouns"]:
                item["pronouns"] = re.split(r",|/ ?", item["pronouns"].strip("()"))

            yield item
