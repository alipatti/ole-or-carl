from typing import Literal
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.scraper.carleton import CarletonDirectorySpider, get_carleton_cookies
from src.scraper.stolaf import OlafDirectorySpider


def scrape(site: Literal["carleton", "stolaf", "all"]):

    process = CrawlerProcess(get_project_settings())

    if site in {"carleton", "all"}:
        get_carleton_cookies()
        process.crawl(CarletonDirectorySpider)

    if site in {"stolaf", "all"}:
        process.crawl(OlafDirectorySpider)

    process.start()


if __name__ == "__main__":
    scrape("carleton")
