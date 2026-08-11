# FFmpeg Ken Burns / Zoom Pan Pitfalls

Lessons from 3 failed builds producing vertical (1080×1920) Ken Burns segments from large AI-generated source images (7MB+ PNGs, 1530×2720).

## Problem 1: `zoompan` is catastrophically slow on large source images

**Symptom**: build hangs 4+ minutes on a single Ken Burns segment (17.6s × 24fps = 422 frames), never completing within timeout.

**Root cause**: `zoompan` re-processes the entire input image for each output frame. A 1530×2720 source × 422 frames = massive per-pixel computation. Designed for small thumbnail sequences, not multi-megapixel stills.

**Fix — Pre-resize + `crop` filter (10x faster)**:

```python
from PIL import Image

# Step 1: Pre-resize to overscaled target (adds ~8% margin for pan room)
overscale = 1.08
target_w = int(1080 * overscale)  # 1166
target_h = int(1920 * overscale)  # 2073
src_resized = src.resize((target_w, target_h), Image.LANCZOS)
src_resized.save(tmp_scaled, "PNG")

# Step 2: ffmpeg crop with time-based expressions on the SMALL pre-resized image
# crop filter uses 't' (seconds) — NOT 'on' (frame number, zoompan-only)
crop_expr = (
    f"crop=w=1080:h=1920:"
    f"x='(iw-1080)/2*(1-t/{dur:.1f})':"
    f"y='(ih-1920)/2*(1-t/{dur:.1f})'"
)
```

```bash
ffmpeg -y -loop 1 -framerate 24 -t 17.6 -i _kb_scaled.png \
  -vf "crop=w=1080:h=1920:x='(iw-1080)/2*(1-t/17.6)':y='(ih-1920)/2*(1-t/17.6)',format=yuv420p" \
  -c:v libx264 -preset ultrafast -crf 20 -pix_fmt yuv420p -r 24 output.mp4
```

**Why it works**: Source pre-resized to ~1166×2073 (2.4MB vs 7MB), `crop` operates cheaply per-frame since it just shifts a crop window — no pixel resampling.

## Problem 2: `crop` vs `zoompan` variable names

| Variable | Works in `crop`? | Works in `zoompan`? | Meaning |
|----------|------------------|---------------------|----------|
| `t` | YES | no | Time in seconds |
| `n` | YES | no | Frame number (0-indexed) |
| `on` | NO | YES | Output frame number (zoompan-specific) |
| `iw` / `ih` | YES | YES | Input dimensions |

Using `on` in a `crop` expression silently fails — ffmpeg returns NaN and the segment falls back to static scale (no zoom/pan animation). Use `t` or `n` instead.

## Problem 3: Caption text encoding corruption

JSON with accented French text in Python scripts can inject random CJK characters (e.g. `吞` in `armées吞érables`) if the source file has mixed encoding. This survives into the final video.

**Fix**: Validate after writing caption JSON:
```python
import json, re
with open(path) as f:
    data = json.load(f)
for item in data:
    if re.search(r'[\u3000-\u9fff]', item['caption']):
        print(f"WARN: CJK char in caption: {item['id']}")
```

## Problem 4: zoompan STILL times out even on pre-scaled 1080×1920 images

**Symptom** (Aug 9, 2026): Pre-scaled source to exactly 1080×1920 via PIL, then ran zoompan with `z='min(zoom+0.0008,1.12)':d=422`. Timed out after 60s. Even at target resolution, zoompan's per-frame full-image reprocessing is too slow for 400+ frame segments.

**Fix**: DON'T use `zoompan` at all for long segments. Two reliable alternatives:

1. **Use the `crop` filter** (see Problem 1 above) — pre-resize to ~1166×2073, then crop-pan. Tested at ~8s per segment.

2. **Use `stream_loop` on a video clip instead** (fastest, ~2s per segment):
```bash
ffmpeg -y -stream_loop -1 -i seedance_clip.mp4 \
  -t 17.6 \
  -vf "scale=1080:1920:flags=lanczos,format=yuv420p" \
  -c:v libx264 -preset ultrafast -crf 20 -pix_fmt yuv420p -r 24 output.mp4
```
This loops a 5s Seedance clip to fill any duration. When you have video clips available, always prefer this over static images — it's faster AND looks more professional.

## Problem 5: Watermark overlay invisible — RGBA alpha too low

**Symptom**: `watermark_sankofa.png` (1080×1920 RGBA) overlaid via `[0:v][2:v]overlay=x=W-w-20:y=H-h-20` — QA showed watermark completely invisible.

**Root cause**: Alpha channel max value was 41/255 (16% opacity). The overlay filter respects alpha, so 16% on a 79×79px logo in the corner of a 1080×1920 frame is imperceptible.

**Fix**: Boost alpha via numpy before build:
```python
from PIL import Image
import numpy as np
arr = np.array(Image.open('watermark.png'))
alpha = arr[:,:,3]
arr[:,:,3] = np.where(alpha > 0, np.minimum(alpha * 4, 150), 0).astype(np.uint8)
Image.fromarray(arr, 'RGBA').save('watermark_boosted.png')
```
Target alpha ~150 (59% opacity) for corner watermarks — visible in QA without being intrusive.

## Verified pipeline (Aug 2026)

```
Source image (7MB, 1530×2720)
  → PIL pre-resize to 1166×2073 (2.4MB)
  → ffmpeg crop with t-based expressions (ultrafast preset)
  → 1080×1920 H.264 segment in ~8s (vs 4min+ with zoompan)
```

### Preferred: video clips over static images
When Seedance/Hailuo video clips are available, ALWAYS use `stream_loop` instead of Ken Burns:
- 2s build time vs 8s+ for crop vs 60s+ timeout for zoompan
- Dynamic motion looks more professional than Ken Burns pan
- Same concat/audio/watermark pipeline works unchanged
