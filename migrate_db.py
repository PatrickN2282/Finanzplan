import sqlite3
conn = sqlite3.connect('finanzen_pro_v1_4.db')
c = conn.cursor()
try:
    c.execute('ALTER TABLE konten ADD COLUMN typ TEXT DEFAULT "Bankkonto"')
    print('Spalte typ hinzugefügt')
except sqlite3.OperationalError as e:
    print(f'Spalte typ bereits vorhanden: {e}')
try:
    c.execute('ALTER TABLE konten ADD COLUMN parent_id INTEGER')
    print('Spalte parent_id hinzugefügt')
except sqlite3.OperationalError as e:
    print(f'Spalte parent_id bereits vorhanden: {e}')
try:
    c.execute('ALTER TABLE eintraege ADD COLUMN betrag_typ TEXT DEFAULT "Gesamtbetrag"')
    print('Spalte betrag_typ hinzugefügt')
except sqlite3.OperationalError as e:
    print(f'Spalte betrag_typ bereits vorhanden: {e}')
try:
    c.execute('ALTER TABLE users ADD COLUMN vorname TEXT')
    print('Spalte vorname hinzugefügt')
except sqlite3.OperationalError as e:
    print(f'Spalte vorname bereits vorhanden: {e}')
try:
    c.execute('ALTER TABLE users ADD COLUMN nachname TEXT')
    print('Spalte nachname hinzugefügt')
except sqlite3.OperationalError as e:
    print(f'Spalte nachname bereits vorhanden: {e}')
conn.commit()
conn.close()