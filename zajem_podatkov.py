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
CSV_FILE = "rezultati.csv"
MAX_CONSECUTIVE_EMPTY = 3