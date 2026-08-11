#!/usr/bin/env python3
"""
BATCH FUNNEL BUILDER — Club Med style for all vertical videos
Structure: [Stinger] → [Hook question + context] → [Build rapid cuts] → [Climax] → [Sunset + CTA VO]

KEY TECHNIQUES (battle-tested):
- Hook VO prefixed with association/brand context (~8s, not 3.5s) — prevents "entering too fast"
- Brand identity: cream bg, Playfair Display (titles), Poppins (body), logo, dates, contact on hook card
- Font validation: verify .ttf files aren't corrupted HTML (file command)
- PIL API: Image.Resampling.LANCZOS (not Image.LANCZOS — deprecated Pillow >= 9.1)
- Slow-mo setpts instead of loops (factors 1.02-1.18 = invisible)
- Audio: stinger isolated, VO+music delayed via adelay=3700 (stinger_dur+200ms)
- Sunset ping-pong: forward+reverse+forward for long CTA VOs (>8s)
- No CTA price card when VO already announces prices
- clip_trims: split same clip at start/mid/end timestamps when only 1 source available

Usage: python3 build_funnel_all.py [video_id1] [video_id2] ...
"""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(".")  # adapt to project root
FONT_DIR = BASE / "assets" / "fonts"
STINGER = BASE / "assets" / "signature_ces_stingered.mp4"
MUSIC = BASE / "assets" / "music" / "afroswing_v2.mp3"
SUNSET_SRC = BASE / "renders" / "sunset_bg.mp4"
OUT = BASE / "output" / "v4_funnel"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 720, 1280
FPS = 30
BUFFER = 0.8

# BRAND PALETTE (adapt from brand_identity.md)
TERRACOTTA = "#A0392B"    # primary
OCHRE = "#B58761"         # secondary
CACAO = "#492E21"         # text on light
CREAM = "#F5E8D3"         # main bg
SAFFRON = "#D88A22"       # highlight
TEAL = "#5BA897"
LOGO = BASE / "assets" / "logo.png"  # PNG with transparency

def font_title(sz):
    """Playfair Display for titles. Uses Variable font (others may be corrupted HTML)."""
    p = FONT_DIR / "PlayfairDisplay-Variable.ttf"
    return ImageFont.truetype(str(p), sz) if p.exists() else ImageFont.load_default()

def font_body(sz, medium=False):
    """Poppins for body text."""
    name = "Poppins-SemiBold.ttf" if medium else "Poppins-Regular.ttf"
    p = FONT_DIR / name
    return ImageFont.truetype(str(p), sz) if p.exists() else ImageFont.load_default()

def font(sz, bold=False):
    """Legacy alias — redirects to Poppins."""
    return font_body(sz, medium=bold)

def run(cmd, label=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ❌ {label}: {r.stderr[-300:]}")
        sys.exit(1)
    return r

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())

def prep_video(tmp, name, src, duration, trim_pos=None):
    """Slow-mo stretch. trim_pos splits a clip at different timestamps."""
    out = tmp / f"seg_{name}.mp4"
    src_dur = dur(src)
    if trim_pos and src_dur > 3.0:
        if trim_pos == "start": ss = 0
        elif trim_pos == "mid": ss = max(0, src_dur / 2 - duration / 2)
        elif trim_pos == "end": ss = max(0, src_dur - duration)
        else: ss = 0
        actual_dur = min(duration, src_dur - ss)
        factor = duration / actual_dur
        run(["ffmpeg", "-y", "-ss", str(ss), "-i", str(src), "-t", f"{actual_dur:.2f}",
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setpts={factor:.4f}*PTS",
             "-r", str(FPS), "-t", str(duration),
             "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(out)], name)
        return out
    if src_dur >= duration:
        run(["ffmpeg", "-y", "-i", str(src), "-t", str(duration),
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
             "-r", str(FPS), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
             "-an", str(out)], name)
    else:
        factor = duration / src_dur
        run(["ffmpeg", "-y", "-i", str(src),
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setpts={factor:.4f}*PTS",
             "-r", str(FPS), "-t", str(duration),
             "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(out)], name)
    return out

def make_sunset(tmp, cta_vo_dur):
    """Ping-pong sunset: forward+reverse+forward for long CTA VOs."""
    sunset_needed = cta_vo_dur + 1.5
    scaled = tmp / "sunset_scaled.mp4"
    run(["ffmpeg", "-y", "-i", str(SUNSET_SRC),
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
         "-r", str(FPS), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(scaled)])
    rev = tmp / "sunset_rev.mp4"
    run(["ffmpeg", "-y", "-i", str(scaled), "-vf", "reverse",
         "-r", str(FPS), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(rev)])
    pp_list = tmp / "sunset_pp.txt"
    with open(pp_list, "w") as f:
        f.write(f"file '{scaled.absolute()}'\nfile '{rev.absolute()}'\nfile '{scaled.absolute()}'\n")
    out = tmp / "seg_sunset.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(pp_list),
         "-t", f"{sunset_needed:.1f}", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(out)])
    return out

def build_video(vid_id, config):
    """Build one video with the funnel structure."""
    tmp = BASE / "renders" / f"{vid_id}_funnel"
    tmp.mkdir(parents=True, exist_ok=True)
    clips_dir = config['clips_dir']
    clips = config['clips']
    vo_data = config['vo']
    hook_lines = config['hook_lines']
    stinger_dur = dur(STINGER)

    # VO generation
    durations = {}
    for name, text in vo_data:
        vo_path = tmp / f"{name}.wav"
        run(["edge-tts", "--voice", "fr-CH-ArianeNeural", "--text", text, "--write-media", str(vo_path)])
        durations[name] = dur(vo_path)

    # Segments
    segs = []
    # Stinger
    stinger_seg = tmp / "seg_stinger.mp4"
    run(["ffmpeg", "-y", "-i", str(STINGER),
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
         "-r", str(FPS), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", str(stinger_seg)])
    segs.append(stinger_seg)
    # Hook card — BRAND COMPLIANT (cream bg, logo, dates, contact, tagline)
    hook_dur = durations["hook_vo"] + 0.5  # hook VO ~8s with context prefix
    hook_img = tmp / "hook_card.png"
    im = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(im)
    # Logo centered top
    if LOGO.exists():
        logo_img = Image.open(str(LOGO)).convert("RGBA")
        lw = 200
        ratio = lw / logo_img.width
        lh = int(logo_img.height * ratio)
        logo_img = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
        im.paste(logo_img, ((W - lw) // 2, 80), logo_img)
    # Title lines (Playfair Display)
    y = 360
    for line in hook_lines:
        sz = 58 if line.get('hl') else 42
        col = TERRACOTTA if line.get('hl') else CACAO
        d.text((W//2, y), line['t'], fill=col, font=font_title(sz), anchor='mt')
        y += 72
    # Dates + lieu
    d.text((W//2, 720), "DU 10 AU 14 AOÛT", fill=TERRACOTTA, font=font_body(28, medium=True), anchor='mt')
    d.text((W//2, 758), "AU PETIT-LANCY", fill=OCHRE, font=font_body(24, medium=True), anchor='mt')
    d.line([(W//2 - 80, 805), (W//2 + 80, 805)], fill=OCHRE, width=2)
    # Contact
    d.text((W//2, 830), "email@association.org", fill=CACAO, font=font_body(22), anchor='mt')
    d.text((W//2, 862), "+41 76 XXX XX XX", fill=CACAO, font=font_body(22), anchor='mt')
    d.text((W//2, 900), "@handle", fill=OCHRE, font=font_body(20, medium=True), anchor='mt')
    # Tagline
    d.text((W//2, H - 90), "TAGLINE", fill=TERRACOTTA, font=font_body(18, medium=True), anchor='mt')
    im.save(str(hook_img), quality=95)
    hook_seg = tmp / "seg_hook.mp4"
    run(["ffmpeg", "-y", "-loop", "1", "-i", str(hook_img), "-t", str(hook_dur),
         "-vf", f"zoompan=z='1.05':d={int(hook_dur*FPS)}:s={W}x{H}:fps={FPS}",
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(hook_seg)])
    segs.append(hook_seg)
    # Build clips
    build_vo_names = [k for k in [v[0] for v in vo_data] if k.startswith("build_")]
    clip_trims = config.get('clip_trims', [None] * len(clips))
    for i, vo_name in enumerate(build_vo_names):
        clip_path = clips_dir / clips[i] if i < len(clips) else clips_dir / clips[-1]
        clip_dur = durations[vo_name] + BUFFER
        trim = clip_trims[i] if i < len(clip_trims) else None
        segs.append(prep_video(tmp, f"b{i}", clip_path, clip_dur, trim_pos=trim))
    # Climax
    climax_dur = durations["climax_vo"] + 1.5
    segs.append(prep_video(tmp, "climax", clips_dir / clips[-1], climax_dur))
    # Sunset
    segs.append(make_sunset(tmp, durations["cta_vo"]))

    # Concat
    concat_list = tmp / "concat.txt"
    with open(concat_list, "w") as f:
        for s in segs: f.write(f"file '{s.absolute()}'\n")
    video = tmp / "video.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(video)])
    video_dur = dur(video)

    # Audio: stinger alone, VO+music delayed by stinger_dur+200ms
    vo_order = ["hook_vo"] + build_vo_names + ["climax_vo", "cta_vo"]
    vo_parts = []
    t = stinger_dur
    d = durations["hook_vo"]; vo_parts.append((tmp / "hook_vo.wav", t, d)); t += d + 0.5
    for vn in build_vo_names:
        d = durations[vn]; vo_parts.append((tmp / f"{vn}.wav", t, d)); t += d + BUFFER
    d = durations["climax_vo"]; vo_parts.append((tmp / "climax_vo.wav", t, d)); t += d + 1.5
    d = durations["cta_vo"]; vo_parts.append((tmp / "cta_vo.wav", t, d))

    inputs = []; filter_parts = []
    for i, (vp, start, _) in enumerate(vo_parts):
        inputs.extend(["-i", str(vp)])
        delay_ms = int(start * 1000)
        filter_parts.append(f"[{i}:a]adelay={delay_ms}|{delay_ms}[d{i}]")
    mix = "".join(f"[d{i}]" for i in range(len(vo_parts)))
    fc = ";".join(filter_parts) + f";{mix}amix=inputs={len(vo_parts)}:duration=longest:normalize=0[vout]"
    vo_padded = tmp / "vo_padded.wav"
    run(["ffmpeg", "-y"] + inputs + ["-filter_complex", fc, "-map", "[vout]", "-c:a", "pcm_s16le", str(vo_padded)])

    stinger_a = tmp / "stinger_a.aac"
    run(["ffmpeg", "-y", "-i", str(STINGER), "-vn", "-c:a", "aac", "-b:a", "128k", str(stinger_a)])
    final_audio = tmp / "final_audio.aac"
    run(["ffmpeg", "-y", "-i", str(stinger_a), "-i", str(vo_padded), "-i", str(MUSIC),
         "-filter_complex",
         f"[0:a]volume=1.0[a_sting];"
         f"[1:a]volume=2.5,adelay=200|200[a_vo];"
         f"[2:a]volume=0.12,atrim=0:{video_dur:.1f},adelay=3700|3700,afade=t=out:st={video_dur-2.0:.1f}:d=2.0[a_mus];"
         f"[a_sting][a_vo][a_mus]amix=inputs=3:duration=longest:normalize=0[aout]",
         "-map", "[aout]", "-c:a", "aac", "-b:a", "128k", "-t", str(video_dur), str(final_audio)])

    # Subtitles
    sub_map = config.get('sub_text', {})
    sub_lines = []
    for name, start, d in vo_parts:
        txt = sub_map.get(name, "")
        if txt:
            h = int(start // 3600); m = int((start % 3600) // 60); s = start % 60
            he = int((start+d) // 3600); me = int(((start+d) % 3600) // 60); se = (start+d) % 60
            start_ts = f"{h}:{m:02d}:{s:05.2f}"
            end_ts = f"{he}:{me:02d}:{se:05.2f}"
            sub_lines.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{txt}")
    subs_file = tmp / "subs.ass"
    with open(subs_file, "w") as f:
        f.write("[Script Info]\nTitle: CES\nScriptType: v4.00+\nPlayResX: 720\nPlayResY: 1280\n\n")
        f.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        f.write("Style: Default,Poppins SemiBold,38,&H00D3E8F5,&H001E1E7A,&H00212E49,&H80000A1A,-1,0,0,0,100,100,0,0,1,3,1,2,60,60,140,1\n\n")
        f.write("[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        for line in sub_lines: f.write(line + "\n")

    # Final
    final = OUT / f"{vid_id}.mp4"
    run(["ffmpeg", "-y", "-i", str(video), "-i", str(final_audio),
         "-map", "0:v", "-map", "1:a", f"-vf", f"subtitles={subs_file}",
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-t", str(video_dur), str(final)])
    # Compress for TG
    tg = Path(f"/tmp/TG_{vid_id}.mp4")
    run(["ffmpeg", "-y", "-i", str(final),
         "-c:v", "libx264", "-crf", "26", "-maxrate", "3200k", "-bufsize", "6400k",
         "-preset", "fast", "-vf", "scale=720:1280",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(tg)])
    print(f"✅ {vid_id}: {dur(final):.1f}s → TG: {tg.stat().st_size/1048576:.1f}MB")
    return tg

# ═══ CONFIG PATTERN ═══
# Each video = dict with clips_dir, clips (filenames), clip_trims (optional),
# hook_lines (list of {t, hl?}), vo (list of (name, text)), sub_text (ASS-formatted)
#
# VIDEOS = {
#     "example": {
#         "clips_dir": Path("assets/clips"),
#         "clips": ["clip1.mp4", "clip2.mp4", "clip3.mp4"],
#         "hook_lines": [{"t": "Et si..."}, {"t": "MOT CLÉ", "hl": True}],
#         "vo": [
#             ("hook_vo", "Question hook?"),
#             ("build_a", "Preuve A."),
#             ("build_b", "Preuve B."),
#             ("build_c", "Preuve C."),
#             ("climax_vo", "Climax émotionnel."),
#             ("cta_vo", "Prix, dates, lieu. CTA."),
#         ],
#         "sub_text": {
#             "hook_vo": r"Question\N hook?",
#             "cta_vo": r"Prix\N Dates\N Lieu",
#         },
#     },
# }
