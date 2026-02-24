"""
Hilfsskript: PostgreSQL-Verbindung und Datenbankstruktur prüfen.
Aufruf: python check_db.py
"""
import os
import sys
sys.path.append('.')

# Für Standalone-Ausführung: Secrets manuell setzen oder .env laden
# Alternativ: connection_url als Umgebungsvariable setzen
# export DB_URL="postgresql://user:pass@host:5432/dbname"

def check_db():
    from psycopg2 import connect
    db_url = os.environ.get("DB_URL")
    if not db_url:
        print("❌ Bitte DB_URL als Umgebungsvariable setzen.")
        print("   export DB_URL='postgresql://user:pass@host:5432/dbname'")
        sys.exit(1)

    try:
        conn = connect(db_url)
        c = conn.cursor()

        # Tabellen auflisten (einfache Anführungszeichen für SQL-Strings!)
        c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [t[0] for t in c.fetchall()]
        print(f"✅ Verbindung erfolgreich! Tabellen: {tables}")

        if 'users' in tables:
            c.execute("SELECT id, username FROM users LIMIT 5")
            print(f"   Users (Vorschau): {c.fetchall()}")

        if 'eintraege' in tables:
            c.execute("SELECT COUNT(*) FROM eintraege")
            print(f"   Einträge gesamt: {c.fetchone()[0]}")

        # Spalten von eintraege prüfen
        c.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name='eintraege'
            ORDER BY ordinal_position
        """)
        cols = c.fetchall()
        print(f"   Spalten in 'eintraege': {[col[0] for col in cols]}")

        c.close()
        conn.close()
        print("✅ Alles OK!")
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    check_db()
