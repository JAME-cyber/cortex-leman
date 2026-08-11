#!/usr/bin/env python3
"""
Cortex Leman — Video Brief Generator v1.1
Simplified pipeline for fast rendering on low-CPU environments.

Usage:
  python3 generate_video.py --text "Brief content" --output video.mp4
  python3 generate_video.py --file brief.md --output video.mp4
  python3 generate_video.py --text "..." --voice fr-CH-FabriceNeural --aspect 16:9
"""

import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────

BRAND = {
    "bg_dark": (26, 26, 46),
    "bg_mid": (22, 33, 62),
    "accent": (233, 69, 96),
    "text": (245, 245, 245),
}

DEFAULT_VOICE = "fr-CH-ArianeNeural"
DEFAULT_ASPECT = "9:16"

ASPECTS = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
}

FPS = 24
VIDEO_CODEC = "libx264"


def find_font():
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(p):
            return p
    for root, dirs, files in os.walk("/usr/share/fonts"):
        for f in files:
            if f.endswith((".ttf", ".ttc")):
                return os.path.join(root, f)
    return None


def clean_text(text: str) -> str:
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
    text = re.sub(r'\|\|([^|]+)\|\|', r'\1', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def split_paragraphs(text: str) -> list[str]:
    paragraphs = re.split(r'\n\n+', text.strip())
    return [p.strip() for p in paragraphs if p.strip()]


# ── TTS ─────────────────────────────────────────────────────────────────────

async def generate_tts(text: str, voice: str, output_path: str) -> str:
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()
    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)
    return submaker.get_srt()


def run_tts(text: str, voice: str, output_path: str) -> str:
    return asyncio.run(generate_tts(text, voice, output_path))


def parse_srt(srt_text: str) -> list[dict]:
    if not srt_text or not srt_text.strip():
        return []
    blocks = re.split(r'\n\n+', srt_text.strip())
    subtitles = []
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        time_match = re.match(
            r'(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})',
            lines[1]
        )
        if not time_match:
            continue
        g = time_match.groups()
        start = int(g[0])*3600 + int(g[1])*60 + int(g[2]) + int(g[3])/1000
        end = int(g[4])*3600 + int(g[5])*60 + int(g[6]) + int(g[7])/1000
        text = ' '.join(lines[2:]).strip()
        if text:
            subtitles.append({"start": start, "end": end, "text": text})
    return subtitles


# ── Pexels ──────────────────────────────────────────────────────────────────

def search_pexels(query: str, api_key: str, orientation: str = "portrait") -> list[str]:
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation={orientation}"
    req = urllib.request.Request(url, headers={"Authorization": api_key})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        target_h = 1920 if orientation == "portrait" else 1080
        urls = []
        for video in data.get("videos", []):
            for vf in video.get("video_files", []):
                if vf.get("height") == target_h:
                    urls.append(vf["link"])
                    break
            if len(urls) >= 2:
                break
        return urls
    except Exception:
        return []


def download_video(url: str, output_path: str):
    urllib.request.urlretrieve(url, output_path)


# ── FFmpeg-based video generation (fast, no MoviePy for composition) ────────

def create_frame_image(text: str, width: int, height: int, font: str, bg_color: tuple, output_path: str, title_mode: bool = False):
    """Create a single PNG frame using Pillow (fast, no MoviePy dependency for frames)."""
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    try:
        if title_mode:
            font_main = ImageFont.truetype(font, 56)
            font_sub = ImageFont.truetype(font, 28)
        else:
            font_main = ImageFont.truetype(font, 40)
            font_sub = ImageFont.truetype(font, 24)
    except Exception:
        font_main = ImageFont.load_default()
        font_sub = font_main
    
    if title_mode:
        # Accent line
        line_y = height // 2 - 80
        draw.rectangle([(100, line_y), (width - 100, line_y + 4)], fill=BRAND["accent"])
        # Title
        draw.text((width // 2, height // 2 - 40), text, fill=BRAND["text"],
                  font=font_main, anchor="mm")
        # Date
        date_str = datetime.now().strftime("Semaine du %d/%m/%Y")
        draw.text((width // 2, height // 2 + 50), date_str, fill=BRAND["accent"],
                  font=font_sub, anchor="mm")
    else:
        # Wrap text
        max_chars = 30 if height > width else 50
        words = text.split()
        lines = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 > max_chars:
                lines.append(current)
                current = word
            else:
                current = f"{current} {word}".strip()
        if current:
            lines.append(current)
        
        # Only show first 3 lines
        lines = lines[:3]
        if len(text) > max_chars * 3:
            lines[-1] = lines[-1][:-3] + "..."
        
        total_h = len(lines) * 50
        start_y = (height - total_h) // 2
        
        for i, line in enumerate(lines):
            y = start_y + i * 50
            draw.text((width // 2, y), line, fill=BRAND["text"],
                      font=font_main, anchor="mm")
    
    img.save(output_path, "PNG")


def create_subtitle_srt(subtitles: list[dict], offset: float, output_path: str):
    """Write subtitles as SRT file for ffmpeg burn-in."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles):
            start = sub["start"] + offset
            end = sub["end"] + offset
            # ASS-style formatting: bold white on semi-transparent black
            text = sub["text"].replace('\n', ' ')
            f.write(f"{i+1}\n")
            f.write(f"{_fmt_time(start)} --> {_fmt_time(end)}\n")
            f.write(f"{text}\n\n")


def _fmt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_video_ffmpeg(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    aspect: str = DEFAULT_ASPECT,
    title: str = "Brief RGPD-IA",
    pexels_key: str = None,
):
    """FFmpeg-based pipeline: much faster than MoviePy compositing."""
    
    width, height = ASPECTS.get(aspect, ASPECTS["9:16"])
    font = find_font()
    if not font:
        print("ERROR: No font found.", file=sys.stderr)
        sys.exit(1)
    
    tmpdir = tempfile.mkdtemp(prefix="mpt_")
    audio_path = os.path.join(tmpdir, "audio.mp3")
    srt_path = os.path.join(tmpdir, "subtitles.srt")
    
    try:
        # Step 1: Clean + split
        print("[1/5] Cleaning text...")
        clean = clean_text(text)
        paragraphs = split_paragraphs(clean)
        if not paragraphs:
            print("ERROR: No content after cleaning.", file=sys.stderr)
            sys.exit(1)
        
        full_text = '\n\n'.join(paragraphs)
        print(f"   → {len(paragraphs)} paragraphs, {len(full_text)} chars")
        
        # Step 2: TTS
        print(f"[2/5] Generating TTS ({voice})...")
        srt_text = run_tts(full_text, voice, audio_path)
        subtitles = parse_srt(srt_text)
        print(f"   → Subtitles: {len(subtitles)} segments")
        
        # Get audio duration via ffprobe
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", audio_path],
            capture_output=True, text=True
        )
        total_duration = float(result.stdout.strip())
        print(f"   → Duration: {total_duration:.1f}s")
        
        title_duration = 3.0
        content_duration = title_duration + total_duration
        
        # Step 3: Write SRT with offset
        print("[3/5] Writing subtitles...")
        create_subtitle_srt(subtitles, title_duration, srt_path)
        
        # Step 4: Create background images + concat
        print("[4/5] Creating visual frames...")
        
        # Title frame
        title_img = os.path.join(tmpdir, "title.png")
        create_frame_image(title, width, height, font, BRAND["bg_dark"], title_img, title_mode=True)
        
        # Content frames (one per paragraph, cycle backgrounds)
        content_imgs = []
        for i, para in enumerate(paragraphs):
            img_path = os.path.join(tmpdir, f"content_{i}.png")
            bg = BRAND["bg_dark"] if i % 2 == 0 else BRAND["bg_mid"]
            display = para[:120] + ("..." if len(para) > 120 else "")
            create_frame_image(display, width, height, font, bg, img_path)
            content_imgs.append(img_path)
        
        # If Pexels key available, try to mix in stock footage
        pexels_clips = []
        if pexels_key:
            orientation = "portrait" if height > width else "landscape"
            for i, para in enumerate(paragraphs[:3]):  # Max 3 Pexels clips
                search_term = ' '.join(para.split()[:3]) + " technology"
                urls = search_pexels(search_term, pexels_key, orientation)
                if urls:
                    clip_path = os.path.join(tmpdir, f"pexels_{i}.mp4")
                    try:
                        download_video(urls[0], clip_path)
                        pexels_clips.append((i, clip_path))
                        print(f"   → Pexels clip for paragraph {i+1}")
                    except Exception:
                        pass
        
        # Step 5: FFmpeg compose
        print("[5/5] Rendering video with FFmpeg...")
        
        # Strategy: Create a slideshow from images, overlay audio + subtitles
        # Each content image gets equal time from the audio duration
        
        # Build concat file for FFmpeg
        # Title: 3 seconds, then content images share the audio duration
        para_duration = total_duration / max(len(paragraphs), 1)
        
        concat_path = os.path.join(tmpdir, "concat.txt")
        with open(concat_path, 'w') as f:
            # Title card
            f.write(f"file '{title_img}'\n")
            f.write(f"duration {title_duration}\n")
            
            # Content images
            for i, img in enumerate(content_imgs):
                f.write(f"file '{img}'\n")
                f.write(f"duration {para_duration}\n")
        
        # FFmpeg command: image slideshow + audio + subtitles
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_path,
            "-i", audio_path,
            "-itsoffset", str(title_duration), "-i", audio_path,  # audio delayed
            # Use second audio input (delayed), ignore first
            "-map", "0:v", "-map", "2:a",
            # Subtitle burn-in
            "-vf", f"subtitles={srt_path}:force_style='FontName=DejaVu Sans,FontSize=14,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,Outline=1,Shadow=1,MarginV=30'",
            "-c:v", VIDEO_CODEC,
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-r", str(FPS),
            "-shortest",
            output_path,
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr[-500:]}", file=sys.stderr)
            # Fallback: without subtitles
            print("Retrying without subtitles...")
            cmd_simple = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", concat_path,
                "-itsoffset", str(title_duration), "-i", audio_path,
                "-map", "0:v", "-map", "1:a",
                "-c:v", VIDEO_CODEC,
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-pix_fmt", "yuv420p",
                "-r", str(FPS),
                "-shortest",
                output_path,
            ]
            result = subprocess.run(cmd_simple, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"FFmpeg error (no subs): {result.stderr[-500:]}", file=sys.stderr)
                sys.exit(1)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n✅ Video generated: {output_path}")
        print(f"   Duration: {content_duration:.1f}s")
        print(f"   Resolution: {width}x{height}")
        print(f"   Size: {file_size:.1f}MB")
        print(f"   Subtitles: {len(subtitles)} segments")
    
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Cortex Leman — Video Brief Generator")
    parser.add_argument("--text", help="Brief text content")
    parser.add_argument("--file", help="Read brief from file")
    parser.add_argument("--output", "-o", help="Output video path", required=True)
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"TTS voice (default: {DEFAULT_VOICE})")
    parser.add_argument("--aspect", default=DEFAULT_ASPECT, choices=list(ASPECTS.keys()))
    parser.add_argument("--title", default="Brief RGPD-IA", help="Title card text")
    
    args = parser.parse_args()
    
    if args.file:
        with open(args.file, "r") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        print("ERROR: Provide --text or --file", file=sys.stderr)
        sys.exit(1)
    
    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    
    generate_video_ffmpeg(
        text=text,
        output_path=args.output,
        voice=args.voice,
        aspect=args.aspect,
        title=args.title,
        pexels_key=pexels_key if pexels_key else None,
    )


if __name__ == "__main__":
    main()
