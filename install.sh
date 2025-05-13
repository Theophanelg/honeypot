#!/bin/bash

# Fonction pour mettre à jour le système
update_system() {
    echo "Mise à jour de l'OS..."
    sudo apt update -y && sudo apt upgrade -y
}

# Fonction pour installer les dépendances nécessaires
install_dependencies() {
    echo "Installation des dépendances nécessaires..."
    sudo apt install -y python3 python3-pip python3-venv sqlite3 git curl
}

# Fonction pour installer les paquets Python nécessaires
install_python_packages() {
    echo "Installation des packages Python..."
    pip3 install --upgrade pip
    pip3 install flask colorlog
    pip3 install colorama
}

# Fonction pour configurer l'environnement virtuel Python
setup_virtualenv() {
    echo "Création de l'environnement virtuel..."
    cd /home/$USER/honeypot
    python3 -m venv venv
    source venv/bin/activate
}

# Fonction pour installer les dépendances dans l'environnement virtuel
install_virtualenv_dependencies() {
    echo "Installation des dépendances dans l'environnement virtuel..."
    pip install -r requirements.txt
}

# Fonction pour rendre les scripts exécutables
make_scripts_executable() {
    echo "Rendre les scripts exécutables..."
    chmod +x honeypot_launcher.py
    chmod +x services/ssh_server.py
    chmod +x services/http_server.py
    chmod +x services/ftp_server.py
}

# Fonction pour lancer le honeypot (optionnel)
launch_honeypot() {
    echo "Lancement du honeypot..."
    python honeypot_launcher.py
}

# Fonction principale qui orchestre l'installation
main() {
    update_system
    install_dependencies
    install_python_packages
    setup_virtualenv
    install_virtualenv_dependencies
    make_scripts_executable
    install_elk
    echo "Installation terminée avec succès!"
    echo "Lancez votre honeypot en exécutant : python honeypot_launcher.py"
    
    # Optionnel: Lancer automatiquement le honeypot après l'installation
    # launch_honeypot
}

# Appel de la fonction principale
main
