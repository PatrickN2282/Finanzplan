import streamlit as st
from db import get_conn
from auth import auth_page
from ui import eintrag_dialog, dashboard_page, entries_page, settings_page

st.set_page_config(
    page_title="Finanz-Master",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# PRECISION FINANCE – Dual Light/Dark CSS
# Palette:
#   Marine  #1B3A6B   → Navigation, Struktur, Links
#   Neongrün #39D353  → Positive Werte, CTAs, Einnahmen
#   Orange   #F07800  → Warnungen, Abos, Highlights
#   Hellgrau #F4F5F7  → Light-BG
#   Dunkelgrau #1A1F2E → Dark-BG / Light-Text
#   Rot      #D63B3B  → Negative Werte, Ausgaben
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* ══════════════════════════════════════════
   TOKENS – Precision Finance
   Hintergrund:  #ECEEF3  (seichtes Blaugrau)
   Surface:      #F6F7FA  (helles Grau, kein Weiß)
   Surface2:     #ECEEF3  (Tabellen-Header)
   Dialog-BG:    #F0F2F7  (mittleres Grau, kein Weiß/Schwarz)
   Text-Input-BG:#F6F7FA  mit dunklem Text
   ══════════════════════════════════════════ */
:root {
    /* Akzentfarben */
    --marine:      #1B3A6B;
    --marine-l:    #254E94;
    --marine-dim:  rgba(27,58,107,0.09);
    --marine-dim2: rgba(27,58,107,0.05);
    --neon:        #39D353;
    --orange:      #F07800;
    --red:         #D63B3B;
    --red-dim:     rgba(214,59,59,0.08);
    --green:       #1C9E3A;

    /* Hintergründe – seichtes Blaugrau-Spektrum */
    --bg:          #E8EBF2;   /* Seichtes Grau-Blau für App-BG */
    --surface:     #F4F5F9;   /* Karten, Eingaben – etwas heller */
    --surface2:    #DFE2EC;   /* Tabellen-Header, dunkleres Segment */
    --dialog-bg:   #EDF0F7;   /* Popup-Hintergrund – mittleres Grau */

    /* Ränder & Schatten */
    --border:      rgba(27,58,107,0.11);
    --border-s:    rgba(27,58,107,0.2);

    /* Text */
    --text:        #1A1F2E;
    --text-2:      #4A5270;
    --text-3:      #7A84A0;

    --shadow:      rgba(27,58,107,0.07);
    --r:           12px;
    --r-s:         8px;
}

/* ── BASE ─────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
}
.main .block-container {
    padding: 1.8rem 2.8rem 3rem !important;
    max-width: 1500px !important;
}

/* ── SIDEBAR ──────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--marine) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.13) !important;
    border-radius: var(--r-s) !important;
    color: rgba(255,255,255,0.75) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.13) !important;
    border-color: rgba(255,255,255,0.24) !important;
    color: white !important;
    transform: translateX(2px);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--neon) !important;
    border-color: var(--neon) !important;
    color: #0A1F0D !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(57,211,83,0.35);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: #47E063 !important;
    box-shadow: 0 6px 20px rgba(57,211,83,0.45);
    transform: translateX(2px) translateY(-1px);
}
[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio label {
    border-radius: var(--r-s) !important;
    padding: 0.55rem 0.85rem !important;
    color: rgba(255,255,255,0.6) !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    transition: all 0.18s ease !important;
    border: 1px solid transparent !important;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(255,255,255,0.13) !important;
    border-color: rgba(255,255,255,0.22) !important;
    color: white !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stRadio label:hover:not(:has(input:checked)) {
    background: rgba(255,255,255,0.07) !important;
    color: rgba(255,255,255,0.85) !important;
}
[data-testid="stSidebar"] [data-testid="stRadioLabel"] { display: none !important; }
[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.2) !important;
}

/* Sidebar-Toggle sichtbar auf Marine-BG */
[data-testid="stSidebarCollapseButton"] button,
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] {
    background: rgba(255,255,255,0.18) !important;
    border: 1px solid rgba(255,255,255,0.32) !important;
    border-radius: 8px !important;
    color: white !important;
}
[data-testid="stSidebarCollapseButton"] button svg,
button[aria-label="Close sidebar"] svg,
button[aria-label="Open sidebar"] svg {
    fill: white !important; stroke: white !important; opacity: 1 !important;
}
[data-testid="collapsedControl"] {
    background: var(--marine) !important;
    border-radius: 0 8px 8px 0 !important;
    border: 1px solid rgba(27,58,107,0.2) !important;
    box-shadow: 2px 0 8px rgba(27,58,107,0.15) !important;
}
[data-testid="collapsedControl"] button svg {
    fill: white !important; stroke: white !important;
}

/* ── METRIKEN ─────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    padding: 1.1rem 1.3rem !important;
    box-shadow: 0 2px 6px var(--shadow) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::after {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0; width: 3px;
    background: var(--marine);
    border-radius: 3px 0 0 3px;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 18px var(--shadow) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-3) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: var(--text) !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

/* ── DATAFRAMES ───────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important;
    box-shadow: 0 1px 4px var(--shadow) !important;
}
/* Header: etwas dunkler als surface, kein Schwarz */
[data-testid="stDataFrame"] thead th {
    background: var(--surface2) !important;
    color: var(--text-2) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-s) !important;
    padding: 0.65rem 1rem !important;
}
/* Zeilen: surface (helles Grau), kein Weiß/Schwarz */
[data-testid="stDataFrame"] tbody tr {
    border-bottom: 1px solid var(--border) !important;
    transition: background 0.12s !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(odd) td {
    background: var(--surface) !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background: #ECF0F6 !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: rgba(27,58,107,0.07) !important;
}
[data-testid="stDataFrame"] tbody td {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.875rem !important;
    color: var(--text) !important;
    padding: 0.55rem 1rem !important;
}

/* ── EXPANDER ─────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    box-shadow: 0 1px 4px var(--shadow);
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stExpander"]:hover {
    border-color: var(--border-s) !important;
    box-shadow: 0 3px 10px var(--shadow) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    font-size: 0.9rem !important;
    padding: 0.85rem 1.1rem !important;
}

/* ── TABS ─────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface2) !important;
    border-radius: var(--r-s) !important;
    padding: 3px !important;
    gap: 0 !important;
    border: 1px solid var(--border) !important;
    width: fit-content;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    color: var(--text-3) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.4rem 1.1rem !important;
    font-size: 0.87rem !important;
    transition: all 0.18s !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--marine) !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 4px var(--shadow) !important;
    border: 1px solid var(--border) !important;
}

/* ── BUTTONS ──────────────────────────────── */
.stButton > button {
    font-family: 'Outfit', sans-serif !important;
    border-radius: var(--r-s) !important;
    font-weight: 500 !important;
    font-size: 0.87rem !important;
    transition: all 0.18s ease !important;
    border: 1px solid var(--border-s) !important;
    background: var(--surface) !important;
    color: var(--text-2) !important;
    box-shadow: 0 1px 3px var(--shadow) !important;
}
.stButton > button[kind="primary"] {
    background: var(--marine) !important;
    border-color: var(--marine) !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 3px 10px rgba(27,58,107,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--marine-l) !important;
    box-shadow: 0 5px 16px rgba(27,58,107,0.4) !important;
    transform: translateY(-1px);
}
.stButton > button:not([kind="primary"]):hover {
    border-color: var(--marine) !important;
    color: var(--marine) !important;
    background: var(--marine-dim) !important;
}

/* ── SEGMENTED CONTROL ────────────────────── */
[data-testid="stSegmentedControl"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-s) !important;
    padding: 3px !important;
}
[data-testid="stSegmentedControl"] button {
    border-radius: 6px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--text-3) !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.18s !important;
}
[data-testid="stSegmentedControl"] button[aria-checked="true"] {
    background: var(--surface) !important;
    color: var(--marine) !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 4px var(--shadow) !important;
    border: 1px solid var(--border) !important;
}

/* ── INPUTS & SELECTBOX ───────────────────── */
/* Hintergrund surface (helles Grau), dunkler Text */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background: var(--surface) !important;
    border: 1px solid var(--border-s) !important;
    border-radius: var(--r-s) !important;
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.18s, box-shadow 0.18s !important;
    box-shadow: inset 0 1px 2px rgba(27,58,107,0.06) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--marine) !important;
    box-shadow: 0 0 0 3px var(--marine-dim), inset 0 1px 2px rgba(27,58,107,0.06) !important;
    outline: none !important;
}
/* Placeholder sichtbar auf hellem Hintergrund */
[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder {
    color: var(--text-3) !important;
    opacity: 1 !important;
}
/* "Drücke Enter zum bestätigen" und ähnliche Helper-Texte */
[data-testid="stTextInput"] small,
[data-testid="stTextInput"] + div small,
[data-testid="InputInstructions"],
[class*="InputInstructions"],
[data-testid="stTextInput"] [data-testid="InputInstructions"],
div[class*="instructionsContainer"] {
    color: var(--text-3) !important;
    background: transparent !important;
    opacity: 1 !important;
}
/* Number-Input stepper buttons */
[data-testid="stNumberInput"] button {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text-2) !important;
}
/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border-s) !important;
    border-radius: var(--r-s) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
    color: var(--text) !important;
}
[data-testid="stSelectbox"] li {
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
}
/* Date input */
[data-testid="stDateInput"] input {
    background: var(--surface) !important;
    color: var(--text) !important;
}

/* ── MODAL / DIALOG ───────────────────────── */
/* Mittleres Blaugrau – kein Weiß, kein Schwarz */
[data-testid="stModal"] > div {
    background: var(--dialog-bg) !important;
    border: 1px solid var(--border-s) !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 50px rgba(27,58,107,0.18), 0 4px 16px rgba(27,58,107,0.1) !important;
}
/* Inputs innerhalb des Dialogs auch auf dialog-bg abstimmen */
[data-testid="stModal"] [data-testid="stTextInput"] input,
[data-testid="stModal"] [data-testid="stNumberInput"] input,
[data-testid="stModal"] [data-testid="stDateInput"] input,
[data-testid="stModal"] [data-testid="stSelectbox"] > div > div {
    background: var(--surface) !important;
    color: var(--text) !important;
}
[data-testid="stModal"] [data-testid="stTextInput"] input::placeholder,
[data-testid="stModal"] [data-testid="stNumberInput"] input::placeholder {
    color: var(--text-3) !important;
    opacity: 1 !important;
}

/* ── ALERTS ───────────────────────────────── */
[data-testid="stInfo"] {
    background: rgba(27,58,107,0.07) !important;
    border: 1px solid rgba(27,58,107,0.18) !important;
    border-left: 3px solid var(--marine) !important;
    border-radius: var(--r-s) !important;
    color: var(--marine) !important;
}
[data-testid="stSuccess"] {
    background: rgba(57,211,83,0.08) !important;
    border: 1px solid rgba(57,211,83,0.22) !important;
    border-left: 3px solid var(--neon) !important;
    border-radius: var(--r-s) !important;
}
[data-testid="stError"] {
    background: var(--red-dim) !important;
    border: 1px solid rgba(214,59,59,0.2) !important;
    border-left: 3px solid var(--red) !important;
    border-radius: var(--r-s) !important;
}
[data-testid="stWarning"] {
    background: rgba(240,120,0,0.07) !important;
    border: 1px solid rgba(240,120,0,0.2) !important;
    border-left: 3px solid var(--orange) !important;
    border-radius: var(--r-s) !important;
}

/* ── PLOTLY ───────────────────────────────── */
[data-testid="stPlotlyChart"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    box-shadow: 0 1px 4px var(--shadow) !important;
    padding: 0.25rem;
}

/* ── TYPO ─────────────────────────────────── */
h1 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: var(--text) !important;
}
h2 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    font-size: 1.15rem !important;
    letter-spacing: -0.015em !important;
}
h3 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-2) !important;
    font-size: 0.95rem !important;
}

/* ── DIVIDER ──────────────────────────────── */
hr {
    border: none !important;
    height: 1px !important;
    background: var(--border) !important;
    margin: 1rem 0 !important;
}

/* ── SCROLLBAR ────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-s); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--marine); }

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
    u_id         = st.session_state.user_id
    username     = st.session_state.get('username', 'User')
    vorname      = st.session_state.get('vorname', '')
    display_name = vorname if vorname else username

    with st.sidebar:
        # User-Badge
        initials = (display_name[:2]).upper()
        st.markdown(f"""
        <div style="padding:1.4rem 0.5rem 1rem;text-align:center;
                    border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:0.8rem;">
            <div style="
                width:48px;height:48px;border-radius:12px;
                background:rgba(57,211,83,0.2);
                border:2px solid rgba(57,211,83,0.5);
                display:flex;align-items:center;justify-content:center;
                margin:0 auto 0.7rem;
                font-family:'Outfit',sans-serif;font-weight:800;font-size:1rem;
                color:#39D353;letter-spacing:-0.02em;
            ">{initials}</div>
            <div style="font-family:'Outfit',sans-serif;font-weight:700;font-size:0.95rem;
                        color:rgba(255,255,255,0.95);letter-spacing:-0.01em;">{display_name}</div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.35);margin-top:1px;">
                @{username}
            </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📝 Einträge", "⚙️ Verwaltung"],
            label_visibility="collapsed"
        )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.divider()

        if st.button("＋  Neuer Eintrag", width='stretch', type="primary"):
            eintrag_dialog(conn, u_id)

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

        # Theme Toggle
        dark = st.session_state.dark_mode
        toggle_label = "☀️  Hell-Modus" if dark else "🌙  Dunkel-Modus"
        if st.button(toggle_label, width='stretch'):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

        if st.button("↩  Abmelden", width='stretch'):
            for key in ['logged_in', 'user_id', 'username', 'vorname', 'conn']:
                st.session_state.pop(key, None)
            st.rerun()

        st.markdown("""
        <div style="position:absolute;bottom:1rem;left:0;right:0;text-align:center;">
            <span style="font-size:0.65rem;color:rgba(255,255,255,0.15);
                         font-family:'Outfit',sans-serif;letter-spacing:0.08em;">
                FINANZ-MASTER  v1.5
            </span>
        </div>""", unsafe_allow_html=True)

    if page == "📊 Dashboard":
        dashboard_page(conn, u_id)
    elif page == "📝 Einträge":
        entries_page(conn, u_id)
    elif page == "⚙️ Verwaltung":
        settings_page(conn, u_id)
