#!/usr/bin/env python3
"""
B-roll AI v3 — Full build pipeline (PATTERN VALIDÉ USER juil. 2026).
Slides à fond transparent (bg #04102B → alpha 0 via PIL/numpy).
Clip AI joue en boucle derrière le texte sur toute la durée de la section.

USAGE:
  1. Adapter BROLL_MAP (section → clip AI id) et ORDER.
  2. Lancer en background: python3 assemble_ai_broll_v3_full.py
  3. Compresser le output en HEVC pour Telegram si >50 MB.

CONTRAINTES:
  - Lancer en background=true (9 sections > 300s foreground).
  - Preset ultrafast obligatoire.
  - Les slides source doivent avoir un fond #04102B opaque (HTML LEC standard).
"""
import subprocess, os, json
from pathlib import Path
from PIL import Image
import numpy as np

BASE = Path("/home/tars/crypto-project")
BROLL = BASE / "video_clips/broll_ai"
SLIDES_PNG = BASE / "CHANNEL/video2/renders/slides_png"
WORK = BASE / "CHANNEL/video2/renders/broll_ai_v3"
WORK.mkdir(parents=True, exist_ok=True)
OUT = WORK / "video2_broll_ai_v3.mp4"

W, H, FPS = 1280, 720, 30
AUDIO = BASE / "CHANNEL/video2/audio"
DURS = json.loads((AUDIO / "durations.json").read_text())
ORDER = ["01_hook","02_cequelle_vend","03_dou_vient_argent","04_capacite",
         "05_prix_realise","06_cout_complet","07_contrats","08_dette_capex","09_verdict"]
BGM = BASE / "audio/bgm_stellardrone.mp3"

# Section → AI clip id (doit exister dans BROLL/<id>.mp4)
BROLL_MAP = {
    "01_hook":"br01_datacenter_pan", "02_cequelle_vend":"br02_gpu_racks_closeup",
    "03_dou_vient_argent":"br05_trading_charts", "04_capacite":"br04_construction_timelapse",
    "05_prix_realise":"br05_trading_charts", "06_cout_complet":"br02_gpu_racks_closeup",
    "07_contrats":"br03_fiber_optic_light", "08_dette_capex":"br01_datacenter_pan",
    "09_verdict":"br04_construction_timelapse",
}

# Background color to make transparent (LEC standard dark navy)
BG_R, BG_G, BG_B = 4, 16, 43  # #04102B

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR: {r.stderr[-300:]}")
    return r.returncode == 0

def make_transparent(src_png, out_png):
    """Remove background color #04102B from slide PNG → transparent.
    Returns % of transparent pixels."""
    img = Image.open(src_png).convert("RGBA")
    arr = np.array(img)
    tol = 15
    mask = ((np.abs(arr[:,:,0].astype(int) - BG_R) < tol) &
            (np.abs(arr[:,:,1].astype(int) - BG_G) < tol) &
            (np.abs(arr[:,:,2].astype(int) - BG_B) < tol))
    arr[mask, 3] = 0
    # Soft edges for partial matches
    edge = ((np.abs(arr[:,:,0].astype(int) - BG_R) < tol+12) &
            (np.abs(arr[:,:,1].astype(int) - BG_G) < tol+12) &
            (np.abs(arr[:,:,2].astype(int) - BG_B) < tol+12) & ~mask)
    arr[edge, 3] = arr[edge, 3] // 3
    Image.fromarray(arr).save(out_png)
    return mask.sum() / mask.size * 100

# ─── Step 1: Transparent slides ──────────────────────────────────────────────
print("🎨 Slides transparentes...")
for name in ORDER:
    pct = make_transparent(SLIDES_PNG / f"{name}.png", WORK / f"{name}_t.png")
    print(f"  {name}: {pct:.1f}% transparent")

# ─── Step 2: Build sections ──────────────────────────────────────────────────
print("\n🎬 Build sections...\n")
clips = []
for name in ORDER:
    D = DURS[name]["duration"]
    ai = BROLL / f"{BROLL_MAP[name]}.mp4"
    tslide = WORK / f"{name}_t.png"
    au = AUDIO / f"{name}.mp3"
    loops = int(D / 6.0) + 2  # clip source = 6s

    comp = WORK / f"{name}_comp.mp4"
    run(["ffmpeg","-y",
         "-stream_loop",str(loops),"-i",str(ai),
         "-i",str(tslide),
         "-filter_complex",
         f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
         f"eq=brightness=-0.05:saturation=0.9:contrast=1.05[bg];"
         f"[bg][1:v]overlay=0:0[v]",
         "-map","[v]","-t",f"{D:.2f}",
         "-c:v","libx264","-preset","ultrafast","-crf","18",
         "-pix_fmt","yuv420p","-r",str(FPS),str(comp)])

    clip = WORK / f"clip_{name}.mp4"
    run(["ffmpeg","-y","-i",str(comp),"-i",str(au),
         "-c:v","copy","-c:a","aac","-b:a","128k","-shortest",str(clip)])
    clips.append(str(clip))
    print(f"  ✅ {name} ({D:.1f}s)")

# ─── Step 3: Concat + BGM ────────────────────────────────────────────────────
print("\n📋 Concaténation + BGM...")
cl = WORK / "concat.txt"
cl.write_text("".join(f"file '{c}'\n" for c in clips))
voiced = WORK / "voiced.mp4"
run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(cl),"-c","copy",str(voiced)])

tot = sum(DURS[k]["duration"] for k in ORDER)
fo = max(0, tot - 4)
run(["ffmpeg","-y","-i",str(voiced),"-i",str(BGM),"-filter_complex",
     f"[1:a]atrim=0:{tot:.2f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=3,"
     f"afade=t=out:st={fo:.2f}:d=4,volume=0.10[bgm];"
     f"[0:a]volume=1.0[v];[bgm][v]amix=inputs=2:duration=first:dropout_transition=0,"
     f"alimiter=limit=0.95[a]",
     "-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","128k",
     "-shortest",str(OUT)])

sz = os.path.getsize(OUT) // 1024 // 1024
dur = float(subprocess.run(
    ["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(OUT)],
    capture_output=True, text=True).stdout.strip())
print(f"\n✅ {OUT}")
print(f"   {dur:.1f}s | {sz} MB")
