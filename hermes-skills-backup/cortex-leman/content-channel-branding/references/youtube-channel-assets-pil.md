# YouTube Channel Assets — PIL-Only Generation

When Playwright/browser is NOT available, generate YouTube channel assets (banner, thumbnails, profile pic) using pure PIL (Pillow). Validated August 2026 on Sankofa (african-heroes project).

## Why PIL-Only?

The branding skill's intro/stinger pipeline uses Playwright for HTML→PNG capture. But for **static assets** (banner, thumbnails, profile pic), PIL alone is sufficient and faster — no browser install needed. This is the fallback when Playwright is absent or broken.

## YouTube Spec Reference

| Asset | Dimensions | Notes |
|-------|-----------|-------|
| Profile picture | 800×800 (min 98×98) | Circle crop on YouTube |
| Banner | 2560×1440 total | **Safe zone: 1546×423 centered** (visible on all devices) |
| Thumbnail | 1280×720 (16:9) | Min 640×360 |
| Thumbnail (Shorts) | 1080×1920 (9:16) | Vertical |

### Banner safe zone math

```
Total:  2560 × 1440
Safe:   1546 × 423
X offset: (2560 - 1546) / 2 = 507px from left
Y offset: (1440 - 423) / 2 = 508px from top
```

Content outside the safe zone is only visible on desktop/TV and gets cropped on mobile.

## Banner Generation Pattern

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os, random

# Palette constants from brand identity
GOLD = (232, 163, 61)
TERRACOTTA = (181, 82, 46)
ANTHRACITE = (26, 26, 26)
SABLE = (244, 232, 208)

# Font paths — DejaVu is the Playfair substitute on Tars (pitfall #26)
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
FONT_SERIF_ITALIC = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf'

W, H = 2560, 1440
banner = Image.new('RGB', (W, H), ANTHRACITE)
draw = ImageDraw.Draw(banner)

# 1. Warm radial gradient (left terracotta glow + right gold glow)
for y in range(H):
    for x in range(0, W, 3):  # step 3px for speed
        dx_l = (x - W*0.15) / (W*0.35)
        glow_l = max(0, 1 - dx_l*dx_l) * 0.20
        dx_r = (x - W*0.82) / (W*0.25)
        glow_r = max(0, 1 - dx_r*dx_r) * 0.15
        glow = max(glow_l, glow_r)
        r = int(min(255, 26 + glow * 200))
        g = int(min(255, 26 + glow * 130))
        b = int(min(255, 26 + glow * 30))
        draw.rectangle([x, y, x+2, y], fill=(r, g, b))

# 2. Adinkra geometric pattern (fills right side — avoids "too empty" QA flag)
random.seed(42)
pattern = Image.new('RGBA', (W, H), (0,0,0,0))
pd = ImageDraw.Draw(pattern)
for i in range(35):
    cx = random.randint(int(W*0.45), W - 100)
    cy = random.randint(100, H - 100)
    size = random.randint(15, 60)
    alpha = random.randint(8, 25)
    shape = random.choice(['circle', 'concentric', 'cross', 'diamond'])
    # ... draw shape at (cx, cy) with (*PRIMARY, alpha)
banner = Image.alpha_composite(banner.convert('RGBA'), pattern).convert('RGB')

# 3. Safe zone content: logo + channel name + tagline + topics
sz_x = (W - 1546) // 2  # 507
sz_y = (H - 423) // 2   # 508
# Paste logo with glow, draw "SANKOFA" in serif gold, tagline in italic sable
# Topics: "◆ REINES    ◆ ROYAUMES    ◆ LÉGENDES" in bold terracotta

# 4. Corner ornaments (L-shaped gold lines, ~30% opacity)
# 5. Bottom tag: "RETOURNE LA CHERCHER" (small, centered, low opacity)
```

**Key technique:** the right-side pattern overlay (step 2) solved a QA failure — initial banner was flagged "right side too empty" (8.5→passing). Use `random.seed()` for reproducibility.

## Thumbnail Generation Pattern

```python
def create_thumbnail(character_img, title_main, title_sub, kicker, output_name):
    """
    Branded thumbnail: full-bleed character image right 72%,
    dark gradient overlay left for text readability,
    title in serif gold, kicker in terracotta, watermark logo.
    Gold border 3px.
    """
    W, H = 1280, 720
    # Scale character image to fill right 72%
    # Create dark gradient (255 at x=0 → 0 at x=W*0.55, power 1.5)
    # Paste "kicker" (top-left, small uppercase terracotta)
    # Paste "title_main" (large serif gold)
    # Gold divider line
    # Paste "title_sub" (italic serif sable)
    # Watermark logo (60×60, 40% opacity, bottom-right)
    # Gold border
```

**Pitfall:** if title text is long (e.g., "MAMI WATA"), the right edge may overlap the character image area. Run QA after generation.

## Profile Picture

Simple resize from the highest-quality logo source:
```python
logo = Image.open(logo_seedream_path)  # 2048×2048 source
profile = logo.resize((800, 800), Image.LANCZOS)
profile.save('profile_picture_800.png')
```

## Video Frame Extraction for Thumbnails

When the best character image is inside a video clip (b-roll), extract a still:
```python
import subprocess
subprocess.run([
    'ffmpeg', '-y', '-i', 'broll_video.mp4',
    '-ss', '2', '-frames:v', '1',
    '-q:v', '2', '/tmp/still.png'
], capture_output=True)
```

## QA Workflow for Generated Assets

GLM-5.2 has no native vision (error 1210). Use the OpenRouter Gemini fallback:

```bash
python3 ~/.hermes/skills/devops/vision-analysis-fallback/scripts/or_vision.py \
    "/path/to/asset.png" \
    "QA: Check (1) text readability, (2) image visibility, (3) contrast, (4) composition balance. Score /10."
```

**Checklist per asset:**
- [ ] Channel name readable at thumbnail size (1280×720 and 320×180 preview)
- [ ] Tagline visible in safe zone (banner)
- [ ] No text overlapping character image
- [ ] Primary color dominates
- [ ] Brightness ≥0.95 on subject
- [ ] Gold border visible
- [ ] Score ≥8/10 from Gemini QA

**Common QA failures & fixes:**
| Failure | Fix |
|---------|-----|
| Right side empty (banner) | Add geometric pattern overlay (step 2 above) |
| Title overlaps image | Reduce font size or shorten title |
| Low contrast text | Add subtle text shadow or increase gradient opacity |
| Logo too small | Increase logo_size in safe zone |
