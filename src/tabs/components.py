import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils import NORMALISED_STATUSES

DISPLAY_COLS = {
    "reference_no": "Ref No",
    "validated_date": "Date",
    "status": "Status",
    "address": "Address",
    "summary": "Summary",
    "website": "Council",
    "search_word": "Keyword",
    "full_link": "Link",
    "scraped_at": "Scraped At",
    "lead_label": "Lead Score",
    "score": "Score",
}


def date_range_inputs(key_prefix: str, default_days: int = 30):
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("From", value=date.today() - timedelta(days=default_days), key=f"{key_prefix}_start")
    with col2:
        end = st.date_input("To", value=date.today(), key=f"{key_prefix}_end")
    return start, end


def status_multiselect(key: str, default=None):
    return st.multiselect(
        "Status",
        options=NORMALISED_STATUSES,
        default=default if default is not None else NORMALISED_STATUSES,
        key=key,
    )


def results_table(df: pd.DataFrame, filename: str = "results.csv"):
    df = df.rename(columns={k: v for k, v in DISPLAY_COLS.items() if k in df.columns})
    st.dataframe(
        df,
        use_container_width=True,
        column_config={"Link": st.column_config.LinkColumn("Link", display_text="View")},
        hide_index=True,
    )
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), filename, "text/csv")
