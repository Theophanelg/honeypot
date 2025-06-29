#!/bin/bash

# Lancement du honeypot dans un tmux
launch_honeypot() {
    tmux new-session -d -s honeypot_session 'venv/bin/python honeypot_launcher.py'
    tmux split-window -h 'tail -f honeypot.log' 
    tmux -2 attach-session -t honeypot_session 
}

# Fonction principale
main() {
    echo "Lancement du honeypot"
    launch_honeypot
} 

main
