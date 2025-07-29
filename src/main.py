import streamlit as st
import json
import os
import datetime
import pandas as pd
import logging

from scraper import scrape_all_sites
from db import fetch_filtered_results
from store import get_all_keywords, get_all_urls

INPUT_FILE = "scrape_inputs.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[  
        logging.FileHandler("scraper.log"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)

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
    start_date = st.date_input(
        "Start date",
        datetime.date.today() - datetime.timedelta(days=30),
        min_value=datetime.date(1985, 1, 1),
        max_value=datetime.date.today()
    )
with col2:
    end_date = st.date_input(
        "End date",
        datetime.date.today(),
        min_value=datetime.date(1985, 1, 1),
        max_value=datetime.date.today()
    )

if start_date > end_date:
    st.error("Start date cannot be after end date")

# Initialize session state (no defaults)
if "urls_input" not in st.session_state:
    st.session_state.urls_input = ""

if "keywords_input" not in st.session_state:
    st.session_state.keywords_input = ""

# --- URL Text Area + Load Button ---
st.session_state.urls_input = st.text_area(
    "Enter URLs (one per line):",
    value=st.session_state.urls_input,
    key="urls_text",
    height=150
)
if st.button("Load archived URLs"):
    st.session_state.urls_input = "\n".join(get_all_urls())
    st.rerun()

# --- Keyword Text Area + Load Button ---
st.session_state.keywords_input = st.text_area(
    "Enter keywords (one per line):",
    value=st.session_state.keywords_input,
    key="keywords_text",
    height=100
)
if st.button("Load archived Keywords"):
    st.session_state.keywords_input = "\n".join(get_all_keywords())
    st.rerun()



# Main Scrape + Show button
if st.button("Scrape"):
    urls = [url.strip() for url in st.session_state.urls_input.strip().splitlines() if url.strip()]
    keywords = [kw.strip() for kw in st.session_state.keywords_input.strip().splitlines() if kw.strip()]

    save_inputs(urls, keywords)

    if not urls or not keywords:
        st.warning("Please enter at least one URL and one keyword")
        logging.warning("User provided no URLs or keywords.")
    else:
        try:
            with st.spinner("Scraping websites... please wait"):
                successes, failures = scrape_all_sites(urls, keywords)

            # Show scrape summary
            if successes:
                st.success(f"Scraping completed for {len(successes)} site(s).")

            if failures:
                st.warning(f"Failed to scrape {len(failures)} site/keyword combinations:")
                for site_keyword, err in failures:
                    st.text(f"{site_keyword} -> {err}")

            # Fetch only whatever succeeded
            filtered_results = fetch_filtered_results(start_date, end_date, urls, keywords)

            if filtered_results:
                st.write(f"Found {len(filtered_results)} results between {start_date} and {end_date}")
                st.dataframe(filtered_results)

                df = pd.DataFrame(filtered_results)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", csv, "planning_results.csv", "text/csv")
            else:
                st.info("No results found for this date range, URLs, and keywords.")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            logging.error("Error during scraping or filtering", exc_info=True)
