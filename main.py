import streamlit as st
from db import get_conn
from auth import auth_page
from ui import eintrag_dialog, dashboard_page, entries_page, settings_page

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Finanz-Master",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MASTER CSS: Dark Finance Glassmorphism ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

:root {
    --cyan:      #00D4FF;
    --cyan-dim:  rgba(0, 212, 255, 0.12);
    --cyan-glow: rgba(0, 212, 255, 0.3);
    --green:     #00FF87;
    --red:       #FF4C6A;
    --bg:        #080B14;
    --bg2:       #0D1117;
    --glass:     rgba(255,255,255,0.035);
    --glass-b:   rgba(255,255,255,0.07);
    --border:    rgba(255,255,255,0.07);
    --border-h:  rgba(0, 212, 255, 0.35);
    --text:      #E2E8F0;
    --muted:     #64748B;
    --r:         14px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg) !important;
}

/* Hintergrund-Mesh */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 70% 50% at 5% 5%, rgba(0,212,255,0.06) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 95% 95%, rgba(0,255,135,0.04) 0%, transparent 50%),
        radial-gradient(ellipse 40% 35% at 50% 50%, rgba(100,40,255,0.03) 0%, transparent 65%),
        #080B14 !important;
    background-attachment: fixed !important;
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.25); border-radius: 2px; }

/* ── SIDEBAR ──────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(8,11,20,0.97) !important;
    border-right: 1px solid var(--border) !important;
    backdrop-filter: blur(24px);
}
[data-testid="stSidebar"] .stButton > button {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.25s ease !important;
    width: 100%;
    text-align: left !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--cyan-dim) !important;
    border-color: var(--border-h) !important;
    color: var(--cyan) !important;
    transform: translateX(4px);
    box-shadow: 4px 0 20px var(--cyan-glow);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.18), rgba(0,212,255,0.07)) !important;
    border-color: rgba(0,212,255,0.45) !important;
    color: var(--cyan) !important;
    font-weight: 600 !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.12), inset 0 1px 0 rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(0,212,255,0.28), rgba(0,212,255,0.12)) !important;
    box-shadow: 0 0 35px rgba(0,212,255,0.25), inset 0 1px 0 rgba(255,255,255,0.1);
    transform: translateX(4px);
}
[data-testid="stSidebar"] .stRadio > div { gap: 3px !important; }
[data-testid="stSidebar"] .stRadio label {
    border-radius: 10px !important;
    padding: 0.55rem 0.85rem !important;
    color: var(--muted) !important;
    font-size: 0.88rem !important;
    transition: all 0.2s !important;
    border: 1px solid transparent !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: var(--cyan-dim) !important;
    border-color: rgba(0,212,255,0.28) !important;
    color: var(--cyan) !important;
    font-weight: 600 !important;
    box-shadow: 0 0 12px rgba(0,212,255,0.08);
}
[data-testid="stSidebar"] .stRadio label:hover:not(:has(input:checked)) {
    background: var(--glass) !important;
    color: #94A3B8 !important;
    border-color: var(--border) !important;
}
[data-testid="stSidebar"] [data-testid="stRadioLabel"] { display: none; }

/* ── METRIKEN ─────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    padding: 1.2rem 1.4rem !important;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(16px);
    transition: all 0.3s ease !important;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
}
[data-testid="metric-container"]:hover {
    border-color: var(--border-h) !important;
    background: rgba(0,212,255,0.06) !important;
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(0,212,255,0.1), 0 0 0 1px rgba(0,212,255,0.1);
}
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: -0.025em !important;
    line-height: 1.2 !important;
}

/* ── DATAFRAMES ───────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important;
    backdrop-filter: blur(12px);
}
[data-testid="stDataFrame"] thead th {
    background: rgba(0,0,0,0.5) !important;
    color: var(--muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 0.65rem 1rem !important;
}
[data-testid="stDataFrame"] tbody tr {
    border-bottom: 1px solid rgba(255,255,255,0.025) !important;
    transition: background 0.15s !important;
}
[data-testid="stDataFrame"] tbody tr:hover {
    background: rgba(0,212,255,0.04) !important;
}
[data-testid="stDataFrame"] tbody td {
    font-size: 0.875rem !important;
    padding: 0.6rem 1rem !important;
    color: #CBD5E1 !important;
}

/* ── EXPANDER ─────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    backdrop-filter: blur(12px);
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stExpander"]:hover { border-color: rgba(0,212,255,0.18) !important; }
[data-testid="stExpander"] summary {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    color: var(--text) !important;
    padding: 0.85rem 1.1rem !important;
}

/* ── TABS ─────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(0,0,0,0.4) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 0 !important;
    border: 1px solid var(--border) !important;
    width: fit-content;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.42rem 1.1rem !important;
    font-size: 0.87rem !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: var(--cyan-dim) !important;
    color: var(--cyan) !important;
    border: 1px solid rgba(0,212,255,0.28) !important;
    font-weight: 600 !important;
    box-shadow: 0 0 12px rgba(0,212,255,0.08) !important;
}

/* ── BUTTONS ──────────────────────────────── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    border: 1px solid var(--border) !important;
    background: var(--glass) !important;
    color: #94A3B8 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.22), rgba(0,212,255,0.08)) !important;
    border-color: rgba(0,212,255,0.45) !important;
    color: var(--cyan) !important;
    font-weight: 600 !important;
    box-shadow: 0 0 18px rgba(0,212,255,0.1), inset 0 1px 0 rgba(255,255,255,0.07);
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 30px rgba(0,212,255,0.22), inset 0 1px 0 rgba(255,255,255,0.1);
    transform: translateY(-1px);
}
.stButton > button:not([kind="primary"]):hover {
    border-color: rgba(0,212,255,0.22) !important;
    color: var(--text) !important;
    background: rgba(255,255,255,0.05) !important;
}

/* ── SEGMENTED CONTROL ────────────────────── */
[data-testid="stSegmentedControl"] {
    background: rgba(0,0,0,0.4) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 3px !important;
}
[data-testid="stSegmentedControl"] button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.2s !important;
}
[data-testid="stSegmentedControl"] button[aria-checked="true"] {
    background: var(--cyan-dim) !important;
    color: var(--cyan) !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    font-weight: 600 !important;
}

/* ── INPUTS ───────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background: rgba(0,0,0,0.45) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(0,212,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,212,255,0.08) !important;
    outline: none !important;
}

/* ── DIALOGE ──────────────────────────────── */
[data-testid="stModal"] > div {
    background: rgba(10,14,24,0.97) !important;
    border: 1px solid rgba(0,212,255,0.18) !important;
    border-radius: 18px !important;
    backdrop-filter: blur(30px) !important;
    box-shadow: 0 30px 80px rgba(0,0,0,0.75), 0 0 60px rgba(0,212,255,0.06) !important;
}

/* ── ALERTS ───────────────────────────────── */
[data-testid="stInfo"] {
    background: rgba(0,212,255,0.06) !important;
    border: 1px solid rgba(0,212,255,0.18) !important;
    border-radius: 10px !important; color: #94CFDF !important;
}
[data-testid="stSuccess"] {
    background: rgba(0,255,135,0.06) !important;
    border: 1px solid rgba(0,255,135,0.22) !important; border-radius: 10px !important;
}
[data-testid="stError"] {
    background: rgba(255,76,106,0.07) !important;
    border: 1px solid rgba(255,76,106,0.22) !important; border-radius: 10px !important;
}
[data-testid="stWarning"] {
    background: rgba(255,180,0,0.06) !important;
    border: 1px solid rgba(255,180,0,0.22) !important; border-radius: 10px !important;
}

/* ── PLOTLY ───────────────────────────────── */
[data-testid="stPlotlyChart"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    padding: 0.5rem;
    backdrop-filter: blur(10px);
}

/* ── TYPO ─────────────────────────────────── */
h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.035em !important;
    color: var(--text) !important;
}
h2 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #CBD5E1 !important;
    font-size: 1.2rem !important;
}
h3 {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    color: #94A3B8 !important;
    font-size: 0.95rem !important;
}

/* ── DIVIDER ──────────────────────────────── */
hr {
    border: none !important; height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent) !important;
    margin: 1rem 0 !important;
}

/* ── LAYOUT ───────────────────────────────── */
.main .block-container {
    padding: 1.5rem 2.5rem 3rem !important;
    max-width: 1440px !important;
}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ROUTING ---
if not st.session_state.logged_in:
    auth_page()
else:
    conn = get_conn()
    u_id = st.session_state.user_id
    username     = st.session_state.get('username', 'User')
    vorname      = st.session_state.get('vorname', '')
    display_name = vorname if vorname else username

    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1.2rem 0.4rem 1rem; text-align:center;">
            <div style="
                width:50px; height:50px; border-radius:50%;
                background: linear-gradient(135deg,rgba(0,212,255,0.28),rgba(0,255,135,0.12));
                border: 1px solid rgba(0,212,255,0.38);
                display:flex; align-items:center; justify-content:center;
                margin: 0 auto 0.65rem; font-size:1.3rem;
                box-shadow: 0 0 22px rgba(0,212,255,0.18);
            ">👤</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.97rem;
                        color:#E2E8F0;letter-spacing:-0.01em;">{display_name}</div>
            <div style="font-size:0.72rem;color:#334155;margin-top:2px;letter-spacing:0.04em;">
                @{username}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📝 Einträge", "⚙️ Verwaltung"],
            label_visibility="collapsed"
        )

        st.divider()

        if st.button("＋  Neuer Eintrag", use_container_width=True, type="primary"):
            eintrag_dialog(conn, u_id)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button("⎋  Abmelden", use_container_width=True):
            for key in ['logged_in', 'user_id', 'username', 'vorname', 'conn']:
                st.session_state.pop(key, None)
            st.rerun()

        st.markdown("""
        <div style="position:absolute;bottom:1rem;left:0;right:0;text-align:center;">
            <span style="font-size:0.65rem;color:#1E293B;letter-spacing:0.07em;font-family:'DM Sans',sans-serif;">
                FINANZ·MASTER v1.5
            </span>
        </div>""", unsafe_allow_html=True)

    # ── PAGES ──
    if page == "📊 Dashboard":
        dashboard_page(conn, u_id)
    elif page == "📝 Einträge":
        entries_page(conn, u_id)
    elif page == "⚙️ Verwaltung":
        settings_page(conn, u_id)
