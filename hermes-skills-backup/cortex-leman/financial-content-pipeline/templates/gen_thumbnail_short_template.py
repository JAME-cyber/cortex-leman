#!/usr/bin/env python3
"""Template Shorts 9:16 (1080×1920) pour L'EFFET COMPOSÉ.
Validé 2026-07-19 (batch de 7 thumbnails produits).

Usage single:
  python3 gen_thumbnail_short_template.py <clip_id> <ticker> <company> <tagline> <bg_path> <label>

Usage batch (éditer SHORTS ci-dessous):
  python3 gen_thumbnail_short_template.py
"""
import sys, asyncio
from pathlib import Path
from playwright.async_api import async_playwright

LOGO = "/home/tars/crypto-project/branding/final/logo_static.png"
OUT_DIR = Path("/home/tars/crypto-project/CHANNEL/thumbnails/shorts")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# === CONFIG VALIDÉE (B1 — base claire, gradient directionnel) ===
BRIGHTNESS = 0.95
OVERLAY_TOP = 0.30
OVERLAY_BOTTOM = 0.75

CSS = f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  width: 1080px; height: 1920px; overflow: hidden;
  font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
  background: #0a1628; position: relative;
}}
.bg {{
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  filter: brightness({BRIGHTNESS}) saturate(1.15);
}}
.overlay {{
  position: absolute; inset: 0;
  background: linear-gradient(180deg,
    rgba(10,22,40,{OVERLAY_TOP}) 0%,
    rgba(10,22,40,0.15) 35%,
    rgba(10,22,40,0.50) 65%,
    rgba(10,22,40,{OVERLAY_BOTTOM}) 100%);
}}
.topbar {{
  position: absolute; top: 0; left: 0; right: 0;
  background: linear-gradient(180deg, rgba(10,22,40,0.95), rgba(10,22,40,0));
  padding: 64px 56px 100px;
  display: flex; align-items: center; justify-content: space-between;
}}
.brand {{
  color: #d4a017; font-size: 32px; font-weight: 900;
  letter-spacing: 6px; text-transform: uppercase;
  text-shadow: 0 2px 8px rgba(0,0,0,0.9);
}}
.episode {{
  background: rgba(212,160,23,0.95); color: #0a1628;
  padding: 6px 18px; border-radius: 6px; font-weight: 800;
  font-size: 24px; letter-spacing: 4px; text-transform: uppercase;
}}
.content {{
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 0 56px 140px;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.6));
}}
.ticker {{
  color: #d4a017; font-size: 28px; font-weight: 700; letter-spacing: 4px;
  margin-bottom: 24px; display: inline-block;
  padding: 6px 18px; border: 3px solid #d4a017;
  background: rgba(10,22,40,0.75);
}}
.title {{
  color: #ffffff; font-size: 140px; font-weight: 900;
  line-height: 0.95; letter-spacing: -3px;
  text-shadow: 0 4px 24px rgba(0,0,0,0.95), 0 2px 4px rgba(0,0,0,0.8);
}}
.subtitle {{
  color: #d4a017; font-size: 56px; font-weight: 700;
  margin-top: 32px; letter-spacing: 1px; line-height: 1.1;
  text-shadow: 0 2px 12px rgba(0,0,0,0.95);
}}
.logo {{
  position: absolute; bottom: 48px; right: 56px;
  width: 100px; height: auto; opacity: 0.9;
  filter: drop-shadow(0 2px 8px rgba(0,0,0,0.8));
}}
"""

def html_for(bg_path, ticker, company, tagline, episode_label):
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
  <div class="bg" style="background-image: url('{bg_path}');"></div>
  <div class="overlay"></div>
  <div class="topbar">
    <div class="brand">L'EFFET COMPOSÉ</div>
    <div class="episode">{episode_label}</div>
  </div>
  <div class="content">
    <div class="ticker">{ticker}</div>
    <div class="title">{company.upper()}</div>
    <div class="subtitle">{tagline}</div>
  </div>
  <img class="logo" src="{LOGO}">
</body></html>
"""


async def capture(html_str, out_path):
    tmp = out_path.with_suffix('.html')
    tmp.write_text(html_str, encoding="utf-8")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        page = await ctx.new_page()
        await page.goto(f"file://{tmp}")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(0.5)
        await page.screenshot(path=str(out_path), clip={"x":0,"y":0,"width":1080,"height":1920})
        await browser.close()


async def main():
    if len(sys.argv) == 7:
        clip_id, ticker, company, tagline, bg, label = sys.argv[1:7]
        out = OUT_DIR / f"thumb_short_{clip_id}_{company.lower().replace(' ', '_')}.png"
        await capture(html_for(bg, ticker, company, tagline, label), out)
        print(f"✅ {out}")
        return

    # Batch mode — éditer cette liste pour un nouveau batch
    BG = "/home/tars/crypto-project/CHANNEL/video3/grok_assets"
    SHORTS = [
        ("A",    "OVH.PA",   "OVHcloud",  "+5,5% seulement ?",    f"{BG}/ovhcloud_split_v4.jpg", "CLIP A"),
        ("B",    "OVH.PA",   "OVHcloud",  "Le moat européen",      f"{BG}/ovhcloud_split_v1.jpg", "CLIP B"),
        ("C",    "OVH.PA",   "OVHcloud",  "Le piège du capex",     f"{BG}/ovhcloud_split_v2.jpg", "CLIP C"),
        ("D",    "OVH.PA",   "OVHcloud",  "Le verdict",            f"{BG}/ovhcloud_split_v3.jpg", "CLIP D"),
        ("TRP",  "TRUMPF",   "TRUMPF",    "Le maillon invisible",  f"{BG}/trumpf_split_v2.jpg",   "SHORT"),
        ("ASML", "ASML.AS",  "ASML",      "100% des puces ≤7nm",   f"{BG}/asml_split_v6.jpg",     "SHORT"),
        ("PORT", "×4",       "PORTFOLIO", "Quatre sociétés, une infra", f"{BG}/soitec_split_v4.jpg", "SHORT"),
    ]
    print(f"Batch de {len(SHORTS)} thumbnails Shorts 9:16...")
    for clip_id, ticker, company, tagline, bg, label in SHORTS:
        out = OUT_DIR / f"thumb_short_{clip_id}_{company.lower().replace(' ', '_')}.png"
        await capture(html_for(bg, ticker, company, tagline, label), out)
        print(f"  📸 {out.name}")
    print("✅ Batch terminé")


if __name__ == "__main__":
    asyncio.run(main())
