#!/usr/bin/env python3
"""Template générateur de thumbnails YouTube 1280×720 (LE CONTRE-POINT et long-form).
Pipeline : HTML/CSS slides → Playwright capture → PNG.
Sélection photo bg via PIL ImageStat (workaround modèle sans vision).

USAGE :
  1. Éditer PARAMS ci-dessous (TICKER, TITLE, EPISODE_NUM, SUBTITLE, BG_PATH).
  2. Lancer : python gen_thumbnail_template.py
  3. Le script génère 3 variants (V1 minimaliste, V2 3-risques reco, V3 curiosité).
  4. Livrer les 3 PNG au user via MEDIA: → il choisit.
"""
import asyncio, sys
from pathlib import Path
from PIL import Image, ImageStat
from playwright.async_api import async_playwright

# ============================================================
# PARAMS À ÉDITER
# ============================================================
TICKER = "OVH.PA"                # ex: "ASML.AS", "TRUMPF.DE"...
TITLE = "OVHCLOUD"               # gros titre, ~10 caractères max
EPISODE_NUM = "01"               # numéro d'épisode affiché top-right
SUBTITLE_DEFAULT = "Le bear case"  # V1
SUBTITLE_V2 = "Ce qu'on ne vous dit pas"  # V2 (3 risques)
SUBTITLE_V3 = "Ce qui peut mal tourner"   # V3 (flèche rouge)
# Dossier des 6 variants photo Grok pour scoring PIL (tous les *_split_v*.jpg)
BG_DIR = "/home/tars/crypto-project/CHANNEL/video3/grok_assets"
BG_PREFIX = "ovhcloud_split"     # préfixe des fichiers à scorer
LOGO = "/home/tars/crypto-project/branding/final/logo_static.png"
OUT_DIR = Path("/tmp/thumbnails_out")  # éditer selon le besoin
# ============================================================

OUT_DIR.mkdir(parents=True, exist_ok=True)
SLIDES_DIR = OUT_DIR / "slides"
SLIDES_DIR.mkdir(exist_ok=True)

# === Scoring photo bg par PIL (workaround modèle sans vision) ===
def score_thumbnail_candidate(path):
    img = Image.open(path).convert("RGB")
    s = ImageStat.Stat(img)
    r, g, b = s.mean
    lum = 0.299*r + 0.587*g + 0.114*b
    contrast = sum(s.stddev) / 3
    lum_pen = abs(lum - 70) * 0.5
    return contrast - lum_pen

def pick_best_bg():
    cands = []
    for i in range(1, 7):
        p = Path(BG_DIR) / f"{BG_PREFIX}_v{i}.jpg"
        if p.exists():
            cands.append((p, score_thumbnail_candidate(p)))
    if not cands:
        print(f"⚠️ Aucun candidat trouvé pour {BG_PREFIX}_v*.jpg dans {BG_DIR}")
        sys.exit(1)
    cands.sort(key=lambda x: x[1], reverse=True)
    print("Top 3 candidats bg (score PIL):")
    for p, sc in cands[:3]:
        print(f"  {p.name}: score={sc:.0f}")
    return str(cands[0][0])

# === CSS template commun ===
BASE_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  width: 1280px; height: 720px; overflow: hidden;
  font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
  background: #0a1628; position: relative;
}
.bg {
  position: absolute; inset: 0;
  background-image: url('BG_PLACEHOLDER');
  background-size: cover; background-position: center;
  filter: brightness(0.45) saturate(1.2);
}
.overlay {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(10,22,40,0.85) 0%, rgba(10,22,40,0.4) 50%, rgba(212,160,23,0.15) 100%);
}
.topbar {
  position: absolute; top: 0; left: 0; right: 0;
  background: linear-gradient(180deg, rgba(10,22,40,0.95), rgba(10,22,40,0));
  padding: 32px 56px 60px;
  display: flex; align-items: center; justify-content: space-between;
}
.brand { color: #d4a017; font-size: 22px; font-weight: 800; letter-spacing: 6px; text-transform: uppercase; }
.episode { color: rgba(255,255,255,0.6); font-size: 16px; letter-spacing: 4px; text-transform: uppercase; }
.content { position: absolute; bottom: 0; left: 0; right: 0; padding: 0 56px 56px; }
.ticker {
  color: #d4a017; font-size: 20px; font-weight: 700; letter-spacing: 3px;
  margin-bottom: 12px; display: inline-block;
  padding: 4px 12px; border: 2px solid #d4a017;
}
.title {
  color: #ffffff; font-size: 108px; font-weight: 900;
  line-height: 0.95; letter-spacing: -2px;
  text-shadow: 0 4px 24px rgba(0,0,0,0.8);
}
.subtitle { color: #ffffff; font-size: 42px; font-weight: 600; margin-top: 18px; letter-spacing: 1px; }
.logo { position: absolute; bottom: 32px; right: 56px; width: 80px; height: auto; opacity: 0.85; }
"""

def build_html(bg_path, subtitle, variant):
    extra_css = ""
    extra_body = ""
    if variant == "v2":
        extra_css = """
.risk-box {
  position: absolute; top: 180px; right: 56px;
  background: rgba(212, 160, 23, 0.95); color: #0a1628;
  padding: 24px 32px; border-radius: 8px; text-align: center;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
.risk-number { font-size: 96px; font-weight: 900; line-height: 1; }
.risk-label { font-size: 20px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }
"""
        extra_body = """
  <div class="risk-box">
    <div class="risk-number">3</div>
    <div class="risk-label">Risques</div>
  </div>
"""
    elif variant == "v3":
        extra_css = """
.arrow {
  position: absolute; top: 160px; right: 80px;
  width: 220px; height: 220px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(220, 38, 38, 0.95); border-radius: 50%;
  box-shadow: 0 12px 40px rgba(220,38,38,0.5);
  font-size: 140px; color: white; font-weight: 900;
  transform: rotate(-10deg);
}
"""
        extra_body = '<div class="arrow">↓</div>'
    css = BASE_CSS.replace("BG_PLACEHOLDER", bg_path) + extra_css
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{css}</style></head>
<body>
  <div class="bg"></div>
  <div class="overlay"></div>
  <div class="topbar">
    <div class="brand">LE CONTRE-POINT</div>
    <div class="episode">Épisode {EPISODE_NUM}</div>
  </div>
  {extra_body}
  <div class="content">
    <div class="ticker">{TICKER}</div>
    <div class="title">{TITLE}</div>
    <div class="subtitle">{subtitle}</div>
  </div>
  <img class="logo" src="{LOGO}">
</body></html>
"""

async def capture(html_str, name):
    html_path = SLIDES_DIR / f"{name}.html"
    png_path = OUT_DIR / f"{name}.png"
    html_path.write_text(html_str, encoding="utf-8")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        page = await ctx.new_page()
        await page.goto(f"file://{html_path}")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(0.5)
        await page.screenshot(path=str(png_path), clip={"x":0,"y":0,"width":1280,"height":720})
        await browser.close()
    print(f"  📸 {name}: {png_path}")

async def main():
    print("=== Thumbnail generator (LE CONTRE-POINT) ===")
    bg = pick_best_bg()
    print(f"BG retenu: {bg}\n")
    print("Génération 3 variants...")
    await capture(build_html(bg, SUBTITLE_DEFAULT, "v1"), "v1_minimaliste")
    await capture(build_html(bg, SUBTITLE_V2, "v2"), "v2_risques")
    await capture(build_html(bg, SUBTITLE_V3, "v3"), "v3_curiosite")
    print(f"\n✅ 3 thumbnails dans {OUT_DIR}")
    print("Livrer les 3 au user via MEDIA: → il choisit.")

if __name__ == "__main__":
    asyncio.run(main())
