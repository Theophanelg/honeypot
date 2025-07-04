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

# Initialisation de la BDD SQLite
conn, cursor = get_db()

# Configuration du logger
def setup_logger():
    log_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    file_handler = logging.FileHandler('honeypot.log')
    file_handler.setFormatter(log_formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

logger = setup_logger()

# Fonction d'enregistrement des attaques
def log_attack(ip, port, service, data, method="GET"):
    data_type = analyze_data(data)

    # Attribution des couleurs
    if service == "SSH":
        color = Fore.RED
    elif service == "HTTP":
        color = Fore.BLUE
    elif service == "FTP":
        color = Fore.MAGENTA
    else:
        color = Fore.WHITE

    log_msg = f"{color}{service} attack from {ip}:{port} -> {data} (Type: {data_type}){Style.RESET_ALL}"
    logger.info(log_msg)

    try:
        cursor.execute("INSERT INTO attacks (ip, port, service, data, data_type) VALUES (?, ?, ?, ?, ?)",
                       (ip, port, service, data, data_type))
        conn.commit()

        if service == "HTTP":
            user_agent = extract_user_agent(data)
            if user_agent:
                cursor.execute("INSERT INTO user_agents (ip, port, user_agent) VALUES (?, ?, ?)",
                               (ip, port, user_agent))
                conn.commit()

            payload = extract_payload(data, method)
            if payload:
                cursor.execute("INSERT INTO payloads (ip, port, service, payload) VALUES (?, ?, ?, ?)",
                               (ip, port, service, payload))
                conn.commit()
    except Exception as e:
        logger.error(f"{Fore.RED}Erreur insertion dans la BDD: {e}{Style.RESET_ALL}")

    # Vérifie la réputation de l’IP si pas encore faite
    try:
        rep_conn = rep_cursor = get_db()
        rep_cursor = rep_conn.cursor()
        rep_cursor.execute("SELECT 1 FROM ip_reputation WHERE ip = ?", (ip,))
        if not rep_cursor.fetchone():
            check_ip_reputation(ip)
        rep_conn.close()
    except Exception as e:
        logger.error(f"{Fore.RED}Erreur lors de la vérification de réputation IP : {e}{Style.RESET_ALL}")

    # Mise à jour de l’activité IP
    try:
        ip_conn = ip_cursor = get_db()
        ip_cursor = ip_conn.cursor()

        now = datetime.now()
        ip_cursor.execute("SELECT count, last_seen FROM ip_activity WHERE ip = ?", (ip,))
        row = ip_cursor.fetchone()

        if row:
            count, last_seen = row
            last_seen = datetime.fromisoformat(last_seen)
            if now - last_seen < timedelta(minutes=5):
                count += 1
            else:
                count = 1
        else:
            count = 1

        ip_cursor.execute(
            "REPLACE INTO ip_activity (ip, count, last_seen) VALUES (?, ?, ?)",
            (ip, count, now.isoformat())
        )
        ip_conn.commit()

        if count >= 50:
            logger.warning(f"{Fore.YELLOW}[!] IP {ip} trop active. Ajout à la blacklist.{Style.RESET_ALL}")
            os.system(f"sudo iptables -A INPUT -s {ip} -j DROP")
            ip_cursor.execute("INSERT INTO blacklist (ip, blocked_at) VALUES (?, ?) ON CONFLICT(ip) DO UPDATE SET blocked_at = excluded.blocked_at",
                              (ip, now.isoformat()))
            ip_conn.commit()

        ip_conn.close()
    except Exception as e:
        logger.error(f"{Fore.RED}Erreur suivi d’activité IP : {e}{Style.RESET_ALL}")

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
        payload = json.dumps(request_data)
    return payload
