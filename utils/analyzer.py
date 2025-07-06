import json
import re
from typing import Union

def analyze_data(data: Union[str, bytes]) -> str:
    """
    Analyse les données brutes capturées par les honeypots pour déterminer leur type
    (par exemple, identifiants, requêtes HTTP, commandes SSH, adresses IP).
    """
    if not isinstance(data, str):
        try:
            data = data.decode() if isinstance(data, bytes) else str(data)
        except Exception:
            return "Unknown (decode error)"

    if "password" in data.lower() or "login" in data.lower():
        return "Credentials"
    
    if re.match(r"^(GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH) ", data):
        return "HTTP Request"

    try:
        json.loads(data)
        return "JSON"
    except Exception:
        pass

    ip4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    ip6 = re.compile(r"\b([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}\b")
    if ip4.search(data) or ip6.search(data):
        return "Possible IP Address"

    # Logique de catégorisation des commandes SSH
    if data.strip() == "ls" or data.startswith("ls "):
        return "SSH - File Listing"
    if data.strip() == "cd" or data.startswith("cd ") or data.strip() == "pwd":
        return "SSH - Directory Nav."
    if data.startswith("cat ") or data.startswith("more ") or data.startswith("less "):
        return "SSH - File View"

    if data.startswith("mkdir "):
        return "SSH - Dir Creation"
    if data.startswith("rm "):
        return "SSH - File/Dir Deletion"
    if data.startswith("touch "):
        return "SSH - File Creation"

    if data.strip() == "whoami" or data.strip() == "id" or data.strip() == "uname -a":
        return "SSH - System Info"
    if data.startswith("echo "):
        return "SSH - Echo"
    
    if re.search(r'\b(sudo|apt|yum|dnf|apk|chmod|chown)\b', data):
        return "SSH - Priv Esc/Install"
    
    if re.search(r'\b(wget|curl|ftp|nc|netcat)\b', data):
        return "SSH - Download/Net"

    return "Unknown"