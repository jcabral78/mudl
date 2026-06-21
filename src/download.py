import yt_dlp

def baixar(nome, url):
    while True:
        try:
            ydl_opts = {
                'format': 'm4a/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320'
                }],
                'outtmpl': f'{nome}.%(ext)s',
                'quiet': 'true'
            }

            print(f"Baixando Agora: {nome}")
            yt_dlp.YoutubeDL(ydl_opts).download(url)
        except:
            print("     Ocorreu um erro, tentando novamente")
        else:
            break
