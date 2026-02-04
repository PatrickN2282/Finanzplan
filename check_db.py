import sqlite3
conn = sqlite3.connect('finanzen_pro_v1_4.db')
c = conn.cursor()
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = c.fetchall()
print('Tabellen:', tables)
if 'users' in [t[0] for t in tables]:
    c.execute('SELECT * FROM users')
    print('Users:', c.fetchall())
conn.close()