import streamlit as st
import pandas as pd
from db import fetch_results
from store import get_all_urls, get_all_keywords
from utils import score_lead, SCORE_LABELS, SCORE_HEX
from tabs.components import date_range_inputs, status_multiselect

_DEFAULT_STATUSES = ["Pending", "Approved"]


_COL_WIDTHS = {
    "lead_score":    ("Score",   "90px"),
    "status":        ("Status",  "100px"),
    "validated_date":("Date",    "95px"),
    "address":       ("Address", "220px"),
    "summary":       ("Summary", "300px"),
    "reference_no":  ("Ref",     "110px"),
    "website":       ("Council", "160px"),
    "full_link":     ("Link",    "55px"),
}


def _render_leads_table(df):
    th = (
        "background:#0F1C28;color:#456070;font-size:0.7rem;font-weight:600;"
        "letter-spacing:0.08em;text-transform:uppercase;padding:8px 12px;"
        "border-bottom:1px solid #3A9FC5;white-space:nowrap;"
        "resize:horizontal;overflow:hidden;position:relative;"
    )
    td = (
        "padding:7px 12px;border-bottom:1px solid #1A2A38;"
        "color:#C5D5DF;font-size:0.82rem;white-space:nowrap;"
        "overflow:hidden;text-overflow:ellipsis;max-width:0;"
    )

    col_keys = [c for c in _COL_WIDTHS if c in df.columns]

    headers = "".join(
        f'<th style="{th}width:{_COL_WIDTHS[c][1]};min-width:60px;">{_COL_WIDTHS[c][0]}</th>'
        for c in col_keys
    )

    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for col in col_keys:
            val = row.get(col, "") or ""
            if col == "lead_score":
                score  = int(val)
                label  = SCORE_LABELS.get(score, "")
                colour = SCORE_HEX.get(score, "#5A6472")
                circle = (
                    f'<span style="display:inline-block;width:9px;height:9px;border-radius:50%;'
                    f'background:{colour};margin-right:6px;vertical-align:middle;'
                    f'box-shadow:0 0 5px {colour}99;"></span>'
                )
                cells += f'<td style="{td}">{circle}{label}</td>'
            elif col == "full_link" and val:
                cells += f'<td style="{td}"><a href="{val}" target="_blank" style="color:#3A9FC5;text-decoration:none;">View</a></td>'
            else:
                cells += f'<td style="{td}" title="{val}">{val}</td>'
        rows_html += (
            f'<tr onmouseover="this.style.background=\'rgba(58,159,197,0.05)\'"'
            f' onmouseout="this.style.background=\'\'">{cells}</tr>'
        )

    st.markdown(f"""
    <div style="overflow-x:auto;border:1px solid #1A2A38;border-radius:6px;margin-top:0.5rem;">
      <table style="table-layout:fixed;width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)


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
            index=0, format_func=lambda x: SCORE_LABELS[x], key="leads_minscore",
            help="Scores are based on keyword matching in the application summary. "
                 "5 = Hot (core AD keywords), 1 = Low (no match). See Help for full details.",
        )
        legend_items = [(5, "Hot"), (4, "High"), (3, "Good"), (2, "Moderate"), (1, "Low")]
        dots = " &nbsp;·&nbsp; ".join(
            f'<span style="display:inline-block;width:9px;height:9px;border-radius:50%;'
            f'background:{SCORE_HEX[s]};margin-right:4px;vertical-align:middle;'
            f'box-shadow:0 0 4px {SCORE_HEX[s]}88;"></span>'
            f'<span style="color:#8AABB8;font-size:0.75rem;">{label}</span>'
            for s, label in legend_items
        )
        st.markdown(f'<div style="margin-top:0.25rem">{dots}</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        all_urls = get_all_urls()
        selected_urls = st.multiselect("Filter by council:", options=all_urls, key="leads_urls")
    with col4:
        all_keywords = get_all_keywords()
        selected_keywords = st.multiselect("Filter by keyword:", options=all_keywords, key="leads_keywords")

    results = fetch_results(
        start_date, end_date,
        websites=selected_urls or None,
        statuses=selected_statuses or None,
        summary_keywords=selected_keywords or None,
    )
    if not results:
        st.info("No applications found for the selected filters.")
        return

    df = pd.DataFrame(results)
    df["lead_score"] = df.apply(lambda r: score_lead(r.get("summary", ""), r.get("address", "")), axis=1)
    df = df[df["lead_score"] >= min_score]

    if df.empty:
        st.info(f"No leads at minimum score {SCORE_LABELS[min_score]}.")
        return

    status_order = {"Pending": 0, "Approved": 1}
    df["_order"] = df["status"].map(status_order).fillna(2)
    df = df.sort_values(["_order", "lead_score", "validated_date"], ascending=[True, False, False])
    df = df.drop(columns=["_order"])

    st.write(f"**{len(df)} leads** — {(df['status']=='Pending').sum()} Pending, {(df['status']=='Approved').sum()} Approved")

    _render_leads_table(df)

    export_cols = ["status", "validated_date", "address", "summary", "reference_no", "website", "full_link"]
    st.download_button(
        "Download CSV",
        df[[c for c in export_cols if c in df.columns]].to_csv(index=False).encode("utf-8"),
        "leads.csv",
        "text/csv",
    )
