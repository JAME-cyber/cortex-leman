# Seedance 2.5 — Official Guide (Leaked ByteDance Internal Doc)

**Discovered**: Aug 2, 2026 via @lena_z01 tweet (1024 bookmarks)
**Source**: Screen recording of internal ByteDance document
**Breadcrumb visible**: `ByteDance > Xinyao Wang > 【Dreamina】 Seedance 2.5 User Guide`
**Watermark**: "Linyi Zheng"

This is the authoritative feature list for Seedance 2.5, ahead of API release.

## Features Not Available on 2.0

### 1. Long-form up to 180 seconds
- Video Extension: base video extensible by +4 to +30s
- Extreme case: 30s → 60s possible
- **Max theoretical: 180 seconds of continuous video**

### 2. Smart Edit (text-based editing)
- **Smart Edit**: describe changes in natural language on existing video
- **Edit with marks**: marquee selection + brushes for precise local edits on frame elements

### 3. MultiModal References (major upgrade)
Inputs accepted simultaneously:
- Prompt text
- Reference picture (style/character)
- Reference video (movement/composition)
- Reference audio (audio-driven generation)

### 4. Timestamp Text Control
ByteDance officializes the timestamped shot-by-shot prompt structure discovered by community.
This is the same structure as patterns #50, #64, #65, #68 — now officially supported.

### 5. Creative & Mask Transitions
- **Creative transitions**: transitions described in prompt (e.g., "paper airplane flies towards camera, naturally transition to video 2")
- **Mask transitions**: masks for targeted transitions

### 6. Partial Elimination (post-editing)
"Partial elimination function for post-editing of the original video is accurately executed"
Removes unwanted elements from generated video: subtitles, BGM, objects. Sd2.5 > Sd2.0 on this.

### 7. Clay Renderer (3D Integration) — MOST INTERESTING
A plug-in that:
- Integrates **Maya/Blender** with Seedance
- Converts **3D camera language** (Maya/Blender camera scheduling, spatial composition) into prompts/generation
- Features: Lens language restoration, Space and Composition Lock, Character position and movement trajectory control

This is the Blender/Houdini MCP pattern — but **integrated natively** into the video generator.
Not an external MCP: the 3D software speaks directly to Seedance.

### 8. Official Prompt Formula (for real persons)
The guide gives an official character structure:
- **Hairstyle/Hair Color** → subdivision
- **Clothing/Clothing texture** → subdivision
- **Tone Atmosphere**
- **Character Material**
- **Light and Shadow Effects**

## Comparison Sd2.5 vs Sd2.0 (from the guide)

The guide contains a comparison table showing Sd2.5 improvements over Sd2.0 across:
- Multi-modal input handling (better combined reference consistency)
- Smart Edit accuracy
- Partial elimination precision
- Overall narrative coherence

## Platform Availability (Aug 2, 2026)

| Platform | Sd 2.0 | Sd 2.5 | Access |
|----------|--------|--------|--------|
| **BytePlus API** | ✅ | ❌ not yet | B2B cloud, $4.30/M tokens |
| **Dreamina** (consumer) | ✅ | ✅ | China-locked portal |
| **Higgsfield** | ✅ | ✅ ($49+/mo) | Draw-to-direct camera motion (exclusive), MCP/CLI, 4K campaign |
| kie.ai | ✅ | ❌ registered but non-functional (500 errors) | Our current provider |
| Pollo.ai | ✅ | ❓ claims 2.5 | Cloudflare-blocked, unverified |
| MuAPI | ❌ | ✅ early-access live | Spicy tier $0.60 cheapest 2.5 entry |
| OpenArt | ❓ | ✅ ($14+/mo) | 3 clips/mo on cheapest plan |
| Runway | ❓ | ✅ ($15+/mo) | Most expensive per clip ($5.76) |

## What This Means for Tars Stack

| Feature | Impact | When Available |
|---------|--------|---------------|
| 180s long-form | Game-changer for african-heroes (full episode in one pass) | When BytePlus adds 2.5 |
| Clay Renderer | Professional camera control, Blender→video bridge | When BytePlus adds 2.5 |
| Multimodal refs | Character consistency finally solved (image+video+audio lock) | When BytePlus adds 2.5 |
| Smart Edit | Post-edit without regenerating = massive credit savings | When BytePlus adds 2.5 |
| Timestamp control | Already validated via community patterns | Available now (2.0) |

## French Language Validation (Aug 3, 2026)

@patrickassale tweet (1,160 likes, 751 bmk) — 30s T2V scene in French:
- **Quality**: natural, colloquial French ("tu te fous", "lâche-moi avec ça")
- **Multi-voice**: 3 distinct characters (man, woman, child) with individual timbres
- **Emotion**: anger → tenderness → contempt transitions, all convincing
- **Audio**: stereo 44.1kHz/128kbps, professional dynamics

**⚠️ Script control gap**: the API only exposes `prompt` + `generate_audio`. The model **invents dialogue** from a vague prompt. No `script` or `dialogue` parameter exists. This means:
- ✅ **Narrative/fiction** (Culture en Saveur, African Heroes): immediately exploitable
- ⚠️ **Business content** (CES/LEC pricing, client identity): model may hallucinate facts. Keep VO ElevenLabs pipeline until script-lock is available.

## Assets Saved
- `~/references/seedance_25_guide/` — mp4, 57 frames from the screen recording
- Watchdog: `bin/check-seedance25-byteplus.sh` (cron job 83d97b07a8f6, every 6h)
