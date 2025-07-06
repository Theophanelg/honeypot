import sqlite3
from typing import Optional, List, Tuple, Any

# Ce module gère toutes les interactions avec la base de données SQLite du honeypot.
# Il initialise les tables et fournit des fonctions pour insérer et récupérer des logs.

# Connexion globale et création des tables au chargement du module
# Cela garantit que la base de données et ses schémas sont prêts à l'emploi.
conn = sqlite3.connect("honeypot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS attacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    port INTEGER,
    service TEXT,
    data TEXT,
    data_type TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    port INTEGER,
    user_agent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS payloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    port INTEGER NOT NULL,
    service TEXT NOT NULL,
    payload TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ip_reputation (
    ip TEXT PRIMARY KEY,
    abuse_score INTEGER,
    last_reported TEXT,
    country TEXT,
    isp TEXT
);
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ip_activity (
    ip TEXT PRIMARY KEY,
    count INTEGER,
    last_seen TEXT
); 
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS blacklist (
    ip TEXT PRIMARY KEY,
    blocked_at TEXT
)
""")
conn.commit()

def get_db() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """
    Fournit une nouvelle connexion à la base de données SQLite.
    Les lignes sont retournées comme des objets dict-like (sqlite3.Row).
    """
    conn = sqlite3.connect('honeypot.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor

def get_filtered_logs(ip: Optional[str] = None, service: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[sqlite3.Row]:
    """
    Récupère les logs d'attaques de la base de données, avec options de filtrage.
    """
    conn = sqlite3.connect("honeypot.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = "SELECT * FROM attacks WHERE 1=1"
    params: List[Any] = []
    if ip:
        query += " AND ip = ?"
        params.append(ip)
    if service:
        query += " AND service = ?"
        params.append(service)
    if start_date:
        query += " AND DATE(timestamp) >= ?"
        params.append(start_date)
    if end_date:
        query += " AND DATE(timestamp) <= ?"
        params.append(end_date)

    query += " ORDER BY timestamp DESC"

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows