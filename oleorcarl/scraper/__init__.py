import os
from typing import Literal

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from ..database import create_tables
from .carleton import CarletonDirectorySpider, get_carleton_cookies
from .stolaf import OlafDirectorySpider
from .linkedin import OlafLinkedInSpider, CarletonLinkedInSpider
from ..settings import DATABASE_PATH


def scrape(
    targets: list[ Literal[
        "carleton_directory",
        "stolaf_directory",
        "carleton_linkedin",
        "stolaf_linkedin",
    ] ] | Literal["all"],  # fmt: skip
    reset_database=False,
):

    process = CrawlerProcess(get_project_settings())

    if reset_database:
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)

        create_tables()

    if (targets == "all") or ("carleton_directory" in targets):
        get_carleton_cookies()

    spider_from_string = {
        "carleton_directory": CarletonDirectorySpider,
        "stolaf_directory": OlafDirectorySpider,
        "carleton_linkedin": CarletonLinkedInSpider,
        "stolaf_linkedin": OlafLinkedInSpider,
    }

    for target in targets:
        process.crawl(spider_from_string[target])

    process.start()
