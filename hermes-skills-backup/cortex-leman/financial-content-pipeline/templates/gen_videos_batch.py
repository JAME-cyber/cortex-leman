#!/usr/bin/env python3
"""Template: batch parallel video generation via Kie.ai (Seedance / Veo / Kling).

Usage:
  1. Edit SCENES below (name + prompt per clip)
  2. Edit OUT_DIR, aspect_ratio, duration, resolution
  3. Edit MODEL (see references/kie-ai-video-models.md for model IDs)
  4. python3 gen_videos_batch.py

Features:
  - ThreadPoolExecutor (max_workers=3) for parallel generation
  - Skip existing clips (idempotent re-runs)
  - Credit tracking before/after
  - Recovery: re-run the script or gen_video() on the failed clip individually

Requirements:
  - KIE_API_KEY or KIE_AI_API_KEY env var
  - Wrapper: kie_client.py in the same directory or sys.path
    (see african-heroes/scripts/kie_client.py for reference implementation)

Validated in production: 6 clips Seedance 480p 9:16 5s, 2026-07-22 (african-heroes Nzinga).
"""
import sys
import json
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── CONFIG ──────────────────────────────────────────────────────────────
OUT_DIR = Path("./broll_video")
MODEL = "bytedance/seedance-2-fast"  # see references/kie-ai-video-models.md
ASPECT_RATIO = "9:16"
DURATION = 5          # seconds (4-15 for Seedance)
RESOLUTION = "480p"   # 480p or 720p (Seedance); 720p/1080p/4k (Veo)
GENERATE_AUDIO = False
MAX_WORKERS = 3
TIMEOUT = 300         # seconds per clip polling

# ── SCENES ──────────────────────────────────────────────────────────────
# Each scene: {name, prompt}. The name becomes the output filename.
SCENES = [
    {
        "name": "scene_01",
        "prompt": (
            "Describe the scene here. Be specific about actions, camera movement, "
            "lighting, and style. 3-20000 chars. No text, no modern elements."
        ),
    },
    {
        "name": "scene_02",
        "prompt": (
            "Another scene description..."
        ),
    },
    # Add more scenes as needed
]


# ── KIE CLIENT (inline minimal — or import from kie_client.py) ──────────
class KieClient:
    API = "https://api.kie.ai/api/v1"

    def __init__(self):
        key = (
            os.environ.get("KIE_API_KEY")
            or os.environ.get("KIE_AI_API_KEY")
        )
        if not key:
            raise RuntimeError("KIE_API_KEY or KIE_AI_API_KEY not set")
        self.key = key

    def _headers(self):
        return {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}

    def get_credits(self):
        r = requests.get(f"{self.API}/chat/credit", headers=self._headers(), timeout=15)
        return r.json().get("data", 0)

    def create_task(self, prompt):
        body = {
            "model": MODEL,
            "input": {
                "prompt": prompt,
                "resolution": RESOLUTION,
                "aspect_ratio": ASPECT_RATIO,
                "duration": DURATION,
                "generate_audio": GENERATE_AUDIO,
            },
        }
        r = requests.post(f"{self.API}/jobs/createTask", json=body, headers=self._headers(), timeout=30)
        data = r.json()
        if data.get("code") != 200:
            raise RuntimeError(f"createTask failed: {data}")
        return data["data"]["taskId"]

    def poll_task(self, task_id):
        for i in range(TIMEOUT // 10 + 1):
            r = requests.get(
                f"{self.API}/jobs/recordInfo",
                params={"taskId": task_id},
                headers=self._headers(),
                timeout=15,
            )
            data = r.json().get("data", {})
            state = data.get("state", "")
            if state == "success":
                result = json.loads(data.get("resultJson", "{}"))
                urls = result.get("resultUrls", [])
                if urls:
                    return urls[0]
                raise RuntimeError("success but no resultUrls")
            elif state == "fail":
                raise RuntimeError(f"task failed: {data.get('failMsg', 'unknown')}")
            elapsed = i * 10
            if elapsed % 30 == 0:
                print(f"    ... waiting ({elapsed}s elapsed)")
            time.sleep(10)
        raise TimeoutError(f"Timed out after {TIMEOUT}s")

    def download(self, url, out_path):
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)

    def gen_one(self, scene):
        """Generate a single clip. Returns (name, success, message)."""
        name = scene["name"]
        out_path = OUT_DIR / f"{name}.mp4"
        if out_path.exists():
            return (name, True, "skip (exists)")
        try:
            tid = self.create_task(scene["prompt"])
            print(f"    task: {tid}")
            url = self.poll_task(tid)
            self.download(url, out_path)
            size_kb = out_path.stat().st_size // 1024
            return (name, True, f"{size_kb} KB")
        except Exception as e:
            return (name, False, str(e))


# ── MAIN ────────────────────────────────────────────────────────────────
import os

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    kc = KieClient()
    credits_start = kc.get_credits()
    print(f"Crédits au départ: {credits_start}")
    print(f"Scènes à générer: {len(SCENES)}")
    print(f"Modèle: {MODEL} {RESOLUTION} {ASPECT_RATIO} {DURATION}s")
    print()

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(kc.gen_one, scene): scene["name"] for scene in SCENES}
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                status = "✅" if result[1] else "❌"
                print(f"\n{status} {result[0]}: {result[2]}")
                results.append(result)
            except Exception as e:
                print(f"\n❌ {name}: {e}")
                results.append((name, False, str(e)))

    credits_end = kc.get_credits()
    ok = sum(1 for r in results if r[1])
    fail = len(results) - ok
    print(f"\n{'='*50}")
    print(f"Réussis: {ok}/{len(results)}")
    print(f"Échoués: {fail}")
    print(f"Crédits utilisés: {credits_start - credits_end:.1f}")
    print(f"Crédits restants: {credits_end}")
    if fail:
        print(f"\nÉchecs (relancer le script pour retry):")
        for name, success, msg in results:
            if not success:
                print(f"  - {name}: {msg}")


if __name__ == "__main__":
    main()
