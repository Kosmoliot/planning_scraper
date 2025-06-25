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

def main():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)
    search_keyword = "concrete tank"
    all_applications = []

    try:
        driver.get("https://info.southnorfolkandbroadland.gov.uk/online-applications/")
        search_input = wait.until(EC.presence_of_element_located((By.ID, "simpleSearchString")))
        search_input.send_keys(search_keyword)
        search_input.send_keys(Keys.RETURN)

        # Wait for the results to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#searchresults li.searchresult")))
        time.sleep(1)

        while True:
            print("Extracting current page...")
            all_applications.extend(extract_results(driver, search_keyword))

            # Check for "next" button
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "p.pager.top a.next")
                next_url = next_button.get_attribute("href")
                print("Navigating to next page...")
                driver.get(next_url)

                # Wait for new results to load
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#searchresults li.searchresult")))
                time.sleep(1)
            except:
                print("No more pages.")
                break

        # Save to CSV
        if all_applications:
            df = pd.DataFrame(all_applications)
            df.to_csv("cornwall_planning_applications.csv", index=False, encoding="utf-8")
            print(f"Saved {len(all_applications)} results to 'cornwall_planning_applications.csv'")
        else:
            print("No results found.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
