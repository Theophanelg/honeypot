import socket
import threading
import time
from utils.logger import log_attack

HTTP_PORT = 8080  # Utilise 80 uniquement en root

RESPONSE = b"""HTTP/1.1 200 OK\r
Server: Apache/2.4.41 (Ubuntu)\r
Content-Type: text/html\r
\r
<html>
<head><title>It works!</title></head>
<body><h1>Welcome to Fake HTTP Honeypot</h1></body>
</html>
"""

def handle_client(client_socket, addr):
    try:
        # Récupère la requête
        data = client_socket.recv(4096).decode(errors='ignore')
        if data:
            request_line = data.splitlines()[0] if data else "EMPTY"
            log_attack(addr[0], addr[1], "HTTP", f"Requête : {request_line}")
        time.sleep(0.3)  # Simule un délai de réponse réaliste
        client_socket.sendall(RESPONSE)
    except Exception as e:
        log_attack(addr[0], addr[1], "HTTP", f"Erreur : {e}")
    finally:
        client_socket.close()

def http_honeypot():
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
            # Un thread par client
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Arrêt du honeypot HTTP.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    http_honeypot()
