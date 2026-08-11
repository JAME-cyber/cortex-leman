#!/usr/bin/env python3
"""
Funnel build template — Hook→Build→Climax→CTA (Club Med style).
Copy and adapt: change VO_SEGMENTS, SUB_TEXT, asset paths, pricing.

Structure: [Stinger] → [Hook card] → [Build clips] → [Climax clip] → [Sunset outro]
~40-45s total. Uses slow-mo setpts (no loops), audio separation (no overlap).
"""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ═══ CONFIG ═══
BASE = Path(".")  # project root
CLIPS_DIR = BASE / "assets" / "clips"       # AI-generated clips (~5s each)
STINGER = BASE / "assets" / "stinger.mp4"    # brand signature (~3.5s, has audio)
OUTRO = BASE / "assets" / "outro.mp4"        # sunset/silhouettes (~4s, no audio)
MUSIC = BASE / "assets" / "music.mp3"
FONT_DIR = BASE / "assets" / "fonts"
OUT = BASE / "output"
TMP = BASE / "renders" / "funnel_tmp"
TMP.mkdir(parents=True, exist_ok=True)

W, H, FPS = 720, 1280, 30
BUFFER = 0.8
BG_COLOR = (38, 30, 27)       # terracotta dark
ACCENT = "#D88A22"            # saffron
ACCENT2 = "#5BA897"           # teal
TEXT = "#F5E6D3"              # cream
SUB = "#C4956C"               # ochre

# ═══ VO SCRIPT — funnel style ═══
VO_SEGMENTS = [
    ("hook",     "Et si vos enfants [désir transformateur] ?"),
    ("build_1",  "[Feature 1]. [Bénéfice court]."),
    ("build_2",  "[Feature 2]. [Bénéfice court]."),
    ("build_3",  "[Feature 3]. [Bénéfice court]."),
    ("build_4",  "[Feature 4]. [Bénéfice court]."),
    ("climax",   "[Promesse émotionnelle — aventure, amitié, souvenirs]."),
    ("cta",      "Réservez ! [Dates] [Lieu] [Prix]."),
]

SUB_TEXT = {
    "hook":    r"Et si vos enfants\N [désir]\N cet été ?",
    "build_1": r"[Feature 1]\N [Bénéfice]",
    "build_2": r"[Feature 2]\N [Bénéfice]",
    "build_3": r"[Feature 3]\N [Bénéfice]",
    "build_4": r"[Feature 4]\N [Bénéfice]",
    "climax":  r"[Promesse émotionnelle]",
    "cta":     r"Réservez !\N [Dates] [Lieu]\N [Prix]",
}

# Clip mapping: VO name → asset filename (5s AI clips)
CLIP_MAP = {
    "build_1": "clip_1.mp4",
    "build_2": "clip_2.mp4",
    "build_3": "clip_3.mp4",
    "build_4": "clip_4.mp4",
    "climax":  "clip_climax.mp4",   # reuse most emotional clip
}

# ═══ HELPERS ═══
def font(sz, bold=True):
    name = "Montserrat-SemiBold.ttf" if bold else "Montserrat-Regular.ttf"
    p = FONT_DIR / name
    return ImageFont.truetype(str(p), sz) if p.exists() else ImageFont.load_default()

def run(cmd, label=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ {label}: {r.stderr[-300:]}"); sys.exit(1)

def ffprobe_dur(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())

def prep_video(name, src, duration):
    """Slow-mo via setpts — no loops, seamless."""
    out = TMP / f"seg_{name}.mp4"
    src_dur = ffprobe_dur(src)
    if src_dur >= duration:
        run(["ffmpeg", "-y", "-i", str(src), "-t", str(duration),
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
             "-r", str(FPS), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
             "-an", str(out)], name)
    else:
        factor = duration / src_dur
        run(["ffmpeg", "-y", "-i", str(src),
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
             f"setpts={factor:.4f}*PTS",
             "-r", str(FPS), "-t", str(duration),
             "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
             "-an", str(out)], name)
        print(f"  (slow-mo {factor:.3f})")
    return out

def prep_image(name, img_path, duration, zoom=1.05):
    out = TMP / f"seg_{name}.mp4"
    run(["ffmpeg", "-y", "-loop", "1", "-i", str(img_path),
         "-t", str(duration),
         "-vf", f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
                f"zoompan=z='{zoom}':d={int(duration*FPS)}:s={W}x{H}:fps={FPS}",
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(out)], name)
    return out

def fmt_time(s):
    h=int(s//3600); m=int((s%3600)//60); sec=s%60
    return f"{h}:{m:02d}:{sec:05.2f}"

# ═══ BUILD ═══
print("=== Generating VO ===")
durations = {}
for name, text in VO_SEGMENTS:
    vo_path = TMP / f"{name}.wav"
    run(["edge-tts", "--voice", "fr-CH-ArianeNeural", "--text", text,
         "--write-media", str(vo_path)], name)
    durations[name] = ffprobe_dur(vo_path)

print("\n=== Building segments ===")
segs = []

# 1. Stinger
stinger_seg = TMP / "seg_stinger.mp4"
run(["ffmpeg", "-y", "-i", str(STINGER),
     "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
     "-r", str(FPS), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "128k", str(stinger_seg)])
segs.append(stinger_seg)
stinger_dur = ffprobe_dur(stinger_seg)

# 2. Hook card
hook_dur = durations["hook"] + 0.5
hook_img = TMP / "hook.png"
img = Image.new('RGB', (W, H), BG_COLOR)
d = ImageDraw.Draw(img)
d.text((W//2, 540), "[QUESTION]", fill=TEXT, font=font(42), anchor='mt')
d.text((W//2, 620), "[KEYWORD]", fill=ACCENT, font=font(52), anchor='mt')
img.save(str(hook_img), quality=95)
segs.append(prep_image("hook", hook_img, hook_dur))

# 3. Build clips (rapid cuts)
for vo_name, clip_file in CLIP_MAP.items():
    if vo_name == "climax": continue
    dur = durations[vo_name] + BUFFER
    segs.append(prep_video(vo_name, CLIPS_DIR / clip_file, dur))

# 4. Climax (longer shots)
climax_dur = durations["climax"] + 1.5
segs.append(prep_video("climax", CLIPS_DIR / CLIP_MAP["climax"], climax_dur))

# 5. Outro — extend via ping-pong if shorter than CTA VO (see references/unified-outro.md)
cta_vo_dur = durations["cta"]
outro_needed = cta_vo_dur + 1.5
outro_src_dur = ffprobe_dur(str(OUTRO))
outro_seg = TMP / "seg_outro.mp4"

if outro_src_dur >= outro_needed:
    # Outro is long enough, just scale + trim
    run(["ffmpeg", "-y", "-i", str(OUTRO),
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
         "-r", str(FPS), "-t", f"{outro_needed:.1f}",
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(outro_seg)])
else:
    # Ping-pong: forward + reverse + forward, then trim
    scaled = TMP / "outro_scaled.mp4"
    run(["ffmpeg", "-y", "-i", str(OUTRO),
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
         "-r", str(FPS), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
         "-an", str(scaled)])
    reversed_cl = TMP / "outro_rev.mp4"
    run(["ffmpeg", "-y", "-i", str(scaled), "-vf", "reverse",
         "-r", str(FPS), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
         "-an", str(reversed_cl)])
    pp_list = TMP / "outro_pp.txt"
    with open(pp_list, "w") as f:
        f.write(f"file '{scaled.absolute()}'\n")
        f.write(f"file '{reversed_cl.absolute()}'\n")
        f.write(f"file '{scaled.absolute()}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(pp_list),
         "-t", f"{outro_needed:.1f}",
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(outro_seg)])
    print(f"  (ping-pong: {outro_src_dur:.1f}s → {outro_needed:.1f}s)")
segs.append(outro_seg)

# Concat video
concat_list = TMP / "concat.txt"
with open(concat_list, "w") as f:
    for s in segs: f.write(f"file '{s.absolute()}'\n")
video = TMP / "video.mp4"
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
     "-c", "copy", str(video)])
video_dur = ffprobe_dur(video)

# ═══ AUDIO (separated: stinger alone, then VO+music) ═══
stinger_a = TMP / "stinger_a.aac"
run(["ffmpeg", "-y", "-i", str(STINGER), "-vn", "-c:a", "aac", "-b:a", "128k", str(stinger_a)])

# VO with timing offsets
vo_timing = []
t = stinger_dur  # VO starts AFTER stinger
d = durations["hook"]; vo_timing.append(("hook", t, d)); t += d + 0.5
for v in ["build_1", "build_2", "build_3", "build_4"]:
    d = durations[v]; vo_timing.append((v, t, d)); t += d + BUFFER
d = durations["climax"]; vo_timing.append(("climax", t, d)); t += d + 1.5
d = durations["cta"]; vo_timing.append(("cta", t, d)); t += d

# Delay each VO segment to its timestamp
filter_parts, inputs = [], []
for i, (name, start, dur) in enumerate(vo_timing):
    inputs += ["-i", str(TMP / f"{name}.wav")]
    delay = int(start * 1000)
    filter_parts.append(f"[{i}:a]adelay={delay}|{delay}[d{i}]")
mix = "".join(f"[d{i}]" for i in range(len(vo_timing)))
filter_complex = ";".join(filter_parts) + f";{mix}amix=inputs={len(vo_timing)}:duration=longest:normalize=0[vout]"
vo_padded = TMP / "vo_padded.wav"
run(["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[vout]",
     "-c:a", "pcm_s16le", str(vo_padded)])

# Final mix: stinger audio + VO + music (music delayed past stinger)
final_audio = TMP / "final_audio.aac"
run(["ffmpeg", "-y",
     "-i", str(stinger_a), "-i", str(vo_padded), "-i", str(MUSIC),
     "-filter_complex",
     f"[0:a]volume=1.0[a_sting];"
     f"[1:a]volume=2.5[a_vo];"
     f"[2:a]volume=0.12,atrim=0:{video_dur:.1f},adelay={int(stinger_dur*1000+200)}|{int(stinger_dur*1000+200)},"
     f"afade=t=out:st={video_dur-2.0:.1f}:d=2.0[a_mus];"
     f"[a_sting][a_vo][a_mus]amix=inputs=3:duration=longest:normalize=0[aout]",
     "-map", "[aout]", "-c:a", "aac", "-b:a", "128k",
     "-t", str(video_dur), str(final_audio)])

# ═══ SUBTITLES ═══
subs_file = TMP / "subs.ass"
with open(subs_file, "w") as f:
    f.write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Montserrat SemiBold,38,&H00D3E8F5,&H001E1E7A,&H00212E49,&H80000A1A,-1,0,0,0,100,100,0,0,1,3,1,2,60,60,140,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
    for name, start, dur in vo_timing:
        txt = SUB_TEXT.get(name, "")
        if txt:
            f.write(f"Dialogue: 0,{fmt_time(start)},{fmt_time(start+dur)},Default,,0,0,0,,{txt}\n")

# ═══ FINAL ═══
final = OUT / "funnel_final.mp4"
run(["ffmpeg", "-y", "-i", str(video), "-i", str(final_audio),
     "-map", "0:v", "-map", "1:a",
     "-vf", f"subtitles={subs_file}",
     "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "128k", "-t", str(video_dur), str(final)])
print(f"\n✅ {final.name}: {ffprobe_dur(final):.1f}s, {final.stat().st_size/1048576:.1f}MB")

# TG compress
tg = Path(f"/tmp/TG_{final.name}")
run(["ffmpeg", "-y", "-i", str(final),
     "-c:v", "libx264", "-crf", "26", "-maxrate", "3200k", "-bufsize", "6400k",
     "-preset", "fast", "-vf", f"scale={W}:{H}",
     "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(tg)])
print(f"📱 TG: {tg.stat().st_size/1048576:.1f}MB → {tg}")
