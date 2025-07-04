import sqlite3

DB_PATH = "honeypot.db"

# Création des tables à l'initialisation du module
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
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
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            port INTEGER,
            user_agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
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
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ip_reputation (
            ip TEXT PRIMARY KEY,
            abuse_score INTEGER,
            last_reported TEXT,
            country TEXT,
            isp TEXT
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ip_activity (
            ip TEXT PRIMARY KEY,
            count INTEGER,
            last_seen TEXT
        ); 
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS blacklist (
            ip TEXT PRIMARY KEY,
            blocked_at TEXT
        )
        """)
        conn.commit()

# Appelle l'initialisation au chargement du module
init_db()

def get_db():
    """Retourne une connexion et un curseur à la base."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor

def insert_attack(ip, port, service, data, data_type):
    """Insère un log d'attaque dans la base."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO attacks (ip, port, service, data, data_type) VALUES (?, ?, ?, ?, ?)",
                (ip, port, service, data, data_type)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"[DB] Erreur insert_attack: {e}")

def get_filtered_logs(ip=None, service=None, start_date=None, end_date=None):
    """Retourne les logs filtrés selon plusieurs critères."""
    with sqlite3.connect(DB_PATH) as conn:
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

        try:
            c.execute(query, params)
            rows = c.fetchall()
        except sqlite3.Error as e:
            print(f"[DB] Erreur get_filtered_logs: {e}")
            rows = []
    return rows

# Ajoute d'autres fonctions d'insertion/lecture si besoin, en reprenant le modèle ci-dessus
