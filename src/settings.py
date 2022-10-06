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

# LOG_FILE="./scrapy.log"

# USER_AGENT = "scraper (+http://www.yourdomain.com)"
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = .25

# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from .scraper.pipelines import UniqueFilter, ImageDownloader, FaceEmbedder, DBSaver, GrownupFilter
ITEM_PIPELINES = {
    GrownupFilter: 100,
    UniqueFilter: 101,
    ImageDownloader: 200,
    FaceEmbedder: 300,
    # DBSaver: 1000,
}
