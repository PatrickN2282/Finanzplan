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

    --c-surface2:   #F1F3F5;
    --text-2:       rgba(30, 41, 59, 0.85);
    --border:       rgba(27, 58, 107, 0.08);
    --r: 12px; --r-s: 8px;
}

/* BASE */
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: var(--c-bg) !important; }

/* FIX FÜR EXPANDER (Grafiken & Statistiken) */
.stExpander {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    background: var(--c-surface) !important;
    overflow: hidden !important;
}

/* Expander Header (Eingeklappt & Ausgeklappt) */
.stExpander summary {
    background-color: #2D3748 !important; /* Dunkles Marine-Grau */
    color: white !important;
    padding: 0.5rem 1rem !important;
    border-radius: var(--r-s) !important;
    transition: all 0.3s ease !important;
}

.stExpander summary:hover {
    background-color: var(--c-primary) !important;
}

/* Icon (Pfeil) im Expander weiß färben */
.stExpander svg {
    fill: white !important;
}

/* Inhalt des Expanders */
.stExpander div[data-testid="stExpanderDetails"] {
    background-color: var(--c-surface) !important;
    padding: 1.5rem !important;
    color: var(--c-text) !important;
}

/* TEXT-LOGIK (Balance-Werte schützen) */
div[data-testid="stVerticalBlock"] .stMarkdown p:not(:has(span[style*="color"])) {
    color: var(--c-list-text) !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] { background: var(--c-primary) !important; border-right: none !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.9) !important; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--value-neon) !important;
    color: #0A1F0D !important;
    font-weight: 700 !important;
}

/* METRIKEN */
[data-testid="metric-container"] { background: var(--c-surface) !important; border: 1px solid var(--border) !important; border-radius: var(--r) !important; }
[data-testid="stMetricValue"] { color: var(--c-text) !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)

# --- ROUTING (unverändert) ---
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

    if page == "📊 Dashboard":
        dashboard_page(conn, u_id)
    elif page == "📝 Einträge":
        entries_page(conn, u_id)
    elif page == "⚙️ Verwaltung":
        settings_page(conn, u_id)
