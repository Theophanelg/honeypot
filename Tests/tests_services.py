import socket
import time
import sqlite3
import os

# Ports à adapter si besoin
HONEY_SSH_PORT = 2222
HONEY_HTTP_PORT = 8080
HONEY_FTP_PORT = 2121

# ===============================
#   BLOC 1 : TESTS UNITAIRES
# ===============================

def test_analyze_data_json():
    from utils.analyzer import analyze_data
    assert analyze_data('{"key": 1}') == "JSON"

def test_analyze_data_credentials():
    from utils.analyzer import analyze_data
    assert analyze_data('login=admin&password=test') == "Credentials"

def test_safe_path_join():
    from services.ssh_server import safe_path_join
    assert safe_path_join("/home/user", "../etc") == "/etc"
    assert safe_path_join("/home/user", "../../../../passwd") is None

# ===============================
#   BLOC 2 : TESTS FONCTIONNELS
# ===============================

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

def test_http_connection():
    """Teste la réponse HTTP du honeypot."""
    assert wait_for_port(HONEY_HTTP_PORT), f"Le service HTTP ne répond pas sur le port {HONEY_HTTP_PORT}"
    s = socket.socket()
    s.connect(("localhost", HONEY_HTTP_PORT))
    s.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
    data = s.recv(1024).decode()
    assert "HTTP/1.1 200 OK" in data and "Fake HTTP" in data, "Réponse HTTP incorrecte"
    s.close()

def test_ftp_connection():
    """Teste la bannière FTP du honeypot."""
    assert wait_for_port(HONEY_FTP_PORT), f"Le service FTP ne répond pas sur le port {HONEY_FTP_PORT}"
    s = socket.socket()
    s.connect(("localhost", HONEY_FTP_PORT))
    data = s.recv(1024).decode()
    assert "220" in data or "FTP" in data, "Réponse FTP incorrecte"
    s.close()

def test_webapp_index():
    """Teste que la page d'accueil Flask répond bien."""
    import requests
    r = requests.get("http://localhost:5000/")
    assert r.status_code == 200
    assert "Logs" in r.text or "Honeypot" in r.text

# ===============================
#   BLOC 3 : TESTS DE NON-RÉGRESSION
# ===============================

def test_db_log_insert_and_filter():
    """Teste insert log puis filtrage par date/service/IP."""
    from utils.logger import log_attack
    test_ip = "192.168.56.56"
    log_attack(test_ip, HONEY_SSH_PORT, "SSH", "Non-regression test")
    from utils.db import get_filtered_logs
    logs = get_filtered_logs(ip=test_ip, service="SSH")
    assert any(log["ip"] == test_ip for log in logs)
    conn = sqlite3.connect("honeypot.db")
    c = conn.cursor()
    c.execute("DELETE FROM attacks WHERE ip=?", (test_ip,))
    conn.commit()
    conn.close()

# ===============================
#   BLOC 4 : TESTS RÉPUTATION IP
# ===============================

def test_ip_reputation_integration():
    """Teste la récupération et stockage réputation AbuseIPDB."""
    from utils.ip_reputation import check_ip_reputation
    test_ip = "8.8.8.8"
    score = check_ip_reputation(test_ip)
    conn = sqlite3.connect("honeypot.db")
    c = conn.cursor()
    c.execute("SELECT abuse_score FROM ip_reputation WHERE ip=?", (test_ip,))
    row = c.fetchone()
    conn.close()
    assert row is not None, "Score de réputation non stocké"
    if score is not None:
        assert int(row[0]) == score

# ===============================
#   BLOC 5 : TESTS ROBUSTESSE ET SÉCURITÉ
# ===============================

def test_blacklist_threshold():
    """Teste l'ajout à la blacklist après flood (sans manipuler iptables)."""
    from utils.logger import log_attack
    test_ip = "10.10.10.10"
    for _ in range(50):
        log_attack(test_ip, HONEY_SSH_PORT, "SSH", "Flood test")
    conn = sqlite3.connect("honeypot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blacklist WHERE ip=?", (test_ip,))
    result = cursor.fetchone()
    assert result is not None, f"{test_ip} non trouvée dans la table blacklist"
    cursor.execute("DELETE FROM blacklist WHERE ip=?", (test_ip,))
    cursor.execute("DELETE FROM attacks WHERE ip=?", (test_ip,))
    conn.commit()
    conn.close()

def test_failover_supervisor():
    """Teste que supervisor relance un service tombé (manuel/bonus)."""
    # Nécessite de lancer supervisor.py séparément
    pass 

# ===============================
#   LANCEMENT DE TOUS LES TESTS
# ===============================

if __name__ == "__main__":
    print("== Tests unitaires ==")
    test_analyze_data_json(); print("test_analyze_data_json OK")
    test_analyze_data_credentials(); print("test_analyze_data_credentials OK")
    test_safe_path_join(); print("test_safe_path_join OK")

    print("== Tests fonctionnels ==")
    test_ssh_connection(); print("test_ssh_connection OK")
    test_http_connection(); print("test_http_connection OK")
    test_ftp_connection(); print("test_ftp_connection OK")
    test_webapp_index(); print("test_webapp_index OK")

    print("== Tests non-régression ==")
    test_db_log_insert_and_filter(); print("test_db_log_insert_and_filter OK")

    print("== Tests réputation ==")
    test_ip_reputation_integration(); print("test_ip_reputation_integration OK")

    print("== Tests robustesse ==")
    test_blacklist_threshold(); print("test_blacklist_threshold OK")

    print("== Tous les tests principaux sont passés ! ==")
