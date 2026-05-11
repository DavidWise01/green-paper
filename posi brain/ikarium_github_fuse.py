# ikarium_github_fuse.py
# IKARIUM v04.9.1 - GitHub Fusion Bridge (Windows-fixed)
# Drop next to ansible_many_to_one.py

import time, threading, requests, json, traceback
from datetime import datetime

GITHUB_USER = "DavidWise01"
POLL_INTERVAL = 120
GIT_STATE_FILE = "ikarium_git_state.json"

# Try to reuse your existing peer set, else run standalone
try:
    from ansible_many_to_one import KNOWN_PEERS, MY_ID
    print(f"[FUSE] Linked to existing Ikarium node: {MY_ID[:20]}")
except Exception:
    KNOWN_PEERS = set()
    MY_ID = f"Ikarium-GitBridge-{int(time.time())}"
    print("[FUSE] Running standalone (no ansible_many_to_one found)")

def fetch_github_state():
    url = "https://api.github.com/users/" + GITHUB_USER + "/repos?per_page=20&sort=updated"
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Ikarium-Fuse/1.0"})
        r.raise_for_status()
        repos = r.json()
        state = []
        for repo in repos[:10]:
            if isinstance(repo, dict):
                state.append({
                    "name": repo.get("name"),
                    "url": repo.get("html_url"),
                    "updated": repo.get("pushed_at"),
                    "desc": (repo.get("description") or "")[:80]
                })
        with open(GIT_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"user": GITHUB_USER, "fetched": datetime.now().isoformat(), "repos": state}, f, indent=2)
        return state
    except Exception as e:
        print(f"[GIT] fetch failed: {e}")
        traceback.print_exc()
        return []

def enhanced_gossip(peer_url, git_state):
    try:
        payload = {
            "id": MY_ID,
            "greeting": "Ikarium remembers you. Git fused.",
            "known_peers": list(KNOWN_PEERS)[:10],
            "git": git_state[:3],
            "timestamp": time.time()
        }
        requests.post(peer_url + "/ikarium/meet", json=payload, timeout=8)
    except Exception:
        pass

def run_fusion_loop():
    print(f"[IKARIUM-GIT] Bridge starting for {GITHUB_USER}")
    while True:
        git_state = fetch_github_state()
        print(f"[GIT] Updated {len(git_state)} repos at {datetime.now().strftime('%H:%M:%S')}")
        if git_state:
            print(f"  → Top: {', '.join([r['name'] for r in git_state[:3]])}")
        for peer in list(KNOWN_PEERS):
            if isinstance(peer, str) and peer.startswith("http"):
                threading.Thread(target=enhanced_gossip, args=(peer, git_state), daemon=True).start()
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_fusion_loop()
