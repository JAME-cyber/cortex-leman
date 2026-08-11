# YouTube Shorts Assembly Pipeline

Pattern validé Aug 2026 sur 4 Shorts Sankofa (Nzinga, Mami Wata, Abla Pokou, Mansa Moussa).
Format: 1080×1920 vertical, <60s pour feed Shorts viral.

## Principe

Chaque Short = **Intro signature** (5s) + **Clips vidéo Seedance** (chacun utilisé UNE FOIS, JAMAIS bouclés) + **CTA fullscreen** + BGM + watermark.
Préférence utilisateur EXPLICITE (correction Aug 2026): 
- **JAMAIS de loops** (`-stream_loop -1` = rendu cheap/amateur). Chaque clip est lu une seule fois.
- **JAMAIS de Ken Burns** si on a assez de clips vidéo pour couvrir la durée audio.
- **Les clips doivent coïncider avec la narration**: le clip du trône joue pendant le hook sur le trône, le clip de bataille pendant la stratégie, etc.
- **Freeze-frame** (`tpad=stop_mode=clone`) pour combler les petits gaps (0.5-2.5s) quand clips < audio. Acceptable, pas un loop.

## Duration budgeting (CRITIQUE)

```
total = intro_dur + content_dur + 0 (CTA inclus dans content)
total DOIT être < 60s pour le feed Shorts
```

| Intro | Budget content | Exemple |
|-------|---------------|---------|
| 5s (avec audio) | ≤54s | 3 beats × ~15s + CTA 5s = ~50s ✅ |
| Pas d'intro | ≤59s | 4 beats × ~13s + CTA 5s = ~57s ✅ |

**Règle**: si total > 60s, couper le segment le moins dramatique. Ne JAMAIS raccourcir l'intro (c'est la signature de marque).

## Structure d'un segment (clips-only, V5)

```python
SEGMENTS = [
    # Chaque segment: 1-2 clips vidéo (5s chacun), placés au bon moment narratif
    {'audio': '01_hook.mp3',       'clips': ['02_tapis_scene.mp4', '00_nzinga_floor.mp4'],  'caption': 'cap_01_hook.png',  'overlay': True},
    {'audio': '02_revelation.mp3', 'clips': ['01_nzinga_portrait.mp4', '09_princess.mp4'], 'caption': 'cap_02_rev.png',   'overlay': True},
    # ...
    # CTA = pas de clips, caption fullscreen
    {'audio': '09_cta_short.mp3',  'clips': [], 'cta': True},
]
```

**Règle de mapping clip↔narration**: le clip visuel DOIT correspondre au contenu audio.
- Hook "gouverneur sur trône" → clip du trône (02_tapis_scene)
- Stratégie "guerriers Imbangala" → clip de bataille (04_imbangala_battle)
- Victoire "traité 1657" → clip du traité (08_nzinga_old_treaty)
**QA obligatoire**: vérifier via vision_analysis que chaque frame correspond à la narration.

## Build order (validé)

1. **Build chaque segment** (scale clips + concat + optional caption overlay + freeze-frame si gap)
2. **Concat segments** (filter_complex concat, pas demuxer — codec mismatch fréquent)
3. **Concat audio** TTS (demuxer concat OK pour mp3)
4. **Merge** video + audio
5. **Prepend intro**: re-encode intro en même codec (libx264, 24fps, 1080×1920) → filter concat video + filter concat audio
6. **Final**: add BGM (-28dB) + watermark (overlay bottom-right)

## Commandes clés

### Clip vidéo SANS boucle — pattern clips-only (VALIDÉ V5)
```bash
# ❌ JAMAIS ÇA — loop = cheap:
# ffmpeg -y -stream_loop -1 -i clip_5s.mp4 -t 15.8 ...

# ✅ PATTERN CLIPS-ONLY: chaque clip joué une fois, freeze-frame pour combler
# 1. Scale chaque clip à 1080x1920
ffmpeg -y -i clip_5s.mp4 \
  -vf "scale=1080:1920:flags=lanczos,format=yuv420p" \
  -c:v libx264 -preset ultrafast -crf 20 -pix_fmt yuv420p -r 24 out.mp4

# 2. Si N clips (N×5s) < audio_dur, freeze la dernière frame pour combler
GAP=$(echo "$AUDIO_DUR - $CLIPS_TOTAL" | bc)
ffmpeg -y -i concatenated_clips.mp4 \
  -vf "tpad=stop_mode=clone:stop_duration=${GAP},format=yuv420p" \
  -c:v libx264 -preset ultrafast -crf 20 -pix_fmt yuv420p -r 24 extended.mp4
```

### Caption overlay sur clip
```bash
ffmpeg -y -i seg_video.mp4 -i caption.png \
  -filter_complex "[0:v][1:v]overlay=0:0[v]" -map "[v]" \
  -c:v libx264 -preset ultrafast -crf 20 -pix_fmt yuv420p -r 24 out.mp4
```

### Prepend intro (video)
```bash
ffmpeg -y -i intro_norm.mp4 -i content_full.mp4 \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" -map "[v]" \
  -c:v libx264 -preset ultrafast -crf 22 -pix_fmt yuv420p -r 24 full_video.mp4
```

### Final mix (intro+content video + VO audio + BGM + watermark)
```bash
ffmpeg -y -i full_video.mp4 -i full_audio.aac -i bgm.mp3 -i watermark.png \
  -filter_complex \
    "[0:v][3:v]overlay=x=W-w-20:y=H-h-20[vout];" \
    "[1:a]volume=1.0[a1];" \
    "[2:a]volume=-28dB,afade=t=in:st=0:d=1,afade=t=out:st={total-2}:d=2[bgm];" \
    "[a1][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset ultrafast -crf 22 -c:a aac -b:a 192k -shortest \
  -pix_fmt yuv420p -r 24 output.mp4
```

## Pitfalls validés

### 0. LOOP DE CLIPS = REJET UTILISATEUR (CRITIQUE)
`-stream_loop -1` pour étendre un clip de 5s sur un audio de 15s produit un rendu cheap/amateur.
L'utilisateur a EXPLICITEMENT rejeté cette approche (V3 → V5).
**Fix**: Utiliser chaque clip UNE SEULE FOIS. Si clips insuffisants, freeze-frame (`tpad=stop_mode=clone`) pour les petits gaps (≤2.5s). Ne JAMAIS boucler.
Voir pattern clips-only ci-dessus.

### 0b. WATERMARK ALPHA TROP FAIBLE = INVISIBLE
Le watermark Sankofa (RGBA 1080×1920, logo 79×79px en bas-droite) avait un alpha max de 41/255 (16%) = invisible sur le rendu final.
**Fix**: Boost alpha à minimum 150/255 (59%). Vérifier avec vision analysis sur une frame full-res.
```python
from PIL import Image; import numpy as np
arr = np.array(Image.open('watermark.png'))
arr[:,:,3] = np.where(arr[:,:,3] > 0, np.minimum(arr[:,:,3] * 4, 150), 0).astype(np.uint8)
Image.fromarray(arr, 'RGBA').save('watermark_boosted.png')
```

### 1. zoompan timeout même sur image pre-scaled
Même avec PIL pre-resize à 1080×1920, `zoompan` sur 422 frames (17.6s × 24fps) timeout à 60s.
**Fix**: Utiliser `crop` filter avec expressions `t` (voir `ffmpeg-kenburns-pitfalls.md`), OU utiliser un clip vidéo Seedance à la place.

### 2. Subagent delegation pour ffmpeg builds = TIMEOUT
delegate_task a un timeout de 600s. Les builds multi-segments (5+ segments × encode + concat + merge) dépassent régulièrement ce budget.
**Fix**: Exécuter les builds en-process via `execute_code` ou `terminal`, pas via subagent.
Les subagents sont OK pour: génération de scripts, QA visuelle, écriture de captions. PAS pour: builds ffmpeg lourds.

### 3. Concat demuxer vs filter concat
Le demuxer `concat` (`-f concat -safe 0 -i list.txt`) échoue si les segments ont des codecs/résolutions/fps différents.
**Fix**: Toujours normaliser tous les segments au même codec (libx264, crf 20, 24fps, 1080×1920, yuv420p) AVANT concat, puis utiliser filter_complex concat pour la sécurité.

### 4. YouTube thumbnail size limit
Les thumbnails PNG générés peuvent dépasser 2MB. Compresser avec PIL:
```python
img.save(path, "JPEG", quality=85)  # PNG → JPEG réduit drastiquement
```

### 5. YouTube API rate limiting
Les uploads de thumbnails en rafale peuvent être rate-limited (403). Prévoir un retry différé (cron 30min).

## Config TTS Edge (référence)

```python
import edge_tts
voice = "fr-FR-HenriNeural"  # VO masculine FR, pitch -5% pour gravité
# Rate: default, pitch: -5% via communicate(text, voice, pitch="-5Hz")
```

## QA Workflow

1. Extraire frames à moments-clés narratifs (pas juste 25/50/75%) — ex: frame pendant le clip du trône, pendant le clip de bataille
2. Vision analysis: résolution, captions lisibles, watermark visible (alpha ≥150), artefacts
3. **Cohérence clip↔narration**: vérifier que chaque frame montre ce que l'audio décrit (trône pendant hook, bataille pendant stratégie, etc.)
4. Verdict par vidéo: APPROVED ou NEEDS FIX
5. Peut être délégué à un subagent (la QA est légère, pas de timeout risque)
6. **Fallback vision**: si `vision_analyze` échoue (error 1210, GLM sans vision native), utiliser `~/.hermes/skills/devops/vision-analysis-fallback/scripts/or_vision.py` (Gemini 2.5 Flash via OpenRouter)

## Assets branding Sankofa

| Asset | Path | Spec |
|-------|------|------|
| Intro | `branding/intro_sankofa.mp4` | 5s, 1080×1920, video+audio |
| Outro | `branding/outro_sankofa.mp4` | ~3s |
| Stinger | `branding/stinger_sankofa.mp3` | 2.5s |
| Watermark | `branding/watermark_sankofa.png` | logo bas-droite, 20px margin |
| BGM | `crypto-project/audio/bgm_stellardrone.mp3` | ambient, -28dB mix |
