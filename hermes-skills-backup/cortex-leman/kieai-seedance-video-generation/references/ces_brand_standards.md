# CES Brand Standards — Video Construction Spec

Consolidated from multiple sessions (Jul-Aug 2026). When building ANY Culture en Saveur video, follow these rules.

## 1. Intro Sequence (mandatory order)

Every CES video MUST start with:

1. **Stinger** — `assets/signature_ces_stingered.mp4` (3.5s). Encode with `-an` (no audio) for clean concat.
2. **Hook card** — cream background (#F5E6D3) with:
   - Logo (top, centered, 200px wide, proportional height)
   - Hook question/title in Playfair Display
   - "DU 10 AU 14 AOÛT" (Poppins SemiBold, terracotta)
   - "AU PETIT-LANCY" (Poppins Regular, ochre)
   - Divider line (ochre, 2px)
   - Contact: email, phone, @handle (Poppins Regular, cacao brown)
   - Tagline: "DÉCOUVRIR · INSPIRER · TRANSMETTRE" (Poppins SemiBold, terracotta, bottom)
3. **Content clips** — Seedance/Hailuo generated clips
4. **CTA card** — contact info + call to action

## 2. Fonts (NEVER use Montserrat)

```
assets/fonts/
  PlayfairDisplay-Variable.ttf    ← titles (font_title)
  PlayfairDisplay-Bold.ttf
  Poppins-Regular.ttf             ← body (font_body)
  Poppins-SemiBold.ttf            ← body medium
  Poppins-Bold.ttf                ← legacy fallback
  Poppins-Medium.ttf
  Montserrat-*.ttf                ← DEPRECATED, do not use
```

Helper functions (put at top of every build script):
```python
def font_title(size):
    return ImageFont.truetype(str(FONT_DIR / 'PlayfairDisplay-Variable.ttf'), size)

def font_body(size, medium=False):
    name = 'Poppins-SemiBold.ttf' if medium else 'Poppins-Regular.ttf'
    return ImageFont.truetype(str(FONT_DIR / name), size)

def font(size, bold=True):
    name = 'Poppins-Bold.ttf' if bold else 'Poppins-Regular.ttf'
    return ImageFont.truetype(str(FONT_DIR / name), size)
```

Subtitle ASS style line:
```
Style: Default,Poppins SemiBold,38,...
```

## 3. Voice (Edge TTS)

```python
# CORRECT — fr-CH voice for Swiss clients
cmd = ['edge-tts', '--voice', 'fr-CH-ArianeNeural', '--text', text, '--write-media', str(out)]

# WRONG — do not use for CES
cmd = ['edge-tts', '--voice', 'fr-FR-DeniseNeural', '--rate=-5%', ...]  # ❌
```

No rate adjustment needed for ArianeNeural.

## 4. Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| TERRACOTTA | #A0392B | Titles, accents, primary brand |
| TERRACOTTA_DARK | #492E21 | Dark backgrounds, CTA cards |
| OCHRE / SAFFRON | #C4956C | Dividers, secondary text, highlights |
| CREAM | #F5E6D3 | Backgrounds (hook cards), light text on dark |
| CACAO | #492E21 | Body text on cream backgrounds |

## 5. Segment Index Management (critical pitfall)

When modifying the `segments = [...]` list:

```python
# AFTER any add/remove, verify ALL downstream indices:
# - segments[N][1] references for each clip/card
# - segments[A:B] slices for menu card loops
# - all_segs = [...] concat list
# - vo_start offset (should = stinger_dur, NOT INTRO_DUR+STEAM_DUR+0.3)

# SAFE PATTERN: use named lookups instead of hardcoded indices
seg_lookup = {name: dur for name, dur, _ in segments}
# Then: seg_lookup["cta"] instead of segments[8][1]
```

**Rule**: after ANY change to segments, run `grep "segments\[" build_script.py` and verify every index.

## 6. Menu Cards

- One card per dish (count = number of dishes, never more)
- Dark overlay card on terracotta background
- Dish number (01, 02, 03...) in Poppins SemiBold, saffron
- Dish name in Playfair Display, cream
- Description in Poppins, cream
- Origin in Poppins, ochre
- Price in Playfair Display inside terracotta circle, cream text

## 7. Video Encoding

- **Source**: 1080×1920, libx264 medium, CRF 20-22, 24fps
- **Telegram**: 810×1440, libx264 ultrafast, CRF 28, maxrate 1800k, 128k AAC
- Always include `-movflags +faststart` for TG versions

## 8. Music

- Background music at volume 0.12
- `assets/music/ces_v2_main.mp3`

### Music start delay (when music should NOT play from the beginning)

By default music plays from t=0. When the user wants music to start at a specific segment (e.g., "que la music démarre à partir du deuxième clip"), use `adelay` on the music audio stream in the ffmpeg filter_complex:

```python
# Calculate delay = sum of all segment durations BEFORE the target clip
music_delay_ms = int((stinger_dur + segments[1][1] + segments[2][1]) * 1000)

# In the filter_complex:
f"[2:a]volume=0.12,adelay={music_delay_ms}|{music_delay_ms},afade=t=out:st={total_dur-1.5}:d=1.5[music];"
```

**Key**: the `adelay` must be applied BEFORE `afade` in the filter chain (delays first, then fade). The `|{music_delay_ms}` syntax applies the delay to both L and R channels. When segments are added/removed, recalculate `music_delay_ms` — it depends on the current segment order.

## 9. Prompt Writing (for Seedance clips)

Use Claude Fable 5 (`anthropic/claude-fable-5`) via OpenRouter as primary backend.
System prompt should specify: Seedance 2.0 expertise, triple identity lock, hex color palette, PROHIBITED list pattern.

## 10. CTA Factual QA (CRITICAL)

Before shipping ANY video, the CTA text (card + VO + subtitles) MUST be fact-checked against what the association actually does. AI-generated CTA copy can contain plausible-sounding but factually WRONG calls to action.

**Validated example (Aug 3, 2026):** Catering video CTA said "Réservez votre stand" (book your stand). The kiosk is run BY the association to sell food TO attendees — there are no stands to rent. The user caught this: "es tu sûre que cela est dans le programme". Fix: changed to "Venez goûter notre street food au kiosque !" across card + VO + subtitles.

**Rule:** the CTA call-to-action must describe what the VIEWER should do (come, taste, register, contact), never what the association internally manages. When in doubt about whether an action exists in the programme, flag it to the user BEFORE building — do not assume.

**Checklist before final build:**
1. Does the CTA action exist in the actual programme? (not invented)
2. Is the action directed at the viewer (not internal logistics)?
3. Are card text + VO + subtitle all consistent with each other?
4. Does the CTA match the video's topic (catering kiosk ≠ workshop registration)?
