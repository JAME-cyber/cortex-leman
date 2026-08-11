# Kie.ai API Reference — Patterns & Quirks

**Validated:** 2026-07-04 via OpenMontage adapter integration (kie_image.py, kie_video.py)
**Base URL:** `https://api.kie.ai`
**Auth:** `Authorization: Bearer <KIE_API_KEY>` (env: `KIE_API_KEY` or `KIE_AI_API_KEY`)
**Key URL:** https://kie.ai/api-key

---

## Architecture: Two API Systems

Kie.ai has **two separate endpoint families** depending on the model:

| API Path | Models | Endpoints |
|----------|--------|-----------|
| **Dedicated Veo API** | `veo3`, `veo3_fast`, `veo3_lite` | `/api/v1/veo/generate`, `/api/v1/veo/recordInfo` |
| **Market Jobs API** | Everything else (Nano Banana, FLUX-2, Kling, Wan, Seedance, etc.) | `/api/v1/jobs/createTask`, `/api/v1/jobs/recordInfo` |

**Mistake to avoid:** Using `/api/v1/jobs/createTask` for Veo3 models or vice versa. The model name determines which API family to use.

---

## Async Flow (Both APIs)

```
1. POST create → returns {code: 200, data: {taskId: "..."}}
2. GET recordInfo?taskId=xxx → poll until state == "success"
3. Parse resultJson (JSON string) → extract resultUrls[0]
4. Download from resultUrls[0] directly (no conversion needed)
```

### Step 1: Create Task

**Market models (images + non-Veo video):**
```python
payload = {
    "model": "nano-banana-2",           # kie.ai model identifier
    "input": {
        "prompt": "...",
        "aspectRatio": "16:9",           # or "1:1", "9:16", "4:3", "3:4"
        "negativePrompt": "...",         # optional
        "seed": 42,                      # optional
    }
}
# POST /api/v1/jobs/createTask
```

**Veo3 video models:**
```python
payload = {
    "prompt": "...",
    "model": "veo3_fast",               # NOT in input, top-level
    "aspect_ratio": "16:9",             # underscore, not camelCase
    "resolution": "720p",               # "720p", "1080p", "4k"
    "duration": 8,                      # 4, 6, or 8 seconds
    "generationType": "TEXT_2_VIDEO",   # or FIRST_AND_LAST_FRAMES_2_VIDEO
    "imageUrls": ["https://..."],       # for image-to-video (1 or 2 URLs)
}
# POST /api/v1/veo/generate
```

**Key schema difference:** Market models nest params under `input.{}` with camelCase. Veo3 uses flat top-level fields with snake_case for some fields.

### Step 2: Poll Status

```python
# Market: GET /api/v1/jobs/recordInfo?taskId=xxx
# Veo3:   GET /api/v1/veo/recordInfo?taskId=xxx

# ⚠️ CRITICAL: The status field is called "state", NOT "status"
data = response.json()["data"]
state = data.get("state")  # ← "state", not "status"
```

**States observed:** `"success"` (done), `"processing"` (in progress)

### Step 3: Parse Result

```python
import json

# ⚠️ CRITICAL: resultJson is a JSON-ENCODED STRING, not a dict
result_json_str = data["resultJson"]     # type: str
parsed = json.loads(result_json_str)
urls = parsed["resultUrls"]              # list of URL strings
image_or_video_url = urls[0]
```

**Do NOT try:** `data["outputs"]`, `data["url"]`, `data["creations"]` — these don't exist on the market API. The result is **always** in `resultJson.resultUrls`.

### Step 4: Download

```python
# Direct download works — no need for /api/v1/common/download-url
import requests
resp = requests.get(urls[0], timeout=60)
# Content is image (JPEG/PNG) or video (MP4)
```

---

## CRITICAL QUIRKS (Discovered During Integration)

### 1. `state` ≠ `status`
The `recordInfo` response uses `state`, not `status`. If you poll for `status`, you'll get `None`/`"?"` forever and time out.

```python
# WRONG — times out:
status = data.get("status", "")  # always ""

# RIGHT:
state = data.get("state", "")    # "success", "processing", "fail"
```

### 2. `resultJson` is a String
The response field `resultJson` contains a JSON string, not a parsed object. You must `json.loads()` it before accessing `resultUrls`.

```python
# WRONG — AttributeError:
data["resultJson"]["resultUrls"]

# RIGHT:
json.loads(data["resultJson"])["resultUrls"]
```

### 3. Different Schema Per API Family
Market models and Veo3 use different request schemas:
- **Market:** `{model: "...", input: {prompt: "..."}}` (nested, camelCase)
- **Veo3:** `{prompt: "...", model: "..."}` (flat, snake_case for some fields)

### 4. Temp URLs Are Directly Downloadable
The URLs in `resultUrls` (e.g. `https://tempfile.aiquickdraw.com/ggc/...`) work with direct GET requests. No need to call `/api/v1/common/download-url` first.

### 5. Image Format Mismatch
Files served from `tempfile.aiquickdraw.com` are **JPEG** even when the URL ends in `.png`. Don't rely on file extension for format detection.

### 6. Error Response Shape
Errors use `failMsg` (string) on the data object, not `error.message`:
```python
# In recordInfo response:
if state in ("fail", "failed"):
    error = data.get("failMsg")  # ← string, not nested dict
```

### 7. Model Identifier Mapping
Friendly names must be mapped to kie.ai identifiers. The API does NOT accept shorthand:
```python
# "nano-banana-2" → "nano-banana-2" (same)
# "flux-2-pro" → "flux-2/pro-text-to-image"
# "seedream-5" → "seedream/5-lite-text-to-image"
```
Always maintain a mapping dict.

---

## Model Catalog (Validated 2026-07-04)

### Image Models (16+)

| Friendly Name | Kie.ai Model ID | Approx Cost |
|---------------|-----------------|-------------|
| `nano-banana-2` | `nano-banana-2` | $0.04 |
| `nano-banana` | `google/nano-banana` | $0.03 |
| `imagen4-ultra` | `google/imagen4-ultra` | $0.06 |
| `flux-2-pro` | `flux-2/pro-text-to-image` | $0.05 |
| `seedream-5` | `seedream/5-lite-text-to-image` | $0.03 |
| `gpt-image-2` | `gpt/gpt-image-2-text-to-image` | $0.04 |
| `grok-imagine` | `grok-imagine/text-to-image` | $0.03 |
| `ideogram-v3` | `ideogram/v3-text-to-image` | $0.03 |
| `z-image` | `z-image/z-image` | $0.02 |

### Video Models

**Veo3 (Dedicated API):**

| Model | Description | Approx Cost |
|-------|-------------|-------------|
| `veo3` | Quality, 4K-capable | $0.50-$1.00 |
| `veo3_fast` | Fast generation | $0.25-$0.50 |
| `veo3_lite` | Lite, cheapest | $0.15 |

**Market Video (Jobs API):**

| Friendly Name | Kie.ai Model ID |
|---------------|-----------------|
| `kling-v3-turbo-t2v` | `kling/v3-turbo-text-to-video` |
| `wan-2.7-t2v` | `wan/2-7-text-to-video` |
| `seedance-2` | `bytedance/seedance-2` |
| `happyhorse-t2v` | `happyhorse/text-to-video` |

---

## Timing & Costs (Real Measurements)

| Model | Typical Duration | Cost |
|-------|-----------------|------|
| nano-banana-2 (1:1) | ~14s | $0.04 |
| nano-banana-2 (16:9) | ~17s | $0.04 |
| veo3_fast (8s, 720p) | ~90s (estimated) | $0.25 |

Poll interval recommendation: 3s for images, 5s for video.
Timeout recommendation: 300s for images, 600s for video.

---

## Environment Setup

```bash
# In ~/.hermes/.env or project .env
KIE_API_KEY=<your-key>          # preferred
# or
KIE_AI_API_KEY=<your-key>       # fallback
```

The adapter checks both env vars: `KIE_API_KEY` first, then `KIE_AI_API_KEY`.

---

## Common Pitfalls

| Problem | Root Cause | Fix |
|---------|-----------|-----|
| Poll times out, status always "?" | Using `status` instead of `state` | Use `data.get("state")` |
| No image URL found | Trying `data["outputs"]` or `data["url"]` | Use `json.loads(data["resultJson"])["resultUrls"]` |
| 400 on Veo3 with market endpoint | Wrong API family | Use `/api/v1/veo/generate` for Veo3 models |
| 400 on market model with Veo endpoint | Wrong API family | Use `/api/v1/jobs/createTask` for non-Veo models |
| Download returns wrong content type | `.png` URL serves JPEG | Don't rely on extension; use magic bytes or content-type header |
| Model not found | Using friendly name as kie.ai identifier | Map through KIE_IMAGE_MODELS / MARKET_VIDEO_MODELS dict |
