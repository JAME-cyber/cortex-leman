---
name: cortex-leman-video-brief
version: 1.0.0
description: Transform Brief RGPD-IA into 60-90sec video (Edge TTS FR, stock or motion-gfx clips, subtitles). Includes xAI TTS voice-swap technique with real-world measurements (Darkom 30s ad, Edge→xAI render proven July 2026).
category: cortex-leman
---

# Video Brief Generator

Turns a text brief (e.g. Brief RGPD-IA Hebdo) into a short video ready for social media.

## When to use
- After Brief RGPD-IA cron produces text content
- When user asks to "make a video" from a brief or text
- As part of the weekly content pipeline

## Requirements
- `edge-tts` (installed)
- `ffmpeg` (installed)
- `Pillow` (installed)
- `Pexels API key` (optional — if `PEXELS_API_KEY` env var set, uses stock footage)
- `moviepy` (NOT needed — v1.1 uses FFmpeg directly for fast render)

## Pipeline

1. **Input**: Text brief (markdown or plain text, ~1500 chars)
2. **Script cleanup**: Strip markdown, extract key talking points
3. **Voice**: Edge TTS with `fr-CH-ArianeNeural` (female) or `fr-CH-FabriceNeural` (male)
4. **Visual**: Two modes:
   - **Pexels mode** (if API key set): search stock footage per paragraph
   - **Motion-gfx mode** (default): colored backgrounds + text overlays, brand colors
5. **Subtitles**: Burned-in from Edge TTS timestamps, white on semi-transparent black
6. **Compose**: MoviePy montage → MP4 9:16 (portrait for X/IG Reels)
7. **Output**: `~/.hermes/output/video-brief-{date}.mp4`

## Script

Run the generation script (FFmpeg-based, fast render):
```bash
python3 ~/.hermes/skills/cortex-leman-video-brief/scripts/generate_video.py \
  --text "Brief text here" \
  --output /path/to/output.mp4 \
  --voice fr-CH-ArianeNeural \
  --aspect 9:16
```

Or pipe from file:
```bash
python3 ~/.hermes/skills/cortex-leman-video-brief/scripts/generate_video.py \
  --file brief.md \
  --output video.mp4
```

## Voices available (FR)

### Edge TTS (free, default)
- `fr-CH-ArianeNeural` — Female, Swiss French (default)
- `fr-CH-FabriceNeural` — Male, Swiss French
- `fr-FR-DeniseNeural` — Female, France
- `fr-FR-HenriNeural` — Male, France

### xAI TTS (paid, higher quality)
- `eve` — Female, natural intonation (beta — only voice confirmed)
- Language param: `fr` or `en` (ISO 639-1)
- Endpoint: `POST https://api.x.ai/v1/tts` (returns MP3 binary)
- Cost: ~$0.10/1K chars (vs Edge TTS at $0)
- Use when: Edge TTS sounds too robotic, client needs premium voice quality, or A/B testing voice conversion rates
- See `references/xai-tts-voice-swap.md` for full integration + voice replacement technique

## Aspects
- `9:16` — Portrait (X/IG Reels/TikTok) — default
- `16:9` — Landscape (YouTube)
- `1:1` — Square

## OpenMontage — When You Need More

For multi-scene videos with AI-generated visuals, music, or real footage, use **OpenMontage** (installed at `/home/tars/OpenMontage/`). It's a full agent-driven video production system. See `references/openmontage-production.md` for setup, zero-key path, low-RAM workaround, and pipeline selection.

## xAI TTS — Premium Voice Alternative

For higher-quality voiceover than Edge TTS, xAI TTS (`eve` voice) produces more natural intonation at ~$0.10/1K chars. See `references/xai-tts-voice-swap.md` for API reference, quality comparison, and the voice-swap technique (replace TTS audio in existing Hyperframes/Remotion compositions without re-editing visuals).

## Edge TTS Voice Discovery

Voice names are easy to get wrong (e.g. `fr-FF-HenriettaNeural` doesn't exist — the correct format is `fr-FR-` not `fr-FF-`). Always enumerate available voices programmatically before hardcoding a name:

```python
import asyncio, edge_tts

async def list_voices():
    voices = await edge_tts.list_voices()
    fr = [v for v in voices if v['Locale'].startswith('fr')]
    for v in fr:
        print(f"{v['ShortName']:30s} {v['Gender']:8s} {v['FriendlyName']}")

asyncio.run(list_voices())
```

**French voices available (July 2026):**
- `fr-CH-ArianeNeural` / `fr-CH-FabriceNeural` — Swiss French (default for Cortex Leman)
- `fr-FR-VivienneMultilingualNeural` / `fr-FR-RemyMultilingualNeural` — Multilingual
- `fr-FR-DeniseNeural` / `fr-FR-EloiseNeural` — France French
- `fr-FR-HenriNeural` — France French male
- `fr-CA-*` / `fr-BE-*` — Canadian / Belgian variants

## Voice Agent Architecture (STT → LLM → TTS)

For interactive voice agents (receptionniste, assistant téléphonique, etc.), see `references/voice-agent-architecture.md` for the full pipeline pattern with provider matrix, browser STT fallback, and FastAPI reference implementation.

## Pitfalls
- Edge TTS 7.x: uses `SentenceBoundary` not `WordBoundary`. Script handles both via `feed()`.
- Edge TTS timeout: default 30s, can hang on bad network. Script has timeout handling.
- **Edge TTS voice name format**: `fr-FF-` does NOT exist. Use `fr-FR-` (France) or `fr-CH-` (Switzerland). Always verify with `edge_tts.list_voices()` before hardcoding.
- **Edge TTS `NoAudioReceived` exception**: thrown when voice name is invalid. The error message says "verify parameters" — the parameter that's wrong is almost always the voice name.
- **Z.ai coding endpoint does NOT support STT** (audio transcription): calling `/audio/transcriptions` returns error 1211 "Unknown Model". Z.ai only provides LLM chat completions on the coding endpoint. For STT, use Groq Whisper (fast/cheap), browser Web Speech API (free), or local Whisper.
- FFmpeg subtitle burn-in: needs libass compiled in. Falls back to no-subtitles if missing.
- NumPy 2.x crash on old CPUs: pinned to `<2` in Hermes venv.
- If Pexels key missing, falls back to motion-gfx mode automatically (Pillow-generated frames).
- v1.1 uses FFmpeg concat+burn-in instead of MoviePy compositing — 10x faster render.
- **OpenMontage low-RAM crash:** Remotion's headless Chrome OOM-kills on <4GB RAM machines. Must use `--scale 0.5 --concurrency 1`. See `references/openmontage-production.md`.
