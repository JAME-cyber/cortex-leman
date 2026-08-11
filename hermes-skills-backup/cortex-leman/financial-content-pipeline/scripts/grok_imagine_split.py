#!/usr/bin/env python3
"""Grok Imagine (via kie.ai) — split-screen vertical assets pour Shorts.

Génère 6 variants par acteur, télécharge les images.
Coût: $0.02 par acteur (4 credits / 6 images).

Usage:
    python grok_imagine_split.py ovhcloud asml soitec

Acteurs disponibles: ovhcloud, asml, soitec (étendre PROMPTS si besoin).
"""
import os, sys, time, json, requests
from pathlib import Path

# Load API key
for env_file in ["/home/tars/.hermes/.env", os.path.expanduser("~/.hermes/.env")]:
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("KIE") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()
KEY = os.environ.get("KIE_AI_API_KEY") or os.environ.get("KIE_API_KEY")
if not KEY:
    sys.exit("KIE_AI_API_KEY manquant dans ~/.hermes/.env")

BASE = "https://api.kie.ai"
S = requests.Session()
S.headers.update({"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})

# Prompts split-screen photoréaliste + data viz, vertical 9:16, palette L'EFFET COMPOSÉ
PROMPTS = {
    "ovhcloud": """Split screen composition, vertical 9:16.
LEFT PANEL (top half): A modern data center aisle with rows of server racks glowing with blue LED lights, cinematic lighting, depth of field, photorealistic, OVHcloud-style infrastructure.
RIGHT PANEL (bottom half): Abstract financial growth chart with green upward arrows, golden circuit board patterns overlaid, dark navy background #04102B.
Subtle divider line in gold #D2B257 between panels. Professional, corporate, cinematic, high detail.""",
    "asml": """Split screen composition, vertical 9:16.
LEFT PANEL (top half): A highly complex EUV lithography machine, precision engineering, blue and silver metallic components, clean room environment, photorealistic, cinematic lighting.
RIGHT PANEL (bottom half): Abstract semiconductor wafer with golden circuit traces, green yield improvement chart trending upward, dark navy background #04102B.
Subtle divider line in gold #D2B257 between panels. Professional, corporate, cinematic, high detail.""",
    "soitec": """Split screen composition, vertical 9:16.
LEFT PANEL (top half): Silicon-on-insulator (SOI) semiconductor wafer glowing with rainbow iridescence, held by precision robotic arm, clean room, photorealistic, cinematic.
RIGHT PANEL (bottom half): Abstract stacked layered substrate visualization with golden bonds, green performance metrics chart, dark navy background #04102B.
Subtle divider line in gold #D2B257 between panels. Professional, corporate, cinematic, high detail.""",
}


def generate(actor: str, out_dir: str = None, quality: str = "standard") -> list:
    """Génère 6 variants split-screen pour un acteur. Retourne liste de paths locaux."""
    if actor not in PROMPTS:
        raise ValueError(f"Acteur inconnu: {actor}. Disponibles: {list(PROMPTS.keys())}")
    out_dir = Path(out_dir or "/home/tars/crypto-project/CHANNEL/video3/grok_assets")
    out_dir.mkdir(parents=True, exist_ok=True)

    body = {
        "model": "grok-imagine/text-to-image",
        "input": {"prompt": PROMPTS[actor], "aspect_ratio": "9:16", "quality": quality},
    }
    print(f"[{actor}] Création tâche...")
    r = S.post(f"{BASE}/api/v1/jobs/createTask", json=body, timeout=30)
    r.raise_for_status()
    task_id = r.json()["data"]["taskId"]
    print(f"[{actor}] Task: {task_id}")

    for attempt in range(40):
        time.sleep(5)
        r = S.get(f"{BASE}/api/v1/jobs/recordInfo?taskId={task_id}", timeout=15)
        d = r.json().get("data", {})
        state = d.get("state")
        if state == "success":
            result = json.loads(d["resultJson"])
            urls = result["resultUrls"]
            break
        elif state in ("failed", "error"):
            raise RuntimeError(f"Tâche échouée: {d}")
    else:
        raise TimeoutError(f"[{actor}] timeout")

    paths = []
    for i, url in enumerate(urls):
        data = requests.get(url, timeout=60).content
        p = out_dir / f"{actor}_split_v{i+1}.jpg"
        p.write_bytes(data)
        paths.append(str(p))
        print(f"  → {p}")
    print(f"[{actor}] ✅ {len(paths)} variants téléchargés")
    return paths


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: grok_imagine_split.py <actor1> [actor2] [actor3]")
    for actor in sys.argv[1:]:
        generate(actor)
