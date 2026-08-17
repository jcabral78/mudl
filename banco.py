import sqlite3

con = sqlite3.connect("mudl.db")
c = con.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS musicas(
    id INTEGER,
    url TEXT,
    nome TEXT,
    media_id TEXT
)""")

con.commit()
con.close()
