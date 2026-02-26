import streamlit as st
import pandas as pd
from db import hash_pw, get_conn

def auth_page():

    # ── Emoji-Hintergrund + Card-Rahmung ──────────────────────────
    st.markdown("""
    <style>
    /* Vollbild-Hintergrund */
    [data-testid="stAppViewContainer"] {
        background: #F0F2F5 !important;
    }

    /* Emoji-Canvas – liegt hinter allem */
    #emoji-bg {
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        overflow: hidden;
        user-select: none;
    }

    .e {
        position: absolute;
        font-style: normal;
        line-height: 1;
        opacity: 0.13;
        filter: grayscale(20%);
        animation: efloat 18s ease-in-out infinite;
    }

    @keyframes efloat {
        0%, 100% { transform: translateY(0px) rotate(var(--r)); }
        50%       { transform: translateY(-12px) rotate(var(--r)); }
    }

    /* Login-Card – Glassmorphism */
    #auth-card-wrap {
        position: relative;
        z-index: 10;
        max-width: 480px;
        margin: 2.5rem auto 0;
        background: rgba(255,255,255,0.82);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(13,126,168,0.20);
        border-radius: 20px;
        box-shadow:
            0 4px 32px rgba(13,21,38,0.12),
            0 1px 0 rgba(255,255,255,0.9) inset;
        padding: 2.2rem 2.2rem 1.8rem;
    }

    /* Hauptbereich-Padding reduzieren */
    [data-testid="stMainBlockContainer"] {
        padding-top: 0 !important;
    }

    /* Tab-Panel innerhalb Card ohne extra Border */
    #auth-card-wrap + div [data-testid="stTabs"] [role="tabpanel"],
    [data-testid="stTabs"] [role="tabpanel"] {
        background: transparent !important;
        border-left: none !important;
        border-right: none !important;
        border-bottom: none !important;
        padding: 1rem 0 0 !important;
    }
    </style>

    <div id="emoji-bg" aria-hidden="true"></div>

    <script>
    (function() {
        const emojis = [
            "💰","💳","📈","📉","🏦","💵","💶","💴","🪙","📊",
            "💹","🏧","💸","🤑","📋","🧾","💼","🔐","⚡","📅",
            "🎯","🔄","📌","💡","⚖️","🏆","🎲","🔢","📐","✅"
        ];
        const bg = document.getElementById("emoji-bg");
        if (!bg) return;
        for (let i = 0; i < 55; i++) {
            const span = document.createElement("span");
            span.className = "e";
            span.textContent = emojis[Math.floor(Math.random() * emojis.length)];
            const size  = 22 + Math.random() * 36;
            const rot   = (Math.random() * 60 - 30).toFixed(1) + "deg";
            const delay = (Math.random() * 12).toFixed(2) + "s";
            const dur   = (14 + Math.random() * 10).toFixed(1) + "s";
            span.style.cssText =
                "left:"  + (Math.random()*100).toFixed(2) + "%;" +
                "top:"   + (Math.random()*100).toFixed(2) + "%;" +
                "font-size:" + size + "px;" +
                "--r:" + rot + ";" +
                "animation-delay:" + delay + ";" +
                "animation-duration:" + dur + ";";
            bg.appendChild(span);
        }
    })();
    </script>

    <div id="auth-card-wrap">
    """, unsafe_allow_html=True)

    # ── Logo ──────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:0 0 1.4rem;">
        <div style="
            display:inline-flex;align-items:center;justify-content:center;
            width:60px;height:60px;border-radius:14px;
            background:#0D7EA8;
            box-shadow:0 8px 24px rgba(13,126,168,0.35);
            margin-bottom:1rem;font-size:1.6rem;
        ">📊</div>
        <h1 style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:1.9rem;
                   letter-spacing:0.06em;text-transform:uppercase;margin:0;color:#0D1526;">
            Finanz-Master
        </h1>
        <p style="color:#5A6A8A;margin:0.25rem 0 0;font-size:0.82rem;
                  font-weight:400;font-family:'DM Sans',sans-serif;">
            Deine persönliche Finanzplanung · v1.5
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────
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

    # Card schließen
    st.markdown("</div>", unsafe_allow_html=True)
