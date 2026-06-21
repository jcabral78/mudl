import sqlite3

def inserir(data):
    cursor.executemany("INSERT INTO musicas VALUES(?, ?)", data)
    con.commit()

def retornar():
    res = cursor.execute("SELECT * FROM musicas")
    return res.fetchall()

def fechar():
    con.close()

con = sqlite3.connect("mudl.db")
cursor = con.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS musicas(nome, link)")
