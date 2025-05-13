from flask import Flask, render_template, request
from utils.db import get_db

app = Flask(__name__)

# Connexion à la base de données
conn, cursor = get_db()

# Route pour afficher les logs
@app.route('/')
def index():
    service = request.args.get('service')
    date = request.args.get('date')

    query = "SELECT * FROM attacks"
    conditions = []
    values = []

    if service:
        conditions.append("service = ?")
        values.append(service)

    if date:
        conditions.append("DATE(timestamp) = ?")
        values.append(date)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY timestamp DESC LIMIT 100"

    cursor.execute(query, values)
    attacks = cursor.fetchall()

    cursor.execute("SELECT * FROM payloads")
    payloads = cursor.fetchall()
    print("Payloads :")
    for p in payloads:
        print(p["ip"], p["port"], p["payload"])

    return render_template('index.html', attacks=attacks, payloads=payloads)

@app.route('/stats')
def stats():

    # Nombre d'attaques par jours
    cursor.execute("SELECT DATE(timestamp) as day, COUNT(*) as total FROM attacks GROUP BY day ORDER BY total DESC LIMIT 7")
    attacks_per_day = cursor.fetchall()

    # Top 5 IPs
    cursor.execute("SELECT ip, COUNT(*) as total FROM attacks GROUP BY ip ORDER BY total DESC LIMIT 5")
    top_ips = cursor.fetchall()

    # Top 5 ports
    cursor.execute("SELECT port, COUNT(*) as total FROM attacks GROUP BY port ORDER BY total DESC LIMIT 5")
    top_ports = cursor.fetchall()

    return render_template('stats.html', attacks_per_day=attacks_per_day, top_ips=top_ips, top_ports=top_ports)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)