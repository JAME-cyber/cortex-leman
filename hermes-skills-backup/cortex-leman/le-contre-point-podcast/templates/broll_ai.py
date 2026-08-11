#!/usr/bin/env python3
"""
B-roll AI Generator — Veo 3.1 Fast via kie.ai
Pipeline parallèle pour générer des clips photoréalistes (datacenter, GPU, finance).

USAGE:
  1. Définir BROLL_CLIPS (id + prompt) ci-dessous.
  2. python broll_ai.py              # submit generation tasks
  3. python broll_ai.py --status     # poll + auto-download completed clips

COÛT: 65 crédits/clip (Fast 1080p 16:9). Un short à 5 clips = 325 crédits (~$1.63).

⚠️ `successFlag` est au niveau `data`, PAS `data.response` — bug #1 cause de boucle infinie.
"""
import os, sys, json, time, requests, subprocess
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
API_KEY = os.environ.get("KIE_API_KEY", "")
if not API_KEY:
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"  # crypto-project/.env
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("KIE_API_KEY"):
                API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
if not API_KEY:
    print("ERROR: KIE_API_KEY not found in env or .env"); sys.exit(1)

BASE_URL = "https://api.kie.ai"
GEN_ENDPOINT = f"{BASE_URL}/api/v1/veo/generate"
STATUS_ENDPOINT = f"{BASE_URL}/api/v1/veo/record-info"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "video_clips" / "broll_ai"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = OUTPUT_DIR / "tasks.json"

# ─── B-roll Prompts — PERSONNALISER PAR SHORT ─────────────────────────────────
# Format 16:9 ou 9:16, photoréaliste, cinématique. Optimisé pour Veo 3.1.
# RÈGLE: pas de texte lisible, pas de personnes identifiables.
BROLL_CLIPS = [
    {
        "id": "br01_datacenter_pan",
        "prompt": (
            "Cinematic slow camera pan through a massive modern data center. "
            "Endless rows of server racks with blue and green LED lights blinking. "
            "Cold fog rolling across the floor. Cool blue lighting, photorealistic, "
            "4K cinematic, shallow depth of field. No people, no text. "
            "Clean industrial infrastructure aesthetic."
        ),
    },
    {
        "id": "br02_gpu_closeup",
        "prompt": (
            "Extreme close-up of glowing GPU accelerator cards in a server rack, "
            "fans spinning slowly. Macro shot showing circuit boards with green PCBs "
            "and gold contacts. Warm orange heat glow contrasting with blue ambient light. "
            "Photorealistic, cinematic, shallow depth of field. No text."
        ),
    },
    # ... ajouter d'autres clips selon le short
]

# ─── API Functions ────────────────────────────────────────────────────────────

def generate_video(clip_config, model="veo3_fast", aspect_ratio="16:9",
                   resolution="1080p", duration=6):
    """Submit a Veo 3.1 generation task. Returns taskId."""
    payload = {
        "prompt": clip_config["prompt"],
        "model": model,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "duration": duration,
        "generationType": "TEXT_2_VIDEO",
        "enableTranslation": True,
    }
    try:
        r = requests.post(GEN_ENDPOINT, headers=HEADERS, json=payload, timeout=30)
        data = r.json()
        if data.get("code") == 200:
            task_id = data["data"]["taskId"]
            print(f"  ✅ {clip_config['id']}: taskId={task_id}")
            return task_id
        else:
            print(f"  ❌ {clip_config['id']}: code={data.get('code')} msg={data.get('msg')}")
            return None
    except Exception as e:
        print(f"  ❌ {clip_config['id']}: {e}")
        return None


def check_task(task_id):
    """Poll task status. Returns (status, result_urls).
    
    ⚠️ CRITICAL: successFlag is at data level, NOT data.response level.
    """
    try:
        r = requests.get(STATUS_ENDPOINT, headers=HEADERS,
                         params={"taskId": task_id}, timeout=15)
        data = r.json()
        if data.get("code") != 200:
            return "error", []
        d = data.get("data", {})
        resp = d.get("response", {})
        # ✅ CORRECT: successFlag at data level (with fallback for API changes)
        flag = d.get("successFlag", resp.get("successFlag"))
        if flag == 1:
            urls = resp.get("resultUrls", [])
            return "success", urls
        elif flag in (2, 3):
            return "failed", []
        return "generating", []
    except Exception:
        return "error", []


def download_clip(url, output_path):
    """Download MP4 with wget."""
    r = subprocess.run(["wget", "-q", "-O", str(output_path), url],
                       capture_output=True, timeout=120)
    return r.returncode == 0


# ─── Main Workflow ────────────────────────────────────────────────────────────

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def cmd_generate():
    print("🚀 Génération B-roll AI — Veo 3.1 Fast")
    state = load_state()
    new_clips = [c for c in BROLL_CLIPS if c["id"] not in state or not state[c["id"]].get("taskId")]
    if not new_clips:
        print("  Toutes les tâches déjà soumises. Utilise --status.")
        return
    for clip in new_clips:
        task_id = generate_video(clip)
        if task_id:
            state[clip["id"]] = {"taskId": task_id, "submitted": time.time(), "status": "submitted"}
            save_state(state)
        time.sleep(1)  # rate limit: 20 req/10s max

def cmd_status():
    state = load_state()
    to_download = []
    for clip_id, info in state.items():
        if info.get("status") == "downloaded": continue
        status, urls = check_task(info["taskId"])
        if status == "success" and urls:
            print(f"  ✅ {clip_id}: SUCCESS")
            info["urls"] = urls
            to_download.append((clip_id, urls))
        elif status == "failed":
            print(f"  ❌ {clip_id}: FAILED")
        elif status == "generating":
            elapsed = int(time.time() - info.get("submitted", time.time()))
            print(f"  ⏳ {clip_id}: generating ({elapsed}s)")
    save_state(state)
    for clip_id, urls in to_download:
        for url in urls:
            out = OUTPUT_DIR / f"{clip_id}.mp4"
            if download_clip(url, out):
                info[clip_id]["status"] = "downloaded"
                print(f"  ⬇️  {out.name}: {out.stat().st_size//1024}KB")
    save_state(state)

if __name__ == "__main__":
    if "--status" in sys.argv:
        cmd_status()
    else:
        cmd_generate()
