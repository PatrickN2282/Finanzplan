import streamlit as st
from db import init_db

# Hilfsskript zum Überprüfen der PostgreSQL-Verbindung
if __name__ == "__main__":
    try:
        conn = init_db()
        c = conn.cursor()
        c.execute('SELECT table_name FROM information_schema.tables WHERE table_schema="public"')
        tables = c.fetchall()
        print('Tabellen in Supabase:', tables)
        if ('users',) in tables:
            c.execute('SELECT id, username FROM users LIMIT 5')
            print('Users (Vorschau):', c.fetchall())
        c.close()
        conn.close()
        print('✅ Verbindung zu Supabase erfolgreich!')
    except Exception as e:
        print(f'❌ Fehler: {e}')