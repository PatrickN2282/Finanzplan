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
# PRECISION FINANCE – High Contrast Light Design (v1.3.3)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
    --c-primary:    #1B3A6B; 
    --c-bg:         #F8F9FA; 
    --c-surface:    #FFFFFF; 
    --c-text:       #1E293B; 
    --value-pos:    #2BB34F; 
    --value-neg:    #F44336; 
    --value-warn:   #FF9800; 
    --value-neon:   #39D353; 
    --border:       rgba(27, 58, 107, 0.15);
}

/* 1. DER RADIKALE TEXT-FIX */
/* Erzwingt dunkle Schrift für ALLES, außer Elemente mit expliziter Farbe (Bilanzen) */
html, body, [data-testid="stAppViewContainer"], .main, [data-testid="stMarkdownContainer"] p, 
[data-testid="stMetricLabel"], label, .stCaptionContainer, span:not([style*="color"]) {
    color: var(--c-text) !important;
    font-family: 'Outfit', sans-serif !important;
    opacity: 1 !important;
}

/* 2. BILANZ-FARBEN RETTEN (Grün & Rot in der Timeline) */
/* Diese Selektoren schützen deine farbigen Beträge vor der allgemeinen Abdunklung */
span[style*="color: rgb(28, 158, 58)"], span[style*="color: #1C9E3A"], span[style*="color: green"] { 
    color: var(--value-pos) !important; 
    font-weight: 700 !important;
}
span[style*="color: rgb(214, 59, 59)"], span[style*="color: #D63B3B"], span[style*="color: red"] { 
    color: var(--value-neg) !important; 
    font-weight: 700 !important;
}

/* 3. MODAL / POP-UP (Pastell & Klarheit) */
div[data-testid="stModal"] > div:first-child > div:first-child {
    background-color: #F0F2F6 !important; /* Helles Pastell-Blau */
    border: 1px solid var(--border) !important;
}
div[data-testid="stModal"] * { color: var(--c-text) !important; }
div[data-testid="stModal"] input, div[data-testid="stModal"] div[data-baseweb="select"] > div {
    background-color: white !important;
    color: var(--c-text) !important;
}

/* 4. DIAGRAMM-LEGENDEN (Fix für die unsichtbaren Kategorien) */
/* Plotly/SVG Texte werden hiermit erfasst */
text, .legendtext, .xtick text, .ytick text {
    fill: #475569 !important;
    font-size: 13px !important;
}

/* 5. EXPANDER FIX */
.stExpander { background: white !important; border: 1px solid var(--border) !important; }
.stExpander summary { background-color: #2D3748 !important; color: white !important; }
.stExpander summary svg { fill: white !important; }

/* 6. SIDEBAR */
[data-testid="stSidebar"] { background: var(--c-primary) !important; }
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--value-neon) !important;
    color: #0A1F0D !important;
}
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
