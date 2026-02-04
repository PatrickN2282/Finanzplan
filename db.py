import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import hashlib

# --- DATENBANK SETUP ---
def init_db():
    conn = sqlite3.connect("finanzen_pro_v1_4.db", check_same_thread=False)
    c = conn.cursor()
    # Tabellen mit user_id Erweiterung
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS konten
                 (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, iban TEXT, typ TEXT DEFAULT 'Bankkonto', parent_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS kategorien
                 (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS eintraege
                 (id INTEGER PRIMARY KEY, user_id INTEGER, art TEXT, konto_id INTEGER,
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