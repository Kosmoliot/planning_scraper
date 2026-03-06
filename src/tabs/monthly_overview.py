import streamlit as st
import pandas as pd
from db import fetch_results
from tabs.components import date_range_inputs, status_multiselect, results_table


def render():
    st.header("Monthly Overview")
    start_date, end_date = date_range_inputs("mo", default_days=30)
    selected_statuses = status_multiselect("mo_statuses")

    results = fetch_results(start_date, end_date, statuses=selected_statuses or None)
    if results:
        results_table(pd.DataFrame(results), "monthly_results.csv")
    else:
        st.info("No planning applications found for this period.")
