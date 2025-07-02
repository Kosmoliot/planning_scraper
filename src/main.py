#   main.py

import streamlit as st
from scraper import scrape_all_sites
from db import insert_new_rows
import json
from pathlib import Path

INPUT_FILE = Path("saved_inputs.json")

def load_inputs():
    if INPUT_FILE.exists():
        try:
            data = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
            return data.get("urls", ""), data.get("keywords", "")
        except:
            pass
    return ("https://planning.norwich.gov.uk/online-applications/\n"
            "https://planningon-line.rushcliffe.gov.uk/online-applications/",
            "concrete tank\nanaerobic")

def save_inputs(u, k):
    INPUT_FILE.write_text(json.dumps({"urls": u, "keywords": k}, indent=2), encoding="utf-8")

st.set_page_config(page_title="Planning Scraper", layout="wide")
st.title("Multi-site Planning Scraper")

urls_text, keywords_text = load_inputs()
urls_input = st.text_area("Portal URLs (one per line):", urls_text, height=150)
keywords_input = st.text_area("Search keywords (one per line):", keywords_text, height=100)

if st.button("Scrape"):
    list_urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
    list_keywords = [k.strip() for k in keywords_input.splitlines() if k.strip()]

    if not list_urls or not list_keywords:
        st.warning("Please add both URLs and keywords.")
    else:
        save_inputs(urls_input, keywords_input)
        with st.spinner("Scraping..."):
            df = scrape_all_sites(list_urls, list_keywords)
            if not df.empty:
                insert_new_rows(df)
                st.success(f"Scraped {len(df)} entries.")
                st.dataframe(df)
                st.download_button("Download CSV", df.to_csv(index=False), "results.csv", "text/csv")
            else:
                st.info("No results found.")
