import streamlit as st
import pandas as pd
from db import fetch_results
from store import get_all_urls
from utils import score_lead, SCORE_LABELS
from tabs.components import date_range_inputs, status_multiselect, results_table, DISPLAY_COLS

_DEFAULT_STATUSES = ["Pending", "Approved"]


def render():
    st.header("Leads")
    st.caption(
        "Pending = decision imminent. Approved = permission granted, equipment purchase likely soon."
    )

    start_date, end_date = date_range_inputs("leads", default_days=180)

    col1, col2 = st.columns(2)
    with col1:
        selected_statuses = status_multiselect("leads_statuses", default=_DEFAULT_STATUSES)
    with col2:
        min_score = st.selectbox(
            "Minimum lead score", options=[1, 2, 3, 4, 5],
            index=0, format_func=lambda x: SCORE_LABELS[x], key="leads_minscore"
        )

    all_urls = get_all_urls()
    selected_urls = st.multiselect("Filter by council (leave blank for all):", options=all_urls, key="leads_urls")

    results = fetch_results(start_date, end_date, websites=selected_urls or None, statuses=selected_statuses or None)
    if not results:
        st.info("No applications found for the selected filters.")
        return

    df = pd.DataFrame(results)
    df["lead_score"] = df.apply(lambda r: score_lead(r.get("summary", ""), r.get("address", "")), axis=1)
    df["lead_label"] = df["lead_score"].map(SCORE_LABELS)
    df = df[df["lead_score"] >= min_score]

    if df.empty:
        st.info(f"No leads with score >= {SCORE_LABELS[min_score]}.")
        return

    status_order = {"Pending": 0, "Approved": 1}
    df["_order"] = df["status"].map(status_order).fillna(2)
    df = df.sort_values(["_order", "lead_score", "validated_date"], ascending=[True, False, False])
    df = df.drop(columns=["_order"])

    cols = ["lead_label", "status", "validated_date", "address", "summary", "reference_no", "website", "full_link"]
    df = df[[c for c in cols if c in df.columns]]

    st.write(f"**{len(df)} leads** — {(df['status']=='Pending').sum()} Pending, {(df['status']=='Approved').sum()} Approved")
    results_table(df, "leads.csv")
