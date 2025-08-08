import streamlit as st
import datetime
import pandas as pd
from logger import get_logger
from scraper import scrape_all_sites
from db import fetch_filtered_results
from store import get_all_keywords, get_all_urls

def render():
    # Setup logging
    logger = get_logger()

    st.set_page_config(page_title="Planning Scraper", layout="wide")
    st.header("🔍 Manual Scraper")


    # Date Filter
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

        if not urls or not keywords:
            st.warning("Please enter at least one URL and one keyword")
            logger.warning("User provided no URLs or keywords.")
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
                logger.error("Error during scraping or filtering", exc_info=True)
