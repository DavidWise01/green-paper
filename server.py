from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import time
import os

app = Flask(__name__)

# this is the notebook on the bolted-down shelf
DB_PATH = "/data/library.db"

# make the notebook if it doesn't exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS shouts (
            id INTEGER PRIMARY KEY,
            message TEXT,
            created_at REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/shout", methods=["POST"])
def shout():
    msg = request.json.get("message", "")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO shouts (message, created_at) VALUES (?,?)",
                 (msg, time.time()))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/board")
def board():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT message, created_at FROM shouts ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    # turn it into a list the browser can read
    out = [{"message": r[0], "time": r[1]} for r in rows]
    return jsonify(out)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)