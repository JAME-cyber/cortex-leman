#!/bin/bash
# ffmpeg Ad Assembly Pipeline — Reusable Build Script
#
# Assembles video clips + VO audio + text overlays into a branded vertical ad.
# Fallback when HyperFrames server is unavailable or for rapid prototyping.
#
# Usage: Edit the CLIP_TIMING, OVERLAYS, and FONT paths, then run:
#   bash ffmpeg-ad-assembly.sh
#
# Based on Darkom-Debarras V2 production (July 2026).
# Produces 720x1280 9:16 vertical, 30s, H.264 + AAC, ~9MB.

set -e

# ─── CONFIG ──────────────────────────────────────────────────────────────────
CLIPS_DIR="clips"
AUDIO_DIR="audio"
OUT_DIR="renders"
mkdir -p "$OUT_DIR"

# Fonts — DejaVu is universally available on Linux
FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# Fallback: Liberation fonts
[ ! -f "$FONT_BOLD" ] && FONT_BOLD="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
[ ! -f "$FONT_REG" ] && FONT_REG="/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# Brand colors (hex without #, prefixed with 0x for ffmpeg)
# Example: Darkom-Debarras
PRIMARY="0x143d24"    # Vert forêt — dark backgrounds
ACCENT="0xa0ab37"     # Olive — CTA, stats
SURFACE="0xf8f8f5"    # Crème — text on dark
WHITE="white"
MUTED_ALPHA="0xf8f8f5aa"  # Semi-transparent crème for watermarks

# ─── STEP 1: Normalize clips to 720x1280 ────────────────────────────────────
# Each clip: scale + crop to exact 720x1280, trim to target duration.
# Add tpad=stop_mode=clone:stop_duration=N to extend short clips.

normalize_clip() {
    local input="$1"
    local output="$2"
    local duration="$3"
    local extra_vf="${4:-}"

    local vf="scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1"
    [ -n "$extra_vf" ] && vf="${vf},${extra_vf}"

    ffmpeg -y -i "$input" -t "$duration" \
        -vf "$vf" -an \
        -c:v libx264 -preset medium -crf 18 \
        "$output" 2>/dev/null
}

echo "Normalizing clips..."
normalize_clip "$CLIPS_DIR/clip-01.mp4" "$CLIPS_DIR/norm-01.mp4" 5
normalize_clip "$CLIPS_DIR/clip-02.mp4" "$CLIPS_DIR/norm-02.mp4" 5
# Clip 3 is 4s — clone last frame to pad to 5s
normalize_clip "$CLIPS_DIR/clip-03.mp4" "$CLIPS_DIR/norm-03.mp4" 5 "tpad=stop_mode=clone:stop_duration=1"
normalize_clip "$CLIPS_DIR/clip-04.mp4" "$CLIPS_DIR/norm-04.mp4" 6
normalize_clip "$CLIPS_DIR/clip-05.mp4" "$CLIPS_DIR/norm-05.mp4" 4

# ─── STEP 2: Create CTA card (solid color background) ───────────────────────
echo "Creating CTA card..."
ffmpeg -y -f lavfi -i "color=c=${PRIMARY}:s=720x1280:d=5:r=25" \
    -c:v libx264 -preset medium -crf 18 \
    "$CLIPS_DIR/norm-06-raw.mp4" 2>/dev/null

# ─── STEP 3: Concat all clips ───────────────────────────────────────────────
echo "Concatenating..."
cat > "$CLIPS_DIR/concat_list.txt" << EOF
file 'norm-01.mp4'
file 'norm-02.mp4'
file 'norm-03.mp4'
file 'norm-04.mp4'
file 'norm-05.mp4'
file 'norm-06-raw.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i "$CLIPS_DIR/concat_list.txt" \
    -c copy "$OUT_DIR/base-video.mp4" 2>/dev/null

# ─── STEP 4: Merge VO tracks with silence padding ───────────────────────────
# Each VO clip starts 0.3s into its scene.
# Run via python3 (numpy + soundfile required).
echo "Merging VO..."
python3.12 << 'PYEOF'
import numpy as np, soundfile as sf

AUDIO_DIR = 'audio'
SR = 24000
TOTAL = 30.0

output = np.zeros(int(TOTAL * SR), dtype=np.float32)

scenes = [
    (0.3, 'vo-1.wav'),
    (5.3, 'vo-2.wav'),
    (10.3, 'vo-3.wav'),
    (15.3, 'vo-4.wav'),
    (21.3, 'vo-5.wav'),
    (25.3, 'vo-6.wav'),
]

for start, fname in scenes:
    audio, sr = sf.read(f'{AUDIO_DIR}/{fname}')
    if sr != SR:
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=SR)
    start_sample = int(start * SR)
    end_sample = min(start_sample + len(audio), len(output))
    output[start_sample:end_sample] += audio[:end_sample - start_sample]

peak = np.abs(output).max()
if peak > 0.95:
    output = output * (0.95 / peak)

sf.write(f'{AUDIO_DIR}/vo-full.wav', output, SR, subtype='PCM_16')
print(f'VO track: {len(output)/SR:.1f}s')
PYEOF

# ─── STEP 5: Text overlays + final render ───────────────────────────────────
# Pattern: drawtext filters chained via commas, each with enable='between(t,start,end)'
# Syntax: drawtext=fontfile=...:text='...':fontcolor=...:fontsize=N:x=...:y=...:enable='...'
#
# Positioning helpers:
#   Centered: x=(w-text_w)/2
#   Vertical fraction: y=h*0.25 (25% from top)
#   Shadow: shadowcolor=black@0.5:shadowx=2:shadowy=2
#   Bg box: box=1:boxcolor=0xa0ab37:boxborderw=12

echo "Applying overlays and rendering final..."
ffmpeg -y \
  -i "$OUT_DIR/base-video.mp4" \
  -i "$AUDIO_DIR/vo-full.wav" \
  -filter_complex "
    [0:v]
    drawtext=fontfile='$FONT_BOLD':text='YOUR TITLE':fontcolor=$WHITE:fontsize=52:x=(w-text_w)/2:y=h*0.12:shadowcolor=black@0.5:shadowx=2:shadowy=2:enable='between(t,0.5,4.5)',
    drawtext=fontfile='$FONT_BOLD':text='SUBTITLE':fontcolor=$ACCENT:fontsize=28:x=(w-text_w)/2:y=h*0.18:enable='between(t,5.5,9.5)',
    drawtext=fontfile='$FONT_BOLD':text='48-72H':fontcolor=$WHITE:fontsize=64:x=(w-text_w)/2:y=h*0.40:shadowcolor=black@0.5:shadowx=2:shadowy=2:enable='between(t,10.5,14.5)',
    drawtext=fontfile='$FONT_REG':text='Intervention rapide':fontcolor=$SURFACE:fontsize=24:x=(w-text_w)/2:y=h*0.50:enable='between(t,10.5,14.5)',
    drawtext=fontfile='$FONT_BOLD':text='CTA BUTTON':fontcolor=$PRIMARY:fontsize=36:box=1:boxcolor=$ACCENT:boxborderw=12:x=(w-text_w)/2:y=h*0.53:enable='between(t,26.5,29.5)',
    drawtext=fontfile='$FONT_BOLD':text='06 00 00 00 00':fontcolor=$SURFACE:fontsize=42:x=(w-text_w)/2:y=h*0.65:enable='between(t,26.5,29.5)',
    drawtext=fontfile='$FONT_REG':text='yourdomain.fr':fontcolor=$MUTED_ALPHA:fontsize=20:x=(w-text_w)/2:y=h*0.92:enable='between(t,0,25)'
    [v];
    [1:a]volume=1.5,apad,atrim=0:30[a]
  " \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset medium -crf 18 \
  -c:a aac -b:a 192k \
  -t 30 \
  -movflags +faststart \
  "$OUT_DIR/ad-final.mp4"

echo ""
echo "=== Result ==="
ls -lh "$OUT_DIR/ad-final.mp4"
ffprobe -v quiet -show_entries format=duration:stream=width,height,codec_name \
  -of default=noprint_wrappers=1 "$OUT_DIR/ad-final.mp4"
