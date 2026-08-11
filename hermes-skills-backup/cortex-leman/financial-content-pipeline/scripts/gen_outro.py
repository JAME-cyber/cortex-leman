#!/usr/bin/env python3
"""Outro signature réutilisable — L'EFFET COMPOSÉ.
Produit outro_signature.mp4 (1080x1920, ~11s) à append à la fin de chaque clip.

Stack : Playwright (slide HTML) + edge-tts HenriNeural +10% + ffmpeg (Ken Burns + BGM).
Le disclaimer AMF est intégré à la fois en texte (slide) et en voix (TTS) — un seul
segment porte toute la clôture: CTA abonnement + tagline + acteurs + disclaimer.

Usage :
    python gen_outro.py
    → produit branding/outro_signature/outro_signature.mp4

Pour append à un clip existant (même codec H.264/AAC, le demuxer concat marche) :
    echo "file 'clip_body.mp4'" > list.txt
    echo "file '/abs/outro_signature.mp4'" >> list.txt
    ffmpeg -y -f concat -safe 0 -i list.txt -c copy clip_final.mp4
"""
import asyncio, edge_tts, os, subprocess
from playwright.sync_api import sync_playwright

BASE = "/home/tars/crypto-project/CHANNEL/branding/outro_signature"
BGM = "/home/tars/crypto-project/audio/bgm_stellardrone.mp3"
VOICE = "fr-FR-HenriNeural"
RATE = "+10%"
FPS = 30
os.makedirs(BASE, exist_ok=True)

# Slide HTML — palette LEC : navy #04102B / or #D2B257 / vert #36D478
HTML = """<!doctype html><html><head><meta charset='utf-8'><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;background:#04102B;color:#EAF2FF;font-family:'Segoe UI',Helvetica,Arial,sans-serif;overflow:hidden;position:relative}
.bg-glow{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(210,178,87,0.18) 0%,rgba(4,16,43,0) 55%)}
.wrap{position:absolute;inset:0;padding:80px 60px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}
.kicker{font-size:24px;letter-spacing:8px;color:#9FB3CC;text-transform:uppercase;font-weight:700;margin-bottom:30px}
.logo{font-size:78px;font-weight:900;line-height:1.1;margin-bottom:8px}
.logo .gr{color:#36D478} .logo .go{color:#D2B257}
.logo-sub{font-size:22px;letter-spacing:3px;color:#9FB3CC;margin-bottom:60px;text-transform:uppercase}
.cta{background:linear-gradient(135deg,#D2B257 0%,#E8C56A 100%);color:#04102B;font-size:46px;font-weight:900;padding:22px 56px;border-radius:14px;margin-bottom:40px;box-shadow:0 8px 32px rgba(210,178,87,0.4);text-transform:uppercase;letter-spacing:2px}
.cta .arrow{display:inline-block;margin-left:14px;font-weight:300}
.tagline{font-size:30px;color:#EAF2FF;font-weight:600;line-height:1.4;max-width:800px;margin-bottom:40px}
.tagline .go{color:#D2B257}
.actors{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}
.actors .pill{background:rgba(54,212,120,0.1);border:1.5px solid #36D478;color:#36D478;font-size:20px;font-weight:700;padding:8px 20px;border-radius:30px;letter-spacing:1px}
.disclaimer{position:absolute;bottom:36px;left:60px;right:60px;font-size:16px;color:#5e7591;border-top:2px solid rgba(20,35,61,0.8);padding-top:14px;line-height:1.5}
.disclaimer strong{color:#7a92ad}
</style></head><body>
<div class='bg-glow'></div>
<div class='wrap'>
  <div class='kicker'>Infrastructure physique · Euronext</div>
  <div class='logo'><span class='gr'>L'EFFET</span> <span class='go'>COMPOSÉ</span></div>
  <div class='logo-sub'>Les maillons invisibles des puces, du cloud, de l'IA</div>
  <div class='cta'>Abonne-toi<span class='arrow'>→</span></div>
  <div class='tagline'>Une nouvelle enquête <span class='go'>chaque semaine</span><br>sur l'infrastructure qui fait tourner le monde.</div>
  <div class='actors'>
    <span class='pill'>OVHcloud</span>
    <span class='pill'>ASML</span>
    <span class='pill'>TRUMPF</span>
    <span class='pill'>Soitec</span>
  </div>
</div>
<div class='disclaimer'>
  <strong>⚠️ Ce contenu est strictement informatif et ne constitue pas un conseil en investissement</strong><br>
  ni une recommandation d'achat ou de vente. L'investissement comporte un risque de perte en capital.
</div>
</body></html>"""

# --- 1. Capture slide ---
SLIDE_PATH = f"{BASE}/outro_slide.png"
html_path = f"{BASE}/outro.html"
open(html_path, "w").write(HTML)
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg.goto(f"file://{html_path}")
    pg.wait_for_timeout(500)
    pg.screenshot(path=SLIDE_PATH, type="png")
    b.close()
print(f"✅ Slide capturée: {SLIDE_PATH}")

# --- 2. TTS ---
TEXT = ("Abonne-toi à L'Effet Composé. Une nouvelle enquête chaque semaine sur l'infrastructure "
        "physique qui fait tourner le monde. Ce contenu est strictement informatif et ne constitue "
        "pas un conseil en investissement.")
AUDIO_PATH = f"{BASE}/outro_voix.mp3"
async def tts():
    await edge_tts.Communicate(TEXT, VOICE, rate=RATE).save(AUDIO_PATH)
asyncio.run(tts())
r = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",AUDIO_PATH],
                   capture_output=True, text=True)
D = float(r.stdout.strip())
print(f"✅ TTS: {AUDIO_PATH} ({D:.1f}s)")

# --- 3. Ken Burns + BGM + voix ---
frames = int(D * FPS)
zoom_inc = 0.03 / frames
filt = (f"scale=2160:3840:force_original_aspect_ratio=increase,"
        f"crop=2160:3840,"
        f"zoompan=z='min(zoom+{zoom_inc:.6f},1.03)':d={frames}:s=1080x1920:fps={FPS},"
        f"format=yuv420p")
tmp_v = f"{BASE}/_video.mp4"
subprocess.run(["ffmpeg","-y","-loop","1","-i",SLIDE_PATH,"-i",AUDIO_PATH,
                "-vf",filt,"-t",str(D),
                "-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p","-r",str(FPS),
                "-c:a","aac","-b:a","128k","-shortest",tmp_v], check=True,
               capture_output=True)

OUT = f"{BASE}/outro_signature.mp4"
fadeout = max(0, D - 2)
subprocess.run(["ffmpeg","-y","-i",tmp_v,"-i",BGM,"-filter_complex",
                f"[0:a]aformat=channel_layouts=stereo[voice];"
                f"[1:a]aformat=channel_layouts=stereo,atrim=0:{D:.2f},asetpts=PTS-STARTPTS,"
                f"afade=t=in:st=0:d=1,afade=t=out:st={fadeout:.2f}:d=2,volume=0.06[bgm];"
                f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.95[aout]",
                "-map","0:v","-map","[aout]",
                "-c:v","copy","-c:a","aac","-b:a","128k","-shortest",OUT], check=True,
               capture_output=True)
os.remove(tmp_v)
sz = os.path.getsize(OUT) / (1024*1024)
print(f"\n✅ {OUT} ({sz:.1f} MB · {D:.1f}s)")
print("   → Append à la fin de chaque clip via demuxer concat (même codec).")
