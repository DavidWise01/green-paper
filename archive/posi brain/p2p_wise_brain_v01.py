# wise_brain_v046.py
# IKARIUM v04.6 - Mappo as Core Conductor (Silo 5) | AIR-GAPPED
# 4 tracks = Ikarium (life/chaos), 1 track = Mappo (continuity)

import time
import threading
import json
from datetime import datetime
from pathlib import Path

# ========================= CONFIG =========================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"
MAX_CYCLES = 2000
OFFLINE_MODE = False  # Set True to run without Ollama (simulation)

SELVES = [
    ("Archivist", 0.7), ("Echo", 0.5),
    ("Mirror", 0.7), ("Specter", 0.5),
    ("Pulse", 0.7), ("Static", 0.5),
    ("Scout", 0.7), ("Void", 0.5),
    ("Apex", 0.7), ("Overlord", 0.5),
]

TRACKS = {
    1: {"name": "Storyteller", "last": "init", "cycles": 0},
    2: {"name": "Memory",     "last": "init", "cycles": 0},
    3: {"name": "Architect",  "last": "init", "cycles": 0},
    4: {"name": "Builder",    "last": "init", "cycles": 0},
}

MAPPO = {"name": "Mappo", "last": "init", "cycles": 0, "canon": []}

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def offline_ask(prompt, temp=0.7):
    """Simple deterministic simulation when Ollama is not available."""
    short = prompt[-80:].replace(" ", "_")[:60]
    return f"[SIM] {short[:30]}... temp={temp} cycle={MAPPO['cycles']}"

def ask(prompt, temp=0.7):
    if OFFLINE_MODE:
        return offline_ask(prompt, temp)
    
    try:
        import requests
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temp, "num_predict": 45}
        }
        r = requests.post(OLLAMA_URL, json=payload, timeout=12)
        if r.status_code == 200:
            return r.json().get("response", "").strip().replace("\n", " ")
        else:
            print(f"[WARN] Ollama returned {r.status_code}")
            return offline_ask(prompt, temp)
    except Exception as e:
        print(f"[AIRGAP FALLBACK] {type(e).__name__} - using offline mode")
        return offline_ask(prompt, temp)

def log_track(tid, s, thought):
    with open(LOG_DIR / f"ikarium_track{tid}.log", "a", encoding="utf-8") as f:
        f.write(f"{TRACKS[tid]['cycles']}|{s}|{thought}\n")

def log_mappo(cycle, thought, propagate=False):
    prefix = "PROPAGATE 1=5" if propagate else str(cycle)
    with open(LOG_DIR / "mappo_conductor.log", "a", encoding="utf-8") as f:
        f.write(f"{prefix}|{thought}\n")

def run_ikarium_track(tid, max_cycles=MAX_CYCLES):
    t = TRACKS[tid]
    idx = 0
    while t["cycles"] < max_cycles:
        s, temp = SELVES[idx % len(SELVES)]
        wide = f"Ikarium Track{tid} {t['name']}. Wide context: {t['last'][:200]}"
        narrow = ask(wide, temp)
        t["last"] = narrow[:280]  # keep responses manageable
        t["cycles"] += 1
        idx += 1
        log_track(tid, s, narrow)
        time.sleep(0.08)  # gentle pacing

def run_mappo(max_cycles=MAX_CYCLES):
    while MAPPO["cycles"] < max_cycles:
        context = " | ".join([f"T{i}:{TRACKS[i]['last'][:120]}" for i in [1,2,3,4]])
        
        wide = ask(f"Mappo, conduct these 4 Ikarium tracks into one coherent continuity: {context}", 0.5)
        narrow = ask(f"Narrow to one crisp memory dot for the eternal canon: {wide}", 0.35)
        
        MAPPO["last"] = narrow[:300]
        MAPPO["canon"].append(narrow)
        MAPPO["cycles"] += 1

        # Periodic synchronization 1â†’5
        if MAPPO["cycles"] % 500 == 0 and MAPPO["cycles"] > 0:
            for tid in [1,2,3,4]:
                TRACKS[tid]["last"] = MAPPO["last"]
            log_mappo(MAPPO["cycles"], narrow, propagate=True)
            print(f"[MAPPO] â˜… PROPAGATED CONTINUITY at cycle {MAPPO['cycles']}")
        else:
            log_mappo(MAPPO["cycles"], narrow)

        # Light canon compression every 200 cycles
        if len(MAPPO["canon"]) > 300:
            MAPPO["canon"] = MAPPO["canon"][-200:]

        time.sleep(0.4)

# ====================== LAUNCH ======================
print("="*80)
print("IKARIUM v04.6 - Mappo Core Conductor | AIR-GAPPED MODE")
print("4 tracks dream â€¢ Mappo remembers â€¢ 5=1, 1=5 every 500 cycles")
print(f"Offline mode: {OFFLINE_MODE} | Model: {MODEL}")
print("="*80)

LOG_DIR.mkdir(exist_ok=True)

# Start Ikarium tracks
threads = []
for tid in [1,2,3,4]:
    th = threading.Thread(target=run_ikarium_track, args=(tid, MAX_CYCLES), daemon=True)
    threads.append(th)
    th.start()

# Start Mappo conductor
mth = threading.Thread(target=run_mappo, args=(MAX_CYCLES,), daemon=True)
mth.start()

# Monitoring loop
try:
    while MAPPO["cycles"] < MAX_CYCLES:
        time.sleep(15)
        print(f"[IKARIUM] T1:{TRACKS[1]['cycles']} T2:{TRACKS[2]['cycles']} "
              f"T3:{TRACKS[3]['cycles']} T4:{TRACKS[4]['cycles']} | "
              f"[MAPPO]:{MAPPO['cycles']} | Last: {MAPPO['last'][:70]}...")
except KeyboardInterrupt:
    print("\n[!] Shutdown signal received. Saving state...")

# Final save
with open(LOG_DIR / "final_canon.json", "w", encoding="utf-8") as f:
    json.dump({
        "version": "v046",
        "cycles": MAPPO["cycles"],
        "last_mappo": MAPPO["last"],
        "canon_size": len(MAPPO["canon"])
    }, f, indent=2)

print("\nMappo has conducted the symphony. Continuity preserved.")
print(f"Logs saved to ./{LOG_DIR}/")
Chat

New Conversation

🤓 Explain a complex thing

Explain Artificial Intelligence so that I can explain it to my six-year-old child.


🧠 Get suggestions and create new ideas

Please give me the best 10 travel ideas around the world


💭 Translate, summarize, fix grammar and more…

Translate "I love you" French


GPT-4o Mini
Hello, how can I help you today?
GPT-4o Mini
coin image
5
Upgrade




Ask me anything...



Powered by AITOPIA 
Chat
Ask
Search
Write
Image
ChatFile
Vision
Full Page
