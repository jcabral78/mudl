import os
from pathlib import Path
import sqlite3
import requests
import yt_dlp
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, APIC

def baixar_musica(nome_arquivo, mbid, url_youtube, dir_musicas):

    ###################
    # Pegar metadados #
    ###################

    url = f"https://musicbrainz.org/ws/2/recording/{mbid}"
    params = {"inc": "artists+releases+media+release-groups", "fmt": "json"}
    headers = {"User-Agent": "mudl ( https://github.com/jcabral78/mudl )"}
    
    dados = requests.get(url, params=params, headers=headers).json()
    
    release = dados["releases"][0]
    faixas = release["media"][0].get("track") or release["media"][0].get("tracks")

    capa = requests.get(f"https://coverartarchive.org/release-group/{release['release-group']['id']}/front", headers=headers)
    
    metadados = {
        "nome": dados["title"],
        "artista": dados["artist-credit"][0]["name"],
        "album": release["title"],
        "capa": capa.content,
        "data": release.get("date"),
        "numero": faixas[0]["position"]
    }
    
    #################
    # Baixar música #
    #################

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320'
            }],
        'paths': {'home': os.fspath(dir_musicas)},
        'outtmpl': f'{nome_arquivo}.%(ext)s',
        'quiet': 'true'
    }

    print(f"Baixando: {nome_arquivo}")
    yt_dlp.YoutubeDL(ydl_opts).download([url_youtube])

    #####################
    # Inserir metadados #
    #####################

    audio = ID3(dir_musicas / f"{nome_arquivo}.mp3")
    audio.add(TIT2(encoding = 3, text = metadados['nome']))
    audio.add(TPE1(encoding = 3, text = metadados['artista']))
    audio.add(TALB(encoding = 3, text = metadados['album']))
    audio.add(APIC(encoding = 3, mime = 'image/jpeg', type = 3, data = metadados['capa']))
    audio.add(TDRC(encoding = 3, text = metadados['data']))
    audio.add(TRCK(encoding = 3, text = str(metadados['numero'])))
    audio.save()


base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
dir_config = base / "mudl"
dir_config.mkdir(parents=True, exist_ok=True)

dir_musicas = Path.home() / "Músicas"
dir_musicas.mkdir(parents=True, exist_ok=True)


conexao = sqlite3.connect(dir_config / "mudl.db")
cursor = conexao.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS musicas(
        ID_musica INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_musica TEXT NOT NULL,
        nome_artista TEXT NOT NULL,
        media_id TEXT NOT NULL,
        url TEXT NOT NULL
    )
''')


escolha = input("C - R - U - D: ")

if escolha == "C":
    info_c = (input("nome: "), input("artista: "), input("id: "), input("url: "))
    cursor.execute("INSERT INTO musicas (nome_musica, nome_artista, media_id, url) VALUES(?, ?, ?, ?)", info_c)

if escolha == "R":
    res_r = cursor.execute("SELECT * FROM musicas")
    res_r = res_r.fetchall()

    for i, registros in enumerate(res_r):
        print(f"{i + 1}) {registros[1]} - {registros[2]} | {registros[3]} | {registros[4]}")

if escolha == "U":
    media_id_u = input("media_id: ")
    info_u = (input("nome: "), input("artista: "), input("id: "), input("url: "), media_id_u)
    cursor.execute("UPDATE musicas SET nome_musica = ?, nome_artista = ?, media_id = ?, url = ? WHERE media_id = ?", (info_u))

if escolha == "D":
    media_id_d = input("media_id: ")
    cursor.execute("DELETE FROM musicas WHERE media_id = ?", (media_id_d,))

conexao.commit()


res = cursor.execute("SELECT * FROM musicas")
res = res.fetchall()

for registros in res:
    nome_arquivo = f"{registros[1]} - {registros[2]}"
    if not (dir_musicas / f"{nome_arquivo}.mp3").is_file():
        baixar_musica(nome_arquivo, registros[3], registros[4], dir_musicas)

conexao.close()
