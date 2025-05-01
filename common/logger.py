import logging
from common.analyzer import analyze_data
from common.db import get_db

logging.basicConfig(filename="honeypot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

conn, cursor = get_db()

def log_attack(ip, port, service, data):
    data_type = analyze_data(data)
    logging.info(f"{service} attack from {ip}:{port} -> {data} (Type: {data_type})")
    cursor.execute("INSERT INTO attacks (ip, port, service, data, data_type) VALUES (?, ?, ?, ?, ?)",
                   (ip, port, service, data, data_type))
    conn.commit()