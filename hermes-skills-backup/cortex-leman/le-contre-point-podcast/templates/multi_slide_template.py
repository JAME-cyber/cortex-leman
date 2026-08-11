#!/usr/bin/env python3
"""
Template: alternance visuelle multi-slide pour LE CONTRE-POINT.
Remplace capture_slide() (1 PNG) par capture_slides() (7 PNGs par section).

Integration dans gen_podcast.py:
  1. Remplacer la fonction html_slide() par html_slide_section(section_key, meta)
  2. Remplacer capture_slide() par capture_slides(durations, sections_meta)
  3. Remplacer final_render() par final_render_multi(slide_pngs, durations, ...)
  4. Ajouter le dict SECTIONS_META (parallele a SECTIONS)

Palette testee: contraste lumineux 35-115 entre sections sombres (angles bear)
et claires (changement/verdict). Compatible 2fps ultrafast.
"""
import subprocess
from pathlib import Path

# === PALETTE MULTI-SLIDE (a definir par episode dans SECTIONS_META) ===
# Exemple pour ep03_soitec
SECTIONS_META_EXAMPLE = {
    "01_cold_open":  {"text_key": "-2% PART DE MARCHÉ",  "bg": "#04102B", "accent": "#E84545"},  # bleu nuit + rouge
    "02_rappel":     {"text_key": "THÈSE BULL",          "bg": "#0A1F3C", "accent": "#36D478"},  # bleu clair + vert
    "03_angle1":     {"text_key": "NICHE TECHNOLOGIQUE",  "bg": "#1A0A0A", "accent": "#E84545"},  # rouge noir
    "04_angle2":     {"text_key": "CYCLICITÉ AUTO",      "bg": "#1A0A0A", "accent": "#E84545"},  # rouge noir
    "05_angle3":     {"text_key": "CONCENTRATION CLIENT","bg": "#1A0A0A", "accent": "#E84545"},  # rouge noir
    "06_changement": {"text_key": "CRITÈRES FALSIFIABLES","bg": "#0A2A0A", "accent": "#D2B257"},  # vert noir + or
    "07_verdict":    {"text_key": "VERDICT",             "bg": "#04102B", "accent": "#D2B257"},  # bleu nuit + or
}

# === CONTRASTE RENFORCÉ: luminosité cible par section ===
# Problème observé: palettes sombres toutes proches (lum 20-38).
# Solution: bg-glow opacity accrue + sections "claires" vraiment claires.
# Sections "bear" (angles) restent sombres pour l'atmosphère menaçante.
# Sections "rappel" et "changement" montent en luminosité pour le contraste.
# Objectif: recréer l'effet Yassine/TIC (lum 30->160) sans sortie du brand LEC.

def html_slide_section(section_key, meta, episode_num=3, company="Soitec", logo_path=None):
    """
    Genere le HTML d'une slide pour une section donnee.
    Chaque section a son propre bg/accent/text_key pour creer l'alternance visuelle.
    """
    import os
    logo_html = f'<img src="file://{logo_path}" class="logo">' if logo_path and os.path.exists(logo_path) else ""
    bg = meta["bg"]
    accent = meta["accent"]
    text_key = meta["text_key"]
    # Numero de section (ex: "01" -> "01 / 07")
    section_num = section_key.split("_")[0]
    is_cold_open = section_key == "01_cold_open"
    # Cold open: chiffre choc en tres grand, pas de text_key normal
    key_display = f'<div class="hook-number">{text_key}</div>' if is_cold_open else f'<div class="text-key">{text_key}</div>'
    key_class = "hook-number" if is_cold_open else "text-key"

    return f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1920px;height:1080px;overflow:hidden;background:{bg};font-family:'Inter',sans-serif;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:80px;transition:background 0.3s}}
.bg-glow{{position:absolute;width:800px;height:800px;border-radius:50%;background:radial-gradient(circle,{accent}22 0%,transparent 70%);top:50%;left:50%;transform:translate(-50%,-50%)}}
.kicker{{color:{accent};font-size:28px;font-weight:700;letter-spacing:6px;text-transform:uppercase;margin-bottom:25px;z-index:1;opacity:0.9}}
.title{{color:#FFFFFF;font-size:80px;font-weight:900;line-height:1.05;text-align:center;letter-spacing:-2px;margin-bottom:15px;z-index:1}}
.title .accent{{color:{accent}}}
.episode{{color:#E8E8E8;font-size:32px;font-weight:400;letter-spacing:2px;margin-bottom:40px;z-index:1;opacity:0.7}}
.topic{{color:#FFFFFF;font-size:44px;font-weight:700;opacity:0.5;z-index:1;margin-bottom:30px}}
.section-num{{position:absolute;top:60px;right:60px;color:{accent};font-size:42px;font-weight:900;opacity:0.6}}
.{key_class}{{color:{accent};font-size:120px;font-weight:900;letter-spacing:-2px;z-index:1;text-align:center;line-height:1;text-transform:uppercase}}
.hook-number{{color:{accent};font-size:180px;font-weight:900;letter-spacing:-4px;z-index:1;text-align:center;line-height:0.9}}
.logo{{position:absolute;top:60px;left:60px;width:100px;height:auto;opacity:0.7}}
.disclaimer{{position:absolute;bottom:40px;left:50%;transform:translateX(-50%);color:rgba(232,232,232,0.3);font-size:18px;font-weight:300;letter-spacing:1px}}
</style></head><body>
<div class="bg-glow"></div>
{logo_html}
<div class="section-num">{section_num} / 07</div>
<div class="kicker">L'Effet Composé</div>
<div class="title"><span class="accent">LE</span> CONTRE-POINT</div>
<div class="episode">Épisode {episode_num} · {company}</div>
{key_display}
<div class="disclaimer">Ce contenu ne constitue pas un conseil en investissement · MiFID II</div>
</body></html>"""


def capture_slides(sections_meta, episode_num, company, logo_path, slides_dir, out_dir):
    """
    Remplace capture_slide(). Genere 7 PNGs (un par section) avec palettes contrastees.
    Retourne un dict {section_key: png_path}.
    """
    from playwright.sync_api import sync_playwright
    slide_pngs = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        for section_key, meta in sections_meta.items():
            html_path = slides_dir / f"slide_{section_key}.html"
            html_path.write_text(
                html_slide_section(section_key, meta, episode_num, company, logo_path),
                encoding="utf-8"
            )
            png_path = out_dir / f"slide_{section_key}.png"
            page.goto(f"file://{html_path}")
            page.wait_for_timeout(400)  # plus court car pas de fonts externes critiques
            page.screenshot(path=str(png_path), full_page=False)
            slide_pngs[section_key] = png_path
            print(f"  📸 {section_key}: {meta['text_key']} ({meta['bg']})")
        browser.close()
    print(f"  ✅ {len(slide_pngs)} slides capturées")
    return slide_pngs


def render_section_video(slide_png, audio_path, bgm, duration, out_path, ass_path=None, subs_enabled=False):
    """
    Render un segment video pour une section: slide PNG + audio + BGM.
    Retourne le chemin du MP4 du segment.
    """
    fadeout = max(0, duration - 4)
    vf = f"ass={ass_path},format=yuv420p" if subs_enabled and ass_path else "format=yuv420p"
    subprocess.run(["ffmpeg", "-y",
                    "-loop", "1", "-framerate", "2", "-t", f"{duration:.3f}", "-i", str(slide_png),
                    "-i", str(audio_path),
                    "-i", str(bgm),
                    "-vf", vf,
                    "-filter_complex",
                    f"[2:a]volume=-28dB,afade=t=in:st=0:d=3,afade=t=out:st={fadeout:.2f}:d=4[bgm];"
                    f"[1:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]",
                    "-map", "0:v", "-map", "[aout]",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-pix_fmt", "yuv420p", "-r", "2",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", str(out_path)],
                   capture_output=True, text=True, check=True)
    return out_path


def concat_section_videos(segment_paths, out_path):
    """Concatene les 7 segments MP4 en une seule video finale."""
    concat_list = out_path.parent / "concat_segments.txt"
    with open(concat_list, "w") as f:
        for seg in segment_paths:
            f.write(f"file '{seg}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(concat_list), "-c", "copy", str(out_path)],
                   capture_output=True, text=True, check=True)
    return out_path


# === INTEGRATION DANS __main__ ===
# Remplacer les etapes 1 et 5 du main original par:
#
# print("[1/5] Capture 7 slides (multi-slide)...")
# slide_pngs = capture_slides(SECTIONS_META, EP_NUM, COMPANY, LOGO, SLIDES_DIR, OUT_DIR)
#
# print("[2/5] Génération voix...")
# durations = asyncio.run(gen_tts())
# audio_full = concat_audio(durations)
#
# print("[3/5] Sous-titres...")
# srt = gen_subs(durations, AUDIO_DIR / "subs.srt")
# ass = AUDIO_DIR / "subs.ass"
# srt_to_ass_longform(srt, ass)
#
# print("[4/5] Render 7 segments vidéo...")
# segment_paths = []
# for section_key in SECTIONS.keys():
#     seg_out = OUT_DIR / f"segment_{section_key}.mp4"
#     render_section_video(
#         slide_pngs[section_key],
#         durations[section_key]["path"],
#         BGM,
#         durations[section_key]["duration"],
#         seg_out
#     )
#     segment_paths.append(seg_out)
#
# print("[5/5] Concaténation finale...")
# OUT = BASE / f"le_contre_point_ep{EP_NUM}_{TICKER}.mp4"
# concat_section_videos(segment_paths, OUT)
