import streamlit as st
import pandas as pd
from db import fetch_failed_urls

def render():
    st.header("❌ Today's Failed URLs")

    df = fetch_failed_urls()
    results = fetch_failed_urls()

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.warning("No Failed URLs today")