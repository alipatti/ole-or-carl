#############
# FILEPATHS #
#############

DATABASE_PATH = "./db.sqlite"
DEFAULT_IMAGES_DIR = "./oleorcarl/scraper/default_images"
GRID_SEARCH_RESULTS_PATH = "./oleorcarl/classifier/grid_search_results.csv"

CARLETON_COOKIE_PATH = "./oleorcarl/scraper/cookies.pickle.secret"
LINKEDIN_HEADER_PATH = "./oleorcarl/scraper/linkedin_headers.yaml.secret"

########################
# SCRAPING TARGET URLS #
########################

CARLETON_DIRECTORY_URL = "https://www.carleton.edu/directory/"
CARLETON_IMG_URL = "https://apps.carleton.edu/stock/ldapimage.php?id={}"

OLAF_DIRECTORY_URL = "https://www.stolaf.edu/directory/search/"
OLAF_IMG_URL = "https://www.stolaf.edu/stofaces/face.cfm?username={}&fullsize"

LINKEDIN_API_URL = "https://www.linkedin.com/voyager/api/search/hits"

###################
# SCRAPY SETTINGS #
###################

# See https://docs.scrapy.org/en/latest/topics/settings.html

BOT_NAME = "Carleton/Olaf Directory Scraper"

SPIDER_MODULES = ["oleorcarl.scraper"]
NEWSPIDER_MODULE = "oleorcarl.scraper"

LOG_LEVEL = "DEBUG"
# LOG_FILE="./scrapy.log"

# USER_AGENT = "scraper (+http://www.yourdomain.com)"
# ROBOTSTXT_OBEY = True
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_TARGET_CONCURRENCY = 1
CONCURRENT_ITEMS = 10000

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(levelname)s: %(message)s"
LOG_FORMATTER = "oleorcarl.scraper.middleware.OleOrCarlLogFormatter"

# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "oleorcarl.scraper.pipelines.ItemPrinter": 1,
    "oleorcarl.scraper.pipelines.GrownupFilter": 100,
    "oleorcarl.scraper.pipelines.UniqueFilter": 101,
    "oleorcarl.scraper.pipelines.FaceEmbedder": 300,
    "oleorcarl.scraper.pipelines.DBSaver": 1000,
}
