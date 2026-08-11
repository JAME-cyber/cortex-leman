#!/usr/bin/env python3
"""TEMPLATE — Assemblage Shorts 9:16 LEC complet (juil. 2026, validé video8 EU Chips).

Pipeline end-to-end en un seul script:
  1. Capture slides HTML → PNG via Playwright
  2. Build Ken Burns segments (zoompan lent sur slide statique)
  3. Concat body (stream copy)
  4. Génère sous-titres SRT (word-chunked, 4 mots/ligne) depuis gen_tts.py SECTIONS
  5. Convert SRT → ASS (PlayResY=1920, font 42, bordure 3)
  6. Burn subs + BGM sur body
  7. Concat final: INTRO + BODY + OUTRO (filter_complex avec normalisation SAR/fps/audio)

Réutilise tts_engine.py (ElevenLabs George + fallback edge-tts).

ADAPTER:
  - VIDEO_DIR, ORDER (noms des sections)
  - durs (depuis audio/durations.json produit par gen_tts.py)
  - SLIDES_HTML, AUDIO, BGM, INTRO, OUTRO paths
  - Palette CSS dans gen_slides.py (navy/gold/green par défaut)

PRÉREQUIS:
  - gen_slides.py a produit les .html dans slides/
  - gen_tts.py a produit les .mp3 + durations.json dans audio/
  - gen_tts.py contient un dict SECTIONS (AST-parsé pour les subs)

FFMPEG NOTES:
  - Ken Burns: scale=2160:3840 + crop + zoompan avec preset=ultrafast = ~10s/segment (OK)
  - Subs burn: preset=medium crf=18 = qualité maximale
  - Concat final: filter_complex (PAS demuxer concat) avec setsar=1, fps=24, aresample=44100
"""
import subprocess, os, json, sys, ast
from pathlib import Path

# === CONFIG — ADAPTER CES PATHS ===
BASE = "/home/tars/crypto-project"
VIDEO_DIR = f"{BASE}/CHANNEL/videoN_xxx"
SLIDES_HTML = f"{VIDEO_DIR}/slides"
SLIDES_PNG = f"{VIDEO_DIR}/renders/slides_png"
AUDIO = f"{VIDEO_DIR}/audio"
BGM = f"{BASE}/audio/bgm_stellardrone.mp3"
INTRO = f"{BASE}/CHANNEL/video3/clips/intro_9x16.mp4"          # 5.0s
OUTRO = f"{BASE}/CHANNEL/branding/outro_signature/outro_signature.mp4"  # ~10.8s
WORK = f"{VIDEO_DIR}/renders/clips"
OUT = f"{VIDEO_DIR}/renders/clip_xxx_final.mp4"

ORDER = ["01_hook", "02_data", "03_paradoxe", "04_riposte", "05_enjeu", "06_lecon"]
FPS = 30
# === FIN CONFIG ===

os.makedirs(SLIDES_PNG, exist_ok=True)
os.makedirs(WORK, exist_ok=True)
durs = json.load(open(f"{AUDIO}/durations.json"))

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ERR [{cmd[0]}]:", r.stderr[-800:])
    return r.returncode

def get_dur(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except (ValueError, AttributeError):
        return -1.0  # corrupt/missing

def fmt_time(s):
    h = int(s // 3600); m = int((s % 3600) // 60)
    sec = int(s % 60); ms = int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

# === 1. Capture slides HTML → PNG ===
print("[1/6] Capture slides HTML → PNG (Playwright)...")
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1920})
    for name in ORDER:
        html_path = f"{SLIDES_HTML}/{name}.html"
        png_path = f"{SLIDES_PNG}/{name}.png"
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(600)
        page.screenshot(path=png_path, full_page=False)
        print(f"  📸 {name}.png")
    browser.close()

# === 2. Build Ken Burns segments ===
print("\n[2/6] Génération segments Ken Burns...")
clips = []
for name in ORDER:
    D = durs[name]["duration"]
    frames = int(D * FPS)
    slide = f"{SLIDES_PNG}/{name}.png"
    au = f"{AUDIO}/{name}.mp3"
    clip = f"{WORK}/{name}.mp4"
    zoom_inc = 0.04 / frames if frames else 0.0002
    filt = (f"scale=2160:3840:force_original_aspect_ratio=increase,"
            f"crop=2160:3840,"
            f"zoompan=z='min(zoom+{zoom_inc:.6f},1.04)':d={frames}:s=1080x1920:fps={FPS},"
            f"format=yuv420p")
    print(f"  [{name}] {D:.1f}s")
    run(["ffmpeg", "-y", "-loop", "1", "-i", slide, "-i", au,
         "-vf", filt, "-t", str(D),
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "128k", "-shortest", clip])
    clips.append(clip)

# === 3. Concat body ===
print("\n[3/6] Concaténation body...")
cl = f"{WORK}/concat.txt"
with open(cl, "w") as f:
    for c in clips:
        f.write(f"file '{c}'\n")
body_voiced = f"{WORK}/body_voiced.mp4"
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", cl, "-c", "copy", body_voiced])

# === 4. Generate SRT subs (word-chunked from gen_tts.py SECTIONS) ===
print("\n[4/6] Génération sous-titres SRT...")
srt_path = f"{WORK}/subs.srt"
sections_text = {}
with open(f"{VIDEO_DIR}/gen_tts.py") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "SECTIONS":
                sections_text = ast.literal_eval(node.value)
                break

with open(srt_path, "w") as f:
    cumulative = 0.0
    idx = 1
    for name in ORDER:
        D = durs[name]["duration"]
        text = sections_text[name]
        words = text.split()
        chunk_size = 4
        chunks = [" ".join(words[j:j+chunk_size]) for j in range(0, len(words), chunk_size)]
        total_chars = sum(len(c) for c in chunks)
        offset = cumulative
        for chunk in chunks:
            chunk_dur = D * (len(chunk) / total_chars)
            f.write(f"{idx}\n{fmt_time(offset)} --> {fmt_time(offset + chunk_dur)}\n{chunk}\n\n")
            offset += chunk_dur
            idx += 1
        cumulative += D

# Convert SRT → ASS with proper 9:16 scaling
ass_path = f"{WORK}/subs.ass"
subprocess.run(["ffmpeg", "-y", "-i", srt_path, ass_path], capture_output=True, text=True, check=True)
with open(ass_path) as f:
    lines = f.readlines()
events = []
in_events = False
for line in lines:
    if line.strip().startswith("[Events]"):
        in_events = True
    if in_events:
        events.append(line)
header = """[Script Info]
Title: Subs
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,42,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,3,0,2,40,40,60,1

"""
with open(ass_path, "w") as f:
    f.write(header)
    for line in events:
        f.write(line)
print(f"  ✅ {idx-1} entrées sous-titres")

# === 5. Burn subs + BGM on body ===
print("\n[5/6] Sous-titres + BGM sur le body...")
body_final = f"{WORK}/body_final.mp4"
body_dur = get_dur(body_voiced)
ass_escaped = ass_path.replace("/", "\\/").replace(":", "\\:")
if os.path.exists(BGM):
    cmd = [
        "ffmpeg", "-y", "-i", body_voiced, "-i", BGM,
        "-vf", f"subtitles='{ass_escaped}'",
        "-filter_complex", f"[1:a]volume=-24dB,afade=t=in:st=0:d=1,afade=t=out:st={body_dur-1.5}:d=1.5[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        body_final
    ]
else:
    cmd = [
        "ffmpeg", "-y", "-i", body_voiced,
        "-vf", f"subtitles='{ass_escaped}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", body_final
    ]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print(f"  FFmpeg err: {r.stderr[-1000:]}")
    sys.exit(1)

# === 6. Concat: INTRO + BODY + OUTRO (filter_complex avec normalisation) ===
print("\n[6/6] Concaténation finale: INTRO + BODY + OUTRO...")
r = subprocess.run([
    "ffmpeg", "-y",
    "-i", INTRO,
    "-i", body_final,
    "-i", OUTRO,
    "-filter_complex",
    "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#04102B,setsar=1,fps=24[v0];"
    "[0:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a0];"
    "[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#04102B,setsar=1,fps=24[v1];"
    "[1:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a1];"
    "[2:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#04102B,setsar=1,fps=24[v2];"
    "[2:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a2];"
    "[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]",
    "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-r", "24",
    OUT
], capture_output=True, text=True)
if r.returncode != 0:
    print(f"  FFmpeg err: {r.stderr[-1500:]}")
    sys.exit(1)

final_dur = get_dur(OUT)
size_mb = os.path.getsize(OUT) / (1024*1024)
print(f"\n✅ CLIP FINAL: {OUT}")
print(f"   Durée: {final_dur:.1f}s ({final_dur/60:.1f} min)")
print(f"   Taille: {size_mb:.1f} MB")
