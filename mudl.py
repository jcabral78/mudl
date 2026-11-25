import os
from pathlib import Path
import argparse
import sqlite3
import requests
import yt_dlp
from yt_dlp.utils import DownloadError
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, APIC
import sys
import time

def fazer_request(url, params, headers):
    for i in range(5):
        try:
            time.sleep(2 * i)
            resposta = requests.get(url, params=params, headers=headers, timeout=30)
            resposta.raise_for_status()
            dados = resposta.json()
        except requests.RequestException as e:
            print(f"Erro: houve algum problema com a requisição ao MusicBrainz\n{e}")
        else:
            return dados

    sys.exit("Não foi possível fazer a requisição")

def pegar_musicas_mesmo_id(cursor, media_id_mesmo):
    res_mesmo_id = cursor.execute("SELECT * FROM musicas WHERE media_id = ?", (media_id_mesmo,))
    res_mesmo_id = res_mesmo_id.fetchall()

    if len(res_mesmo_id) > 1:
        musicas_mesmo_id = list()

        for mesmo_id in res_mesmo_id:
            print(f"{mesmo_id[0]}) {mesmo_id[1]} - {mesmo_id[2]} | nº da release: {mesmo_id[4]} | URL: {mesmo_id[5]}")
            musicas_mesmo_id.append(mesmo_id[0])

        try:
            escolha = int(input("Escolha a música certa: "))
        except ValueError:
            sys.exit(f"Erro: valor incorreto")

        if not escolha in musicas_mesmo_id:
            sys.exit(f"Erro: valor incorreto")
        else:
            return escolha

        return None

def registrar_metadados():
    pegar_nome = input("Deseja usar o nome registrado nos metadados da música? [s/N] ")
    pegar_artista = input("Deseja usar o artista registrado nos metadados da música? [s/N] ")
    registrar_album = input("Escolha um nome de álbum para usar nos metadados (opcional): ")
    registrar_data = input("Escolha uma data para usar nos metadados (opcional): ")
    registrar_numero = input("Escolha número da música para usar nos metadados (opcional): ")

    if pegar_nome.upper() == "S":
        pegar_nome = 1
    else:
        pegar_nome = 0

    if pegar_artista.upper() == "S":
        pegar_artista = 1
    else:
        pegar_artista = 0

    if registrar_numero:
        try:
            registrar_numero = int(registrar_numero)
        except ValueError:
            sys.exit(f"Erro: valor incorreto")

    return (pegar_nome, pegar_artista, registrar_album, registrar_data, registrar_numero)

def pegar_release(media_id_r):
    url = f"https://musicbrainz.org/ws/2/recording/{media_id_r}"
    params = {"inc": "artists+releases+media+release-groups", "fmt": "json"}
    headers = {"User-Agent": "mudl ( https://github.com/jcabral78/mudl )"}
    
    dados = fazer_request(url, params, headers)

    print("0) Tipo do release | Data de lançamento | Nome do release | ID do release")
    for i, releases in enumerate(dados["releases"]):
        tipo = releases["release-group"].get("primary-type")
        data = releases.get("date")
        nome = releases["release-group"].get("title")
        release_id = releases.get("id")

        print(f"{i + 1}) {tipo} | {data} | {nome} | {release_id}")

    try:
        return int(input("Escolha a release que deseja registrar: ")) - 1
    except ValueError:
        sys.exit(f"Erro: valor incorreto")

def baixar_musica(nome_arquivo, mbid, release_certa, url_youtube, dir_musicas, metadados_registrados):
    url = f"https://musicbrainz.org/ws/2/recording/{mbid}"
    params = {"inc": "artists+releases+media+release-groups", "fmt": "json"}
    headers = {"User-Agent": "mudl ( https://github.com/jcabral78/mudl )"}
    
    dados = fazer_request(url, params, headers)

    release = dados["releases"][release_certa]
    faixas = release["media"][0].get("track") or release["media"][0].get("tracks")

    while True:
        try:
            time.sleep(2)
            capa = requests.get(f"https://coverartarchive.org/release/{release['id']}/front", headers=headers)
            capa.raise_for_status()
        except requests.RequestException as e:
            print(f"Erro: houve algum problema com a requisição da capa\n{e}")
            print("Tentando novamente")
        else:
            break
    
    metadados = {
        "nome": dados["title"],
        "artista": dados["artist-credit"][0]["name"],
        "album": release["title"],
        "capa": capa.content,
        "data": release.get("date"),
        "numero": faixas[0]["position"]
    }

    if metadados_registrados[0]:
        metadados["nome"] = metadados_registrados[0]

    if metadados_registrados[1]:
        metadados["artista"] = metadados_registrados[1]

    if metadados_registrados[2]:
        metadados["album"] = metadados_registrados[2]

    if metadados_registrados[3]:
        metadados["data"] = metadados_registrados[3]

    if metadados_registrados[4]:
        metadados["numero"] = metadados_registrados[4]


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
    for i in range(5):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_youtube])
        except DownloadError as e:
            causa = e.exc_info[1] if e.exc_info else e
            print(f"Erro: houve algum problema no download\n{causa}")
        else:
            break
    else:
        sys.exit("Não foi possível fazer o download da música")


    audio = ID3(dir_musicas / f"{nome_arquivo}.mp3")
    audio.add(TIT2(encoding = 3, text = metadados['nome']))
    audio.add(TPE1(encoding = 3, text = metadados['artista']))
    audio.add(TALB(encoding = 3, text = metadados['album']))
    audio.add(APIC(encoding = 3, mime = 'image/jpeg', type = 3, data = metadados['capa']))
    audio.add(TDRC(encoding = 3, text = metadados['data']))
    audio.add(TRCK(encoding = 3, text = str(metadados['numero'])))
    audio.save()


def main():
    parser = argparse.ArgumentParser()
    grupo = parser.add_mutually_exclusive_group()
    
    grupo.add_argument("-c", "--criar", action="store_true")
    grupo.add_argument("-l", "--ler", action="store_true")
    grupo.add_argument("-a", "--atualizar", action="store_true")
    grupo.add_argument("-r", "--remover", action="store_true")
    
    args = parser.parse_args()

    
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
            release_certa INTEGER NOT NULL,
            url TEXT NOT NULL,
            usar_nome INTEGER,
            usar_artista INTEGER,
            album TEXT,
            data TEXT,
            numero TEXT
        )
    ''')


    if args.criar:
        media_id_c = input("ID da música (MusicBrainz): ")

        release_certa = pegar_release(media_id_c)

        info_c = [input("Nome da música: "), input("Nome do artista/banda: "),
                  media_id_c, release_certa, input("URL da música (Youtube): ")]

        metadados_registrados_c = registrar_metadados()

        for metadados_c in metadados_registrados_c:
            info_c.append(metadados_c)

        info_c = tuple(info_c)

        cursor.execute("""INSERT INTO musicas (nome_musica, nome_artista, media_id, release_certa, url,
                        usar_nome, usar_artista, album, data, numero)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", info_c)
        conexao.commit()
    
    elif args.ler:
        res_l = cursor.execute("SELECT * FROM musicas")
        res_l = res_l.fetchall()
    
        for i, registros in enumerate(res_l):
            print(f"{i + 1}) {registros[1]} - {registros[2]} | ID: {registros[3]} | Nº da release: {registros[4] + 1} | URL: {registros[5]}")

            if registros[6] or registros[7] or registros[8] or registros[9] or registros[10]:
                print("     ", end="")

            if registros[6]:
                print("Usando nome nos metadados   ", end="")

            if registros[7]:
                print("Usando artista nos metadados   ", end="")

            if registros[8]:
                print(f"Album: {registros[8]}   ", end="")

            if registros[9]:
                print(f"Data: {registros[9]}   ", end="")

            if registros[10]:
                print(f"Nº da música: {registros[10]}   ", end="")

            if registros[6] or registros[7] or registros[8] or registros[9] or registros[10]:
                print()
    
    elif args.atualizar:
        media_id_u = input("ID da música (MusicBrainz): ")

        musica_certa = pegar_musicas_mesmo_id(cursor, media_id_u)
        if musica_certa:
            media_id_ou_musica = "ID_musica"
            media_id_u = musica_certa
        else:
            media_id_ou_musica = "media_id"

        media_id_u_novo = input("Novo ID da música (MusicBrainz): ")

        release_certa = pegar_release(media_id_u_novo)

        info_u = [input("Novo nome da música: "), input("Novo nome do artista: "),
                  media_id_u_novo, release_certa, input("Novo URL da música (Youtube): ")]

        metadados_registrados_a = registrar_metadados()

        for metadados_a in metadados_registrados_a:
            info_u.append(metadados_a)

        info_u.append(media_id_u)

        info_u = tuple(info_u)

        cursor.execute(f"""UPDATE musicas SET nome_musica = ?, nome_artista = ?, media_id = ?, release_certa = ?, url = ?,
                        usar_nome = ?, usar_artista = ?, album = ?, data = ?, numero = ? WHERE {media_id_ou_musica} = ?""",
                       info_u)
        conexao.commit()
    
    elif args.remover:
        media_id_d = input("ID da música (MusicBrainz): ")

        musica_certa = pegar_musicas_mesmo_id(cursor, media_id_d)
        if musica_certa:
            media_id_ou_musica = "ID_musica"
            media_id_d = musica_certa
        else:
            media_id_ou_musica = "media_id"

        cursor.execute(f"DELETE FROM musicas WHERE {media_id_ou_musica} = ?", (media_id_d,))
        conexao.commit()
    
    else: 
        res = cursor.execute("SELECT * FROM musicas")
        res = res.fetchall()
        
        for registros in res:
            nome_arquivo = f"{registros[1]} - {registros[2]}"
            metadados_registrados = ["", "", "", "", ""]

            if registros[6]:
                metadados_registrados[0] = registros[1]

            if registros[7]:
                metadados_registrados[1] = registros[2]

            if registros[8]:
                metadados_registrados[2] = registros[8]

            if registros[9]:
                metadados_registrados[3] = registros[9]

            if registros[10]:
                metadados_registrados[4] = registros[10]

            if not (dir_musicas / f"{nome_arquivo}.mp3").is_file():
                baixar_musica(nome_arquivo, registros[3], registros[4], registros[5], dir_musicas, metadados_registrados)
    
    conexao.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(130)
