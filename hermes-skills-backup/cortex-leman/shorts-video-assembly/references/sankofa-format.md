# Format Sankofa (african-heroes) — Documentaire historique burn-in

Différent du marketing funnel (CES): pas de Hook→Build→Climax→CTA, pas de pricing, pas de stinger.
Structure narrative en 3 actes type documentaire historique. Sous-titres ET titres de chapitre BRÛLÉS (hardcoded via ASS), pas SRT natif YouTube.

## Le Modèle Nzinga (standard Sankofa)

Analyse technique d'une vidéo de référence (Nzinga, 1080×1920, 24fps):

| Élément | Style | Position | Technique |
|---|---|---|---|
| **Titres de chapitre** | Jaune (#D7A050), gras, 56px | HAUT (Alignment=8, MarginV=60) | Burn-in ASS |
| **Sous-titres VO** | Blanc, 36px, contour noir + shadow | BAS (Alignment=2, MarginV=100) | Burn-in ASS |
| **Vidéo** | Full-bleed zoom-crop | Plein écran | `scale=-1:1920,crop=1080:1920` |
| **VO** | fr-FR-HenriNeural, rate -5%, pitch -5Hz | Audio principal | edge-tts |
| **Musique** | Volume 0.12 | Background | Optionnel |

### Structure 3 actes

Chaque vidéo suit 3 chapitres avec titres jaunes brûlés:

| Vidéo | Acte 1 | Acte 2 | Acte 3 |
|---|---|---|---|
| Nzinga | LE DÉFI | LA RÉPONSE | LA VICTOIRE |
| Amanirenas | L'ATTAQUE | LA GUERRE | LA VICTOIRE |
| Mansa Moussa | L'EMPIRE | LE PÈLERINAGE | L'HÉRITAGE |

## ASS Template (deux styles)

```ass
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Chapter,DejaVu Sans,56,&H0000D7FF,&H0000D7FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,3,0,8,80,80,60,1
Style: Subtitle,DejaVu Sans,36,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,80,80,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:18.00,Chapter,,0,0,0,,L'EMPIRE
Dialogue: 0,0:00:18.00,0:00:47.00,Chapter,,0,0,0,,LE PÈLERINAGE
Dialogue: 0,0:00:47.00,0:01:34.00,Chapter,,0,0,0,,L'HÉRITAGE
Dialogue: 1,0:00:00.10,0:00:04.81,Subtitle,,0,0,0,,Texte du sous-titre\\Nsur deux lignes
```

**Couleurs ASS (format &H00BBGGRR):**
- Jaune chapitre: `&H0000D7FF` (BGR inverse de #FFD700)
- Blanc sous-titre: `&H00FFFFFF`
- Noir contour: `&H00000000`
- Semi-transparent backdrop: `&H80000000` (alpha 80)

**⚠ Alignment ASS:** 8 = haut-centre, 2 = bas-centre. Ne PAS utiliser 2 pour les deux (erreur qui superpose chapitres et sous-titres — testé et corrigé sur Amanirenas V4, aout 2026).

**⚠ Channel handle YouTube:** Le handle (@xxx) **ne peut pas** être modifié via l'API YouTube Data v3 — seule YouTube Studio permet le changement (Settings → Channel → Basic info → Handle). L'API expose le handle en lecture seule via `snippet.customUrl`.

```bash
# 1. Zoom-crop clips → 1080×1920 full-bleed
for f in clips/v*.mp4; do
  ffmpeg -y -i "$f" -vf "scale=-1:1920,crop=1080:1920" \
    -an -c:v libx264 -preset fast -crf 20 "$WORK/$(basename $f)"
done

# 2. Concat clips
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy "$WORK/video.mp4"

# 3. Audio: VO + fade out
ffmpeg -y -i audio/vo.mp3 \
  -af "adelay=500|500,apad=pad_dur=2,afade=t=out:st=$(($DUR-2)):d=2" \
  -t "$DUR" -c:a aac -b:a 128k "$WORK/audio.m4a"

# 4. Mux video+audio
ffmpeg -y -i "$WORK/video.mp4" -i "$WORK/audio.m4a" \
  -c:v copy -c:a copy -shortest "$WORK/base.mp4"

# 5. Burn ASS (SLOW ~1fps on 1080×1920)
ffmpeg -y -i "$WORK/base.mp4" \
  -vf "subtitles=video.ass" \
  -c:v libx264 -preset fast -crf 22 -c:a copy \
  output/video_final.mp4
```

**⚠ Burn-in ASS encoding time:** ~1fps sur 1080×1920 = ~15min pour 72s de vidéo. Lancer en `background=true` avec `notify_on_complete=true`.

## Thumbnails Sankofa

### Format thumbnail

| Élément | Spec |
|---|---|
| Dimensions | 1080×1920 |
| Frame source | Frame CLEAN (sans sous-titres brûlés) extraite du clip |
| Titre | Blanc bold, 78px (DejaVu Sans Bold), ombre noire |
| Sous-titre | Orange #E89560, 36px, sous le titre |
| Gradient | Sombre bas → lumineux haut (pour lisibilité texte) |

### Extraction de frames clean (sans texte brûlé)

Les vidéos avec sous-titres brûlés contiennent du texte dans CHAQUE frame. Pour les thumbnails, il faut des frames SANS texte:

```bash
# Scan complet à 2fps (108 frames pour 54s de vidéo)
ffmpeg -y -i video.mp4 -vf "fps=2" /tmp/scan_%04d.jpg

# Sélection manuelle via vision model des frames sans texte
# Chercher: plans larges, paysages, portraits sans overlay
```

### Génération PIL

```python
from PIL import Image, ImageDraw, ImageFont

thumb = Image.open(clean_frame).resize((1080, 1920))
draw = ImageDraw.Draw(thumb)

# Gradient sombre bas
overlay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
for y in range(1200, 1920):
    alpha = int((y - 1200) / 720 * 180)
    ImageDraw.Draw(overlay).line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
thumb = Image.alpha_composite(thumb.convert('RGBA'), overlay).convert('RGB')
draw = ImageDraw.Draw(thumb)

# Titre (blanc + ombre)
title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 85)
for dx, dy in [(3,3),(2,2),(-2,2),(2,-2)]:
    draw.text((tx+dx, ty+dy), title, font=title_font, fill=(0,0,0,220))
draw.text((tx, ty), title, font=title_font, fill=(255,255,255))

# Sous-titre (orange Sankofa #E89560)
sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
draw.text((sx, sy), subtitle, font=sub_font, fill=(232,149,96))
```

## edge-tts paramètres (VO Sankofa)

```bash
# ✅ CORRECT — pitch en Hz, rate en %
edge-tts --voice "fr-FR-HenriNeural" --rate="-5%" --pitch="-5Hz" \
  -f script.txt --write-media vo.mp3 --write-subtitles vo.vtt

# ❌ ERREUR — pitch en % échoue (ValueError)
edge-tts --voice "fr-FR-HenriNeural" --rate="-5%" --pitch="-5%" ...
```

**Voix Sankofa standard:** `fr-FR-HenriNeural`, rate -5%, pitch -5Hz.
**VO script:** Texte continue, 3 paragraphes = 3 actes, ~80-95s selon densité.

## Upload YouTube (batch thumbnails)

Voir `scripts/yt_upload.py` pour l'upload complet. Pour les mises à jour de thumbnails par batch:

```python
# YouTube API rate-limite les uploads de thumbnails (~3-4 avant 429)
# Attendre 15s entre chaque upload
for vid_id, thumb_path, name in videos:
    resp = requests.post(
        f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        files={"file": ("thumbnail.jpg", open(thumb_path, 'rb'), "image/jpeg")}
    )
    time.sleep(15)  # anti-rate-limit
```

**⚠ Taille thumbnail:** <2MB. PIL génère du JPEG quality 95 typiquement 100-400KB → OK.

## Préparation de clips en attente de crédits

Quand les crédits Seedance/kie.ai sont épuisés, préparer le package complet:

```
project/
├── script_vo.txt          # Script narration 3 actes
├── audio/
│   ├── vo.mp3             # VO edge-tts générée
│   └── vo.vtt             # Sous-titres timed
├── video.ass              # ASS avec chapitres + sous-titres
├── prompts_seedance.md    # Prompts clips prêts à générer
├── build.sh               # Script build complet
└── clips/                 # (vide — remplir quand crédits disponibles)
```

**Workflow:** Script → VO → VTT → ASS → Prompts → (attente crédits) → Clips → Build → Thumbnail → Upload

## Package en attente de crédits (pattern Mansa Moussa, août 2026)

Quand tous les assets sont prêts mais les crédits vidéo indisponibles, le package est entièrement fonctionnel et reproductible:

| Fichier | Rôle | Génration |
|---|---|---|
| `script_vo.txt` | Script narration 3 actes | Manuscrit |
| `audio/vo.mp3` | VO edge-tts (93s) | `edge-tts --voice "fr-FR-HenriNeural" --rate="-5%" --pitch="-5Hz"` |
| `audio/vo.vtt` | Sous-titres timed | edge-tts output |
| `video.ass` | Chapitres jaunes + subs blancs | Python ASS generator |
| `prompts_seedance.md` | 11 prompts 9:16 prêts à copier | Manuscrit |
| `build_mansa.sh` | Script build complet | Bash |
| `thumbnail_mansa_moussa.jpg` | Template PIL (frame placeholder) | PIL drawtext |

**⚠ edge-tts pitch units:** `--pitch="-5Hz"` (CORRECT). `--pitch="-5%"` échoue avec ValueError. Cette unité a été confirmée plusieurs fois — ne pas regresser.

**Process complet de production (validé Amanirenas + Mansa Moussa):**
1. Script VO (3 paragraphes = 3 actes, ~80-95s)
2. edge-tts VO + VTT
3. Python ASS generator (3 chapitres, Alignment=8 haut, Alignment=2 bas)
4. ffmpeg build (zoom-crop → concat → VO mux → ASS burn-in)
5. Extraction frames clean pour thumbnail (scan 2fps → sélection vision)
6. PIL thumbnail (titre blanc 85px + sous-titre orange #E89560 38px + gradient bas)
7. Upload YouTube (yt_upload.py + thumbnail API)

## Batch thumbnail update (pattern août 2026)

Mettre à jour les thumbnails de vidéos **déjà publiées** en un seul batch:

```python
videos = [
    (video_id_1, "/path/to/thumb1.jpg"),
    (video_id_2, "/path/to/thumb2.jpg"),
    (video_id_3, "/path/to/thumb3.jpg"),
]
for vid, thumb_path in videos:
    resp = requests.post(
        f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}",
        headers={"Authorization": f"Bearer {access_token}"},
        files={"file": ("thumbnail.jpg", open(thumb_path, 'rb'), "image/jpeg")}
    )
    time.sleep(15)  # anti-rate-limit 429
```

**⚠ YouTube API limite les thumbnails à ~3-4 uploads rapides avant 429.** Toujours `sleep(15)` entre chaque. Convertir en JPEG q92 avant upload (<2MB obligatoire).
