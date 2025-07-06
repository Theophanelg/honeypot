import socket
import threading
import datetime
import os
import time
from typing import Optional, List
from utils.logger import log_attack

# Ce module simule un serveur SSH interactif avec un système de fichiers factice.
# Il journalise les commandes utilisateur et fournit des réponses limitées.

# Les systèmes de fichiers sont des variables globales manipulées directement par les fonctions.
fake_fs = {
    "/": ["home", "etc", "var"],
    "/home": ["user"],
    "/home/user": ["notes.txt", "secrets.txt"],
    "/etc": ["passwd"],
}

file_contents = {
    "/home/user/notes.txt": "ToDo:\n- buy milk\n- hack NASA",
    "/home/user/secrets.txt": "NASA login: admin / password123",
    "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000::/home/user:/bin/bash"
}

def safe_path_join(base: str, target: str) -> Optional[str]:
    """
    Joint les chemins en toute sécurité pour le système de fichiers factice, prévenant la traversée de répertoire.
    """
    target = os.path.normpath(target).lstrip("/")
    new_path = os.path.normpath(os.path.join(base, target))
    if not new_path.startswith("/"):
        new_path = "/" + new_path
    for path in fake_fs:
        if new_path == path or new_path.startswith(path + "/"):
            return new_path
    return None

def handle_client(client_socket: socket.socket, address: tuple):
    """
    Gère une connexion client SSH entrante, simulant un shell interactif.
    Journalise toutes les commandes tentées par le client.
    """
    ip, port = address
    print(f"[+] Connexion SSH simulée de {ip}")
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/ssh_{ip}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    try:
        client_socket.sendall(b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3\r\n")
        time.sleep(0.2)
        client_socket.sendall(b"login: ")
        client_socket.recv(1024)
        client_socket.sendall(b"Password: ")
        client_socket.recv(1024)

        client_socket.sendall(b"\nWelcome to Ubuntu 22.04 LTS (GNU/Linux 5.15 x86_64)\n\n")
        current_dir = "/home/user"

        while True:
            prompt = f"user@honeypot:{current_dir}$ ".encode()
            client_socket.sendall(prompt)
            
            output_payload = ""
            try:
                cmd = client_socket.recv(1024).decode(errors="ignore").strip()
                if not cmd:
                    break
            except (ConnectionResetError, BrokenPipeError):
                log_attack(ip, port, "SSH", "Déconnexion brutale", output_content="Déconnexion brutale")
                break

            with open(log_file, "a") as f:
                f.write(f"[{datetime.datetime.now()}] {ip} > {cmd}\n")

            if cmd in ("exit", "logout"):
                output_payload = "logout\nConnection closed.\n"
                client_socket.sendall(output_payload.encode())
                log_attack(ip, port, "SSH", cmd, output_content=output_payload.strip())
                break

            elif cmd == "cd":
                current_dir = "/home/user"
                log_attack(ip, port, "SSH", cmd, output_content="")
                time.sleep(0.1)

            elif cmd.startswith("cd "):
                target = cmd[3:].strip()
                new_path = safe_path_join(current_dir, target)
                if new_path and new_path in fake_fs:
                    current_dir = new_path
                    output_payload = ""
                else:
                    output_payload = "No such directory\n"
                    client_socket.sendall(output_payload.encode())
                log_attack(ip, port, "SSH", cmd, output_content=output_payload.strip())
                time.sleep(0.1)

            elif cmd == "ls":
                files = fake_fs.get(current_dir, [])
                output_payload = "  ".join(files) + "\r\n\r\n"
                client_socket.sendall(output_payload.encode())
                log_attack(ip, port, "SSH", cmd, output_content=output_payload.strip())
                time.sleep(0.1)

            elif cmd.startswith("cat "):
                path = os.path.normpath(os.path.join(current_dir, cmd[4:].strip()))
                if path in file_contents:
                    output_payload = file_contents[path] + "\n"
                    client_socket.sendall(output_payload.encode())
                else:
                    output_payload = "No such file\n"
                    client_socket.sendall(output_payload.encode())
                log_attack(ip, port, "SSH", cmd, output_content=output_payload.strip())
                time.sleep(0.1)

            elif cmd == "pwd":
                output_payload = current_dir + "\n"
                client_socket.sendall(output_payload.encode())
                log_attack(ip, port, "SSH", cmd, output_content=output_payload.strip())
                time.sleep(0.1)

            elif cmd == "whoami":
                output_payload = "user\n"
                client_socket.sendall(output_payload.encode())
                log_attack(ip, port, "SSH", cmd, output_content=output_payload.strip())
                time.sleep(0.1)

            elif cmd == "id":
                output_payload = "uid=1000(user) gid=1000(user) groups=1000(user)\n"
                client_socket.sendall(output_payload.encode())
                log_attack(ip, port, "SSH", cmd, output_content=output_payload.strip())
                time.sleep(0.1)

            elif cmd.startswith("echo "):
                output_payload = cmd[5:].strip() + "\n"
                client_socket.sendall(output_payload.encode())
                log_attack(ip, port, "SSH", cmd, output_content=output_payload.strip())
                time.sleep(0.1)

            elif cmd.startswith("mkdir "):
                dir_name = cmd[6:].strip()
                new_dir_path = safe_path_join(current_dir, dir_name)
                if new_dir_path and new_dir_path not in fake_fs:
                    fake_fs[new_dir_path] = []
                    parent_dir = os.path.dirname(new_dir_path)
                    parent_dir_name = parent_dir if parent_dir != "/" else "/"
                    if parent_dir_name in fake_fs and dir_name not in fake_fs[parent_dir_name]:
                        fake_fs[parent_dir_name].append(dir_name)
                        fake_fs[parent_dir_name].sort()
                    output_payload = ""
                else:
                    output_payload = "mkdir: cannot create directory '" + dir_name + "': File exists or invalid path\n"
                    client_socket.sendall(output_payload.encode())
                log_attack(ip, port, "SSH", cmd, output_content=output_payload.strip())
                time.sleep(0.1)

            elif cmd.startswith("rm "):
                target_name = cmd[3:].strip()
                target_path = safe_path_join(current_dir, target_name)
                
                if target_path and (target_path in fake_fs or target_path in file_contents):
                    if target_path in file_contents:
                        del file_contents[target_path]
                        parent_dir_path = os.path.dirname(target_path)
                        if parent_dir_path in fake_fs and target_name in fake_fs[parent_dir_path]:
                            fake_fs[parent_dir_path].remove(target_name)
                        output_payload = ""
                    elif target_path in fake_fs and not fake_fs[target_path]:
                        del fake_fs[target_path]
                        parent_dir_path = os.path.dirname(target_path)
                        parent_dir_name = parent_dir_path if parent_dir_path != "/" else "/"
                        if parent_dir_name in fake_fs and target_name in fake_fs[parent_dir_name]:
                            fake_fs[parent_dir_name].remove(target_name)
                        output_payload = ""
                    else:
                        output_payload = "rm: cannot remove '" + target_name + "': Is a directory (or not empty)\n"
                        client_socket.sendall(output_payload.encode())
                else:
                    output_payload = "rm: cannot remove '" + target_name + "': No such file or directory\n"
                    client_socket.sendall(output_payload.encode())
                log_attack(ip, port, "SSH", cmd, output_content=output_payload.strip())
                time.sleep(0.1)

            elif cmd == "":
                continue

            else:
                output_payload = "command not found\n"
                client_socket.sendall(output_payload.encode())
                log_attack(ip, port, "SSH", cmd, output_content=output_payload.strip())
                time.sleep(0.1)

    except Exception as e:
        print(f"[!] Erreur avec {ip} : {e}")
        log_attack(ip, port, "SSH", f"Erreur : {e}", output_content=str(e).strip())
    finally:
        client_socket.close()
        print(f"[-] Déconnexion de {ip}")
        log_attack(ip, port, "SSH", "Déconnexion", output_content="Déconnexion")

def ssh_honeypot(port=2222):
    """
    Démarre le honeypot SSH, écoutant les connexions entrantes.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", port))
    except PermissionError:
        print(f"Permission refusée pour ouvrir le port {port}. Utilise un port >1024 ou lance avec sudo.")
        return
    server.listen(10)
    print(f"Honeypot SSH en écoute sur le port {port}...")

    try:
        while True:
            client_sock, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("Arrêt du honeypot SSH.")
    finally:
        server.close()

if __name__ == "__main__":
    ssh_honeypot(port=2222)