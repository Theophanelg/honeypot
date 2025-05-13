import logging
from utils.analyzer import analyze_data
from utils.db import get_db
from colorama import Fore, Style
import re
import json
from urllib.parse import urlparse, parse_qs

# Initialisation de la BDD SQLite
conn, cursor = get_db()

# Configuration du logger
def setup_logger():
    log_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Création d'un gestionnaire de flux
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    # Création d'un gestionnaire de fichier pour le fichier honeypot.log
    file_handler = logging.FileHandler('honeypot.log')
    file_handler.setFormatter(log_formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
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

    # Message à afficher
    log_msg = (f"{color}{service} attack from {ip}:{port} -> {data} (Type: {data_type}){Style.RESET_ALL}")
    logger.info(log_msg)
    
    try:
        # Insertion dans la table attack
        cursor.execute("INSERT INTO attacks (ip, port, service, data, data_type) VALUES (?, ?, ?, ?, ?)",
                       (ip, port, service, data, data_type))
        conn.commit()
        
        # Si HTTP dans la table user_agents
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
            if payload_dict:
                payload = json.dumps(payload_dict)
            else:
                payload = None

    elif method == 'POST':
        payload = json.dumps(request_data)

    return payload