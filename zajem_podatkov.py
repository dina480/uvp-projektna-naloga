# Projektna naloga pri prdmetu Uvod v programiranje

import os
import re
import csv
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

# URL spletne strani, kjer se nahajajo rezultati
BASE_URL = "https://www.nepremicnine.net/oglasi-oddaja/stanovanje/soba/{page}/"
# Ime CSV datoteke v katero se bodo shranili podatki
CSV_FILE = "rezultati.csv"
MAX_CONSECUTIVE_EMPTY = 3


def extract_listing_links(soup):
    boxes = soup.select("div.property-box.property-normal")
    out = []
    for b in boxes:
        a = b.find("a", class_="url-title-m") or b.find("a", href=True)
        if a and a.get("href"):
            href = a["href"]
            if href.startswith("/"):
                href = "https://www.nepremicnine.net" + href
            out.append(href)
    return out


def is_cloudflare_block(html):
    return (
        "Sorry, you have been blocked" in html or "Cloudflare Ray ID" in html
    )


def get_main_html(driver, page):
    url = BASE_URL.format(page=page)
    driver.get(url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.property-box.property-normal")
        )
    )
    time.sleep(2)
    html = driver.page_source
    if is_cloudflare_block(html):
        print("Blocked by Cloudflare.")
        return None
    return html

