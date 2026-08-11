#!/usr/bin/env python3
"""Build v3: B-roll vidéo Seedance + caption overlay.

Différences vs v2:
  - Clips vidéo (496x864) au lieu d'images statiques + Ken Burns
  - Scale 496x864 → 1080x1920 (lanczos)
  - Loop si TTS > 5s, trim si TTS < 5s
  - Fallback image statique si pas de clip vidéo (beat 08_legacy)
  - Caption overlay, subs ASS, BGM, watermark, outro inchangés
"""
import json, os, subprocess, sys, math, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path("/home/tars/african-heroes/CHANNEL/video1_nzinga")
BROLL_IMG_DIR = BASE / "broll"          # Images statiques (fallback)
BROLL_VID_DIR = BASE / "broll_video"    # Clips vidéo Seedance
AUDIO_DIR = BASE / "audio"
CLIPS_DIR = BASE / "clips"
TMP_DIR = BASE / "tmp_v3"
CAPTIONS_DIR = BASE / "captions_v3"
for d in [CLIPS_DIR, TMP_DIR, CAPTIONS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

BGM_PATH = Path("/home/tars/crypto-project/audio/bgm_stellardrone.mp3")

# ── Mapping beats → clips vidéo (ou image fallback) ──────────────────────
BEATS_CONFIG = [
    {
        "id": "01_hook",
        "video": "00_nzinga_floor.mp4",
        "image": "02_tapis_scene.png",
        "caption": "1626. Un gouverneur portugais invite\nune reine africaine à négocier.\nIl la fait asseoir par terre.",
        "kicker": "Le défi",
        "fullscreen": False,
    },
    {
        "id": "02_hook_revelation",
        "video": "02_tapis_scene.mp4",
        "image": "02_tapis_scene.png",
        "caption": "Elle fait agenouiller une servante.\nEt s'assoit sur son dos.\nDésormais, elle le regarde d'en haut.",
        "kicker": "La réponse",
        "fullscreen": False,
    },
    {
        "id": "03_identity",
        "video": "01_nzinga_portrait.mp4",
        "image": "01_nzinga_portrait.png",
        "caption": "NZINGA\nReine du Ndongo et du Matamba\n1583 — 1663",
        "kicker": "Son nom",
        "fullscreen": False,
    },
    {
        "id": "04_context",
        "video": "07_nzinga_young_training.mp4",
        "image": "07_nzinga_young_training.png",
        "caption": "Les Portugais voulaient l'or,\nles esclaves et le territoire.\nSon père l'avait formée comme un prince.",
        "kicker": "Le contexte",
        "fullscreen": False,
    },
    {
        "id": "05_strategy",
        "video": "04_imbangala_battle.mp4",
        "image": "04_imbangala_battle.png",
        "caption": "Elle s'allie aux Imbangala —\nles mercenaires des Portugais.\nEt les retourne contre eux.",
        "kicker": "Le coup de génie",
        "fullscreen": False,
    },
    {
        "id": "06_40ans",
        "video": "06_nzinga_horseback.mp4",
        "image": "06_nzinga_horseback.png",
        "caption": "40 ans de guerre d'usure.\nAttaques éclair. Espionnage.\nElle joue les Néerlandais contre les Portugais.",
        "kicker": "La guerre d'usure",
        "fullscreen": False,
    },
    {
        "id": "07_victory",
        "video": "08_nzinga_old_treaty.mp4",
        "image": "08_nzinga_old_treaty.png",
        "caption": "1657. Elle a 74 ans.\nElle signe un traité en position de force.\nElle obtient sa sœur. Et le respect.",
        "kicker": "La victoire",
        "fullscreen": False,
    },
    {
        "id": "08_legacy",
        "video": None,
        "image": "05_statue_luanda.png",
        "caption": "« Tant que Nzinga vivait,\nle Portugal n'a jamais été en sécurité. »\n— Archives portugaises",
        "kicker": "L'héritage",
        "fullscreen": False,
    },
    {
        "id": "09_cta",
        "video": None,
        "caption": "SANKOFA\nRetourne la chercher.",
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
        return -1.0


def fmt_time(s):
    h = int(s // 3600); m = int((s % 3600) // 60)
    sec = int(s % 60); ms = int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


# ── Caption HTML (inchangé vs v2) ────────────────────────────────────────
def make_caption_html(beat, out_html):
    caption_html = beat["caption"].replace("\n", "<br>")
    kicker = beat["kicker"]
    fullscreen = beat["fullscreen"]

    if fullscreen:
        html = f"""<!doctype html><html><head><meta charset='utf-8'>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;position:relative;font-family:'Segoe UI',Helvetica,Arial,sans-serif;
background:radial-gradient(ellipse at 50% 50%,rgba(232,163,61,0.15) 0%,transparent 60%),linear-gradient(160deg,#1A1A1A 0%,#241a10 100%)}}
.wrap{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:80px}}
.kicker{{font-size:28px;letter-spacing:6px;color:#E8A33D;text-transform:uppercase;font-weight:700;margin-bottom:50px}}
.caption{{font-size:64px;color:#F4E8D0;font-weight:900;line-height:1.3;text-shadow:0 0 60px rgba(232,163,61,0.3)}}
.accent{{width:100px;height:4px;background:#B5522E;margin:40px auto}}
.cta-badge{{margin-top:50px;font-size:32px;color:#E8A33D;font-weight:700;padding:20px 50px;border:3px solid #E8A33D;border-radius:50px;background:rgba(232,163,61,0.1)}}
</style></head>
<body><div class='wrap'>
<div class='kicker'>{kicker}</div>
<div class='caption'>{caption_html}</div>
<div class='accent'></div>
<div class='cta-badge'>Abonne-toi</div>
</div></body></html>"""
    else:
        html = f"""<!doctype html><html><head><meta charset='utf-8'>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html{{background:transparent}}
body{{width:1080px;height:1920px;overflow:hidden;position:relative;font-family:'Segoe UI',Helvetica,Arial,sans-serif;background:transparent}}
.desc-bar{{
    position:absolute;top:0;left:0;right:0;
    background:linear-gradient(to bottom, rgba(26,26,26,0.97) 0%, rgba(26,26,26,0.92) 55%, rgba(26,26,26,0) 100%);
    padding:70px 60px 100px 60px;min-height:520px;
    display:flex;flex-direction:column;justify-content:flex-start;
}}
.kicker{{font-size:24px;letter-spacing:4px;color:#E8A33D;text-transform:uppercase;font-weight:700;margin-bottom:20px}}
.caption{{font-size:44px;color:#F4E8D0;font-weight:700;line-height:1.35;text-shadow:0 2px 20px rgba(0,0,0,0.8)}}
.accent{{width:80px;height:4px;background:#B5522E;margin:20px 0}}
</style></head>
<body>
<div class='desc-bar'>
<div class='kicker'>{kicker}</div>
<div class='accent'></div>
<div class='caption'>{caption_html}</div>
</div></body></html>"""

    out_html.write_text(html)


def capture_caption(beat, out_png):
    html_path = CAPTIONS_DIR / f"cap_{beat['id']}.html"
    make_caption_html(beat, html_path)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(500)
        if beat["fullscreen"]:
            page.screenshot(path=str(out_png), full_page=False)
        else:
            page.screenshot(path=str(out_png), full_page=False, omit_background=True)
        browser.close()


# ── NOUVEAU: Build segment from VIDEO clip ────────────────────────────────
def build_video_segment(video_path, dur, out_path):
    """Scale 496x864 → 1080x1920, play once then freeze last frame with slow zoom."""
    clip_dur = get_dur(str(video_path))
    if clip_dur <= 0:
        raise RuntimeError(f"invalid clip duration: {clip_dur}")

    if dur <= clip_dur + 0.3:
        # Trim: take first N seconds
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-t", f"{dur:.3f}",
            "-vf", "scale=1080:1920:flags=lanczos,format=yuv420p",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
            "-an", "-r", "24",
            str(out_path)
        ]
    else:
        # Play once, then freeze last frame with slow zoom for the remainder
        freeze_dur = dur - clip_dur
        # tpad clones last frame, zoompan adds slow zoom on frozen portion
        vf = (
            f"scale=1080:1920:flags=lanczos,"
            f"tpad=stop_mode=clone:stop_duration={freeze_dur:.3f},"
            f"format=yuv420p"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
            "-an", "-r", "24",
            "-t", f"{dur:.3f}",
            str(out_path)
        ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"      ERR video seg: {r.stderr[-400:]}")
        raise RuntimeError("video segment failed")


def build_image_segment(img_path, dur, out_path, beat_idx):
    """Fallback: image statique + Ken Burns (hérité de v2)."""
    zoom_factor = 0.08
    direction = 1 if beat_idx % 2 == 0 else -1
    if direction > 0:
        vf = (f"scale=1188:-2,crop=1080:1920:x='(in_w-1080)/2*(1-{zoom_factor}*t/{dur})'"
              f":y='(in_h-1920)/2',format=yuv420p")
    else:
        vf = (f"scale=1188:-2,crop=1080:1920:x='(in_w-1080)/2*({zoom_factor}*t/{dur})'"
              f":y='(in_h-1920)/2',format=yuv420p")

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
        "-i", str(img_path), "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        vf_simple = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p"
        cmd2 = [
            "ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
            "-i", str(img_path), "-vf", vf_simple,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
        ]
        r2 = subprocess.run(cmd2, capture_output=True, text=True)
        if r2.returncode != 0:
            raise RuntimeError(f"image seg failed: {r2.stderr[-300:]}")


def build_fullscreen_segment(caption_png, dur, out_path):
    vf = "scale=1080:1920,format=yuv420p"
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
        "-i", str(caption_png), "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"fullscreen seg failed: {r.stderr[-300:]}")


def overlay_caption(broll_video, caption_png, dur, out_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(broll_video),
        "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
        "-i", str(caption_png),
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"      overlay ERR: {r.stderr[-400:]}")
        raise RuntimeError("caption overlay failed")


# ── Sous-titres (inchangé) ───────────────────────────────────────────────
def generate_srt(beats_audio, out_path, time_offset=0.0):
    entries = []
    idx = 1
    cumulative = 0.0
    for beat in beats_audio:
        words = beat["text"].split()
        chunk_size = 4
        chunks = [" ".join(words[j:j+chunk_size]) for j in range(0, len(words), chunk_size)]
        total_chars = sum(len(c) for c in chunks)
        offset = cumulative + time_offset
        for chunk in chunks:
            chunk_dur = beat["duration"] * (len(chunk) / max(total_chars, 1))
            entries.append((idx, offset, offset + chunk_dur, chunk))
            offset += chunk_dur
            idx += 1
        cumulative += beat["duration"]
    with open(out_path, "w") as f:
        for idx, start, end, text in entries:
            f.write(f"{idx}\n{fmt_time(start)} --> {fmt_time(end)}\n{text}\n\n")
    return len(entries)


def srt_to_ass(srt_path, ass_path):
    subprocess.run(["ffmpeg", "-y", "-i", srt_path, ass_path],
                   capture_output=True, text=True, check=True)
    with open(ass_path) as f:
        lines = f.readlines()
    events = []
    in_events = False
    for line in lines:
        if line.strip().startswith("[Events]"):
            in_events = True
        if in_events:
            events.append(line)
    header = """[Script Info]
Title: Sankofa Subs
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
        for line in events:
            f.write(line)


# ── MAIN ─────────────────────────────────────────────────────────────────
def main():
    script = json.loads((AUDIO_DIR / "durations.json").read_text())
    dur_map = {b["id"]: b["duration"] for b in script}
    text_map = {b["id"]: b["text"] for b in script}

    # 1. Captions
    print("\n[1/5] Génération captions (Playwright)...")
    for beat in BEATS_CONFIG:
        cap_png = CAPTIONS_DIR / f"cap_{beat['id']}.png"
        if not cap_png.exists():
            capture_caption(beat, cap_png)
            print(f"    📝 {beat['id']}")
        else:
            print(f"    (cached) {beat['id']}")

    # 2. Build segments
    print("\n[2/5] Build segments (vidéo Seedance / fallback image)...")
    seg_paths = []
    for i, beat in enumerate(BEATS_CONFIG):
        bid = beat["id"]
        dur = dur_map[bid]
        cap_png = CAPTIONS_DIR / f"cap_{bid}.png"

        if beat["fullscreen"]:
            seg = TMP_DIR / f"seg_{i:02d}.mp4"
            build_fullscreen_segment(cap_png, dur, seg)
            print(f"    [seg {i}] {bid} (fullscreen text)")
            seg_paths.append(seg)
            continue

        video_name = beat.get("video")
        video_path = BROLL_VID_DIR / video_name if video_name else None

        seg = TMP_DIR / f"seg_{i:02d}.mp4"
        if seg.exists() and get_dur(str(seg)) >= dur - 0.2:
            print(f"    [seg {i}] {bid} (cached)")
            seg_paths.append(seg)
            continue

        if video_path and video_path.exists():
            # ── VIDEO CLIP (v3) ──
            base_video = TMP_DIR / f"broll_{i:02d}.mp4"
            if not base_video.exists():
                build_video_segment(video_path, dur, base_video)
            seg = TMP_DIR / f"seg_{i:02d}.mp4"
            overlay_caption(base_video, cap_png, dur, seg)
            seg_paths.append(seg)
            action = "freeze" if dur > 5.5 else "trim"
            print(f"    [seg {i}] {bid} 🎬 {video_name} ({action}, {dur:.1f}s)")
        else:
            # ── FALLBACK IMAGE ──
            img_name = beat.get("image")
            img_path = BROLL_IMG_DIR / img_name if img_name else None
            if img_path and img_path.exists():
                base_video = TMP_DIR / f"broll_{i:02d}.mp4"
                build_image_segment(img_path, dur, base_video, i)
                seg = TMP_DIR / f"seg_{i:02d}.mp4"
                overlay_caption(base_video, cap_png, dur, seg)
                seg_paths.append(seg)
                print(f"    [seg {i}] {bid} 🖼️ {img_name} (Ken Burns, {dur:.1f}s)")
            else:
                seg = TMP_DIR / f"seg_{i:02d}.mp4"
                build_fullscreen_segment(cap_png, dur, seg)
                seg_paths.append(seg)
                print(f"    [seg {i}] {bid} ⚠️ fallback caption seule")

    # 3. Concat
    print("\n[3/5] Concaténation segments...")
    concat_list = TMP_DIR / "concat.txt"
    with open(concat_list, "w") as f:
        for p in seg_paths:
            f.write(f"file '{p.resolve()}'\n")
    video_concat = TMP_DIR / "video.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", str(video_concat)
    ], capture_output=True, text=True, check=True)

    # 4. Audio
    print("\n[4/5] Audio + sous-titres + BGM...")
    audio_concat = TMP_DIR / "audio_concat.txt"
    with open(audio_concat, "w") as f:
        for beat in BEATS_CONFIG:
            bid = beat["id"]
            audio_path = AUDIO_DIR / f"{bid}.mp3"
            f.write(f"file '{audio_path.resolve()}'\n")
    audio_full = TMP_DIR / "audio_full.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(audio_concat),
        "-c:a", "libmp3lame", "-b:a", "192k", str(audio_full)
    ], capture_output=True, text=True, check=True)

    video_audio = TMP_DIR / "video_audio.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(video_concat), "-i", str(audio_full),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-r", "24", "-shortest", str(video_audio)
    ], capture_output=True, text=True, check=True)

    # 5. Subs + BGM + Watermark (final pass)
    watermark_path = Path("/home/tars/african-heroes/CHANNEL/branding/watermark_sankofa.png")
    outro_path = Path("/home/tars/african-heroes/CHANNEL/branding/outro_sankofa.mp4")

    srt_path = TMP_DIR / "subs.srt"
    srt_data = []
    for beat in BEATS_CONFIG:
        bid = beat["id"]
        srt_data.append({"id": bid, "text": text_map[bid], "duration": dur_map[bid]})
    generate_srt(srt_data, str(srt_path))
    ass_path = TMP_DIR / "subs.ass"
    srt_to_ass(str(srt_path), str(ass_path))

    dur_total = get_dur(str(video_audio))
    ass_escaped = str(ass_path).replace("/", "\\/").replace(":", "\\:")
    out_path = CLIPS_DIR / "nzinga_v3_noloop.mp4"

    if BGM_PATH.exists():
        cmd = [
            "ffmpeg", "-y", "-i", str(video_audio), "-i", str(BGM_PATH),
            "-i", str(watermark_path),
            "-filter_complex",
            f"[0:v][2:v]overlay=x=W-w-20:y=H-h-20,subtitles='{ass_escaped}'[vout];"
            f"[1:a]volume=-28dB,afade=t=in:st=0:d=1,afade=t=out:st={dur_total-2}:d=2[bgm];"
            f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-shortest",
            "-pix_fmt", "yuv420p", "-r", "24",
            str(out_path)
        ]
    else:
        cmd = [
            "ffmpeg", "-y", "-i", str(video_audio),
            "-i", str(watermark_path),
            "-filter_complex",
            f"[0:v][1:v]overlay=x=W-w-20:y=H-h-20,subtitles='{ass_escaped}'[vout]",
            "-map", "[vout]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-r", "24",
            str(out_path)
        ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR: {r.stderr[-800:]}")
        raise RuntimeError("final assembly failed")

    # 6. Outro
    if outro_path.exists():
        print("\nPostpend outro Sankofa…")
        final_path = CLIPS_DIR / "nzinga_v3_final.mp4"
        r = subprocess.run([
            "ffmpeg", "-y",
            "-i", str(out_path),
            "-i", str(outro_path),
            "-filter_complex",
            "[0:v]fps=24,setsar=1[mainv];"
            "[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=24[outrov];"
            "[mainv][0:a][outrov][1:a]concat=n=2:v=1:a=1[vout][aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-r", "24",
            str(final_path)
        ], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  WARN: outro concat failed: {r.stderr[-400:]}")
        else:
            print(f"  ✅ Outro ajouté")
            shutil.move(str(final_path), str(out_path))

    size_mb = os.path.getsize(out_path) / (1024*1024)
    final_dur = get_dur(str(out_path))
    print(f"\n✅ VIDÉO FINALE: {out_path}")
    print(f"   Durée: {final_dur:.1f}s | Taille: {size_mb:.1f} MB")
    return out_path


if __name__ == "__main__":
    main()
