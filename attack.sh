#!/bin/bash
set -e

# Vérification des dépendances
for cmd in curl ftp ssh sshpass; do
    if ! command -v $cmd &> /dev/null; then
        echo "Erreur : $cmd n'est pas installé. Installe-le avec 'sudo apt install $cmd'"
        exit 1
    fi
done

HONEYPOT_HOST="192.168.79.128"
HONEYPOT_HTTP_PORT=8080    # adapte à ton port réel !
HONEYPOT_SSH_PORT=2222
HONEYPOT_FTP_PORT=2121

IPS=("192.168.1.100" "10.0.0.55" "203.0.113.77" "198.51.100.42" "192.168.79.128")

echo "==============================="
echo "=== SIMULATION D'ATTAQUES ==="
echo "==============================="

echo -e "\n=== Attaques HTTP (Port $HONEYPOT_HTTP_PORT) ==="
for ip in "${IPS[@]}"; do
    echo "--- HTTP GET (Credentials in URL) from $ip ---"
    curl -s -A "EvilScanner/9.9" -H "X-Forwarded-For: $ip" "http://$HONEYPOT_HOST:$HONEYPOT_HTTP_PORT/?user=admin&pass=123"

    echo "--- HTTP POST (Login Attempt) from $ip ---"
    curl -s -X POST -A "MaliciousBot/4.2" -H "X-Forwarded-For: $ip" -d "username=root&password=hunter2" "http://$HONEYPOT_HOST:$HONEYPOT_HTTP_PORT/login"

    echo "--- HTTP GET (Simple Page Request) from $ip ---"
    curl -s -A "SuperBot/1.0" -H "X-Forwarded-For: $ip" "http://$HONEYPOT_HOST:$HONEYPOT_HTTP_PORT/"

    echo "--- HTTP GET (Path Traversal Attempt) from $ip ---"
    curl -s -A "NMAP-WebScan/1.0" -H "X-Forwarded-For: $ip" "http://$HONEYPOT_HOST:$HONEYPOT_HTTP_PORT/../../etc/passwd"

    echo "--- HTTP GET (XSS Attempt) from $ip ---"
    curl -s -A "SQLMap/1.6" -H "X-Forwarded-For: $ip" "http://$HONEYPOT_HOST:$HONEYPOT_HTTP_PORT/?name=<script>alert('XSS')</script>"

    echo "--- HTTP POST (JSON Payload Injection) from $ip ---"
    curl -s -X POST -A "API-Exploiter/0.1" -H "Content-Type: application/json" -H "X-Forwarded-For: $ip" -d '{"cmd": "system(\"ls -la /\")", "user": "test"}' "http://$HONEYPOT_HOST:$HONEYPOT_HTTP_PORT/api/v1/execute"

    echo "--- HTTP HEAD (Reconnaissance) from $ip ---"
    curl -s -I -A "ReconBot/0.5" -H "X-Forwarded-For: $ip" "http://$HONEYPOT_HOST:$HONEYPOT_HTTP_PORT/"
done

echo -e "\n=== Attaques FTP (Port $HONEYPOT_FTP_PORT) ==="
# FTP : vérifier que le service écoute bien sur le port choisi
for cred in "anonymous hackme" "admin admin" "root toor"; do
    user=$(echo $cred | cut -d' ' -f1)
    pass=$(echo $cred | cut -d' ' -f2)
    echo "--- FTP login attempt: $user/$pass ---"
    echo -e "open $HONEYPOT_HOST $HONEYPOT_FTP_PORT\nuser $user $pass\nquit" | ftp -n > /dev/null 2>&1
done

echo "--- FTP (Post-Login Commands Simulation) ---"
(
echo "open $HONEYPOT_HOST $HONEYPOT_FTP_PORT"
sleep 1
echo "user testuser testpass"
sleep 1
echo "ls"
sleep 1
echo "get notes.txt"
sleep 1
echo "put local_file.txt remote_file.txt"
sleep 1
echo "pwd"
sleep 1
echo "quit"
) | ftp -n > /dev/null 2>&1

echo -e "\n=== Attaques SSH (Port $HONEYPOT_SSH_PORT) ==="
echo "--- SSH (Initial Command Execution Attempt) ---"
ssh -p $HONEYPOT_SSH_PORT fakeuser@$HONEYPOT_HOST -o StrictHostKeyChecking=no -o ConnectTimeout=5 "whoami" > /dev/null 2>&1 || true

for creds in "root root" "admin password" "ubuntu ubuntu"; do
    user=$(echo $creds | cut -d' ' -f1)
    pass=$(echo $creds | cut -d' ' -f2)
    echo "--- SSH (Common Credential - $user/$pass) ---"
    sshpass -p "$pass" ssh -p $HONEYPOT_SSH_PORT $user@$HONEYPOT_HOST -o StrictHostKeyChecking=no -o ConnectTimeout=5 "ls -la /" > /dev/null 2>&1 || true
done

echo "--- SSH (Simulated Interactive Session) ---"
ssh -p $HONEYPOT_SSH_PORT attacker@$HONEYPOT_HOST -o StrictHostKeyChecking=no -o ConnectTimeout=5 "cd /etc; ls; cat passwd" > /dev/null 2>&1 || true

echo -e "\n=========================================="
echo "=== Terminé. Vérifie tes logs maintenant ! ==="
echo "=========================================="
