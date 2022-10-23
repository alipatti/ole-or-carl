import logging
from typing import TYPE_CHECKING

from scrapy import logformatter
from scrapy.exceptions import DontCloseSpider
from scrapy import signals

if TYPE_CHECKING:
    from scrapy.crawler import Crawler
    from scrapy import Spider

# TODO add listener to spider_idle signal in order to prevent the Ole spider from
# closing prematurely and leaving a bunch of unprocessed items in the pipeline


class OleOrCarlLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        return {
            "level": logging.DEBUG,
            "msg": "Dropped %(email)s (%(exception)s).",
            "args": {
                "exception": exception,
                "email": item["email"],
            },
        }


# Turns out scrapy works fine and it was just my code throwing an exception...

# class ClosingPreventerExtension:
#     crawler: "Crawler"

#     def __init__(self, crawler) -> None:
#         self.crawler = crawler
#         crawler.signals.connect(self.prevent_closure, signal=signals.spider_idle)

#     def prevent_closure(self, spider: "Spider"):
#         spider.log(
#             f"{spider} thinks it's done. It's not.",
#             logging.INFO,
#         )
#         spider.log(
#             f"Preventing {spider} from closing.",
#             logging.INFO,
#         )
#         raise DontCloseSpider

#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(crawler)
