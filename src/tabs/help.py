import streamlit as st
from utils import SCORE_HEX, SCORE_LABELS


def render():
    st.header("Support")

    # ── Lead Scoring ──────────────────────────────────────────────────────────
    st.subheader("Lead Scoring")
    st.write(
        "Every planning application is automatically scored 1–5 based on keyword matches "
        "found in the application summary and address. The more relevant the keywords, "
        "the higher the score."
    )

    legend_items = [(5, "Hot"), (4, "High"), (3, "Good"), (2, "Moderate"), (1, "Low")]
    dots = " &nbsp;&nbsp; ".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;">'
        f'<span style="display:inline-block;width:11px;height:11px;border-radius:50%;'
        f'background:{SCORE_HEX[s]};box-shadow:0 0 6px {SCORE_HEX[s]}99;"></span>'
        f'<span style="color:#C5D5DF;font-size:0.85rem;font-weight:500;">{s} — {label}</span>'
        f'</span>'
        for s, label in legend_items
    )
    st.markdown(f'<div style="margin:0.75rem 0 1.25rem">{dots}</div>', unsafe_allow_html=True)

    st.markdown("#### Keyword tiers")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div style="border:1px solid #1A2A38;border-top:2px solid {SCORE_HEX[5]};'
            f'border-radius:6px;padding:1rem;">'
            f'<div style="font-size:0.7rem;font-weight:600;letter-spacing:0.1em;'
            f'text-transform:uppercase;color:#456070;margin-bottom:0.6rem;">High Value &nbsp;+3 pts</div>'
            f'<div style="font-size:0.82rem;color:#C5D5DF;line-height:1.8;">'
            f'anaerobic<br>digester<br>digestion<br>biogas<br>biomethane<br>ad plant<br>'
            f'anaerobic digestion<br>anaerobic digester'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div style="border:1px solid #1A2A38;border-top:2px solid {SCORE_HEX[3]};'
            f'border-radius:6px;padding:1rem;">'
            f'<div style="font-size:0.7rem;font-weight:600;letter-spacing:0.1em;'
            f'text-transform:uppercase;color:#456070;margin-bottom:0.6rem;">Medium Value &nbsp;+2 pts</div>'
            f'<div style="font-size:0.82rem;color:#C5D5DF;line-height:1.8;">'
            f'slurry tank<br>slurry lagoon<br>slurry store<br>slurry pit<br>'
            f'storage tank<br>concrete tank<br>water tank<br>digestate<br>'
            f'biodigester<br>gas holder<br>fermentation tank<br>effluent tank<br>'
            f'effluent lagoon<br>waste water tank'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div style="border:1px solid #1A2A38;border-top:2px solid {SCORE_HEX[2]};'
            f'border-radius:6px;padding:1rem;">'
            f'<div style="font-size:0.7rem;font-weight:600;letter-spacing:0.1em;'
            f'text-transform:uppercase;color:#456070;margin-bottom:0.6rem;">Low Value &nbsp;+1 pt</div>'
            f'<div style="font-size:0.82rem;color:#C5D5DF;line-height:1.8;">'
            f'slurry<br>silo<br>farm waste<br>organic waste<br>sewage<br>'
            f'manure<br>feedstock<br>livestock<br>agricultural waste<br>'
            f'waste treatment<br>composting'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### Score thresholds")
    thresholds = [
        ("9+ pts",  5, "Hot",      "Core AD equipment keywords present — very high relevance"),
        ("6–8 pts", 4, "High",     "Strong match across multiple relevant keyword tiers"),
        ("3–5 pts", 3, "Good",     "Moderate match — worth reviewing"),
        ("1–2 pts", 2, "Moderate", "Weak match — low-value keywords only"),
        ("0 pts",   1, "Low",      "No matching keywords found"),
    ]
    for pts, score, label, desc in thresholds:
        colour = SCORE_HEX[score]
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;padding:7px 0;'
            f'border-bottom:1px solid #1A2A38;">'
            f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;'
            f'background:{colour};box-shadow:0 0 5px {colour}99;flex-shrink:0;"></span>'
            f'<span style="color:#6A8A9A;font-size:0.78rem;width:60px;flex-shrink:0;">{pts}</span>'
            f'<span style="color:{colour};font-size:0.82rem;font-weight:500;width:90px;flex-shrink:0;">'
            f'{score} — {label}</span>'
            f'<span style="color:#8AABB8;font-size:0.82rem;">{desc}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Status Definitions ────────────────────────────────────────────────────
    st.subheader("Application Statuses")
    statuses = [
        ("Pending",   "#3A9FC5", "Decision not yet made — ideal for early outreach"),
        ("Approved",  "#2A8A5A", "Permission granted — equipment purchase likely imminent"),
        ("Refused",   "#C0392B", "Application rejected"),
        ("Withdrawn", "#B5A030", "Applicant withdrew the application"),
        ("Decided",   "#5A6472", "Outcome recorded but approval/refusal unclear from portal"),
        ("Unknown",   "#2A3A4A", "Status could not be mapped to a standard value"),
    ]
    for status, colour, desc in statuses:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;padding:7px 0;'
            f'border-bottom:1px solid #1A2A38;">'
            f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;'
            f'background:{colour};flex-shrink:0;"></span>'
            f'<span style="color:{colour};font-size:0.82rem;font-weight:500;width:90px;flex-shrink:0;">'
            f'{status}</span>'
            f'<span style="color:#8AABB8;font-size:0.82rem;">{desc}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
