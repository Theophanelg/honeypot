import socket
import threading
import time
from utils.logger import log_attack

FTP_PORT = 2121  # Change en 21 si tu veux vraiment tester comme "root"

def handle_ftp_client(client_socket, addr):
    try:
        log_attack(addr[0], addr[1], "FTP", "Tentative de connexion")
        client_socket.sendall(b"220 Fake FTP Server ready.\r\n")
        time.sleep(0.5)  # Simule un vrai délai

        # Boucle de dialogue minimale, simule un login
        data = client_socket.recv(1024).decode(errors='ignore')
        if data:
            log_attack(addr[0], addr[1], "FTP", data.strip())
            # Simule réponse au USER
            if data.upper().startswith("USER"):
                client_socket.sendall(b"331 Please specify the password.\r\n")
                time.sleep(0.5)
                data = client_socket.recv(1024).decode(errors='ignore')
                log_attack(addr[0], addr[1], "FTP", data.strip())
                client_socket.sendall(b"530 Login incorrect.\r\n")
        client_socket.close()
        log_attack(addr[0], addr[1], "FTP", "Déconnexion")
    except Exception as e:
        log_attack(addr[0], addr[1], "FTP", f"Erreur: {e}")
        try:
            client_socket.close()
        except Exception:
            pass

def ftp_honeypot():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind(("0.0.0.0", FTP_PORT))
    except PermissionError:
        print(f"Permission refusée pour ouvrir le port {FTP_PORT}. Essaye en root ou utilise un port >1024.")
        return
    server_socket.listen(10)
    print(f"Honeypot FTP en écoute sur le port {FTP_PORT}...")

    while True:
        try:
            client_socket, addr = server_socket.accept()
            # Un thread par client pour ne pas bloquer le serveur
            threading.Thread(target=handle_ftp_client, args=(client_socket, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("Arrêt du honeypot FTP.")
            break
        except Exception as e:
            print(f"Erreur accept: {e}")

    server_socket.close()

if __name__ == "__main__":
    ftp_honeypot()
