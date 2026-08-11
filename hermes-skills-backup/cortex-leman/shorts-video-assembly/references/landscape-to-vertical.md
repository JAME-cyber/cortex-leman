# Landscape → Vertical Conversion (16:9 clips to 9:16 Shorts)

## Problème

Les modèles de génération vidéo (Gemini Omni, Hailuo, Seedance) produisent souvent en 16:9 (1280×720), mais YouTube Shorts / TikTok / Reels exigent du 9:16 (1080×1920).

## ✅ Solution validée : Zoom-crop plein écran (APPROUVÉ user)

**Utiliser TOUJOURS cette approche par défaut.**

```bash
ffmpeg -y -ss START -t DURATION -i input.mp4 \
  -vf "scale=-1:1920,crop=1080:1920,fps=24" \
  -c:v libx264 -preset ultrafast -crf 20 -an \
  output_vertical.mp4
```

**Comment ça marche :**
1. `scale=-1:1920` : augmente la hauteur à 1920px (garde le ratio → largeur ~3414px pour un 1280×720)
2. `crop=1080:1920` : crop le centre depuis l'image large
3. Résultat : plein écran, aucun bord flou, aucune bande

**Trade-off :** On perd ~68% de la largeur de l'image (crop latéral). Pour des portraits centrés et des scènes avec un point focal central, c'est parfait.

**Vérification pixel anti-bands :** std > 20 sur les lignes du bord = contenu réel (pas de bande). std < 15 = bande floue ou barre noire.

```python
from PIL import Image
import numpy as np

def has_letterbox(img_path, threshold=15):
    img = Image.open(img_path)
    arr = np.array(img)
    h = arr.shape[0]
    top_std = np.mean([np.std(arr[y]) for y in range(0, 60, 10)])
    bot_std = np.mean([np.std(arr[y]) for y in range(h-60, h, 10)])
    return top_std < threshold or bot_std < threshold
```

## ❌ Approche REJETÉE : Blurred background fill

```bash
# NE PAS FAIRE — bands floues visibles → REJET USER (Amanirenas V1, août 2026)
ffmpeg -i clip.mp4 \
  -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30[bg];
   [0:v]scale=1080:-1[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[v]" \
  output.mp4
```

**Raison du rejet :** Le user identifie immédiatement les "bandes floues en haut et en bas" comme amateur. Cette approche a été utilisée en V1 et rejetée explicitement. **Ne plus jamais utiliser pour les Shorts Sankofa.**

## ⚠️ Sous-titres : Style Sankofa validé (APPROUVÉ user)

Le style de sous-titres précédent (V1) **REJETÉ** par le user : sous-titres trop grands, occupaient tout l'écran, boîte noire opaque.

**Style correct (V2, validé août 2026) :**

```bash
ffmpeg -y -i input.mp4 \
  -vf "subtitles=subs.vtt:force_style='FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=60'" \
  -c:v libx264 -preset ultrafast -crf 20 -c:a copy \
  output.mp4
```

| Paramètre | Valeur V1 (REJETÉE) | Valeur V2 (VALIDÉE) | Raison |
|---|---|---|---|
| FontSize | 28 | **16** | Trop grand, envahissant |
| BorderStyle | 3 (opaque box) | **1** (outline only) | Boîte noire masque la vidéo |
| Alignment | 8 (top) | **2** (bottom) | Les ST en haut couvrent les visages |
| MarginV | 100 | **60** | Plus proche du bord, discret |
| Outline | 3 | **2** | Plus fin, moins lourd |
| Shadow | 1 | **0** | Pas d'ombre |

**Référence visuelle :** Les Shorts Sankofa (Nzinga `k4bhvsb-cZE`, Mami Wata `E4m25eP05oI`, Abla Pokou `Eb_1LmHWjxc`) ont des sous-titres en **bas**, petit format, texte blanc avec contour noir. Analyser une frame avec `or_vision.py` pour confirmer.

## Pipeline complet : 9 clips landscape → Short vertical

```bash
#!/bin/bash
# Step 1: Convert each clip to full-bleed vertical
for clip in clips/*.mp4; do
    ffmpeg -y -ss 0.5 -t 8.0 -i "$clip" \
      -vf "scale=-1:1920,crop=1080:1920,fps=24" \
      -c:v libx264 -preset ultrafast -crf 20 -an \
      "work/v_$(basename $clip)"
done

# Step 2: Concat
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy video_concat.mp4

# Step 3: VO with delay + fade out
ffmpeg -y -i audio/vo.mp3 \
  -af "adelay=500|500,apad=pad_dur=3,afade=t=out:st=78:d=3" \
  -t VIDEO_DURATION -c:a aac -b:a 192k vo_final.m4a

# Step 4: Mux
ffmpeg -y -i video_concat.mp4 -i vo_final.m4a -c:v copy -c:a copy -shortest with_audio.mp4

# Step 5: Burn subtitles (BOTTOM, small, outline only — Sankofa style)
ffmpeg -y -i with_audio.mp4 \
  -vf "subtitles=subs.vtt:force_style='FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=60'" \
  -c:v libx264 -preset ultrafast -crf 20 -c:a copy \
  output/short_final.mp4
```

## Encoding specs (1080×1920 master)

| Param | Value | Note |
|---|---|---|
| Resolution | 1080×1920 | 9:16 standard Shorts |
| FPS | 24 | Match source (Gemini Omni native) |
| Codec | libx264 | H.264 |
| CRF | 20 | High quality |
| Preset | ultrafast | CPU limité — voir clip-vo-timing.md pitfall |
| Audio | AAC 192k | |
| Container | MP4 +faststart | Web-optimized |
