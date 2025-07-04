import time
import re
import random
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from store import store_results

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--single-process")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")
    options.binary_location = "/usr/bin/google-chrome"
    return webdriver.Chrome(options=options)

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

            ref_no = re.search(r"Ref\\. No:\\s*(\\S+)", meta_info)
            validated = re.search(r"Validated:\\s*([^|]+)", meta_info)
            status = re.search(r"Status:\\s*(.+)", meta_info)

            applications.append({
                "Website": site,
                "Search Word": keyword,
                "Reference No": ref_no.group(1) if ref_no else "",
                "Validated Date": validated.group(1).strip() if validated else "",
                "Status": status.group(1).strip() if status else "",
                "Address": address,
                "Summary": summary
            })
        except Exception as e:
            logging.warning(f"Error extracting result block: {e}")
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
                        logging.info("No 'results per page' option found.")

                    # Wait for results
                    max_wait = 60
                    elapsed = 0
                    while elapsed < max_wait:
                        results = driver.find_elements(By.CSS_SELECTOR, "ul#searchresults li.searchresult")
                        if results:
                            break
                        msg = driver.find_elements(By.CSS_SELECTOR, "div.messagebox li")
                        if any("no results found" in li.text.lower() for li in msg):
                            logging.info(f"No results for '{keyword}' on {site_url}")
                            raise StopIteration
                        time.sleep(1)
                        elapsed += 1

                except StopIteration:
                    continue
                except Exception as e:
                    logging.warning(f"Failed to start search on {site_url} with '{keyword}': {e}")
                    continue

                time.sleep(random.uniform(1, 2))
                page = 1
                max_pages = 50

                while True:
                    logging.info(f"Extracting page {page} for '{keyword}' from {site_url}")
                    page_data = extract_results(driver, keyword, site_url)
                    store_results(page_data)
                    all_data.extend(page_data)

                    try:
                        next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.next")
                        if not next_buttons:
                            logging.info("Reached last page.")
                            break
                        driver.execute_script("arguments[0].click();", next_buttons[0])
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#searchresults li.searchresult")))
                        time.sleep(random.uniform(1, 2))
                        page += 1
                        if page > max_pages:
                            logging.warning("Max page limit hit — stopping.")
                            break
                    except Exception as e:
                        logging.warning(f"Pagination error: {e}")
                        break
    finally:
        driver.quit()

    return pd.DataFrame(all_data)
