#!/usr/bin/env python3
"""Build v3 template: Vidéo B-roll IA + caption overlay.

Template pour projets narratifs 9:16 (Sankofa/african-heroes, biographies).
Remplace les images statiques + Ken Burns par des clips vidéo IA (Seedance, Veo).

Réutilise l'architecture Variante D (2 couches) avec :
- B-roll = clip vidéo au lieu d'image statique
- Caption en HAUT (gradient sombre top→mid, pas bottom)
- Subs ASS en BAS (MarginV=120)

Usage :
  1. Définir BEATS_CONFIG (mapping beat → clip vidéo ou image fallback)
  2. Générer les clips vidéo via templates/gen_videos_batch.py (kie.ai)
  3. Générer le TTS (edge-tts) → audio/ avec durations.json
  4. Lancer : python3 build_v3.py (en background, ~5-10 min sur CPU lent)

Voir references/video-broll-assembly-recipe.md pour les détails techniques.
"""
import json, os, subprocess, sys, math, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

# ── CONFIGURATION — éditer ces paths ──────────────────────────────────────
BASE = Path("/home/tars/african-heroes/CHANNEL/video1_nzinga")
BROLL_IMG_DIR = BASE / "broll"          # Images statiques (fallback)
BROLL_VID_DIR = BASE / "broll_video"    # Clips vidéo IA (Seedance/Veo)
AUDIO_DIR = BASE / "audio"
CLIPS_DIR = BASE / "clips"
TMP_DIR = BASE / "tmp_v3"
CAPTIONS_DIR = BASE / "captions_v3"
for d in [CLIPS_DIR, TMP_DIR, CAPTIONS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

BGM_PATH = Path("/home/tars/crypto-project/audio/bgm_stellardrone.mp3")
WATERMARK = Path("/home/tars/african-heroes/CHANNEL/branding/watermark_sankofa.png")
OUTRO = Path("/home/tars/african-heroes/CHANNEL/branding/outro_sankofa.mp4")

# ── BEATS — éditer pour chaque vidéo ──────────────────────────────────────
BEATS_CONFIG = [
    {
        "id": "01_hook",
        "video": "clip_name.mp4",         # dans BROLL_VID_DIR
        "caption": "Caption text here.",
        "kicker": "KICKER",
        "fullscreen": False,
    },
    # ... plus de beats ...
    {
        "id": "08_fallback",
        "video": None,                    # pas de clip → image statique
        "image": "fallback.png",          # dans BROLL_IMG_DIR
        "caption": "...",
        "kicker": "Fallback",
        "fullscreen": False,
    },
    {
        "id": "09_cta",
        "video": None,
        "caption": "CHANNEL NAME\nTagline.",
        "kicker": "Abonne-toi",
        "fullscreen": True,
    },
]


def get_dur(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except (ValueError, AttributeError):
        return -1.0   # sentinel: file corrupt or missing (moov atom not found)


def fmt_time(s):
    h = int(s // 3600); m = int((s % 3600) // 60)
    sec = int(s % 60); ms = int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


# ── Caption HTML ──────────────────────────────────────────────────────────
def make_caption_html(beat, out_html):
    caption = beat["caption"].replace("\n", "<br>")
    kicker = beat["kicker"]
    if beat["fullscreen"]:
        out_html.write_text(f"""<!doctype html><html><head><meta charset='utf-8'>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;font-family:'Segoe UI',sans-serif;
background:linear-gradient(160deg,#1A1A1A 0%,#241a10 100%)}}
.wrap{{position:absolute;inset:0;display:flex;flex-direction:column;
justify-content:center;align-items:center;text-align:center;padding:80px}}
.kicker{{font-size:28px;letter-spacing:6px;color:#E8A33D;text-transform:uppercase;
font-weight:700;margin-bottom:50px}}
.caption{{font-size:64px;color:#F4E8D0;font-weight:900;line-height:1.3}}
.accent{{width:100px;height:4px;background:#B5522E;margin:40px auto}}
</style></head><body><div class='wrap'>
<div class='kicker'>{kicker}</div>
<div class='caption'>{caption}</div>
<div class='accent'></div>
</div></body></html>""")
    else:
        out_html.write_text(f"""<!doctype html><html><head><meta charset='utf-8'>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html{{background:transparent}}
body{{width:1080px;height:1920px;background:transparent;font-family:'Segoe UI',sans-serif}}
.desc-bar{{position:absolute;top:0;left:0;right:0;
background:linear-gradient(to bottom,rgba(26,26,26,0.97) 0%,rgba(26,26,26,0.92) 55%,rgba(26,26,26,0) 100%);
padding:70px 60px 100px 60px;min-height:520px}}
.kicker{{font-size:24px;letter-spacing:4px;color:#E8A33D;text-transform:uppercase;font-weight:700;margin-bottom:20px}}
.caption{{font-size:44px;color:#F4E8D0;font-weight:700;line-height:1.35}}
.accent{{width:80px;height:4px;background:#B5522E;margin:20px 0}}
</style></head><body>
<div class='desc-bar'><div class='kicker'>{kicker}</div><div class='accent'></div>
<div class='caption'>{caption}</div></div></body></html>""")


def capture_caption(beat, out_png):
    html_path = CAPTIONS_DIR / f"cap_{beat['id']}.html"
    make_caption_html(beat, html_path)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(500)
        page.screenshot(path=str(out_png), omit_background=not beat["fullscreen"])
        browser.close()


# ── Video segment (v3 core) ───────────────────────────────────────────────
def build_video_segment(video_path, dur, out_path):
    """Scale 496x864 → 1080x1920, freeze frame (NOT loop), ultrafast."""
    clip_dur = get_dur(str(video_path))
    if clip_dur <= 0:
        raise RuntimeError(f"invalid clip duration: {clip_dur}")
    if dur <= clip_dur + 0.3:
        cmd = ["ffmpeg", "-y", "-i", str(video_path), "-t", f"{dur:.3f}",
               "-vf", "scale=1080:1920:flags=lanczos,format=yuv420p",
               "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
               "-an", "-r", "24", str(out_path)]
    else:
        freeze_dur = dur - clip_dur
        vf = (f"scale=1080:1920:flags=lanczos,"
              f"tpad=stop_mode=clone:stop_duration={freeze_dur:.3f},"
              f"format=yuv420p")
        cmd = ["ffmpeg", "-y", "-i", str(video_path), "-vf", vf,
               "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
               "-an", "-r", "24", "-t", f"{dur:.3f}", str(out_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"video seg failed: {r.stderr[-400:]}")


def build_image_segment(img_path, dur, out_path, beat_idx):
    """Fallback: image statique + Ken Burns."""
    zoom = 0.08
    d = 1 if beat_idx % 2 == 0 else -1
    vf = (f"scale=1188:-2,crop=1080:1920:x='(in_w-1080)/2*(1-{zoom}*t/{dur})'"
          f":y='(in_h-1920)/2',format=yuv420p" if d > 0 else
          f"scale=1188:-2,crop=1080:1920:x='(in_w-1080)/2*({zoom}*t/{dur})'"
          f":y='(in_h-1920)/2',format=yuv420p")
    cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
           "-i", str(img_path), "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast",
           "-crf", "18", "-pix_fmt", "yuv420p", "-r", "24", str(out_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        cmd2 = ["ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
                "-i", str(img_path), "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-r", "24", str(out_path)]
        subprocess.run(cmd2, capture_output=True, text=True, check=True)


def overlay_caption(broll_video, caption_png, dur, out_path):
    cmd = ["ffmpeg", "-y", "-i", str(broll_video),
           "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
           "-i", str(caption_png),
           "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
           "-map", "[v]", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", "24", str(out_path)]
    subprocess.run(cmd, capture_output=True, text=True, check=True)


def build_fullscreen_segment(caption_png, dur, out_path):
    cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
           "-i", str(caption_png), "-vf", "scale=1080:1920,format=yuv420p",
           "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-r", "24", str(out_path)]
    subprocess.run(cmd, capture_output=True, text=True, check=True)


# ── Subtitles ─────────────────────────────────────────────────────────────
def generate_srt(beats_audio, out_path, time_offset=0.0):
    entries, idx, cumul = [], 1, 0.0
    for beat in beats_audio:
        words = beat["text"].split()
        chunks = [" ".join(words[j:j+4]) for j in range(0, len(words), 4)]
        total = sum(len(c) for c in chunks)
        off = cumul + time_offset
        for c in chunks:
            d = beat["duration"] * (len(c) / max(total, 1))
            entries.append((idx, off, off + d, c))
            off += d; idx += 1
        cumul += beat["duration"]
    with open(out_path, "w") as f:
        for i, s, e, t in entries:
            f.write(f"{i}\n{fmt_time(s)} --> {fmt_time(e)}\n{t}\n\n")


def srt_to_ass(srt_path, ass_path):
    subprocess.run(["ffmpeg", "-y", "-i", srt_path, ass_path],
                   capture_output=True, text=True, check=True)
    with open(ass_path) as f: lines = f.readlines()
    events, in_ev = [], False
    for l in lines:
        if l.strip().startswith("[Events]"): in_ev = True
        if in_ev: events.append(l)
    header = """[Script Info]
Title: Subs
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,42,&H00F4E8D0,&H000000FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,4,1,2,80,80,120,1

"""
    with open(ass_path, "w") as f:
        f.write(header)
        for l in events: f.write(l)


# ── MAIN ──────────────────────────────────────────────────────────────────
def main():
    script = json.loads((AUDIO_DIR / "durations.json").read_text())
    dur_map = {b["id"]: b["duration"] for b in script}
    text_map = {b["id"]: b["text"] for b in script}

    # 1. Captions
    print("\n[1/5] Captions...")
    for beat in BEATS_CONFIG:
        cap_png = CAPTIONS_DIR / f"cap_{beat['id']}.png"
        if not cap_png.exists():
            capture_caption(beat, cap_png)
            print(f"    📝 {beat['id']}")

    # 2. Segments
    print("\n[2/5] Segments...")
    seg_paths = []
    for i, beat in enumerate(BEATS_CONFIG):
        bid = beat["id"]; dur = dur_map[bid]
        cap_png = CAPTIONS_DIR / f"cap_{bid}.png"
        seg = TMP_DIR / f"seg_{i:02d}.mp4"

        # Cache check — defensive against corrupt MP4 (get_dur returns -1.0)
        if seg.exists():
            if get_dur(str(seg)) >= dur - 0.2:
                print(f"    [seg {i}] (cached)")
                seg_paths.append(seg); continue
            else:
                seg.unlink()  # corrupt/incomplete — delete and rebuild

        if beat["fullscreen"]:
            build_fullscreen_segment(cap_png, dur, seg)
        elif beat.get("video") and (BROLL_VID_DIR / beat["video"]).exists():
            base = TMP_DIR / f"broll_{i:02d}.mp4"
            if not base.exists(): build_video_segment(BROLL_VID_DIR / beat["video"], dur, base)
            overlay_caption(base, cap_png, dur, seg)
            print(f"    [seg {i}] 🎬 {beat['video']}")
        elif beat.get("image") and (BROLL_IMG_DIR / beat["image"]).exists():
            base = TMP_DIR / f"broll_{i:02d}.mp4"
            if not base.exists(): build_image_segment(BROLL_IMG_DIR / beat["image"], dur, base, i)
            overlay_caption(base, cap_png, dur, seg)
            print(f"    [seg {i}] 🖼️ {beat['image']}")
        else:
            build_fullscreen_segment(cap_png, dur, seg)
            print(f"    [seg {i}] ⚠️ caption only")
        seg_paths.append(seg)

    # 3. Concat
    print("\n[3/5] Concat...")
    concat_list = TMP_DIR / "concat.txt"
    with open(concat_list, "w") as f:
        for p in seg_paths: f.write(f"file '{p.resolve()}'\n")
    video_concat = TMP_DIR / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
                    "-c", "copy", str(video_concat)], capture_output=True, text=True, check=True)

    # 4. Audio
    print("\n[4/5] Audio...")
    audio_concat = TMP_DIR / "audio_concat.txt"
    with open(audio_concat, "w") as f:
        for beat in BEATS_CONFIG:
            f.write(f"file '{(AUDIO_DIR / f\"{beat['id']}.mp3\").resolve()}'\n")
    audio_full = TMP_DIR / "audio_full.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(audio_concat),
                    "-c:a", "libmp3lame", "-b:a", "192k", str(audio_full)],
                   capture_output=True, text=True, check=True)
    video_audio = TMP_DIR / "video_audio.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(video_concat), "-i", str(audio_full),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-pix_fmt", "yuv420p", "-r", "24", "-shortest", str(video_audio)],
                   capture_output=True, text=True, check=True)

    # 5. Final (subs + BGM + watermark)
    print("\n[5/5] Final assembly...")
    srt_data = [{"id": b["id"], "text": text_map[b["id"]], "duration": dur_map[b["id"]]}
                for b in BEATS_CONFIG]
    generate_srt(srt_data, str(TMP_DIR / "subs.srt"))
    srt_to_ass(str(TMP_DIR / "subs.srt"), str(TMP_DIR / "subs.ass"))

    dur_total = get_dur(str(video_audio))
    ass_esc = str(TMP_DIR / "subs.ass").replace("/", "\\/").replace(":", "\\:")
    out_path = CLIPS_DIR / "video_v3.mp4"

    cmd = ["ffmpeg", "-y", "-i", str(video_audio), "-i", str(BGM_PATH), "-i", str(WATERMARK),
           "-filter_complex",
           f"[0:v][2:v]overlay=x=W-w-20:y=H-h-20,subtitles='{ass_esc}'[vout];"
           f"[1:a]volume=-28dB,afade=t=in:st=0:d=1,afade=t=out:st={dur_total-2}:d=2[bgm];"
           f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]",
           "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-pix_fmt", "yuv420p", "-r", "24", str(out_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(f"final: {r.stderr[-800:]}")

    # 6. Outro
    if OUTRO.exists():
        final_path = CLIPS_DIR / "video_v3_final.mp4"
        subprocess.run(["ffmpeg", "-y", "-i", str(out_path), "-i", str(OUTRO),
                        "-filter_complex",
                        "[0:v]fps=24,setsar=1[mainv];"
                        "[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
                        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=24[outrov];"
                        "[mainv][0:a][outrov][1:a]concat=n=2:v=1:a=1[vout][aout]",
                        "-map", "[vout]", "-map", "[aout]",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                        "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-r", "24",
                        str(final_path)], capture_output=True, text=True)
        shutil.move(str(final_path), str(out_path))

    print(f"\n✅ {out_path} | {get_dur(str(out_path)):.1f}s | {os.path.getsize(out_path)/1e6:.1f}MB")


if __name__ == "__main__":
    main()
