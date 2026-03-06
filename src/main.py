import streamlit as st
from tabs import manual_scraper, database_explorer, failed_urls, manage_data, leads, map_view

st.set_page_config(page_title="Planning Scraper", layout="wide")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Leads", "Map", "Database Explorer", "Manual Scraper", "Failed URLs", "Manage Data"])

with tab1:
    leads.render()

with tab2:
    map_view.render()

with tab3:
    database_explorer.render()

with tab4:
    manual_scraper.render()

with tab5:
    failed_urls.render()

with tab6:
    manage_data.render()
