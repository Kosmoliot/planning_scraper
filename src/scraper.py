import time
import re
import random
import pandas as pd
import logging, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from store import store_results, store_keyword, store_url
import streamlit as st

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[  
        logging.FileHandler("scraper.log"),   # Logs to a file
        logging.StreamHandler()  # Logs to console
    ]
)

# Helper function for driver setup
def setup_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")

    if os.getenv("RAILWAY_ENVIRONMENT"):
        # Running on Railway -> use headless Chromium in container
        options.binary_location = "/usr/bin/chromium"
        driver = webdriver.Chrome(options=options)
        logging.info("Using headless Chromium on Railway")
    else:
        # Running locally -> use installed Chrome
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        logging.info("Using local Chrome browser")

    return driver

# Function to extract search results from a page
def extract_results(driver, keyword, site):
    results = driver.find_elements(By.CSS_SELECTOR, "ul#searchresults li.searchresult")
    applications = []
    logging.info(f"Extracting results for '{keyword}' on {site}")
    
    for res in results:
        try:
            summary = res.find_element(By.CLASS_NAME, "summaryLinkTextClamp").text.strip() if res.find_elements(By.CLASS_NAME, "summaryLinkTextClamp") else res.find_element(By.TAG_NAME, "a").text.strip()
            link_element = res.find_element(By.TAG_NAME, "a")
            relative_link = link_element.get_attribute("href")
            
            # Construct the full link if it's relative
            full_link = relative_link if not relative_link.startswith("/") else site.rstrip("/") + relative_link
            
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
                "Summary": summary,
                "Link": full_link
            })
        except Exception as e:
            logging.error(f"Error extracting result: {e}")
            continue
    return applications

def scrape_site(driver, site_url, keyword, wait):
    logging.info(f"Scraping keyword '{keyword}' from {site_url}")
    driver.get(site_url)

    # Step 1: Enter keyword in search box & submit
    search_input = wait.until(
        EC.presence_of_element_located((By.ID, "simpleSearchString"))
    )
    search_input.clear()
    search_input.send_keys(keyword)
    search_input.send_keys(Keys.RETURN)

    time.sleep(2)  # small wait for page refresh

    # Step 2: Check for "No results found" before doing anything else
    no_result_box = driver.find_elements(By.CSS_SELECTOR, "div.messagebox li")
    for li in no_result_box:
        msg = li.text.strip().lower()
        if "no results found" in msg:
            logging.info(f"No results found for '{keyword}' on {site_url}.")
            return False  # explicitly signal "no results"

    # Step 3: If results exist, try setting results per page = 100
    try:
        select = Select(driver.find_element(By.ID, "resultsPerPage"))
        select.select_by_value("100")
        go_button = driver.find_element(
            By.CSS_SELECTOR, 'input[type="submit"][value="Go"]'
        )
        go_button.click()
        logging.info(f"Changed results per page to 100 for {site_url}")
        time.sleep(2)  # allow page reload
    except NoSuchElementException:
        logging.info(f"No 'results per page' dropdown found on {site_url} (skipping)")

    # Step 4: Return True meaning “results might exist, go paginate”
    return True


def scrape_pages(driver, keyword, site_url, wait, all_data):
    """Iterate through all pages if any results exist"""
    page = 1
    max_pages = 50

    logging.info(f"Starting pagination for '{keyword}' on {site_url}")

    while page <= max_pages:
        try:
            logging.info(f"Extracting data from page {page}")
            page_data = extract_results(driver, keyword, site_url)

            if not page_data and page == 1:
                logging.info(f"No search results detected on the first page for '{keyword}' at {site_url}.")
                break

            all_data.extend(page_data)
            store_results(page_data)

            next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.next")
            if not next_buttons:
                logging.info(f"No more pages for '{keyword}' on {site_url}.")
                break

            # Click next page
            driver.execute_script("arguments[0].click();", next_buttons[0])
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul#searchresults li.searchresult"))
            )
            time.sleep(random.uniform(1, 2))
            page += 1

        except Exception as e:
            logging.error(f"Error scraping page {page} for '{keyword}' on {site_url}: {e}")
            break


def scrape_all_sites(urls, keywords):
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    all_data = []
    successes = set()
    failures = []

    for site_url in urls:
        site_had_success = False

        for keyword in keywords:
            try:
                logging.info(f"Starting scrape for '{keyword}' on {site_url}")

                store_keyword(keyword)
                store_url(site_url)

                # Run search and check if results exist
                has_results = scrape_site(driver, site_url, keyword, wait)

                # If no results, log + continue with next keyword/site
                if not has_results:
                    logging.info(f"Skipping pagination for '{keyword}' on {site_url} (no results).")
                    continue

                # Paginate & extract results
                scrape_pages(driver, keyword, site_url, wait, all_data)
                site_had_success = True  # mark that at least 1 keyword worked


            except Exception as e:
                logging.error(f"Failed scraping '{keyword}' on {site_url}: {e}")
                failures.append((f"{site_url} (keyword: {keyword})", str(e)))
                continue

        # Only add site once if at least one keyword succeeded
        if site_had_success:
            successes.add(site_url)

    driver.quit()
    logging.info("Scraping process completed.")

    return list(successes), failures
