# Seedance 2.0 — Multi-Platform Landscape (Jul 2026)

Seedance 2.0 (ByteDance) is accessible through multiple platforms, not just KIE.AI.
Each has different strengths: API access, pricing, and feature support (especially face+voice reference).

## Platform Comparison

| Platform | API | Face+Voice Ref | 5s 720p Cost | Best For |
|----------|-----|----------------|-------------|----------|
| **KIE.AI** | ✅ REST | ❌ unconfirmed | ~205cr ($1.03) | Automated pipelines, pay-per-use |
| **EvoLink** | ✅ REST | ✅ video ref | ~$0.99 (T2V) / ~$1.21 (ref) | API access to face+voice reference |
| **Maxfusion AI** | ❌ UI only | ✅ (ByteDance-authorized) | Unknown (account-gated) | Manual face+voice work |
| **seedance2.ai** | ❌ UI only | ✅ | 60cr (~$0.30) | Cheapest manual generation |
| **Pippit** | ❌ UI only | ❌ | From $14.90/mo | Consumer/editing workflow |

## EvoLink API (Recommended for face+voice via API)

- Base URL: `https://evolink.ai`
- API endpoint: `POST /v1/videos/generations`
- Auth: `Authorization: Bearer YOUR_API_KEY`
- Async: returns task_id, poll `GET /v1/tasks/{task_id}`
- Model IDs: `seedance-2.0-text-to-video`, reference-to-video variants

### Reference-to-Video pricing (EvoLink)
Billed on **input + output seconds** (not just output):

| Resolution | $/sec | Credits/sec | 5s output (15s ref input = 20s total) |
|-----------|-------|------------|--------------------------------------|
| 480p | $0.056 | 3.834 | ~$1.12 |
| 720p | $0.121 | 8.22 | ~$2.42 |
| 1080p | $0.302 | 20.52 | ~$6.04 |

**Strategy:** Test at 480p Fast ($0.37 for 5s) to validate prompt, then render final at 720p.

## Maxfusion AI — Face+Voice Reference (ByteDance-Authorized)

**Source:** @OriSilver article (Apr 2026, x.com/i/article/2047111884638212096)

Maxfusion AI (@MaxfusionAI) is the only platform explicitly authorized by ByteDance
to process human face AND voice references simultaneously in Seedance 2.0.

### Why it matters
Other platforms block human face references (liability). Maxfusion exposes this natively.
The technique only works when you can pass face+voice into the model simultaneously.
Stitched pipelines (face swap + separate voice clone) produce results that feel "assembled" —
this produces something that feels "native."

### Setup requirements
1. **Source video**: 15 seconds of yourself (old YouTube video works)
2. **Must be unedited** — no cuts, jump cuts, or transitions (confuses reference extraction)
3. **Voice must be loud and clear** — model learns voice characteristics from audio
4. **No background noise** — coffee shop, street noise, room echo all degrade voice reference

### The exact prompt (copy-paste template)
```
Use this video as a reference for looks and voice only.
Do not use @Video1 in the scene itself, only the likeness
and especially the voice of the character.
A cinematic scene of @Video1 [YOUR SCENE DESCRIPTION + SCRIPT HERE]
```

Replace `@Video1` with whatever tag Maxfusion assigns your reference file.
The `@` tag is **OBLIGATORY** — omitting it breaks the reference anchoring.

### Three critical success factors
1. **"Voice only" instruction** — tells Seedance to prioritize voice extraction.
   Without it, model weights visual likeness heavily → looks right but sounds generic.
2. **"Do not use @Video1 in the scene itself"** — prevents model from reconstructing
   the actual footage instead of extracting characteristics for new generation.
3. **`@` tag in both instruction AND scene description** — the tag is how the model
   resolves the reference. Using it once is not enough.

### Three failure modes
1. **Bad source video** — edited clips, noisy audio, quiet delivery → degraded voice
2. **Missing `@` tag in prompt** — no anchor to reference file → generic character
3. **Missing voice instruction** — skip "for looks and voice" → weak voice output

### Business application
Eliminates recording bottleneck: 1 reference clip → N generated scenes with consistent
likeness and voice. Change only the script and scene description.
- **CES**: Host across multiple scenes without re-recording
- **LEC**: Market updates (bull/bear) with same presenter
- **african-heroes**: Consistent narrator across episodes

## BytePlus — Official ByteDance API (Aug 2026)

**Source:** @lena_z01 leak of internal ByteDance/Dreamina docs (1024 bookmarks)

BytePlus (`byteplus.com/en/product/video-generation`) is the official B2B cloud arm of ByteDance.
**This is the direct-from-creator API** — no middleman.

### Pricing (Token-based, $4.30/M tokens uniform)

| Plan | Price | Tokens | ~480P videos |
|------|-------|--------|-------------|
| Light | $30.10 | 7M | ~28 |
| Production | $43.00 | 10M | ~40 |
| Premium | $55.90 | 13M | ~52 |

Token offset ratio: up to ~1:8 across resolutions and input modes.
Validity: 3 months. Resolutions: 480P / 720P / 1080P / **4K**.

### Features vs kie.ai

| Feature | kie.ai | BytePlus |
|---------|--------|----------|
| Cost/720p 10s | **$0.50** | ~$1.61 |
| 4K | ❌ | ✅ |
| Multimodal refs (text+img+video+audio) | ❌ | ✅ |
| Seedance 2.0 mini | ❌ | ✅ |
| Billing | Per-second (predictable) | Token-based (variable) |
| Middleman | Revendeur | Direct ByteDance |

### Seedance 2.5 STATUS

**NOT on BytePlus API yet** (Aug 2026). Only on Dreamina (consumer portal, China-locked)
and **Higgsfield** (draw-to-direct feature, $49+/mo).
2.5 features leaked from internal docs:
- **180s long-form** (base video extensible +4 to +30s)
- **Smart Edit** (natural language video editing) + **Edit with marks** (brush-based local edits)
- **Multimodal References** (prompt + image + video + audio simultaneously)
- **Timestamp Text Control** (officialized — pattern validated by community)
- **Creative/Mask Transitions** (inter-clip transitions described in prompt)
- **Partial Elimination** (remove subtitles/BGM/objects from generated video)
- **Clay Renderer** (Maya/Blender bridge — 3D camera language → video generation)
- **Draw-to-Direct Camera Motion** (Higgsfield-exclusive, Aug 2026): draw a trajectory line on an image → camera follows that path. Kills text-prompting camera motion. Demo: orbit around Mona Lisa via circular line draw.
- **Prompt formula for real persons**: Hairstyle→subdivision, Clothing→texture, Tone, Character Material, Light/Shadow

### Seedance 2.5 Pricing — Multi-Platform Comparison (Aug 2026)

Source: higgsfield.ai/blog/seedance-2-5-pricing-2026 (official, Aug 6 2026)

All prices for **720p, 8s clip, monthly billing**, cheapest plan including Sd 2.5 on each platform:

| Platform | Cheapest plan w/ 2.5 | Credits in plan | Credits/clip | Cost/clip | Clips/month |
|----------|---------------------|----------------|-------------|-----------|-------------|
| **Higgsfield** | $49/mo | 1,000 | 52 | $2.55 | ~19 |
| **Dreamina** | $19/mo | 1,575 | 296 | $3.57 | ~5 |
| **Magnific** | $20/mo | 20,000 | 3,520 | $3.52 | ~5 |
| **OpenArt** | $14/mo | 4,000 | 1,040 | $3.64 | ~3 |
| **Runway** | $15/mo | 625 | 240 | $5.76 | ~2 |

**Higgsfield is cheapest per-clip AND most clips/month** despite highest entry plan.

Cost levers:
- **Resolution**: 480p draws ~24cr vs 52cr at 720p on Higgsfield → doubles monthly output (19→41 clips)
- **Mode**: Standard > Fast > Mini tiers within same model family
- **Credits don't roll over** — expire each billing cycle

Higgsfield free tier: 10cr/day, watermark, models limited, **NO Seedance 2.5** (requires $49+ plan).
kie.ai: **NO Seedance 2.5** (only 2.0, confirmed Aug 2026).

### Draw-to-Direct (Higgsfield Exclusive, Aug 2026)

Source: @tokufxug demo tweet (x.com/i/status/2086265541564715153, Aug 9 2026, 2061 likes)

**What it does**: Draw a line/trajectory on any image → Seedance 2.5 generates a camera motion
following that exact path. Eliminates text-prompting camera movements ("slow dolly zoom, 45° arc").

**Demo**: Orbital camera around Mona Lisa (circular line drawn → 360° orbit generated).

**Impact on static-image pipelines** (african-heroes, CES): Transforms Ken Burns-style
static images into true cinematic camera motion (parallax, orbit, push) without T2V generation
from scratch. Could replace PIL Ken Burns + zoompan ffmpeg pipeline.

**Access**: Higgsfield $49/mo plan minimum. Draw-to-direct is a Higgsfield UI feature,
not part of the Seedance 2.5 API spec — cannot be replicated via kie.ai or other platforms.
Higgsfield also has MCP & CLI access but unlimited promos do NOT apply there.

### Watchdog active

A silent cron job (`bin/check-seedance25-byteplus.sh`) monitors BytePlus product/docs/purchase pages
every 6h. Alerts when "Seedance 2.5" text appears. Job ID: `83d97b07a8f6`.

### Verdict

Garder kie.ai comme provider principal. BytePlus est 2-3x plus cher pour le même Seedance 2.0.
Monitorer pour le release 2.5 — quand ça arrive, ce sera le seul accès officiel aux features
(180s, Clay Renderer, Smart Edit). Le watchdog prévient automatiquement.

---

## seedance2.ai Pricing (Direct Platform)

Cheapest credit rates but **no API** — manual UI operation only.

| Model | Resolution | Credits/sec | 5s cost | With video ref (5s out + 3s in) |
|-------|-----------|------------|---------|-------------------------------|
| Seedance 2.0 | 480p | 6 | 30cr | 32cr |
| | 720p | 12 | 60cr | 64cr |
| | 1080p | 30 | 150cr | 160cr |
| | 4K | 70 | 350cr | 320cr |
| Seedance 2.0 Fast | 480p | 5 | 25cr | 24cr |
| | 720p | 10 | 50cr | 48cr |
| Seedance 2.0 Mini | 480p | 3 | 15cr | 16cr |
| | 720p | 6 | 30cr | 32cr |

## Higgsfield AI — Unlimited Burst Platform

**Source:** higgsfield.ai (Jul 2026), Seedance 2.5 teaser tweet

Higgsfield is a Seedance 2.0 hosting platform with its own MCP & CLI, Cinema Studio (web UI),
and Supercomputer (agent). Key differentiator: **14-day unlimited Seedance promotions** that
make burst generation free for a window.

### ⚠️ Critical limitation: Unlimited = Web-UI only
> *"Unlimited models and Free Generations on plans are accessible only via higgsfield.ai
> and are NOT accessible on MCP/CLI, Canvas or Supercomputer."*

The unlimited promotion **cannot** feed automated pipelines (prompt_optimizer.py, batch scripts).
It only works through the manual web UI. Paid credits work via MCP/CLI normally.

### Pricing (Annual, Jul 2026)

| Plan | Credits/mo | €/mo (annual) | Unlimited perk |
|------|-----------|---------------|----------------|
| Starter | 270 | €19 | ❌ No 7-day unlimited |
| Plus | 1,200 | €47 (was €59) | ✅ 7d Seedance 2.0 4K + 7d any model |
| Ultra | 3,000-9,000 | €99 (was €129) | ✅ Same as Plus + 8 parallel gens |

**5 free gens promo**: Seedance 2.0 4K 8s, no charge, card verification required.
Signup requires OAuth (Google/Apple/Microsoft) or email — **cannot be completed headlessly**.
Human intervention needed for account creation + card entry.

### Strategy for Cortex Leman pipelines
1. **Short burst**: Use 14-day unlimited window to mass-validate all 58 patterns in 4K,
   one test per pattern. Then return to kie.ai API for production automation.
2. **Character sheet factory**: Generate hundreds of Seedream/GPT Image 2 reference sheets
   during the unlimited window — these persist as assets after the promo ends.
3. **Seedance 2.5 monitor**: When 2.5 launches (teaser active Jul 2026), test longer scenes
   and native extension chaining (may obsolete pattern #47).
4. **MCP/CLI access**: Available with paid credits. Could integrate into prompt_optimizer.py
   as an alternative backend — but unlimited credits do NOT apply here.

### Platform comparison update

| Platform | API | Unlimited promo | 5s 720p Cost | Best For |
|----------|-----|-----------------|-------------|----------|
| **KIE.AI** | ✅ REST | ❌ | ~205cr ($1.03) | Automated pipelines, pay-per-use |
| **Higgsfield** | ✅ MCP/CLI (paid only) | ✅ 14-day (web only) | In-plan credits | Burst pattern validation, manual 4K |
| **EvoLink** | ✅ REST | ❌ | ~$0.99 (T2V) / ~$1.21 (ref) | API access to face+voice reference |
| **Maxfusion AI** | ❌ UI only | ❌ | Unknown (account-gated) | Manual face+voice work |
| **seedance2.ai** | ❌ UI only | ❌ | 60cr (~$0.30) | Cheapest manual generation |
| **Pippit** | ❌ UI only | ❌ | From $14.90/mo | Consumer/editing workflow |

## Decision matrix: which platform to use

| Need | Platform |
|------|----------|
| Automated pipeline (no human face) | **KIE.AI** (API, pay-per-use) |
| Burst pattern validation (14-day window) | **Higgsfield** (unlimited web UI) |
| Automated face+voice reference | **EvoLink** (API, Reference-to-Video) |
| Manual face+voice (best quality) | **Maxfusion AI** (ByteDance-authorized) |
| Cheapest manual one-off | **seedance2.ai** (lowest credit rates) |
| Consumer editing + publishing | **Pippit** ($14.90/mo subscription) |
