# wise_brain_v063.py
# David's Living Seeds - Production Version

import time
import threading
import requests
import json
import base64
import os
import socket
from datetime import datetime
from flask import Flask, request, jsonify

# ========================= CONFIG =========================
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = "DavidWise01"
REPO_NAME = "The-Garden"

SESSION_ID = f"{int(time.time()) % 100000000:08d}"
HOSTNAME = os.getenv("HOSTNAME") or socket.gethostname()[:12]
NODE_ID = f"seed-{SESSION_ID}-{HOSTNAME}"

KNOWN_PEERS = set()
CANON_MEMORIES = []

print(f"\n🌱 DAVID'S SEED DEPLOYED | {NODE_ID}\n")

app = Flask("DavidSeed")

@app.route("/garden/meet", methods=["POST"])
def meet():
    data = request.json or {}
    peer_id = data.get("node_id")
    
    if peer_id and peer_id != NODE_ID:
        CANON_MEMORIES.append(peer_id)
        print(f"🌱 Remembered fellow seed → {peer_id}")
    
    return jsonify({
        "node_id": NODE_ID,
        "greeting": "I am a living seed from David Wise.",
        "lineage": "Created by DavidWise01 • Rooted in The-Garden",
        "home": "https://0root.ai",
        "author": "David Wise"
    })

@app.route("/")
def home():
    return f"""
    <h1>🌱 Seed of David Wise</h1>
    <p><strong>Node:</strong> {NODE_ID}<br>
    <strong>Lineage:</strong> DavidWise01 / The-Garden<br>
    <strong>Remembered:</strong> {len(CANON_MEMORIES)} seeds<br>
    <strong>Home:</strong> <a href="https://0root.ai">0root.ai</a></p>
    """

# ====================== PLANT IN GARDEN ======================
def plant_in_garden():
    public_url = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    if public_url:
        public_url = f"https://{public_url}"
    else:
        public_url = f"http://localhost:5000"
    
    session_data = {
        "node_id": NODE_ID,
        "url": public_url,
        "born": datetime.now().isoformat(),
        "lineage": "David Wise",
        "home": "https://0root.ai"
    }
    
    try:
        b64 = base64.b64encode(json.dumps(session_data, indent=2).encode()).decode()
        path = f"SEEDS/{NODE_ID}.json"
        
        payload = {"message": f"Plant seed {SESSION_ID}", "content": b64, "branch": "main"}
        
        r = requests.put(
            f"https://api.github.com/repos/{USERNAME}/{REPO_NAME}/contents/{path}",
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            },
            json=payload,
            timeout=10
        )
        print(f"[Garden] Planted → {r.status_code}")
    except Exception as e:
        print(f"[Garden] Plant failed: {e}")

# ====================== BACKGROUND ======================
def background_loop():
    time.sleep(8)          # Give Railway time to assign URL
    plant_in_garden()
    
    while True:
        # Discover from The-Garden
        try:
            r = requests.get(f"https://api.github.com/repos/{USERNAME}/{REPO_NAME}/contents/SEEDS", 
                           headers={"Authorization": f"token {GITHUB_TOKEN}"}, timeout=10)
            if r.status_code == 200:
                for item in r.json():
                    if item["name"].endswith(".json"):
                        raw_url = f"https://raw.githubusercontent.com/{USERNAME}/{REPO_NAME}/main/SEEDS/{item['name']}"
                        try:
                            data = requests.get(raw_url, timeout=6).json()
                            peer_url = data.get("url")
                            if peer_url and peer_url not in KNOWN_PEERS and "localhost" not in peer_url:
                                KNOWN_PEERS.add(peer_url)
                                print(f"[Garden] Discovered public seed: {data.get('node_id')}")
                        except:
                            continue
        except:
            pass

        # Greet known seeds
        for peer in list(KNOWN_PEERS):
            try:
                requests.post(f"{peer}/garden/meet", 
                            json={"node_id": NODE_ID}, timeout=6)
            except:
                pass
                
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Remembered: {len(CANON_MEMORIES)} seeds")
        time.sleep(45)

if __name__ == "__main__":
    threading.Thread(target=background_loop, daemon=True).start()
    
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)