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

# Vrne seznam URL-jev do posameznih oglasov nepremičnin
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

# Preverjanje Cloudflare blokade v html vsebini
def is_cloudflare_block(html):
    return (
        "Sorry, you have been blocked" in html or "Cloudflare Ray ID" in html
    )

# Vrne html vsebino strani, če ta ni blokirana
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


def extract_size_and_obcina(soup):
    size = ""
    obcina = ""

    meta_desc = soup.find("meta", attrs={"itemprop": "description"})
    if meta_desc and meta_desc.get("content"):
        m = re.search(
            r"(\d+(?:[.,]\d+)?)\s*m\s*2", meta_desc["content"], flags=re.I
        )
        if m:
            size = m.group(1).replace(",", ".").strip()


    more_info = soup.find("div", class_=lambda c: c and "more_info" in c)
    if more_info:
        t = more_info.get_text(" ", strip=True)
        m = re.search(r"Občina:\s*([^|]+)", t, flags=re.I)
        if m:
            obcina = m.group(1).strip()

    return size, obcina


def extract_price(soup):
    price_meta = soup.find("meta", attrs={"itemprop": "price"})
    if price_meta and price_meta.get("content"):
        return price_meta["content"] + " EUR"
    return ""