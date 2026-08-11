#!/usr/bin/env python3
"""Clip portfolio — présente N acteurs visuellement en un seul clip 9:16.
Structuré pour L'EFFET COMPOSÉ (4 acteurs: OVHcloud/ASML/Trumpf/Soitec) mais
paramétrable pour toute série multi-acteurs.

Structure (validée 2026-07-19, clip portfolio 71.4s):
  1. Hook      (~5s)   — "Quatre entreprises. Une infrastructure."
  2..N+1. Acteurs (~10s chacun) — photo Grok en bg + Ken Burns + tagline + desc
  N+2. Synthèse (~8s)  — 3 mots-clés de l'offre éditoriale

Leçons intégrées (voir SKILL.md):
  - ORDER constante module-level unique (anti-drift naming)
  - Chaque acteur: dict (key, name, photo, tagline, desc) itéré
  - Ken Burns alterné in/out pour breaker la monotonie
  - CSS bg brightness(0.65) saturate(1.15) + overlay 0.65→0.10→0.65 (base Trumpf V2)
  - Intro 5s via filter_complex (PAS demuxer)
  - Outro 10.8s via demuxer concat
  - post-concat: assert abs(expected-actual) < 0.5

Adaptation: copier ce template, éditer ACTEURS + VOIX + html_hook/html_synthese.
"""
import asyncio, os, json, subprocess
from pathlib import Path
import edge_tts

# === CONFIG ===
BASE = Path("/home/tars/crypto-project/CHANNEL/videoN_portfolio")
GROK = Path("/home/tars/crypto-project/CHANNEL/video3/grok_assets")
INTRO = "/home/tars/crypto-project/CHANNEL/video3/clips/intro_9x16.mp4"
OUTRO = "/home/tars/crypto-project/CHANNEL/branding/outro_signature/outro_signature.mp4"
BGM = "/home/tars/crypto-project/audio/bgm_stellardrone.mp3"
VOICE = "fr-FR-HenriNeural"
RATE = "+10%"

# === Acteurs (key, name, photo, tagline, desc) ===
ACTEURS = [
    ("ovh",  "OVHcloud", GROK / "ovhcloud_split_v4.jpg", "Le souverain européen",
     "Data centers souverains, qualification SecNumCloud. La pièce que les Américains ne peuvent pas répliquer."),
    # ... ajouter/modifier
]

# === ORDRE UNIQUE (anti-drift, voir SKILL.md) ===
ORDER = ["01_hook"] + [f"0{i+2}_{a[0]}" for i, a in enumerate(ACTEURS)] + [f"{len(ACTEURS)+2:02d}_synthese"]
# ex: ["01_hook", "02_ovh", "03_asml", "04_trp", "05_soi", "06_synthese"]

# === VOIX (clés DOIVENT matcher ORDER) ===
VOIX = {
    "01_hook": "Quatre entreprises. Quatre angles d'attaque sur l'infrastructure physique qui fait tourner le monde.",
    # ... une entrée par clé dans ORDER
}

def html_slide_bg(photo_path, kicker, name, tagline, idx):
    """Slide avec photo en background (CSS base Trumpf V2)."""
    return f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;background:#04102B;font-family:'Inter',sans-serif}}
.bg{{position:absolute;inset:0;background-image:url('file://{photo_path}');background-size:cover;background-position:center;filter:brightness(0.65) saturate(1.15)}}
.overlay{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(4,16,43,0.65) 0%,rgba(4,16,43,0.10) 50%,rgba(4,16,43,0.85) 100%)}}
.content{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-end;padding:90px 80px 140px}}
.kicker{{color:#D2B257;font-size:36px;font-weight:700;letter-spacing:3px;text-transform:uppercase;margin-bottom:24px}}
.name{{color:#FFFFFF;font-size:128px;font-weight:900;line-height:0.95;margin-bottom:32px;text-shadow:0 4px 30px rgba(0,0,0,0.6)}}
.tagline{{color:#36D478;font-size:48px;font-weight:700;margin-bottom:40px}}
.bar{{position:absolute;bottom:60px;left:80px;height:4px;background:#D2B257;width:140px;border-radius:2px}}
</style></head><body>
<div class='bg'></div><div class='overlay'></div>
<div class='content'>
  <div class='kicker'>Acteur {idx}/{len(ACTEURS)}</div>
  <div class='name'>{name}</div>
  <div class='tagline'>{tagline}</div>
</div>
<div class='bar'></div>
</body></html>"""

# === Pipeline identique aux autres clips ===
# (gen_tts, capture_slides via Playwright, ken_burns, concat, subs, final_assemble)
# Voir ~/crypto-project/CHANNEL/video6_portfolio/gen_portfolio.py pour la version pleine.
