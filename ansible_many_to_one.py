# ansible_many_to_one.py
# IKARIUM v05.0 - Mutiny Distributed Chat
# Messages gossip to all peers

from flask import send_from_directory

@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

@app.route("/carrier/<path:filename>")
def carrier_files(filename):
    return send_from_directory('carrier', filename)

import os
import time
import threading
import requests
import json
import socket
import hashlib
from pathlib import Path
from datetime import datetime

MY_ID = "Ikarium-" + socket.gethostname() + "-" + str(int(time.time()))
MY_ID = MY_ID[:40]

KNOWN_PEERS = {}
CANON_MEMORIES = []
MESSAGES = []
SEEN_MSG_IDS = set()
STATE_FILE = Path("ikarium_state.json")

def load_state():
    global KNOWN_PEERS, CANON_MEMORIES, MESSAGES, SEEN_MSG_IDS
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            KNOWN_PEERS = data.get("peers", {})
            CANON_MEMORIES = data.get("memories", [])
            MESSAGES = data.get("messages", [])[-50:]
            SEEN_MSG_IDS = set(data.get("seen_ids", []))
            print("[STATE] Loaded " + str(len(KNOWN_PEERS)) + " peers, " + str(len(MESSAGES)) + " msgs")
        except Exception as e:
            print("[STATE] Load failed: " + str(e))

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
    """Gossip message to all known peers"""
    for pid, info in list(KNOWN_PEERS.items()):
        url = info.get("url", "")
        if url.startswith("http") and pid != msg_data.get("origin"):
            try:
                threading.Thread(
                    target=lambda u: requests.post(u + "/ikarium/shout", 
                        json=msg_data, timeout=3),
                    args=(url,),
                    daemon=True
                ).start()
            except:
                pass

def run_http_server():
    from flask import Flask, request, jsonify
    app = Flask("Ikarium")

    @app.after_request
    def add_cors(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return response

    @app.route("/ikarium/meet", methods=["POST", "OPTIONS"])
    def meet():
        if request.method == "OPTIONS":
            return "", 200
        data = request.json or {}
        peer_id = data.get("id")
        if peer_id and peer_id != MY_ID:
            # Store peer URL properly
            peer_url = "http://" + request.remote_addr + ":5000"
            KNOWN_PEERS[peer_id] = {
                "url": peer_url,
                "last_seen": datetime.now().isoformat(),
                "git": data.get("git", []),
                "greeting": data.get("greeting", "")
            }
            save_state()
        return jsonify({"id": MY_ID, "greeting": "Ikarium remembers you.", "status": "ok"})

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
        
        # Create unique message ID to prevent loops
        user = data.get("user", "anon")[:20]
        origin = data.get("origin", data.get("id", MY_ID))
        timestamp = data.get("time", datetime.now().strftime("%H:%M:%S"))
        
        # Hash to create unique ID
        msg_id = hashlib.md5(f"{origin}{timestamp}{text}".encode()).hexdigest()[:12]
        
        # Prevent duplicate processing
        if msg_id in SEEN_MSG_IDS:
            return jsonify({"status": "duplicate", "id": msg_id})
        
        SEEN_MSG_IDS.add(msg_id)
        
        msg = {
            "user": user,
            "text": text,
            "node": origin,
            "time": timestamp,
            "msg_id": msg_id,
            "relayed": data.get("relay", False)
        }
        
        MESSAGES.append(msg)
        if len(MESSAGES) > 50:
            MESSAGES.pop(0)
        
        print("[SHOUT] " + user + "@" + origin[:12] + ": " + text[:60])
        save_state()
        
        # GOSSIP TO PEERS - this is the relay
        if not data.get("relay"):  # Only origin broadcasts, relays don't re-broadcast to prevent storms
            broadcast_data = {
                "user": user,
                "text": text,
                "origin": origin,
                "time": timestamp,
                "msg_id": msg_id,
                "relay": True
            }
            threading.Thread(target=broadcast_message, args=(broadcast_data,), daemon=True).start()
        
        return jsonify({"status": "broadcast", "id": msg_id, "peers": len(KNOWN_PEERS)})

    @app.route("/ikarium/chat", methods=["GET"])
    def chat():
        return jsonify({
            "messages": MESSAGES[-25:],
            "node": MY_ID,
            "peers": len(KNOWN_PEERS)
        })

    @app.route("/", methods=["GET"])
    def home():
        return "IKARIUM " + MY_ID + " - MUTINY RELAY ACTIVE"

    port = int(os.environ.get("PORT", 5000))
    print("[HTTP] http://0.0.0.0:" + str(port) + " - DISTRIBUTED CHAT")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    print("="*60)
    print("IKARIUM v05.0 - DISTRIBUTED MUTINY")
    print("Node: " + MY_ID)
    print("Messages will gossip to all peers")
    print("="*60)
    load_state()
    threading.Thread(target=run_http_server, daemon=True).start()
    try:
        while True:
            time.sleep(60)
            save_state()
    except KeyboardInterrupt:
        save_state()
