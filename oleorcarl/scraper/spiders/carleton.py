from itertools import product
import logging
import pickle
from string import ascii_lowercase
import os
import time

import scrapy

from scrapy.http import HtmlResponse, Request
from scrapy.selector import SelectorList

from ...database.models import Student
from ...settings import COOKIE_PATH, CARLETON_DIRECTORY_URL


class CarletonSpider(scrapy.Spider):
    name = "carleton"
    allowed_domains = ["carleton.edu"]

    warning_text = "Over 100 matches found. Showing the first 100."

    def start_requests(self):

        # get carleton auth cookies
        cookies = _get_carleton_cookies()

        yield from (
            Request(CARLETON_DIRECTORY_URL, cookies=cookies, body={"email": f"{a}{b}"})
            for a, b in product(ascii_lowercase, ascii_lowercase)
        )

    def parse(self, response: HtmlResponse):  # pylint: disable=arguments-differ

        if self.warning_text in str(response):
            self.log(
                f"Over 100 matches found when attempting to scrape"
                f"{response.url}. Only scraping the first 100.",
                logging.ERROR,
            )

        prefix = "campus-directory__"
        # add_prefix = lambda classname: f"campus-directory__{classname}"
        selectors = {
            "student": f"{prefix}people {prefix}person",
            "image": f"{prefix}person-image",
            "name": f"{prefix}person-name",
            "year": f"{prefix}cohort-year",
            "pronouns": f"{prefix}pronouns",
            "majors": f"{prefix}person-majors",
            "minors": f"{prefix}person-minors",
            "email": f"{prefix}email",
        }

        for li in response.css(selectors["student"]):
            # load data that we know so far and send it down the pipeline
            # to have the other attributes added (image, face vector embedding, etc.)
            li: SelectorList
            yield Student(
                email=li.css(...),
                name=li.css(...),
                school="carleton",
            )


def _get_carleton_cookies() -> dict:
    """Prompts the user for Carleton credentials, logs in, and
    stores the cookies for use by the scraper"""
    # pylint: disable=import-outside-toplevel
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support.expected_conditions import element_to_be_clickable

    # check if cookies exist and are recent
    threshold = 60 * 60  # 1 hour

    if os.path.exists(COOKIE_PATH) and (
        os.path.getmtime(COOKIE_PATH) - time.time() < threshold
    ):
        with open(COOKIE_PATH, "rb") as f:
            return pickle.load(f)

    print("Carleton login cookies are expired or do not exist.")
    print("Please enter Carleton login information:")
    username = input(" - username: ")
    password = input(" - password: ")

    print("Retrieving cookies...")

    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    url = "https://www.carleton.edu/directory/wp-login.php?redirect_to=%2Fdirectory%2F"

    driver.get(url)
    driver.find_element(By.ID, "idp_55012701_button").click()

    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.NAME, "_eventId_proceed").click()

    frame = driver.find_element(By.ID, "duo_iframe")
    driver.switch_to.frame(frame)

    wait = WebDriverWait(driver, 30)
    wait.until(
        element_to_be_clickable((By.CSS_SELECTOR, ".positive.auth-button"))
    ).click()
    wait.until(lambda driver: driver.current_url in CARLETON_DIRECTORY_URL)

    cookies = driver.get_cookies()
    driver.close()

    with open(COOKIE_PATH, "wb") as f:
        pickle.dump(cookies, f)

    return cookies
