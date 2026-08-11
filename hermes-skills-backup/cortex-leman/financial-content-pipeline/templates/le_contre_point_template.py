#!/usr/bin/env python3
"""LE CONTRE-POINT — Template générateur podcast long-form bear case.
Format: 1920x1080, voix HenriNeural +0%, BGM -28dB, slide statique, ~8-12 min.

Usage:
  1. cp ce template → CHANNEL/le_contre_point/ep0N_acteur/gen_podcast.py
  2. Éditer TITLE, EPISODE_NUM, TOPIC, SECTIONS (7 sections obligatoires)
  3. python3 gen_podcast.py  (lancer en background, ~15-20 min CPU)

Structure SECTIONS (obligatoire pour conformité AMF):
  01_cold_open    hook + disclaimer AMF renforcé
  02_rappel       rappel thèse bull en 3 piliers
  03_angle1       1er angle d'attaque
  04_angle2       2e angle d'attaque
  05_angle3       3e angle d'attaque
  06_changement   critères falsifiables publics (MOAT éditorial)
  07_verdict      verdict nuancé + outro MiFID II
"""
import asyncio, os, json, subprocess, re
from pathlib import Path
import edge_tts

# ════════════════════════════════════════════════════════════════
#  À ÉDITER POUR CHAQUE ÉPISODE
# ════════════════════════════════════════════════════════════════
TITLE = "OVHcloud"
EPISODE_NUM = 1
TOPIC = "Le bear case"

SECTIONS = {
    "01_cold_open": """[HOOK en 2 phrases sur la valeur].
Aujourd'hui, on fait l'inverse. On décortique tout ce qui peut mal tourner.
Bienvenue dans Le Contre-Point.
Avertissement : ce contenu est fourni à titre informatif et éducatif uniquement. Il ne constitue pas un conseil en investissement, une recommandation d'achat ou de vente, ni une sollicitation. Les instruments financiers mentionnés sont volatils et présentent un risque de perte en capital. Consultez un conseiller financier agréé avant toute décision. L'auteur déclare ses positions éventuelles en fin d'épisode.""",

    "02_rappel": """[Rappel des 3 piliers de la thèse bull présentée dans les Shorts].
Premièrement, [pilier 1].
Deuxièmement, [pilier 2].
Troisièmement, [pilier 3].
C'est la thèse. Elle est cohérente. Maintenant, regardons ce qu'elle ne dit pas.""",

    "03_angle1": """[Premier angle mort — ex: concurrents oubliés, pression structurelle].
[Développement factuel, sourcé].""",

    "04_angle2": """[Deuxième angle — ex: économie capitalistique, ROIC < WACC].
[Développement factuel, sourcé].""",

    "05_angle3": """[Troisième angle — ex: gouvernance, liquidité, risques opérationnels].
[Développement factuel, sourcé].""",

    "06_changement": """Maintenant, l'exercice honnête. Qu'est-ce qui invaliderait ce contre-point ?
Trois critères falsifiables.
Premier : si [condition observable et datée], je retirerais l'angle [N].
Deuxième : si [condition], je retirerais l'angle [N].
Troisième : si [condition], je reconsidérerais la thèse bull dans son ensemble.
Ces trois critères sont publics. Ils sont datés. Ils permettent de vérifier dans six mois, un an, deux ans, si le contre-point tient ou non.""",

    "07_verdict": """Verdict.
[Valeur] n'est pas un mauvais business. [Nuance].
Mais la thèse bull omet trois choses : [récap angles].
Le prix actuel de l'action intègre peut-être ces facteurs. Peut-être pas. C'est à toi de décider.
Ce qui est certain, c'est qu'acheter uniquement pour [narration bull], sans avoir fait l'exercice du contre-point, c'est investir avec un seul œil ouvert.
Disclosure de l'auteur : l'auteur peut détenir, avoir détenu, ou envisager de détenir des positions sur les instruments mentionnés. Les positions sont susceptibles d'évolution sans préavis. Ce contenu ne constitue pas un conseil en investissement au sens de la directive MiFID II. Consultez un professionnel agréé avant toute décision.
C'était Le Contre-Point, un format de L'Effet Composé. Le prochain épisode décortiquera le bear case de [prochaine valeur].
À bientôt.""",
}

# ════════════════════════════════════════════════════════════════
#  CONFIG (ne pas éditer sauf si besoin)
# ════════════════════════════════════════════════════════════════
BASE = Path(__file__).parent
AUDIO_DIR = BASE / "audio"
SLIDES_DIR = BASE / "slides"
OUT_DIR = BASE / "renders"
for d in [AUDIO_DIR, SLIDES_DIR, OUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

VOICE = "fr-FR-HenriNeural"
RATE = "+0%"  # posé pour long-form
BGM = "/home/tars/crypto-project/audio/bgm_stellardrone.mp3"
LOGO = "/home/tars/crypto-project/CHANNEL/branding/logo_lec.png"
ORDER = ["01_cold_open","02_rappel","03_angle1","04_angle2","05_angle3","06_changement","07_verdict"]

# ════════════════════════════════════════════════════════════════

def html_slide():
    logo_path = f"file://{LOGO}" if os.path.exists(LOGO) else ""
    logo_html = f'<img src="{logo_path}" class="logo">' if logo_path else ""
    return f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1920px;height:1080px;overflow:hidden;background:#04102B;font-family:'Inter',sans-serif;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:80px}}
.bg-glow{{position:absolute;width:800px;height:800px;border-radius:50%;background:radial-gradient(circle,rgba(54,212,120,0.08) 0%,transparent 70%);top:50%;left:50%;transform:translate(-50%,-50%)}}
.kicker{{color:#D2B257;font-size:34px;font-weight:700;letter-spacing:6px;text-transform:uppercase;margin-bottom:30px;z-index:1}}
.title{{color:#FFFFFF;font-size:110px;font-weight:900;line-height:1.05;text-align:center;letter-spacing:-2px;margin-bottom:20px;z-index:1}}
.title .accent{{color:#36D478}}
.episode{{color:#E8E8E8;font-size:42px;font-weight:400;letter-spacing:2px;margin-bottom:50px;z-index:1}}
.topic{{color:#FFFFFF;font-size:64px;font-weight:700;opacity:0.85;z-index:1}}
.logo{{position:absolute;top:60px;left:60px;width:120px;height:auto;opacity:0.8}}
.disclaimer{{position:absolute;bottom:40px;left:50%;transform:translateX(-50%);color:rgba(232,232,232,0.4);font-size:20px;font-weight:300;letter-spacing:1px}}
</style></head><body>
<div class="bg-glow"></div>
{logo_html}
<div class='kicker'>L'Effet Composé</div>
<div class='title'><span class='accent'>LE</span> CONTRE-POINT</div>
<div class='episode'>Épisode {EPISODE_NUM}</div>
<div class='topic'>{TITLE} — {TOPIC}</div>
<div class='disclaimer'>Ce contenu ne constitue pas un conseil en investissement · MiFID II</div>
</body></html>"""

async def gen_tts():
    durations = {}
    for name in ORDER:
        path = AUDIO_DIR / f"{name}.mp3"
        await edge_tts.Communicate(SECTIONS[name], VOICE, rate=RATE).save(str(path))
        dur = float(subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",str(path)],
                                   capture_output=True, text=True).stdout.strip())
        durations[name] = {"path": str(path), "duration": dur}
        print(f"  {name}: {dur:.1f}s")
    total = sum(d["duration"] for d in durations.values())
    with open(AUDIO_DIR / "durations.json", "w") as f:
        json.dump(durations, f, indent=2)
    print(f"\n  Total: {total:.1f}s ({total/60:.1f} min)")
    return durations

def capture_slide():
    from playwright.sync_api import sync_playwright
    html_path = SLIDES_DIR / "slide.html"
    html_path.write_text(html_slide(), encoding="utf-8")
    png_path = OUT_DIR / "slide.png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(1000)
        page.screenshot(path=str(png_path), full_page=False)
        browser.close()
    print(f"  📸 Slide: {png_path}")
    return png_path

def concat_audio(durations):
    al = AUDIO_DIR / "concat.txt"
    with open(al, "w") as f:
        for key in ORDER:
            f.write(f"file '{durations[key]['path']}'\n")
    full = AUDIO_DIR / "full.mp3"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(al),"-c","copy",str(full)],
                   capture_output=True, text=True, check=True)
    return full

def gen_subs(durations, out_path):
    def fmt(s):
        h=int(s//3600);m=int((s%3600)//60);sec=int(s%60);ms=int((s%1)*1000)
        return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"
    entries = []
    idx = 1
    cumul = 0.0
    for key in ORDER:
        text = SECTIONS[key].replace("\n", " ")
        dur = durations[key]["duration"]
        phrases = re.split(r'(?<=[.!?])\s+', text)
        total_chars = sum(len(p) for p in phrases)
        offset = cumul
        for phrase in phrases:
            phrase = phrase.strip()
            if not phrase:
                continue
            phrase_dur = dur * (len(phrase) / total_chars)
            entries.append((idx, offset, offset+phrase_dur, phrase))
            offset += phrase_dur
            idx += 1
        cumul += dur
    with open(out_path, "w") as f:
        for i, s, e, t in entries:
            f.write(f"{i}\n{fmt(s)} --> {fmt(e)}\n{t}\n\n")
    return out_path

def srt_to_ass_longform(srt, ass):
    subprocess.run(["ffmpeg","-y","-i",str(srt),str(ass)], capture_output=True, text=True, check=True)
    header = """[Script Info]
Title: LE CONTRE-POINT
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Inter,52,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,4,2,2,120,120,80,1

"""
    with open(ass) as f:
        lines = f.readlines()
    with open(ass, "w") as f:
        f.write(header)
        in_ev = False
        for line in lines:
            if line.strip().startswith("[Events]"):
                in_ev = True
            if in_ev:
                f.write(line)

def final_render(slide_png, audio_full, bgm, ass, out):
    dur = float(subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",str(audio_full)],
                               capture_output=True,text=True).stdout.strip())
    fadeout = max(0, dur-4)
    subprocess.run(["ffmpeg","-y",
                    "-loop","1","-framerate","30","-t",f"{dur:.3f}","-i",str(slide_png),
                    "-i",str(audio_full),
                    "-i",bgm,
                    "-vf",f"ass={str(ass).replace('/',chr(92)+'/')},format=yuv420p",
                    "-filter_complex",
                    f"[2:a]volume=-28dB,afade=t=in:st=0:d=3,afade=t=out:st={fadeout:.2f}:d=4[bgm];"
                    f"[1:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]",
                    "-map","0:v","-map","[aout]",
                    "-c:v","libx264","-preset","medium","-crf","22","-pix_fmt","yuv420p","-r","30",
                    "-c:a","aac","-b:a","160k","-shortest",str(out)],
                   capture_output=True, text=True, check=True)
    return out

if __name__ == "__main__":
    print("=" * 60)
    print(f"  LE CONTRE-POINT — Épisode {EPISODE_NUM} : {TITLE}")
    print("=" * 60)
    print("\n[1/5] Capture slide statique...")
    slide = capture_slide()
    print("\n[2/5] Génération voix (edge-tts, rate +0%)...")
    durations = asyncio.run(gen_tts())
    print("\n[3/5] Concat audio...")
    audio_full = concat_audio(durations)
    print("\n[4/5] Sous-titres...")
    srt = gen_subs(durations, AUDIO_DIR / "subs.srt")
    ass = AUDIO_DIR / "subs.ass"
    srt_to_ass_longform(srt, ass)
    print("\n[5/5] Render final...")
    OUT = BASE / f"le_contre_point_ep{EPISODE_NUM:02d}_{TITLE.lower().replace(' ','_')}.mp4"
    final_render(slide, audio_full, BGM, ass, OUT)
    sz = os.path.getsize(OUT)/(1024*1024)
    dur = float(subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",str(OUT)],
                               capture_output=True,text=True).stdout.strip())
    print(f"\n✅ {OUT}")
    print(f"   {sz:.1f} MB · {dur:.1f}s ({dur/60:.1f} min)")
