import time
import re
import random
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager



# Logging setup
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def extract_results(driver, keyword, site):
    results = driver.find_elements(By.CSS_SELECTOR, "ul#searchresults li.searchresult")
    applications = []

    for res in results:
        try:
            summary = res.find_element(By.CSS_SELECTOR, "div.summaryLinkTextClamp").text.strip()
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
                    # Set results per page to 100 if dropdown exists
                    try:
                        select = Select(driver.find_element(By.ID, "resultsPerPage"))
                        select.select_by_value("100")
                        go_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Go"]')
                        go_button.click()
                        time.sleep(2)
                        logging.info("Set results per page to 100.")
                    except NoSuchElementException:
                        logging.warning("Could not find resultsPerPage dropdown.")


                    # Wait for results or "no results found"
                    max_wait = 60  # seconds
                    poll_interval = 1
                    elapsed = 0

                    try:
                        while True:
                            try:
                                if driver.find_elements(By.CSS_SELECTOR, "ul#searchresults li.searchresult"):
                                    break

                                # Check if "No results found." is present in messagebox
                                message_boxes = driver.find_elements(By.CSS_SELECTOR, "div.messagebox")
                                for box in message_boxes:
                                    list_items = box.find_elements(By.TAG_NAME, "li")
                                    for li in list_items:
                                        if "no results found" in li.text.strip().lower():
                                            logging.info(f"No results for '{keyword}' on {site_url}")
                                            raise StopIteration

                                time.sleep(poll_interval)
                                elapsed += poll_interval
                                if elapsed >= max_wait:
                                    logging.info(f"Still waiting for results after {max_wait} seconds for '{keyword}' on {site_url}")
                                    break
                            except Exception as e:
                                logging.info(f"Unexpected error while waiting: {e}")
                                break
                    except StopIteration:
                        continue  # Skip to next keyword

                    time.sleep(random.uniform(1, 2))

                    
                    page_num = 1
                    max_pages = 50  # fail-safe

                    while True:
                        logging.info(f"Extracting page {page_num} for '{keyword}' on {site_url}")
                        all_data.extend(extract_results(driver, keyword, site_url))

                        try:
                            next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.next")
                            if not next_buttons:
                                logging.info("No 'Next' button found. Reached last page.")
                                break

                            next_button = next_buttons[0]
                            driver.execute_script("arguments[0].click();", next_button)
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#searchresults li.searchresult")))
                            time.sleep(random.uniform(1, 2))
                            page_num += 1

                            if page_num > max_pages:
                                logging.warning("Reached max page limit; stopping pagination to avoid infinite loop.")
                                break

                        except Exception as e:
                            logging.exception("Error during pagination.")
                            break


                except TimeoutException:
                    logging.info(f"Skipping '{keyword}' on {site_url} due to timeout.")
                except Exception as e:
                    logging.info(f"Error scraping '{keyword}' on {site_url}: {e}")
    finally:
        driver.quit()

    return pd.DataFrame(all_data)
