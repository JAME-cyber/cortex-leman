# Veo 3.1 via Google Gemini API — Reference

## Discovery Context (Jul 2026)
- @itsshara_ai demoed "100% AI-made" cinematic 3D animated short (Seedance 2.0 + GPT Image 2 workflow, 15s, 12 cuts, Pixar-like quality)
- @XiaoKooeye demoed 2D narrative animation generated **directly by Gemini** (10s, Chinese guofeng style, zero cuts — "茶叶从山林走向世界" / "丝绸之路上的琵琶传播")
- These are two DIFFERENT approaches: Seedance for photoreal/cinematic, Gemini/Veo for 2D narrative/story-book

## API Access — CONFIRMED Working

### Models available
```
models/veo-3.1-generate-preview        → predictLongRunning
models/veo-3.1-fast-generate-preview   → predictLongRunning
models/imagen-4.0-generate-001         → predict
models/imagen-4.0-ultra-generate-001   → predict
models/imagen-4.0-fast-generate-001    → predict
```

### Endpoint
```
POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:predictLongRunning?key={API_KEY}
Content-Type: application/json
```

### Request body (validated format, received 429 not 400 — so schema is correct)
```json
{
  "instances": [{
    "prompt": "..."
  }],
  "parameters": {
    "sampleCount": 1,
    "aspectRatio": "9:16",
    "resolution": "720p",
    "durationSeconds": 8
  }
}
```

### Parameters
| Param | Values |
|-------|--------|
| aspectRatio | "9:16", "16:9", "1:1" |
| resolution | "720p", "1080p" |
| durationSeconds | 4-8 (estimated) |
| sampleCount | 1+ |

### Authentication
- API key from Google AI Studio: https://aistudio.google.com/apikey
- Key format: `AQ.Ab8R...` (not the standard `AIza...` format — may be a newer OAuth-style key)
- **CRITICAL**: Free tier returns HTTP 429 (RESOURCE_EXHAUSTED) for Veo models. Must enable billing (Blaze plan).

## What Does NOT Work
- **OpenRouter**: 41 Google/Gemini models available, but ALL are text+image+video→text (input). NONE generate video output. OpenRouter does not proxy Veo.
- **Gemini API free tier**: 429 on both veo-3.1-generate-preview and veo-3.1-fast-generate-preview
- **GEMINI_API_KEY in .env**: was empty — now set with the key above

## Go/No-Go Decision

| Scenario | Use Seedance (kie.ai) | Use Veo (Gemini API) |
|----------|-----------------------|----------------------|
| Photorealistic clips (CES cuisine, kiosk) | ✅ Validated, proven | ❌ Untested for photorealism |
| 2D narrative animation (african-heroes legends) | ⚠️ Possible but not native strength | ✅ @XiaoKooeye proved this style |
| 3D Pixar-style animation | ⚠️ Flat/Canva-like (pitfall #9) | ❓ Untested |
| Cost-sensitive batch (6+ clips) | $1.03/clip, known cost | $0.35-0.75/sec = $1.75-3.75/clip (MORE expensive) |
| One-shot continuous (no cuts) | Possible (pattern #45) | ✅ Native strength (zero cuts in demos) |

## Cost Comparison
| | Seedance 5s 720p | Veo 8s 720p (est.) |
|---|---|---|
| Per clip | $1.03 | ~$2.80-6.00 |
| Per CES short (5 clips) | $5.15 | ~$14-30 |
| Advantage | Cheaper, validated | Better 2D narrative |

## Google Vids — FREE Veo 3.1 Access Path (Aug 2026)

**Source:** @aiseomastery / Julian Goldie Agency tutorial (63 bookmarks, 8.5min)

Veo 3.1 is built directly into **Google Vids** (video editor at vids.google.com), free for
every personal Google account. **No billing plan required** — this is a different access path
from the Gemini API.

### Key Facts
| Feature | Detail |
|---------|--------|
| Cost | **FREE** (personal Google accounts) |
| Quota | **10 generations/month** |
| Duration | 8-10s per clip |
| Timestamp prompts | ✅ Supported ("0 to 3 seconds: character does X") |
| Extend feature | ✅ (continue/extend existing clip) |
| Editor | Full timeline, transitions, VO recording, music |

### Workflow (from tutorial)
1. Claude (Sonnet 5) → scene-by-scene outline
2. Pinterest → 5-6 style reference images in a folder
3. Character reference sheet (multi-angle, locked features)
4. Generate clips in Google Vids with timestamp prompts
5. Connect clips: Extend (continue) OR camera angle switch (last frame → new angle = clean cut)
6. Assemble in Vids editor: timeline, trim, transitions, VO

### Camera Angle Switch Trick
Take the last frame of clip A → generate clip B from a different camera angle.
A changed angle reads as an intentional edit instead of a continuity error.
Same technique as professional film editing between shots.

### Limitations vs Seedance
- 10/month quota = too low for production pipeline
- Cartoon/flat illustration quality ≠ photorealistic Seedance
- No multimodal character references
- No API — manual UI only

### Verdict
Free Veo 3.1 path for prototyping and 2D narrative exploration.
Too limited for Tars production volume. The camera angle switch trick is a useful editing technique
regardless of the generation tool used.

## Next Steps to Unlock
1. Enable billing on Google AI Studio (Blaze plan)
2. Run a single Veo test with african-heroes prompt (2D narrative style)
3. Compare side-by-side with equivalent Seedance clip
4. If Veo wins on 2D narrative → integrate for african-heroes series only
5. Google Vids free tier = zero-cost prototyping before spending API credits
