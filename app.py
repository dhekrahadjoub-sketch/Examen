"""
Backend Flask — Examen TEC (800 étudiants)
Déployez sur Render.com (gratuit) ou Railway.app
"""
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json, csv, io, os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Autorise les requêtes depuis GitHub Pages

# ── Stockage en mémoire (suffisant pour un examen de quelques heures) ──
exam_status = {"status": "none"}
copies = []

# ── Statut ──────────────────────────────────────────────────────────────
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(exam_status)

@app.route('/api/status', methods=['POST'])
def set_status():
    data = request.get_json()
    exam_status['status'] = data.get('status', 'none')
    return jsonify({"ok": True})

# ── Copies ───────────────────────────────────────────────────────────────
@app.route('/api/copies', methods=['GET'])
def get_copies():
    return jsonify(copies)

@app.route('/api/copies', methods=['POST'])
def add_copy():
    record = request.get_json()
    record['server_time'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    copies.append(record)
    print(f"[COPY] {record.get('name')} — {record.get('score')}/20")
    return jsonify({"ok": True}), 201

@app.route('/api/copies/<int:idx>', methods=['DELETE'])
def delete_copy(idx):
    if 0 <= idx < len(copies):
        copies.pop(idx)
        return jsonify({"ok": True})
    return jsonify({"error": "Not found"}), 404

@app.route('/api/copies/clear', methods=['POST'])
def clear_copies():
    copies.clear()
    return jsonify({"ok": True})

# ── Stats ────────────────────────────────────────────────────────────────
@app.route('/api/stats', methods=['GET'])
def get_stats():
    if not copies:
        return jsonify({"total": 0, "avg": 0, "max": 0, "min": 0})
    scores = [c.get('score', 0) for c in copies]
    return jsonify({
        "total": len(copies),
        "avg":   round(sum(scores) / len(scores), 2),
        "max":   round(max(scores), 2),
        "min":   round(min(scores), 2)
    })

# ── Export CSV ────────────────────────────────────────────────────────────
@app.route('/api/export', methods=['GET'])
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['#', 'Nom', 'Matricule', 'Filière', 'Groupe', 'Score/20', 'Date'])
    for i, c in enumerate(copies, 1):
        writer.writerow([i, c.get('name'), c.get('matricule'), c.get('filiere'),
                         c.get('group'), c.get('score'), c.get('timestamp')])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=copies_tec.csv"}
    )

# ── Health check ──────────────────────────────────────────────────────────
@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "ok", "copies": len(copies), "exam": exam_status['status']})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
