import subprocess
import os
import sys
import time
import threading

services = {
    "ssh": "services/ssh_server.py",
    "http": "services/http_server.py",
    "ftp": "services/ftp_server.py",
}

processes = {}

def start_service(name, path):
    print(f"[+] Démarrage service {name}")
    
    # Ajoute le dossier racine au PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()  # répertoire actuel = racine projet

    proc = subprocess.Popen(
        ["python3", path],
        env=env
    )
    processes[name] = proc

def monitor_services():
    while True:
        for name, path in services.items():
            proc = processes.get(name)
            if proc is None or proc.poll() is not None:
                print(f"[!] {name} arrêté. Relance...")
                start_service(name, path)
        time.sleep(10)

if __name__ == "__main__":
    for name, path in services.items():
        start_service(name, path)

    monitor_thread = threading.Thread(target=monitor_services)
    monitor_thread.daemon = True
    monitor_thread.start()

    while True:
        time.sleep(60)
