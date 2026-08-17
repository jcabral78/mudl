import yt_dlp

def download(url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320'
        }],
        'outtmpl': '/home/joao/Músicas/temp/%(title)s.%(ext)s',
        'quiet': 'true',
        'cookiesfrombrowser': ('firefox',)
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(url)
