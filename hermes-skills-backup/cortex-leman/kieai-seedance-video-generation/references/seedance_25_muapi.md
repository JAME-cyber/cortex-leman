# Seedance 2.5 via MuAPI — Alternative Provider

**Last updated**: Aug 3, 2026 — audio synthesis confirmed via schema, kie.ai status checked

## Provider Status (Aug 3, 2026)

| Provider | Seedance 2.5 | Audio | Status |
|----------|-------------|-------|--------|
| kie.ai | Model registered (`bytedance/seedance-2-5`) but **non-functional** (HTTP 500, "Coming Soon" page) | N/A | 🔴 Blocked |
| muapi.ai | ✅ **Early access live** — 10 variants operational | ✅ `generate_audio: true` by default | 🟢 Available |

## Endpoints (10 variants on muapi.ai)

| Endpoint | Resolutions | Max Duration | Cost |
|---|---|---|---|
| T2V (text-to-video) | 720p, 480p | 30s | $3.00 / $1.50 |
| I2V (image-to-video) | 720p, 480p | 30s | $3.00 / $1.50 |
| First & Last Frame | 720p, 480p | 30s | $3.00 / $1.50 |
| Omni-Reference | 720p, 480p | 30s | $3.60 / $1.80 |
| Spicy T2V / I2V | 480p–4K | 4–16s | **$0.60** (cheapest) |

## Key upgrades vs Seedance 2.0

- **30s clips** (up from 15s on 2.0)
- **Native audio synthesis** — `generate_audio: true` param, confirmed in schema (Aug 3)
- **Omni-Reference**: 20 images / 6 videos / 6 audio (up from 9/3/3 on 2.0)
- **Seedance Character**: 1-3 photos → multi-panel character sheet → `consistent_video()` for cross-shot identity lock
- **480p tier** exists for cheap drafts
- **Spicy tier**: relaxed moderation, higher-contrast motion, 4K output, cheapest ($0.60)

## API Schema (confirmed Aug 3 via `GET /api/v1/models/{model-name}`)

**Auth:** `x-api-key: {MUAPI_API_KEY}` header (no Bearer prefix)

**Input schema** (seedance-2.5-spicy-text-to-video):
```json
{
  "prompt": "string (required) — scene description",
  "aspect_ratio": "16:9 | 9:16 | 1:1 | 3:4 | 4:3 | 21:9",
  "duration": "int 4-16 (spicy) or up to 30 (standard)",
  "resolution": "480p | 720p | 1080p | 4K",
  "generate_audio": "boolean (default: true) — NATIVE audio synthesis",
  "camera_fixed": "boolean (default: false)"
}
```

**Output:**
```json
{
  "id": "request_id",
  "status": "prediction status",
  "output": {
    "video": "https://..."
  }
}
```

## Pricing Comparison (12x more expensive than kie.ai for 2.0)

| Provider | Quality | Per sec | 6s clip | 30s clip |
|---|---|---|---|---|
| **kie.ai (us, Seedance 2.0)** | Standard | **$0.05** | **$0.30** | **$1.50** |
| muapi.ai 480p | Seedance 2.5 draft | $0.30 | $1.80 | $9.00 |
| muapi.ai 720p | Seedance 2.5 | $0.60 | $3.60 | $18.00 |
| muapi.ai Spicy | Seedance 2.5 spicy | $0.10 | $0.60 | N/A (16s max) |

## Impact on Cortex Leman Pipeline

**Current workflow (Seedance 2.0):**
```
Script → Seedance 2.0 (silent) → VO ElevenLabs/Edge → lip-sync/overlay → final
```

**With Seedance 2.5 native audio:**
```
Script + dialogue → Seedance 2.5 T2V → final (VO included)
```

Eliminates VO generation + lip-sync steps (~40% of production time).

### Unknowns to validate with live test:
1. ~~**FR/VO française**~~ — ✅ **VALIDATED Aug 3** via @patrickassale tweet (1.1K likes, 751 bmk). 30s scene: couple dispute in kitchen + child interruption. French is natural, colloquial ("tu te fous", "lâche-moi"), multi-voice (3 characters: man, woman, child), emotional range (anger → tenderness → contempt). Audio: stereo 44.1kHz, 128kbps, pro dynamics (-24.5 dB mean, -1.3 dB peak). **French is production-ready for narrative content.**
2. **Voice control** — still unknown. API schema only exposes `prompt` + `generate_audio`. No `script`/`dialogue` parameter. Model **invents dialogue from vague prompt** — good for fiction, risky for business content (pricing, client identity). Unless script-lock exists, keep VO ElevenLabs for CES/LEC business content.
3. **Multi-scene consistency** — voice coherence across separate generations still unknown
4. **Lip-sync quality** — @patrickassale demo was wide shot, close-up lip-sync unconfirmed

## Python wrapper

```bash
pip install seedance-2-api
```

Repo: github.com/SamurAIGPT/Seedance-2.5-API
API: `POST https://api.muapi.ai/api/v1/seedance-2.5-text-to-video`
Auth: `x-api-key: <MUAPI_API_KEY>`
MCP server included (`python3 mcp_server.py`)

## Getting muapi.ai API Key

1. Go to https://muapi.ai/dashboard
2. Create account → API Keys section → Generate key
3. **Sandbox keys** available for free mock-data testing
4. Production keys: pay-as-you-go (no subscription)
5. No key in env yet — add `MUAPI_API_KEY` to `~/.hermes/.env`

## Verdict (Aug 2026)

- ❌ **No migration** — kie.ai remains 12x cheaper for production (2.0)
- ✅ **Spicy tier ($0.60)** cheapest entry point for 2.5 experiments
- ✅ **480p tier** useful for drafts per Retake Protocol
- ✅ **Omni-Reference 20 images** = killer feature for multi-char (not on kie.ai)
- ✅ **First & Last Frame** = keyframe-driven transitions (not on kie.ai)
- ✅ **Native audio** = pipeline simplification if quality matches demo
- ⚠️ **Early access** — gated, preview builds
- ⚠️ **2.5 quality concerns** — morphing during fast action + object persistence issues reported
- ⚠️ **kie.ai "Coming Soon"** — when kie.ai enables 2.5, re-evaluate cost gap

## Decision triggers for migration

1. **Client project needs 20+ character refs** → MuAPI Omni-Reference is the only option
2. **Client project needs 30s single clips** → MuAPI (kie.ai maxes at 15s)
3. **Client project needs native dialogue audio** → MuAPI (kie.ai silent only)
4. **kie.ai adds Seedance 2.5** → re-evaluate immediately (would eliminate the cost gap)

## Quick Reference: Check muapi.ai Model Catalog (no auth)

```bash
curl -sL "https://api.muapi.ai/api/v1/models" | python3 -c "
import sys, json
d = json.load(sys.stdin)
models = d.get('models', d) if isinstance(d, dict) else d
for m in models:
    name = m.get('name', '')
    if 'seedance' in name.lower():
        print(f\"{name} | \${m.get('cost','?')} | {m.get('description','')[:80]}\")
"
```

Check specific model schema (no auth):
```bash
curl -sL "https://api.muapi.ai/api/v1/models/{model-name}" | python3 -m json.tool
```
