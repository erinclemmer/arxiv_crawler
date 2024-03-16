import re
import random
from time import sleep
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SEARCH_URL = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C44&q="

RESULT_CLASS = "gs_r"
TITLE_CLASS = "gs_rt"
LINK_CLASS = "gs_ggsd"

def sleep_rand():
    extra_sec = random.randint(1, 5)
    extra_mil = random.randint(1, 999)
    sleep_time = float(str(5 + extra_sec) + '.' + str(extra_mil))
    print(f'Sleeping {sleep_time:.2f}s')
    sleep(sleep_time)

def get_arxiv_from_g_scholar(title: str):
    sub = title[:100]

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options)
    driver.get(SEARCH_URL + quote(title))
    # sleep_rand()
    try:
        # Wait for the results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, RESULT_CLASS))
        )
        # Find the profile link
        for el in driver.find_elements(By.CLASS_NAME, RESULT_CLASS):
            try:
                title = el.find_element(By.CLASS_NAME, TITLE_CLASS).find_element(By.TAG_NAME, "a").text[:50]
                if title != sub:
                    continue
                link = el.find_element(By.CLASS_NAME, LINK_CLASS).find_element(By.TAG_NAME, "a").get_attribute("href")
                match = re.findall(r'\d{4}.\d{5}', link)
                if len(match) == 0:
                    continue

                return match[0]
            except:
                continue

    except Exception:
        sleep(1)
        return None