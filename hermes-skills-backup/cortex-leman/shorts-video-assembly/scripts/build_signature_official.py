#!/usr/bin/env python3
"""
Marketing signature builder using the OFFICIAL client logo.

Animates the real logo: fade-in + scale-up (easeOutCubic) + hold with breathing +
tagline/date/location fading in at the bottom. Produces a 3.5s reusable intro segment.

NEVER draw a fake logo/tampon when the client has an official one.
Always use the real brand asset — authenticity > aesthetics.

Usage:
    python3 build_signature_official.py <logo_path> <output_mp4> [--tagline TEXT] [--date TEXT] [--location TEXT] [--duration 3.5]

Requirements: PIL/Pillow, ffmpeg
"""
import subprocess, math, sys, argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30

# Default palette (override with project charte)
PALETTE = {
    "terra":      (0xA0, 0x39, 0x2B),
    "ochre":      (0xB5, 0x87, 0x61),
    "cacao":      (0x49, 0x2E, 0x21),
    "cream":      (0xF5, 0xE8, 0xD3),
}


def remove_background(img, tolerance=12):
    """Chroma-key removal for opaque RGBA logos with uniform bg.
    Samples the corner pixel and makes similar pixels transparent."""
    bg = img.getpixel((5, 5))
    data = list(img.getdata())
    new_data = []
    for px in data:
        r, g, b, a = px
        if abs(r - bg[0]) < tolerance and abs(g - bg[1]) < tolerance and abs(b - bg[2]) < tolerance:
            new_data.append((r, g, b, 0))
        else:
            new_data.append(px)
    out = Image.new("RGBA", img.size)
    out.putdata(new_data)
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    return out


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def build_signature(logo_path, output_path, tagline, date_text, location_text,
                    duration=3.5, font_dir=None):
    """Build animated signature with official logo."""
    FRAMES = int(duration * FPS)
    tmp = Path("/tmp/sig_logo_frames")
    tmp.mkdir(exist_ok=True)

    # Load and process logo
    logo = Image.open(logo_path).convert("RGBA")
    logo_proc = remove_background(logo)
    print(f"Logo: {logo.size} → cropped to {logo_proc.size}")

    # Fonts (fallback to defaults if not provided)
    font_dir = Path(font_dir) if font_dir else Path(__file__).parent.parent / "assets/fonts"
    try:
        f_pfair = str(font_dir / "PlayfairDisplay-Variable.ttf")
        f_poppins = str(font_dir / "Poppins-Bold.ttf")
        f_poppins_reg = str(font_dir / "Poppins-Regular.ttf")
        ImageFont.truetype(f_pfair, 10)  # test load
    except Exception:
        f_pfair = "DejaVuSerif-Bold.ttf"
        f_poppins = "DejaVuSans-Bold.ttf"
        f_poppins_reg = "DejaVuSans.ttf"

    CREAM = PALETTE["cream"]

    for frame_num in range(FRAMES):
        t = frame_num / FPS

        # Phases
        if t < 0.6:
            p = t / 0.6
            scale = 0.85 + 0.15 * ease_out_cubic(p)
            logo_alpha = ease_out_cubic(p)
            bar_alpha = 0
        elif t < 1.0:
            p = (t - 0.6) / 0.4
            scale = 1.0
            logo_alpha = 1.0
            bar_alpha = p
        elif t < duration - 0.7:
            scale = 1.0 + 0.01 * math.sin((t - 1.0) * 2)
            logo_alpha = 1.0
            bar_alpha = 1.0
        else:
            p = (t - (duration - 0.7)) / 0.7
            scale = 1.0 + 0.02 * p
            logo_alpha = 1.0
            bar_alpha = 1.0

        img = Image.new("RGB", (W, H), CREAM)
        draw = ImageDraw.Draw(img)

        # Place logo
        logo_size = int(700 * scale)
        logo_resized = logo_proc.resize((logo_size, logo_size), Image.LANCZOS)
        lx = (W - logo_size) // 2
        ly = (H // 2 - 250) - (logo_size // 2)
        img.paste(logo_resized, (lx, ly), logo_resized)
        draw = ImageDraw.Draw(img, "RGBA")

        # Bottom strip
        if bar_alpha > 0:
            a = int(255 * bar_alpha)
            draw.rectangle([80, H - 380, W - 80, H - 376], fill=(*PALETTE["ochre"], a))

            # Tagline
            if tagline:
                f = ImageFont.truetype(f_poppins, 28)
                bbox = draw.textbbox((0, 0), tagline, font=f)
                tw = bbox[2] - bbox[0]
                draw.text(((W - tw) // 2, H - 340), tagline, font=f, fill=(*PALETTE["cacao"], a))

            # Date
            if date_text:
                f = ImageFont.truetype(f_pfair, 44)
                f.set_variation_by_axes([700]) if hasattr(f, 'set_variation_by_axes') else None
                bbox = draw.textbbox((0, 0), date_text, font=f)
                tw = bbox[2] - bbox[0]
                draw.text(((W - tw) // 2, H - 280), date_text, font=f, fill=(*PALETTE["terra"], a))

            # Location
            if location_text:
                f = ImageFont.truetype(f_poppins_reg, 28)
                bbox = draw.textbbox((0, 0), location_text, font=f)
                tw = bbox[2] - bbox[0]
                draw.text(((W - tw) // 2, H - 210), location_text, font=f, fill=(*PALETTE["ochre"], a))

            draw.rectangle([80, H - 100, W - 80, H - 96], fill=(*PALETTE["ochre"], a))

        img.save(str(tmp / f"frame_{frame_num:04d}.png"))

    print(f"Generated {FRAMES} frames")

    # Encode
    cmd = ["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(tmp / "frame_%04d.png"),
           "-c:v", "libx264", "-preset", "fast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", str(output_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        sz = output_path.stat().st_size / (1024 * 1024)
        print(f"✅ Signature: {output_path} ({sz:.2f}MB)")
    else:
        print(f"❌ Encode failed: {r.stderr[-300:]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build animated signature with official logo")
    parser.add_argument("logo", type=str, help="Path to official logo PNG")
    parser.add_argument("output", type=str, help="Output MP4 path")
    parser.add_argument("--tagline", type=str, default="DÉCOUVRIR · INSPIRER · TRANSMETTRE")
    parser.add_argument("--date", type=str, default="10 – 14 août 2026")
    parser.add_argument("--location", type=str, default="Maison de Quartier du Plateau · Petit-Lancy")
    parser.add_argument("--duration", type=float, default=3.5)
    parser.add_argument("--font-dir", type=str, default=None)
    args = parser.parse_args()

    build_signature(
        Path(args.logo),
        Path(args.output),
        args.tagline,
        args.date,
        args.location,
        args.duration,
        args.font_dir,
    )
