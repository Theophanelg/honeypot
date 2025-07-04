import threading
import time
from services.ssh_server import ssh_honeypot
from services.http_server import http_honeypot
from services.ftp_server import ftp_honeypot

def start_services():
    print("[*] Démarrage du service SSH (port 2222)...")
    ssh_thread = threading.Thread(target=ssh_honeypot, kwargs={"port": 2222}, daemon=True)
    ssh_thread.start()

    print("[*] Démarrage du service HTTP (port 8080)...")
    http_thread = threading.Thread(target=http_honeypot, daemon=True)
    http_thread.start()

    print("[*] Démarrage du service FTP (port 2121)...")
    ftp_thread = threading.Thread(target=ftp_honeypot, daemon=True)
    ftp_thread.start()

    # Tu peux ajouter d'autres services ici de la même façon

if __name__ == "__main__":
    print("===== Démarrage du honeypot multi-services =====")
    start_services()
    try:
        while True:
            time.sleep(1)  # Utilise un sleep pour ne pas charger le CPU
    except KeyboardInterrupt:
        print("\n[!] Honeypot arrêté par l'utilisateur")
