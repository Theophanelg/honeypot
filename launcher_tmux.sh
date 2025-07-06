#!/bin/bash
set -e # Quitte immédiatement si une commande échoue

SESSION="honeypot_main_session"
PROJECT_ROOT=$(dirname "$(realpath "$0")") # Chemin absolu du répertoire du projet

echo "====================================================="
echo "=== Lancement Complet du Honeypot Multi-Services ==="
echo "====================================================="

# --- Étape 1: Vérifier les dépendances système (tmux) ---
echo "[*] Vérification de la dépendance 'tmux'..."
if ! command -v tmux &> /dev/null; then
    echo "Erreur : 'tmux' n'est pas installé."
    echo "Veuillez l'installer manuellement : sudo apt install tmux"
    echo "Puis relancez ce script."
    exit 1
fi

# --- Étape 2: Préparer l'environnement Python (venv et packages) ---
echo "[*] Préparation de l'environnement Python..."
cd "$PROJECT_ROOT" # S'assurer d'être à la racine du projet

if [[ ! -d "venv" ]]; then
    echo "[*] Environnement virtuel 'venv' non trouvé. Création..."
    python3 -m venv venv
fi

echo "[*] Activation de l'environnement virtuel..."
source venv/bin/activate

echo "[*] Installation/Mise à jour des packages Python via requirements.txt..."
if [[ -f requirements.txt ]]; then
    pip install --upgrade pip > /dev/null 2>&1 # Mettre à jour pip silencieusement
    pip install -r requirements.txt > /dev/null 2>&1 # Installer les dépendances silencieusement
    echo "[*] Packages Python installés/mis à jour."
else
    echo "Avertissement : Le fichier 'requirements.txt' est manquant. Impossible d'installer les dépendances Python."
fi

# --- Étape 3: Gérer la session tmux et lancer les applications ---
echo "[*] Gestion de la session tmux et lancement des services..."

# Si une session existe déjà, on l'efface d'abord pour un démarrage propre
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "[*] Session tmux '$SESSION' existante détectée. Suppression..."
    tmux kill-session -t "$SESSION"
    sleep 1 # Laisser le temps à tmux de se terminer
fi

echo "[*] Création de la session tmux '$SESSION' avec 3 panes:"
echo "    - Pane 1 (en haut à gauche): Services Honeypot"
echo "    - Pane 2 (en haut à droite): Application Web Flask"
echo "    - Pane 3 (en bas): Logs en temps réel"

# Lancer le honeypot_launcher.py dans le premier pane
tmux new-session -d -s "$SESSION" "cd '$PROJECT_ROOT' && source venv/bin/activate && python3 honeypot_launcher.py"

# Séparer la fenêtre horizontalement pour l'application Flask
tmux split-window -h -t "$SESSION:0.0" "cd '$PROJECT_ROOT' && source venv/bin/activate && python3 app.py"

# Séparer la fenêtre (racine) verticalement pour les logs (s'étend sur les deux panes du haut)
tmux split-window -v -t "$SESSION" "cd '$PROJECT_ROOT' && tail -f honeypot.log"

# Sélectionner le premier pane (honeypot_launcher) pour l'affichage initial
tmux select-pane -t "$SESSION:0.0"

echo "[*] Services lancés dans la session tmux '$SESSION'."
echo "[*] Attachement à la session tmux. Appuyez sur Ctrl+b d pour la détacher."

# Attacher au session tmux
tmux -2 attach-session -t "$SESSION"

echo "====================================================="
echo "=== Script de Lancement Terminé ==="
echo "====================================================="