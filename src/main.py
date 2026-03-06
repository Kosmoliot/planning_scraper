import streamlit as st
from tabs import manual_scraper, failed_urls, manage_data, leads, map_view, help as help_tab

st.set_page_config(
    page_title="Planning Applications",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
html, body, .stApp {
    background-color: #0C1219;
    color: #C5D5DF;
    font-family: 'Inter', sans-serif;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #0A1018 !important;
    border-right: 1px solid #1A2A38;
    min-width: 220px !important;
    max-width: 220px !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 0;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stRadio span {
    color: #6A8A9A !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}

/* ── Nav buttons ── */
section[data-testid="stSidebar"] .stButton {
    margin: 0 !important;
    padding: 0 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-left: 2px solid transparent !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    color: #5A7A8A !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.02em !important;
    padding: 10px 20px !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(58, 159, 197, 0.07) !important;
    border-left-color: #3A9FC5 !important;
    color: #A0C0D0 !important;
}
section[data-testid="stSidebar"] .stButton > button:focus {
    outline: none !important;
    box-shadow: none !important;
}

/* ── Main content ── */
.main .block-container {
    padding: 2rem 3rem;
    max-width: 1400px;
}

/* ── Headers ── */
h1 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #D8E8F0;
    letter-spacing: -0.02em;
    border-bottom: 1px solid #1A2A38;
    padding-bottom: 0.75rem;
    margin-bottom: 1.5rem;
}
h2 {
    font-size: 1.05rem;
    font-weight: 600;
    color: #B0C8D8;
}
h3 {
    font-size: 0.9rem;
    font-weight: 500;
    color: #6A8A9A;
}

/* ── Buttons ── */
.stButton > button {
    background-color: transparent;
    color: #3A9FC5;
    border: 1px solid #1E4A60;
    border-radius: 4px;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    padding: 0.4rem 1rem;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background-color: rgba(58, 159, 197, 0.10);
    border-color: #3A9FC5;
    color: #5AB8D8;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1A5A78, #3A9FC5);
    color: #E8F4FA;
    border: none;
    font-weight: 600;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2070A0, #4AAFE5);
}

/* ── Inputs ── */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #0F1C28;
    border: 1px solid #1E3040;
    border-radius: 4px;
    color: #C5D5DF;
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #3A9FC5;
    box-shadow: 0 0 0 2px rgba(58, 159, 197, 0.18);
}
input::placeholder, textarea::placeholder { color: #2A4050 !important; }

/* ── Select / Multiselect ── */
.stMultiSelect > div > div,
.stSelectbox > div > div {
    background-color: #0F1C28 !important;
    border-color: #1E3040 !important;
    border-radius: 4px !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #111D2A, #0C1219);
    border: 1px solid #1A2A38;
    border-top: 2px solid #3A9FC5;
    border-radius: 6px;
    padding: 1rem 1.25rem;
}
[data-testid="metric-container"] label {
    color: #456070 !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #D8E8F0;
    font-size: 1.75rem;
    font-weight: 700;
}

/* ── Dataframe ── */
.stDataFrame { border: 1px solid #1A2A38; border-radius: 6px; }
[data-testid="stDataFrame"] thead th {
    background-color: #0F1C28 !important;
    color: #456070 !important;
    font-size: 0.7rem !important;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-bottom: 1px solid #3A9FC5 !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background-color: rgba(58, 159, 197, 0.05) !important;
}

/* ── Alerts ── */
[data-testid="stNotification"] {
    background-color: #0F1C28;
    border: 1px solid #1E3040;
    border-radius: 4px;
    font-size: 0.875rem;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid #1A2A38; margin: 1rem 0; }

/* ── Expander ── */
details {
    background-color: #0F1C28 !important;
    border: 1px solid #1A2A38 !important;
    border-radius: 6px !important;
}
summary { color: #6A8A9A !important; font-size: 0.875rem; font-weight: 500; }

/* ── Caption ── */
.stCaption { color: #3A5060 !important; font-size: 0.78rem; }

/* ── Progress ── */
.stProgress > div > div { background: linear-gradient(90deg, #1A5A78, #3A9FC5); }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #3A9FC5 !important; }

section[data-testid="stSidebar"] .stButton > button {
    all: unset;
    display: flex !important;
    align-items: center;
    width: 100%;
    padding: 10px 20px;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.02em;
    color: #5A7A8A !important;
    border-left: 2px solid transparent;
    cursor: pointer;
    transition: all 0.15s ease;
    box-sizing: border-box;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(58, 159, 197, 0.07) !important;
    border-left-color: #3A9FC5 !important;
    color: #A0C0D0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0C1219; }
::-webkit-scrollbar-thumb { background: #1E3040; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3A9FC5; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='padding: 1.5rem 1.5rem 1rem;'>
            <div style='font-size: 1rem; font-weight: 700; color: #D8E8F0;
                        letter-spacing: -0.01em; font-family: Inter, sans-serif;'>
                Planning Applications
            </div>
        </div>
        <div style='height: 1px; background: #1A2A38; margin: 0 0 0.5rem;'></div>
    """, unsafe_allow_html=True)

    if st.session_state.get("active_page") not in ["Leads", "Map", "Manual Search", "Failed URLs", "Manage Data", "Help"]:
        st.session_state["active_page"] = "Leads"

    active = st.session_state.get("active_page", "Leads")

    # Highlight active nav button via injected CSS
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"][kind="secondary"]:not(:hover) {{
        color: #5A7A8A !important;
    }}
    [data-testid="stSidebar"] button[key="nav_{active}"],
    [data-testid="stSidebar"] div:has(> button[key="nav_{active}"]) > button {{
        background: rgba(58,159,197,0.10) !important;
        border-left: 2px solid #3A9FC5 !important;
        color: #3A9FC5 !important;
        font-weight: 500 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    nav_items = ["Leads", "Map", "Manual Search", "Failed URLs", "Manage Data"]
    for item in nav_items:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state["active_page"] = item
            st.rerun()

    st.markdown("""
        <a href="?nav=Help" target="_self" style="
            position:fixed;bottom:0;left:0;width:220px;
            padding:10px 20px;
            background:#0A1018;
            border-top:1px solid #1A2A38;
            color:#5A7A8A;
            font-family:Inter,sans-serif;
            font-size:0.85rem;
            text-decoration:none;
            display:block;
            z-index:9999;
            transition:all 0.15s ease;
        " onmouseover="this.style.background='rgba(58,159,197,0.07)';this.style.borderLeftColor='#3A9FC5';this.style.color='#A0C0D0';"
           onmouseout="this.style.background='#0A1018';this.style.borderLeftColor='transparent';this.style.color='#5A7A8A';">
            Help
        </a>
    """, unsafe_allow_html=True)


# ── Page routing ─────────────────────────────────────────────────────────────
pages = {
    "Leads":         leads.render,
    "Map":           map_view.render,
    "Manual Search": manual_scraper.render,
    "Failed URLs":   failed_urls.render,
    "Manage Data":   manage_data.render,
    "Help":          help_tab.render,
}

if st.query_params.get("nav") == "Help":
    st.session_state["active_page"] = "Help"
    st.query_params.clear()
    st.rerun()

active = st.session_state.get("active_page", "Leads")
if active in pages:
    pages[active]()
