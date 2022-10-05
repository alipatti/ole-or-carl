from itertools import product
import json
import os
import pickle
import string
import typing
import re

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# SELENIUM IMPORTS
# (needed for logging in to Carleton directory with Duo)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import element_to_be_clickable

###################
# CUSTOM TYPEDEFS #
###################

Email = typing.NewType("Email", str)


#############
# CONSTANTS #
#############

OLAF_DIRECTORY_URL = "https://www.stolaf.edu/directory/search/"
CARLETON_DIRECTORY_URL = "https://www.carleton.edu/directory/"

IMG_URLS = {
    "stolaf.edu": lambda id: f"https://www.stolaf.edu/stofaces/face.cfm?username={id}&fullsize",
    "carleton.edu": lambda id: f"https://apps.carleton.edu/stock/ldapimage.php?id={id}",
}

IMG_FOLDER = "data/images/"
DIRECTORY_FOLDER = "data/directory/"

CREDENTIALS_PATH = "data/credentials.txt"
COOKIE_PATH = "data/carleton_cookies.pkl"
OLE_PATH = os.path.join(DIRECTORY_FOLDER + "oles.json")
CARL_PATH = os.path.join(DIRECTORY_FOLDER + "carls.json")


################
# OLE SCRAPING #
################


def _scrape_oles() -> None:
    pronouns_regex = re.compile(r"\([a-z,/ ]+\)")
    classyear_regex = re.compile(r"[1-9]{2}")

    # these departments show up when you search "Student"
    depts_to_exclude = {
        "Center for Advising and Academic Support",
        "Writing Program",
        "Taylor Center for Equity and Inclusion",
        "Institutional Effectiveness and Assessment",
        "Alumni and Parent Relations",
        "Registrar’s Office",
        "Residence Life",
        "Student Accounts",
        "Business Office",
        "Dean of Students",
        "Student Activities",
        "Student Support Services",
    }

    params = {"title": "student"}
    with requests.post(OLAF_DIRECTORY_URL, params=params) as r:
        soup = BeautifulSoup(r.text, "lxml")

    students = soup.select(".results .result")
    directory = {}

    for student in tqdm(students, desc="Scraping Oles"):

        header = student.select_one(".c-faculty__name")
        email = header.template["data-email"]

        info = directory[email] = {}

        match = pronouns_regex.search(header.get_text())
        pronouns = match.group(0) if match else ""

        info["name"] = header.get_text().replace(pronouns, "").strip()

        title = student.select_one(".c-faculty__title").get_text()
        match = classyear_regex.search(title)
        info["year"] = int(match.group()) if match else ""

        student_depts = student.select(".c-faculty__departments li")
        info["depts"] = [li.get_text() for li in student_depts]

        if set(info["depts"]) & depts_to_exclude:
            del directory[email]

    with open(OLE_PATH, "wt") as f:
        json.dump(directory, f)


#################
# CARL SCRAPING #
#################


def _get_carleton_cookies() -> dict:

    try:
        with open(COOKIE_PATH, "rb") as f:
            cookies = pickle.load(f)
    except (FileNotFoundError, EOFError):

        print("Enter Carleton login information.")
        username = input("username: ")
        password = input("password: ")

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


def _scrape_carls(login_cookies=None) -> None:

    if not login_cookies:
        login_cookies = _get_carleton_cookies()

    s = requests.Session()
    for cookie in login_cookies:
        s.cookies.set(cookie["name"], cookie["value"])

    r = s.get(CARLETON_DIRECTORY_URL)
    soup = BeautifulSoup(r.text, "lxml")

    years = [el["value"] for el in soup.select("#classYear option") if el["value"]]
    directory = {}

    year_char_combos = list(product(years, string.ascii_lowercase))

    for year, char in tqdm(year_char_combos, desc="Scraping Carls"):
        params = {"scopeAffiliation": "student", "classYear": year, "email": char}
        r = s.get(CARLETON_DIRECTORY_URL, params=params)
        soup = BeautifulSoup(r.text, "lxml")

        students = soup.select(".campus-directory__person")
        for student in students:
            get_div_text = lambda class_name: student.select_one(class_name).get_text()

            email = get_div_text(".campus-directory__email a")
            info = directory[email] = {}

            info["name"] = get_div_text(".campus-directory__person-name")
            info["year"] = year

            info["majors"] = [
                a.get_text()
                for a in student.select(".campus-directory__person-majors a")
            ]

    s.close()

    with open(CARL_PATH, "wt") as f:
        json.dump(directory, f)


###############
# DRIVER CODE #
###############


def get_directory() -> dict[Email, dict]:
    """
    Gets a directory of Carleton and Olaf Students.
    Creates the directory if one does not exist.
    """

    if not os.path.exists(OLE_PATH):
        print("No Olaf directory found. Scraping Oles...")
        _scrape_oles()

    if not os.path.exists(CARL_PATH):
        print("No Carleton directory found. Scraping Carls...")
        _scrape_carls()

    with open(OLE_PATH, "rt") as ole_f, open(CARL_PATH, "rt") as carl_f:
        directory = json.load(ole_f) | json.load(carl_f)

    return directory


def _get_images(directory):
    emails = directory.keys()

    for email in tqdm(emails, desc="Retrieving images"):
        path = IMG_FOLDER + email + ".jpg"
        if os.path.exists(path):
            continue

        id, extension = email.split("@")
        url = IMG_URLS[extension](id)

        with requests.get(url) as r, open(path, "wb") as f:
            f.write(r.content)


def build_directory():
    print("Creating directory...")
    directory = get_directory()
    print("Retrieving images...")
    _get_images(directory)
    print("Done!")


if __name__ == "__main__":
    build_directory()
