import streamlit as st
import pandas as pd
from psycopg2 import connect, OperationalError
from datetime import datetime, timedelta
import plotly.express as px
import hashlib

# --- DATENBANK SETUP ---
def init_db():
    """Verbindung zu PostgreSQL aufbauen und Tabellen anlegen."""
    db_url = st.secrets["database"]["connection_url"]
    conn = connect(db_url)
    conn.autocommit = False
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id SERIAL PRIMARY KEY,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 vorname TEXT DEFAULT '',
                 nachname TEXT DEFAULT '')''')

    c.execute('''CREATE TABLE IF NOT EXISTS konten (
                 id SERIAL PRIMARY KEY,
                 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                 name TEXT NOT NULL,
                 iban TEXT DEFAULT '',
                 typ TEXT DEFAULT 'Bankkonto',
                 parent_id INTEGER)''')

    c.execute('''CREATE TABLE IF NOT EXISTS kategorien (
                 id SERIAL PRIMARY KEY,
                 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                 name TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS eintraege (
                 id SERIAL PRIMARY KEY,
                 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                 art TEXT NOT NULL,
                 konto_id INTEGER NOT NULL REFERENCES konten(id) ON DELETE CASCADE,
                 kategorie TEXT,
                 zweck TEXT,
                 betrag REAL DEFAULT 0,
                 betrag_typ TEXT DEFAULT 'Monatliche Rate',
                 typ TEXT NOT NULL,
                 intervall TEXT DEFAULT 'Monatlich',
                 start_datum TEXT,
                 end_datum TEXT,
                 kuendigung_tage INTEGER)''')

    conn.commit()
    c.close()
    return conn


def get_conn():
    """Gibt eine aktive Verbindung zurück – reconnect bei Bedarf."""
    if 'conn' not in st.session_state or st.session_state.conn is None:
        st.session_state.conn = init_db()
        return st.session_state.conn
    try:
        # Ping
        st.session_state.conn.cursor().execute("SELECT 1")
        return st.session_state.conn
    except OperationalError:
        st.session_state.conn = init_db()
        return st.session_state.conn


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# --- HILFSFUNKTIONEN ---
def format_euro(val):
    if val is None:
        return "0,00 €"
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def get_emoji(art, typ):
    if typ == "Einnahme":
        return "💰"
    if art == "Abo":
        return "🔄"
    if art == "Finanzierung":
        return "📉"
    return "💸"
