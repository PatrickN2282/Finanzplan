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
# PRECISION FINANCE – Unified High Contrast Design (v2.0 Stable)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
    --c-primary:    #1B3A6B; 
    --c-bg:         #ffffff; 
    --c-surface:    #FFFFFF; 
    --c-text:       #1E293B; 
    --c-list-text:  #2D3748; 

    --value-pos:    #2BB34F; 
    --value-neg:    #F44336; 
    --value-warn:   #FF9800; 
    --value-neon:   #39D353; 

    --border:       rgba(27, 58, 107, 0.08);
    --r: 12px; 
    --r-s: 8px;
}

/* ─────────────────────────────────────────────
   BASE TYPOGRAPHY
───────────────────────────────────────────── */
html, body {
    font-family: 'Outfit', sans-serif !important;
    color: var(--c-text);
}

[data-testid="stAppViewContainer"] {
    background: var(--c-bg);
}

/* Markdown & normale Texte */
.stMarkdown p,
.stMarkdown span,
label,
small,
[data-testid="stMetricLabel"],
[data-testid="stWidgetLabel"] {
    color: var(--c-list-text);
}

/* ─────────────────────────────────────────────
   SVG FIX FÜR DIAGRAMME (WICHTIG!)
───────────────────────────────────────────── */
svg text {
    fill: var(--c-list-text) !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ─────────────────────────────────────────────
   EXPANDER
───────────────────────────────────────────── */
.stExpander {
    border: 1px solid var(--border);
    border-radius: var(--r);
    background: var(--c-surface);
    margin-bottom: 1rem;
}

.stExpander summary {
    background-color: #2D3748;
    color: white;
    border-radius: var(--r-s);
}

.stExpander summary:hover {
    background-color: var(--c-primary);
}

.stExpander svg {
    fill: white !important;
}

/* ─────────────────────────────────────────────
   METRIKEN
───────────────────────────────────────────── */
[data-testid="metric-container"] { 
    background: var(--c-surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
}

[data-testid="stMetricValue"] { 
    color: var(--c-text);
    font-weight: 800;
}

/* ─────────────────────────────────────────────
   SIDEBAR
───────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--c-primary);
}

[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.9);
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--value-neon);
    color: #0A1F0D;
    font-weight: 700;
}

/* ─────────────────────────────────────────────
   WERTFARBEN (FÜR TABELLEN & LISTEN)
   → NICHT global überschrieben!
───────────────────────────────────────────── */
.pos { color: var(--value-pos) !important; font-weight:600; }
.neg { color: var(--value-neg) !important; font-weight:600; }
.warn { color: var(--value-warn) !important; font-weight:600; }

/* ─────────────────────────────────────────────
   MODAL / DIALOG – DARKMODE-PROOF
   Erzwingt Light-Theme unabhängig vom OS
───────────────────────────────────────────── */

/* Backdrop */
[data-testid="stModal"] > div:first-child {
    background: rgba(10, 20, 50, 0.55) !important;
    backdrop-filter: blur(4px);
}

/* Dialog-Container */
[data-testid="stModal"] [role="dialog"],
div[class*="dialog"],
div[class*="Modal"] {
    background: #FFFFFF !important;
    color: #1E293B !important;
    border: 1px solid rgba(27,58,107,0.12) !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.18) !important;
}

/* Alle Texte im Dialog */
[data-testid="stModal"] *,
[data-testid="stModal"] p,
[data-testid="stModal"] label,
[data-testid="stModal"] span:not(.pos):not(.neg):not(.warn),
[data-testid="stModal"] div {
    color: #1E293B !important;
}

/* Dialog-Titel */
[data-testid="stModal"] h1,
[data-testid="stModal"] h2,
[data-testid="stModal"] h3 {
    color: #1A1F2E !important;
    font-weight: 700 !important;
}

/* ─────────────────────────────────────────────
   INPUTS & TEXTFELDER (überall, nicht nur Dialog)
───────────────────────────────────────────── */
input[type="text"],
input[type="number"],
input[type="email"],
input[type="password"],
textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background: #F8F9FA !important;
    color: #1E293B !important;
    border: 1px solid rgba(27,58,107,0.2) !important;
    border-radius: 8px !important;
}

input[type="text"]:focus,
input[type="number"]:focus,
textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #1B3A6B !important;
    box-shadow: 0 0 0 3px rgba(27,58,107,0.12) !important;
    background: #FFFFFF !important;
}

/* ─────────────────────────────────────────────
   DROPDOWNS / SELECTBOX
───────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #F8F9FA !important;
    color: #1E293B !important;
    border: 1px solid rgba(27,58,107,0.2) !important;
    border-radius: 8px !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
    border-color: #1B3A6B !important;
    box-shadow: 0 0 0 3px rgba(27,58,107,0.12) !important;
}

/* Dropdown-Optionsliste */
[data-baseweb="popover"],
[data-baseweb="menu"],
ul[role="listbox"],
[role="listbox"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(27,58,107,0.15) !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.12) !important;
}

/* Einzelne Dropdown-Option */
li[role="option"],
[data-baseweb="menu"] li,
[role="option"] {
    background: #FFFFFF !important;
    color: #1E293B !important;
}

/* Hover-State der Option */
li[role="option"]:hover,
[role="option"]:hover,
[aria-selected="true"][role="option"] {
    background: rgba(27,58,107,0.08) !important;
    color: #1B3A6B !important;
}

/* Ausgewählte Option */
[aria-selected="true"] {
    background: rgba(27,58,107,0.1) !important;
    font-weight: 600 !important;
}

/* Selectbox-Text-Farbe */
[data-testid="stSelectbox"] span,
[data-testid="stSelectbox"] div[class*="ValueContainer"] span {
    color: #1E293B !important;
}

/* ─────────────────────────────────────────────
   SEGMENTED CONTROL (Art-Auswahl im Dialog)
───────────────────────────────────────────── */
[data-testid="stSegmentedControl"] {
    background: rgba(27,58,107,0.06) !important;
    border-radius: 10px !important;
    padding: 3px !important;
}

[data-testid="stSegmentedControl"] button {
    background: transparent !important;
    color: #4A5270 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    border: none !important;
}

[data-testid="stSegmentedControl"] button[aria-checked="true"],
[data-testid="stSegmentedControl"] button[data-active="true"] {
    background: #1B3A6B !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(27,58,107,0.25) !important;
}

/* ─────────────────────────────────────────────
   DATE INPUT
───────────────────────────────────────────── */
[data-testid="stDateInput"] > div {
    background: #F8F9FA !important;
    border: 1px solid rgba(27,58,107,0.2) !important;
    border-radius: 8px !important;
}

/* ─────────────────────────────────────────────
   FORM / BUTTON
───────────────────────────────────────────── */
[data-testid="stModal"] [data-testid="stForm"] {
    background: transparent !important;
}

/* Primär-Button im Dialog */
[data-testid="stModal"] .stButton > button[kind="primary"],
[data-testid="stModal"] button[data-testid="stFormSubmitButton"][kind="primary"] {
    background: #1B3A6B !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}

[data-testid="stModal"] .stButton > button[kind="primary"]:hover {
    background: #142d54 !important;
    box-shadow: 0 4px 14px rgba(27,58,107,0.35) !important;
}

/* Sekundär-Button (Abbrechen) */
[data-testid="stModal"] .stButton > button:not([kind="primary"]) {
    background: #F1F3F7 !important;
    color: #4A5270 !important;
    border: 1px solid rgba(27,58,107,0.15) !important;
    border-radius: 8px !important;
}

/* ─────────────────────────────────────────────
   INFO / WARNING BOXES IM DIALOG
───────────────────────────────────────────── */
[data-testid="stModal"] [data-testid="stAlert"],
[data-testid="stModal"] .stAlert {
    border-radius: 8px !important;
}

[data-testid="stModal"] [data-testid="stAlert"][data-type="info"] {
    background: rgba(27,58,107,0.07) !important;
    border-left: 3px solid #1B3A6B !important;
    color: #1A1F2E !important;
}

/* ─────────────────────────────────────────────
   DIVIDER IM DIALOG
───────────────────────────────────────────── */
[data-testid="stModal"] hr {
    border-color: rgba(27,58,107,0.1) !important;
}

/* ─────────────────────────────────────────────
   LABEL-TEXTE (überall, nicht nur Dialog)
───────────────────────────────────────────── */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: #4A5270 !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ROUTING
# ─────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    auth_page()
else:
    conn = get_conn()
    u_id = st.session_state.user_id
    username = st.session_state.get('username', 'User')
    display_name = st.session_state.get('vorname', username)

    with st.sidebar:
        initials = (display_name[:2]).upper()
        st.markdown(f"""
        <div style="padding:1.4rem 0.5rem 1rem;
                    text-align:center;
                    border-bottom:1px solid rgba(255,255,255,0.1);
                    margin-bottom:0.8rem;">
            <div style="width:48px;height:48px;border-radius:12px;
                        background:rgba(255,152,0,0.15);
                        border:2px solid var(--value-warn);
                        display:flex;align-items:center;
                        justify-content:center;
                        margin:0 auto 0.7rem;
                        font-weight:800;
                        color:var(--value-warn);">
                {initials}
            </div>
            <div style="font-weight:700;color:white;">
                {display_name}
            </div>
            <div style="font-size:0.72rem;
                        color:rgba(255,255,255,0.35);">
                @{username}
            </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📝 Einträge", "⚙️ Verwaltung"],
            label_visibility="collapsed"
        )

        st.divider()

        if st.button("＋ Neuer Eintrag", use_container_width=True, type="primary"):
            eintrag_dialog(conn, u_id)

        if st.button("↩ Abmelden", use_container_width=True):
            for key in ['logged_in', 'user_id', 'username', 'vorname']:
                st.session_state.pop(key, None)
            st.rerun()

    if page == "📊 Dashboard":
        dashboard_page(conn, u_id)
    elif page == "📝 Einträge":
        entries_page(conn, u_id)
    elif page == "⚙️ Verwaltung":
        settings_page(conn, u_id)
