import socket
import time
import sqlite3
import os

def wait_for_port(port, timeout=5):
    """Attend que le port soit disponible."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return True
        except:
            time.sleep(0.5)
    return False

def test_ssh_connection():
    assert wait_for_port(22), "Le service SSH ne répond pas"

    s = socket.socket()
    s.connect(("localhost", 22))
    banner = s.recv(1024).decode()
    assert "SSH" in banner, "Bannière SSH manquante"
    s.close()

def test_logger_db_inserts():
    from utils.logger import log_attack
    test_ip = "192.168.1.123"
    log_attack(test_ip, 22, "SSH", "Test log")

    conn = sqlite3.connect("honeypot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs WHERE ip=?", (test_ip,))
    result = cursor.fetchone()
    assert result is not None, "Aucune entrée dans les logs pour le test"
    conn.close()

def test_blacklist_threshold():
    from utils.logger import log_attack
    test_ip = "10.10.10.10"
    # Simule 50 tentatives
    for _ in range(50):
        log_attack(test_ip, 22, "SSH", "Flood test")

    # Vérifie si iptables contient la règle (nécessite sudo)
    result = os.popen(f"sudo iptables -L INPUT -n | grep {test_ip}").read()
    assert test_ip in result, f"{test_ip} non trouvée dans iptables"
