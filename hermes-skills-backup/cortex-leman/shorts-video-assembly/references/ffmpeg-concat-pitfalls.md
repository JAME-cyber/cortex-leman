# ffmpeg Concat & Rendering Pitfalls — Short-Form Video Pipeline

Apprentissages validés en production (août 2026, basketball short "RISE" + CES + african-heroes).

## 1. FPS Mismatch — le concat silencieux cassé

**Problème :** Quand des segments vidéo ont des framerates différents (30fps, 60fps, 25fps), `ffmpeg -f concat -c copy` produit soit un fichier illisible, soit une vidéo avec des sauts/desync. Ce n'est PAS une erreur ffmpeg — le exit code peut être 0.

**Scénario réel :**
```
poster_intro.mp4  → 30fps (généré depuis image fixe)
seg01.mp4         → 60fps (extrait d'un clip smartphone)
seg04.mp4         → 25fps (extrait d'un autre clip)
outro.mp4         → 30fps
```
Résultat : concat produit 4min36s de vidéo aberrante au lieu de 23s.

**Fix : normaliser TOUS les segments à la même FPS avant concat.**

```python
# Dans l'extraction de chaque segment, TOUJOURS forcer fps:
vf = f"scale={W}:{H},crop={W}:{H},eq=...,fps={FPS},format=yuv420p"
#                                                                          ^^^^^
#                                                              OBLIGATOIRE pour concat
```

**Règle :** avant tout concat `-c copy`, vérifier :
```bash
for f in segments/*.mp4; do
  echo -n "$f: "
  ffprobe -v quiet -show_entries stream=r_frame_rate -of csv=p=0 "$f"
done
```
Si les valeurs diffèrent → re-encoder avec `fps=30` ou utiliser `-c:v libx264` au lieu de `-c copy`.

---

## 2. Zoompan sur segments courts = TIMEOUT KILLER

**Problème :** `zoompan` sur des segments de 1.5s (45 frames à 30fps) peut prendre 30-60s PAR SEGMENT sur CPU limité. Pour 12 segments = 600s+ = timeout garanti.

**Scénario réel :** Build V2 du short basket — 12 segments × zoompan = timeout 600s après seulement 4 segments complétés.

**Cause :** zoompan recalcule chaque pixel à chaque frame. Sur 1080×1920 c'est ~2M pixels × 45 frames = 90M calculs par segment.

**Fix : échelles de priorité pour le mouvement de caméra sur CPU limité :**

| Approche | Vitesse | Qualité | Quand utiliser |
|----------|---------|---------|----------------|
| **Pas de zoom** (crop fixe) | Instantané | Plate | Si clips ont déjà du mouvement |
| **scale + crop dynamique** (pre-zoom statique) | Rapide | Bon | Zoom fixe 1.1x appliqué au scale |
| **zoompan** | Lent (30-60s/seg) | Excellent | Machine puissante ONLY |
| **Post-zoom au merge final** | Moyen | Bon | Un seul passage zoompan sur la vidéo complète |

**Pattern recommandé pour rapid-fire cuts (1.5-2s segments) :**
```python
# PAS de zoompan par segment. Appliquer color grading + scale uniquement.
vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},eq=gamma=1.3:saturation=1.35,fps=30,format=yuv420p"
# Le "mouvement" vient du rythme des cuts, pas du zoom individuel
```

---

## 3. Subtitles Filter — Path Absolu Obligatoire

**Problème :** Le filtre `subtitles=` de ffmpeg ne trouve pas le fichier ASS quand le path est relatif, même si le cwd est correct. Erreur silencieuse : `Unable to open subs.ass` → build échoue.

**Fix : TOUJOURS utiliser un chemin absolu pour le fichier ASS.**
```python
# ❌ Échoue
f"-vf", f"subtitles=tmp/subs.ass"

# ✅ Marche
f"-vf", f"subtitles=/home/tars/project/tmp/subs.ass"

# En Python, utiliser Path.resolve() ou absolute():
ass_path = Path("tmp/subs.ass").resolve()
f"-vf", f"subtitles={ass_path}"
```

---

## 4. QA Contact Sheet — Validation Visuelle en Un Shot

**Pattern :** Avant de livrer une vidéo, extraire 5-6 frames clés et les envoyer à un modèle vision (Gemini 2.5 Flash via OpenRouter) pour scoring.

**Extraction contact sheet via ffmpeg tile :**
```bash
# Sélectionner 6 frames réparties dans la vidéo
# n = frame number = timestamp × fps
ffmpeg -y -i video.mp4 -vf "
  select='eq(n\,30)+eq(n\,120)+eq(n\,240)+eq(n\,360)+eq(n\,480)+eq(n\,630)',
  scale=270:480,
  tile=3x2
" -frames:v 1 contact_sheet.jpg
```

**Scoring via Gemini 2.5 Flash :**
```python
# Voir scripts/visual_qa_gpt.py dans kieai-seedance-video-generation
# Adapter pour contact sheets: envoyer l'image + prompt structuré
# Demander: score /10 sur flow, pacing, subs, TikTok readiness + issues
```

**Format de prompt QA optimal (court = réponse complète) :**
```
Contact sheet of 6 frames from a {dur}s {format} short.
Rate 1-10 on: (1) visual flow, (2) pacing, (3) subtitle readability,
(4) TikTok readiness. Is this publishable? Top 2 issues.
```

**Seuil de publication :** ≥7/10 overall = publishable. <7 = itérer.

---

## 5. Compression Telegram — Pipeline Validé

**Limite Telegram : 20MB pour les médias envoyés via bot API.**

**Pipeline de compression validé (1080×1920 → <20MB) :**
```bash
ffmpeg -y -i master.mp4 \
  -vf "scale=810:1440" \
  -c:v libx264 -preset ultrafast -crf 28 \
  -c:a aac -b:a 128k -ac 1 \
  tg_version.mp4
```

**Paramètres validés :**
| Paramètre | Master | Telegram |
|-----------|--------|----------|
| Résolution | 1080×1920 | 810×1440 |
| Preset | ultrafast/medium | ultrafast |
| CRF | 20-23 | 28 |
| Audio | stereo 128k | mono 128k |
| Taille typique | 25-35MB | 8-12MB |

**Règle :** Toujours produire DEUX versions : master (1080×1920, qualité max) + tg (810×1440, <20MB).

---

## 6. Audio Mix — VO + Ambient + Bass Boost

**Pattern d'audio mix pour shorts avec VO + ambiance sonore des clips :**

```python
# 1. Extraire audio ambient d'un clip source
ffmpeg -y -ss 5 -t {dur} -i clip.mp4 -vn -ac 2 -ar 44100 amb.wav

# 2. Mixer VO (delayed) + ambient (quiet, bass-boosted)
ffmpeg -y \
  -i vo.mp3 -i amb.wav \
  -filter_complex \
    "[0:a]adelay=1500|1500,volume=1.2[vo];" \
    "[1:a]volume=0.2,bass=g=6:f=80[bt];" \
    "[vo][bt]amix=inputs=2:duration=longest:dropout_transition=0,volume=0.9[aout]" \
  -map "[aout]" -c:a pcm_s16le -ar 44100 -ac 2 amix.wav
```

**Points clés :**
- `adelay=1500|1500` : la VO commence 1.5s après le début (pendant le poster intro)
- `bass=g=6:f=80` : l'ambient est bass-boosté pour un effet "beat" subliminal
- Output en WAV (pcm_s16le) — le MP3 pose des problèmes de codec avec certains mix
- Volume VO 1.2x, ambient 0.2x — la VO doit toujours dominer

---

## 7. Edge TTS vs ElevenLabs — Choix VO

| Critère | Edge TTS | ElevenLabs |
|---------|----------|------------|
| Coût | Gratuit | ~$0.01-0.05/phrase |
| Qualité | Bonne, robotique propre | **Supérieure, grain émotionnel** |
| Setup | CLI direct | API REST, clé requise |
| Vitesse | <2s | 3-5s |
| Durée output | Plus long (18s pour même texte) | Plus court/punchy (14s) |
| Personnalité | Voix standard | Adam (grave), Antoni (jeune), etc. |

**Config ElevenLabs dans Hermes :**
- `config.yaml` section `tts.elevenlabs`: voice_id + model_id
- **Clé API** : chercher dans `~/crypto-project/.env` (ELEVENLABS_API_KEY) si absente de `~/.hermes/.env`
- Model : `eleven_multilingual_v2` (support FR natif)
- Voice settings : stability 0.5, similarity 0.75, style 0.35, use_speaker_boost true

**Rule :** Edge TTS par défaut. ElevenLabs quand l'utilisateur demande plus de grain émotionnel ou une voix spécifique.

---

## 8. Build Script Robustesse — Checklist Avant Lancement

Avant de lancer un build multi-segments en foreground/background :

```python
# 1. Vérifier que tous les segments existent et ont la même FPS
for seg in segments:
    assert seg.exists(), f"Missing: {seg}"
    fps = ffprobe_fps(seg)
    assert fps == TARGET_FPS, f"FPS mismatch: {seg} is {fps}, expected {TARGET_FPS}"

# 2. Vérifier que le subs.ass existe au path absolu
assert SUBS_PATH.is_absolute(), "subs path must be absolute"

# 3. Vérifier que la VO existe et sa durée < durée vidéo
vo_dur = ffprobe_dur(VO_PATH)
assert vo_dur < video_dur, f"VO ({vo_dur}s) longer than video ({video_dur}s)"

# 4. Estimer le temps de render (règle empirique CPU limité)
estimated_render = total_segments * 3  # 3s per segment for ultrafast
if estimated_render > 250:
    print(f"⚠ Estimated render: {estimated_render}s — use background=true")
```
