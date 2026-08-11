# Edge TTS — Voice Discovery & Pitfalls

## Discovery Command

```python
import asyncio, edge_tts

async def list_voices():
    voices = await edge_tts.list_voices()
    fr = [v for v in voices if v['Locale'].startswith('fr')]
    for v in fr:
        print(f"{v['ShortName']:35s} {v['Gender']:8s} {v['FriendlyName']}")

asyncio.run(list_voices())
```

## French Voices (as of July 2026)

| ShortName | Gender | Locale |
|-----------|--------|--------|
| fr-FR-DeniseNeural | Female | France |
| fr-FR-EloiseNeural | Female | France |
| fr-FR-HenriNeural | Male | France |
| fr-FR-VivienneMultilingualNeural | Female | France |
| fr-FR-RemyMultilingualNeural | Male | France |
| **fr-CH-ArianeNeural** | **Female** | **Switzerland** |
| **fr-CH-FabriceNeural** | **Male** | **Switzerland** |
| fr-CA-SylvieNeural | Female | Canada |
| fr-CA-AntoineNeural | Male | Canada |
| fr-BE-CharlineNeural | Female | Belgium |

## Common Error

```
edge_tts.exceptions.NoAudioReceived: No audio was received.
Please verify that your parameters are correct.
```

**Cause**: Invalid voice ShortName (e.g. made-up `fr-FF-HenriettaNeural`).

**Fix**: Run `list_voices()` to get exact ShortNames. They follow the pattern `{lang}-{REGION}-{Name}Neural`.

## TTS Implementation Pattern

```python
import io, edge_tts

async def text_to_speech(text: str, voice: str = "fr-CH-ArianeNeural") -> bytes:
    clean = text.replace("*", "").replace("#", "").replace("|", "")
    communicate = edge_tts.Communicate(clean, voice)
    audio = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.write(chunk["data"])
    return audio.getvalue()
```

## Quality Notes

- 48 kbps, 24 kHz, monaural MP3 output
- ~45KB for a 2-sentence response (fast to stream)
- Swiss FR voices sound natural for FR-CH business contexts
- No SSML support in the basic Communicate API (rate/volume adjustments via `rate` and `volume` params)
