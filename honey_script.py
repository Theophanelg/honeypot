import socket
import threading
import logging
import sqlite3
import json
import os

# Configuration du logging pour enregistrer les tentatives d'attaques
logging.basicConfig(filename="honeypot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Initialisation de la base de données SQLite pour stocker les attaques
conn = sqlite3.connect("honeypot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS attacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    port INTEGER,
    service TEXT,
    data TEXT,
    data_type TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def analyze_data(data):
    """ Détermine le type de données reçues en fonction du contenu """
    try:
        json.loads(data)
        return "JSON"
    except json.JSONDecodeError:
        pass
    
    if "password" in data.lower() or "login" in data.lower():
        return "Credentials"
    elif "GET" in data or "POST" in data:
        return "HTTP Request"
    elif any(c.isdigit() for c in data) and ":" in data:
        return "Possible IP Address"
    else:
        return "Unknown"

def log_attack(ip, port, service, data):
    """ Enregistre une attaque dans les logs et la base de données """
    data_type = analyze_data(data)
    logging.info(f"{service} attack from {ip}:{port} -> {data} (Type: {data_type})")
    cursor.execute("INSERT INTO attacks (ip, port, service, data, data_type) VALUES (?, ?, ?, ?, ?)", (ip, port, service, data, data_type))
    conn.commit()

def ssh_honeypot():
    """ Simule un serveur SSH vulnérable """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.19.144", 22))
    server_socket.listen(5)
    print("Honeypot SSH en écoute sur le port 22...")
    while True:
        client_socket, addr = server_socket.accept()
        log_attack(addr[0], addr[1], "SSH", "Tentative de connexion")
        client_socket.send(b"SSH-2.0-OpenSSH_7.9p1 Debian-10\n")
        data = client_socket.recv(1024).decode(errors='ignore')
        log_attack(addr[0], addr[1], "SSH", data)
        client_socket.close()

def http_honeypot():
    """ Simule un serveur HTTP vulnérable """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.19.144", 80))
    server_socket.listen(5)
    print("Honeypot HTTP en écoute sur le port 80...")
    while True:
        client_socket, addr = server_socket.accept()
        request = client_socket.recv(1024).decode(errors='ignore')
        log_attack(addr[0], addr[1], "HTTP", request)
        response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n<h1>Bienvenue</h1>"
        client_socket.send(response.encode())
        client_socket.close()

def ftp_honeypot():
    """ Simule un serveur FTP vulnérable """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.19.144", 21))
    server_socket.listen(5)
    print("Honeypot FTP en écoute sur le port 21...")
    while True:
        client_socket, addr = server_socket.accept()
        log_attack(addr[0], addr[1], "FTP", "Tentative de connexion")
        client_socket.send(b"220 Fake FTP Server\n")
        data = client_socket.recv(1024).decode(errors='ignore')
        log_attack(addr[0], addr[1], "FTP", data)
        client_socket.close()

def start_honeypot():
    """ Démarre les différents services du honeypot en parallèle """
    threading.Thread(target=ssh_honeypot).start()
    threading.Thread(target=http_honeypot).start()
    threading.Thread(target=ftp_honeypot).start()
    print("Honeypot démarré...")

if __name__ == "__main__":
    start_honeypot()

