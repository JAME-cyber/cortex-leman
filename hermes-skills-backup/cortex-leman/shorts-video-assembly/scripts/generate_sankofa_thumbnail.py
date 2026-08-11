#!/usr/bin/env python3
"""
Sankofa thumbnail generator.
Extracts a clean frame (no burned text) from a video and composites
a title + subtitle in the Sankofa standard style.

Usage:
    python3 generate_sankofa_thumbnail.py <video.mp4> <TITLE> <SUBTITLE> <output.jpg>

Example:
    python3 generate_sankofa_thumbnail.py video.mp4 "REINE NZINGA" "Celle qui a humilié les Portugais" thumbnail_nzinga.jpg
"""
import sys
import os
import subprocess
import tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ACCENT_COLOR = (232, 149, 96)  # #E89560 Sankofa orange


def extract_clean_frame(video_path, fps=2):
    """Scan video at fps, return path to the cleanest frame (no burned text)."""
    tmpdir = tempfile.mkdtemp()
    pattern = os.path.join(tmpdir, "frame_%04d.jpg")
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-vf", f"fps={fps}", pattern],
        capture_output=True
    )
    
    frames = sorted([f for f in os.listdir(tmpdir) if f.startswith("frame_")])
    if not frames:
        raise RuntimeError("No frames extracted from video")
    
    best_frame = None
    best_score = float('inf')
    
    for fname in frames:
        fpath = os.path.join(tmpdir, fname)
        arr = np.array(Image.open(fpath))
        h = arr.shape[0]
        
        # Score = white pixel density in top 15% + bottom 15% (text zones)
        top_white = np.sum(np.all(arr[:int(h * 0.15)] > 200, axis=2))
        bot_white = np.sum(np.all(arr[int(h * 0.85):] > 200, axis=2))
        score = top_white + bot_white
        
        # Skip opening logo frames (first 5% of video usually black/gold intro)
        frame_idx = int(fname.split("_")[1].split(".")[0])
        total_frames = len(frames)
        if frame_idx < total_frames * 0.05:
            continue
        
        if score < best_score:
            best_score = score
            best_frame = fpath
    
    # If all frames have text, use the least-text one
    if best_frame is None:
        best_frame = os.path.join(tmpdir, frames[len(frames) // 2])
    
    print(f"Best frame: {best_frame} (text score: {best_score})")
    return best_frame


def make_thumbnail(frame_path, title_text, subtitle_text, output_path):
    """Create a 1080x1920 thumbnail with title + subtitle overlay."""
    src = Image.open(frame_path)
    sw, sh = src.size
    
    # Scale to height=1920
    scale = 1920 / sh
    new_w = int(sw * scale)
    src_scaled = src.resize((new_w, 1920), Image.LANCZOS)
    
    # Center crop to 1080 wide
    left = max(0, (new_w - 1080) // 2)
    thumb = src_scaled.crop((left, 0, left + 1080, 1920)).convert('RGBA')
    
    # Dark gradient at bottom 45% for text readability
    overlay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for y in range(1050, 1920):
        progress = (y - 1050) / 870
        alpha = int(progress ** 1.4 * 200)
        draw_ov.line([(0, y), (1080, y)], fill=(0, 0, 0, min(alpha, 210)))
    
    thumb = Image.alpha_composite(thumb, overlay)
    draw = ImageDraw.Draw(thumb)
    
    # Title (big bold white with shadow)
    title_font = ImageFont.truetype(FONT_BOLD, 85)
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (1080 - tw) // 2
    ty = 1450
    
    for dx, dy in [(3, 3), (2, 2), (-2, 2), (2, -2)]:
        draw.text((tx + dx, ty + dy), title_text, font=title_font, fill=(0, 0, 0, 220))
    draw.text((tx, ty), title_text, font=title_font, fill=(255, 255, 255))
    
    # Subtitle (accent orange with shadow)
    sub_font = ImageFont.truetype(FONT_BOLD, 38)
    bbox2 = draw.textbbox((0, 0), subtitle_text, font=sub_font)
    sw2 = bbox2[2] - bbox2[0]
    sx = (1080 - sw2) // 2
    sy = ty + th + 25
    
    for dx, dy in [(2, 2), (1, 1), (-1, 1), (1, -1)]:
        draw.text((sx + dx, sy + dy), subtitle_text, font=sub_font, fill=(0, 0, 0, 220))
    draw.text((sx, sy), subtitle_text, font=sub_font, fill=ACCENT_COLOR)
    
    thumb.convert('RGB').save(output_path, quality=95)
    print(f"Thumbnail saved: {output_path} (1080x1920)")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(f"Usage: {sys.argv[0]} <video.mp4> <TITLE> <SUBTITLE> <output.jpg>")
        sys.exit(1)
    
    video = sys.argv[1]
    title = sys.argv[2]
    subtitle = sys.argv[3]
    output = sys.argv[4]
    
    clean_frame = extract_clean_frame(video)
    make_thumbnail(clean_frame, title, subtitle, output)
