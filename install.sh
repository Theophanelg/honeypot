#!/bin/bash
set -e # Quitte immédiatement si une commande échoue

# Ce script automatise l'installation des dépendances système et Python
# nécessaires pour exécuter le honeypot.
# Il est conçu pour être exécuté une seule fois pour préparer l'environnement.

if [[ ! -f "honeypot_launcher.py" || ! -d "services" ]]; then
    echo "Erreur : Ce script doit être lancé depuis la racine du projet (là où se trouve honeypot_launcher.py) !"
    exit 1
fi

echo "==== Mise à jour de l'OS ===="
sudo apt update -y && sudo apt upgrade -y

echo "==== Installation des dépendances système nécessaires ===="
sudo apt install -y python3 python3-pip python3-venv sqlite3 git curl tmux ssh sshpass ftp

echo "==== Création de l'environnement virtuel Python ===="
python3 -m venv venv

echo "==== Activation de l'environnement virtuel ===="
source venv/bin/activate

echo "==== Mise à jour de pip dans le venv ===="
pip install --upgrade pip

echo "==== Installation des packages Python du projet ===="
if [[ ! -f requirements.txt ]]; then
    echo "Erreur : Le fichier requirements.txt est manquant ! Créez-le avec les dépendances Flask, Colorama, Requests, python-dotenv."
    deactivate
    exit 1
fi
pip install -r requirements.txt

echo "==== Rendre les scripts exécutables ===="
chmod +x honeypot_launcher.py
chmod +x services/ssh_server.py
chmod +x services/http_server.py
chmod +x services/ftp_server.py
chmod +x attack.sh
chmod +x launcher_tmux.sh
chmod +x launcher_flask.sh

echo "==== Installation terminée avec succès ! ===="
echo
echo "Pour lancer le honeypot (recommandé) :"
echo "1) Activez l'environnement virtuel (si pas déjà fait) : source venv/bin/activate"
echo "2) Lancez le honeypot et l'interface web dans tmux : ./launcher_tmux.sh"
echo
echo "Pour lancer l'interface web seule : ./launcher_flask.sh"
echo "Pour lancer les services honeypot seuls : python honeypot_launcher.py"
echo "Pour simuler des attaques : ./attack.sh"