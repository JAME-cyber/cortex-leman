#!/usr/bin/env python3
"""
Template: Shorts Video Assembly (9:16 multi-segment)
Pipeline: VO generation → timeline calc → video stretch → title card → concat → amix → subs → final

Usage:
  1. Define SEGMENTS (video source + VO text) below
  2. Define TITLE_CARD and CTA text
  3. Run: python3 build_shorts.py

Adapt paths, VO text, and video sources to your project.
Tested with: Zankofa T1 (~/culture-en-saveur/), 36.2s output, 1080x1920.
"""
import subprocess
import json
import sys
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import urllib.request

# ════════════════════════════════════════════════════════════════════
# CONFIGURATION — Adapt these for your project
# ════════════════════════════════════════════════════════════════════

BASE = Path(__file__).parent.parent
TMP = BASE / "tmp_build"
OUT = BASE / "output" / "short_final.mp4"
W, H = 1080, 1920

# Voice (verify with: edge-tts --list-voices | grep "^fr-")
VOICE = "fr-FR-DeniseNeural"  # fr-CH-HenriNeural REMOVED July 2026

# Video clips: (source_video, vo_text)
SEGMENTS = [
    # (video_path, vo_text)
    ("assets/clips/clip_1.mp4", "Premier segment de narration."),
    ("assets/clips/clip_2.mp4", "Deuxième segment de narration."),
    ("assets/clips/clip_3.mp4", "Troisième segment de narration."),
]

# Intro segment (logo/stinger)
INTRO_VIDEO = "assets/intro.mp4"
INTRO_DURATION = 3.0  # seconds

# Title card
TITLE_TEXT_MAIN = "TITRE PRINCIPAL"
TITLE_TEXT_SUB = "Sous-titre"
TITLE_DURATION = 4.5  # seconds, will be adjusted to VO duration

# Title VO (plays over title card)
TITLE_VO = "Texte de narration pour le title card."

# CTA
CTA_VO = "Texte de narration pour le CTA. Contact et appel à l'action."
CTA_TEXT = "Appelez maintenant\n06 12 34 56 78"
CTA_DURATION = 10.0

# Flags (optional): download from flagcdn.com
FLAGS = [
    ("eg", "ÉGYPTE"),
    ("cm", "CAMEROUN"),
    ("so", "SOMALIE"),
]

# Background photo for title card (optional)
TITLE_BG_PHOTO = None  # path to photo, or None for gradient

# Music
MUSIC_PATH = "assets/music.mp3"
MUSIC_VOLUME = 0.35  # 35% background

# Stinger
STINGER_PATH = "assets/stinger.mp3"

# Subtitle font
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ════════════════════════════════════════════════════════════════════
# END CONFIGURATION
# ════════════════════════════════════════════════════════════════════


def run(cmd, check=True):
    """Run command, return CompletedProcess."""
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"  ❌ Error: {r.stderr[:300]}")
    return r


def get_duration(path):
    """Get media duration in seconds."""
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True
    )
    return float(json.loads(r.stdout)["format"]["duration"])


def gen_vo(text, output_path, voice=VOICE):
    """Generate TTS with edge-tts (--write-media, NOT --write-audio)."""
    r = subprocess.run([
        "edge-tts", "--voice", voice,
        "--text", text,
        "--write-media", str(output_path),
    ], capture_output=True)
    if r.returncode != 0:
        print(f"  ❌ edge-tts failed: {r.stderr.decode()[:200]}")
        return None
    return output_path


def stretch_video(src, target_dur, out):
    """Stretch/compress video to match target duration using setpts."""
    src_dur = get_duration(src)
    factor = target_dur / src_dur
    run([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", f"setpts={factor:.4f}*PTS,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
        "-t", f"{target_dur:.2f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "24", "-an",
        str(out)
    ])


def make_still(image_path, duration, out):
    """Create video segment from still image."""
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(image_path),
        "-t", f"{duration:.2f}",
        "-vf", f"scale={W}:{H}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "24", "-an",
        str(out)
    ])


def download_flags():
    """Download official flags from flagcdn.com (NEVER draw in PIL)."""
    flags_dir = BASE / "assets" / "flags"
    flags_dir.mkdir(parents=True, exist_ok=True)
    for code, _ in FLAGS:
        path = flags_dir / f"{code}.png"
        if not path.exists():
            url = f"https://flagcdn.com/w640/{code}.png"
            urllib.request.urlretrieve(url, path)
            print(f"  ✅ Flag {code}: {path}")
    return flags_dir


def make_title_card(out_path, flags_dir, bg_photo=None):
    """Generate title card image with flags."""
    img = Image.new('RGB', (W, H), '#2d1500')

    if bg_photo:
        bg = Image.open(bg_photo).convert("RGB")
        bg_ratio = bg.width / bg.height
        target_ratio = W / H
        if bg_ratio > target_ratio:
            new_h = bg.height
            new_w = int(new_h * target_ratio)
            left = (bg.width - new_w) // 2
            bg = bg.crop((left, 0, left + new_w, new_h))
        else:
            new_w = bg.width
            new_h = int(new_w / target_ratio)
            top = (bg.height - new_h) // 2
            bg = bg.crop((0, top, new_w, top + new_h))
        bg = bg.resize((W, H), Image.LANCZOS)
        overlay = Image.new('RGB', (W, H), (20, 8, 0))
        img = Image.blend(bg, overlay, 0.30)  # 30% — 55% is too dark (building invisible)
    else:
        for y in range(H):
            r = int(45 + (y/H) * 30)
            g = int(21 + (y/H) * 15)
            b = int(0 + (y/H) * 10)
            for x in range(W):
                img.putpixel((x,y), (r,g,b))

    draw = ImageDraw.Draw(img)
    font_huge = ImageFont.truetype(FONT_PATH, 80)
    font_med = ImageFont.truetype(FONT_PATH, 48)
    font_small = ImageFont.truetype(FONT_PATH, 36)

    # Title
    parts = TITLE_TEXT_MAIN.split("\n")
    y = 550
    for part in parts:
        draw.text((W//2, y), part, fill='#FFD700', font=font_huge, anchor='mm')
        y += 90
    draw.line([(200, y+30), (880, y+30)], fill='#FF8C00', width=3)
    draw.text((W//2, y+100), TITLE_TEXT_SUB, fill='#FFFFFF', font=font_med, anchor='mm')

    # Flags (spacing 120px to prevent overlap)
    if FLAGS:
        flag_w, flag_h = 180, 120
        spacing = 120
        total_w = len(FLAGS) * flag_w + (len(FLAGS) - 1) * spacing
        start_x = (W - total_w) // 2

        for i, (code, label) in enumerate(FLAGS):
            flag = Image.open(flags_dir / f"{code}.png").convert("RGB")
            flag = flag.resize((flag_w, flag_h), Image.LANCZOS)
            fx = start_x + i * (flag_w + spacing)
            fy = 950
            img.paste(flag, (fx, fy))
            draw.text((fx + flag_w//2, fy + flag_h + 35), label,
                      fill='#FF8C00', font=font_small, anchor='mm')

    img.save(str(out_path), quality=92)
    print(f"  ✅ Title card: {out_path}")


def make_cta(out_path):
    """Generate CTA frame."""
    img = Image.new('RGB', (W, H), '#1a0a00')
    draw = ImageDraw.Draw(img)
    font_huge = ImageFont.truetype(FONT_PATH, 72)
    font_med = ImageFont.truetype(FONT_PATH, 48)

    lines = CTA_TEXT.split("\n")
    y = H // 2 - 100
    for line in lines:
        draw.text((W//2, y), line, fill='#FFD700', font=font_huge, anchor='mm')
        y += 90

    img.save(str(out_path), quality=92)
    print(f"  ✅ CTA frame: {out_path}")


def make_subtitles(vo_files, vo_delays, out_path):
    """Generate ASS subtitles from VO files."""
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {W}",
        f"PlayResY: {H}",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV",
        f"Style: Default,DejaVu Sans,48,&H00FFFFFF,&H00000000,&H80000000,-1,0,3,1,2,50,50,120",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, Text",
    ]

    # Build timeline
    names = ["title"] + [f"seg{i}" for i in range(len(SEGMENTS))] + ["cta"]
    texts = [TITLE_VO] + [s[1] for s in SEGMENTS] + [CTA_VO]

    t = 0.0
    for i, (name, text) in enumerate(zip(names, texts)):
        dur = get_duration(vo_files[i])
        start = t + vo_delays[i]
        end = start + dur
        # Format timestamps
        def fmt(s):
            m = int(s // 60)
            sec = s % 60
            return f"{m}:{sec:05.1f}"
        lines.append(f"Dialogue: 0,{fmt(start)},{fmt(end)},Default,,{text}")
        t = end

    with open(out_path, 'w') as f:
        f.write("\n".join(lines))
    print(f"  ✅ Subtitles: {out_path}")


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    (BASE / "output").mkdir(parents=True, exist_ok=True)

    # 1. Generate VO
    print("=== VO Generation ===")
    vo_files = []
    vo_texts = [TITLE_VO] + [s[1] for s in SEGMENTS] + [CTA_VO]
    for i, text in enumerate(vo_texts):
        vo_path = TMP / f"vo_{i:02d}.mp3"
        gen_vo(text, vo_path)
        dur = get_duration(vo_path)
        print(f"  vo_{i:02d}: {dur:.2f}s")
        vo_files.append(vo_path)

    # 2. Timeline
    print("\n=== Timeline ===")
    vo_durs = [get_duration(f) for f in vo_files]
    segments = [
        ("intro", INTRO_DURATION),
        ("title", max(TITLE_DURATION, vo_durs[0] + 0.5)),
    ]
    for i in range(len(SEGMENTS)):
        segments.append((f"seg{i+1}", vo_durs[i+1] + 0.5))
    segments.append(("cta", max(CTA_DURATION, vo_durs[-1] + 0.8)))

    total = sum(s[1] for s in segments)
    for name, dur in segments:
        print(f"  {name}: {dur:.1f}s")
    print(f"  TOTAL: {total:.1f}s")

    # 3. Download flags
    print("\n=== Flags ===")
    flags_dir = download_flags() if FLAGS else None

    # 4. Title card
    print("\n=== Title Card ===")
    title_img = TMP / "title_card.jpg"
    make_title_card(title_img, flags_dir, TITLE_BG_PHOTO)

    # 5. CTA
    cta_img = TMP / "cta_frame.jpg"
    make_cta(cta_img)

    # 6. Prepare video segments
    print("\n=== Preparing segments ===")
    seg_files = []

    # Intro
    seg0 = TMP / "seg0_intro.mp4"
    run(["ffmpeg", "-y", "-i", str(BASE / INTRO_VIDEO),
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
         "-t", f"{segments[0][1]:.2f}",
         "-c:v", "libx264", "-preset", "fast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-r", "24", "-an", str(seg0)])
    seg_files.append(seg0)
    print(f"  ✅ seg0_intro")

    # Title card
    seg1 = TMP / "seg1_title.mp4"
    make_still(title_img, segments[1][1], seg1)
    print(f"  ✅ seg1_title")

    # Country/theme clips
    for i, (video_src, _) in enumerate(SEGMENTS):
        seg = TMP / f"seg{i+2}_clip.mp4"
        stretch_video(BASE / video_src, segments[i+2][1], seg)
        seg_files.append(seg)
        print(f"  ✅ seg{i+2}_clip")

    # CTA
    seg_last = TMP / f"seg{len(segments)-1}_cta.mp4"
    make_still(cta_img, segments[-1][1], seg_last)
    seg_files.append(seg_last)
    print(f"  ✅ seg{len(segments)-1}_cta")

    # 7. Concat
    print("\n=== Concatenating ===")
    concat_file = TMP / "concat.txt"
    with open(concat_file, "w") as f:
        for sf in seg_files:
            f.write(f"file '{sf.absolute()}'\n")

    concat_out = TMP / "concat_video.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_file),
         "-c", "copy", str(concat_out)])

    # 8. Audio: per-segment VO delays
    print("\n=== Audio ===")
    vo_delays = [0.0] * len(vo_files)
    t = 0.0
    for i, (_, dur) in enumerate(segments):
        if i < len(vo_files):
            vo_delays[i] = t + (dur - vo_durs[i]) / 2  # center VO in segment
            t += dur
        else:
            t += dur

    # Build audio: VO segments at delays + music + stinger
    audio_parts = []
    for i, vf in enumerate(vo_files):
        delay_ms = int(vo_delays[i] * 1000)
        audio_parts.append(f"[{i}:a]adelay={delay_ms}|{delay_ms}[vo{i}]")

    n_vo = len(vo_files)
    labels = "".join(f"[vo{i}]" for i in range(n_vo))
    amix_inputs = n_vo + 2  # VO + music + stinger

    fc = ";".join(audio_parts)
    fc += f";[{n_vo}:a]volume={MUSIC_VOLUME}[music]"
    fc += f";[{n_vo+1}:a]volume=0.8[stinger]"
    fc += f";{labels}[music][stinger]amix=inputs={amix_inputs}:duration=longest:dropout_transition=0[aout]"

    audio_out = TMP / "audio_final.mp3"
    audio_inputs = [str(f) for f in vo_files] + [str(BASE / MUSIC_PATH), str(BASE / STINGER_PATH)]

    cmd = ["ffmpeg", "-y"]
    for inp in audio_inputs:
        cmd += ["-i", inp]
    cmd += ["-filter_complex", fc, "-map", "[aout]",
            "-t", f"{total:.2f}", "-b:a", "128k", str(audio_out)]
    run(cmd)
    print(f"  ✅ Audio: {audio_out}")

    # 9. Subtitles
    print("\n=== Subtitles ===")
    subs = TMP / "subtitles.ass"
    make_subtitles(vo_files, vo_delays, subs)

    # 10. Final build
    print("\n=== FINAL BUILD ===")
    run([
        "ffmpeg", "-y",
        "-i", str(concat_out),
        "-i", str(audio_out),
        "-vf", f"ass={subs}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "24",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(OUT)
    ])

    # Verify
    final_dur = get_duration(OUT)
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=duration", "-of", "csv=p=0", str(OUT)],
        capture_output=True, text=True
    )
    audio_dur = float(r.stdout.strip()) if r.stdout.strip() else 0
    size_mb = OUT.stat().st_size / (1024 * 1024)

    print(f"\n  ✅ SHORT FINAL")
    print(f"     Size: {size_mb:.1f} MB")
    print(f"     Resolution: {W}x{H}")
    print(f"     Duration: {final_dur:.1f}s")
    print(f"     Audio dur: {audio_dur:.1f}s")

    if abs(final_dur - audio_dur) > 1.0:
        print(f"  ⚠️  WARNING: Audio ({audio_dur:.1f}s) ≠ Video ({final_dur:.1f}s)!")

    # Cleanup
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
