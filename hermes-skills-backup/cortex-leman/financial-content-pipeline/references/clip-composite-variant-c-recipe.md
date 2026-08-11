# Variante C — Composite broll recipe (clip Trumpf V2, 2026-07-19)

Recipe complet pour produire un clip vertical 9:16 avec images Grok en background de slides clés + intro + sous-titres burn-in. Référence pour reproduction.

## Contexte validé

- **Clip** : "Le Maillon Invisible" (Trumpf → ASML → Chine), 94.5s total
- **Pipeline** : `~/crypto-project/CHANNEL/video4/`
- **Sortie** : `clip_trumpf_v2_final.mp4` (1080×1920, 18.3 MB, H.264/AAC stereo)

## Prérequis

- `~/.venv/bin/python` (contient playwright + edge_tts)
- Images Grok générées : `python grok_imagine.py <actor>` → 6 variants 720×1280 dans `CHANNEL/video3/grok_assets/`
- Intro existante : `~/crypto-project/branding/intro_9x16.mp4` (5s, 1080×1920, stereo AAC)
- BGM : `~/crypto-project/audio/bgm_stellardrone.mp3`
- ffprobe + ffmpeg

## Ordre d'exécution (7 étapes)

```bash
cd ~/crypto-project

# 1. TTS — dict SECTIONS dans gen_tts.py
~/.venv/bin/python CHANNEL/video4/gen_tts.py
# → audio/*.mp3 + audio/durations.json

# 2. Slides navy simples (hook, conclusion, disclaimer)
~/.venv/bin/python CHANNEL/video4/gen_slides.py
# → slides/*.html

# 3. Slides composites (broll Grok + overlay texte)
#    Copier d'abord 3 images Grok dans slides/, puis :
~/.venv/bin/python CHANNEL/video4/gen_broll_slides.py
# → slides/{02_revelation,03_stakes,04_tension}.html + .png capturés

# 4. Capture PNG des slides navy restantes
~/.venv/bin/python CHANNEL/video4/capture_slides.py
# → renders/slides_png/*.png

# 5. Sous-titres (SRT + ASS avec offset intro 5.5s)
~/.venv/bin/python CHANNEL/video4/gen_subs.py
# → renders/subs.srt + renders/subs.ass

# 6. Assemblage V2 (intro + body Ken Burns + BGM + subs burn-in)
~/.venv/bin/python CHANNEL/video4/assemble_v2.py
# → renders/clip_trumpf_v2_final.mp4

# 7. Vérification technique
ffprobe -v quiet -show_entries format=duration:stream=width,height,channels,codec_name \
  -of default=noprint_wrappers=1 CHANNEL/video4/renders/clip_trumpf_v2_final.mp4
```

## Points de friction résolus (ne pas répéter les erreurs)

### 1. Two-venv trap
- ❌ `python3.12` ou `crypto-project/.venv/bin/python` → `ModuleNotFoundError: No module named 'playwright'`
- ✅ `~/.venv/bin/python` pour tout script qui importe playwright (capture, broll)

### 2. Concat intro+body : 3 pièges en cascade
Le `ffmpeg -f concat -safe 0 -i list.txt -c copy` échoue ou corrompt l'audio. Causes :

| Piège | Symptôme | Fix |
|---|---|---|
| Audio mono (body TTS) vs stereo (intro AAC) | Erreur `26 channels` au mix BGM en aval | Re-encoder l'audio lors de la concat (pas `-c copy`) |
| SAR différent entre sources | `Input link in0:v0 parameters ... do not match` | `[N:v]setsar=1[vN]` avant le concat |
| Frames AAC défectueuses dans intro | `Invalid data found`, `NaN/+Inf` | `filter_complex concat=n=2:v=1:a=1` au lieu du demuxer |

Pattern final robuste (assemble_v2.py step 3) :
```
ffmpeg -i INTRO -i BODY \
  -filter_complex "[0:v]setsar=1[v0];[1:v]setsar=1[v1];
    [v0][0:a][v1][1:a]concat=n=2:v=1:a=1[outv][outa];
    [outa]aformat=channel_layouts=stereo,aresample=44100[afix]" \
  -map [outv] -map [afix] \
  -c:v libx264 -preset ultrafast -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 128k OUT
```

### 3. Sous-titres désynchronisés
Sans offset, les subs apparaissent pendant l'intro (5.5s de décalage). Le `gen_subs.py` ajoute `INTRO_DUR = 5.5` à chaque timestamp SRT/ASS.

Le burn-in ASS se fait sur le fichier final (après BGM), pas sur le body seul — sinon les subs sont perdus au mix.

### 4. Ordre des opérations
Ordre incorrect = sous-titres perdus ou audio corrompu :
1. Construire body (slides + voice + Ken Burns)
2. Concaténer intro+body (filter_complex, pas demuxer)
3. Mixer BGM (amix sur le fichier concaténé)
4. Burn-in subs ASS sur le fichier final

## Structure des slides

| Slide | Type | Background | Source visuel |
|---|---|---|---|
| 01_hook | Navy simple | `#04102B` | — |
| 02_revelation | **Composite** | trumpf_split_v1.jpg (clean room) | Grok |
| 03_stakes | **Composite** | trumpf_split_v3.jpg (laser details) | Grok |
| 04_tension | **Composite** | trumpf_split_v5.jpg (supply chain map) | Grok |
| 05_conclusion | Navy simple | `#04102B` | — |
| 06_disclaimer | Navy simple | `#04102B` | — |

## CSS pour slide composite

⚠️ **Itérer sur le tuning** (validé 2026-07-19, clip Trumpf V2, 2 itérations). Trois paliers testés :

| Palier | `.bg` filter | `.overlay` gradient | Lum. centre | Verdict Tars |
|---|---|---|---|---|
| Initial | `brightness(0.35)` | `0.85 → 0.40 → 0.85` | 31.8 | ❌ « background sombre » |
| Corrigé 1 | `brightness(0.55) saturate(1.1)` | `0.75 → 0.15 → 0.75` | 40.3 | ❌ « plus claire » (insuffisant) |
| **Base validée** | **`brightness(0.65) saturate(1.15)`** | **`0.65 → 0.10 → 0.65`** | **44.7** | ✅ |

```css
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
   filter:brightness(0.65) saturate(1.15)}                   /* base validée */
.overlay{position:absolute;inset:0;padding:80px 60px;
         background:linear-gradient(180deg,
           rgba(4,16,43,0.65) 0%,                           /* top opaque (kicker lisible) */
           rgba(4,16,43,0.10) 40%,                          /* centre transparent (photo transparaît) */
           rgba(4,16,43,0.65) 100%)}                        /* bottom opaque (stats lisibles) */
h1{font-size:64px;text-shadow:0 2px 16px rgba(0,0,0,0.9)}   /* ombre sur texte */
```

**Principe de tuning** : `brightness` contrôle la clarté de la photo, l'overlay mid-point contrôle la lisibilité du texte central. Garder le top/bottom du gradient à ≥0.65 (kicker + stats/disclaimer restent lisibles). Ne pas dépasser `brightness(0.75)` sans monter aussi l'overlay mid (sinon le titre central perd en contraste).

### QA visuelle quand le modèle n'a pas de vision

Le modèle actif (GLM-5.2 via zai) ne supporte pas `vision_analyze` (erreur 1210 systématique). Workaround validé : **QA quantitative + side-by-side montage** pour valider un changement visuel sans devoir voir l'image.

```python
from PIL import Image, ImageStat
# Mesurer luminance + contraste sur la zone critique (ici : centre de la slide,
# où la photo doit transparaître derrière le texte)
img = Image.open("slide.png").convert("RGB")
w, h = img.size
center = img.crop((int(w*0.1), int(h*0.35), int(w*0.9), int(h*0.65)))
stat = ImageStat.Stat(center)
lum = 0.299*stat.mean[0] + 0.587*stat.mean[1] + 0.114*stat.mean[2]
contrast = stat.stddev[0]
```

Générer un side-by-side AVANT/APRÈS (Playwright capture deux versions avec labels, Pillow colle les deux moitiés redimensionnées) et le livrer au user pour validation visuelle finale. Voir `~/crypto-project/CHANNEL/video4/` pour le script complet.

```bash
cd ~/crypto-project && uv pip install playwright pillow   # si manquant
```

## Évolution

- Le pattern s'applique à n'importe quel acteur (asml, ovhcloud, soitec, trumpf) — il suffit d'éditer les dicts SECTIONS + les `page()` HTML et de générer les Grok correspondants.
- Pour un clip 100% composite (toutes slides avec broll), supprimer `gen_slides.py` et tout passer dans `gen_broll_slides.py`.
- Pour un clip Variante B (100% navy), supprimer `gen_broll_slides.py` et `grok_imagine.py`.
