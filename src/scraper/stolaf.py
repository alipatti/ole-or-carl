import typing
import scrapy


if typing.TYPE_CHECKING:
    from scrapy.http import HtmlResponse


# TODO: implement (while on campus)


class OlafDirectorySpider(scrapy.Spider):
    name = 'stolaf'
    allowed_domains = ['stolaf.edu']

    def start_requests(self):
        pass

    def parse(self, response: "HtmlResponse", **kwargs):
        del kwargs  # unused

    

