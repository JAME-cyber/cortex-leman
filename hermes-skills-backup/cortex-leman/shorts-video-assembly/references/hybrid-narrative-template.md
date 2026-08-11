# Hybrid Narrative — Real Footage + AI Anime (Dream vs Reality)

**Validated Aug 3, 2026** — basketball short "RISE — Le Grind" (9:16, ~33s).

## When to use

When you have **real footage that is visually static or "boring"** (e.g. Pilates/reformer conditioning clips, gym workouts, rehab exercises) but the narrative calls for **energy and aspiration**. Instead of forcing the footage to carry the video alone (flat) or replacing it entirely with AI clips (loses authenticity), create a **hybrid arc** where real footage and AI clips serve different narrative roles.

## The Dream-vs-Reality Arc

| Act | Source | Narrative Role | Duration |
|-----|--------|---------------|----------|
| 1. Hook / Dream | AI poster zoom-in (Seedream → ffmpeg zoompan) | "This is who he wants to be" | 3s |
| 2. Grind / Reality | Real footage, fast cuts 1.5s each, color graded | "This is what it actually takes" | ~9s (6 cuts) |
| 3. Dream building | AI anime clips (Hailuo I2V from poster) | "The dream starts to materialize" | ~10s (alternates with reality) |
| 4. Glory / Climax | AI anime clip (celebration/dunk) | "The payoff" | 5s |
| 5. Outro | Poster or text card | "VOILÀ COMMENT ON DEVIENT PRO" | 3s |

**Key insight**: interleave real and AI clips in Act 3 (real → anime → real → anime → real → anime). The alternation creates **rhythmic contrast** — the viewer's brain experiences the transition from grind to glory as a gradual shift, not an abrupt jump.

## Technical setup

### Poster → I2V reference pipeline
1. Generate anime poster with Seedream 5.0 Pro (identity-locked from user photo via Qwen-VL analysis)
2. Upload poster to catbox.moe → get URL
3. Use URL as `image_url` for Hailuo 2.3 Pro I2V clips (45cr each, ~90-150s/clip)
4. Submit all Hailuo tasks in parallel, then poll sequentially

### ElevenLabs VO override
Default project voice is Edge TTS (fr-CH-ArianeNeural). For shorts requiring **emotional weight**, use ElevenLabs via the TTS tool:
- Voice: Adam (`pNInz6obpgDQGcFmaJgB`), model `eleven_multilingual_v2`
- Key location: project `.env` file (e.g. `~/crypto-project/.env`), NOT Hermes config
- ElevenLabs VO is ~30% shorter than Edge TTS for same text (more natural pacing, fewer pauses)

### Color grading for real footage
Apply uniform dramatic grading to ALL real footage segments to bridge the visual gap with anime clips:
```
-vf eq=gamma=1.3:brightness=0.05:saturation=1.35:contrast=1.15
```
The high saturation (1.35) pushes real footage toward the vibrant anime palette, reducing the clash.

## ⚠ Pitfall: ffmpeg `-shortest` truncates video to VO length

When merging video (concat of segments) + audio (VO + ambient mix), **`-shortest` cuts the output to the SHORTEST stream**. If the VO is 14s but the video is 33s, the output will be 14s — silently losing 19s of footage.

**Symptoms**: final video much shorter than expected (e.g. 13.7s instead of 33s).

**Fix**: Remove `-shortest` entirely. Use `amix=inputs=2:duration=longest` in the audio mix filter to extend the audio to the longest input. Add `atrim=duration=<video_len>` on the ambient track to pad it.

```python
# ❌ WRONG — cuts to shortest stream (VO)
ffmpeg -i video.mp4 -i audio.wav -shortest output.mp4

# ✅ CORRECT — audio extends to video length
ffmpeg -i video.mp4 -i audio.wav \
  -c:v libx264 -crf 23 \
  -c:a aac -b:a 128k \
  output.mp4  # no -shortest
```

**Audio mix pattern** (VO + ambient, extend to video duration):
```python
"-filter_complex",
"[0:a]volume=2.0[vo];[1:a]volume=0.15,atrim=duration=30[amb];"
"[vo][amb]amix=inputs=2:duration=longest:dropout_transition=0[a]"
```

## ⚠ Pitfall: mixed framerate breaks concat

Real footage clips often have different framerates (30, 60, 25fps). Concatenating them directly produces stuttering or corruption. **Fix**: normalize ALL segments to 30fps BEFORE concat via `-vf fps=30 -r 30` in each segment's ffmpeg command. Do this at the segment extraction stage, not at concat time.

## Budget breakdown (reference)

| Item | Cost |
|------|------|
| Poster (Seedream 5.0 Pro 9:16) | ~28cr |
| 3 anime clips (Hailuo 2.3 Pro 6s 768p × 3) | 135cr |
| VO (ElevenLabs) | ~$0.02 (external, not KIE) |
| Build (ffmpeg, 0 credits) | 0cr |
| **Total** | **~163cr (~$0.82)** |

## Applicability

This pattern generalizes beyond basketball to ANY project where:
- User provides real footage that is authentic but visually static
- The narrative needs aspiration/energy beyond what the footage shows
- A poster or character design already exists as a style reference

Examples: fitness journeys, cooking "before mastery" arcs, student-to-professional transitions, rehab/recovery stories.
