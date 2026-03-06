import streamlit as st
import pandas as pd
import pydeck as pdk
from db import fetch_results
from geocoder import get_geocoding_stats
from utils import score_lead, SCORE_LABELS, SCORE_HEX
from tabs.components import date_range_inputs, status_multiselect, results_table

SCORE_COLOURS = {
    5: [192,  57,  43, 210],   # muted red    — Hot
    4: [200, 121,  65, 200],   # muted orange — High
    3: [181, 160,  48, 195],   # muted yellow — Good
    2: [ 58, 110, 168, 185],   # muted blue   — Moderate
    1: [ 90, 100, 114, 170],   # muted grey   — Low
}



def render():
    st.header("Map")

    stats = get_geocoding_stats()
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Geocoded", f"{stats['geocoded_ok']:,}")
    col_b.metric("Failed", f"{stats['geocoded_failed']:,}")
    col_c.metric("Remaining", f"{stats['pending']:,}")

    if stats["pending"] > 0:
        est_hours = stats["pending"] * 1.1 / 3600
        est_str = f"~{est_hours:.1f} hrs" if est_hours >= 1 else f"~{est_hours * 60:.0f} min"
        st.info(
            f"Geocoding worker is processing {stats['pending']:,} remaining records in the background ({est_str} at 1 req/sec). "
            f"The map will populate automatically as records are geocoded."
        )

    st.divider()

    start_date, end_date = date_range_inputs("map", default_days=365 * 5)
    col1, col2 = st.columns(2)
    with col1:
        selected_statuses = status_multiselect("map_statuses")
    with col2:
        min_score = st.selectbox(
            "Minimum lead score", options=[1, 2, 3, 4, 5],
            index=0, format_func=lambda x: SCORE_LABELS[x], key="map_minscore",
            help="Scores are based on keyword matching in the application summary. "
                 "5 = Hot (core AD keywords), 1 = Low (no match). See Help for full details.",
        )

    rows = fetch_results(start_date, end_date, statuses=selected_statuses or None, geocoded_only=True)
    if not rows:
        st.info("No geocoded applications match the current filters. Try widening the date range or including more statuses. If no records have been geocoded yet, run a batch above.")
        return

    df = pd.DataFrame(rows)
    df["score"] = df.apply(lambda r: score_lead(r.get("summary", ""), r.get("address", "")), axis=1)
    df = df[df["score"] >= min_score]

    if df.empty:
        st.info(f"No results at minimum score {SCORE_LABELS[min_score]}.")
        return

    df["colour"] = df["score"].map(SCORE_COLOURS)
    df["validated_date"] = df["validated_date"].astype(str)
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    st.write(f"**{len(df):,} applications mapped**")

    st.pydeck_chart(pdk.Deck(
        layers=[pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["longitude", "latitude"],
            get_fill_color="colour",
            get_radius=6000,
            radius_min_pixels=5,
            radius_max_pixels=22,
            pickable=True,
            auto_highlight=True,
        )],
        initial_view_state=pdk.ViewState(
            latitude=df["latitude"].mean(),
            longitude=df["longitude"].mean(),
            zoom=6,
            min_zoom=3,
            max_zoom=15,
        ),
        tooltip={
            "html": "<b>{status}</b> — {score} stars<br/>{address}<br/><small>{summary}</small>",
            "style": {"backgroundColor": "#1e293b", "color": "white", "maxWidth": "300px"},
        },
    ))

    legend_items = [
        (5, "Hot"), (4, "High"), (3, "Good"), (2, "Moderate"), (1, "Low")
    ]
    dots = " &nbsp;·&nbsp; ".join(
        f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;'
        f'background:{SCORE_HEX[s]};margin-right:5px;vertical-align:middle;'
        f'box-shadow:0 0 4px {SCORE_HEX[s]}88;"></span>'
        f'<span style="color:#8AABB8;font-size:0.78rem;">{label} ({s})</span>'
        for s, label in legend_items
    )
    st.markdown(f'<div style="margin-top:0.5rem">{dots}</div>', unsafe_allow_html=True)

    with st.expander("Show data table"):
        cols = ["status", "score", "validated_date", "address", "summary", "reference_no", "full_link"]
        results_table(df[[c for c in cols if c in df.columns]], "map_results.csv")
