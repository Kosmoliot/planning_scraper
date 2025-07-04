import time
import re
import random
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from store import store_results

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[  
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()  # logs to terminal
    ]
)

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extract_results(driver, keyword, site):
    results = driver.find_elements(By.CSS_SELECTOR, "ul#searchresults li.searchresult")
    applications = []
    for res in results:
        try:
            try:
                summary = res.find_element(By.CLASS_NAME, "summaryLinkTextClamp").text.strip()
            except:
                summary = res.find_element(By.TAG_NAME, "a").text.strip()

            meta_info = res.find_element(By.CSS_SELECTOR, "p.metaInfo").text.strip()
            address = res.find_element(By.CSS_SELECTOR, "p.address").text.strip()

            ref_no = re.search(r"Ref\. No:\s*(\S+)", meta_info)
            validated = re.search(r"Validated:\s*([^|]+)", meta_info)
            status = re.search(r"Status:\s*(.+)", meta_info)

            applications.append({
                "Website": site,
                "Search Word": keyword,
                "Reference No": ref_no.group(1) if ref_no else "",
                "Validated Date": validated.group(1).strip() if validated else "",
                "Status": status.group(1).strip() if status else "",
                "Address": address,
                "Summary": summary
            })
        except Exception:
            continue
    return applications

def scrape_all_sites(urls, keywords):
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    all_data = []

    try:
        for site_url in urls:
            for keyword in keywords:
                logging.info(f"Scraping keyword '{keyword}' from {site_url}")
                try:
                    driver.get(site_url)
                    search_input = wait.until(EC.presence_of_element_located((By.ID, "simpleSearchString")))
                    search_input.clear()
                    search_input.send_keys(keyword)
                    search_input.send_keys(Keys.RETURN)

                    try:
                        select = Select(driver.find_element(By.ID, "resultsPerPage"))
                        select.select_by_value("100")
                        go_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Go"]')
                        go_button.click()
                        time.sleep(2)
                    except NoSuchElementException:
                        pass

                    max_wait = 60
                    elapsed = 0
                    while True:
                        try:
                            results = driver.find_elements(By.CSS_SELECTOR, "ul#searchresults li.searchresult")
                            if results:
                                break
                            boxes = driver.find_elements(By.CSS_SELECTOR, "div.messagebox")
                            for box in boxes:
                                for li in box.find_elements(By.TAG_NAME, "li"):
                                    if "no results found" in li.text.strip().lower():
                                        raise StopIteration
                            time.sleep(1)
                            elapsed += 1
                            if elapsed >= max_wait:
                                break
                        except:
                            break
                except StopIteration:
                    continue

                time.sleep(random.uniform(1, 2))
                page = 1
                max_pages = 50

                while True:
                    page_data = extract_results(driver, keyword, site_url)
                    all_data.extend(page_data)
                    store_results(page_data)

                    try:
                        next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.next")
                        if not next_buttons:
                            break
                        driver.execute_script("arguments[0].click();", next_buttons[0])
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#searchresults li.searchresult")))
                        time.sleep(random.uniform(1, 2))
                        page += 1
                        if page > max_pages:
                            break
                    except:
                        break
    finally:
        driver.quit()

    return pd.DataFrame(all_data)
