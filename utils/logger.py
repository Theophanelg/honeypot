import logging
from utils.analyzer import analyze_data
from utils.db import get_db
from colorama import Fore, Style

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
def log_attack(ip, port, service, data):
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
        cursor.execute("INSERT INTO attacks (ip, port, service, data, data_type) VALUES (?, ?, ?, ?, ?)",
                (ip, port, service, data, data_type))
        conn.commit()
    except Exception as e: 
        logger.error(f"{Fore.RED}Error dans la connexion à la BDD: {e}{Style.RESET_ALL}")