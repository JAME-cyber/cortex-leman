#!/bin/bash
# Amanirenas Short V4 — Format Sankofa Standard (modèle Nzinga)
# Chapter titles (jaune, haut) + Subtitles (blanc, bas) + VO
set -e

CLIPS=/home/tars/sankofa/amanirenas/work_v2
WORK=/home/tars/sankofa/amanirenas/work_v4
OUT=/home/tars/sankofa/amanirenas/output
AUDIO=/home/tars/sankofa/amanirenas/audio

mkdir -p "$WORK" "$OUT"

echo "=== Step 1: Concat clips (reuse V2 zoom-cropped) ==="
cat > "$WORK/concat.txt" << EOF
file '$CLIPS/v01.mp4'
file '$CLIPS/v02.mp4'
file '$CLIPS/v03.mp4'
file '$CLIPS/v04.mp4'
file '$CLIPS/v05.mp4'
file '$CLIPS/v06.mp4'
file '$CLIPS/v07.mp4'
file '$CLIPS/v08.mp4'
file '$CLIPS/v09.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i "$WORK/concat.txt" -c copy "$WORK/video.mp4" 2>/dev/null
DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$WORK/video.mp4")
echo "Video: ${DUR}s"

echo "=== Step 2: Audio (VO + fade) ==="
ffmpeg -y -i "$AUDIO/vo_amani.mp3" \
  -af "adelay=500|500,apad=pad_dur=2,afade=t=out:st=79:d=2" \
  -t "$DUR" -c:a aac -b:a 128k -ar 44100 -ac 2 "$WORK/audio.m4a" 2>/dev/null
echo "Audio done"

echo "=== Step 3: Mux video+audio ==="
ffmpeg -y -i "$WORK/video.mp4" -i "$WORK/audio.m4a" \
  -c:v copy -c:a copy -shortest "$WORK/base.mp4" 2>/dev/null
echo "Mux done"

echo "=== Step 4: Burn ASS subtitles (chapters + subs) ==="
ffmpeg -y -i "$WORK/base.mp4" \
  -vf "subtitles=/home/tars/sankofa/amanirenas/amanirenas_v4.ass" \
  -c:v libx264 -preset medium -crf 20 \
  -c:a copy \
  "$OUT/amanirenas_short_v4.mp4" 2>/dev/null

echo "=== DONE ==="
ls -la "$OUT/amanirenas_short_v4.mp4"
ffprobe -v quiet -show_entries stream=width,height -show_entries format=duration -of csv "$OUT/amanirenas_short_v4.mp4"
