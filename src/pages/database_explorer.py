import streamlit as st
import pandas as pd
from db import fetch_filtered_results
from store import get_all_urls, get_all_keywords
import datetime

def render():
    st.header("🗂 Database Explorer")

    all_urls = get_all_urls()
    all_keywords = get_all_keywords()

    selected_urls = st.multiselect("Filter by website(s):", options=all_urls, default=all_urls)
    selected_keywords = st.multiselect("Filter by keyword(s):", options=all_keywords, default=all_keywords)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", datetime.date.today() - datetime.timedelta(days=30))
    with col2:
        end_date = st.date_input("End date", datetime.date.today())

    if st.button("Search"):
        results = fetch_filtered_results(start_date, end_date, selected_urls, selected_keywords)
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "filtered_results.csv", "text/csv")
        else:
            st.info("No results found for the selected filters.")
