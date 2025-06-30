#!/bin/bash

HONEYPOT_HOST="localhost"
HONEYPOT_HTTP_PORT=80
HONEYPOT_SSH_PORT=22
HONEYPOT_FTP_PORT=21

echo "=== Envoi de requêtes HTTP ==="

# Requête GET avec paramètres
curl -A "EvilScanner/9.9" "http://$HONEYPOT_HOST:$HONEYPOT_HTTP_PORT/?user=admin&pass=123"

# Requête POST simulée
curl -X POST -A "MaliciousBot/4.2" -d "username=root&password=hunter2" "http://$HONEYPOT_HOST:$HONEYPOT_HTTP_PORT/login"

# Requête GET simple
curl -A "SuperBot/1.0" "http://$HONEYPOT_HOST:$HONEYPOT_HTTP_PORT/"

echo "open $HONEYPOT_HOST $HONEYPOT_FTP_PORT
user anonymous hackme
quit" | ftp -n

echo "=== Tentative de connexion SSH ==="
ssh -p $HONEYPOT_SSH_PORT fakeuser@$HONEYPOT_HOST -o StrictHostKeyChecking=no -o ConnectTimeout=5 "whoami"

echo "=== Terminé. Vérifie tes logs maintenant ! ==="
