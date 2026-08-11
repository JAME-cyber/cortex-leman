# xAI TTS — Voice Provider for Video Production

xAI's TTS API as an alternative to Edge TTS for video voiceover generation. Includes the voice-swap technique for replacing audio in existing video projects without re-rendering visuals.

## API Reference

**Endpoint**: `POST https://api.x.ai/v1/tts`

**Headers**:
```
Authorization: Bearer xai-...
Content-Type: application/json
```

**Payload**:
```json
{
  "text": "Message à synthétiser",
  "voice_id": "eve",
  "language": "fr"
}
```

**Response**: Binary MP3 (MPEG layer III, 128 kbps, 24 kHz, Mono).

### Known Parameters

| Param | Type | Values | Notes |
|-------|------|--------|-------|
| `text` | string | any | Max ~5000 chars tested |
| `voice_id` | string | `"eve"` | Only voice confirmed working (beta) |
| `language` | string | `"fr"`, `"en"` | ISO 639-1 code |

### Cost Model

- ~$0.10 / 1,000 characters (beta pricing)
- Edge TTS comparison: $0 (free)
- Typical 30s ad voiceover: 6 segments × ~40 chars = ~240 chars → **~$0.024 total**
- Typical 90s explainer: ~1500 chars → **~$0.15**

### Quality vs Edge TTS

| Aspect | Edge TTS (FabriceNeural) | xAI TTS (Eve) |
|--------|--------------------------|---------------|
| Cost | Free | ~$0.10/1K chars |
| Naturalness | Good, slightly robotic | More natural intonation |
| Speech rate | Configurable via `rate` param | Fixed (no rate control in beta) |
| Voices | 4+ FR voices (M/F) | 1 confirmed (`eve`, female) |
| Latency | ~1-2s per clip | ~2-3s per clip |
| French quality | fr-CH accents available | Standard FR (no CH variant) |

## Voice Swap Technique

### Problem

You have a finished video (e.g. a Hyperframes/Remotion composition) with TTS audio baked into specific timestamps. You want to swap the voice provider without re-doing the visual edit.

### Solution

Most composition frameworks (Hyperframes, Remotion) reference audio files by path in their HTML/JSX timeline. The timing is defined in the composition metadata, NOT encoded in the audio files. So you can:

1. **Locate the audio clips** (usually `.wav` files in an `audio/` directory)
2. **Backup the originals** (rename to `_originals/`)
3. **Generate new clips** with the same text, same audio spec (sample rate, channels, normalization)
4. **Re-render** the composition — it picks up the new files automatically

### Step-by-step (Hyperframes example)

#### 1. Find the VO script and timing

Look in the project for:
- `audio/vo-script.txt` — text per scene
- `gen_vo.py` — generation script with Edge TTS voice config
- `index.html` — `<audio>` tags with `data-start` and `data-duration` attributes

```html
<!-- Example: Hyperframes audio timeline -->
<audio id="vo-1" src="audio/vo-1.wav" data-start="0.4" data-duration="1.66">
<audio id="vo-2" src="audio/vo-2.wav" data-start="5.4" data-duration="2.66">
```

The `data-start` and `data-duration` define when each clip plays. As long as new clips fit within their time windows, the swap works.

#### 2. Generate replacement clips

```python
import json, subprocess, urllib.request
from pathlib import Path

API_KEY = os.environ["XAI_API_KEY"]
API_URL = "https://api.x.ai/v1/tts"
OUT = Path("audio")

CLIPS = {
    "vo-1.wav": "Que faire de tout ça ?",
    "vo-2.wav": "On trie, on donne, on recycle.",
    # ... same text as original gen_vo.py
}

def synth_xai(text):
    payload = json.dumps({"text": text, "voice_id": "eve", "language": "fr"}).encode()
    req = urllib.request.Request(API_URL, data=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()

def to_wav_normalized(mp3_bytes, out_path):
    """Same spec as original: 24kHz mono PCM16 + loudnorm."""
    tmp = Path("tmp.mp3")
    tmp.write_bytes(mp3_bytes)
    subprocess.run([
        "ffmpeg", "-y", "-i", str(tmp),
        "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le",
        "-af", "loudnorm=I=-20:LRA=7:TP=-2",
        str(out_path)
    ], capture_output=True, check=True)

# Backup originals
backup = OUT / "_originals"
backup.mkdir(exist_ok=True)
for f in CLIPS:
    if (OUT / f).exists():
        (OUT / f).rename(backup / f)

# Generate new clips
for fname, text in CLIPS.items():
    to_wav_normalized(synth_xai(text), OUT / fname)
```

#### 3. Verify timing fit

Compare new clip durations against the composition's time windows:

| Clip | Start | Window width | New duration | Fits? |
|------|-------|-------------|-------------|-------|
| vo-1 | 0.4s | 5.0s | 1.10s | ✅ |
| vo-2 | 5.4s | 4.0s | 2.11s | ✅ |
| ... | ... | ... | ... | ... |

If a clip is too long, trim text or use `atempo` ffmpeg filter to speed up slightly.

#### 4. Re-render

```bash
cd /path/to/hyperframes/project
npx hyperframes render . -o renders/output-xai.mp4 -f 24 -q standard
```

The composition reads the new `.wav` files — no HTML/JSX changes needed.

### Pitfalls

- **`cat` on MP3 looks like an error**: Binary MP3 data read as text can produce misleading "Incorrect API key" messages. Always check HTTP status first, then `file output.mp3` — never `cat`.
- **Rate control**: Edge TTS supports `rate="+25%"` to fit text into tight windows. xAI beta has no rate param. If clips overflow their window, shorten the text or apply `atempo` in ffmpeg post-processing.
- **Accent mismatch**: `fr-CH-FabriceNeural` (Swiss French) → `eve` (standard FR). If the local accent matters for the brand, Edge TTS fr-CH voices are the better choice.
- **loudnorm is critical**: Without matching the original's loudness normalization (`I=-20:LRA=7:TP=-2`), new clips will sound quieter/louder than the music bed, breaking the mix.
- **Backup before replacing**: Always move originals to `_originals/` — never overwrite directly. Allows instant rollback.
- **Hyperframes music ducking**: The composition's GSAP timeline ducks music volume during VO segments. New clips must fit within the same `[start, end]` windows or the ducking won't cover them fully.

## Real-World Measurements (Darkom-Débarras, July 2026)

Voice swap: `fr-CH-FabriceNeural` (Edge TTS, male Swiss FR) → `eve` (xAI, female standard FR).

### Duration comparison (6 clips, 30s vertical ad)

| Clip | Text | Edge TTS | xAI Eve | Delta |
|------|------|----------|---------|-------|
| vo-1 | Que faire de tout ça ? | 1.66s | 1.10s | -34% |
| vo-2 | On trie, on donne, on recycle. | 2.66s | 2.11s | -21% |
| vo-3 | On vide. Vous respirez. | 2.78s | 1.51s | -46% |
| vo-4 | Intervention rapide en Haute-Savoie. | 2.33s | 2.04s | -12% |
| vo-5 | Libérez votre espace, simplifiez votre vie. | 2.93s | 2.62s | -11% |
| vo-6 | Devis gratuit en trente secondes. | 2.21s | 2.11s | -5% |

**Key takeaway**: Eve speaks ~20% faster than FabriceNeural at default rate. This is generally favorable — clips leave more breathing room within their time windows. But if you need the voice to fill a window more completely, consider adding a beat of silence before/after rather than padding text.

### Render performance

- Hyperframes render on 2-core / 4GB RAM machine: **~23 minutes** for a 30s composition with 5 video clips + 7 audio tracks
- Output file size increased: 8.8MB (Edge) → 25MB (xAI). Likely due to audio bitrate differences in the muxing step, not video quality change.
- GSAP music ducking worked perfectly with shorter clips — no adjustments needed to the timeline

### Gender mismatch consideration

Original FabriceNeural was **male** (Swiss French). Eve is **female** (standard French). For local Haute-Savoie brands where a masculine voice matters, Edge TTS fr-CH male voices remain the better choice. Always confirm with the user before swapping gender — it changes the brand feel.

## Related

- **SocialPulse Voice Agent**: `cortex-leman-business-generator/references/socialpulse-voice-agent-xai-tts.md` — xAI TTS for WhatsApp/Instagram voice messages (PitcherV2 integration, AI Act compliance, text cleaning for TTS)
- **Edge TTS generation script**: `scripts/generate_video.py` in this skill
- **OpenMontage**: `references/openmontage-production.md` — for multi-scene videos with cloud TTS
