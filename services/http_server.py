import socket
import threading
import time
from utils.logger import log_attack
# Ce module simule un serveur HTTP basique pour servir de honeypot.
# Il répond à toutes les requêtes HTTP avec une page HTML simple
# et enregistre les requêtes complètes des clients.

HTTP_PORT = 8080 # Port sur lequel le honeypot HTTP écoute.

RESPONSE = b"""HTTP/1.1 200 OK\r
Server: Apache/2.4.41 (Ubuntu)\r
Content-Type: text/html\r
\r
<html>
<head><title>It works!</title></head>
<body><h1>Welcome to Fake HTTP Honeypot</h1></body>
</html>
"""

def handle_client(client_socket: socket.socket, addr: tuple):
    """
    Gère une connexion client HTTP entrante, journalise la requête complète
    et envoie une réponse statique.
    """
    try:
        data = client_socket.recv(4096).decode(errors='ignore') # Récupère la requête complète
        if data:
            request_line = data.splitlines()[0] if data else "EMPTY"
            # log_attack avec la requête complète comme 'data' et la réponse comme 'output_content'
            log_attack(addr[0], addr[1], "HTTP", data, method="GET", output_content=RESPONSE.decode(errors='ignore').strip())
        
        time.sleep(0.3)
        client_socket.sendall(RESPONSE)
    except Exception as e:
        log_attack(addr[0], addr[1], "HTTP", f"Erreur: {e}", output_content=str(e).strip())
    finally:
        client_socket.close()

def http_honeypot():
    """
    Démarre le honeypot HTTP, écoutant les connexions entrantes sur le port configuré.
    Chaque nouvelle connexion est gérée dans un thread séparé.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind(("0.0.0.0", HTTP_PORT))
    except PermissionError:
        print(f"Permission refusée pour ouvrir le port {HTTP_PORT}. Essaye en root ou choisis un port >1024.")
        return
    server_socket.listen(10)
    print(f"Honeypot HTTP en écoute sur le port {HTTP_PORT}...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Arrêt du honeypot HTTP.")
    except Exception as e:
        print(f"Erreur accept: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    http_honeypot()