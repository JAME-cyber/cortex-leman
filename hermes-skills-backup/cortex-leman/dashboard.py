from flask import Flask, jsonify, render_template_string
import sqlite3
import os

# Initialiser la base de données
DB_PATH = "/tmp/socialpulse.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            content TEXT,
            validation_score REAL,
            clicks INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            generated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Créer l'app Flask
app = Flask(__name__)

@app.route("/api/stats")
def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total, AVG(validation_score) as avg_score FROM posts")
    stats = cursor.fetchone()
    conn.close()
    return jsonify({
        "total_posts": stats[0],
        "avg_validation_score": round(stats[1] or 0, 2),
        "clicks": 0,
        "shares": 0
    })

@app.route("/")
def dashboard():
    return render_template_string('''
    <div style="background: #0D2538; color: #E8E8E8; padding: 2rem; border: 2px solid #1E3A8A; border-radius: 12px; font-family: 'Segoe UI', sans-serif; box-shadow: 0 4px 16px rgba(30, 58, 138, 0.3);">
        <h1 style="color: #FFFFFF; text-align: center; margin-bottom: 1rem; border-bottom: 1px solid #FF6B35; padding-bottom: 0.5rem;">
            🛡️ CORTEX LEMAN - SOCIALPULSE
        </h1>
        <div style="font-size: 1.2em; line-height: 1.6;">
            <p><strong>Total posts :</strong> <span style="color: #00C851; font-weight: 600;">{{ stats.total_posts }}</span></p>
            <p><strong>Score validation (moyen) :</strong> <span style="color: #FF6B35; font-weight: 600;">{{ stats.avg_validation_score }}</span></p>
            <p><strong>⚠️</strong> Aucun suivi des clics/shares (à ajouter)</p>
        </div>
        <p><a href="/api/stats" style="color: #2563EB; text-decoration: none; font-size: 0.9em;">📊 API Stats JSON</a></p>
    </div>
    ''', stats=get_stats().json)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001)