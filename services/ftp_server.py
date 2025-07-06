import socket
import threading
import time
from utils.logger import log_attack
from typing import Dict, List, Any, Optional

# Ce module simule un serveur FTP basique et interactif pour servir de honeypot.
# Il simule des réponses de connexion, permet une "connexion réussie" pour certains identifiants,
# et gère quelques commandes FTP post-login.

FTP_PORT = 2121

FTP_BANNER = b"220 (vsFTPd 3.0.3)\r\n"

VALID_FTP_CREDS: Dict[str, str] = {
    "user": "password",
    "admin": "admin123",
    "anonymous": ""
}

FTP_FAKE_FILES: Dict[str, List[str]] = {
    "/": ["home", "pub"],
    "/home": ["welcome.txt"],
    "/pub": ["software_update.zip", "README.txt"]
}

FTP_FILE_CONTENTS: Dict[str, str] = {
    "/home/welcome.txt": "Bienvenue sur le serveur FTP.\n",
    "/pub/README.txt": "Ceci est un fichier public.\n"
}


def handle_ftp_client(client_socket: socket.socket, addr: tuple):
    ip = addr[0]
    port = addr[1]
    
    current_ftp_user = ""
    authenticated = False
    
    try:
        log_attack(ip, port, "FTP", "Tentative de connexion", output_content=FTP_BANNER.decode(errors='ignore').strip())
        client_socket.sendall(FTP_BANNER)
        time.sleep(0.5)

        while True:
            raw_data_received = client_socket.recv(1024)
            
            # --- LIGNES DE DEBUG FTP TEMPORAIRES (maintenues) ---
            print(f"DEBUG FTP: Raw data received: {raw_data_received!r}")
            if not raw_data_received:
                print("DEBUG FTP: Received empty data, client disconnected.")
                break
            
            original_data_str = raw_data_received.decode(errors='ignore').strip()
            print(f"DEBUG FTP: Decoded and stripped original data: '{original_data_str}'")

            command_parts_upper = original_data_str.upper().split(' ', 1)
            cmd = command_parts_upper[0]
            arg = ""
            if len(command_parts_upper) > 1:
                arg = original_data_str.split(' ', 1)[1]
            
            print(f"DEBUG FTP: Parsed command: '{cmd}', argument: '{arg}'")
            # --- FIN LIGNES DE DEBUG FTP TEMPORAIRES ---

            log_attack(ip, port, "FTP", original_data_str, output_content=original_data_str)

            if cmd == "USER":
                current_ftp_user = arg
                client_socket.sendall(b"331 Please specify the password.\r\n")
                log_attack(ip, port, "FTP", f"USER {current_ftp_user}", output_content="331 Please specify the password.")
            elif cmd == "PASS":
                if current_ftp_user in VALID_FTP_CREDS and VALID_FTP_CREDS[current_ftp_user] == arg:
                    authenticated = True
                    client_socket.sendall(b"230 User logged in, proceed.\r\n")
                    log_attack(ip, port, "FTP", f"PASS {arg}", output_content="230 User logged in, proceed.")
                else:
                    client_socket.sendall(b"530 Login incorrect.\r\n")
                    log_attack(ip, port, "FTP", f"PASS {arg}", output_content="530 Login incorrect.")
            elif cmd == "QUIT":
                client_socket.sendall(b"221 Goodbye.\r\n")
                log_attack(ip, port, "FTP", "QUIT", output_content="221 Goodbye.")
                break

            elif authenticated:
                if cmd == "SYST":
                    client_socket.sendall(b"215 UNIX Type: L8\r\n")
                    log_attack(ip, port, "FTP", "SYST", output_content="215 UNIX Type: L8")
                elif cmd == "FEAT":
                    client_socket.sendall(b"211-Features:\r\n EPRT\r\n EPSV\r\n MDTM\r\n PASV\r\n REST STREAM\r\n SIZE\r\n TVFS\r\n UTF8\r\n211 End\r\n")
                    log_attack(ip, port, "FTP", "FEAT", output_content="211 Features")
                elif cmd == "PWD" or cmd == "XPWD":
                    client_socket.sendall(b'257 "/" is the current directory.\r\n')
                    log_attack(ip, port, "FTP", cmd, output_content='257 "/" is the current directory.')
                elif cmd == "TYPE":
                    client_socket.sendall(b"200 Type set to I.\r\n")
                    log_attack(ip, port, "FTP", cmd, output_content="200 Type set to I")
                # MODIFICATION ICI : Gère PASV et EPSV différemment et utilise la vraie IP
                elif cmd == "PASV":
                    # Utilise l'IP du honeypot (addr[0])
                    ip_parts = ip.split('.')
                    # Simule un port, par exemple 100*256+20 = 25620
                    # Pourrait être un port aléatoire ou configuré
                    port_p1 = 100
                    port_p2 = 20
                    pasv_response = f"227 Entering Passive Mode ({ip_parts[0]},{ip_parts[1]},{ip_parts[2]},{ip_parts[3]},{port_p1},{port_p2}).\r\n"
                    client_socket.sendall(pasv_response.encode())
                    log_attack(ip, port, "FTP", cmd, output_content=pasv_response.strip())
                elif cmd == "EPSV":
                    # Réponse pour Extended Passive Mode (EPSV)
                    # Le format est "229 Entering Extended Passive Mode (|||port|)"
                    # Simule le même port que PASV pour simplicité
                    port_epsv = 25620 # Le port 100*256+20
                    epsv_response = f"229 Entering Extended Passive Mode (|||{port_epsv}|)\r\n"
                    client_socket.sendall(epsv_response.encode())
                    log_attack(ip, port, "FTP", cmd, output_content=epsv_response.strip())
                elif cmd == "LIST" or cmd == "NLST":
                    files = FTP_FAKE_FILES.get("/", [])
                    output_list = "\r\n".join([f"-rw-r--r--    1 user     group         1234 Jan 01 2025 {f}" for f in files]) + "\r\n"
                    client_socket.sendall(b"150 Here comes the directory listing.\r\n")
                    time.sleep(0.1)
                    client_socket.sendall(output_list.encode())
                    client_socket.sendall(b"226 Directory send OK.\r\n")
                    log_attack(ip, port, "FTP", cmd, output_content="Directory listing sent.")
                else:
                    client_socket.sendall(b"202 Command not implemented, superfluous at this site.\r\n")
                    log_attack(ip, port, "FTP", cmd, output_content="202 Command not implemented")
            else:
                client_socket.sendall(b"530 Not logged in.\r\n")
                log_attack(ip, port, "FTP", cmd, output_content="530 Not logged in.")
            
            time.sleep(0.1)

    except Exception as e:
        log_attack(ip, port, "FTP", f"Erreur: {e}", output_content=str(e))
    finally:
        client_socket.close()
        log_attack(ip, port, "FTP", "Déconnexion", output_content="Disconnected by client")


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