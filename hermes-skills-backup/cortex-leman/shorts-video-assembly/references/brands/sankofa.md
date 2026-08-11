# Sankofa — Brand Specs (YouTube Shorts: African History)

## Channel
- **Name**: Sankofa (@SankofaHistoire)
- **Tagline**: "Retourne la chercher" (symbol Adinkra: apprendre du passé)
- **Email**: sankofa.histoire@gmail.com
- **Niche**: Histoire africaine pour public francophone (Shorts verticaux)

## Format

| Param | Value |
|---|---|
| Resolution | 1080×1920 (9:16 vertical) |
| FPS | 24 |
| Duration | 50-75s |
| Codec | h264 + AAC |
| Style | Cinematic photorealistic, biais corrected (dark-skinned explicit) |

## Format Standard (modèle Nzinga)

ALL Sankofa videos match this format. Reference video: Nzinga (k4bhvsb-cZE).

### Video Structure — TWO TEXT LAYERS (not one)

| Element | Position | Style | Colour |
|---|---|---|---|
| **Chapter title** | TOP center (Alignment=8) | Bold, 56px DejaVu Sans | Yellow `#D7A050` |
| **Subtitles (VO)** | BOTTOM center (Alignment=2) | Regular, 36px DejaVu Sans | White, black outline |
| **Voice-over** | Full duration | fr-FR-HenriNeural, rate=-5% | Edge TTS |
| **Video** | Full-bleed 1080×1920 | scale=-1:1920,crop=1080:1920 | No letterbox, no blur |

**⚠ CRITICAL**: Nzinga has TWO distinct text layers burned into the video:
1. **Chapter titles** (yellow, TOP) — 3 act titles that change through the video
2. **Subtitles** (white, BOTTOM) — VO transcription

These are NOT the same layer. Do not confuse them.

### 3-Act Narrative Structure

Every video uses 3 chapter titles displayed at the TOP in yellow:

| Act | Role | Nzinga example | Amanirenas example |
|---|---|---|---|
| Act 1 | Setup/conflict | LE DÉFI | L'ATTAQUE |
| Act 2 | Escalation/climax | LA RÉPONSE | LA GUERRE |
| Act 3 | Resolution/legacy | LA VICTOIRE | LA VICTOIRE |

### ASS Subtitle File (burned-in)

Both chapter titles and subtitles are in ONE ASS file with TWO styles:

```ini
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Alignment, MarginV, Encoding
Style: Chapter,DejaVu Sans,56,&H0000D7FF,&H00000000,&H00000000,1,3,8,60,1
Style: Subtitle,DejaVu Sans,36,&H00FFFFFF,&H00000000,&H80000000,0,2,2,100,1
```

**⚠ CRITICAL PITFALL (learned Aug 2026, Amanirenas V4):** Chapter style MUST use `Alignment=8` (top-center). Default ASS Alignment=2 places text at the bottom — if Chapter uses Alignment=2, chapters and subtitles overlap at the bottom, making both unreadable.

Always verify after first render:
- Chapter = top, yellow, bold
- Subtitle = bottom, white, regular
- No overlap

Subtitle `MarginV=100` for clear separation from bottom edge.

### Build Pipeline (ffmpeg)

```bash
# 1. Zoom-crop clips to 1080×1920 full-bleed (avoid letterbox/blur)
ffmpeg -i clip.mp4 -vf "scale=-1:1920,crop=1080:1920" -c:v libx264 -preset fast v_clip.mp4

# 2. Concatenate clips
ffmpeg -f concat -safe 0 -i concat.txt -c copy video.mp4

# 3. Add VO audio (delay + fade out)
ffmpeg -i video.mp4 -i vo.mp3 \
  -af "adelay=500|500,afade=t=out:st=79:d=2" \
  -t DUR -c:a aac -b:a 128k -ar 44100 -ac 2 base.mp4

# 4. Burn ASS subtitles (chapters + subtitles)
ffmpeg -i base.mp4 -vf "subtitles=file.ass" \
  -c:v libx264 -preset fast -crf 22 -c:a copy output.mp4
```

**⚠ Encoding budget:** ASS subtitle burn-in at 1080×1920 runs at ~5 fps. A 72s video (1740 frames) takes 5-6 minutes. Use `background=true` with `notify_on_complete=true`. Do NOT use foreground terminal (will timeout at 300s).

### VO Generation

```bash
edge-tts --voice fr-FR-HenriNeural --rate="-5%" \
  --file script_vo.txt --write-media vo.mp3 --write-subtitles vo.vtt
```

- Voice: fr-FR-HenriNeural (male, warm, authoritative)
- Rate: -5% for gravitas
- Volume: 2.5 (in mix)
- Script format: numbered lines, blank lines between
- Pas de loops: clips complets uniquement
- Cuts: ≤2s, jamais statique

## Thumbnails (Photo de Présentation)

Every video has a custom thumbnail — distinct from the video frames.

### Standard Style

| Element | Spec |
|---|---|
| Format | 1080×1920 JPEG (vertical) |
| Title | White bold, 85px DejaVu Sans, bottom-center, with shadow |
| Subtitle | Accent orange `#E89560`, 38px, below title |
| Background | Clean frame from video (NO burned text) |
| Gradient | Dark bottom 45% for text readability |

### ⚠ CRITICAL PITFALL: Burned Text in Source Frames (learned Aug 2026)

When extracting thumbnail frames from Sankofa videos that have **burned chapter titles + subtitles** (which ALL Sankofa videos do), most frames contain visible text. Using such a frame as thumbnail background creates visual noise and duplicates the chapter title.

**Detection — scan ALL frames at 2fps, measure white pixel density in text zones:**

```python
from PIL import Image
import numpy as np, os

for f in sorted(os.listdir('.')):
    if not f.startswith('frame_'): continue
    arr = np.array(Image.open(f))
    h = arr.shape[0]
    top_white = np.sum(np.all(arr[:int(h*0.12)] > 200, axis=2))
    bot_white = np.sum(np.all(arr[int(h*0.85):] > 200, axis=2))
    clean = top_white < 500 and bot_white < 500
    print(f"{f}: top={top_white} bot={bot_white} {'✅ CLEAN' if clean else '❌ TEXT'}")
```

Select ONLY frames where both zones have near-zero white pixel counts. Typically <15% of frames are truly clean.

**Alternative:** Use portrait/hero shot generated separately, or extract from the raw clip BEFORE subtitle burn-in.

### Thumbnail Generation (PIL)

```python
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ACCENT = (232, 149, 96)  # #E89560

def make_thumbnail(frame_path, title, subtitle):
    src = Image.open(frame_path)
    sw, sh = src.size
    scale = 1920 / sh
    src = src.resize((int(sw*scale), 1920), Image.LANCZOS)
    left = max(0, (src.width - 1080) // 2)
    thumb = src.crop((left, 0, left+1080, 1920)).convert('RGBA')
    
    # Dark gradient bottom 45%
    overlay = Image.new('RGBA', (1080, 1920), (0,0,0,0))
    draw_ov = ImageDraw.Draw(overlay)
    for y in range(1050, 1920):
        alpha = int(((y-1050)/870)**1.4 * 200)
        draw_ov.line([(0,y),(1080,y)], fill=(0,0,0,min(alpha,210)))
    thumb = Image.alpha_composite(thumb, overlay)
    
    draw = ImageDraw.Draw(thumb)
    
    # Title (white bold + shadow)
    title_font = ImageFont.truetype(FONT_BOLD, 85)
    bbox = draw.textbbox((0,0), title, font=title_font)
    tw = bbox[2]-bbox[0]; th = bbox[3]-bbox[1]
    tx = (1080-tw)//2; ty = 1450
    for dx,dy in [(3,3),(2,2),(-2,2),(2,-2)]:
        draw.text((tx+dx,ty+dy), title, font=title_font, fill=(0,0,0,220))
    draw.text((tx,ty), title, font=title_font, fill=(255,255,255))
    
    # Subtitle (accent orange + shadow)
    sub_font = ImageFont.truetype(FONT_BOLD, 38)
    bbox2 = draw.textbbox((0,0), subtitle, font=sub_font)
    sx = (1080-(bbox2[2]-bbox2[0]))//2
    sy = ty + th + 25
    for dx,dy in [(2,2),(1,1),(-1,1),(1,-1)]:
        draw.text((sx+dx,sy+dy), subtitle, font=sub_font, fill=(0,0,0,220))
    draw.text((sx,sy), subtitle, font=sub_font, fill=ACCENT)
    
    return thumb.convert('RGB')
```

## End Card

- **Fond**: Noir
- **Texte principal**: "ABONNE-TOI" en jaune
- **Texte secondaire**: "SANKOFA" + "Retourne la chercher" en blanc
- **Logo**: Flamme/continent africain, doré, coin bas-droite

## Vidéos publiées

| Titre | Video ID | Statut |
|---|---|---|
| Nzinga | k4bhvsb-cZE | Publié |
| Mami Wata | E4m25eP05oI | Publié |
| Abla Pokou | Eb_1LmHWjxc | Publié |
| Amanirénas | m3krL3cx_p4 | Publié |
| Mansa Moussa | YefZHMLWA60 | Privé (refonte) |

## Sujets planifiés

- Chaka Zulu — à venir
- Samori Touré — à venir

## File Paths

- Videos: `/home/tars/sankofa/<hero>/output/`
- Thumbnails: `/home/tars/sankofa/thumbnails/`
- VO scripts: `/home/tars/sankofa/<hero>/script_vo.txt`
- Build scripts: `/home/tars/sankofa/<hero>/build_v*.sh`
- ASS files: `/home/tars/sankofa/<hero>/<hero>_v*.ass`
- Clips (raw): `/home/tars/sankofa/<hero>/work_v2/`
