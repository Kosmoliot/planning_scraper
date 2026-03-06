import streamlit as st
import pandas as pd
from db import fetch_failed_urls


def render():
    st.header("Failed URLs")

    results = fetch_failed_urls()

    if not results:
        st.info("No failed URLs recorded in the most recent scrape.")
        return

    df = pd.DataFrame(results)

    run_date = pd.to_datetime(df["timestamp"]).dt.date.max()
    st.caption(f"Showing failures from scrape run on **{run_date}** — {len(df)} URL(s) failed")

    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
    df = df.rename(columns={"url": "URL", "message": "Error", "timestamp": "Time"})
    df = df[["Time", "URL", "Error"]]

    st.dataframe(df, use_container_width=True, hide_index=True)
