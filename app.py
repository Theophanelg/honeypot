from flask import Flask, render_template, request, Response, g
from utils.db import get_filtered_logs
import csv
import io
import json
import sqlite3

app = Flask(__name__)

DB_PATH = "honeypot.db"

def get_db():
    """Ouvre une connexion par requête Flask (bonne pratique)."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Ferme proprement la connexion en fin de requête."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    """
    Accueil : affiche la liste des attaques filtrées.
    """
    service = request.args.get('service')
    date = request.args.get('date')

    attacks = get_filtered_logs(service=service, start_date=date, end_date=date)

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM payloads")
    payloads = cursor.fetchall()

    return render_template('index.html', attacks=attacks, payloads=payloads)

@app.route('/stats')
def stats():
    """
    Affiche les statistiques d'attaque.
    """
    ip = request.args.get('ip')
    service = request.args.get('service')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conditions = []
    values = []

    if ip:
        conditions.append("a.ip = ?")
        values.append(ip)
    if service:
        conditions.append("a.service = ?")
        values.append(service)
    if start_date:
        conditions.append("DATE(a.timestamp) >= ?")
        values.append(start_date)
    if end_date:
        conditions.append("DATE(a.timestamp) <= ?")
        values.append(end_date)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    db = get_db()
    cursor = db.cursor()

    # Attaques par jour
    cursor.execute(f"""
        SELECT DATE(a.timestamp) as day, COUNT(*) as total
        FROM attacks a
        {where_clause}
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
    """, values)
    attacks_per_day = cursor.fetchall()

    # Top IPs avec score de réputation
    cursor.execute(f"""
        SELECT a.ip, COUNT(*) as total, r.abuse_score
        FROM attacks a
        LEFT JOIN ip_reputation r ON a.ip = r.ip
        {where_clause}
        GROUP BY a.ip
        ORDER BY total DESC
        LIMIT 5
    """, values)
    raw_top_ips = cursor.fetchall()
    top_ips = []
    for row in raw_top_ips:
        ip, total, score = row
        score = int(score) if score is not None else None
        top_ips.append((ip, total, score))

    # Top ports
    cursor.execute(f"""
        SELECT a.port, COUNT(*) as total
        FROM attacks a
        {where_clause}
        GROUP BY a.port
        ORDER BY total DESC
        LIMIT 5
    """, values)
    top_ports = cursor.fetchall()

    # Liste complète des attaques
    cursor.execute(f"""
        SELECT * FROM attacks a
        {where_clause}
        ORDER BY a.timestamp DESC
        LIMIT 100
    """, values)
    filtered_attacks = cursor.fetchall()

    return render_template('stats.html',
                           attacks_per_day=attacks_per_day,
                           top_ips=top_ips,
                           top_ports=top_ports,
                           filtered_attacks=filtered_attacks,
                           ip=ip,
                           service=service,
                           start_date=start_date,
                           end_date=end_date)

@app.route("/export")
def export():
    """
    Export des logs filtrés au format CSV ou JSON.
    """
    ip = request.args.get("ip")
    service = request.args.get("service")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    fmt = request.args.get("format", "csv")

    entries = get_filtered_logs(ip, service, start_date, end_date)

    if not entries:
        return "Aucune donnée à exporter", 404

    if fmt == "json":
        response = app.response_class(
            response=json.dumps([dict(row) for row in entries], indent=2),
            mimetype="application/json"
        )
        response.headers["Content-Disposition"] = "attachment; filename=logs.json"
        return response

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=entries[0].keys())
    writer.writeheader()
    writer.writerows([dict(row) for row in entries])
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=logs.csv"
    return response

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
