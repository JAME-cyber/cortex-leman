# SocialPulse Voice Agent — xAI TTS Integration

## Overview

Wraps xAI TTS API to convert PitcherV2 text responses into audio for WhatsApp/Instagram voice messages. Integrated between `pitcher.respond()` and message delivery.

## xAI TTS API Reference

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

**Response**: Binary MP3 data (MPEG layer III, 128 kbps, 24 kHz, Mono).

### Known Parameters

| Param | Type | Values | Notes |
|-------|------|--------|-------|
| `text` | string | any | Max ~5000 chars tested |
| `voice_id` | string | `"eve"` | Only voice confirmed working (beta) |
| `language` | string | `"fr"`, `"en"` | ISO 639-1 code |

### Cost Model

- ~$0.10 / 1,000 characters (beta pricing)
- Typical SocialPulse message: 250-350 chars → $0.025-$0.035
- Average: **$0.028/message**

### Pitfall: cat binary MP3 as error

When testing with `cat response | grep`, binary MP3 data can look like an error message ("Incorrect API key provided" appeared in one test because `cat hello.mp3` read binary bytes as text). Always check HTTP status code first, then inspect the file with `file output.mp3` — not `cat`.

## Integration Pattern

```
PitcherV2.respond() → message texte
    ↓ VoiceAgent.speak_pitcher_response()
    ↓ 1. Strip RGPD footer (redondant en voix)
    ↓ 2. Strip markdown/emojis (ne se vocalisent pas)
    ↓ 3. Add disclosure prefix (AI Act Art. 50)
    ↓ 4. Call xAI TTS API
    → .mp3 file
```

### Text Cleaning for TTS

Essential transformations before sending to TTS:

1. **Strip emojis** — they produce garbage audio or silence
2. **Strip markdown** — `**bold**`, `_italic_`, `~~strike~~`, `` `code` ``
3. **Strip markdown links** — keep text, drop URL: `[site](https://...) → site`
4. **Convert bullets** — `• text` → `. text` (natural pause)
5. **Collapse whitespace** — multiple newlines/spaces → single
6. **Strip RGPD footer** — `_SocialPulse — STOP..._` stays in written transcript only

### RGPD Footer Stripping

The footer `_SocialPulse — STOP pour ne plus être contacté_` is stripped from voice payload because:
- Redundant with AI Act disclosure prefix
- Saves ~3s of synthesis time
- The written transcript accompanying the voice message retains it

Regex patterns:
```python
# Italic footer
re.sub(r"\n*_SocialPulse — STOP.*_\s*$", "", text)
# Inline footer
re.sub(r"\n*SocialPulse · STOP.*$", "", text)
```

## Compliance: Voice Messages

| Obligation | Implementation | Reference |
|------------|---------------|-----------|
| **AI Act Art. 50** (transparency) | Prefix `"Message de SocialPulse. "` before every voice message | Prospect must know they're hearing an AI |
| **RGPD art. 6(1)(f)** | Inherited from pipeline legal basis (intérêt légitime B2B) | Same as text channel |
| **RGPD art. 9** (biometric) | N/A — no voice recognition, only synthesis | No STT yet |
| **CPCE L.34-5** (opt-out B2B) | Inherited from `legal_classifier.py` PM/EI gates | Voice follows same channel rules |
| **EI without consent** | Blocked — voice inherits PM/EI/NUANCED classification | `can_sms=False` in LegalClassification |

### AI Act Disclosure Prefix

```python
DISCLOSURE = "Message de SocialPulse. "
# Added automatically when disclose=True (default)
```

This satisfies the AI Act Art. 50 requirement that users must be informed they are interacting with an AI system. The prefix is short, professional, and does not disrupt the message flow.

## Architecture

```
agents/voice_agent.py        # VoiceAgent class — wrapper xAI TTS
    speak(text, lead_slug)              # → MP3 file
    speak_pitcher_response(text, lead)  # → strips RGPD, cleans, synthesizes
    _clean_for_tts(text)                # → strips markdown/emojis
    _slug(name)                         # → filename-safe slug

tests/test_voice_agent.py     # 11 tests (10 unit + 1 integration)
```

### Dependencies

**Zero external dependencies.** Uses only Python stdlib (`urllib`, `json`, `re`, `os`, `time`, `pathlib`). No `requests`, no `aiohttp` — keeps the SocialPulse pipeline dependency-free.

### Error Handling

- HTTP 429/500/502/503 → retry with exponential backoff (2 attempts max)
- Other HTTP errors → return error dict immediately
- Timeout: 15s per attempt
- All returns include `success: bool` + `path` or `error`

## Future: STT Round-Trip

Next phase for full voice conversation:

```
Audio prospect (WhatsApp) → Whisper STT → PitcherV2 → xAI TTS → Audio agent
```

Not yet implemented. Whisper skill exists in the library (`mlops/whisper`).
