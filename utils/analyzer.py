import json
import re

def analyze_data(data):
    # Sécurité : forcer la conversion en str
    if not isinstance(data, str):
        try:
            data = data.decode() if isinstance(data, bytes) else str(data)
        except Exception:
            return "Unknown (decode error)"

    # D'abord : test JSON
    try:
        json.loads(data)
        return "JSON"
    except Exception as e:
        pass  # Tu pourrais logger ici l’erreur si besoin

    # Recherche de credentials (plus large)
    keywords = ["password", "passwd", "login", "motdepasse"]
    if any(word in data.lower() for word in keywords):
        return "Credentials"

    # HTTP request ?
    if re.match(r"^(GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH) ", data):
        return "HTTP Request"

    # Détection IP v4 et v6 avec regex
    ip4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    ip6 = re.compile(r"\b([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}\b")
    if ip4.search(data) or ip6.search(data):
        return "Possible IP Address"

    return "Unknown"
