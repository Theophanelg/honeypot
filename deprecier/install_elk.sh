#!/bin/bash
set -e

# Vérifie que le script est lancé en root
if [[ "$EUID" -ne 0 ]]; then
  echo "Ce script doit être lancé en tant que root. Utilisez : sudo $0"
  exit 1
fi

install_elk() {
    echo "==> Installation d'Elasticsearch et Kibana..."

    # Importer la clé GPG
    if [[ ! -f /usr/share/keyrings/elastic-archive-keyring.gpg ]]; then
        echo "--> Import de la clé GPG Elastic"
        curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elastic-archive-keyring.gpg
    fi

    # Ajouter le dépôt Elastic (si pas déjà ajouté)
    if ! grep -q elastic /etc/apt/sources.list.d/elastic-8.x.list 2>/dev/null; then
        echo "--> Ajout du dépôt Elastic"
        echo "deb [signed-by=/usr/share/keyrings/elastic-archive-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" \
        > /etc/apt/sources.list.d/elastic-8.x.list
    fi

    echo "--> Mise à jour des paquets"
    apt update

    echo "--> Installation d'Elasticsearch et Kibana"
    apt install -y elasticsearch kibana

    # Vérification avant activation
    if command -v elasticsearch >/dev/null && command -v kibana >/dev/null; then
        echo "--> Activation et démarrage des services"
        systemctl enable --now elasticsearch
        systemctl enable --now kibana
        echo "Elasticsearch et Kibana ont été installés et démarrés avec succès."
    else
        echo "Erreur : installation d'Elasticsearch ou Kibana échouée."
        exit 1
    fi
}

main() {
    install_elk
}

main
