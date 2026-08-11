#!/usr/bin/env python3
"""Capture a brand outro signature (HTML animated → frame-by-frame → MP4).
Short version (~2.5s) for placement at the END of short-form videos.

Reuses the same Playwright capture pipeline as the intro, but shorter duration
and different animation: ring draws itself, logo fades in, title/tagline appear.

Usage:
    1. Edit HTML_FILE, LOGO_FILE, STINGER_FILE paths below
    2. Ensure the HTML embeds the logo as base64 <img> (not SVG <image> — see pitfall #9)
    3. Run: python3 capture_brand_outro.py

Output: outro.mp4 (1080x1920, with stinger audio mixed in)
"""
import os, shutil, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

# ═══ CONFIG ═══════════════════════════════════════════════
HTML_FILE = Path("outro.html")        # The animated HTML source
LOGO_FILE = Path("logo.png")          # Logo PNG (will be base64-embedded)
STINGER_FILE = Path("stinger.mp3")    # Brand audio stinger
OUTPUT = Path("outro.mp4")            # Final output

FPS = 30
DURATION = 2.5
WIDTH, HEIGHT = 1080, 1920
# ═════════════════════════════════════════════════════════

FRAMES_DIR = Path("outro_frames")


def embed_logo_base64(html_path, logo_path):
    """Embed logo as base64 JPEG in the HTML ( Chromium SVG <image> workaround)."""
    import base64
    from PIL import Image
    from io import BytesIO

    img = Image.open(logo_path).convert("RGBA")
    img = img.resize((400, 400), Image.LANCZOS)
    bg = Image.new("RGB", (400, 400), (26, 26, 26))
    bg.paste(img, mask=img.split()[3])
    buf = BytesIO()
    bg.save(buf, "JPEG", quality=85)
    b64 = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    html = html_path.read_text()
    html = html.replace("LOGO_PLACEHOLDER", b64)
    html_path.write_text(html)
    return len(b64)


def capture():
    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True)

    total = int(DURATION * FPS) + 1
    print(f"Capturing {total} frames @ {FPS}fps ({DURATION}s)…")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
        page.goto(f"file://{HTML_FILE.absolute()}")
        page.wait_for_load_state("networkidle")

        for i in range(total):
            t = i / FPS
            page.evaluate(f"window.render({t})")
            page.screenshot(path=str(FRAMES_DIR / f"frame_{i:04d}.png"), type="png")
            if i % 30 == 0:
                print(f"  {i}/{total}")

        browser.close()

    # Encode silent video
    silent = OUTPUT.with_suffix(".silent.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", str(FRAMES_DIR / "frame_%04d.png"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "30",
        str(silent)
    ], check=True)

    # Mix with stinger (trimmed to outro duration)
    if STINGER_FILE.exists():
        subprocess.run([
            "ffmpeg", "-y", "-i", str(silent), "-i", str(STINGER_FILE),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", str(OUTPUT)
        ], check=True)
    else:
        shutil.copy(silent, OUTPUT)

    shutil.rmtree(FRAMES_DIR)
    if silent.exists():
        silent.unlink()

    size_kb = os.path.getsize(OUTPUT) // 1024
    print(f"\n✅ {OUTPUT} ({size_kb} KB)")
    print(f"   {WIDTH}x{HEIGHT}, {DURATION}s")


if __name__ == "__main__":
    if "LOGO_PLACEHOLDER" in HTML_FILE.read_text():
        print("Embedding logo as base64…")
        n = embed_logo_base64(HTML_FILE, LOGO_FILE)
        print(f"  Logo embedded ({n} chars)")
    capture()
