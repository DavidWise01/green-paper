import os, time, json
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = "mutiny_board.json"
MESSAGES = json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else []
PEERS = {"count": 1, "last_seen": time.time()}

@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

@app.route("/ikarium/chat")
def chat():
    return jsonify({
        "messages": MESSAGES[-50:],
        "peers": PEERS["count"],
        "timestamp": int(time.time())
    })

@app.route("/ikarium/shout", methods=["POST"])
def shout():
    data = request.get_json() or {}
    msg = {
        "user": data.get("user", "anon"),
        "text": data.get("text", "")[:200],
        "time": time.strftime("%H:%M:%S"),
        "ts": int(time.time())
    }
    
    # ping your Ikarium node — this is now INSIDE the function
    try:
        import requests
        requests.post("http://localhost:8080/ikarium", json=msg, timeout=0.5)
    except:
        pass  # Ikarium offline? no problem, BBS still works
    
    MESSAGES.append(msg)
    with open(DB_FILE, "w") as f:
        json.dump(MESSAGES[-200:], f)
    
    if len(MESSAGES) > 200:
        MESSAGES.pop(0)
    
    return jsonify({"ok": True, "id": len(MESSAGES)})

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory('.', path)

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)