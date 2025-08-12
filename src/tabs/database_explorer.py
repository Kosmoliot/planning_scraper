import streamlit as st
import pandas as pd
from db import fetch_results_by_summary
from store import get_all_urls
import datetime


def render():
    st.header("🗂 Database Explorer")

    #Date filters first
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", datetime.date.today() - datetime.timedelta(days=30))
    with col2:
        end_date = st.date_input("End date", datetime.date.today())

    #Website multiselect
    all_urls = get_all_urls()
    selected_urls = st.multiselect("Filter by website(s):", options=all_urls, default=all_urls)

    #Keyword search box (one keyword per line)
    st.write("Enter one keyword per line:")
    keyword_input = st.text_area(
        "Enter keywords (one per line):",
        height=100
    )
    selected_keywords = [k.strip() for k in keyword_input.split("\n") if k.strip()]

    #Search button
    if st.button("Search"):
        results = fetch_results_by_summary(start_date, end_date, selected_urls, selected_keywords)
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "filtered_results.csv", "text/csv")
        else:
            st.info("No results found for the selected filters.")