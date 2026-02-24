import streamlit as st
from db import get_conn
from auth import auth_page
from ui import eintrag_dialog, dashboard_page, entries_page, settings_page

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Finanz-Master",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
/* Globale Schrift & Hintergrund */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A1D27 0%, #12141E 100%);
    border-right: 1px solid #2A2D3E;
}
[data-testid="stSidebar"] .stButton button {
    width: 100%;
    border-radius: 8px;
    border: 1px solid #2A2D3E;
    background: #1E2130;
    color: #E8EAF0;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #4F8EF7;
    border-color: #4F8EF7;
    color: white;
}

/* Metriken aufhübschen */
[data-testid="metric-container"] {
    background: #1A1D27;
    border: 1px solid #2A2D3E;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    transition: transform 0.15s;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    border-color: #4F8EF7;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}

/* DataFrames */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #2A2D3E;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    background: #1A1D27;
    border: 1px solid #2A2D3E;
    border-bottom: none;
    padding: 0.5rem 1.2rem;
    color: #888;
}
.stTabs [aria-selected="true"] {
    background: #4F8EF7 !important;
    color: white !important;
    border-color: #4F8EF7 !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid #2A2D3E;
    border-radius: 10px;
    background: #1A1D27;
}

/* Primär-Button */
.stButton [data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #4F8EF7, #6B4EFF);
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

/* Divider */
hr {
    border-color: #2A2D3E !important;
    margin: 1rem 0 !important;
}

/* Header Seiten */
h1 { font-weight: 700 !important; letter-spacing: -0.5px; }
h2 { font-weight: 600 !important; color: #C8CADB !important; }
h3 { font-weight: 600 !important; color: #A0A3B5 !important; }

/* Positive/Negative Werte in Metriken */
[data-testid="stMetricDelta"] { font-size: 0.85rem !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #12141E; }
::-webkit-scrollbar-thumb { background: #2A2D3E; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4F8EF7; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INIT ---
if 'conn' not in st.session_state:
    st.session_state.conn = get_conn()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ROUTING ---
if not st.session_state.logged_in:
    auth_page()
else:
    conn = get_conn()
    u_id = st.session_state.user_id
    username = st.session_state.get('username', 'User')
    vorname = st.session_state.get('vorname', '')
    display_name = vorname if vorname else username

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"""
        <div style='padding: 0.5rem 0 1rem 0;'>
            <div style='font-size: 2rem; text-align: center;'>👤</div>
            <div style='text-align: center; font-weight: 700; font-size: 1.1rem; color: #E8EAF0;'>{display_name}</div>
            <div style='text-align: center; font-size: 0.8rem; color: #666; margin-top: 2px;'>@{username}</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📝 Einträge", "⚙️ Verwaltung"],
            label_visibility="collapsed"
        )

        st.divider()

        if st.button("➕ Neuer Eintrag", use_container_width=True, type="primary"):
            eintrag_dialog(conn, u_id)

        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

        if st.button("🚪 Abmelden", use_container_width=True):
            for key in ['logged_in', 'user_id', 'username', 'vorname', 'conn']:
                st.session_state.pop(key, None)
            st.rerun()

    # --- SEITEN ---
    if page == "📊 Dashboard":
        dashboard_page(conn, u_id)
    elif page == "📝 Einträge":
        entries_page(conn, u_id)
    elif page == "⚙️ Verwaltung":
        settings_page(conn, u_id)
