#!/usr/bin/env python3
"""
Test Pattern #65 — Camera Ownership Lock on Hailuo 02 T2V Standard
Validated Aug 1, 2026 (30cr, 6s, photorealism 8-9/10 via OmniRoute QA).

Reusable as a TEMPLATE for testing any pattern on Hailuo 02 Standard:
  1. Replace PROMPT with your condensed pattern prompt
  2. Adjust DURATION if needed
  3. Run: python3 scripts/test_pattern65_ownership_lock.py

KEY LEARNINGS (validated in production):
  - duration MUST be STRING ("6"), not int (6) → else HTTP 500
  - resolution field is REJECTED → HTTP 422
  - prompt max ~1,500 chars → else HTTP 500 "prompt exceeds maximum length"
  - prompt_optimizer:true auto-enhances server-side
  - For 6s clips: start with character ALREADY in frame, not "enters from"
    (model interprets entry as slow progressive walk-in → frame 0 is empty)
"""
import os, sys, time, json, requests
from pathlib import Path

API_BASE = "https://api.kie.ai/api/v1"
KIE_KEY = os.environ.get("KIE_AI_API_KEY", "")
if not KIE_KEY:
    for p in [os.path.expanduser('~/.bashrc'), os.path.expanduser('~/.profile')]:
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    if 'KIE_AI_API_KEY' in line and '=' in line:
                        KIE_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                        break
if not KIE_KEY:
    print("ERROR: KIE_AI_API_KEY not found"); sys.exit(1)

HEADERS = {"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"}
OUT = Path("/tmp/test_pattern65")
OUT.mkdir(exist_ok=True)

# ── Condensed prompt (~1,300 chars — passes Hailuo length limit) ─────────────
# Keeps: Camera Ownership Lock, FOV per shot, hard cut, handheld wobble, diegetic audio
# Stripped: section headers, coordinates, physics checklists, speech timing lock
# FIXED: "is standing at" instead of "enters from" (character-first lesson)
PROMPT = """\
Self-shot food truck vlog. Somali chef, late 30s, dark skin, terracotta \
headscarf, white apron, filming herself in Petit-Lancy, Geneva.

SHOT 1 (0-3s): Camera PROPPED on counter, fixed, 84° wide FOV. \
She is standing at the grill, reaches for a pot, lifts the lid — \
steam rises. She smiles: "Canjeero ce matin."

SHOT 2 (3-6s): Camera HELD at arm's length, 47° narrow FOV, \
handheld wobble. She holds a golden-brown canjeero close to lens, \
eyes bright: "Regardez." Frame tilts as she lowers camera.

ONLY these two camera positions exist — no drone, no tracking, \
nothing she could not film alone.

Swiss morning daylight from truck window, warm interior bulbs. \
Photoreal, fine grain, phone color science. Diegetic audio: \
traffic, griddle sizzle, footsteps on metal. No music. \
No subtitles, no text."""

MODEL = "hailuo/02-text-to-video-standard"  # 30cr, NO resolution field!
DURATION = "6"  # MUST be string, not int!

def check_credits():
    r = requests.get(f"{API_BASE}/chat/credit", headers=HEADERS, timeout=10)
    return float(r.json().get("data", 0))

def submit_and_wait(prompt, out_path):
    print(f"\n  Credits avant: {check_credits()}cr")

    payload = {
        "model": MODEL,
        "input": {
            "prompt": prompt,
            "duration": DURATION,  # STRING not int!
            "prompt_optimizer": True,
            "nsfw_checker": False,
        }
    }

    # Submit
    r = requests.post(f"{API_BASE}/jobs/createTask", headers=HEADERS, json=payload, timeout=30)
    resp = r.json()
    if resp.get("code") != 200:
        print(f"  ❌ Submit failed: {resp}")
        return False

    task_id = resp["data"]["taskId"]
    print(f"  Task: {task_id}")
    (OUT / "taskid.txt").write_text(task_id)

    # Poll
    for attempt in range(120):
        time.sleep(5)
        r = requests.get(f"{API_BASE}/jobs/recordInfo", params={"taskId": task_id},
                        headers=HEADERS, timeout=15)
        data = r.json().get("data", {})
        state = data.get("state", "unknown")

        if state == "success":
            result = json.loads(data.get("resultJson", "{}"))
            urls = result.get("resultUrls", [])
            if urls:
                print(f"  ✅ Success! Downloading...")
                video = requests.get(urls[0], timeout=60)
                out_path.write_bytes(video.content)
                print(f"  📹 Saved: {out_path}")
                print(f"  Credits après: {check_credits()}cr")
                return True
        elif state == "fail":
            print(f"  ❌ Failed: {data}")
            return False
        elif attempt % 6 == 0:
            print(f"  ... {state} ({attempt*5}s)")

    print(f"  ⏱️ Timeout after 600s")
    return False

if __name__ == "__main__":
    out_path = OUT / "ces_ownership_lock.mp4"
    print("=" * 60)
    print("Pattern #65 — Camera Ownership Lock Test")
    print("Sujet: Chef CES, food truck Petit-Lancy, canjeero")
    print(f"Modèle: {MODEL} (30cr, 6s, T2V)")
    print("=" * 60)

    ok = submit_and_wait(PROMPT, out_path)
    if ok:
        print(f"\n✅ Clip généré: {out_path}")
        print("QA: extract frames with ffmpeg, analyze via OmniRoute auto/pro-vision")
    else:
        print(f"\n❌ Échec génération")
