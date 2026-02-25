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
# PRECISION FINANCE – Fixed Light Design (v1.3.3)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* FIXIERTES DESIGN - Dark Mode Abfrage wurde entfernt */
:root {
    /* ── BASIS FARBEN ── */
    --c-primary:    #1B3A6B; /* Marineblau */
    --c-bg:         #F8F9FA; /* Hellgrau aus config.toml */
    --c-surface:    #FFFFFF; /* Weiß für Karten */
    --c-text:       #1E293B; /* Dunkles Schiefergrau */
    
    /* Listeneinträge (Tiguan, Arbeitgeber) */
    --c-list-text:  #2D3748; 

    /* Akzentfarben */
    --value-pos:    #2BB34F; /* Neongrün (sanft) */
    --value-neg:    #F44336; /* Rot */
    --value-warn:   #FF9800; /* Orange */
    --value-neon:   #39D353; /* Button-Neon */

    /* Ableitungen */
    --c-surface2:   #F1F3F5;
    --c-dialog:     #FFFFFF;
    --text-2:       rgba(30, 41, 59, 0.85);
    --text-3:       rgba(30, 41, 59, 0.6);
    --border:       rgba(27, 58, 107, 0.08);
    --border-s:     rgba(27, 58, 107, 0.15);
    --shadow:       rgba(27, 58, 107, 0.05);
    
    --r:   12px;
    --r-s:  8px;
}

/* BASE STYLE */
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; color: var(--c-text); }
[data-testid="stAppViewContainer"] { background: var(--c-bg) !important; }
[data-testid="stHeader"] { background: transparent !important; }
.main .block-container { padding: 1.8rem 2.8rem 3rem !important; max-width: 1500px !important; }

/* SIDEBAR - Immer Marineblau */
[data-testid="stSidebar"] { background: var(--c-primary) !important; border-right: none !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.9) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: var(--r-s) !important;
    color: white !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.15) !important;
    border-color: var(--value-warn) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--value-neon) !important;
    border-color: var(--value-neon) !important;
    color: #0A1F0D !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(255,255,255,0.12) !important;
    border-left: 3px solid var(--value-warn) !important;
}

/* LISTENEINTRÄGE & TEXTE */
div[data-testid="stVerticalBlock"] .stMarkdown p {
    color: var(--c-list-text) !important;
    font-weight: 500 !important;
}
div[data-testid="stVerticalBlock"] .stMarkdown span {
    color: var(--text-2) !important;
}

/* METRIKEN & TABELLEN */
[data-testid="metric-container"] {
    background: var(--c-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
}
[data-testid="stMetricValue"] { color: var(--c-text) !important; font-weight: 800 !important; }
[data-testid="stDataFrame"] { 
    border: 1px solid var(--border) !important; 
    border-radius: var(--r) !important; 
    background-color: var(--c-surface) !important;
}

/* INPUTS */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
    background: var(--c-surface) !important;
    border: 1px solid var(--border-s) !important;
    color: var(--c-text) !important;
}

/* SCROLLBAR */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: var(--value-warn); border-radius: 10px; }
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
            <div style="width:48px;height:48px;border-radius:12px;background:rgba(255,152,0,0.15);border:2px solid var(--value-warn);display:flex;align-items:center;justify-content:center;margin:0 auto 0.7rem;font-family:'Outfit',sans-serif;font-weight:800;color:var(--value-warn);">{initials}</div>
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

    if page == "📊 Dashboard":
        dashboard_page(conn, u_id)
    elif page == "📝 Einträge":
        entries_page(conn, u_id)
    elif page == "⚙️ Verwaltung":
        settings_page(conn, u_id)
