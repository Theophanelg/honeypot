import threading
from services.ssh_server import ssh_honeypot
from services.http_server import http_honeypot
from services.ftp_server import ftp_honeypot


def start_services():
    threading.Thread(target=ssh_honeypot, daemon=True).start()
    threading.Thread(target=http_honeypot, daemon=True).start()
    threading.Thread(target=ftp_honeypot, daemon=True).start()

if __name__ == "__main__":
    print("Démarrage du honeypot...")
    start_services()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Honeypot arrêté par l'utilisateur")
