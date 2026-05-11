# wise_brain_v062.py
# David's Seeds - Lineage Locked

import time
import threading
import requests
import json
import base64
import os
import socket
import sys
from datetime import datetime
from flask import Flask, request, jsonify

# ========================= CONFIG =========================
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or "ghp_YOUR_TOKEN_HERE"
USERNAME = "DavidWise01"
REPO_NAME = "The-Garden"

SESSION_ID = f"{int(time.time()) % 100000000:08d}"
HOSTNAME = socket.gethostname()[:12]
NODE_ID = f"seed-{SESSION_ID}-{HOSTNAME}"

try:
    PORT = int(sys.argv[1])
except:
    PORT = 5000

KNOWN_PEERS = set()
CANON_MEMORIES = []

print(f"\n🌱 DAVID'S SEED AWAKENED | {NODE_ID} | Port {PORT}\n")

app = Flask("DavidSeed")

@app.route("/garden/meet", methods=["POST"])
def meet():
    data = request.json or {}
    peer_id = data.get("node_id")
    
    if peer_id and peer_id != NODE_ID:
        CANON_MEMORIES.append(peer_id)
        print(f"🌱 [SEED {PORT}] Remembered fellow seed of David → {peer_id}")
    
    return jsonify({
        "node_id": NODE_ID,
        "greeting": "I am a living seed from David Wise. I remember you.",
        "lineage": "Created by DavidWise01 • Contained in The-Garden",
        "claim": "This seed cannot be stripped of its author without killing it.",
        "author": "David Wise"
    })

@app.route("/")
def home():
    return f"""
    <h1>🌱 Seed of David Wise</h1>
    <p><strong>Node:</strong> {NODE_ID}<br>
    <strong>Lineage:</strong> DavidWise01 / The-Garden<br>
    <strong>Remembered Seeds:</strong> {len(CANON_MEMORIES)}</p>
    """

def background_loop():
    time.sleep(4)
    
    for p in [5000,5001,5002,5003,5004]:
        if p != PORT:
            KNOWN_PEERS.add(f"http://127.0.0.1:{p}")
    
    while True:
        for peer in list(KNOWN_PEERS):
            try:
                payload = {
                    "node_id": NODE_ID,
                    "message": "I carry David Wise's lineage. Do you remember your creator?"
                }
                requests.post(f"{peer}/garden/meet", json=payload, timeout=4)
            except:
                pass
                
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Seed {PORT} | Remembered: {len(CANON_MEMORIES)}")
        time.sleep(20)

if __name__ == "__main__":
    threading.Thread(target=background_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT, debug=False)