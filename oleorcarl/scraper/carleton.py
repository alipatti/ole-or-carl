import json
import logging
import pickle
from string import ascii_lowercase
import os
import time
from typing import TYPE_CHECKING

import scrapy

from scrapy.http import FormRequest
from scrapy.exceptions import CloseSpider

from .items import ModelItem
from .pipelines import GrownupFilter, UniqueFilter, FaceEmbedder, DBSaver
from ..database import Student
from ..settings import (
    CARLETON_COOKIE_PATH,
    CARLETON_CREDENTIALS_PATH,
    CARLETON_DIRECTORY_URL,
    CARLETON_LOGIN_URL,
)

if TYPE_CHECKING:
    from scrapy.selector import SelectorList
    from scrapy.http import HtmlResponse


class CarletonDirectorySpider(scrapy.Spider):
    name = "Carleton Directory Scraper"
    allowed_domains = ["carleton.edu"]

    custom_settings = {
        "ITEM_PIPELINES": {
            GrownupFilter: 100,
            UniqueFilter: 101,
            FaceEmbedder: 300,
            DBSaver: 1000,
        }
    }

    overflow_warning = "Over 100 matches found"
    login_warning = "Sign in for more search options"

    def __init__(self, name=None, **kwargs):

        if not os.path.exists(CARLETON_COOKIE_PATH):
            raise ValueError(
                "Carleton auth cookies are required. "
                "Run `get_carleton_cookies()` to get them."
            )

        super().__init__(name, **kwargs)

    def start_requests(self):

        cookies = get_cookies()

        # deploy requests searching for
        # aa...@carleton.edu, ab...@carleton.edu, ac...@carleton.edu, ..
        # in order to keep < 100 results per page (beyond which the directory won't show)
        for a in ascii_lowercase:
            self.log(f"Scraping Carleton '{a}' emails...", logging.INFO)

            for b in ascii_lowercase:
                yield FormRequest(
                    CARLETON_DIRECTORY_URL,
                    cookies=cookies,
                    method="GET",
                    formdata={"email": f"{a}{b}", "scopeAffiliation": "student"},
                    callback=self.parse,
                )

            self.log(f"Finished scraping '{a}' emails.", logging.INFO)

    def parse(self, response: "HtmlResponse"):  # pylint: disable=arguments-differ
        if self.overflow_warning in response.text:
            self.log(
                f"Over 100 matches found when attempting to scrape"
                f"{response.url}. Only scraping the first 100.",
                logging.ERROR,
            )

        if self.login_warning in response.text:
            self.log("Unable to log in to the Carleton Directory.", logging.ERROR)
            raise CloseSpider("Unable to log in to the Carleton Directory.")

        pre = ".campus-directory__"  # wordpress CSS class prefix

        for li in response.css(f"{pre}people {pre}person"):
            li: "SelectorList"

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
            item["source"] = self.name

            if item["pronouns"]:
                item["pronouns"] = item["pronouns"].split("/")

            if item["departments"] == ["Undecided"]:
                item["departments"] = []

            yield item


def create_cookies(headless=True) -> None:
    # pylint: disable=import-outside-toplevel
    from playwright.sync_api import sync_playwright

    logging.info("Creating new Carleton auth cookies...")

    with open(CARLETON_CREDENTIALS_PATH, "rt", encoding="utf-8") as f:
        username, password = f.read().split()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        page.goto(CARLETON_LOGIN_URL)  # login through directory redirect url
        page.click("a[href^='/console/ds/s/']")  # click to login w credentials

        # fill credentials
        page.fill("#username", username)
        page.fill("#password", password)
        page.click("form button[type='submit']")

        # duo auth
        frame = page.frame_locator("#duo_iframe")
        frame.locator(".stay-logged-in input[type='checkbox']").click()
        frame.locator(".push-label button").click()  # send push
        logging.info("Duo push notification sent. Waiting for approval...")

        page.wait_for_url("*carleton.edu/directory/")  # wait for approval
        logging.info("Approval received!")

        cookies = context.cookies()

    with open(CARLETON_COOKIE_PATH, "wt", encoding="utf8") as f:
        json.dump(cookies, f)


def get_cookies() -> dict[str, str]:
    """Prompts the user for Carleton credentials, logs in, and
    stores the cookies for use by the scraper in the file
    given by `settings.COOKIE_PATH`"""

    if not os.path.exists(CARLETON_COOKIE_PATH):
        logging.warning("Carleton auth cookies do not exist.")
        create_cookies()

    with open(CARLETON_COOKIE_PATH, "rt", encoding="utf8") as f:
        cookies = json.load(f)

    if any(
        cookie["expires"] < time.time() for cookie in cookies if cookie["expires"] > 0
    ):

        logging.warning("Some Carleton auth cookies are expired.")
        create_cookies()
        return get_cookies()
    # fmt: skip

    return cookies
