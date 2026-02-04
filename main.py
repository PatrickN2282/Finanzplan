import streamlit as st
from db import init_db
from auth import auth_page
from ui import eintrag_dialog, dashboard_page, entries_page, settings_page

# --- HAUPTPROGRAMM ---
st.set_page_config(page_title="Finanz-Master v1.4.1", layout="wide")

# --- KEIN CUSTOM CSS ---

if 'conn' not in st.session_state:
    st.session_state.conn = init_db()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    auth_page()
else:
    conn = st.session_state.conn
    u_id = st.session_state.user_id

    # --- SIDEBAR ---
    with st.sidebar:
        st.title(f"🏦 {st.session_state.username}")
        page = st.radio("Navigation", ["📊 Dashboard", "📝 Einträge", "⚙️ Verwaltung"])
        if st.button("➕ Neuer Eintrag", width='stretch'): eintrag_dialog(conn, u_id)
        st.divider()
        if st.button("🚪 Abmelden", width='stretch'):
            st.session_state.logged_in = False
            st.rerun()

    # --- PAGES ---
    if page == "📊 Dashboard":
        dashboard_page(conn, u_id)
    elif page == "📝 Einträge":
        entries_page(conn, u_id)
    elif page == "⚙️ Verwaltung":
        settings_page(conn, u_id)