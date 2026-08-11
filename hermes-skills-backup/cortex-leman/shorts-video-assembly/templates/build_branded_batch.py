#!/usr/bin/env python3
"""
Template: Batch prepend stinger + append outro to all videos in a campaign.

Structure per video: [Stinger ~3.5s] → [Video body + pricing CTA] → [Outro ~4s]

Usage:
  1. Set STINGER, SUNSET_CLIP, MUSIC paths
  2. Add video filenames to VIDEOS list
  3. Run: python3 build_branded_batch.py
  4. Outputs go to output/v3_branded/

See also: references/unified-intro-stinger.md, references/unified-outro.md
"""
import subprocess
from pathlib import Path

# ═══════════════════════════════════════
# CONFIG — adapt to your campaign
# ═══════════════════════════════════════

BASE = Path("/path/to/project")
OUT = BASE / "output"

# Stinger: brand signature with audio (~3.5s)
STINGER = str(BASE / "assets/signature_stingered.mp4")

# Outro clip: animated background (~4s, no audio)
OUTRO_CLIP = str(BASE / "renders/sunset_bg.mp4")

# Music track for outro fade-out
MUSIC = str(BASE / "assets/music/campaign_music.mp3")

# Videos to process (filenames in OUT/)
VIDEOS = [
    "video1.mp4",
    "video2.mp4",
    # ...
]

# Compression settings
CRF = 20           # render quality
TG_CRF = 26        # Telegram delivery compression
TG_MAXRATE = 3200

# ═══════════════════════════════════════
# ENGINE — don't modify below
# ═══════════════════════════════════════

def run(cmd, timeout=600):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        print(f"  ❌ {r.stderr[-400:]}")
        return False
    return True

def probe_dur(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True
    )
    return float(r.stdout.strip())

def build_branded(src_path, out_path):
    """
    3-segment concat: stinger + body + outro.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", STINGER,       # 0: stinger (has audio)
        "-i", str(src_path), # 1: main video (has audio)
        "-i", OUTRO_CLIP,    # 2: outro bg (no audio)
        "-i", MUSIC,         # 3: music for outro
        "-filter_complex",
        # Video: scale to 720x1280@30, concat 3 segments
        "[0:v]scale=720:1280,fps=30[sting_v];"
        "[1:v]scale=720:1280,fps=30[main_v];"
        "[2:v]scale=720:1280,fps=30[outro_v];"
        "[sting_v][main_v][outro_v]concat=n=3:v=1:a=0[vout];"
        # Audio: stinger → body → music fade-out
        "[3:a]atrim=20:24.2,asetpts=PTS-STARTPTS,"
        "afade=t=out:st=3.0:d=1.2,volume=0.25[outro_mus];"
        "[0:a]anull[sting_a];"
        "[1:a]anull[main_a];"
        "[sting_a][main_a][outro_mus]concat=n=3:v=0:a=1[aout]",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", str(CRF), "-pix_fmt", "yuv420p", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k", "-r", "30",
        str(out_path)
    ]
    src_dur = probe_dur(src_path)
    print(f"  Building → {out_path.name}")
    if run(cmd):
        final = probe_dur(out_path)
        print(f"  ✅ {final:.1f}s (stinger + {src_dur:.1f}s content + outro)")
        return True
    return False

def compress_tg(src, dst):
    """Compress for Telegram delivery."""
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-c:v", "libx264", "-crf", str(TG_CRF),
        "-maxrate", f"{TG_MAXRATE}k", "-bufsize", f"{TG_MAXRATE*2}k",
        "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(dst)
    ]
    return run(cmd)

if __name__ == "__main__":
    branded_dir = OUT / "branded"
    branded_dir.mkdir(exist_ok=True)

    for fname in VIDEOS:
        src = OUT / fname
        if not src.exists():
            print(f"⚠️  {fname} not found, skipping")
            continue

        stem = src.stem
        dst = branded_dir / f"{stem}_branded.mp4"

        print(f"\n{'='*55}")
        print(f"📹 {fname}")

        if build_branded(src, dst):
            # Also create TG-compressed version
            tg_path = Path(f"/tmp/TG_{dst.name}")
            if compress_tg(dst, tg_path):
                sz = tg_path.stat().st_size / 1048576
                print(f"  📦 TG: {sz:.1f}MB")

    print(f"\n{'='*55}")
    print(f"✅ All branded videos in: {branded_dir}")
