# Text-Overlay TikTok Production (No B-roll, No IA Clips)

Pipeline de production vidéo TikTok 9:16 utilisant UNIQUEMENT ffmpeg drawtext sur fonds colorés + VO Edge TTS + musique procédurale. Aucun clip IA, aucun stock footage, aucune librairie musicale.

**Cas d'usage :** Contenu data-driven (sourcing, prix, comparaisons) où le message est porté par les chiffres et la VO, pas par le visuel. Production en <5min pour ~$0.20.

## Architecture

```
Script (raw text)
  → Claude Fable 5 (OpenRouter) → script enhanced + visual directions + overlay timing
  → Edge TTS FR (+12%) → VO mp3 + SRT
  → ffmpeg drawtext sur color lavfi segments → 5 segments avec overlays
  → concat + mux VO + musique procédurale (sine lowpass)
  → Vision QA frames clés
```

## Step 1 — Script Enhancement via Claude Fable 5

```python
import json, urllib.request

prompt = f"""Tu es un directeur créatif vidéo expert en TikTok. Voici un script: {script}
Retourne un JSON avec:
1. script_enhanced (hook + problem + reveal + margin_reveal + cta)
2. visual_directions (per segment: colors, composition, overlays, animation)
3. voice_directions (tone/pacing/emphasis per segment)
4. hook_variants (A/B/C)
5. text_overlays (exact text + timing in seconds + style spec)
Retourne UNIQUEMENT le JSON valide."""

payload = {
    "model": "anthropic/claude-fable-5",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 4000, "temperature": 0.8
}
# POST to https://openrouter.ai/api/v1/chat/completions
```

**Cost: ~$0.20** (4k output tokens, $0.19575 completion). Les visual directions + overlay timing sont production-ready.

## Step 2 — VO Generation

```bash
edge-tts --voice "fr-FR-HenriNeural" \
  --rate "+12%" \
  --text "$(cat vo_script.txt)" \
  --write-media vo.mp3 \
  --write-subtitles vo.srt
```

**Tuning validé (aout 2026):**
- Script raw 180 mots → VO 73s (trop long)
- Script tightened 131 mots + rate +12% → VO 54s (parfait TikTok)
- **Cible: 120-135 mots pour sub-60s à +12%**

## Step 3 — Background Segments (ffmpeg lavfi)

```bash
ffmpeg -y -f lavfi -i "color=c=0x0a0a0a:s=1080x1920:r=30:d=3" \
  -c:v libx264 -preset ultrafast -tune stillimage -pix_fmt yuv420p \
  bg_hook.mp4
```

Couleurs par segment (palettes sombres pour contraste overlay max):
- Hook: `0x0a0a0a` (noir pur)
- Problem: `0x1a1a2e` (bleu nuit)
- Reveal: `0x0f1923` (bleu foncé tech)
- Margin/CTA: `0x0a0a0a`

## Step 4 — Text Overlays (drawtext)

```bash
ffmpeg -y -i bg_hook.mp4 \
  -vf "drawtext=fontfile={FONT}:text='89€':fontsize=120:fontcolor=white:
       x=(w-text_w)/2:y=(h-text_h)/2-100:
       enable='between(t,0.3,1.8)'"
```

**Timing pattern:**
- `enable='between(t,start,end)'` pour chaque overlay
- Plusieurs drawtext dans un seul `-vf` séparés par des virgules
- Changer de couleur: `fontcolor=yellow`, `fontcolor=red`, `fontcolor=0x00ff00`
- Background box: `box=1:boxcolor=black@0.7:boxborderw=20`

**Font fallback:** Si Poppins absent (CES brand std), `FreeSerifBold.ttf` fonctionne. Vérifier avec:
```python
import glob
bold = [f for f in glob.glob("/usr/share/fonts/**/*.ttf", recursive=True) 
        if "bold" in f.lower() or "black" in f.lower()]
```

## Step 5 — Concat + Mux

```bash
# Concat list
file '/path/seg_hook.mp4'
file '/path/seg_problem.mp4'
...

# Concatenate
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy video_only.mp4

# Mux VO
ffmpeg -y -i video_only.mp4 -i vo.mp3 \
  -c:v copy -c:a aac -b:a 128k -shortest raw.mp4
```

## Step 6 — Procedural Background Music

Quand pas de librairie musicale disponible:

```bash
ffmpeg -y \
  -f lavfi -i "sine=frequency=60:duration=54" \
  -filter_complex "[0:a]volume=0.08,lowpass=f=200[out]" \
  -map "[out]" -c:a aac -b:a 96k -t 54 bg_music.aac
```

Mix final (CES brand standard: musique à 0.12 derrière VO):

```bash
ffmpeg -y -i video_only.mp4 -i vo.mp3 -i bg_music.aac \
  -filter_complex "[1:a]volume=1.0[vo];[2:a]volume=0.12[music];[vo][music]amix=inputs=2:duration=shortest[mix]" \
  -map 0:v -map "[mix]" \
  -c:v libx264 -preset ultrafast -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart -shortest final.mp4
```

## Step 7 — Vision QA

Extraire frames clés et vérifier overlays:

```bash
for t in 1 5 16 40 52; do
  ffmpeg -y -ss $t -i final.mp4 -frames:v 1 frame_${t}s.png
done
```

Vérifier via OpenRouter vision (Gemini 2.5 Flash fallback):
- Texte lisible ? Contraste suffisant ?
- Position correcte (centre, pas coupé) ?
- Couleurs cohérentes (palette définie) ?

## Encoding Settings (CES standard)

| Contexte | Preset | CRF | Resolution | Audio | Timeout |
|---|---|---|---|---|---|
| **Build/render** | ultrafast | 22 | 1080×1920 | 128k AAC | 300s |
| **Telegram delivery** | ultrafast | 28 | 810×1440 | 128k AAC | 300s |

Toujours `-pix_fmt yuv420p` pour compatibilité cross-platform.

## Limites de ce pattern

- **Pas de B-roll** : les fonds colorés sont minimalistes. Pour contenu narratif ou émotionnel, utiliser des clips IA (voir `shorts-video-assembly` skill).
- **Overlays statiques** : ffmpeg drawtext ne gère pas nativement slide-in/bounce. Pour animations, pré-rendre en PNG séquence ou utiliser filter_complex complex.
- **Pas de sous-titres brûlés** : le SRT Edge TTS peut être brûlé séparément via `subtitles=vo.srt` filter.

## Référence session

- **Date:** 4 aout 2026
- **Projet:** Sourcing montres minimalistes → TikTok "Révélation Prix"
- **Durée production:** ~8 min total (Claude Fable 5: 1min, TTS: 5s, ffmpeg: 2min, QA: 2min)
- **Coût:** $0.21 (Claude Fable 5 uniquement)
- **Sortie:** 54s, 1080×1920, 1.15 MB

## Différence avec clip-VO-timing.md

`clip-VO-timing.md` traite le problème des clips IA courts (5s) vs VO longues (10s+). Ce document traite un pattern DIFFÉRENT: production sans clips IA du tout, uniquement text overlays sur fonds colorés. Complémentaire, non redondant.
