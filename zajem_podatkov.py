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

# Preveri Cloudflare blokade v html vsebini
def is_cloudflare_block(html):
    return (
        "Sorry, you have been blocked" in html or "Cloudflare Ray ID" in html
    )

# Vrne html vsebino strani, če ta ni blokirana
def get_main_html(driver, page):
    url = BASE_URL.format(page=page)
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.property-box.property-normal")
            )
        )
    except:
        return None
    
    time.sleep(2)
    html = driver.page_source
    if is_cloudflare_block(html):
        print("Blocked by Cloudflare.")
        return None
    return html

# Zapre pojavno okno za piškotke, če se to pojavi
def dismiss_cookie_popup(driver):
    try:
        btn = driver.find_element(
            By.ID, "CybotCookiebotDialogBodyButtonAccept"
        )
        if btn.is_displayed():
            btn.click()
            time.sleep(2)
    except NoSuchElementException:
        pass

# Izlušči željene podatke
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
            
    if size == "":
        h1 = soup.find("h1")
        if h1:
            t = h1.get_text(" ", strip=True)
            m = re.search(r"(\d+(?:[.,]\d+)?)\s*m\s*2", t, flags=re.I)
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


# Nastavi in zažene Chrome brskalnik 
options = uc.ChromeOptions()
options.headless = False
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
)
if not options.binary_location:
    options.binary_location = (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    )

print("Starting Chrome browser...")
driver = uc.Chrome(options=options)

# Obdelovanje večih strani
rows = []
all_links = set()
consecutive_empty = 0
page = 1

#  Zanka teče dokler ne najde več zaporednih praznih strani
while consecutive_empty < MAX_CONSECUTIVE_EMPTY:
    html = get_main_html(driver, page)
    if page == 1:
        dismiss_cookie_popup(driver)

    if not html:
        consecutive_empty += 1
        page += 1
        continue

    soup = BeautifulSoup(html, "html.parser")
    links = set(extract_listing_links(soup))
    new_links = links - all_links
    print(f"--- Page {page}: Found {len(new_links)} listings ---")

    if not new_links:
        consecutive_empty += 1
        page += 1
        continue

    all_links |= new_links
    for link in new_links:
        m = re.search(r"_(\d+)/", link)
        if not m:
            print("no id:", link)
            continue
        listing_id = m.group(1)

        driver.get(link)
        time.sleep(5)
        full_page = driver.page_source
        if is_cloudflare_block(full_page) or not full_page.strip():
            print("blocked/empty:", listing_id)
            continue

        s = BeautifulSoup(full_page, "html.parser")
        price = extract_price(s)
        size, obcina = extract_size_and_obcina(s)

        rows.append([listing_id, link, size, price, obcina])
        print(f"{listing_id} | {size} m2 | {price} | {obcina}")

    consecutive_empty = 0
    page += 1

driver.quit()

# Nastanek CSV datoteke
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "url", "size", "price", "obcina"])
    w.writerows(rows)

print("Saved:", CSV_FILE)