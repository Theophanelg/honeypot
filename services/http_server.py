import socket
from common.logger import log_attack

def http_honeypot():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 80))
    server_socket.listen(5)
    print("Honeypot HTTP en écoute sur le port 80...")
    while True:
        client_socket, addr = server_socket.accept()
        request = client_socket.recv(1024).decode(errors='ignore')
        log_attack(addr[0], addr[1], "HTTP", request)
        response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n<h1>Bienvenue</h1>"
        client_socket.send(response.encode())
        client_socket.close()