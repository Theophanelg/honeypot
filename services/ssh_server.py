import socket
import threading
import datetime
import os
from utils.logger import log_attack

fake_fs = {
    "/": ["home", "etc", "var"],
    "/home": ["user"],
    "/home/user": ["notes.txt", "secrets.txt"],
    "/etc": ["passwd"],
}

file_contents = {
    "/home/user/notes.txt": "ToDo:\n- buy milk\n- hack NASA",
    "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000::/home/user:/bin/bash"
}

def safe_path_join(base, target):
    new_path = os.path.normpath(os.path.join(base, target))
    if not new_path.startswith("/"):
        new_path = "/" + new_path
    for path in fake_fs:
        if new_path == path or new_path.startswith(path + "/"):
            return new_path
    return None

def handle_client(client_socket, address):
    ip = address[0]
    port = address[1]
    print(f"[+] Connexion SSH simulée de {ip}")
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/ssh_{ip}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    try:
        client_socket.sendall(b"login: ")
        client_socket.recv(1024)
        client_socket.sendall(b"Password: ")
        client_socket.recv(1024)

        client_socket.sendall(b"\nWelcome to Ubuntu 22.04 LTS (GNU/Linux 5.15 x86_64)\n\n")
        current_dir = "/home/user"

        while True:
            prompt = f"user@honeypot:{current_dir}$ ".encode()
            client_socket.sendall(prompt)
            cmd = client_socket.recv(1024).decode(errors="ignore").strip()

            with open(log_file, "a") as f:
                f.write(f"[{datetime.datetime.now()}] {ip} > {cmd}\n")

            log_attack(ip, 22, "SSH", cmd)  

            if cmd in ("exit", "logout"):
                break

            elif cmd.startswith("cd "):
                target = cmd[3:].strip()
                new_path = safe_path_join(current_dir, target)
                if new_path and new_path in fake_fs:
                    current_dir = new_path
                else:
                    client_socket.sendall(b"No such directory\n")

            elif cmd == "ls":
                files = fake_fs.get(current_dir, [])
                output = "  ".join(files) + "\r\n\r\n"
                client_socket.sendall(output.encode())

            elif cmd.startswith("cat "):
                path = os.path.normpath(os.path.join(current_dir, cmd[4:].strip()))
                if path in file_contents:
                    client_socket.sendall((file_contents[path] + "\n").encode())
                else:
                    client_socket.sendall(b"No such file\n")

            elif cmd == "pwd":
                client_socket.sendall((current_dir + "\n").encode())

            else:
                client_socket.sendall(b"command not found\n")

    except Exception as e:
        print(f"[!] Erreur avec {ip} : {e}")
    finally:
        client_socket.close()
        print(f"[-] Déconnexion de {ip}")


def ssh_honeypot(port=22):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"Honeypot SSH en écoute sur le port {port}...")

    while True:
        client_sock, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_sock, addr))
        thread.start()

if __name__ == "__main__":
    ssh_honeypot(port=2222)
