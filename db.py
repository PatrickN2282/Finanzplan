import streamlit as st
import pandas as pd
from psycopg2 import connect
from datetime import datetime, timedelta
import plotly.express as px
import hashlib

# --- DATENBANK SETUP ---
def init_db():
    conn = connect(
        host="db.xsssssdmoqcxyxvvfzev.supabase.co",
        port=5432,
        dbname="postgres",
        user="postgres",
        password="Hannover1896!Pixel"
    )
    c = conn.cursor()
    # Tabellen mit user_id Erweiterung
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS konten
                 (id SERIAL PRIMARY KEY, user_id INTEGER, name TEXT, iban TEXT, typ TEXT DEFAULT 'Bankkonto', parent_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS kategorien
                 (id SERIAL PRIMARY KEY, user_id INTEGER, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS eintraege
                 (id SERIAL PRIMARY KEY, user_id INTEGER, art TEXT, konto_id INTEGER,
                  kategorie TEXT, zweck TEXT, betrag REAL, typ TEXT, intervall TEXT,
                  start_datum TEXT, end_datum TEXT, kuendigung_tage INTEGER)''')
    conn.commit()
    return conn

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# --- HILFSFUNKTIONEN ---
def format_euro(val):
    if val is None: return "0,00 €"
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"

def get_emoji(art, typ):
    if typ == "Einnahme": return "💰"
    if art == "Abo": return "🔄"
    if art == "Finanzierung": return "📉"
    return "💸"