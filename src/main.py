import streamlit as st
from tabs import monthly_overview, manual_scraper, database_explorer

st.set_page_config(page_title="Planning Scraper", layout="wide")

tab1, tab2, tab3 = st.tabs(["Monthly Overview", "Manual Scraper", "Database Explorer"])

with tab1:
    monthly_overview.render()

with tab2:
    manual_scraper.render()

with tab3:
    database_explorer.render()
