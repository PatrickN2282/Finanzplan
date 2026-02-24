import streamlit as st
import pandas as pd
from db import hash_pw, get_conn

# --- AUTH LOGIK ---
def auth_page():
    # Zentrierter Login-Container
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("""
        <div style='text-align:center; padding: 2rem 0 1rem 0;'>
            <span style='font-size: 3rem;'>🏦</span>
            <h1 style='margin: 0.5rem 0 0 0; font-size: 1.8rem; font-weight: 700;'>Finanz-Master</h1>
            <p style='color: #888; margin: 0.2rem 0 1.5rem 0; font-size: 0.9rem;'>v1.5.0</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 Login", "📝 Registrieren"])

        with tab1:
            with st.form("login_form"):
                u = st.text_input("Benutzername", placeholder="Dein Benutzername")
                p = st.text_input("Passwort", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Anmelden", use_container_width=True, type="primary")
                if submitted:
                    if not u or not p:
                        st.error("Bitte Benutzername und Passwort eingeben.")
                    else:
                        conn = get_conn()
                        user = pd.read_sql_query(
                            "SELECT * FROM users WHERE username=%s AND password=%s",
                            conn, params=(u, hash_pw(p))
                        )
                        if not user.empty:
                            st.session_state.logged_in = True
                            st.session_state.user_id = int(user.iloc[0]['id'])
                            st.session_state.username = user.iloc[0]['username']
                            st.session_state.vorname = user.iloc[0].get('vorname', '')
                            st.rerun()
                        else:
                            st.error("Benutzername oder Passwort falsch.")

        with tab2:
            st.info("Erstelle ein neues Konto, um deine eigenen Finanzen zu verwalten.")
            with st.form("reg_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_vorname = st.text_input("Vorname", placeholder="Max")
                with col2:
                    new_nachname = st.text_input("Nachname", placeholder="Mustermann")
                new_u = st.text_input("Wunsch-Benutzername", placeholder="maxmuster")
                new_p = st.text_input("Passwort wählen", type="password", placeholder="Mindestens 6 Zeichen")
                new_p2 = st.text_input("Passwort wiederholen", type="password", placeholder="••••••••")

                if st.form_submit_button("Account erstellen", use_container_width=True, type="primary"):
                    if not new_u or not new_p:
                        st.error("Benutzername und Passwort sind Pflichtfelder.")
                    elif len(new_p) < 6:
                        st.error("Passwort muss mindestens 6 Zeichen lang sein.")
                    elif new_p != new_p2:
                        st.error("Passwörter stimmen nicht überein.")
                    else:
                        conn = get_conn()
                        try:
                            c = conn.cursor()
                            c.execute(
                                "INSERT INTO users (username, password, vorname, nachname) VALUES (%s,%s,%s,%s) RETURNING id",
                                (new_u, hash_pw(new_p), new_vorname, new_nachname)
                            )
                            u_id_new = c.fetchone()[0]
                            # Standard-Kategorien
                            for kat in ["Gehalt", "Miete", "Lebensmittel", "Auto", "Versicherung", "Freizeit"]:
                                c.execute("INSERT INTO kategorien (user_id, name) VALUES (%s,%s)", (u_id_new, kat))
                            # Standard-Konto
                            c.execute(
                                "INSERT INTO konten (user_id, name, iban, typ) VALUES (%s,%s,%s,%s)",
                                (u_id_new, "Hauptkonto", "", "Bankkonto")
                            )
                            conn.commit()
                            c.close()
                            st.success("✅ Account erstellt! Du kannst dich jetzt einloggen.")
                        except Exception as e:
                            conn.rollback()
                            if "unique" in str(e).lower():
                                st.error("Dieser Benutzername ist bereits vergeben.")
                            else:
                                st.error(f"Fehler bei der Registrierung: {e}")
