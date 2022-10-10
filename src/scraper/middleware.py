import logging

from scrapy import logformatter


class OleOrCarlLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        return {
            "level": logging.DEBUG,  # lowering the level from logging.WARNING
            "msg": logformatter.DROPPEDMSG,
            "args": {
                "exception": exception,
                "item": item,
            },
        }
