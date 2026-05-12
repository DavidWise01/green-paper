from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import time
import os

app = Flask(__name__)
CORS(app)

DB_PATH = "/data/library.db"

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    # base table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS shouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    # migrate: add handle column if missing
    try:
        conn.execute("ALTER TABLE shouts ADD COLUMN handle TEXT DEFAULT 'anon'")
    except sqlite3.OperationalError:
        pass  # already exists
    # ensure default for old rows
    conn.execute("UPDATE shouts SET handle='anon' WHERE handle IS NULL")
    conn.commit()
    return conn

@app.route("/")
def home():
    response = send_from_directory(".", "index.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/shout", methods=["POST"])
def shout():
    data = request.get_json(silent=True) or {}
    msg = data.get("message", "").strip()
    handle = data.get("handle", "anon").strip()[:32] or "anon"
    if not msg:
        return jsonify({"error": "empty"}), 400
    try:
        conn = get_db()
        conn.execute("INSERT INTO shouts (message, created_at, handle) VALUES (?,?,?)",
                     (msg, time.time(), handle))
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/board")
def board():
    try:
        conn = get_db()
        rows = conn.execute(
            "SELECT handle, message, created_at FROM shouts ORDER BY id DESC LIMIT 200"
        ).fetchall()
        conn.close()
        return jsonify([{"handle": r[0] or "anon", "message": r[1], "time": r[2]} for r in rows])
    except Exception as e:
        return jsonify([])

@app.route("/canary")
def canary():
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
            handles = conn.execute("SELECT COUNT(DISTINCT handle) FROM shouts").fetchone()[0]
            conn.close()
            info["shout_count"] = count
            info["unique_handles"] = handles
        else:
            info["db_size_bytes"] = 0
            info["shout_count"] = 0
            info["unique_handles"] = 0
    except Exception as e:
        info["error"] = str(e)
    info["status"] = "alive" if info["volume_mounted"] and info["writable"] else "volume_missing"
    return jsonify(info)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
