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
# PRECISION FINANCE – Native Adaptive CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* * DYNAMISCHE FARBSTEUERUNG:
 * Wir nutzen die von Streamlit injizierten Variablen aus der config.toml.
 * Falls diese nicht vorhanden sind (Fallback), nutzen wir deine Originalfarben.
 */
:root {
    --c-primary:  var(--primary-color, #1B3A6B);
    --c-bg:       var(--background-color, #E8EBF2);
    --c-surface:  var(--secondary-background-color, #F4F5F9);
    --c-text:     var(--text-color, #1A1F2E);

    /* Semantische Wertfarben */
    --value-pos:   #1C9E3A;
    --value-neg:   #D63B3B;
    --value-warn:  #F07800;
    --value-neon:  #39D353;

    /* Deine originalen mathematischen Ableitungen */
    --c-surface2:  color-mix(in srgb, var(--c-surface) 80%, var(--c-bg) 20%);
    --c-dialog:    color-mix(in srgb, var(--c-surface) 90%, var(--c-bg) 10%);
    --border:      color-mix(in srgb, var(--c-primary) 11%, transparent);
    --border-s:    color-mix(in srgb, var(--c-primary) 22%, transparent);
    --text-2:      color-mix(in srgb, var(--c-text) 70%, transparent);
    --text-3:      color-mix(in srgb, var(--c-text) 40%, transparent);
    --shadow:      color-mix(in srgb, var(--c-primary) 8%, transparent);
    --primary-dim:  color-mix(in srgb, var(--c-primary) 9%, transparent);
    --primary-dim2: color-mix(in srgb, var(--c-primary) 5%, transparent);

    --r:   12px;
    --r-s:  8px;
}

/* BASE */
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: var(--c-bg) !important; }
[data-testid="stHeader"] { background: transparent !important; }
.main .block-container { padding: 1.8rem 2.8rem 3rem !important; max-width: 1500px !important; }

/* SIDEBAR - Vollständiges Original-Styling */
[data-testid="stSidebar"] { background: var(--c-primary) !important; border-right: none !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
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
    background: var(--value-neon) !important;
    border-color: var(--value-neon) !important;
    color: #0A1F0D !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(57,211,83,0.35);
}
[data-testid="stSidebar"] .stRadio label {
    border-radius: var(--r-s) !important;
    padding: 0.55rem 0.85rem !important;
    color: rgba(255,255,255,0.6) !important;
    transition: all 0.18s ease !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(255,255,255,0.13) !important;
    color: white !important;
    font-weight: 600 !important;
}

/* METRIKEN - Vollständiges Original-Styling */
[data-testid="metric-container"] {
    background: var(--c-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    padding: 1.1rem 1.3rem !important;
    box-shadow: 0 2px 6px var(--shadow) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="metric-container"]:hover { transform: translateY(-2px); box-shadow: 0 5px 18px var(--shadow) !important; }
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; font-weight: 600 !important; text-transform: uppercase !important; color: var(--text-3) !important; }
[data-testid="stMetricValue"] { font-size: 1.55rem !important; font-weight: 700 !important; color: var(--c-text) !important; }

/* DATAFRAMES */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: var(--r) !important; overflow: hidden !important; }
[data-testid="stDataFrame"] thead th { background: var(--c-surface2) !important; color: var(--text-2) !important; font-size: 0.7rem !important; font-weight: 600 !important; }
[data-testid="stDataFrame"] tbody tr:hover td { background: var(--primary-dim) !important; }

/* TABS & SEGMENTED CONTROL */
.stTabs [data-baseweb="tab-list"], [data-testid="stSegmentedControl"] {
    background: var(--c-surface2) !important;
    border-radius: var(--r-s) !important;
    padding: 3px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [aria-selected="true"], [data-testid="stSegmentedControl"] button[aria-checked="true"] {
    background: var(--c-surface) !important;
    color: var(--c-primary) !important;
    font-weight: 700 !important;
}

/* INPUTS */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
    background: var(--c-surface) !important;
    border: 1px solid var(--border-s) !important;
    border-radius: var(--r-s) !important;
    color: var(--c-text) !important;
}
[data-testid="stTextInput"] input:focus { border-color: var(--c-primary) !important; box-shadow: 0 0 0 3px var(--primary-dim) !important; }

/* MODAL */
[data-testid="stModal"] > div {
    background: var(--c-dialog) !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 50px var(--shadow) !important;
}

/* ALERTS */
[data-testid="stSuccess"] { background: rgba(28,158,58,0.07) !important; border-left: 3px solid var(--value-pos) !important; border-radius: var(--r-s) !important; }
[data-testid="stError"] { background: rgba(214,59,59,0.07) !important; border-left: 3px solid var(--value-neg) !important; border-radius: var(--r-s) !important; }

/* TYPO & DIVIDER */
h1 { font-weight: 800 !important; color: var(--c-text) !important; }
h2 { font-weight: 700 !important; color: var(--c-text) !important; }
hr { border: none !important; height: 1px !important; background: var(--border) !important; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-thumb { background: var(--border-s); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ROUTING (OHNE TOGGLE LOGIK) ---
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

    # PAGE ROUTING
    if page == "📊 Dashboard":
        dashboard_page(conn, u_id)
    elif page == "📝 Einträge":
        entries_page(conn, u_id)
    elif page == "⚙️ Verwaltung":
        settings_page(conn, u_id)
