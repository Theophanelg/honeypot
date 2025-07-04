Voici une version **améliorée et complète de ton README**, incluant toutes les recommandations et points vus ensemble, **parfaite pour un projet cybersécurité en contexte étudiant** :

---

# Honeypot

## Description

Ce projet consiste en un **honeypot pédagogique** déployé sur plusieurs services simulés : SSH, HTTP et FTP.
Son but est de détecter, piéger et enregistrer les tentatives d’attaques automatisées ou manuelles, pour analyse ou démonstration.

* **honeypot\_launcher.py** : lance tous les services vulnérables simulés sur leurs ports respectifs (par défaut : SSH sur 2222, HTTP sur 8080, FTP sur 2121).
* Toutes les activités sont journalisées dans une base **SQLite** et dans des fichiers de logs.
* L’interface web (Flask) permet de visualiser les logs, les statistiques, d’exporter les données et de filtrer les attaques.

> ⚠️ **Avertissement**
> Ce projet est destiné à l’expérimentation et à la formation. **Ne l’exposez jamais en production ou sur un réseau sensible**. Les faux services sont volontairement vulnérables !
>
> **Respectez la légalité : n’utilisez ce honeypot que dans un environnement de test isolé, sous votre contrôle.**

---

## Fonctionnalités

* **Détection et enregistrement** des connexions suspectes sur SSH, HTTP et FTP.
* **Analyse automatique** des payloads : détection JSON, credential stuffing, requêtes HTTP, attaques XSS/SQLi...
* **Enregistrement détaillé** dans SQLite : logs d’attaques, payloads, user-agents, réputation IP, activités par IP.
* **Visualisation web** : filtres avancés, statistiques, top IP/ports/services, export CSV/JSON.
* **Blocage automatique** d’IP trop actives via iptables et blacklist en base.
* **Simulation réaliste** (délais, prompts, bannière SSH, fausse arborescence).
* **Scripts de test d’attaque** (`attack.sh`), d’intégration (`test_services.py`) et de gestion (`supervisor.py`, `launcher_flask.sh`, `launcher_tmux.sh`).
* **Installation et gestion propres** via environnement virtuel Python.

---

## Prérequis

* Système **Linux (Debian/Ubuntu recommandé)**.
* **Python 3** (>= 3.8 recommandé)
* **git**, **curl**, **sqlite3**, **tmux** (pour supervision), **ftp**, **ssh**, **sshpass** (pour les tests d’attaque).
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

4. **Lancez le honeypot** (plusieurs options) :

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

5. **Interface web**
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

  Modifiez l’adresse IP/ports si besoin dans le script.

* **Exportez les données** via l’interface web (CSV ou JSON, via `/export`).

* **Tests automatiques** :

  ```bash
  python Tests/test_services.py
  ```

---

## Scripts Utilitaires

* **supervisor.py** : Surveille et relance les services en cas de crash.
* **attack.sh** : Lance des attaques simulées sur tous les services du honeypot.
* **install\_elk.sh** : Installation rapide d’Elasticsearch et Kibana (pour ceux qui veulent une supervision avancée, à lancer séparément et avec précaution).
* **launcher\_flask.sh** : Lance uniquement l’interface Flask dans le venv.
* **launcher\_tmux.sh** : Lance tous les services dans une session tmux.

---

## Sécurité et bonnes pratiques

* **Jamais de secret en dur dans le code !** Utilisez le fichier `.env` pour vos clés (ex : clé AbuseIPDB pour l’IP reputation).
* **Ne jamais exécuter de commande reçue d’un attaquant** dans vos services simulés.
* **N’exposez pas votre honeypot sur internet** sauf si vous savez ce que vous faites.
* **Testez sur une VM ou un conteneur dédié** pour limiter les risques.
* **Évitez d’utiliser les ports < 1024** sauf si nécessaire et en connaissance de cause (souvent, les honeypots étudiants tournent sur 2222, 8080, 2121, etc.).
* **Pensez à consulter vos logs et votre base SQLite régulièrement** pour détecter d’éventuelles attaques ou fuites.

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

Besoin de précisions ? Consultez la doc, ou posez vos questions !
