from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import time
import os

app = Flask(__name__)
CORS(app)

# THE PERSISTENT PATH - this is the bolted cabinet
DB_PATH = "/data/library.db"

def get_db():
    # make sure /data exists (Railway creates it when volume mounts)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
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
    data = request.get_json(silent=True) or {}
    msg = data.get("message", "").strip()
    if not msg:
        return jsonify({"error": "empty"}), 400

    try:
        conn = get_db()
        conn.execute("INSERT INTO shouts (message, created_at) VALUES (?,?)",
                     (msg, time.time()))
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "saved_to": DB_PATH})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/board")
def board():
    try:
        conn = get_db()
        rows = conn.execute(
            "SELECT message, created_at FROM shouts ORDER BY id DESC LIMIT 100"
        ).fetchall()
        conn.close()
        return jsonify([{"message": r[0], "time": r[1]} for r in rows])
    except Exception as e:
        return jsonify([])

@app.route("/canary")
def canary():
    """Health check: is the library alive and where is it writing?"""
    info = {
        "db_path": DB_PATH,
        "volume_mounted": os.path.isdir("/data"),
        "db_exists": os.path.exists(DB_PATH),
        "writable": os.access("/data", os.W_OK) if os.path.isdir("/data") else False,
    }
    try:
        if info["db_exists"]:
            info["db_size_bytes"] = os.path.getsize(DB_PATH)
            conn = get_db()
            count = conn.execute("SELECT COUNT(*) FROM shouts").fetchone()[0]
            conn.close()
            info["shout_count"] = count
        else:
            info["db_size_bytes"] = 0
            info["shout_count"] = 0
    except Exception as e:
        info["error"] = str(e)
    
    info["status"] = "alive" if info["volume_mounted"] and info["writable"] else "volume_missing"
    return jsonify(info)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
