import requests
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ABUSE_API_KEY")
API_URL = "https://api.abuseipdb.com/api/v2/check"

# Vérifie la réputation d'une IP via AbuseIPDB et stocke le résultat
def check_ip_reputation(ip):
    if not API_KEY:
        print("[ERREUR] Clé API AbuseIPDB manquante.")
        return

    try:
        response = requests.get(
            API_URL,
            headers={
                "Accept": "application/json",
                "Key": API_KEY
            },
            params={
                "ipAddress": ip,
                "maxAgeInDays": 30
            }
        )

        if response.status_code != 200:
            print(f"[ERREUR] API AbuseIPDB - {response.status_code}: {response.text}")
            return

        data = response.json()["data"]

        abuse_score = data.get("abuseConfidenceScore")
        last_reported = data.get("lastReportedAt")
        country = data.get("countryCode")
        isp = data.get("isp")

        # Stocke dans la base
        conn = sqlite3.connect("honeypot.db", check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO ip_reputation (ip, abuse_score, last_reported, country, isp)
            VALUES (?, ?, ?, ?, ?)
        """, (ip, abuse_score, last_reported, country, isp))
        conn.commit()
        conn.close()

        print(f"[INFO] Réputation stockée pour {ip} (score: {abuse_score})")

    except Exception as e:
        print(f"[ERREUR] Exception lors de la requête à AbuseIPDB: {e}")
