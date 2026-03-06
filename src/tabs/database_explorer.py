import streamlit as st
import pandas as pd
from db import fetch_results
from store import get_all_urls
from tabs.components import date_range_inputs, status_multiselect, results_table


def render():
    st.header("Database Explorer")
    start_date, end_date = date_range_inputs("de", default_days=30)

    all_urls = get_all_urls()
    selected_urls = st.multiselect("Council / website:", options=all_urls, default=all_urls)
    selected_statuses = status_multiselect("de_statuses")
    keyword_input = st.text_area("Search summary (one keyword per line):", height=80)
    selected_keywords = [k.strip() for k in keyword_input.split("\n") if k.strip()]

    results = fetch_results(
        start_date, end_date,
        websites=selected_urls or None,
        statuses=selected_statuses or None,
        summary_keywords=selected_keywords or None,
    )
    if results:
        st.caption(f"{len(results)} results")
        results_table(pd.DataFrame(results), "explorer_results.csv")
    else:
        st.info("No results found for the selected filters.")
