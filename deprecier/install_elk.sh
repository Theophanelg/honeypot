# Fonction pour installer Elasticsearch et Kibana
install_elk() {
    echo "Installation d'Elasticsearch et Kibana..."

    # Importer la clé GPG
    curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elastic-archive-keyring.gpg

    # Ajouter le dépôt Elastic
    echo "deb [signed-by=/usr/share/keyrings/elastic-archive-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | \
    sudo tee /etc/apt/sources.list.d/elastic-8.x.list

    # Mise à jour et installation
    sudo apt update
    sudo apt install -y elasticsearch kibana

    # Activer et démarrer les services
    sudo systemctl enable --now elasticsearch
    sudo systemctl enable --now kibana

    echo "Elasticsearch et Kibana ont été installés et démarrés."
}

main() {
    install_elk
}

main