#!/usr/bin/env python3
"""
Batch-compress individual section clips for Telegram delivery.
Each clip (one per section) is compressed to H.264 ~1100 kbps → 2-8 MB.
Used when the user wants separate clips per section instead of one long file.

Usage:
    python compress_individual.py <clips_dir> [--out <out_dir>]

Defaults:
    clips_dir = the broll_ai_v3/ render directory (contains clip_NN_*.mp4)
    out_dir   = clips_dir/individual/

Bitrate strategy:
    1100 kbps video (H.264 ultrafast) + 128 kbps audio (AAC).
    Sweet spot for 720p clips 20-55s: 2-8 MB each, under Telegram's 50 MB limit.
    The text on transparent slides stays readable at this bitrate (validated user).

Pitfall (see SKILL.md #19): do NOT use HEVC on these clips — they are outputs of
ffmpeg concat -c copy on stream_loop segments, and libx265 fails on frame 0.
"""
import subprocess, os, sys, argparse
from pathlib import Path

def compress_one(src: Path, out: Path, bitrate: str = "1100k") -> tuple[bool, str]:
    """Compress a single clip. Returns (success, info_str)."""
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(src),
        "-c:v", "libx264", "-preset", "ultrafast",
        "-b:v", bitrate, "-maxrate", "1500k", "-bufsize", "2200k",
        "-c:a", "aac", "-b:a", "128k",
        str(out)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        return False, r.stderr[-200:]
    sz = os.path.getsize(out) // 1024 // 1024
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(out)],
        capture_output=True, text=True).stdout.strip())
    return True, f"{sz}MB | {dur:.1f}s"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips_dir", nargs="?", 
                    default="/home/tars/crypto-project/CHANNEL/video2/renders/broll_ai_v3")
    ap.add_argument("--out", default=None, help="output dir (default: <clips_dir>/individual)")
    ap.add_argument("--bitrate", default="1100k")
    args = ap.parse_args()

    clips_dir = Path(args.clips_dir)
    out_dir = Path(args.out) if args.out else clips_dir / "individual"
    out_dir.mkdir(parents=True, exist_ok=True)

    clips = sorted(clips_dir.glob("clip_*.mp4"))
    # Exclude already-compressed _tg.mp4 files
    clips = [c for c in clips if not c.stem.endswith("_tg")]
    if not clips:
        print(f"No clip_*.mp4 found in {clips_dir}")
        sys.exit(1)

    print(f"Compressing {len(clips)} clips → {out_dir}\n")
    total_ok = 0
    for clip in clips:
        out = out_dir / clip.name.replace(".mp4", "_tg.mp4")
        ok, info = compress_one(clip, out, args.bitrate)
        if ok:
            print(f"  ✅ {out.name}: {info}")
            total_ok += 1
        else:
            print(f"  ❌ {clip.name}: {info}")
    print(f"\nDone. {total_ok}/{len(clips)} compressed.")

if __name__ == "__main__":
    main()
