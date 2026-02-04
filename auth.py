import sys
sys.path.append('.')
import streamlit as st
import pandas as pd
import sqlite3
from db import hash_pw

# --- AUTH LOGIK (Multi-User & Secrets) ---
def auth_page():
    st.title("🔐 Finanz-Master v1.4.1")
    tab1, tab2 = st.tabs(["Login", "Registrieren"])

    with tab1:
        with st.form("login_form"):
            u = st.text_input("Benutzername")
            p = st.text_input("Passwort", type="password")
            if st.form_submit_button("Anmelden", width='stretch'):
                user = pd.read_sql_query("SELECT * FROM users WHERE username=? AND password=?",
                                         st.session_state.conn, params=(u, hash_pw(p)))
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_id = int(user.iloc[0]['id'])
                    st.session_state.username = user.iloc[0]['username']
                    st.rerun()
                else:
                    st.error("Benutzername oder Passwort falsch.")

    with tab2:
        st.info("Erstelle ein neues Konto, um deine eigenen Finanzen zu verwalten.")
        with st.form("reg_form"):
            new_vorname = st.text_input("Vorname")
            new_nachname = st.text_input("Nachname")
            new_u = st.text_input("Wunsch-Benutzername")
            new_p = st.text_input("Passwort wählen", type="password")
            if st.form_submit_button("Account erstellen", width='stretch'):
                try:
                    c = st.session_state.conn.cursor()
                    c.execute("INSERT INTO users (username, password) VALUES (%s,%s) RETURNING id", (new_u, hash_pw(new_p)))
                    u_id_new = c.fetchone()[0]
                    # Standard-Kategorien für neuen User anlegen
                    for kat in ["Gehalt", "Miete", "Lebensmittel", "Auto", "Versicherung"]:
                        c.execute("INSERT INTO kategorien (user_id, name) VALUES (%s,%s)", (u_id_new, kat))
                    # Standard-Konto anlegen
                    c.execute("INSERT INTO konten (user_id, name, iban, typ) VALUES (%s, %s, %s, %s)", (u_id_new, "Hauptkonto", "", "Bankkonto"))
                    st.session_state.conn.commit()
                    st.success("Account erstellt! Du kannst dich jetzt einloggen.")
                except Exception as e:
                    st.error(f"Fehler bei der Registrierung: {e}")