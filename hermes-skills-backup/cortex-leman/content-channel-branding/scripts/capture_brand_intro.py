#!/usr/bin/env python3
"""Capture an animated brand intro HTML → frame-by-frame → MP4.
Reuses the pattern from L'Effet Composé (capture_intro_vertical.py).

Usage:
  python capture_brand_intro.py <path_to_intro.html> <output.mp4> [stinger.mp3]

The HTML must expose:
  - window.DURATION (float, seconds)
  - window.render(t) (function, takes time in seconds)

Output: 1080x1920 H.264 MP4 with optional stinger audio (apad to match video duration).
"""
import os, sys, shutil, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <intro.html> <output.mp4> [stinger.mp3]")
    sys.exit(1)

HTML = Path(sys.argv[1]).resolve()
MP4 = Path(sys.argv[2]).resolve()
STINGER = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else None
FPS = 30
FRAMES = HTML.parent / f"_intro_frames_{HTML.stem}"

if not HTML.exists():
    print(f"❌ HTML not found: {HTML}")
    sys.exit(1)

if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)

# Capture frames
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
print("Encoding video…")
subprocess.run([
    "ffmpeg", "-y", "-framerate", str(FPS), "-i", str(FRAMES / "f%04d.png"),
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", str(silent_mp4),
], check=True, capture_output=True)

# Mix audio
print("Mixing audio…")
if STINGER and STINGER.exists():
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
        print(f"Audio error:\n{r.stderr[-800:]}")
        # Fallback: silent
        shutil.copy(silent_mp4, MP4)
        print("  (fallback: silent intro)")
else:
    shutil.copy(silent_mp4, MP4)
    print("  (no stinger — silent intro)")

sz = os.path.getsize(MP4) // 1024
print(f"\n✅ {MP4} ({sz} KB)")
print(f"   1080x1920, {duration}s")

shutil.rmtree(FRAMES, ignore_errors=True)
