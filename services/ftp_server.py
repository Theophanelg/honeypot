import socket
import threading
import time
from utils.logger import log_attack # Utilise la fonction log_attack

# Ce module simule un serveur FTP basique pour servir de honeypot.
# Il écoute les connexions entrantes, simule un dialogue minimal (login),
# et enregistre les interactions des clients.

FTP_PORT = 2121 # Port sur lequel le honeypot FTP écoute.

def handle_ftp_client(client_socket: socket.socket, addr: tuple):
    """
    Gère une connexion client FTP entrante, simule des réponses FTP
    et journalise les interactions.
    """
    try:
        log_attack(addr[0], addr[1], "FTP", "Tentative de connexion", output_content="220 Fake FTP Server ready.")
        client_socket.sendall(b"220 Fake FTP Server ready.\r\n")
        time.sleep(0.5)

        data = client_socket.recv(1024).decode(errors='ignore')
        if data:
            # Enregistre la commande USER/PASS comme 'data' et 'output_content'
            log_attack(addr[0], addr[1], "FTP", data.strip(), output_content=data.strip())
            
            if data.upper().startswith("USER"):
                client_socket.sendall(b"331 Please specify the password.\r\n")
                time.sleep(0.5)
                
                data = client_socket.recv(1024).decode(errors='ignore')
                # Enregistre la commande PASS comme 'data' et 'output_content'
                log_attack(addr[0], addr[1], "FTP", data.strip(), output_content=data.strip())
                client_socket.sendall(b"530 Login incorrect.\r\n")
        
        client_socket.close()
        log_attack(addr[0], addr[1], "FTP", "Déconnexion", output_content="Disconnected by client")
    except Exception as e:
        log_attack(addr[0], addr[1], "FTP", f"Erreur: {e}", output_content=str(e))
        try:
            client_socket.close()
        except Exception:
            pass

def ftp_honeypot():
    """
    Démarre le honeypot FTP, écoutant les connexions entrantes sur le port configuré.
    Chaque nouvelle connexion est gérée dans un thread séparé.
    """
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
            threading.Thread(target=handle_ftp_client, args=(client_socket, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("Arrêt du honeypot FTP.")
            break
        except Exception as e:
            print(f"Erreur accept: {e}")

    server_socket.close()

if __name__ == "__main__":
    ftp_honeypot()