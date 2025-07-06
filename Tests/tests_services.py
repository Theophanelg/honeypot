import socket
import time
import sqlite3
import os

HONEY_SSH_PORT = 2222

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
    """Teste la bannière SSH du honeypot sur le port custom."""
    assert wait_for_port(HONEY_SSH_PORT), f"Le service SSH ne répond pas sur le port {HONEY_SSH_PORT}"
    s = socket.socket()
    s.connect(("localhost", HONEY_SSH_PORT))
    banner = s.recv(1024).decode()
    assert "SSH" in banner, "Bannière SSH manquante"
    s.close()

def test_logger_db_inserts():
    """Teste l'insertion d'une attaque dans la BDD."""
    from utils.logger import log_attack
    test_ip = "192.168.1.123"
    log_attack(test_ip, HONEY_SSH_PORT, "SSH", "Test log")

    conn = sqlite3.connect("honeypot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attacks WHERE ip=?", (test_ip,))
    result = cursor.fetchone()
    assert result is not None, "Aucune entrée dans la table attacks pour le test"
    # Nettoyage
    cursor.execute("DELETE FROM attacks WHERE ip=?", (test_ip,))
    conn.commit()
    conn.close()

def test_blacklist_threshold():
    """Teste l'ajout à la blacklist après flood (sans manipuler iptables)."""
    from utils.logger import log_attack
    test_ip = "10.10.10.10"
    # Simule 50 tentatives
    for _ in range(50):
        log_attack(test_ip, HONEY_SSH_PORT, "SSH", "Flood test")

    # Vérifie si l'IP est dans la table blacklist (ne touche pas à iptables)
    conn = sqlite3.connect("honeypot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blacklist WHERE ip=?", (test_ip,))
    result = cursor.fetchone()
    assert result is not None, f"{test_ip} non trouvée dans la table blacklist"
    # Nettoyage
    cursor.execute("DELETE FROM blacklist WHERE ip=?", (test_ip,))
    cursor.execute("DELETE FROM attacks WHERE ip=?", (test_ip,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    test_ssh_connection()
    print("test_ssh_connection OK")
    test_logger_db_inserts()
    print("test_logger_db_inserts OK")
    test_blacklist_threshold()
    print("test_blacklist_threshold OK")
