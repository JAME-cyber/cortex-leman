#!/bin/bash
# Mansa Moussa Short — Format Sankofa Standard (modèle Nzinga)
# Chapter titles (jaune, haut) + Subtitles (blanc, bas) + VO
# Usage: bash build_mansa.sh  (après avoir généré les clips dans clips/)
set -e

WORK=/home/tars/sankofa/mansa_moussa/work
CLIPS=/home/tars/sankofa/mansa_moussa/clips
OUT=/home/tars/sankofa/mansa_moussa/output
AUDIO=/home/tars/sankofa/mansa_moussa/audio

mkdir -p "$WORK" "$OUT"

echo "=== Step 1: Zoom-crop clips to 1080x1920 full-bleed ==="
for f in "$CLIPS"/v*.mp4; do
  name=$(basename "$f" .mp4)
  ffmpeg -y -i "$f" \
    -vf "scale=-1:1920,crop=1080:1920" \
    -an -c:v libx264 -preset fast -crf 20 \
    "$WORK/${name}.mp4" 2>/dev/null
  echo "  $name done"
done

echo "=== Step 2: Concat clips ==="
> "$WORK/concat.txt"
for f in "$WORK"/v*.mp4; do
  echo "file '$f'" >> "$WORK/concat.txt"
done
ffmpeg -y -f concat -safe 0 -i "$WORK/concat.txt" -c copy "$WORK/video.mp4" 2>/dev/null
DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$WORK/video.mp4")
echo "Video: ${DUR}s"

echo "=== Step 3: Audio (VO + fade) ==="
ffmpeg -y -i "$AUDIO/vo_mansa.mp3" \
  -af "adelay=500|500,apad=pad_dur=2,afade=t=out:st=91:d=2" \
  -t "$DUR" -c:a aac -b:a 128k -ar 44100 -ac 2 "$WORK/audio.m4a" 2>/dev/null

echo "=== Step 4: Mux video+audio ==="
ffmpeg -y -i "$WORK/video.mp4" -i "$WORK/audio.m4a" \
  -c:v copy -c:a copy -shortest "$WORK/base.mp4" 2>/dev/null

echo "=== Step 5: Burn ASS subtitles ==="
ffmpeg -y -i "$WORK/base.mp4" \
  -vf "subtitles=/home/tars/sankofa/mansa_moussa/mansa_moussa.ass" \
  -c:v libx264 -preset fast -crf 22 \
  -c:a copy \
  "$OUT/mansa_moussa_short.mp4" 2>/dev/null

echo "=== DONE ==="
ls -la "$OUT/mansa_moussa_short.mp4"
