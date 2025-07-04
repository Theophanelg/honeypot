#!/bin/bash
set -e

# Recommande d'exécuter ce script à la racine du projet
if [[ ! -f "honeypot_launcher.py" || ! -d "services" ]]; then
    echo "Erreur : Lance ce script depuis la racine du projet (là où se trouve honeypot_launcher.py) !"
    exit 1
fi

echo "==== Mise à jour de l'OS ===="
sudo apt update -y && sudo apt upgrade -y

echo "==== Installation des dépendances système nécessaires ===="
sudo apt install -y python3 python3-pip python3-venv sqlite3 git curl

echo "==== Création de l'environnement virtuel Python ===="
python3 -m venv venv

echo "==== Activation de l'environnement virtuel ===="
source venv/bin/activate

echo "==== Mise à jour de pip dans le venv ===="
pip install --upgrade pip

echo "==== Installation des packages Python du projet ===="
if [[ ! -f requirements.txt ]]; then
    echo "Erreur : Le fichier requirements.txt est manquant !"
    deactivate
    exit 1
fi
pip install -r requirements.txt

echo "==== Rendre les scripts exécutables ===="
chmod +x honeypot_launcher.py
chmod +x services/ssh_server.py
chmod +x services/http_server.py
chmod +x services/ftp_server.py

echo "==== Installation terminée avec succès ! ===="
echo
echo "Pour utiliser le projet :"
echo "1) Active l'environnement virtuel : source venv/bin/activate"
echo "2) Lance le honeypot : python honeypot_launcher.py"
echo
echo "⚠️ Optionnel : installe et configure ELK si tu veux superviser graphiquement les logs."
echo "Voir le script : deprecier/install_elk.sh"
