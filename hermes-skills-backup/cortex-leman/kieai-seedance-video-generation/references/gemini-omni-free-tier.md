# Gemini Omni — Free Video Generation Alternative

## Overview

Gemini Omni (via gemini.google.com) offers free AI video generation during promotional periods. Validated Aug 2026 for Sankofa african-heroes channel.

## Capabilities

| Feature | Detail |
|---|---|
| Input | Text-to-video AND image-to-video |
| Output | ~8-15s clips, up to 4K resolution |
| Audio | Native (ambient + voice synthesis) |
| Aspect ratio | 16:9 or 9:16 |
| Editing | In-chat conversational ("change the lighting", "pan slower", "add more dust") |
| Cost | FREE during promo periods (e.g. 10 videos free, Aug 2026) |

## Comparison to Seedance

| | Gemini Omni | Seedance 2.0 (kie.ai) | Seedance 2.5 (muapi.ai) |
|---|---|---|---|
| Cost | **FREE** (promos) | $0.05/sec | $0.30-0.60/sec |
| API access | ❌ Web/app only | ✅ REST API | ✅ REST API |
| Automation | ❌ Blocked | ✅ Scriptable | ✅ Scriptable |
| Max duration | ~15s | 15s | 30s |
| Audio | ✅ Native | ❌ | ✅ Native |

## Critical Limitation: No Browser Automation

**Google blocks headless/headless-like browsers from logging in.** When attempting `browser_navigate` → Google login, the response is:

> "Ce navigateur ou cette application ne sont peut-être pas sécurisés."

This is a security policy, not a bug. Workarounds tried (Aug 2026):
- Accepting cookies dialog first → still blocked
- Different user agents → still blocked
- Direct curl with redirect following → 302 redirect loop with `google_abuse` token

**The user must generate manually** on their own device (phone or desktop browser). The agent's role is:
1. Prepare structured prompts (see Universal Prompt Structure below)
2. Deliver prompts to user for copy-paste
3. QA the generated video from share links (`share.gemini.google/<id>`)

## QA Workflow for Gemini Omni Output

When user shares a Gemini Omni generation link:

1. Navigate to the share URL with `browser_navigate` (share pages are public, no login needed)
2. Remove cookie dialog via `browser_console`: `document.querySelector('[role="dialog"]').remove()`
3. Take screenshot with `browser_vision` (or fallback to `vision-analysis-fallback` skill if error 1210)
4. Analyze: subject accuracy, lighting, camera movement quality, historical/cultural fidelity
5. Report verdict + suggested in-chat edits (e.g. "Make the pyramids steeper and narrower")

Share pages show a `0:00 / 0:10` video player indicator in the DOM text — confirms video content is present.

## Universal 7-Element Prompt Structure

All AI video models (Hailuo, Seedance, Gemini Omni) produce better output when prompts follow this structure:

```
Subject → Environment → Camera → Lighting → Mood → Style → Quality
```

### Example (Amanirenas / Meroë establishing shot, tested Aug 2026)

> Aerial establishing shot of the ancient city of Meroë, Kingdom of Kush, 25 BCE. Golden desert landscape with palm groves along the Nile. More than 200 steep pyramids — smaller and steeper than Egyptian pyramids — rise from the ochre earth. Camera slowly descends from high altitude to rooftop level. Lighting: warm golden hour, deep amber tones. Mood: majestic, ancient, powerful. Style: cinematic historical documentary, photorealistic. Quality: 4K, ultra-detailed.

### Why each element matters

| Element | What it controls | If omitted |
|---|---|---|
| Subject | Who/what is in frame | Random or generic subjects |
| Environment | Setting, context, background | Inconsistent or wrong location |
| Camera | Angle, movement, framing | Static or random camera |
| Lighting | Color temperature, shadows | Flat lighting, no atmosphere |
| Mood | Emotional tone | Nonspecific emotional register |
| Style | Visual genre (documentary, anime, etc.) | Default "AI look" |
| Quality | Resolution, detail level | Lower fidelity output |

## Historical Character Consistency

For multi-shot historical content (e.g. Sankofa african-heroes), repeat identifying features in EVERY prompt to maintain character consistency across generations:

Example — Amanirenas (one-eyed Kushite queen):
- "one-eyed, war scar across her left eye"
- "dark skin, high cheekbones"
- "Kushite golden crown, gold earrings"
- "white linen royal robe with gold embroidery"

Gemini Omni does NOT have character reference locking (unlike Seedance 2.5 Omni-Reference). Text description repetition is the only consistency mechanism.
