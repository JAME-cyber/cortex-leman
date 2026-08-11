# Gemini Omni Video Generation (Aug 2026)

Model-specific knowledge for Google Gemini Omni T2V (free promo, 10 clips/account, 10s/clip, 1080p).

Tested Aug 2026 on Sankofa project (Queen Amanirenas of Kush) — 13 generations across 2 accounts.

## What Works (Green Zone)

| Pattern | Why | Example Result |
|---|---|---|
| **Single character + strong decor** | Model locks onto one subject, no drift | Throne room portrait, establishing landscape |
| **Establishing shots / landscapes** | No complex motion to track | Meroë pyramids aerial, Nile river dawn |
| **Battle scenes (wide)** | Chaos hides inconsistencies | Syène battle, Roman legion advancing |
| **Documentary nature shots** | Static subjects, slow camera | Pyramids today, no people |
| **Portraits (close-up, static camera)** | Face detail is strong | Amanirenas hero portrait (best result) |

## What Fails (Red Zone)

| Pattern | Why | Fix |
|---|---|---|
| **Multi-character dialogue scenes** | Model loses subject tracking, drifts to generic | Simplify to 2 characters max, face-to-face |
| **Crowd + hero interaction** | Hero disappears mid-clip | Remove crowd, focus on hero alone |
| **"Bloody bandage" / gore terms** | Safety filter hard-blocks generation | Use "white linen bandage" or just "bandage" |
| **Consecutive prompts in same chat** | Context bleed — model amalgamates previous prompt with current | **New chat for every prompt** |
| **Implicit skin tone** | Defaults to light skin if not explicit | Always write "dark-skinned", "deep brown skin" |
| **Wound/bandage without physical detail** | Ignored if not prominent enough | Lead with "bandage covering her right eye" in first sentence |

## Prompt Template (80-100 words optimal)

```
[CHARACTER: name, skin tone explicitly, age, key physical features in 1 sentence].
[ACTION: single clear action].
[SETTING: 1 location, 1-2 visual details].
[SECONDARY ELEMENTS: max 2 other characters or objects].
[Camera: ONE simple instruction — e.g. "slow push-in", "tracking shot from behind"].
[Lighting: ONE phrase — e.g. "golden hour", "torchlit interior"].
[Style: cinematic, photorealistic. Quality: 4K.]
```

### Example (Portrait — scored Excellent)

```
Extreme close-up portrait of Queen Amanirenas of Kush. A dark-skinned Nubian woman in her 40s with high cheekbones, a white linen bandage covering her right eye, her left eye blazing with fierce determination. She wears a golden Kushite crown with serpent motifs, heavy gold earrings. Her natural curly black hair frames her face. Torch light flickers across her face, half in warm orange light, half in deep shadow. Camera: static close-up, eye-level. Style: cinematic portrait, photorealistic, chiaroscuro. Quality: 4K, detailed skin texture.
```

## Retry Strategy (Validated)

When a generation fails or scores low:

1. **Identify the specific failure** via frame extraction QA (ffmpeg → or_vision.py)
2. **Reinforce the missing element** — move it to first sentence, add physical detail
3. **Simplify** — remove secondary elements, reduce to 1 character + 1 decor
4. **Soften safety triggers** — "bloody" → "white linen", "severed head" → "bronze head"

Retry success rate: 2/2 (100%) on reinforced prompts — both retries scored higher than originals.

## QA Workflow (Agent-Side)

Since the user generates in their browser, the agent receives video files. QA pipeline:

```bash
# 1. Extract 4 frames from the 10s clip
ffmpeg -y -i video.mp4 -vf "select='eq(n\,0)+eq(n\,60)+eq(n\,120)+eq(n\,180)'" -vsync vfr /tmp/frame_%02d.jpg

# 2. Analyze first + last frame with vision (NVIDIA free)
python3 ~/.hermes/skills/devops/vision-analysis-fallback/scripts/or_vision.py \
  /tmp/frame_01.jpg "Specific checklist questions about the intended content"

# 3. Compare against prompt intent, produce verdict table
```

**Key insight**: First frame is most faithful. Mid-frames drift. If first + last pass, clip is usable.

## Access Constraints

- **Headless browser login = IMPOSSIBLE.** Google blocks "non-secure browser/app". User must generate manually in their browser.
- **Share links** (`share.gemini.google/XXX`) — readable but heavy cookie consent dialogs. Content accessible via `browser_console` DOM extraction.
- **10 free clips per account.** Multiple Google accounts = multiple batches.
- **No API access** (web UI only, Aug 2026).

## Known Limitations

- No character consistency between clips (unlike Seedance Omni-Reference)
- No reference image input (text-only T2V)
- 10 seconds max per clip
- Clips are silent (no audio generation)
- Clips silent — VO/music must be added in post (ffmpeg)
