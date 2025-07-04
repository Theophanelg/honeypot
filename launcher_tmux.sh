#!/bin/bash
set -e

# Vérifie que tmux est installé
if ! command -v tmux &> /dev/null; then
    echo "Erreur : tmux n'est pas installé. Installe-le avec : sudo apt install tmux"
    exit 1
fi

# Vérifie que le venv existe
if [[ ! -d "venv" ]]; then
    echo "Erreur : l'environnement virtuel 'venv' n'existe pas. Lance d'abord install.sh !"
    exit 1
fi

SESSION="honeypot_session"

# Si une session existe déjà, on l'efface d'abord
if tmux has-session -t $SESSION 2>/dev/null; then
    echo "[*] Session tmux $SESSION déjà existante : suppression."
    tmux kill-session -t $SESSION
fi

echo "[*] Lancement du honeypot dans tmux..."
tmux new-session -d -s $SESSION 'venv/bin/python honeypot_launcher.py'
tmux split-window -h -t $SESSION 'tail -f honeypot.log'
tmux select-pane -t $SESSION:0.0
tmux -2 attach-session -t $SESSION
