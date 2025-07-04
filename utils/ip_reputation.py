import requests
import sqlite3
import os
import logging
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ABUSEIPDB_API_KEY")  # Harmonisé
API_URL = "https://api.abuseipdb.com/api/v2/check"
DB_PATH = "honeypot.db"

logger = logging.getLogger(__name__)

def check_ip_reputation(ip):
    if not API_KEY:
        logger.error("Clé API AbuseIPDB manquante.")
        return None

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
            },
            timeout=10  # Timeout ajouté
        )

        if response.status_code != 200:
            logger.error(f"API AbuseIPDB - {response.status_code}: {response.text}")
            return None

        try:
            json_response = response.json()
            if "data" not in json_response:
                logger.error("Champ 'data' manquant dans la réponse JSON de AbuseIPDB.")
                return None
            data = json_response["data"]
        except Exception as e:
            logger.error(f"Erreur de décodage JSON AbuseIPDB: {e}")
            return None

        abuse_score = data.get("abuseConfidenceScore")
        last_reported = data.get("lastReportedAt")
        country = data.get("countryCode")
        isp = data.get("isp")

        # Context manager pour la base
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO ip_reputation (ip, abuse_score, last_reported, country, isp)
                    VALUES (?, ?, ?, ?, ?)
                """, (ip, abuse_score, last_reported, country, isp))
                conn.commit()
            logger.info(f"Réputation stockée pour {ip} (score: {abuse_score})")
        except sqlite3.Error as db_e:
            logger.error(f"Erreur SQLite: {db_e}")
            return None

        return abuse_score

    except requests.Timeout:
        logger.error("Timeout lors de la requête à AbuseIPDB.")
        return None
    except requests.RequestException as e:
        logger.error(f"Exception lors de la requête à AbuseIPDB: {e}")
        return None

# Si tu veux tester ce module directement
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ip = "8.8.8.8"
    score = check_ip_reputation(ip)
    print(f"Score pour {ip} : {score}")
