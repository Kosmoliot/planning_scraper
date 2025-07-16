import logging
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from store import store_results

def setup_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Detect Railway vs local
    import os
    if os.getenv("RAILWAY_ENVIRONMENT"):
        options.add_argument("--headless")
        options.binary_location = "/usr/bin/chromium"
        driver = webdriver.Chrome(options=options)
    else:
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)

    return driver

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

            # Extract the link safely
            try:
                link_element = res.find_element(By.CSS_SELECTOR, "a.summaryLink")
            except NoSuchElementException:
                link_element = res.find_element(By.TAG_NAME, "a")

            relative_link = link_element.get_attribute("href")
            if relative_link.startswith("/"):
                base = site.rstrip("/")
                full_link = base + relative_link
            else:
                full_link = relative_link

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
            logging.warning(f"Skipping one result due to error: {e}")
            continue

    return applications

def scrape_single_site(site, keywords):
    driver = setup_driver()
    all_results = []

    for keyword in keywords:
        try:
            logging.info(f"Searching {site} for keyword '{keyword}'")
            driver.get(site)
            time.sleep(2)

            # Search form elements (adjust if needed)
            search_input = driver.find_element(By.ID, "searchCriteria")
            search_input.clear()
            search_input.send_keys(keyword)
            search_button = driver.find_element(By.ID, "searchButton")
            search_button.click()

            time.sleep(3)

            results = extract_results(driver, keyword, site)
            if results:
                all_results.extend(results)
                store_results(results)
                logging.info(f"Stored {len(results)} results for '{keyword}' on {site}")
            else:
                logging.info(f"No results for '{keyword}' on {site}")

        except Exception as e:
            logging.error(f"Keyword '{keyword}' failed on {site}: {e}", exc_info=True)
            continue

    driver.quit()
    return all_results

def scrape_all_sites(urls, keywords):
    successes = []
    failures = []

    for site in urls:
        try:
            scrape_single_site(site, keywords)
            successes.append(site)
        except Exception as e:
            logging.error(f"Scraping failed for site {site}: {e}", exc_info=True)
            failures.append((site, str(e)))
            continue

    return successes, failures
