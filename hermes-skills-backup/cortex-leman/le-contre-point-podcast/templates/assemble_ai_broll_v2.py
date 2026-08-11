#!/usr/bin/env python3
"""
Template: B-roll AI Background Loop + Slide Overlay (CNBC style)
Pattern validé sur video2 CoreWeave (juil. 2026).

Le clip AI joue en boucle pendant TOUTE la section.
La slide PNG est overlay à 88% opacity (motion visible derrière).

USAGE:
  1. Définir BROLL_AI_MAP (section → clip AI id)
  2. Avoir généré les clips via broll_ai.py (voir templates/broll_ai.py)
  3. Avoir les slides PNG (renders/slides_png/) et audio MP3 par section
  4. python3 assemble_ai_broll_v2.py

OUTPUT: video2_broll_ai_loop.mp4 (puis compresser en HEVC pour Telegram)
"""
import subprocess, os, json
from pathlib import Path

# ─── CONFIG ──────────────────────────────────────────────────────────────────
BASE = Path("/home/tars/crypto-project")
BROLL_AI_DIR = BASE / "video_clips/broll_ai"       # où broll_ai.py télécharge les clips
WORK = BASE / "CHANNEL/video2/renders/broll_ai_v2" # dir de travail (peut varier)
OUT = WORK / "video2_broll_ai_loop.mp4"

W, H, FPS = 1280, 720, 30

# Mapping: section → AI clip (sans extension)
# Les sections pointent vers les clips générés par broll_ai.py
BROLL_AI_MAP = {
    "01_hook":               "br01_datacenter_pan",
    "02_cequelle_vend":      "br02_gpu_racks_closeup",
    "03_dou_vient_argent":   "br05_trading_charts",
    # ... adapter selon épisode
}

SLIDES = BASE / "CHANNEL/video2/renders/slides_png"  # PNG 1280x720 par section
AUDIO  = BASE / "CHANNEL/video2/audio"
BGM    = BASE / "audio/bgm_stellardrone.mp3"

# Charger durées depuis le TTS
DURS = json.loads((AUDIO / "durations.json").read_text())
ORDER = list(DURS.keys())

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR: {r.stderr[-300:]}")
    return r.returncode == 0

# ─── BUILD ───────────────────────────────────────────────────────────────────
print("🎬 Build B-roll AI loop + slide overlay\n")
WORK.mkdir(parents=True, exist_ok=True)
clips = []

for name in ORDER:
    D = DURS[name]["duration"]
    au = str(AUDIO / f"{name}.mp3")

    ai_id = BROLL_AI_MAP.get(name)
    ai_path = BROLL_AI_DIR / f"{ai_id}.mp4"
    if not ai_path.exists():
        print(f"  ⚠️ {name}: AI clip manquant ({ai_id}), skip")
        continue

    # 1) Loop AI clip sur toute la durée de section
    bg = WORK / f"{name}_bg.mp4"
    loop_count = int(D / 6.0) + 2  # clips font 6s par défaut
    run(["ffmpeg", "-y", "-stream_loop", str(loop_count), "-i", str(ai_path),
         "-t", f"{D:.2f}",
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},format=yuv420p",
         "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", str(FPS), str(bg)])

    # 2) Overlay slide PNG à 88% opacity
    composed = WORK / f"{name}_composed.mp4"
    run(["ffmpeg", "-y", "-i", str(bg), "-i", str(SLIDES / f"{name}.png"),
         "-filter_complex",
         f"[1:v]format=rgba,colorchannelmixer=aa=0.88[sl];"
         f"[0:v][sl]overlay=0:0,eq=brightness=-0.03:contrast=1.03[v]",
         "-map", "[v]",
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-t", f"{D:.2f}",
         str(composed)])

    # 3) Mux audio
    clip = WORK / f"clip_{name}.mp4"
    run(["ffmpeg", "-y", "-i", str(composed), "-i", au,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", str(clip)])
    clips.append(str(clip))
    print(f"  ✅ {name}: AI loop ({D:.1f}s) + slide overlay")

# 4) Concat all sections
concat_file = WORK / "concat.txt"
concat_file.write_text("".join(f"file '{c}'\n" for c in clips))
voiced = WORK / "voiced.mp4"
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
     "-c", "copy", str(voiced)])

# 5) BGM mix
tot = sum(DURS[k]["duration"] for k in ORDER)
fo = max(0, tot - 4)
run(["ffmpeg", "-y", "-i", str(voiced), "-i", str(BGM), "-filter_complex",
     f"[1:a]atrim=0:{tot:.2f},asetpts=PTS-STARTPTS,"
     f"afade=t=in:st=0:d=3,afade=t=out:st={fo:.2f}:d=4,volume=0.10[bgm];"
     f"[0:a]volume=1.0[v];[bgm][v]amix=inputs=2:duration=first:"
     f"dropout_transition=0,alimiter=limit=0.95[a]",
     "-map", "0:v", "-map", "[a]",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", str(OUT)])

sz = os.path.getsize(OUT) // 1024 // 1024
print(f"\n✅ {OUT} ({sz} MB)")
print(f"   B-roll AI en loop + slide overlay 88%")
print(f"   Compresser en HEVC pour Telegram (cf skill pitfall #15)")
