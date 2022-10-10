import logging

from scrapy import logformatter

# TODO add listener to spider_idle signal in order to prevent the Ole spider from
# closing prematurely and leaving a bunch of unprocessed items in the pipeline


class OleOrCarlLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        return {
            "level": logging.DEBUG,  # lowering the level from logging.WARNING
            "msg": logformatter.DROPPEDMSG,
            "args": {
                "exception": exception,
                "item": item,  # TODO add email to log message
            },
        }
