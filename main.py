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
# PRECISION FINANCE – Fixed High Contrast Design (v1.3.3)
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
    --text-2:       #475569; 
    --text-3:       #64748B; 
    --border:       rgba(27, 58, 107, 0.08);
    --r: 12px; --r-s: 8px;
}

/* BASE STYLE */
html, body, [class*="css"] { 
    font-family: 'Outfit', sans-serif !important; 
    color: var(--c-text) !important; 
}
[data-testid="stAppViewContainer"] { background: var(--c-bg) !important; }

/* RADIKALER FIX FÜR ALLE LABELS & LEGENDEN (Statistik-Teil) */
[data-testid="stMetricLabel"], 
.stCaptionContainer, 
small, 
label,
[data-testid="stText"],
[data-testid="stWidgetLabel"] p,
.stMarkdown p,
.stMarkdown span {
    color: var(--c-list-text) !important;
    opacity: 1 !important;
}

/* Spezieller Fix für Diagramm-Legenden und Achsen-Beschriftungen */
div[data-testid="stExpanderDetails"] * {
    color: var(--c-list-text) !important;
}

/* EXPANDER DESIGN */
.stExpander {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    background: var(--c-surface) !important;
    margin-bottom: 1rem !important;
}
.stExpander summary {
    background-color: #2D3748 !important;
    color: white !important;
    border-radius: var(--r-s) !important;
}
.stExpander summary:hover { background-color: var(--c-primary) !important; }
.stExpander svg { fill: white !important; }

/* SCHUTZ FÜR FARBIGE WERTE (Timeline) */
span[style*="color: rgb(28, 158, 58)"], span[style*="color: green"] { color: var(--value-pos) !important; }
span[style*="color: rgb(214, 59, 59)"], span[style*="color: red"] { color: var(--value-neg) !important; }

/* SIDEBAR */
[data-testid="stSidebar"] { background: var(--c-primary) !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.9) !important; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--value-neon) !important;
    color: #0A1F0D !important;
    font-weight: 700 !important;
}

/* METRIKEN */
[data-testid="metric-container"] { 
    background: var(--c-surface) !important; 
    border: 1px solid var(--border) !important; 
}
[data-testid="stMetricValue"] { color: var(--c-text) !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)

# --- ROUTING ---
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
