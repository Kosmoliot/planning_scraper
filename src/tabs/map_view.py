import streamlit as st
import pandas as pd
import pydeck as pdk
from db import fetch_results
from geocoder import get_geocoding_stats, run_geocoding_batch, BATCH_SIZE
from utils import score_lead, SCORE_LABELS
from tabs.components import date_range_inputs, status_multiselect, results_table

SCORE_COLOURS = {
    5: [220,  38,  38, 200],
    4: [234, 127,  36, 200],
    3: [234, 197,  36, 200],
    2: [ 59, 130, 246, 200],
    1: [156, 163, 175, 180],
}


def render():
    st.header("Map")

    stats = get_geocoding_stats()
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Geocoded", f"{stats['geocoded_ok']:,}")
    col_b.metric("Failed", f"{stats['geocoded_failed']:,}")
    col_c.metric("Remaining", f"{stats['pending']:,}")

    if stats["pending"] > 0:
        with st.expander(f"Geocode {stats['pending']:,} remaining records"):
            st.caption(f"Free OpenStreetMap API, 1 req/sec. Batch of {BATCH_SIZE} ≈ {BATCH_SIZE * 1.1 / 60:.0f} min.")
            batch = st.number_input("Batch size", min_value=10, max_value=BATCH_SIZE, value=100, step=10)
            if st.button("Start geocoding"):
                bar = st.progress(0)
                txt = st.empty()
                ok, fail, remaining = run_geocoding_batch(
                    batch_size=batch,
                    progress_callback=lambda i, t: (bar.progress(i / t), txt.text(f"{i}/{t}"))
                )
                st.success(f"Done — {ok} geocoded, {fail} failed, {remaining:,} remaining.")
                st.rerun()

    st.divider()

    start_date, end_date = date_range_inputs("map", default_days=180)
    col1, col2 = st.columns(2)
    with col1:
        selected_statuses = status_multiselect("map_statuses", default=["Pending", "Approved"])
    with col2:
        min_score = st.selectbox(
            "Minimum lead score", options=[1, 2, 3, 4, 5],
            index=0, format_func=lambda x: SCORE_LABELS[x], key="map_minscore"
        )

    rows = fetch_results(start_date, end_date, statuses=selected_statuses or None, geocoded_only=True)
    if not rows:
        st.info("No geocoded applications found. Run a geocoding batch first.")
        return

    df = pd.DataFrame(rows)
    df["score"] = df.apply(lambda r: score_lead(r.get("summary", ""), r.get("address", "")), axis=1)
    df = df[df["score"] >= min_score]

    if df.empty:
        st.info(f"No results at minimum score {SCORE_LABELS[min_score]}.")
        return

    df["colour"] = df["score"].map(SCORE_COLOURS)
    st.write(f"**{len(df):,} applications mapped**")

    st.pydeck_chart(pdk.Deck(
        layers=[pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["longitude", "latitude"],
            get_fill_color="colour",
            get_radius=800,
            pickable=True,
            auto_highlight=True,
        )],
        initial_view_state=pdk.ViewState(
            latitude=df["latitude"].mean(),
            longitude=df["longitude"].mean(),
            zoom=6,
        ),
        tooltip={
            "html": "<b>{status}</b> — {score} stars<br/>{address}<br/><small>{summary}</small>",
            "style": {"backgroundColor": "#1e293b", "color": "white", "maxWidth": "300px"},
        },
    ))

    st.caption("🔴 Hot (5) · 🟠 High (4) · 🟡 Good (3) · 🔵 Moderate (2) · ⚫ Low (1)")

    with st.expander("Show data table"):
        cols = ["status", "score", "validated_date", "address", "summary", "reference_no", "full_link"]
        results_table(df[[c for c in cols if c in df.columns]], "map_results.csv")
