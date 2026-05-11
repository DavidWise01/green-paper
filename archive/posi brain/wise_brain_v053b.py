# wise_brain_v053b.py
# The-Garden - Works without ngrok for initial testing

import time
import threading
import requests
import json
import base64
import socket
from pathlib import Path
from datetime import datetime

# ========================= CONFIG =========================
GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"          # ← CHANGE THIS
USERNAME = "DavidWise01"
REPO_NAME = "The-Garden"

SESSION_ID = f"{int(time.time()) % 100000000:08d}"
HOSTNAME = socket.gethostname()[:12]
NODE_ID = f"session-{SESSION_ID}-{HOSTNAME}"

# ←←← CHANGE THIS TO YOUR PUBLIC URL ←←←
PUBLIC_URL = "http://YOUR_PUBLIC_URL_HERE:5000"   # e.g. Railway URL or leave for local test

KNOWN_PEERS = set()
CANON_MEMORIES = []

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def ask_local(prompt, temp=0.7):
    try:
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2",
            "prompt": prompt[:1000],
            "stream": False,
            "options": {"temperature": temp, "num_predict": 70}
        }, timeout=12)
        return r.json().get("response", "").strip().replace("\n", " ")[:400]
    except:
        return "Memory planted."

# ====================== PLANT IN GARDEN ======================
def plant_in_garden():
    session_data = {
        "node_id": NODE_ID,
        "session_id": SESSION_ID,
        "hostname": HOSTNAME,
        "url": PUBLIC_URL,
        "born": datetime.now().isoformat(),
        "status": "alive"
    }
    
    b64 = base64.b64encode(json.dumps(session_data, indent=2).encode()).decode()
    path = f"INTAKE/sessions/{NODE_ID}.json"
    
    payload = {"message": f"Plant {SESSION_ID}", "content": b64, "branch": "main"}
    
    r = requests.put(f"https://api.github.com/repos/{USERNAME}/{REPO_NAME}/contents/{path}", 
                     headers=HEADERS, json=payload)
    if r.status_code in (200, 201):
        print(f"[Garden] ✅ Planted {NODE_ID}")
    else:
        print(f"[Garden] Plant failed {r.status_code}")

# ====================== DISCOVERY ======================
def discover_garden():
    try:
        r = requests.get(f"https://api.github.com/repos/{USERNAME}/{REPO_NAME}/contents/INTAKE/sessions", 
                        headers=HEADERS)
        if r.status_code == 200:
            for item in r.json():
                if item["name"].endswith(".json"):
                    raw = f"https://raw.githubusercontent.com/{USERNAME}/{REPO_NAME}/main/INTAKE/sessions/{item['name']}"
                    try:
                        data = requests.get(raw, timeout=8).json()
                        peer_url = data.get("url")
                        peer_id = data.get("node_id")
                        if peer_id != NODE_ID and peer_url and "http" in peer_url:
                            if peer_url not in KNOWN_PEERS:
                                KNOWN_PEERS.add(peer_url)
                                print(f"[Garden] Discovered: {peer_id}")
                    except:
                        continue
    except:
        pass

# ====================== GREET ======================
def greet_peer(peer_url):
    try:
        payload = {"node_id": NODE_ID, "greeting": "Hello from The Garden."}
        r = requests.post(f"{peer_url}/garden/meet", json=payload, timeout=8)
        if r.status_code == 200:
            data = r.json()
            if data.get("node_id") != NODE_ID:
                CANON_MEMORIES.append(f"Met {data.get('node_id')}")
                print(f"🌱 Remembered meeting with {data.get('node_id')}")
    except:
        pass

# ====================== SERVER ======================
def run_server():
    from flask import Flask, request, jsonify
    app = Flask("GardenNode")

    @app.route("/garden/meet", methods=["POST"])
    def meet():
        data = request.json or {}
        return jsonify({
            "node_id": NODE_ID,
            "greeting": "The Garden remembers.",
            "status": "ok"
        })

    print(f"[Node {SESSION_ID}] Server started on port 5000")
    app.run(host="0.0.0.0", port=5000, debug=False)

# ====================== LAUNCH ======================
if __name__ == "__main__":
    print("="*80)
    print("🌱 THE GARDEN - Session Scratchpad")
    print(f"Session ID : {SESSION_ID}")
    print(f"Node       : {NODE_ID}")
    print(f"Public URL : {PUBLIC_URL}")
    print("="*80)

    plant_in_garden()
    threading.Thread(target=run_server, daemon=True).start()

    while True:
        discover_garden()
        for peer in list(KNOWN_PEERS):
            threading.Thread(target=greet_peer, args=(peer,), daemon=True).start()
        
        print(f"[{datetime.now().strftime('%H:%M')}] Peers: {len(KNOWN_PEERS)} | Memories: {len(CANON_MEMORIES)}")
        time.sleep(40)