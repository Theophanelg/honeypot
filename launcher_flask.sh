env() {
    python3 -m venv venv
    source venv/bin/activate
}

launch_flask() {
    python3 app.py
}

main() {
    env
    launch_flask
}

main