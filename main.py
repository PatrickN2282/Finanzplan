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
# FINANCE MASTER – Marine Neon Stable UI (Dialog + Dropdown Fix)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* ─────────────────────────────────────────────
   COLOR SYSTEM
───────────────────────────────────────────── */
:root {
    --marine: #1B3A6B;
    --neon: #39D353;
    --orange: #F07800;
    --bg: #F4F6FA;
    --surface: #FFFFFF;
    --text: #1A1F2E;
    --text-soft: #6B7280;
    --border: rgba(27,58,107,0.12);

    --value-pos: #2BB34F;
    --value-neg: #F44336;
    --value-warn: #FF9800;
}

/* ─────────────────────────────────────────────
   GLOBAL BASE
───────────────────────────────────────────── */
html, body {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}

/* Text Elemente */
.stMarkdown p,
.stMarkdown span,
label,
small,
[data-testid="stMetricLabel"],
[data-testid="stWidgetLabel"] {
    color: var(--text-soft) !important;
}

/* ─────────────────────────────────────────────
   SIDEBAR
───────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--marine) !important;
}

[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.92) !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--neon) !important;
    color: #0A1F0D !important;
    font-weight: 700 !important;
    border: none !important;
}

/* ─────────────────────────────────────────────
   METRICS
───────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

[data-testid="stMetricValue"] {
    font-weight: 800 !important;
    color: var(--text) !important;
}

/* ─────────────────────────────────────────────
   EXPANDER
───────────────────────────────────────────── */
.stExpander {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

.stExpander summary {
    background: var(--marine) !important;
    color: white !important;
}

.stExpander svg {
    fill: white !important;
}

/* ─────────────────────────────────────────────
   SVG FIX (Charts)
───────────────────────────────────────────── */
svg text {
    fill: #4A5270 !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ─────────────────────────────────────────────
   DIALOG FIX (für @st.dialog)
───────────────────────────────────────────── */

/* Overlay */
div[data-testid="stDialogOverlay"] {
    background: rgba(0,0,0,0.35) !important;
}

/* Dialog Container */
div[data-testid="stDialog"] {
    background: var(--surface) !important;
    border-radius: 16px !important;
    border: 1px solid var(--border) !important;
}

/* Dialog Content */
div[data-testid="stDialog"] * {
    color: var(--text) !important;
}

/* ─────────────────────────────────────────────
   SELECTBOX / DROPDOWN FIX (BaseWeb Portal)
───────────────────────────────────────────── */

/* Select Feld */
div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* Dropdown Popover */
div[data-baseweb="popover"] {
    background: var(--surface) !important;
}

/* Listbox */
div[role="listbox"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
}

/* Optionen */
div[role="option"] {
    background: var(--surface) !important;
    color: var(--text) !important;
}

/* Hover */
div[role="option"]:hover {
    background: var(--bg) !important;
}

/* Selected Option */
div[aria-selected="true"] {
    background: var(--marine) !important;
    color: white !important;
}

/* ─────────────────────────────────────────────
   VALUE COLORS (NICHT ÜBERSCHREIBEN!)
───────────────────────────────────────────── */
.pos { color: var(--value-pos) !important; font-weight:600; }
.neg { color: var(--value-neg) !important; font-weight:600; }
.warn { color: var(--value-warn) !important; font-weight:600; }

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
                        background:rgba(240,120,0,0.15);
                        border:2px solid var(--orange);
                        display:flex;align-items:center;
                        justify-content:center;
                        margin:0 auto 0.7rem;
                        font-weight:800;
                        color:var(--orange);">
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
