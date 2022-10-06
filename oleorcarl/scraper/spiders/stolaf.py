import scrapy


class StolafSpider(scrapy.Spider):
    name = 'stolaf'
    allowed_domains = ['stolaf.edu']
    start_urls = ['http://stolaf.edu/']

    def parse(self, response):
        pass
