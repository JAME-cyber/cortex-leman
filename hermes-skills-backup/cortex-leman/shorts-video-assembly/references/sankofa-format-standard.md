# Sankofa Format Standard (modèle Nzinga)

## Règle d'or
**Nzinga (@SankofaHistoire, k4bhvsb-cZE) est le modèle unique.** Toutes les vidéos Sankofa doivent suivre le même format de présentation : voix off + sous-titres brûlés + titres de chapitre. Pas d'exception.

L'utilisateur a explicitement dit : "Nzinga est notre modèle video, toutes les vidéos doit être du même modèle, voix off, sous-titre, présentation."

## Structure narrative : 3 actes
Chaque vidéo est divisée en 3 chapitres avec titre jaune en haut.

| Acte | Nzinga | Amanirenas |
|------|--------|------------|
| 1 | LE DÉFI (0-18s) | L'ATTAQUE (0-24s) |
| 2 | LA RÉPONSE (18-36s) | LA GUERRE (24-50s) |
| 3 | LA VICTOIRE (36-54s) | LA VICTOIRE (50-81s) |

Les titres sont courts (1-2 mots), dramatiques, en majuscules.

## Spécifications visuelles (mesurées pixel par pixel sur Nzinga 1080x1920)

### Titres de chapitre (HAUT)
- Position : y ≈ 4-8% du haut (~75-150px sur 1920)
- Couleur : jaune doré RGB ~ (205, 161, 96) → ASS `&H0000D7FF`
- Font : bold, taille ~56px (ASS PlayResY=1920)
- Pas de background box — texte direct sur l'image

### Sous-titres VO (BAS)
- Position : y ≈ 88-95% du bas (~1690-1825px sur 1920)
- Couleur : blanc `&H00FFFFFF`
- Outline : noir, 2px `&H00000000`
- BackColour (shadow) : noir semi-transparent `&H80000000`
- Font : regular, taille ~36px
- Alignment : 2 (bottom-center)

### Format technique
- 1080×1920 (9:16 vertical)
- 24fps
- h264 + AAC stereo 44100
- Full-bleed (scale=-1:1920,crop=1080:1920 — PAS de letterbox, PAS de flou/pad)

## Pipeline de production

### 1. Clips source
Générer via Seedance/Gemini (voir kieai-seedance-video-generation). QA chaque clip avec or_vision.py.

### 2. Voix off
```bash
edge-tts --voice fr-FR-HenriNeural --rate=-5% \
  --text "$(cat script_vo.txt)" \
  --write-media vo.mp3
```

### 3. Sous-titres ASS (chapitres + subs)
Fichier `.ass` avec 2 styles :
- `Chapter` (jaune, haut, bold) — 3 cues pour les 3 actes
- `Subtitle` (blanc, bas, outline noir) — cues syncés à la VO

Voir template : `templates/sankofa_subtitle_template.ass`

### 4. Assemblage FFMPEG
```bash
# Concat clips (déjà zoom-croppés en 1080x1920)
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy video.mp4

# Ajouter VO
ffmpeg -y -i video.mp4 -i vo.mp3 \
  -af "adelay=500|500,apad=pad_dur=2,afade=t=out:st=79:d=2" \
  -c:v copy -c:a aac -b:a 128k -shortest base.mp4

# Burn-in ASS subtitles
ffmpeg -y -i base.mp4 \
  -vf "subtitles=amanirenas.ass" \
  -c:v libx264 -preset fast -crf 22 -c:a copy output.mp4
```

⚠ **Le burn-in ASS sur 1080x1920 est lent** (~1.8fps sur machine 3.8GB RAM). Prévoir background + notify_on_complete. Timeout 300s insuffisant, utiliser 600s+.

### 5. Thumbnail (PIL)
Voir `scripts/generate_sankofa_thumbnail.py` pour le template.
- Extraire frame CLEAN (sans texte brûlé) au milieu de la vidéo
- Compositer : titre blanc bold 85px + sous-titre orange #E89560 38px
- Gradient sombre bas pour lisibilité
- Format 1080×1920

## Thumbnails : extraction de frames sans texte brûlé

Les vidéos Sankofa ont des titres de chapitre ET sous-titres brûlés. Pour les thumbnails, il faut des frames CLEAN.

**Méthode : scan pixel**
```python
from PIL import Image
import numpy as np

arr = np.array(Image.open('frame.jpg'))
h = arr.shape[0]
# Top 15% = zone titre chapitre, Bottom 15% = zone sous-titres
top_white = np.sum(np.all(arr[:int(h*0.15)] > 200, axis=2))
bot_white = np.sum(np.all(arr[int(h*0.85):] > 200, axis=2))
# Score < 500 = frame clean (pas de texte)
```

Scan à 2fps sur toute la vidéo, garder uniquement les frames avec score < 500.

## Évolution des versions (leçons apprises)
- **V1 (blur/pad)** : bandes floues haut/bas → REJETé par l'utilisateur
- **V2 (zoom-crop)** : full-bleed OK mais pas de chapitres/sous-titres → incomplet
- **V3 (hook text)** : texte d'accroche overlay → mauvaise interprétation du besoin
- **V4 (format Nzinga)** : ASS avec chapitres jaunes + sous-titres blancs = BON FORMAT

## Vidéos publiées
| Vidéo | YouTube ID | Status |
|-------|-----------|--------|
| Nzinga | k4bhvsb-cZE | Live (modèle) |
| Mami Wata | E4m25eP05oI | Live |
| Abla Pokou | Eb_1LmHWjxc | Live |
| Mansa Moussa | YefZHMLWA60 | Privé (refonte) |
| Amanirenas | — | Prêt (V4 + thumbnail) |
