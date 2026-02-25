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

:root {
    /* ── LIGHT MODE (Config Basis) ── */
    --c-primary:  var(--primary-color, #1B3A6B); /* Marine */
    --c-bg:       var(--background-color, #F8F9FA); 
    --c-surface:  var(--secondary-background-color, #FFFFFF);
    --c-text:     var(--text-color, #1E293B);

    /* Akzentfarben */
    --value-pos:   #2BB34F; /* Neongrün (sanft) */
    --value-neg:   #F44336; /* Rot */
    --value-warn:  #FF9800; /* Orange Akzent */
    --value-neon:  #39D353; /* Knalliges Neongrün für Buttons */

    /* Ableitungen */
    --c-surface2:  color-mix(in srgb, var(--c-surface) 90%, var(--c-bg) 10%);
    --c-dialog:    #FFFFFF;
    --border:      rgba(27, 58, 107, 0.08);
    --border-s:    rgba(27, 58, 107, 0.15);
    --text-2:      rgba(30, 41, 59, 0.8);
    --text-3:      rgba(30, 41, 59, 0.5);
    --shadow:      rgba(27, 58, 107, 0.05);
    
    --r:   12px;
    --r-s:  8px;
}

/* ── DARK MODE OVERRIDE (Pastel Midnight) ── */
@media (prefers-color-scheme: dark) {
    :root {
        --c-primary:  #7DA7D9; /* Pastell-Marine */
        --c-bg:       #20222C; /* Weiches Anthrazit */
        --c-surface:  #2A2D3A; /* Pastell-Slate */
        --c-text:     #E2E8F0; /* Off-White */
        
        --value-pos:   #81C784; /* Pastell-Grün */
        --value-warn:  #FFB74D; /* Pastell-Orange */
        
        --c-surface2:  #333747;
        --c-dialog:    #252833;
        --text-2:      #94A3B8;
        --text-3:      #64748B;
        --border:      rgba(255, 255, 255, 0.05);
        --border-s:    rgba(255, 255, 255, 0.12);
        --shadow:      rgba(0, 0, 0, 0.2);
    }
}

/* BASE */
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: var(--c-bg) !important; }
[data-testid="stHeader"] { background: transparent !important; }
.main .block-container { padding: 1.8rem 2.8rem 3rem !important; max-width: 1500px !important; }

/* SIDEBAR - Marineblaues Original */
[data-testid="stSidebar"] { 
    background: #1B3A6B !important; 
    border-right: none !important; 
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: var(--r-s) !important;
    color: white !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.12) !important;
    border-color: var(--value-warn) !important; /* Orange-Hover-Effekt */
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--value-neon) !important; /* Neongrün */
    border-color: var(--value-neon) !important;
    color: #0A1F0D !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(255,255,255,0.1) !important;
    border-left: 3px solid var(--value-warn) !important; /* Orange-Akzent */
    color: white !important;
}

/* METRIKEN */
[data-testid="metric-container"] {
    background: var(--c-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    box-shadow: 0 4px 12px var(--shadow) !important;
}
[data-testid="stMetricLabel"] { color: var(--text-3) !important; font-size: 0.75rem !important; font-weight: 600 !important;}
[data-testid="stMetricValue"] { color: var(--c-text) !important; font-weight: 800 !important; }

/* TABELLEN */
[data-testid="stDataFrame"] { 
    border: 1px solid var(--border) !important; 
    border-radius: var(--r) !important; 
    background-color: var(--c-surface) !important;
}
[data-testid="stDataFrame"] * { color: var(--c-text) !important; }
[data-testid="stDataFrame"] thead th { 
    background: var(--c-surface2) !important; 
    color: var(--text-2) !important;
}

/* INPUTS */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
    background: var(--c-surface) !important;
    border: 1px solid var(--border-s) !important;
    border-radius: var(--r-s) !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--value-warn) !important; /* Orange Focus */
}

/* MODAL */
[data-testid="stModal"] > div {
    background: var(--c-dialog) !important;
    border-radius: 16px !important;
}

/* TITEL & TEXT */
h1, h2, h3 { color: var(--c-text) !important; letter-spacing: -0.02em !important; }
p, span, label { color: var(--text-2) !important; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: var(--value-warn); border-radius: 10px; opacity: 0.5; }
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
