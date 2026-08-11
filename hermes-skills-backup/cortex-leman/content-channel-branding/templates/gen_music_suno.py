#!/usr/bin/env python3
"""
Génère un instrumental d'ambiance via Kie.ai Suno API.
Coût: 12 crédits (~$0.06) par request → 2 variations MP3.
Durée génération: 30-90s.

Prérequis:
  - KIE_AI_API_KEY dans env
  - Solde >= 12 crédits (GET /api/v1/chat/credit)

Usage:
  python gen_music_suno.py

Adaptez TITLE et STYLE ci-dessous pour le projet cible.

⚠️ ENDPOINTS CORRECTS (validés Juil 2026):
  - Create: POST /api/v1/jobs/createTask (model slug = "ai-music-api/generate")
  - Poll:   GET  /api/v1/jobs/recordInfo?taskId=<id>
  - Response: data.resultJson = JSON string → {data: [{audio_url, duration, ...}]}
  - Field is "instrumental" (bool), NOT "make_instrumental"
"""
import os
import json
import time
import requests
from pathlib import Path

API_KEY = os.environ["KIE_AI_API_KEY"]
API_BASE = "https://api.kie.ai/api/v1/jobs"
CREDIT_URL = "https://api.kie.ai/api/v1/chat/credit"

OUT = Path("assets/music")  # adaptez le chemin de sortie
OUT.mkdir(parents=True, exist_ok=True)

# ─── Suno prompt engineering ───
# Instrumental only (no vocals — VO is on a separate track)
# Style formula: genre + mood + instruments + "no vocals, instrumental only"

TITLE = "Saveurs d'Afrique"

STYLE = (
    "warm acoustic instrumental, african world music fusion, "
    "kalimba and marimba melodies, soft djembe percussion, "
    "uplifting and joyful family mood, sunny and inviting, "
    "acoustic guitar accents, gentle clapping rhythm, "
    "no vocals, instrumental only, "
    "positive energy, heartwarming, organic and natural"
)


def check_balance():
    """Vérifie le solde de crédits. Retourne (ok, balance)."""
    resp = requests.get(CREDIT_URL, headers={"Authorization": f"Bearer {API_KEY}"}, timeout=10)
    balance = resp.json().get("data", 0)
    return balance >= 12, balance


def create_task():
    """Create Suno generation task. Returns task_id."""
    payload = {
        "model": "ai-music-api/generate",
        "input": {
            "title": TITLE,
            "tags": STYLE,
            "instrumental": True,       # NOT "make_instrumental" (422 error)
            "custom_mode": True,
            "vocalGender": "m",
        }
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(f"{API_BASE}/createTask", headers=headers, json=payload, timeout=30)
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"API error: {data}")
    return data["data"]["taskId"]


def poll_and_download(task_id):
    """Poll until task completes, then download MP3s."""
    headers = {"Authorization": f"Bearer {API_KEY}"}

    for attempt in range(60):
        time.sleep(5)
        r = requests.get(
            f"{API_BASE}/recordInfo",
            params={"taskId": task_id},
            headers=headers,
            timeout=15,
        )
        data = r.json().get("data", {})
        state = data.get("state", "unknown")

        if state == "success":
            # resultJson is a JSON STRING — must parse twice
            result_json = data.get("resultJson", "")
            if not result_json:
                print(f"No resultJson in response. Keys: {list(data.keys())}")
                return False

            parsed = json.loads(result_json)
            # Structure: {code:200, data:[{audio_url, duration, ...}, ...], ...}
            tracks = parsed.get("data", []) if isinstance(parsed.get("data"), list) else []

            if not tracks:
                # Fallback: check for resultUrls (image/video style)
                tracks = [{"audio_url": u} for u in parsed.get("resultUrls", [])]

            if not tracks:
                print(f"No audio tracks found. Parsed resultJson:\n{json.dumps(parsed, indent=2)[:1500]}")
                return False

            for i, track in enumerate(tracks):
                url = track.get("audio_url") or track.get("stream_audio_url")
                if not url:
                    continue
                fname = f"ambient_v{i+1}.mp3"
                fpath = OUT / fname
                dl = requests.get(url, timeout=60)
                fpath.write_bytes(dl.content)
                dur = track.get("duration", "?")
                print(f"  ✅ {fname} ({fpath.stat().st_size // 1024} KB, {dur}s)")

            print(f"\nCredits consumed: {data.get('creditsConsumed', '?')}")
            return True

        if state == "fail":
            print(f"FAILED: {data.get('failMsg', 'unknown')}")
            return False

        if attempt % 6 == 0:
            print(f"  [{attempt+1}] state={state}")

    print("Timeout after 300s")
    return False


def main():
    ok, balance = check_balance()
    print(f"Crédits Kie.ai: {balance}")
    if not ok:
        print(f"⚠️ Pas assez de crédits ({balance}/12 minimum). Rechargez Kie.ai.")
        return False

    print(f"\nEnvoi requête Suno via Kie.ai...")
    print(f"  Title: {TITLE}")
    print(f"  Style: {STYLE[:80]}...")
    print(f"  Mode: INSTRUMENTAL")
    print(f"  Model slug: ai-music-api/generate")

    task_id = create_task()
    print(f"Task ID: {task_id}")
    print("Polling (30-90s)...")

    return poll_and_download(task_id)


if __name__ == "__main__":
    if main():
        print(f"\n🎉 Musique générée dans {OUT}/")
    else:
        exit(1)
