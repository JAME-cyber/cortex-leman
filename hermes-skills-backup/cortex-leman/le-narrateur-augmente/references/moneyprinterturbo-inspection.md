# MoneyPrinterTurbo — Architecture Inspection (June 2026)

**Repo:** https://github.com/harry0703/MoneyPrinterTurbo
**Stats:** 81k stars · MIT · v1.2.9 · Python 3.11-3.12 · 591 commits

## 6-Step Pipeline (Text → Video)

1. **Script** — LLM generates narration script from keyword/subject
2. **Terms** — LLM extracts 5 Pexels search terms from the script
3. **Audio** — Edge TTS converts script → MP3 + word-level timestamps
4. **Material** — Pexels/Pixabay API search → download matching stock clips
5. **Subtitle** — Edge timestamps → SRT (or faster-whisper for higher accuracy)
6. **Compose** — MoviePy 2.x assembles: clips + audio + subtitles + BGM → .mp4

## Architecture (MVC)

```
app/
  config/config.py        → TOML config loader (all keys, providers, flags)
  models/schema.py        → VideoParams, MaterialInfo (Pydantic)
  models/const.py         → Task state constants
  services/
    llm.py                → Script + terms generation (15+ providers via OpenAI SDK)
    material.py           → Pexels/Pixabay search+download, API key rotation
    voice.py              → Edge TTS (free), Azure TTS V2, Gemini, SiliconFlow, MiMo TTS
    subtitle.py           → Edge timestamps OR faster-whisper (beam_size=5, VAD)
    video.py              → MoviePy 2.x montage (clips, subs, BGM, transitions)
    task.py               → Orchestrator (script→terms→audio→material→compose)
    state.py              → Task state (in-memory dict or Redis)
    upload_post.py        → Cross-post TikTok/Instagram via Upload-Post API
  controllers/v1/         → FastAPI endpoints (/api/v1/videos/start, etc.)
  router.py               → Route aggregation
main.py                   → uvicorn entry (FastAPI ASGI)
webui/Main.py             → Streamlit UI (separate service)
```

## Key Techniques Worth Reusing

### API Key Rotation (thread-safe round-robin)
```python
_api_key_counter = 0
_api_key_lock = threading.Lock()

def get_api_key(cfg_key: str):
    api_keys = config.app.get(cfg_key)
    global _api_key_counter
    with _api_key_lock:
        _api_key_counter += 1
        return api_keys[_api_key_counter % len(api_keys)]
```

### Think-Block Stripping (reasoning model cleanup)
```python
_THINK_BLOCK_RE = re.compile(r"<think\b[^>]*>.*?</think>", re.IGNORECASE | re.DOTALL)
_UNCLOSED_THINK_BLOCK_RE = re.compile(r"<think\b[^>]*>.*$", re.IGNORECASE | re.DOTALL)
content = _THINK_BLOCK_RE.sub("", content)
content = _UNCLOSED_THINK_BLOCK_RE.sub("", content).strip()
```

### Source Deduplication (avoid visual repetition)
- Group clips by `source_file_path` (same stock video = multiple sub-clips)
- Pick longest clip per source as "primary"
- Shuffle primaries first, overflow clips as fallback

### TLS Verify Default (security-first)
- `tls_verify = True` by default in config
- Only `False` in explicit proxy/self-cert environments
- All Pexels/Pixabay downloads verify TLS

## FR-CH Voice Options (Edge TTS — FREE)

| Voice | Gender | Locale |
|-------|--------|--------|
| `fr-CH-ArianeNeural` | Female | Swiss French |
| `fr-CH-FabriceNeural` | Male | Swiss French |
| `fr-FR-DeniseNeural` | Female | French |
| `fr-FR-HenriNeural` | Male | French |
| `fr-CA-SylvieNeural` | Female | Canadian French |
| `fr-CA-ThierryNeural` | Male | Canadian French |

## Dependencies (from pyproject.toml)

- moviepy==2.2.1
- edge-tts==7.2.7 (FREE TTS)
- fastapi==0.136.3 + uvicorn==0.32.1
- openai==2.24.0 (for LLM calls, supports any provider)
- faster-whisper==1.1.0 (optional subtitle accuracy)
- streamlit==1.58.0 (Web UI)
- loguru==0.7.3 (logging)
- litellm==1.86.2 (100+ LLM providers)
- pydub==0.25.1 (audio processing)
- requests==2.33.1

## Limitations for Cortex Leman Use

- **No X/YouTube upload** — only TikTok/Instagram via Upload-Post
- **No branding hooks** — no logo/watermark overlay system
- **Generic stock footage** — Pexels/Pixabay content, not RGPD/IA branded
- **Chinese-centric defaults** — FR voices available but not default
- **Monolith architecture** — no skill/cron integration
- **Requires ffmpeg + ImageMagick** — heavyweight dependencies

## Adaptation Map for Cortex Leman

| MoneyPrinterTurbo Feature | Cortex Leman Adaptation |
|---|---|
| Pipeline orchestrator (task.py) | Hermes skill `cortex-leman-video-brief` |
| Edge TTS FR-CH | Use `fr-CH-ArianeNeural` / `fr-CH-FabriceNeural` (free) |
| Pexels search | Keep for generic clips, add branded overlay layer |
| MoviePy compose | Keep, add Cortex Leman logo watermark step |
| Upload-Post TikTok/IG | Replace with `xurl` for X + YouTube API |
| Key rotation pattern | Apply to Apify/Pexels keys in Hermes config |
| Think-block strip | Apply when using DeepSeek/reasoning models for scripts |

## MisterIA Content Marketing Pattern

The Brief RGPD-IA video pipeline follows MisterIA's "20h de l'IA" model:
- **Weekly brief** → text (existing cron `476112fc9e18`)
- **Upgrade path** → same brief → 60-90 sec video (9:16 portrait for X/mobile)
- **Distribution** → X via xurl, YouTube via API
- **Lead generation** → video = 10x more reach than text on social