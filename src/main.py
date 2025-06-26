import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def extract_results(driver, keyword):
    """Extracts application results from current page."""
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
                "Search Word": keyword,
                "Reference No": ref_no.group(1) if ref_no else "",
                "Validated Date": validated.group(1).strip() if validated else "",
                "Status": status.group(1).strip() if status else "",
                "Address": address,
                "Summary": summary
            })
        except Exception as e:
            print(f"Skipping a result due to error: {e}")
    return applications

def scrape_site(driver, wait, site_url, keyword):
    driver.get(site_url)
    search_input = wait.until(EC.presence_of_element_located((By.ID, "simpleSearchString")))
    search_input.clear()
    search_input.send_keys(keyword)
    search_input.send_keys(Keys.RETURN)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#searchresults li.searchresult")))
    time.sleep(1)

    all_applications = []

    while True:
        print(f"Extracting results for '{keyword}' on {site_url}...")
        all_applications.extend(extract_results(driver, keyword))

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "p.pager.top a.next")
            next_url = next_button.get_attribute("href")
            driver.get(next_url)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#searchresults li.searchresult")))
            time.sleep(1)
        except:
            print("No more pages.")
            break

    return all_applications

def main():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)

    # Multiple websites and search terms
    urls = [
        # "https://info.southnorfolkandbroadland.gov.uk/online-applications/",
        # "https://planning.cornwall.gov.uk/online-applications/",
        # "https://online.west-norfolk.gov.uk/",
        "https://planning.norwich.gov.uk/online-applications/",
        "https://planningon-line.rushcliffe.gov.uk/online-applications/"
    ]
    keywords = ["concrete tank", "anaerobic"]  # Add more keywords here

    all_data = []

    try:
        for site_url in urls:
            for keyword in keywords:
                data = scrape_site(driver, wait, site_url, keyword)
                all_data.extend(data)

        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv("multi_site_planning_results.csv", index=False, encoding="utf-8")
            print(f"Saved {len(all_data)} results to 'multi_site_planning_results.csv'")
        else:
            print("No results found.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
