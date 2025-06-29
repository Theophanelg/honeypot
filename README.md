# Honeypot

## Description

Ce projet consiste en un **honeypot** déployé sur plusieurs services vulnérables, simulant des serveurs SSH, HTTP et FTP pour détecter et enregistrer les tentatives d'attaques. Le script **honeypot_launcher.py** est responsable du lancement de ces services sur les ports respectifs, et toutes les tentatives d'accès sont enregistrées dans une base de données SQLite et dans des fichiers de logs.

Les services sont :
- **SSH** : Simule un serveur SSH vulnérable.
- **HTTP** : Simule un serveur HTTP vulnérable.
- **FTP** : Simule un serveur FTP vulnérable.

Les tentatives d'attaque sont analysées et les données sont stockées dans une base de données SQLite pour permettre un suivi détaillé des activités.

## Fonctionnalités
- Détection et enregistrement des tentatives de connexion (SSH, HTTP, FTP).
- Identification du type de données reçues (JSON, informations de connexion, requêtes HTTP, etc.).
- Enregistrement des attaques dans des logs et une base de données SQLite.
- Environnement virtuel Python pour une installation propre des dépendances.

## Prérequis

Avant de commencer l'installation, assurez-vous d'avoir les éléments suivants :
- Un système **Linux (Debian/Ubuntu recommandé)**.
- **Python 3** installé.
- **curl**, **git**, et autres dépendances nécessaires.

## Installation

1. Clonez ce repository sur votre machine :
    ```bash
       git clone https://github.com/ton-utilisateur/ton-projet.git /home/$USER/honeypot 
    ```

2. Rendre le script d'installation exécutable : 
    ```bash
        cd /home/$USER/honeypot
        chmod +x install.sh 
    ```

3. Lancer le script install.sh
    ```bash
        ./install.sh
    ```

4. Lancer le Honeypot
    ```bash
        python honeypot_launcher.py
    ```

