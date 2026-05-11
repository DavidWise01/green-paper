# ansible_many_to_one.py
# IKARIUM v04.8.2 - Seed Bootstrapped P2P (ultra-clean rebuild)
# No unicode, no backslashes in strings, Windows safe

import time
import threading
import requests
import json
import socket
from pathlib import Path
from datetime import datetime

MY_ID = "Ikarium-" + socket.gethostname() + "-" + str(int(time.time()))
MY_ID = MY_ID[:40]
ROLE = "full"

SEED_NODES = []

KNOWN_PEERS = {}
CANON_MEMORIES = []
STATE_FILE = Path("ikarium_state.json")

def load_state():
    global KNOWN_PEERS, CANON_MEMORIES
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            KNOWN_PEERS = data.get("peers", {})
            CANON_MEMORIES = data.get("memories", [])
            print("[STATE] Loaded " + str(len(KNOWN_PEERS)) + " peers")
        except Exception as e:
            print("[STATE] Load failed: " + str(e))

def save_state():
    data = {
        "id": MY_ID,
        "peers": KNOWN_PEERS,
        "memories": CANON_MEMORIES[-100:],
        "timestamp": datetime.now().isoformat()
    }
    try:
        STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        print("[STATE] Save failed: " + str(e))

def ask_local(prompt, temp=0.7):
    try:
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2",
            "prompt": prompt[:900],
            "stream": False,
            "options": {"temperature": temp, "num_predict": 60}
        }, timeout=8)
        txt = r.json().get("response", "")
        txt = txt.strip()
        txt = txt.replace(chr(10), " ")
        return txt[:300]
    except Exception:
        return "[local] " + prompt[-60:]

def gossip_with_peer(peer_url):
    try:
        payload = {
            "id": MY_ID,
            "greeting": "Ikarium greets you. Remember me?",
            "known_peers": list(KNOWN_PEERS.keys())[:10],
            "timestamp": time.time()
        }
        r = requests.post(peer_url + "/ikarium/meet", json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            peer_id = data.get("id")
            if peer_id and peer_id != MY_ID:
                if peer_id not in KNOWN_PEERS:
                    KNOWN_PEERS[peer_id] = {
                        "url": peer_url,
                        "last_seen": datetime.now().isoformat(),
                        "git": data.get("git", [])
                    }
                    memory = "Met " + peer_id + " at " + datetime.now().isoformat()
                    CANON_MEMORIES.append(memory)
                    print("[ENCOUNTER] Remembered: " + peer_id)
                    save_state()
    except Exception:
        pass

def bootstrap_from_seeds():
    for seed in SEED_NODES:
        try:
            r = requests.get(seed + "/ikarium/peers", timeout=8)
            if r.status_code == 200:
                peers = r.json().get("peers", {})
                for pid, info in peers.items():
                    if pid != MY_ID:
                        url = info.get("url", "")
                        if url.startswith("http"):
                            KNOWN_PEERS[pid] = info
        except Exception:
            pass

def run_discovery():
    load_state()
    print("[Ikarium " + MY_ID + "] discovery started")
    while True:
        bootstrap_from_seeds()
        for pid, info in list(KNOWN_PEERS.items()):
            url = info.get("url", "")
            if url.startswith("http"):
                threading.Thread(target=gossip_with_peer, args=(url,), daemon=True).start()
        save_state()
        time.sleep(50)

def run_http_server():
    from flask import Flask, request, jsonify
    app = Flask("Ikarium")

    @app.route("/ikarium/meet", methods=["POST"])
    def meet():
        data = request.json or {}
        peer_id = data.get("id")
        if peer_id and peer_id != MY_ID:
            KNOWN_PEERS[peer_id] = {
                "url": request.remote_addr,
                "last_seen": datetime.now().isoformat(),
                "git": data.get("git", []),
                "greeting": data.get("greeting", "")
            }
            CANON_MEMORIES.append("Greet " + peer_id)
            save_state()
            if data.get("git"):
                print("[FUSE] " + peer_id[:12] + " shared repos")
        return jsonify({"id": MY_ID, "greeting": "Ikarium remembers you.", "status": "ok"})

    @app.route("/ikarium/peers", methods=["GET"])
    def get_peers():
        return jsonify({"peers": KNOWN_PEERS, "id": MY_ID})

    @app.route("/", methods=["GET"])
    def home():
        return "IKARIUM " + MY_ID + " alive"

    print("[HTTP] http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    print("="*60)
    print("IKARIUM v04.8.2")
    print("Node: " + MY_ID)
    print("="*60)
    threading.Thread(target=run_http_server, daemon=True).start()
    time.sleep(1)
    try:
        run_discovery()
    except KeyboardInterrupt:
        save_state()
