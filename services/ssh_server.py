import socket
from utils.logger import log_attack

def ssh_honeypot():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 22))
    server_socket.listen(5)
    print("Honeypot SSH en écoute sur le port 22...")
    while True:
        client_socket, addr = server_socket.accept()
        log_attack(addr[0], addr[1], "SSH", "Tentative de connexion")
        client_socket.send(b"SSH-2.0-OpenSSH_7.9p1 Debian-10\n")
        data = client_socket.recv(1024).decode(errors='ignore')
        log_attack(addr[0], addr[1], "SSH", data)
        client_socket.close()
