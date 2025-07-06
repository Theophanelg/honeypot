import logging
from utils.analyzer import analyze_data
from utils.db import get_db, insert_payload
from utils.ip_reputation import check_ip_reputation
from colorama import Fore, Style
import re
import json
from urllib.parse import urlparse, parse_qs
import sqlite3
from datetime import datetime, timedelta
import os
import subprocess
from typing import Union, Optional

def setup_logger():
    """Configure et retourne un logger pour les événements du honeypot."""
    log_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    file_handler = logging.FileHandler('honeypot.log')
    file_handler.setFormatter(log_formatter)

    logger = logging.getLogger("honeypot")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

logger = setup_logger()

def extract_user_agent(data: str) -> Optional[str]:
    """Extrait la chaîne User-Agent des données de requête HTTP."""
    match = re.search(r'User-Agent:\s*(.+)', data, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_http_payload(request_data: str, method: str) -> Optional[str]:
    """Extrait la charge utile des données de requête HTTP (pour GET: paramètres URL, pour POST: corps de la requête)."""
    payload = None
    if method == 'GET':
        match = re.search(r'GET\s+(\S+)', request_data)
        if match:
            url_parsed = urlparse(match.group(1))
            payload_dict = parse_qs(url_parsed.query)
            if payload_dict:
                payload = json.dumps(payload_dict)
    elif method == 'POST':
        payload = json.dumps(request_data)
    return payload

def log_attack(ip: str, port: int, service: str, data: Union[str, bytes], method: str = "GET", output_content: Optional[str] = None):
    """
    Enregistre un événement d'attaque dans la console, un fichier et la base de données.
    Effectue l'analyse des données, la vérification de la réputation IP et le blacklisting.
    """
    data_type = analyze_data(data)

    color = Fore.RED if service == "SSH" else \
            Fore.BLUE if service == "HTTP" else \
            Fore.MAGENTA if service == "FTP" else \
            Fore.WHITE

    log_console = f"{color}{service} attack from {ip}:{port} -> {data} (Type: {data_type}){Style.RESET_ALL}"
    log_file = f"{service} attack from {ip}:{port} -> {data} (Type: {data_type})"

    logger.info(log_console)

    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.emit(logging.LogRecord(
                name=logger.name, level=logging.INFO, pathname=__file__,
                lineno=0, msg=log_file, args=(), exc_info=None
            ))

    attack_id = None
    try:
        conn, cursor = get_db()
        cursor.execute("INSERT INTO attacks (ip, port, service, data, data_type) VALUES (?, ?, ?, ?, ?)",
                       (ip, port, service, data, data_type))
        attack_id = cursor.lastrowid
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logger.error(f"Erreur insertion dans la table 'attacks': {e}")

    # Insertion du payload, utilise insert_payload si l'attaque a été enregistrée avec succès
    if attack_id is not None:
        try:
            if service == "HTTP":
                user_agent = extract_user_agent(data)
                if user_agent:
                    # insert_user_agent pourrait être une nouvelle fonction dans utils.db
                    conn_ua, cursor_ua = get_db()
                    cursor_ua.execute("INSERT INTO user_agents (ip, port, user_agent) VALUES (?, ?, ?)",
                                       (ip, port, user_agent))
                    conn_ua.commit()
                    conn_ua.close()

                payload = extract_http_payload(data, method)
                if payload:
                    insert_payload(attack_id, ip, port, service, payload) # Utilise la nouvelle fonction
            elif service == "SSH":
                payload_to_store = output_content if output_content is not None else data
                insert_payload(attack_id, ip, port, service, payload_to_store) # Utilise la nouvelle fonction
            # Aucune action de BDD ici pour FTP car le payload est la commande, déjà loguée
        except sqlite3.Error as e:
            logger.error(f"Erreur insertion dans la table 'payloads' ou 'user_agents': {e}") # Message plus spécifique

    try:
        conn, cursor = get_db()
        cursor.execute("SELECT 1 FROM ip_reputation WHERE ip = ?", (ip,))
        if not cursor.fetchone():
            check_ip_reputation(ip)
        conn.close()
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de réputation IP : {e}")

    try:
        conn, cursor = get_db()
        now = datetime.now()
        cursor.execute("SELECT count, last_seen FROM ip_activity WHERE ip = ?", (ip,))
        row = cursor.fetchone()

        count = 1
        if row:
            prev_count, last_seen_str = row
            try:
                last_seen = datetime.fromisoformat(last_seen_str)
            except ValueError:
                last_seen = now - timedelta(hours=1)
            
            if now - last_seen < timedelta(minutes=5):
                count = prev_count + 1
            else:
                count = 1

        cursor.execute(
            "REPLACE INTO ip_activity (ip, count, last_seen) VALUES (?, ?, ?)",
            (ip, count, now.isoformat())
        )
        conn.commit()

        if count >= 50:
            logger.warning(f"[!] IP {ip} trop active. Ajout à la blacklist.")
            if os.geteuid() == 0:
                subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
                logger.warning(f"IP {ip} bloquée via iptables.")
            else:
                logger.warning(f"(Non-root) Simulation de blocage iptables pour {ip}. Lancez en root pour appliquer.")

            cursor.execute(
                "INSERT INTO blacklist (ip, blocked_at) VALUES (?, ?) ON CONFLICT(ip) DO UPDATE SET blocked_at = excluded.blocked_at",
                (ip, now.isoformat()))
            conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Erreur suivi d’activité IP : {e}")