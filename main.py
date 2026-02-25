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
    --c-bg:         #F8F9FA; 
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
