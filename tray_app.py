import sys
import os
import threading
import subprocess
import webbrowser
import uvicorn
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# URL locale du serveur
SERVER_URL = "http://127.0.0.1:8000"
CSV_FILE = "history.csv"

def create_icon_image():
    """Génère une icône circulaire verte type Spotify/Shazify."""
    width = 64
    height = 64
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    # Cercle vert
    dc.ellipse((4, 4, width - 4, height - 4), fill="#1DB954")
    # Point central ou symbole
    dc.ellipse((22, 22, width - 22, height - 22), fill="#FFFFFF")
    return image

def start_server():
    """Démarre le serveur Uvicorn FastAPI dans un thread séparé."""
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="error")

def open_browser(icon, item):
    """Ouvre l interface Web Shazify dans le navigateur par défaut."""
    webbrowser.open(SERVER_URL)

def open_csv(icon, item):
    """Ouvre le fichier history.csv s il existe."""
    if os.path.exists(CSV_FILE):
        os.startfile(CSV_FILE)
    else:
        print("Aucun fichier d historique CSV trouvé pour le moment.")

def quit_app(icon, item):
    """Arrête l icône de la barre des tâches et quitte l application."""
    icon.stop()
    sys.exit(0)

def main():
    # 1. Lancement du serveur FastAPI en arrière-plan
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # 2. Création du menu contextuel (clic droit)
    menu = (
        item("Ouvrir Shazify (Navigateur)", open_browser, default=True),
        item("Ouvrir l historique CSV", open_csv),
        pystray.Menu.SEPARATOR,
        item("Quitter Shazify", quit_app)
    )

    # 3. Lancement de l icône dans la barre des tâches
    icon = pystray.Icon("Shazify", create_icon_image(), "Shazify - Détection Audio", menu)
    icon.run()

if __name__ == "__main__":
    main()

