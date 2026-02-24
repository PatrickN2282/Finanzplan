import streamlit as st
import pandas as pd
from db import hash_pw, get_conn

def auth_page():
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        # Logo-Block im neuen Design
        st.markdown("""
        <div style="text-align:center;padding:2.5rem 0 1.5rem;">
            <div style="
                display:inline-flex;align-items:center;justify-content:center;
                width:56px;height:56px;border-radius:14px;
                background:#1B3A6B;
                box-shadow:0 6px 20px rgba(27,58,107,0.35);
                margin-bottom:1rem;font-size:1.5rem;
            ">📊</div>
            <h1 style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1.6rem;
                       letter-spacing:-0.035em;margin:0;color:#1A1F2E;">Finanz-Master</h1>
            <p style="color:#8892AA;margin:0.2rem 0 0;font-size:0.82rem;font-weight:400;">
                Deine persönliche Finanzplanung · v1.5
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])

        with tab1:
            with st.form("login_form"):
                u = st.text_input("Benutzername", placeholder="Dein Benutzername")
                p = st.text_input("Passwort", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Anmelden", width='stretch', type="primary")
                if submitted:
                    if not u or not p:
                        st.error("Bitte alle Felder ausfüllen.")
                    else:
                        conn = get_conn()
                        c = conn.cursor()
                        c.execute(
                            "SELECT id, username, vorname FROM users WHERE username=%s AND password=%s",
                            (u, hash_pw(p))
                        )
                        user_data = c.fetchone()
                        c.close()
                        if user_data:
                            st.session_state.logged_in = True
                            st.session_state.user_id   = int(user_data[0])
                            st.session_state.username  = user_data[1]
                            st.session_state.vorname   = user_data[2] if user_data[2] else ""
                            st.rerun()
                        else:
                            st.error("Benutzername oder Passwort falsch.")

        with tab2:
            st.info("Erstelle ein kostenloses Konto.")
            with st.form("reg_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_vorname  = st.text_input("Vorname", placeholder="Max")
                with col2:
                    new_nachname = st.text_input("Nachname", placeholder="Mustermann")
                new_u  = st.text_input("Benutzername", placeholder="maxmuster")
                new_p  = st.text_input("Passwort", type="password", placeholder="Mindestens 6 Zeichen")
                new_p2 = st.text_input("Passwort bestätigen", type="password", placeholder="••••••••")

                if st.form_submit_button("Account erstellen", width='stretch', type="primary"):
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
                                "INSERT INTO users (username,password,vorname,nachname) VALUES (%s,%s,%s,%s) RETURNING id",
                                (new_u, hash_pw(new_p), new_vorname, new_nachname)
                            )
                            uid = c.fetchone()[0]
                            for kat in ["Gehalt","Miete","Lebensmittel","Auto","Versicherung","Freizeit"]:
                                c.execute("INSERT INTO kategorien (user_id,name) VALUES (%s,%s)", (uid, kat))
                            c.execute("INSERT INTO konten (user_id,name,iban,typ) VALUES (%s,%s,%s,%s)",
                                      (uid, "Hauptkonto", "", "Bankkonto"))
                            conn.commit(); c.close()
                            st.success("✅ Account erstellt! Du kannst dich jetzt anmelden.")
                        except Exception as e:
                            conn.rollback()
                            if "unique" in str(e).lower():
                                st.error("Dieser Benutzername ist bereits vergeben.")
                            else:
                                st.error(f"Fehler: {e}")
