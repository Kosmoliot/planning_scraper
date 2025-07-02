#   scheduled_scraper.py

from scraper import scrape_all_sites
from db import insert_new_rows

urls = ["https://planning.norwich.gov.uk/online-applications/"]
keywords = ["concrete tank", "anaerobic"]

df = scrape_all_sites(urls, keywords)
if not df.empty:
    insert_new_rows(df)
    print(f"Inserted {len(df)} new rows.")
else:
    print("No new data.")
