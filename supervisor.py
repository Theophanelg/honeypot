import subprocess
import os
import sys
import time
import threading
import signal

services = {
    "ssh": "services/ssh_server.py",
    "http": "services/http_server.py",
    "ftp": "services/ftp_server.py",
}

processes = {}

def start_service(name, path):
    print(f"[+] Démarrage service {name}")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    # Chaque service a son propre fichier log pour la sortie standard/erreur
    log_file = open(f"logs/{name}_service.log", "a")
    proc = subprocess.Popen(
        [sys.executable, path],
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT
    )
    processes[name] = (proc, log_file)

def stop_services():
    print("\n[!] Arrêt de tous les services...")
    for name, (proc, log_file) in processes.items():
        if proc.poll() is None:
            print(f"[~] Arrêt du service {name}")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        log_file.close()

def monitor_services():
    crash_count = {name: 0 for name in services}
    while True:
        for name, path in services.items():
            proc, _ = processes.get(name, (None, None))
            if proc is None or proc.poll() is not None:
                crash_count[name] += 1
                print(f"[!] {name} arrêté ({crash_count[name]} crash). Relance...")
                if crash_count[name] > 5:
                    print(f"[X] {name} crash trop souvent ! Relance arrêtée temporairement.")
                    continue
                start_service(name, path)
        time.sleep(10)

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    for name, path in services.items():
        start_service(name, path)

    monitor_thread = threading.Thread(target=monitor_services, daemon=True)
    monitor_thread.start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        stop_services()
        print("[~] Supervisor arrêté.")
