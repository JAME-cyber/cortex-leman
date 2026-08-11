# Hailuo (MiniMax) Video Generation on Kie.ai — Pricing & API

**Discovered July 30, 2026** via Kie.ai pricing page extraction.

## Why Hailuo vs Seedance

Hailuo 2.3 (MiniMax H3) has **superior character facial consistency across multiple cuts** from a single character sheet reference. Seedance 2.0 is better for dynamic motion and director tokens, but Hailuo wins when the #1 requirement is identity preservation across angles — exactly the problem clients complain about (e.g., Linda/Culture en Saveur: "les personnages restent cohérents").

**Use Hailuo when**: character must look identical across 3+ cuts/angles (educational series, recurring mascot, multi-scene narrative).
**Use Seedance when**: motion quality, camera moves (dolly, bullet time), dynamic action scenes matter more than perfect identity lock.

## Pricing (verified July 30, 2026)

Extracted from kie.ai/pricing via `browser_console` DOM scraping (pricing table loads dynamically, not in page source).

### Hailuo 2.3 (current gen)

| Config | Credits | USD | vs Official |
|--------|---------|-----|-------------|
| Pro 6s 768p | **45** | $0.225 | N/A |
| Pro 6s 1080p | **80** | $0.40 | −18.4% |
| Pro 10s 768p | **90** | $0.45 | N/A |
| Standard 6s 768p | **30** | $0.15 | −46.4% |
| Standard 6s 1080p | **50** | $0.25 | −24.2% |
| Standard 10s 768p | **50** | $0.25 | −55.4% |

### Hailuo 02 (previous gen — cheaper)

| Config | Credits | USD | vs Official |
|--------|---------|-----|-------------|
| Standard 6s 512p | 12 | $0.06 | −41.2% |
| Standard 6s 768p (t2v) | 30 | $0.15 | −44.4% |
| Standard 10s 512p (i2v) | 20 | $0.10 | −41.2% |
| Standard 10s 768p | 50 | $0.25 | −44.4% |
| Pro 6s 1080p | 57 | $0.285 | −40.6% |

### Cost Comparison: Character Sheet Multi-Cut Test (4 clips)

| Model | Config | Total Credits | Total USD |
|-------|--------|---------------|-----------|
| Hailuo 2.3 Standard | 6s 768p ×4 | 120 | $0.60 |
| Hailuo 2.3 Pro | 6s 768p ×4 | 180 | $0.90 |
| Hailuo 2.3 Pro | 6s 1080p ×4 | 320 | $1.60 |
| Seedance 2.0 | 5s 720p ×4 | 820 | $4.10 |

**Hailuo is ~4.5× cheaper than Seedance for the same number of clips.** For character-consistency-critical content (educational kids series), Hailuo Pro at $0.90 for 4 angles is the sweet spot.

## API Endpoint

```
POST https://api.kie.ai/api/v1/jobs/createTask
Authorization: Bearer $KIE_AI_API_KEY
Content-Type: application/json
```

Body:
```json
{
  "model": "hailuo/2-3-image-to-video-pro",
  "callBackUrl": "https://httpbin.org/post",
  "input": {
    "prompt": "<motion description — describe what the character DOES, not the setting>",
    "image_url": "<character sheet or reference image URL>",
    "duration": "6",
    "resolution": "768P"
  }
}
```

**Polling**: Same unified endpoint as Seedance: `GET /api/v1/jobs/recordInfo?taskId=<ID>`

**Note**: Unlike Suno API (which migrated to `/api/v1/generate`), Hailuo video still uses the `/api/v1/jobs/createTask` endpoint. The two APIs coexist with different paths as of July 2026.

## Character Sheet Multi-Cut Technique (Pattern #55)

Source: @SharaI Ai Video Creator, x.com/i/status/2082822047986839677 (July 2026)

**Input**: 1 character sheet (single reference image showing the character from front + side + back, or a hero portrait)
**Output**: 12+ clips at different angles, all maintaining face/clothing/body consistency

### Workflow

1. **Generate character sheet** with GPT Image 2 or Seedream 5.0 Pro (front/side/back views + expression variants on one image)
2. **Pass the result URL directly** — no upload needed! The `tempfile.aiquickdraw.com` URL returned by Seedream works as-is for Hailuo's `image_url` field. (Validated Jul 30, 2026: 5 sheets → 6 clips, all successful.)
3. **Submit multiple Hailuo jobs** — each with a DIFFERENT camera angle prompt but SAME `image_url` reference:
   - "Character walking toward camera, frontal tracking shot"
   - "Character from behind, following shot through corridor"
   - "Character profile, side view, slow pan"
   - "Character low angle, looking up, dramatic perspective"
4. **Edit together** with ~2s cuts (short cuts prevent drift perception)

### Why It Works

Hailuo H3's architecture locks identity features (face, hair, skin texture, body type, outfit) from the reference image more rigidly than Seedance. Seedance optimizes for motion fluidity; Hailuo optimizes for identity preservation. For content where a parent needs to recognize "the same child" across scenes (Culture en Saveur), this is the decisive factor.

### Limitations

- Motion is less dynamic than Seedance (stiffer, more "portrait-like")
- No native director tokens (dolly zoom, bullet time) — camera moves must be described in prose
- 10s max duration (1080p limited to 6s)
- Still image-to-video only (no text-to-video character lock in 2.3 Pro)

## Batch Character Pipeline (Seedream → Hailuo I2V — VALIDATED Jul 30, 2026)

End-to-end batch workflow producing 5 character sheets + 6 clips in one script run. Total cost: ~441 credits (~$2.21) for the full set.

**Script**: `/home/tars/culture-en-saveur/scripts/gen_phase2_pipeline.py`

### Key learnings from batch execution:

1. **Seedream `quality` field is REQUIRED** — omitting it returns `code: 500, msg: "This field is required"`. Always set `"quality": "high"` in the `input` dict. The existing KieClient wrapper includes it; raw API calls must not.

2. **Seedream timeout → check task directly before retry.** Seedream tasks frequently exceed 180s polling timeouts but complete successfully on Kie's backend. When a poll times out, do NOT immediately retry — instead query `recordInfo?taskId=` directly. In the Jul 30 batch, 2/5 sheets appeared to "fail" (poll timeout) but were actually `state: "success"` on direct check. Retrying would have wasted ~56 credits and produced duplicate work.

3. **URL passthrough eliminates upload step.** The `resultUrls` from Seedream (`tempfile.aiquickdraw.com/seedream5pro/...` or `/p/...`) work directly as Hailuo's `image_url`. No file-upload API call needed. This simplifies the pipeline from 3 steps to 2 (generate image → pass URL to video gen).

4. **Generation times observed (batch of 5 + 6)**:
   - Seedream character sheets: 60-180s each (some hit 300s polling limit but succeed)
   - Hailuo Pro 6s 768p clips: ~90s each
   - Total wall time for 5 sheets + 6 clips: ~15 min

5. **Budget for batch pipeline**: 5 sheets (~14cr each = 70cr) + 6 clips (45cr each = 270cr) + retry margin (~50cr) = ~390cr total. Fits within a 500cr budget.

## Finding ANY kie.ai Model ID (Universal Technique — VALIDATED Jul 30, 2026)

**Do NOT guess model names or browser-navigate the pricing page.** Use `docs.kie.ai/llms.txt` instead:

```bash
# 1. Get all model IDs and their doc URLs in one call
curl -s 'https://docs.kie.ai/llms.txt' | grep -i hailuo

# 2. Fetch the specific model's OpenAPI spec for exact payload
curl -s 'https://docs.kie.ai/market/hailuo/2-3-image-to-video-pro.md'
```

Output includes the exact `model` value (e.g. `hailuo/2-3-image-to-video-pro`), all input parameters with types/enums, and the `operationId`. This bypasses all JavaScript-rendered pages and works in seconds.

**Session validated Jul 30, 2026**: Spent 10+ minutes guessing model names (20+ API 422 errors with names like `hailuo-2.3`, `Hailuo-AI-2.3`, `video-01`, `MiniMax-Hailuo`, etc.) and browser-navigating kie.ai pricing/docs before discovering this approach. The `llms.txt` endpoint returns plain text with all model IDs and doc URLs — no JS rendering needed.

## Hailuo 02 T2V Standard — Cheapest T2V Option (30cr, VALIDATED Jul 31, 2026)

Model ID: `hailuo/02-text-to-video-standard`

This is the cheapest text-to-video option on kie.ai. It includes a **native `prompt_optimizer`** flag (boolean) that auto-enhances the prompt before generation — effectively free built-in prompt engineering.

**Payload** (VALIDATED end-to-end Jul 31, 2026, 3 clips generated):
```json
{
  "model": "hailuo/02-text-to-video-standard",
  "input": {
    "prompt": "...",
    "duration": "6",
    "prompt_optimizer": true
  }
}
```

**⚠️ CRITICAL — `resolution` field is REJECTED by this model.** Including `"resolution": "768P"` causes HTTP 422 `{"code": 422, "msg": "Invalid parameter"}`. Only `prompt`, `duration`, `prompt_optimizer`, and `nsfw_checker` are accepted. This is the opposite of Hailuo 2.3 Pro (which requires `resolution`). The `docs.kie.ai/market/hailuo/02-text-to-video-standard.md` spec confirms only 4 input fields.

**⚠️ PROMPT LENGTH LIMIT (VALIDATED Aug 1, 2026)**: This model rejects prompts exceeding ~1,500 characters with HTTP 500 `{code: 500, msg: "prompt exceeds maximum length"}`. A full Pattern #65-style 11-section structured prompt (~2,500 chars) gets rejected. Condense to ~1,000-1,300 chars by stripping structural scaffolding while keeping core directives. The `prompt_optimizer: true` flag partially compensates since it auto-expands server-side. See `scripts/test_pattern65_ownership_lock.py` for a validated condensed prompt.

**⚠️ `duration` MUST BE A STRING (VALIDATED Aug 1, 2026)**: `"duration": "6"` (correct) vs `"duration": 6` (returns 500 `"duration it must be a string"`).

## Confirmed Working Payload (Hailuo 2.3 Pro — TESTED END-TO-END Jul 30, 2026)

Full submit → poll → download cycle verified. 45cr consumed (1033.5→988.5). Generation time ~90s.

```json
{
  "model": "hailuo/2-3-image-to-video-pro",
  "input": {
    "prompt": "A warm family kitchen scene with African children cooking together, gentle camera movement",
    "image_url": "https://file.aiquickdraw.com/...webp",
    "duration": "6",
    "resolution": "768P",
    "nsfw_checker": false
  }
}
```

**Key field details (confirmed by testing, not just docs):**
- `duration`: STRING, not int (`"6"` or `"10"`)
- `resolution`: UPPERCASE (`"768P"` or `"1080P"`)
- `image_url`: must be a URL (upload to kie.ai file storage first, or use any accessible image URL)
- Accepted image types: jpeg, png, webp; max 10MB
- `nsfw_checker`: optional boolean, defaults false
- **Generation time observed**: ~90 seconds for 6s Pro 768p clip
- **Download**: direct `requests.get(url)` on `resultUrls[0]` works (same as Seedance)

## Pricing Extraction Technique (Legacy — prefer llms.txt above)

The kie.ai/pricing page loads model tables dynamically via JavaScript. Static fetch returns no pricing data. To extract:

```javascript
// Run in browser_console after navigating to kie.ai/pricing
(() => {
  const grids = document.querySelectorAll('[role="grid"]');
  const results = [];
  grids.forEach(g => {
    g.querySelectorAll('[role="row"]').forEach(r => {
      const cells = r.querySelectorAll('[role="rowheader"], [role="gridcell"]');
      const vals = [...cells].map(c => c.textContent.trim());
      if (vals.length > 0) results.push(vals.join(' | '));
    });
  });
  return JSON.stringify(results);
})()
```

Filter results by typing model name in the search box first to narrow the output.
