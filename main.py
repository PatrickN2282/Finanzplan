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
# PRECISION FINANCE – Native Adaptive CSS (v1.3.3)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* * DYNAMISCHE FARBSTEUERUNG:
 * :root nutzt die config.toml Werte (optimiert für Kontrast).
 * @media erkennt den Browser-Darkmode automatisch.
 */
:root {
    /* ── Basis-Farben (Light Mode aus config.toml) ── */
    --c-primary:  var(--primary-color, #1B3A6B);
    --c-bg:       var(--background-color, #87888C); 
    --c-surface:  var(--secondary-background-color, #F4F5F9);
    
    /* Text auf fast Schwarz für maximalen Kontrast auf dem grauen Hintergrund */
    --c-text:     #0F172A; 

    /* Semantische Wertfarben */
    --value-pos:   #1C9E3A;
    --value-neg:   #D63B3B;
    --value-warn:  #F07800;
    --value-neon:  #39D353;

    /* Mathematische Ableitungen */
    --c-surface2:  color-mix(in srgb, var(--c-surface) 80%, var(--c-bg) 20%);
    --c-dialog:    color-mix(in srgb, var(--c-surface) 95%, var(--c-bg) 5%);
    --border:      rgba(0, 0, 0, 0.12);
    --border-s:    rgba(0, 0, 0, 0.25);
    --text-2:      rgba(15, 23, 42, 0.8);
    --text-3:      rgba(15, 23, 42, 0.55);
    --shadow:      rgba(0, 0, 0, 0.08);
    --primary-dim:  color-mix(in srgb, var(--c-primary) 10%, transparent);
    --primary-dim2: color-mix(in srgb, var(--c-primary) 5%, transparent);

    --r:   12px;
    --r-s:  8px;
}

/* ── AUTOMATISCHER DARK MODE OVERRIDE ── */
@media (prefers-color-scheme: dark) {
    :root {
        --c-primary:  #3A6FBF; 
        --c-bg:       #1A1C24; 
        --c-surface:  #252836; 
        --c-text:     #E2E8F0;
        
        --shadow:      rgba(0,0,0,0.4);
        --border:      rgba(255,255,255,0.08);
        --border-s:    rgba(255,255,255,0.15);
        --text-2:      rgba(226, 232, 240, 0.75);
        --text-3:      rgba(226, 232, 240, 0.45);
        --primary-dim: rgba(58, 111, 191, 0.18);
    }
}

/* BASE */
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: var(--c-bg) !important; }
[data-testid="stHeader"] { background: transparent !important; }
.main .block-container { padding: 1.8rem 2.8rem 3rem !important; max-width: 1500px !important; }

/* SIDEBAR */
[data-testid="stSidebar"] { background: var(--c-primary) !important; border-right: none !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.13) !important;
    border-radius: var(--r-s) !important;
    color: rgba(255,255,255,0.75) !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.13) !important;
    color: white !important;
    transform: translateX(2px);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--value-neon) !important;
    border-color: var(--value-neon) !important;
    color: #0A1F0D !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(57,211,83,0.35);
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(255,255,255,0.13) !important;
    color: white !important;
    font-weight: 600 !important;
}

/* METRIKEN */
[data-testid="metric-container"] {
    background: var(--c-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    box-shadow: 0 2px 6px var(--shadow) !important;
    transition: transform 0.2s ease !important;
}
[data-testid="metric-container"]:hover { transform: translateY(-2px); }
[data-testid="stMetricLabel"] { color: var(--text-3) !important; text-transform: uppercase !important; font-size: 0.72rem !important; }
[data-testid="stMetricValue"] { color: var(--c-text) !important; font-weight: 700 !important; }

/* DATAFRAMES / TABELLEN (Fix für Lesbarkeit) */
[data-testid="stDataFrame"] { 
    border: 1px solid var(--border) !important; 
    border-radius: var(--r) !important; 
    background-color: var(--c-surface) !important;
}
[data-testid="stDataFrame"] * { color: var(--c-text) !important; }
[data-testid="stDataFrame"] thead th { 
    background: var(--c-surface2) !important; 
    font-weight: 700 !important; 
}

/* INPUTS & MODALS */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
    background: var(--c-surface) !important;
    border: 1px solid var(--border-s) !important;
    color: var(--c-text) !important;
}
[data-testid="stModal"] > div {
    background: var(--c-dialog) !important;
    border-radius: 16px !important;
}

/* TYPO & DIVIDER */
h1, h2, h3 { color: var(--c-text) !important; font-weight: 700 !important; }
hr { background: var(--border) !important; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: var(--border-s); border-radius: 3px; }
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
    username = st.session_state.get('username', 'User')
    display_name = st.session_state.get('vorname', username)

    with st.sidebar:
        initials = (display_name[:2]).upper()
        st.markdown(f"""
        <div style="padding:1.4rem 0.5rem 1rem;text-align:center; border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:0.8rem;">
            <div style="width:48px;height:48px;border-radius:12px;background:rgba(57,211,83,0.2);border:2px solid rgba(57,211,83,0.5);display:flex;align-items:center;justify-content:center;margin:0 auto 0.7rem;font-family:'Outfit',sans-serif;font-weight:800;color:#39D353;">{initials}</div>
            <div style="font-weight:700;color:white;">{display_name}</div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.35);">@{username}</div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio("Navigation", ["📊 Dashboard", "📝 Einträge", "⚙️ Verwaltung"], label_visibility="collapsed")
        
        st.divider()

        if st.button("＋ Neuer Eintrag", width='stretch', type="primary"):
            eintrag_dialog(conn, u_id)

        if st.button("↩ Abmelden", width='stretch'):
            for key in ['logged_in', 'user_id', 'username', 'vorname']:
                st.session_state.pop(key, None)
            st.rerun()

        st.markdown("""
        <div style="position:absolute;bottom:1rem;left:0;right:0;text-align:center;">
            <span style="font-size:0.65rem;color:rgba(255,255,255,0.15);letter-spacing:0.08em;">
                FINANZ-MASTER v1.3.3
            </span>
        </div>""", unsafe_allow_html=True)

    # Routing
    if page == "📊 Dashboard":
        dashboard_page(conn, u_id)
    elif page == "📝 Einträge":
        entries_page(conn, u_id)
    elif page == "⚙️ Verwaltung":
        settings_page(conn, u_id)
