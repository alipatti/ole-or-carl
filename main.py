import os
from typing import Literal

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.database import create_tables
from src.scraper.carleton import CarletonDirectorySpider, get_carleton_cookies
from src.scraper.stolaf import OlafDirectorySpider
from src.settings import DATABASE_PATH


def scrape(site: Literal["carleton", "stolaf", "all"], reset_database=False):

    process = CrawlerProcess(get_project_settings())

    if reset_database:
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)

        create_tables()

    if site in {"carleton", "all"}:
        get_carleton_cookies()
        process.crawl(CarletonDirectorySpider)

    if site in {"stolaf", "all"}:
        process.crawl(OlafDirectorySpider)

    process.start()


if __name__ == "__main__":
    scrape("all", reset_database=False)
