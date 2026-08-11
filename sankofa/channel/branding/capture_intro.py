#!/usr/bin/env python3
"""Capture l'intro signature Sankofa (HTML animé → frame par frame → MP4).
Même technique que L'Effet Composé (capture_intro_vertical.py).
"""
import os, shutil, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path("/home/tars/african-heroes/CHANNEL/branding")
HTML = BASE / "intro_sankofa.html"
FRAMES = BASE / "intro_frames"
MP4 = BASE / "intro_sankofa.mp4"
STINGER = BASE / "stinger_sankofa.mp3"
FPS = 30

# Clean frames
if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    page.goto(HTML.as_uri())
    page.wait_for_load_state("networkidle")
    duration = page.evaluate("window.DURATION")
    n = int(duration * FPS) + 1
    print(f"Capture {n} frames @ {FPS}fps ({duration}s)…")
    for i in range(n):
        t = i / FPS
        page.evaluate(f"window.render({t:.4f})")
        page.screenshot(path=str(FRAMES / f"f{i:04d}.png"), type="png")
        if i % 30 == 0:
            print(f"  {i}/{n}")
    browser.close()

# Encode silent video
silent_mp4 = FRAMES / "_silent.mp4"
print("Encodage vidéo…")
subprocess.run([
    "ffmpeg", "-y", "-framerate", str(FPS), "-i", str(FRAMES / "f%04d.png"),
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", str(silent_mp4),
], check=True, capture_output=True)

# Mix with stinger audio
print("Mix stinger audio…")
if STINGER.exists():
    r = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(silent_mp4),
        "-i", str(STINGER),
        "-filter_complex", f"[1:a]volume=-3dB,apad=whole_dur={duration}[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-r", "24",
        str(MP4)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"Erreur audio:\n{r.stderr[-800:]}")
        raise RuntimeError("mix failed")
else:
    # No stinger — silent intro
    shutil.copy(silent_mp4, MP4)
    print("  (pas de stinger — intro silencieuse)")

sz = os.path.getsize(MP4) // 1024
print(f"\n✅ {MP4} ({sz} KB)")
print(f"   1080x1920, {duration}s, logo Sankofa animé + texte ambre")

shutil.rmtree(FRAMES, ignore_errors=True)
