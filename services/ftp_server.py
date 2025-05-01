import socket
from common.logger import log_attack

def ftp_honeypot():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 21))
    server_socket.listen(5)
    print("Honeypot FTP en écoute sur le port 21...")
    while True:
        client_socket, addr = server_socket.accept()
        log_attack(addr[0], addr[1], "FTP", "Tentative de connexion")
        client_socket.send(b"220 Fake FTP Server\n")
        data = client_socket.recv(1024).decode(errors='ignore')
        log_attack(addr[0], addr[1], "FTP", data)
        client_socket.close()