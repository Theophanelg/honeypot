import sqlite3

# Connexion globale
conn = sqlite3.connect("honeypot.db", check_same_thread=False)
cursor = conn.cursor()

# Création des tables
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
    last_seen TIMESTAMP
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

# Fonction d'accès simple à la base
def get_db():
    conn = sqlite3.connect('honeypot.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor


# Fonction utilitaire : récupérer les logs filtrés
def get_filtered_logs(ip=None, service=None, start_date=None, end_date=None):
    conn = sqlite3.connect("honeypot.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = "SELECT * FROM attacks WHERE 1=1"
    params = []

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
