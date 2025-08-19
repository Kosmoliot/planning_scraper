import streamlit as st
from tabs import monthly_overview, manual_scraper, database_explorer, failed_urls

st.set_page_config(page_title="Planning Scraper", layout="wide")

tab1, tab2, tab3, tab4 = st.tabs(["Monthly Overview", "Manual Scraper", "Database Explorer", "Failed URLs"])

with tab1:
    monthly_overview.render()

with tab2:
    manual_scraper.render()

with tab3:
    database_explorer.render()

with tab4:
    failed_urls.render()
