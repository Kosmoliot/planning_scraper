import streamlit as st
import pandas as pd
from db import fetch_filtered_results
from datetime import datetime, timedelta

def render():
    st.header("Monthly Overview")
    today = datetime.today().date()
    last_month = today - timedelta(days=30)

    st.write(f"Showing planning applications from **{last_month}** to **{today}**")

    results = fetch_filtered_results(start_date=last_month, end_date=today, websites=[], keywords=[])
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "monthly_results.csv", "text/csv")
    else:
        st.info("No planning applications found for the last 30 days.")
