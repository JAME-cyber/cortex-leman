# TikTok/Reels Pacing Rules + Build QA Protocol

> Validated Aug 3, 2026 on basketball short (22s, 9:16). QA vision scored V1 at 6.5/10
> with specific failures: static clips, tiny subtitles, slow pacing, jarring transitions.

## Pacing Rules (TikTok/Reels-native)

| Rule | Value | Rationale |
|------|-------|-----------|
| **Cut length** | ≤ 2s per segment | TikTok scroll-speed; static shots >2s = scroll trigger |
| **Subtitle font size** | 96pt+ at 1080×1920 | 72pt fails mobile readability (QA: 6/10) |
| **Subtitle position** | MarginV 120-160px | Below center, above TikTok UI overlay |
| **Total duration** | 20-30s | Sweet spot for completion rate |
| **Hook** | First 2s = highest energy frame | Poster/title card with motion (zoom-in, glow) |
| **Transition bridging** | Cross-dissolve 0.3s between AI poster → raw footage | Hard cut from stylized to raw = jarring (QA: 4/10 flow) |

## Visual QA Protocol (MANDATORY before delivery)

### Step 1: Contact sheet extraction
```bash
ffmpeg -y -i output.mp4 -vf "
  select='eq(n\,30)+eq(n\,180)+eq(n\,360)+eq(n\,540)+eq(n\,630)',
  scale=270:480,
  tile=3x2
" -frames:v 1 /tmp/qa_contact_sheet.jpg
```

### Step 2: Vision model scoring
Send contact sheet to Gemini 2.5 Flash (or GPT-5.6) via OpenRouter with prompt:
```
Rate this short 1-10 on: (1) visual flow, (2) intro impact, (3) clip quality/variety,
(4) subtitle readability, (5) TikTok readiness. List issues. Is this publishable?
```

### Step 3: Go/no-go threshold
- **≥ 8/10 overall**: publishable, deliver to user
- **6-7/10**: deliver V1 but flag specific fixes for V2
- **< 6/10**: do NOT deliver, iterate on the weakest scored dimension first

### Step 4: Frame-by-frame clip analysis BEFORE editing
Before committing to an edit concept, extract 2 frames per source clip (25% + 75% timestamps)
and analyze with vision model. Adapt the concept to the ACTUAL content, not the assumed content.
**Validated lesson**: clips described as "basketball training" were actually Pilates/reformer
footage → concept pivoted from "dunk highlight reel" to "the grind / journey" narrative.

## ffmpeg Build Pitfalls (Shorts Assembly)

### P1: amix filter → MP3 output fails
**Error**: `Invalid audio stream. Exactly one MP3 audio stream is required` when mixing VO + ambient via `amix` and outputting to `.mp3`.

**Cause**: `amix` outputs PCM; ffmpeg cannot mux PCM into MP3 container directly.

**Fix**: Output to `.wav` (pcm_s16le) for intermediate audio, then encode to AAC in the final merge:
```bash
# WRONG:
ffmpeg -i vo.mp3 -i ambient.wav -filter_complex "[0:a]...[1:a]...amix=...[aout]" -map "[aout]" out.mp3  # FAILS

# RIGHT:
ffmpeg -i vo.mp3 -i ambient.wav -filter_complex "[0:a]...[1:a]...amix=...[aout]" -map "[aout]" -c:a pcm_s16le out.wav  # OK
# Then in final merge:
ffmpeg -i video.mp4 -i out.wav ... -c:a aac -b:a 128k final.mp4
```

### P2: ASS subtitles require ABSOLUTE path in ffmpeg filter
**Error**: `[Parsed_subtitles_0] Unable to open subs.ass` even when the file exists in CWD.

**Fix**: Always use absolute path in the `subtitles=` filter:
```bash
# WRONG:
-vf "subtitles=tmp/subs.ass"

# RIGHT:
-vf "subtitles=/home/tars/project/tmp/subs.ass"
```

### P3: Poster zoompan intro technique
Static poster → 4s animated intro with slow zoom-in + fade:
```bash
ffmpeg -y -i poster.png -vf "
  scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,
  zoompan=z='min(1.15-0.04*on/120\,1.0)':d=120:s=1080x1920:fps=30,
  fade=t=in:st=0:d=0.5,fade=t=out:st=3.3:d=0.5,format=yuv420p
" -c:v libx264 -preset medium -crf 20 -t 4 -an poster_intro.mp4
```
- `zoompan z='min(1.15-0.04*on/120\,1.0)'`: starts at 1.15x zoom, linearly decreases to 1.0x over 120 frames (4s at 30fps)
- `\,` escapes the comma inside zoompan expression
- `d=120`: duration in frames (must match fps × seconds)
- Add `eq=gamma=1.15:brightness=0.05:saturation=1.1` for clips that are too dark

### P4: Brightness correction for inconsistent source clips
When raw footage clips are darker than the AI intro/outro:
```bash
ffmpeg -y -i input.mp4 -vf "eq=gamma=1.15:brightness=0.05:saturation=1.1" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -an output.mp4
```
Apply BEFORE concatenation so all segments have consistent brightness.
