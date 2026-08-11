#!/usr/bin/env python3
"""
Thumbnail generator for vertical YouTube Shorts (1080x1920).
Style: big title + accent subtitle + dark gradient bottom.

Usage:
    python3 make_thumbnail.py FRAME_PATH "TITLE" "Subtitle" output.jpg

Example (Sankofa series):
    python3 make_thumbnail.py hero_frame.jpg "AMANIRÉNAS" "La reine qui a défié Rome" thumbnail_amanirenas.jpg
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ACCENT = (232, 149, 96)  # #E89560 Sankofa orange

def make_thumbnail(frame_path, title_text, subtitle_text, output_path, accent_color=ACCENT):
    src = Image.open(frame_path)
    sw, sh = src.size
    # Scale height→1920
    scale = 1920 / sh
    src_scaled = src.resize((int(sw * scale), 1920), Image.LANCZOS)
    # Crop center 1080
    left = (src_scaled.width - 1080) // 2
    thumb = src_scaled.crop((left, 0, left + 1080, 1920)).convert('RGBA')
    
    # Gradient overlay bottom 40%
    overlay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(1100, 1920):
        alpha = int(((y - 1100) / 820) ** 1.5 * 180)
        draw.line([(0, y), (1080, y)], fill=(0, 0, 0, min(alpha, 200)))
    thumb = Image.alpha_composite(thumb, overlay)
    
    draw = ImageDraw.Draw(thumb)
    
    # Title: white bold, centered at ~75% height
    title_font = ImageFont.truetype(FONT_BOLD, 85)
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (W - tw) // 2
    ty = 1450
    
    # Shadow (4-direction offset)
    for dx, dy in [(3, 3), (2, 2), (-2, 2), (2, -2)]:
        draw.text((tx + dx, ty + dy), title_text, font=title_font, fill=(0, 0, 0, 200))
    draw.text((tx, ty), title_text, font=title_font, fill=(255, 255, 255))
    
    # Subtitle: accent color, centered below title
    sub_font = ImageFont.truetype(FONT_BOLD, 38)
    bbox2 = draw.textbbox((0, 0), subtitle_text, font=sub_font)
    sw2 = bbox2[2] - bbox2[0]
    sx = (W - sw2) // 2
    sy = ty + th + 20
    
    for dx, dy in [(2, 2), (1, 1), (-1, 1), (1, -1)]:
        draw.text((sx + dx, sy + dy), subtitle_text, font=sub_font, fill=(0, 0, 0, 200))
    draw.text((sx, sy), subtitle_text, font=sub_font, fill=accent_color)
    
    thumb.convert('RGB').save(output_path, quality=95)
    print(f"Thumbnail saved: {output_path} ({W}x{H})")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(f"Usage: {sys.argv[0]} FRAME_PATH TITLE SUBTITLE OUTPUT.jpg")
        sys.exit(1)
    make_thumbnail(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
