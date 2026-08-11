# Gemini Omni Video Generation

## Overview

Google's Gemini Omni is a multimodal video generator available through the Gemini web app (gemini.google.com).
As of Aug 2026, Google periodically offers free generation promotions (e.g., 10 free videos through Aug 11, 2026).

## Specs

| Spec | Value |
|---|---|
| Duration | ~8-10s per clip |
| Resolution | 720p (web preview), up to 1080p/4K |
| Audio | Native (ambient + voice) |
| Input | Text-to-video, image-to-video |
| Editing | In-chat ("change lighting", "pan slower") |
| Access | gemini.google.com (browser, Google account required) |
| API | Google AI Studio (Gemini API) — separate from web app |
| Cost | Free tier promotions; otherwise requires Google AI subscription |

## Access Notes

- **Cannot automate login** from Hermes browser stack — Google blocks headless/automated browsers ("Ce navigateur ou cette application ne sont peut-être pas sécurisés").
- User must log in manually in their own browser.
- Agent can still prepare prompts and QA the results (user sends video files back via Telegram).
- Gemini Share links (share.gemini.google/XXX) are viewable by the agent via browser after dismissing cookie dialog, but generation must happen in user's authenticated session.

## Prompt Engineering for Gemini Omni

### Key Lessons (tested Aug 2026, Sankofa/Amanirenas)

1. **Keep prompts concise (80-100 words).** Shorter, direct prompts produce better results than long verbose ones. Gemini responds better to clarity than to cinematic jargon.
2. **Explicit physical descriptions for EVERY character.** Gemini defaults to light-skinned/western features. For African/Nubian characters, you MUST specify:
   - `dark-skinned` or `deep brown skin` (not just "African")
   - Hair texture: `natural curly black hair`
   - Body: `strong`, `tall`, specific features
   - Example: `Queen Amanirenas, a dark-skinned Nubian woman, high cheekbones, deep brown skin, natural curly black hair under a golden Kushite crown`
3. **Camera direction = one simple sentence.** Not technical Cinedance-level. Example: `Camera: slow tracking shot from behind, then crane up to reveal pyramids.`
4. **Structure: Subject → Environment → Camera → Lighting → Mood → Style → Quality.** This template works reliably.
5. **Retry with reinforced description** when the model misses physical traits (especially skin tone, wounds, scars). The second pass with stronger keywords usually fixes it.
6. **Violent scenes may need softening.** If Gemini refuses a battle scene, rephrase: `focus on the tension and the statue falling in slow motion` instead of explicit combat.

### Prompt Template

```
[Subject with explicit physical description: skin color, hair, age, clothing, props]. [Action/setting]. [Secondary characters with skin color]. [Background/environment details]. Camera: [one sentence]. Lighting: [type]. Mood: [adjectives]. Style: cinematic, photorealistic. Quality: 4K.
```

### What Gemini Omni Does Well

- Establishing shots (cities, landscapes, aerial)
- Golden hour / warm lighting
- Crowd scenes
- Architecture (pyramids, palaces, monuments)
- Close-up portraits when physical description is explicit enough
- Audio generation (ambient, crowd noise)

### What Gemini Omni Struggles With

- **Skin tone consistency** — defaults to lighter skin without explicit reinforcement
- **Wounds/bandages/scars** — often ignored on first pass
- **Historical accuracy** — armor and clothing may be generic
- **Fine text rendering** — same as all video AI models
- **Multiple specific actions in one clip** — keep to 1-2 beats

## QA Workflow (Agent-side)

When user sends a Gemini Omni video via Telegram:

1. Extract frames with ffmpeg: `ffmpeg -y -i video.mp4 -vf "select='eq(n\,0)+eq(n\,60)+eq(n\,120)+eq(n\,180)'" -vsync vfr /tmp/frame_%02d.jpg`
2. Analyze each frame with NVIDIA vision: `python3 ~/.hermes/skills/devops/vision-analysis-fallback/scripts/or_vision.py /tmp/frame_01.jpg "Describe what you see. Check: [criteria]"`
3. Compare against prompt criteria, report pass/fail per item
4. If skin tone or physical traits are wrong, generate a reinforced retry prompt

This pipeline is free (NVIDIA Llama 3.2 11B Vision) and takes ~5s per frame.
