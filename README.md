# Honeypot

## Description

Ce projet consiste en un **honeypot pédagogique** déployé sur plusieurs services simulés : SSH, HTTP et FTP.
Son but est de détecter, piéger et enregistrer les tentatives d’attaques automatisées ou manuelles, pour analyse ou démonstration.

* **honeypot\_launcher.py** : lance tous les services vulnérables simulés sur leurs ports respectifs (par défaut : SSH sur 2222, HTTP sur 8080, FTP sur 2121).
* Toutes les activités sont journalisées dans une base **SQLite** (`honeypot.db`) et dans des fichiers de logs (`honeypot.log`).
* L’interface web (Flask) permet de visualiser les logs, les statistiques, d’exporter les données et de filtrer les attaques.

> ⚠️ **Avertissement**
> Ce projet est destiné à l’expérimentation et à la formation. **Ne l’exposez jamais en production ou sur un réseau sensible**. Les faux services sont volontairement vulnérables !
>
> **Respectez la légalité : n’utilisez ce honeypot que dans un environnement de test isolé, sous votre contrôle.**

---

## Fonctionnalités

* **Détection et enregistrement** des connexions suspectes sur SSH, HTTP et FTP.
* **Analyse automatique** des payloads : détection JSON, credential stuffing, requêtes HTTP, attaques XSS/SQLi, etc.
* **Enregistrement détaillé** dans SQLite : logs d’attaques, payloads, user-agents, réputation IP (AbuseIPDB), activité par IP, blacklist, etc.
* **Visualisation web** : filtres avancés (IP, service, date), statistiques (top IP, ports, scores de réputation), export CSV/JSON.
* **Blocage automatique** d’IP trop actives via iptables et blacklist en base.
* **Simulation réaliste** (délais, prompts, bannière SSH, fausse arborescence, faux fichiers, etc.).
* **Tests complets** : unitaire, fonctionnel, non-régression, réputation IP, robustesse, tous regroupés dans `Tests/tests_services.py`.
* **Supervision automatique** des services (redémarrage en cas de crash).
* **Installation et gestion propres** via environnement virtuel Python.

---

## Prérequis

* Système **Linux (Debian/Ubuntu recommandé)**.
* **Python 3** (>= 3.8 recommandé)
* **git**, **curl**, **sqlite3**, **tmux**, **ftp**, **ssh**, **sshpass** (pour scripts d’attaque et tests).
* (Optionnel) **pip** et **python3-venv** pour environnement virtuel Python.
* (Optionnel) **ELK** (Elasticsearch/Kibana) pour visualisation avancée : script d’installation fourni (`install_elk.sh`).

---

## Installation

1. **Clonez ce repository** :

   ```bash
   git clone https://github.com/ton-utilisateur/ton-projet.git /home/$USER/honeypot
   cd /home/$USER/honeypot
   ```

2. **Lancez le script d’installation** (va tout préparer : dépendances système, venv, paquets Python, droits) :

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Activez l’environnement virtuel à chaque nouvelle session** :

   ```bash
   source venv/bin/activate
   ```

4. **Vérifiez que le fichier `requirements.txt`** contient bien toutes les dépendances Python nécessaires :

   ```
   flask
   requests
   colorama
   python-dotenv
   ...
   ```

   *(Ajoutez tout paquet manquant selon vos imports)*

5. **Vérifiez que le fichier `.env`** contient au moins votre clé AbuseIPDB (pour la réputation IP) :

   ```
   ABUSEIPDB_API_KEY=xxxxxxxxxxxxxxxx
   ```

   *(Ce fichier **ne doit jamais être versionné** !)*

6. **Lancez le honeypot** (plusieurs options) :

   * Multi-services (recommandé) :

     ```bash
     python honeypot_launcher.py
     ```
   * En tmux avec suivi live des logs :

     ```bash
     ./launcher_tmux.sh
     ```
   * En mode Flask (interface web seule) :

     ```bash
     ./launcher_flask.sh
     ```

7. **Interface web**
   Rendez-vous sur : [http://localhost:5000](http://localhost:5000) (ou l’IP de votre VM si en accès distant).

---

## Utilisation

* **Logs en temps réel** : consultez `honeypot.log` ou utilisez tmux pour surveiller.
* **Analyse/filtrage** : page `/` pour les logs bruts, `/stats` pour les statistiques avancées.
* **Testez votre honeypot** :
  Utilisez le script d’attaque automatisé :

  ```bash
  ./attack.sh
  ```

  *(Modifiez l’adresse IP/ports si besoin dans le script.)*
* **Exportez les données** via l’interface web (CSV ou JSON, via `/export`).
* **Tests automatiques** :

  ```bash
  python Tests/tests_services.py
  ```

  *(Tous les tests unitaires, fonctionnels, non-régression, réputation IP et robustesse sont regroupés et exécutables d’un seul coup.)*
* **Réinitialisez la base** (optionnel) :

  ```bash
  rm honeypot.db
  python honeypot_launcher.py  # ou relancez le service, la base sera recréée
  ```

---

## Scripts Utilitaires

* **supervisor.py** : Surveille et relance les services en cas de crash.
* **attack.sh** : Lance des attaques simulées sur tous les services du honeypot.
* **install\_elk.sh** : Installation rapide d’Elasticsearch et Kibana (pour supervision avancée, à lancer séparément).
* **launcher\_flask.sh** : Lance uniquement l’interface Flask dans le venv.
* **launcher\_tmux.sh** : Lance tous les services dans une session tmux.

---

## Sécurité et bonnes pratiques

* **Jamais de secret en dur dans le code !** Utilisez le fichier `.env` pour vos clés sensibles (ex : AbuseIPDB).
* **Ne jamais exécuter de commande reçue d’un attaquant** dans vos services simulés.
* **N’exposez pas votre honeypot sur internet** sauf si vous maîtrisez totalement l’environnement.
* **Testez sur une VM ou un conteneur dédié** pour limiter les risques.
* **Évitez les ports < 1024** sauf nécessité : utilisez plutôt 2222 (SSH), 8080 (HTTP), 2121 (FTP).
* **Consultez régulièrement vos logs et votre base SQLite** pour surveiller l’activité.

---

## Dépannage & Compatibilité

* **Activez le venv avant toute commande Python** (sinon modules introuvables).
* **Lancez les tests et le honeypot depuis la racine du projet** (sinon problèmes d’imports).
* **Vérifiez que `honeypot.db` existe ou sera créé au lancement.**
* **Modifiez les ports dans les scripts si d’autres services les utilisent déjà.**
* **Pour un reporting de tests moderne** :

  ```bash
  pip install pytest
  pytest Tests/tests_services.py
  ```
* **Pour une base vierge** (avant démo/soutenance) : supprimez le fichier `honeypot.db` avant de relancer.

---

## Contribution

Contributions, suggestions ou rapports de bugs sont bienvenus !
Ouvrez une **issue** ou proposez une **pull request**.

---

## Avertissement légal

Ce projet est fourni à des fins pédagogiques.
**L’exécution de ce honeypot sur un réseau que vous ne contrôlez pas, ou sans autorisation, peut être illégale et/ou dangereuse.
L’auteur ne pourra être tenu responsable de tout usage non conforme à la loi ou à l’éthique.**

---

**Besoin de précisions ? Consultez la doc, posez vos questions ou ouvrez une issue !**

---

