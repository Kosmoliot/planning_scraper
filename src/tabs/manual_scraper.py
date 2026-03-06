import streamlit as st
import pandas as pd
from logger import get_logger
from scraper import scrape_all_sites
from db import fetch_results
from store import get_all_keywords, get_all_urls
from tabs.components import date_range_inputs, results_table


def render():
    logger = get_logger()
    st.header("Manual Scraper")

    start_date, end_date = date_range_inputs("ms")
    if start_date > end_date:
        st.error("Start date cannot be after end date")
        return

    if "urls_input" not in st.session_state:
        st.session_state.urls_input = ""
    if "keywords_input" not in st.session_state:
        st.session_state.keywords_input = ""

    st.session_state.urls_input = st.text_area(
        "URLs (one per line):", value=st.session_state.urls_input, key="urls_text", height=120
    )
    if st.button("Load saved URLs"):
        st.session_state.urls_input = "\n".join(get_all_urls())
        st.rerun()

    st.session_state.keywords_input = st.text_area(
        "Keywords (one per line):", value=st.session_state.keywords_input, key="keywords_text", height=80
    )
    if st.button("Load saved keywords"):
        st.session_state.keywords_input = "\n".join(get_all_keywords())
        st.rerun()

    if st.button("Scrape", type="primary"):
        urls = [u.strip() for u in st.session_state.urls_input.splitlines() if u.strip()]
        keywords = [k.strip() for k in st.session_state.keywords_input.splitlines() if k.strip()]

        if not urls or not keywords:
            st.warning("Enter at least one URL and one keyword.")
            return

        try:
            with st.spinner("Scraping..."):
                successes, failures = scrape_all_sites(urls, keywords)

            if successes:
                st.success(f"Completed for {len(successes)} site(s).")
            if failures:
                st.warning(f"{len(failures)} failure(s):")
                for site_kw, err in failures:
                    st.text(f"{site_kw} → {err}")

            results = fetch_results(start_date, end_date, websites=urls, search_words=keywords)
            if results:
                st.write(f"**{len(results)} results** between {start_date} and {end_date}")
                results_table(pd.DataFrame(results), "scrape_results.csv")
            else:
                st.info("No results found for this date range.")

        except Exception as e:
            st.error(f"Unexpected error: {e}")
            logger.error("Error during scraping", exc_info=True)
