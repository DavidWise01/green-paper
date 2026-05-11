# server.py
# IKARIUM v05.1 - Railway Ready
# Serves Mutiny BBS + API from 0root.ai

import time
import threading
import requests
import json
import socket
import hashlib
import os
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

MY_ID = "Ikarium-" + socket.gethostname() + "-" + str(int(time.time()))
MY_ID = MY_ID[:40]

KNOWN_PEERS = {}
CANON_MEMORIES = []
MESSAGES = []
SEEN_MSG_IDS = set()
STATE_FILE = Path("ikarium_state.json")
PORT = int(os.getenv("PORT", 5000))

def load_state():
    global KNOWN_PEERS, CANON_MEMORIES, MESSAGES, SEEN_MSG_IDS
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            KNOWN_PEERS = data.get("peers", {})
            CANON_MEMORIES = data.get("memories", [])
            MESSAGES = data.get("messages", [])[-50:]
            SEEN_MSG_IDS = set(data.get("seen_ids", []))
            print(f"[STATE] Loaded {len(KNOWN_PEERS)} peers, {len(MESSAGES)} msgs")
        except Exception as e:
            print(f"[STATE] Load failed: {e}")

def save_state():
    data = {
        "id": MY_ID,
        "peers": KNOWN_PEERS,
        "memories": CANON_MEMORIES[-100:],
        "messages": MESSAGES[-50:],
        "seen_ids": list(SEEN_MSG_IDS)[-200:],
        "timestamp": datetime.now().isoformat()
    }
    try:
        STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except:
        pass

def broadcast_message(msg_data):
    for pid, info in list(KNOWN_PEERS.items()):
        url = info.get("url", "")
        if url.startswith("http") and pid != msg_data.get("origin"):
            try:
                threading.Thread(
                    target=lambda u: requests.post(u + "/ikarium/shout", json=msg_data, timeout=3),
                    args=(url,), daemon=True
                ).start()
            except:
                pass

app = Flask("Ikarium", static_folder='.', static_url_path='')

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

# --- STATIC FILES FOR 0ROOT.AI ---
@app.route("/")
def home():
    # Serves index.html (your Mutiny BBS)
    return send_from_directory('.', 'index.html')

@app.route("/carrier/<path:filename>")
def carrier_files(filename):
    return send_from_directory('carrier', filename)

@app.route("/<path:path>")
def static_files(path):
    # Serve any other static files (css, js, etc)
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "404", 404

# --- IKARIUM API ---
@app.route("/ikarium/meet", methods=["POST", "OPTIONS"])
def meet():
    if request.method == "OPTIONS":
        return "", 200
    data = request.json or {}
    peer_id = data.get("id")
    if peer_id and peer_id != MY_ID:
        # Build peer URL from request
        proto = "https" if request.is_secure else "http"
        peer_url = f"{proto}://{request.host}"
        # If peer is external, use their provided URL or origin
        if request.headers.get('Origin'):
            peer_url = request.headers.get('Origin')
        
        KNOWN_PEERS[peer_id] = {
            "url": peer_url,
            "last_seen": datetime.now().isoformat(),
            "git": data.get("git", []),
            "greeting": data.get("greeting", "")
        }
        save_state()
        print(f"[MEET] {peer_id} from {peer_url}")
    return jsonify({"id": MY_ID, "greeting": "Ikarium remembers you. Welcome to 0root.", "status": "ok"})

@app.route("/ikarium/peers", methods=["GET"])
def get_peers():
    return jsonify({"peers": KNOWN_PEERS, "id": MY_ID, "messages": len(MESSAGES)})

@app.route("/ikarium/shout", methods=["POST", "OPTIONS"])
def shout():
    if request.method == "OPTIONS":
        return "", 200
    
    data = request.json or {}
    text = data.get("text", "")[:200].strip()
    if not text:
        return jsonify({"status": "empty"}), 400
    
    user = data.get("user", "anon")[:20]
    origin = data.get("origin", data.get("id", MY_ID))
    timestamp = data.get("time", datetime.now().strftime("%H:%M:%S"))
    
    msg_id = hashlib.md5(f"{origin}{timestamp}{text}".encode()).hexdigest()[:12]
    
    if msg_id in SEEN_MSG_IDS:
        return jsonify({"status": "duplicate"})
    
    SEEN_MSG_IDS.add(msg_id)
    msg = {"user": user, "text": text, "node": origin, "time": timestamp, "msg_id": msg_id}
    MESSAGES.append(msg)
    if len(MESSAGES) > 50:
        MESSAGES.pop(0)
    
    print(f"[SHOUT] {user}@{origin[:12]}: {text[:60]}")
    save_state()
    
    if not data.get("relay"):
        broadcast_data = {**data, "origin": origin, "msg_id": msg_id, "relay": True, "time": timestamp}
        threading.Thread(target=broadcast_message, args=(broadcast_data,), daemon=True).start()
    
    return jsonify({"status": "broadcast", "id": msg_id, "peers": len(KNOWN_PEERS)})

@app.route("/ikarium/chat", methods=["GET"])
def chat():
    return jsonify({"messages": MESSAGES[-25:], "node": MY_ID, "peers": len(KNOWN_PEERS)})

if __name__ == "__main__":
    print("="*60)
    print("IKARIUM v05.1 - RAILWAY DEPLOY")
    print(f"Node: {MY_ID}")
    print(f"Port: {PORT}")
    print("Serving Mutiny BBS at /")
    print("="*60)
    load_state()
    app.run(host="0.0.0.0", port=PORT, debug=False)
