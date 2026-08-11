#!/usr/bin/env python3
"""Capture l'outro signature Sankofa (HTML animé → frame par frame → MP4).
Version courte 2.5s pour placement fin de vidéo.
"""
import os, shutil, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path("/home/tars/african-heroes/CHANNEL/branding")
HTML = BASE / "outro_sankofa.html"
FRAMES = BASE / "outro_frames"
MP4 = BASE / "outro_sankofa.mp4"
STINGER = BASE / "stinger_sankofa.mp3"
FPS = 30
DURATION = 2.5

# Clean frames
if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)

print(f"Capture {int(DURATION * FPS) + 1} frames @ {FPS}fps ({DURATION}s)…")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1920})
    page.goto(f"file://{HTML}")
    page.wait_for_load_state("networkidle")

    total = int(DURATION * FPS) + 1
    for i in range(total):
        t = i / FPS
        page.evaluate(f"window.render({t})")
        page.screenshot(path=str(FRAMES / f"frame_{i:04d}.png"), type="png")
        if i % 30 == 0:
            print(f"  {i}/{total}")

    browser.close()

# Encode video (silent)
print("Encodage vidéo…")
silent_mp4 = BASE / "outro_silent.mp4"
subprocess.run([
    "ffmpeg", "-y", "-framerate", str(FPS),
    "-i", str(FRAMES / "frame_%04d.png"),
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-pix_fmt", "yuv420p", "-r", "30",
    str(silent_mp4)
], check=True)

# Mix with stinger (trimmed to outro duration)
print("Mix stinger audio…")
if STINGER.exists():
    subprocess.run([
        "ffmpeg", "-y", "-i", str(silent_mp4), "-i", str(STINGER),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", str(MP4)
    ], check=True)
else:
    shutil.copy(silent_mp4, MP4)

# Cleanup frames
shutil.rmtree(FRAMES)

size_kb = os.path.getsize(MP4) // 1024
print(f"\n✅ {MP4} ({size_kb} KB)")
print(f"   1080x1920, {DURATION}s, outro signature Sankofa")
