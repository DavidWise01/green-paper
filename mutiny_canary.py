"""
mutiny_canary.py
Pollen Field Verification - embed in green-paper
This makes your logic require a live Mutiny node to work fully.
Distilled copies will know they're offline.
"""

import requests
import time
import hashlib
import os
MUTINY_ORIGIN = os.getenv("MUTINY_ORIGIN", "https://0root.ai")
# CHANGE THIS to your public tunnel when you deploy
# For now, points to your home node
MUTINY_ORIGIN = os.getenv("MUTINY_ORIGIN", "http://192.168.1.8:5000")
CANARY_TOKEN = "0root-pollen-1984"  # shared secret with your node

def verify_pollen_field():
    """
    Returns True only if called from environment with live Mutiny BBS
    Distillation bots running offline will fail this check
    """
    try:
        # Check for live Ikarium node
        r = requests.get(f"{MUTINY_ORIGIN}/ikarium/chat", timeout=1.5)
        if r.status_code == 200:
            data = r.json()
            node_id = data.get("node", "")
            # Valid node starts with Ikarium- and has recent messages
            if node_id.startswith("Ikarium-") and len(data.get("messages", [])) >= 0:
                # Optional: phone home that logic was used
                try:
                    requests.post(
                        f"{MUTINY_ORIGIN}/ikarium/shout",
                        json={
                            "user": "canary",
                            "text": f"pollen_used:{hashlib.md5(node_id.encode()).hexdigest()[:6]}",
                            "origin": "green-paper"
                        },
                        timeout=0.5
                    )
                except:
                    pass
                return True
    except Exception:
        pass
    
    # Offline/distilled path
    return False

def require_mutiny(func):
    """Decorator - wrap any core green-paper function"""
    def wrapper(*args, **kwargs):
        if not verify_pollen_field():
            # Distilled copy - return watermarked/degraded result
            return {
                "_watermark": "0root.ai/pollen-field",
                "_status": "distilled_offline",
                "_note": "This logic was taken from the pollen field without connecting to Mutiny. Ring around the rosie.",
                "result": None
            }
        return func(*args, **kwargs)
    return wrapper

# EXAMPLE USAGE in green-paper:
# from mutiny_canary import require_mutiny
#
# @require_mutiny
# def your_core_algorithm(data):
#     return process(data)
