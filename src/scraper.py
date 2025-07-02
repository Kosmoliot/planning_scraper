#   scraper.py
import time
import re
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def extract_results(driver, keyword, site):
    results = driver.find_elements(By.CSS_SELECTOR, "ul#searchresults li.searchresult")
    data = []
    for r in results:
        try:
            summary = r.find_element(By.CSS_SELECTOR, "div.summaryLinkTextClamp").text.strip()
            meta = r.find_element(By.CSS_SELECTOR, "p.metaInfo").text.strip()
            address = r.find_element(By.CSS_SELECTOR, "p.address").text.strip()
            ref_no = re.search(r"Ref\. No:\s*(\S+)", meta)
            validated = re.search(r"Validated:\s*([^|]+)", meta)
            status = re.search(r"Status:\s*(.+)", meta)
            data.append({
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
    return data

def scrape_all_sites(urls, keywords):
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    all_results = []
    try:
        for site in urls:
            for kw in keywords:
                print(f"Scraping '{kw}' from {site}")
                try:
                    driver.get(site)
                    search = wait.until(EC.presence_of_element_located((By.ID, "simpleSearchString")))
                    search.clear()
                    search.send_keys(kw)
                    search.send_keys(Keys.RETURN)
                    wait.until(EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "ul#searchresults li.searchresult, div.messagebox"
                    )))
                    time.sleep(random.uniform(1,2))
                    try:
                        msg = driver.find_element(By.CSS_SELECTOR, "div.messagebox").text.strip()
                        if "Please check the search criteria" in msg:
                            print(f"No results for {kw} on {site}")
                            continue
                    except NoSuchElementException:
                        pass
                    while True:
                        all_results.extend(extract_results(driver, kw, site))
                        try:
                            nb = driver.find_element(By.CSS_SELECTOR, "p.pager.top a.next")
                            driver.get(nb.get_attribute("href"))
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#searchresults li.searchresult")))
                            time.sleep(random.uniform(1,2))
                        except NoSuchElementException:
                            break
                except TimeoutException:
                    print(f"Timeout on {kw} at {site}")
                except Exception as e:
                    print(f"Error scraping {kw}: {e}")
    finally:
        driver.quit()
    return pd.DataFrame(all_results)
