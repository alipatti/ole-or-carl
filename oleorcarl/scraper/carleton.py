import logging
import pickle
from string import ascii_lowercase
import os
import time

import scrapy

from scrapy.http import HtmlResponse, FormRequest
from scrapy.selector import SelectorList

from .items import ModelItem
from ..database import Student
from ..settings import CARLETON_COOKIE_PATH, CARLETON_DIRECTORY_URL


class CarletonDirectorySpider(scrapy.Spider):
    name = "Carleton Directory Scraper"
    allowed_domains = ["carleton.edu"]

    overflow_warning = "Over 100 matches found"
    login_warning = "to see enhanced results"

    def __init__(self, name=None, **kwargs):

        if not os.path.exists(CARLETON_COOKIE_PATH):
            raise ValueError(
                "Carleton auth cookies are required. "
                "Run `get_carleton_cookies()` to get them."
            )

        super().__init__(name, **kwargs)

    def start_requests(self):

        # load cookies
        with open(CARLETON_COOKIE_PATH, "rb") as f:
            auth_cookies = pickle.load(f)

        # deploy requests
        for a in ascii_lowercase:
            self.log(f"Scraping Carleton '{a}' emails...", logging.INFO)

            for b in ascii_lowercase:
                yield FormRequest(
                    CARLETON_DIRECTORY_URL,
                    cookies=auth_cookies,
                    method="GET",
                    formdata={"email": f"{a}{b}", "scopeAffiliation": "student"},
                    callback=self.parse,
                )

            self.log(f"Finished scraping '{a}' emails.", logging.INFO)

    def parse(self, response: HtmlResponse):  # pylint: disable=arguments-differ
        if self.overflow_warning in str(response):
            self.log(
                f"Over 100 matches found when attempting to scrape"
                f"{response.url}. Only scraping the first 100.",
                logging.ERROR,
            )

        if self.login_warning in str(response):
            self.log("Unable to log in to the Carleton Directory.", logging.ERROR)
            self.close(self, "Unable to log in to the Carleton Directory.")

        pre = ".campus-directory__"  # wordpress CSS class prefix

        for li in response.css(f"{pre}people {pre}person"):
            li: SelectorList  # for intellisense

            item = ModelItem(Student())

            item["name"] = li.css(f"{pre}person-name::text").get()
            item["email"] = li.css(f"{pre}email a::text").get()
            item["year"] = li.css(f"{pre}cohort-year::text").get()
            item["departments"] = (
                li.css(f"{pre}person-majors a::text").getall()
                + li.css(f"{pre}person-minors a::text").getall()
            )
            item["pronouns"] = li.css(f"{pre}pronouns::text").get([])
            item["school"] = "carleton"

            if item["pronouns"]:
                item["pronouns"] = item["pronouns"].split("/")

            if item["departments"] == ["Undecided"]:
                item["departments"] = []

            yield item


def get_carleton_cookies() -> None:
    """Prompts the user for Carleton credentials, logs in, and
    stores the cookies for use by the scraper in the file
    given by `settings.COOKIE_PATH`"""
    # pylint: disable=import-outside-toplevel
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support.expected_conditions import element_to_be_clickable

    # check if cookies exist and are recent
    threshold = 60 * 60 * 6  # 6 hours

    if not os.path.exists(CARLETON_COOKIE_PATH):
        print("Carleton auth cookies do not exist.")
    elif (age := os.path.getmtime(CARLETON_COOKIE_PATH)) - time.time() > threshold:
        print(f"Carleton auth cookies are expired ({age / 60 / 60:.1f} hours).")
    else:
        print("Carleton auth cookies exist. Proceeding...")
        return

    print("Preparing to generate cookies...")
    print("Please enter Carleton login information:")
    username = input(" - username: ")
    password = input(" - password: ")

    print("Retrieving cookies...")

    options = webdriver.ChromeOptions()
    # options.headless = True
    driver = webdriver.Chrome(options=options)

    url = "https://www.carleton.edu/directory/wp-login.php?redirect_to=%2Fdirectory%2F"

    driver.get(url)
    driver.find_element(By.ID, "idp_55012701_button").click()

    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.NAME, "_eventId_proceed").click()

    frame = driver.find_element(By.ID, "duo_iframe")
    driver.switch_to.frame(frame)

    wait = WebDriverWait(driver, 60)
    wait.until(
        element_to_be_clickable((By.CSS_SELECTOR, ".positive.auth-button"))
    ).click()
    wait.until(lambda driver: driver.current_url in CARLETON_DIRECTORY_URL)

    cookies = driver.get_cookies()
    driver.close()

    with open(CARLETON_COOKIE_PATH, "wb") as f:
        pickle.dump(cookies, f)
