import streamlit as st
import json
import os
import datetime

from scraper import scrape_all_sites
from db import fetch_filtered_results

INPUT_FILE = "scrape_inputs.json"

def load_inputs():
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "r") as f:
            data = json.load(f)
            return data.get("urls", []), data.get("keywords", [])
    return [], []

def save_inputs(urls, keywords):
    with open(INPUT_FILE, "w") as f:
        json.dump({"urls": urls, "keywords": keywords}, f, indent=2)

previous_urls, previous_keywords = load_inputs()

default_urls = "\n".join(previous_urls) if previous_urls else "\n".join([
    "https://planning.norwich.gov.uk/online-applications/",
    "https://planningon-line.rushcliffe.gov.uk/online-applications/"
])
default_keywords = "\n".join(previous_keywords) if previous_keywords else "concrete tank\nanaerobic"

st.set_page_config(page_title="Planning Scraper", layout="wide")
st.title("Multi-site Planning Scraper")

# Date Filter
st.subheader("Filter by Validated Date")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", datetime.date.today() - datetime.timedelta(days=30))
with col2:
    end_date = st.date_input("End date", datetime.date.today())

if start_date > end_date:
    st.error("Start date cannot be after end date")

# URLs & Keywords
urls_input = st.text_area("Planning portal URLs (one per line):", default_urls, height=150)
keywords_input = st.text_area("Search keywords (one per line):", default_keywords, height=100)

# Main Scrape + Show button
if st.button("Scrape & Show"):
    urls = [url.strip() for url in urls_input.strip().splitlines() if url.strip()]
    keywords = [kw.strip() for kw in keywords_input.strip().splitlines() if kw.strip()]

    save_inputs(urls, keywords)

    if not urls or not keywords:
        st.warning("Please enter at least one URL and one keyword")
    else:
        # Step 1: Scrape and store all results
        with st.spinner("Scraping websites... please wait"):
            scrape_all_sites(urls, keywords)
        st.success("Scraping completed and stored in database.")

        # Step 2: Fetch only results matching current filters
        filtered_results = fetch_filtered_results(
            start_date,
            end_date,
            urls,
            keywords
        )

        # Step 3: Display filtered results
        if filtered_results:
            st.write(f"Found {len(filtered_results)} results between {start_date} and {end_date}")
            st.dataframe(filtered_results)
        else:
            st.info("No results found for this date range, URLs, and keywords.")
