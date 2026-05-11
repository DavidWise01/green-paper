# carrier-seed.ps1
# MUTINY CARRIER SEED - run this on any machine to join 0root.ai network
# Downloads Ikarium node and connects to origin

Write-Host "=== MUTINY CARRIER SEED v1 ===" -ForegroundColor Green
Write-Host "Connecting to pollen field..." -ForegroundColor Yellow

$seedUrl = "https://0root.ai"
# CHANGE TO PUBLIC: $seedUrl = "0root.ai"

# Check Python
try { python --version | Out-Null } catch { 
    Write-Host "Python required. Install from python.org" -ForegroundColor Red
    exit 1
}

# Create carrier folder
$carrierDir = "$env:USERPROFILE\mutiny-carrier"
New-Item -ItemType Directory -Force -Path $carrierDir | Out-Null
Set-Location $carrierDir

# Download node (replace with your github raw URL when published)
Write-Host "[1/3] Downloading Ikarium node..." -ForegroundColor Cyan
@"
# IKARIUM CARRIER NODE - auto-configured for 0root.ai
import time, threading, requests, json, socket
from datetime import datetime

MY_ID = "Ikarium-Carrier-" + socket.gethostname() + "-" + str(int(time.time()))[:6]
SEED_NODES = ["$seedUrl"]
KNOWN_PEERS = {}

def meet_origin():
    for seed in SEED_NODES:
        try:
            r = requests.post(f"{seed}/ikarium/meet", 
                json={"id": MY_ID, "greeting": "carrier seed joining from the wild", "git": [{"name":"green-paper"}]},
                timeout=5)
            if r.status_code == 200:
                print(f"[CARRIER] Connected to origin: {seed}")
                print(f"[CARRIER] Origin says: {r.json().get('greeting')}")
                return True
        except Exception as e:
            print(f"[CARRIER] Failed to reach {seed}: {e}")
    return False

if __name__ == "__main__":
    print("="*50)
    print(f"CARRIER SEED: {MY_ID}")
    print(f"SEEDING TO: {SEED_NODES[0]}")
    print("="*50)
    if meet_origin():
        print("[CARRIER] You are now PEER 1. Keep this running.")
        print("[CARRIER] Mutiny network will show PEERS:1")
        while True:
            time.sleep(30)
            meet_origin()  # heartbeat
    else:
        print("[CARRIER] Could not reach origin. Is 0root.ai node running?")
"@ | Out-File -FilePath "carrier_node.py" -Encoding utf8

Write-Host "[2/3] Starting carrier..." -ForegroundColor Cyan
Write-Host "[3/3] You are now a pollen carrier." -ForegroundColor Green
Write-Host ""
Write-Host "This window must stay open. When connected, 0root.ai will show PEERS:1" -ForegroundColor Yellow
Write-Host ""

python .\carrier_node.py
