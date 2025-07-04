#!/bin/bash
set -e

# Crée le venv si besoin, sinon active-le simplement
setup_venv() {
    if [[ ! -d "venv" ]]; then
        echo "[*] Création de l'environnement virtuel Python..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        if [[ -f requirements.txt ]]; then
            pip install -r requirements.txt
        else
            echo "requirements.txt manquant !"
        fi
    else
        echo "[*] Activation de l'environnement virtuel existant..."
        source venv/bin/activate
    fi
}

launch_flask() {
    echo "[*] Lancement de l'application Flask..."
    python app.py
}

main() {
    setup_venv
    launch_flask
}

main
