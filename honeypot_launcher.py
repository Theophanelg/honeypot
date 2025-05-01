import threading
from services.ssh_server import ssh_honeypot
from services.http_server import http_honeypot
from services.ftp_server import ftp_honeypot

if __name__ == "__main__":
    print("Démarrage du honeypot...")
    threading.Thread(target=ssh_honeypot).start()
    threading.Thread(target=http_honeypot).start()
    threading.Thread(target=ftp_honeypot).start()
