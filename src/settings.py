# pylint: disable=wrong-import-position
#############
# FILEPATHS #
#############

DATABASE_PATH = "./db.sqlite"
COOKIE_PATH = "./cookies.secret"

##################
# DIRECTORY URLS #
##################

CARLETON_DIRECTORY_URL = "https://www.carleton.edu/directory/"
CARLETON_IMAGE_URL = "https://apps.carleton.edu/stock/ldapimage.php?id={}"

OLAF_DIRECTORY_URL = "https://www.stolaf.edu/directory/search/"
OLAF_IMG_URL = "https://www.stolaf.edu/stofaces/face.cfm?username={}&fullsize"


###################
# SCRAPY SETTINGS #
###################

# See https://docs.scrapy.org/en/latest/topics/settings.html

BOT_NAME = "Carleton/Olaf Directory Scraper"

SPIDER_MODULES = ["src.scraper"]
NEWSPIDER_MODULE = "src.scraper"

LOG_LEVEL = "INFO"
# LOG_FILE="./scrapy.log"

# USER_AGENT = "scraper (+http://www.yourdomain.com)"
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(levelname)s: %(message)s"

# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "src.scraper.pipelines.ItemPrinter": 1,
    "src.scraper.pipelines.GrownupFilter": 100,
    "src.scraper.pipelines.UniqueFilter": 101,
    "src.scraper.pipelines.FaceEmbedder": 300,
    "src.scraper.pipelines.DBSaver": 1000,
}
