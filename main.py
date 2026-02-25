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
# PRECISION FINANCE – High-Contrast & Pastel Modals (v1.3.3)
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
    --c-modal-bg:   #F0F4F8; /* Pastell-Blau-Grau für Popups */
    --value-neon:   #39D353;
    --value-warn:   #FF9800;
    --border:       rgba(27, 58, 107, 0.12);
}

/* 1. GLOBALE TEXTRETTUNG (Sorgt dafür, dass auf Weiß alles sichtbar ist) */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--c-bg) !important;
}

/* Alle Standard-Texte, Labels und Beschreibungen auf der Hauptseite */
[data-testid="stMarkdownContainer"] p, 
[data-testid="stMetricLabel"], 
.stCaptionContainer, 
label, 
span {
    color: var(--c-text) !important;
    opacity: 1 !important;
}

/* 2. MODAL & POP-UP (Eintrag bearbeiten) - PASTELL LOOK */
div[data-testid="stModal"] > div:first-child > div:first-child {
    background-color: var(--c-modal-bg) !important;
    border: 2px solid var(--border) !important;
    border-radius: 16px !important;
}

/* Alle Texte innerhalb des Modals */
div[data-testid="stModal"] * {
    color: #0F172A !important; /* Extra dunkel für Kontrast im Modal */
}

/* Eingabefelder im Modal */
div[data-testid="stModal"] input, 
div[data-testid="stModal"] div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* 3. DROPDOWN-MENÜS (Die schwebenden Listen) */
div[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border: 1px solid var(--border) !important;
}
div[data-baseweb="menu"] li {
    color: #1E293B !important;
}
div[data-baseweb="menu"] li:hover {
    background-color: #E2E8F0 !important;
}

/* 4. SPEZIAL-FIX FÜR DIAGRAMME */
text, .legendtext {
    fill: #475569 !important;
    font-size: 12px !important;
}

/* 5. EXPANDER (Grafiken & Statistiken) */
.stExpander { 
    background: white !important; 
    border: 1px solid var(--border) !important; 
}
.stExpander summary { 
    background-color: #2D3748 !important; 
    color: white !important; 
}
.stExpander summary * { color: white !important; }

/* 6. SIDEBAR */
[data-testid="stSidebar"] { background: var(--c-primary) !important; }
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--value-neon) !important;
    color: #0A1F0D !important;
}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE & ROUTING (Unverändert) ---
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
