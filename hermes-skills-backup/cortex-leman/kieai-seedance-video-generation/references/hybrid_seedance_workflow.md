# Hybrid Seedance + Motion Graphics Workflow

## When to use
- Budget-constrained video production (limited KIE credits)
- Need video action/movement but can't afford full Seedance generation for every segment
- Promo videos for small clients (food, events, products) where 1-2 hero clips suffice

## Concept
Instead of generating an entire video with Seedance (expensive: ~205 credits per 5s), generate **only the hero shot(s)** with Seedance and build the rest with PIL frame rendering + ffmpeg encoding. This produces a 20-30s video for ~200 credits instead of ~1000+.

## Architecture
```
[INTRO: PIL motion graphics] → [HERO: Seedance 5s clip] → [CARDS/MENU: PIL] → [CTA: PIL]
         3s                           5s                              14s               3s      = 25s total
```

## Workflow

### 1. Generate the Seedance hero clip
Use pattern #38 (Narrative Prose Sequence) for cooking/process — it's the easiest and cheapest (~100 words, 5s).

**Proven prompt (Culture en Saveur catering):**
```
Create a cinematic food video showing the preparation of African street food
at an outdoor market stall. Begin with close-up hands shaping spiced ground beef
into flatbread sandwiches, pressing dough firmly, spices and herbs visible on
the work surface. Then transfer them to a sizzling hot grill, oil shimmering,
smoke rising, flames licking. Finally, cut to a golden-brown hawawshi fresh off
the grill, split open to reveal juicy spiced filling, steam escaping, ready
to serve. Capture warm golden-hour lighting, lively street food atmosphere,
detailed food textures, smooth camera movement, mouth-watering close-ups.

Style: warm terracotta red, burnt copper ochre, deep cacao brown, soft ivory
cream color palette. Natural golden hour lighting.

<oil sizzling> <grill crackling> <knife slicing> <steam hissing>

No cold blue tones, no text overlays, no logos, no watermarks.
```

Cost: 205 credits, 5s, 720p 9:16, ~3 min generation time.

### 2. Build PIL motion graphics segments
Render intro/cards/CTA as PNG frames with PIL, encode to MP4 segments with ffmpeg.

Key tips:
- Use the project's brand palette (hex codes from charte officielle)
- Frame rate 24fps matches Seedance output (avoids interpolation on concat)
- Render each segment as a separate MP4 for clean concatenation

### 3. Scale Seedance clip to match motion graphics resolution
Seedance outputs 720x1280 (720p 9:16). If PIL renders at 1080x1920:
```bash
ffmpeg -y -i hero_720.mp4 -vf "scale=1080:1920:flags=lanczos" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -r 24 hero_scaled.mp4
```

### 4. Concatenate segments
```bash
# Create concat list
cat > concat.txt << 'EOF'
file 'intro.mp4'
file 'hero_scaled.mp4'
file 'menu_cards.mp4'
file 'cta.mp4'
EOF

# Concat (stream copy = instant, no re-encode)
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

### 5. Telegram compress
```bash
ffmpeg -y -i final.mp4 \
  -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280" \
  -c:v libx264 -preset fast -crf 26 -maxrate 3200k -bufsize 6400k \
  -c:a aac -b:a 128k -ac 2 -movflags +faststart output_TG.mp4
```

## Pitfall: ffmpeg -start_number placement
When extracting frames starting at offset N (e.g. skipping intro frames for menu segment):
```bash
# CORRECT: -start_number before -i
ffmpeg -y -framerate 24 -start_number 72 -i frame_%05d.png ...

# WRONG: -start_number after -i (ignored, starts at frame 0)
ffmpeg -y -framerate 24 -i frame_%05d.png -start_number 72 ...
```

## ⚠️ Post-build: Audio + Sous-titres + Intro (OBLIGATOIRE)

Le hybrid workflow produit naturellement une vidéo **muette et sans sous-titres**. Ces étapes ne sont pas optionnelles — sans elles l'utilisateur doit systématiquement les réclamer:

1. **Prépend l'intro/stinger du projet** avant le segment intro PIL (ex: 3s `intro_steam_spice.mp4` converti en 24fps, avant `intro.mp4` dans le concat list)
2. **Ajoute une piste audio**: musique de fond mixée à 0.12 volume avec fade in/out
3. **Burn-in les sous-titres ASS**: un sous-titre par segment/menu item, format ASS MarginV=120

Template complet post-concat:
```bash
# Audio: trim musique + fade + mix bas
ffmpeg -y -i music.mp3 -t 28 -af "afade=t=in:st=0:d=1,afade=t=out:st=26:d=2,volume=0.12" -c:a aac music.aac

# Final: mux vidéo + audio + burn sous-titres
ffmpeg -y -i video_concat.mp4 -i music.aac \
  -vf "subtitles=subtitles.ass" \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ac 2 -map 0:v:0 -map 1:a:0 -shortest video_complete.mp4
```

## Reference scripts
- Seedance hero generation: `/home/tars/culture-en-saveur/scripts/gen_catering_seedance.py`
- Full hybrid build (PIL + ffmpeg): `/home/tars/culture-en-saveur/scripts/build_catering_v2.py`
- Proven output (juil. 2026): 28s video avec intro + audio + sous-titres, 1.8MB TG, ~205 credits total

## Budget math
| Approach | Credits | Duration | Quality |
|----------|---------|----------|---------|
| Full Seedance (5 × 5s clips) | ~1025 | 25s | Best (all real footage) |
| **Hybrid (1 Seedance + PIL)** | **~205** | **25s** | Good (hero shot + branded cards) |
| PIL only (no Seedance) | 0 | 20s | Low (static, no action) |

The hybrid approach delivers 80% of the visual impact for 20% of the cost.
