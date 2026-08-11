# Intro/Outro → Video Integration

How to integrate brand intros, outros, and watermarks with content videos: placement strategy, sync management, and ffmpeg patterns for each integration type.

Validated on Sankofa Nzinga v6 (intro prepend, long-form) and v7 (watermark + outro postpend, short-form) — July 2026.

## Placement Strategy — Short-Form vs Long-Form

| Format | Intro (5s) | Watermark | Outro (2.5s) |
|--------|-----------|-----------|--------------|
| **Short 9:16** (~2 min) | ❌ NO — kills the hook | ✅ Yes, during video | ✅ Yes, at end |
| **Long-form** (10-30 min) | ✅ Yes, at beginning | ✅ Yes | ✅ Yes |

**Why no intro on shorts:** The first 3 seconds are critical on YT Shorts/TikTok. A 5s logo animation = ~40% of viewers swipe before the content starts. Hook narrative must be immediate (0s).

## Pipeline A — Outro Postpend (Short-Form)

The outro goes at the END of the video. Use `concat` filter with both video and audio, same pattern as intro prepend but postpend.

### Step 1: Build main video (subs + BGM + watermark in one pass)

Everything is done in a single ffmpeg pass via `-filter_complex`:

```python
cmd = [
    "ffmpeg", "-y",
    "-i", str(video_audio),      # input 0: content (video + narration)
    "-i", str(bgm_path),         # input 1: background music
    "-i", str(watermark_path),   # input 2: watermark PNG (RGBA)
    "-filter_complex",
    # Watermark overlay FIRST, then subs burned in
    f"[0:v][2:v]overlay=x=W-w-20:y=H-h-20,subtitles='{ass_escaped}'[vout];"
    # BGM with fade
    f"[1:a]volume=-28dB,afade=t=in:st=0:d=1,afade=t=out:st={dur-2}:d=2[bgm];"
    f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]",
    "-map", "[vout]", "-map", "[aout]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k", "-shortest",
    "-pix_fmt", "yuv420p", "-r", "24",
    str(main_path)
]
```

**⚠️ CRITICAL:** `-vf` CANNOT be used when you have 2+ inputs (video + watermark PNG). It will fail with:
> *"Simple filtergraph was expected to have exactly 1 input and 1 output. However, it had 2 input(s)"*

Everything must go through `-filter_complex` with labeled streams.

### Step 2: Postpend outro via concat

```python
subprocess.run([
    "ffmpeg", "-y",
    "-i", str(main_path),       # input 0: main content
    "-i", str(outro_path),      # input 1: outro (video + stinger audio)
    "-filter_complex",
    "[0:v]fps=24,setsar=1[mainv];"
    "[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=24[outrov];"
    "[mainv][0:a][outrov][1:a]concat=n=2:v=1:a=1[vout][aout]",
    "-map", "[vout]", "-map", "[aout]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p", "-r", "24",
    str(final_path)
])
```

No subtitle offset needed (subs are already correct — they start at t=0 of the content, which is now t=0 of the final video since there's no intro).

### Step 3: Watermark creation (PIL)

```python
from PIL import Image
logo = Image.open(logo_path).convert("RGBA").resize((80, 80), Image.LANCZOS)
alpha = logo.split()[3].point(lambda a: int(a * 0.4))  # 40% opacity
logo.putalpha(alpha)
canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))  # transparent
canvas.paste(logo, (1080 - 100, 1920 - 100), logo)      # bottom-right
canvas.save("watermark.png")
```

## Pipeline B — Intro Prepend (Long-Form Only)

For long-form content (podcasts, deep-dives), the full 5s intro goes at the beginning.

### Step 1: Concat intro + content (video + audio together)

Use `concat` filter with **both** video and audio streams (`v=1:a=1`):

```python
subprocess.run([
    "ffmpeg", "-y",
    "-i", str(content_video),   # input 0: main content
    "-i", str(intro_video),     # input 1: intro
    "-filter_complex",
    "[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,"
    "fps=24[introv];"
    "[0:v]fps=24[mainv];"
    "[mainv][0:a][introv][1:a]concat=n=2:v=1:a=1[vout][aout]",
    "-map", "[vout]", "-map", "[aout]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p", "-r", "24",
    str(output)
])
```

### Step 2: Offset subtitles by intro duration

```python
intro_dur = get_dur(str(intro_path))
generate_srt(beats, srt_path, time_offset=intro_dur)
```

### Step 3: Delay BGM so it doesn't cover the stinger

```python
f"[1:a]volume=-28dB,adelay={int(intro_dur*1000)}|{int(intro_dur*1000)},"
f"afade=t=in:st={intro_dur}:d=1,afade=t=out:st={dur-2}:d=2[bgm];"
```

## Outro Signature — HTML/JS Animation Pattern

The outro uses the same Playwright frame-by-frame capture pipeline as the intro. Key differences:

| Aspect | Intro | Outro |
|--------|-------|-------|
| Duration | 5s | 2.5s |
| Content | Logo reveal + channel name + symbol animation | Ring draws (stroke-dasharray) + logo fade + title + tagline + channel sub |
| Placement | Beginning (long-form only) | End (all formats) |
| Stinger | Full stinger | Same stinger, trimmed to outro duration |

**Ring animation (stroke-dasharray):**

```javascript
const circ = 2 * Math.PI * radius;
ring.setAttribute('stroke-dasharray', circ);
ring.setAttribute('stroke-dashoffset', circ * (1 - easeOutCubic(t / 0.6)));
```

**Capture script:** `scripts/capture_brand_outro.py` (analogous to `scripts/capture_brand_intro.py`, DURATION=2.5).

## Build Pipeline Order (Short-Form with Outro)

```
[1/5] Captions (Playwright, omit_background=True) → cached PNGs
[2/5] Build segments (b-roll + caption overlay) → per-beat MP4s
[3/5] Concat segments → silent video
[4/5] Audio mux (TTS concat → AAC)
[5/5] Subs + BGM + Watermark (ONE pass via filter_complex)
[6/5] ★ POSTPEND OUTRO (concat v+a)
```

Output filename versioned (e.g., `nzinga_v7.mp4`) so prior versions are preserved.

## Pitfalls

1. **`-vf` with 2+ inputs** — fails with "expected 1 input, got 2". Use `-filter_complex` with labeled streams.
2. **`overlay=enable='1'=x=...`** — invalid syntax. For permanent overlay, omit `enable` entirely.
3. **`concat=a=0`** — silently drops audio. Always use `a=1` and map both audio streams.
4. **fps mismatch** — force `fps=24` (or target) on ALL inputs before concat or frames corrupt.
5. **BGM during stinger (long-form)** — always `adelay` BGM by intro duration.
6. **Subs during intro (long-form)** — always offset SRT timestamps by intro duration.
7. **Build script variable shuffle** — when modifying a complex build script, change ONE thing at a time. Multiple simultaneous changes cause variable permutation bugs (e.g., `video_audio` reassigned to wrong path) that take 3+ full builds to debug on slow CPUs.
