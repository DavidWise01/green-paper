from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import time
import os

app = Flask(__name__)
CORS(app)

# THIS IS THE CHANGE — point to the bolted cabinet
DB_PATH = "/data/library.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS shouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    return conn

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/shout", methods=["POST"])
def shout():
    data = request.get_json()
    msg = data.get("message", "").strip()
    if not msg:
        return jsonify({"error": "empty"}), 400

    conn = get_db()
    conn.execute("INSERT INTO shouts (message, created_at) VALUES (?,?)",
                 (msg, time.time()))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/board")
def board():
    conn = get_db()
    rows = conn.execute(
        "SELECT message, created_at FROM shouts ORDER BY id DESC LIMIT 100"
    ).fetchall()
    conn.close()
    return jsonify([{"message": r[0], "time": r[1]} for r in rows])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)