import logging
from utils.analyzer import analyze_data
from utils.db import get_db
from colorama import Fore, Style
import re
import json
from urllib.parse import urlparse, parse_qs
from utils.ip_reputation import check_ip_reputation
import sqlite3
from datetime import datetime, timedelta
import os

def setup_logger():
    log_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    file_handler = logging.FileHandler('honeypot.log')
    file_handler.setFormatter(log_formatter)

    logger = logging.getLogger("honeypot")
    logger.setLevel(logging.INFO)

    # Pour éviter les handlers dupliqués si le script est rechargé
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

logger = setup_logger()

def log_attack(ip, port, service, data, method="GET"):
    data_type = analyze_data(data)

    # Couleur console
    if service == "SSH":
        color = Fore.RED
    elif service == "HTTP":
        color = Fore.BLUE
    elif service == "FTP":
        color = Fore.MAGENTA
    else:
        color = Fore.WHITE

    # Affichage console coloré, log fichier en brut
    log_console = f"{color}{service} attack from {ip}:{port} -> {data} (Type: {data_type}){Style.RESET_ALL}"
    log_file = f"{service} attack from {ip}:{port} -> {data} (Type: {data_type})"

    logger.info(log_console)
    # Ajoute explicitement dans le fichier sans colorama
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.emit(logging.LogRecord(
                name=logger.name, level=logging.INFO, pathname=__file__,
                lineno=0, msg=log_file, args=(), exc_info=None
            ))

    # Utilisation context manager pour chaque accès BDD
    try:
        with sqlite3.connect("honeypot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO attacks (ip, port, service, data, data_type) VALUES (?, ?, ?, ?, ?)",
                           (ip, port, service, data, data_type))

            if service == "HTTP":
                user_agent = extract_user_agent(data)
                if user_agent:
                    cursor.execute("INSERT INTO user_agents (ip, port, user_agent) VALUES (?, ?, ?)",
                                   (ip, port, user_agent))

                payload = extract_payload(data, method)
                if payload:
                    cursor.execute("INSERT INTO payloads (ip, port, service, payload) VALUES (?, ?, ?, ?)",
                                   (ip, port, service, payload))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Erreur insertion dans la BDD: {e}")

    # Vérifie la réputation de l’IP si pas déjà présente
    try:
        with sqlite3.connect("honeypot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM ip_reputation WHERE ip = ?", (ip,))
            if not cursor.fetchone():
                check_ip_reputation(ip)
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de réputation IP : {e}")

    # Suivi activité IP
    try:
        with sqlite3.connect("honeypot.db") as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute("SELECT count, last_seen FROM ip_activity WHERE ip = ?", (ip,))
            row = cursor.fetchone()

            if row:
                count, last_seen = row
                try:
                    last_seen = datetime.fromisoformat(last_seen)
                except Exception:
                    last_seen = now - timedelta(hours=1)
                if now - last_seen < timedelta(minutes=5):
                    count += 1
                else:
                    count = 1
            else:
                count = 1

            cursor.execute(
                "REPLACE INTO ip_activity (ip, count, last_seen) VALUES (?, ?, ?)",
                (ip, count, now.isoformat())
            )
            conn.commit()

            if count >= 50:
                logger.warning(f"[!] IP {ip} trop active. Ajout à la blacklist.")
                # Vérification iptables seulement si root, log au lieu d'exécuter si non root
                if os.geteuid() == 0:
                    os.system(f"iptables -A INPUT -s {ip} -j DROP")
                    logger.warning(f"IP {ip} bloquée via iptables.")
                else:
                    logger.warning(f"(Non root) Simulation de blocage iptables pour {ip}")

                cursor.execute(
                    "INSERT INTO blacklist (ip, blocked_at) VALUES (?, ?) ON CONFLICT(ip) DO UPDATE SET blocked_at = excluded.blocked_at",
                    (ip, now.isoformat()))
                conn.commit()
    except Exception as e:
        logger.error(f"Erreur suivi d’activité IP : {e}")

def extract_user_agent(data):
    match = re.search(r'User-Agent:\s*(.+)', data, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_payload(request_data, method):
    payload = ""
    if method == 'GET':
        match = re.search(r'GET\s+(\S+)', request_data)
        if match:
            url = match.group(1)
            parsed_url = urlparse(url)
            payload_dict = parse_qs(parsed_url.query)
            payload = json.dumps(payload_dict) if payload_dict else None
    elif method == 'POST':
        # Ici, tu peux améliorer l'extraction du vrai body POST
        payload = json.dumps(request_data)
    return payload
