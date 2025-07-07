#     main()
import streamlit as st
import json
import os
from scraper import scrape_all_sites

# Path to inputs file
INPUT_FILE = "scrape_inputs.json"

# Load previous inputs if available
def load_inputs():
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "r") as f:
            data = json.load(f)
            return data.get("urls", []), data.get("keywords", [])
    return [], []

# Save current inputs
def save_inputs(urls, keywords):
    with open(INPUT_FILE, "w") as f:
        json.dump({"urls": urls, "keywords": keywords}, f, indent=2)

# Load previous or set default values
previous_urls, previous_keywords = load_inputs()

default_urls = "\n".join(previous_urls) if previous_urls else "\n".join([
    "https://planning.norwich.gov.uk/online-applications/",
    "https://planningon-line.rushcliffe.gov.uk/online-applications/"
])
default_keywords = "\n".join(previous_keywords) if previous_keywords else "concrete tank\nanaerobic"

# Streamlit UI
st.set_page_config(page_title="Planning Scraper", layout="wide")
st.title("Multi-site Planning Scraper")

urls_input = st.text_area("Planning portal URLs (one per line):", default_urls, height=150)
keywords_input = st.text_area("Search keywords (one per line):", default_keywords, height=100)

if st.button("Scrape"):
    urls = [url.strip() for url in urls_input.strip().splitlines() if url.strip()]
    keywords = [kw.strip() for kw in keywords_input.strip().splitlines() if kw.strip()]

    if not urls or not keywords:
        st.warning("Please provide both URLs and keywords.")
    else:
        with st.spinner("Scraping... please wait."):
            try:
                df = scrape_all_sites(urls, keywords)
                save_inputs(urls, keywords)  # Save inputs after successful scrape
                if not df.empty:
                    st.success(f"Scraped {len(df)} results from {len(urls)} sites.")
                    st.dataframe(df)
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("Download CSV", csv, "planning_results.csv", "text/csv")
                else:
                    st.info("No results found.")
            except Exception as e:
                st.error(f"Error: {e}")