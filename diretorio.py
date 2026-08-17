import os

home = os.path.expanduser("~")

if not os.path.exists(f"{home}/Músicas"):
    os.makedirs(f"{home}/Músicas")

if not os.path.exists(f"{home}/Músicas/Biblioteca"):
    os.makedirs(f"{home}/Músicas/Biblioteca")

if not os.path.exists(f"{home}/Músicas/Configurações"):
    os.makedirs(f"{home}/Músicas/Configurações")

if not os.path.exists(f"{home}/Músicas/temp"):
    os.makedirs(f"{home}/Músicas/temp")
