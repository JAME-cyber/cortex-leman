# Clip-VO Timing — Le piège du loop

## Problème

Les générateurs vidéo IA (Seedance, Kling, Veo) produisent des clips de **5 secondes maximum** (durée standard). Mais un segment de narration VO dure typiquement **7-12 secondes**. Si le script de build boucle le clip pour combler la durée, le spectateur voit le même plan se répéter → effet amateur, rupture d'immersion.

**Exemple réel (Culture en Saveur T4, juil. 2026):**

| Segment | Clip Seedance | VO + buffer | Boucles produites |
|---------|--------------|-------------|-------------------|
| Henné | 5.0s | 9.5s | ~2x |
| Tambours | 5.0s | 11.2s | ~2x |
| Rhône | 5.0s | 10.3s | ~2x |
| Contes | 5.0s | 8.6s | ~2x |

L'utilisateur a immédiatement identifié le problème ("Pourquoi ça a des loops ?").

## Le code fautif (pattern anti)

```python
def prep_video(name, src, duration):
    # ❌ NAÏF: boucle si source plus courte
    if src_dur >= duration:
        ffmpeg_trim(src, duration)
    else:
        loops = int(duration / src_dur) + 1  # ← CECI EST LE PROBLÈME
        ffmpeg_loop(src, loops, duration)
```

## Solutions (par ordre de qualité)

### 1. Multi-angle cuts (meilleure qualité)

Générer **2 clips minimum par thème** avec angles/prompts différents, puis alterner avec cuts courts de 2-3s.

```python
# Au lieu de boucler 1 clip × 2:
# henne_closeup.mp4 (3s) → henne_wide.mp4 (3s) → henne_detail.mp4 (3s) = 9s
```

**Prompt strategy pour multi-angle:**
- Clip A: "close-up hands applying henna, detailed floral patterns emerging"
- Clip B: "wide shot child sitting patiently, warm room, traditional setting"
- Clip C: "extreme close-up of finished henna design, intricate details"

Coût: ~$0.40-0.60 supplémentaire par segment (205 crédits/clip × 2 clips × 4 segments = 1640 crédits).

### 2. Slow-mo subtil via setpts (BEST quick fix — seamless, no regeneration)

Étirer le clip avec `setpts` pour qu'il dure exactement le temps de la VO. Pour des écarts faibles (clip 5.04s vs VO 5.2-5.6s), le facteur de ralenti est de 2-12% — **imperceptible à l'œil**. Aucune répétition visible.

```python
def prep_video(name, src, duration):
    """Slow-mo: stretch clip to exact duration (no visible loop)."""
    src_dur = ffprobe_dur(src)
    if src_dur >= duration:
        # Trim normally
        run(["ffmpeg", "-y", "-i", src, "-t", str(duration), ...])
    else:
        factor = duration / src_dur
        run(["ffmpeg", "-y", "-i", src,
             "-vf", f"scale={W}:{H},crop={W}:{H},setpts={factor:.4f}*PTS",
             "-r", str(FPS), "-t", str(duration), ...])
        print(f"  (slow-mo factor {factor:.3f})")
```

**Limites pratiques** (validé juil. 2026, CES T4):
- 1.02-1.06x → invisible
- 1.06-1.12x → imperceptible mais légèrement fluide
- >1.15x → devient un effet stylé (ralenti assumé), utiliser avec intention
- >1.30x → trop lent, passer au multi-angle cuts (solution 1)

Cette solution est préférable à l'option image-clé quand le clip a du mouvement intéressant qu'on veut préserver.

### 3. Slow zoom continu sur image-clé (quick fix alternatif)

Si pas de budget pour nouveaux clips, appliquer un zoompan lent sur une frame extraite du clip:

```python
# Extraire frame clé du clip existant
keyframe = extract_frame(clip_path, frame_num=60)
# Zoom lent pendant toute la durée VO
zoompan(keyframe, duration=vo_duration, zoom_start=1.0, zoom_end=1.15)
```

Moins dynamique que du vrai footage mais évite la répétition visible.

### 3b. Ken Burns sur dernière frame (play-then-zoom — ⚠ ÉCHOUÉ sur CPU limité, aout 2026)

**ATTENTION :** La technique Ken Burns zoompan décrite ci-dessous a été testée sur african-heroes Mami Wata (aout 2026) et **a échoué : 31 minutes de timeout** sur un segment de 15.8s. Le coupable est le `scale=2160:3840` avant zoompan — l'upscale 4K d'une image fixe pendant 168+ frames tue une machine avec CPU/RAM limité.

**À n'utiliser QUE sur machine puissante (GPU dédié ou CPU 8+ cores, 16GB+ RAM).** Sur CPU limité, utiliser le **fallback tpad** (solution 3c) ou le **slow-mo setpts** (solution 2).

Quand le clip fait 5s mais la VO dure 10-15s, on ne peut ni boucler (loop visible) ni geler (effet diapositive). Solution hybride : **jouer le clip normalement (5s), puis zoompan lent sur la dernière frame pour le reste de la durée**.

```python
def build_video_segment(video_path, dur, out_path):
    """Play clip once, then slow zoompan on last frame for remaining duration."""
    clip_dur = get_dur(video_path)  # typiquement 5.0s
    
    if dur <= clip_dur + 0.3:
        # Trim simple
        ffmpeg_trim(video_path, dur)
    else:
        remaining = dur - clip_dur
        frames = int(remaining * 24)
        
        # 1. Extraire dernière frame
        ffmpeg("-sseof", "-0.1", "-i", video_path, "-vframes", "1", last_frame.png)
        
        # 2. Rendre la partie vidéo (clip complet)
        ffmpeg(video_path, "-t", clip_dur, scale_1080x1920, video_part.mp4)
        
        # 3. Zoompan sur la dernière frame (⚠ scale=2160:3840 = TUE CPU limité)
        zoom_vf = (
            f"scale=2160:3840:flags=lanczos,"  # ← CECI EST LE BOTTLENECK
            f"zoompan=z='min(zoom+0.0008,1.15)':d={frames}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":s=1080x1920:fps=24,format=yuv420p"
        )
        ffmpeg("-loop", "1", "-t", remaining, last_frame.png, zoom_vf, zoom_part.mp4)
        
        # 4. Concaténer vidéo + zoom
        ffmpeg_concat([video_part.mp4, zoom_part.mp4], out_path)
```

**Points clés :**
- `scale=2160:3840` avant `zoompan` : faut upscaler car zoompan crop — sans upscale, le zoom reveal les bords noirs
- `zoom+0.0008` par frame : zoom de 1.0 → ~1.15 sur 7s (168 frames), assez lent pour être imperceptible mais garde du mouvement
- Centrage : `x='iw/2-(iw/zoom/2)'` garde le zoom centré
- **⚠ TIMEOUT sur CPU limité** : 31 min pour 1 segment de 15.8s (aout 2026, african-heroes Mami Wata). Utiliser solution 3c à la place.

**Pitfall inversé (aout 2026) :** Ma première correction a été d'utiliser `stream_loop` pour répéter le clip → **pire que le freeze** car la répétition complète du clip est encore plus visible qu'un gel. Le user a confirmé que les "loops" étaient le problème. Règle : `stream_loop` ne sert QUE pour des clips abstraits/décoratifs (paysages, textures), JAMAIS pour des clips narratifs avec action reconnaissable.

### 3c. Fallback pragmatique : tpad freeze sur CPU limité (VALIDÉ aout 2026)

Sur machine avec CPU/RAM limité, ni le Ken Burns zoompan ni le slow-mo étendu ne passent dans le budget temps. Le **fallback pragmatique** est `tpad=stop_mode=clone` : jouer le clip 5s puis geler la dernière frame. C'est l'effet "diapositive" que le user identifiera comme peu dynamique, mais c'est le SEUL qui termine dans un budget de 300s.

```python
def build_video_segment(video_path, dur, out_path, beat=None):
    """Scale 496x864 → 1080x1920, play clip, then freeze with tpad."""
    clip_dur = get_dur(str(video_path))
    
    if dur <= clip_dur + 0.3:
        cmd = ["ffmpeg", "-y", "-i", str(video_path),
               "-t", f"{dur:.3f}",
               "-vf", "scale=1080:1920:flags=lanczos,format=yuv420p",
               "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
               "-an", "-r", "24", str(out_path)]
    else:
        freeze_dur = dur - clip_dur
        vf = (f"scale=1080:1920:flags=lanczos,"
              f"tpad=stop_mode=clone:stop_duration={freeze_dur:.3f},"
              f"format=yuv420p")
        cmd = ["ffmpeg", "-y", "-i", str(video_path),
               "-vf", vf,
               "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
               "-an", "-r", "24", "-t", f"{dur:.3f}", str(out_path)]
```

**Mitigation de l'effet diapositive :** Le freeze est moins choquant si le clip montre une scène calme/contemplative (océan, paysage, temple). Pour les segments narratifs avec action, préférer la solution 6 (overlay carte/info-graphique, voir ci-dessous) pour combler visuellement le temps freeze.

**Comparaison des approches pour clip 5s + VO 12s :**

| Approche | Visuel | Coût crédits | Complexité | CPU limité ? |
|----------|--------|--------------|------------|-------------|
| Multi-angle (2-3 clips) | ✅ Meilleur | ~410-615cr | Haute | ✅ Oui |
| Slow-mo setpts (1.0-1.15x) | ✅ Invisible | 0cr | Basse | ✅ Oui |
| Ken Burns dernière frame | ⚠ Bon (motion minimal) | 0cr | Moyenne | ❌ Timeout 31min |
| tpad freeze | ⚠ Diapositive | 0cr | Basse | ✅ Oui |
| stream_loop | ❌❌ Loop évident | 0cr | Basse | ✅ Oui |

**Choix :** Slow-mo si facteur ≤1.15x. tpad freeze si >1.15x sur CPU limité. Ken Burns si machine puissante. Multi-angle si budget permet. JAMAIS stream_loop sur clips narratifs.

### 4. VO plus courte (si le texte le permet)

Raccourcir la narration pour tenir en 5s. Pas idéal — limite la profondeur du message.

### 5. Mix clip + B-roll stock

Alterner le clip IA avec des images/b-roll (zoom sur photos, cartes textuelles, patterns).

### 6. Overlay carte/info-graphique pour clarté géographique (VALIDÉ aout 2026, african-heroes Mami Wata)

Quand un clip vidéo montre un concept géographique (voyage, diaspora, expansion) mais que le viewer ne peut pas identifier les lieux précis, ajouter un **overlay carte stylisé** généré via HTML+Playwright → PNG transparent → compositing ffmpeg.

**Problème réel :** Clip Seedance "voyage transatlantique" montrait océan + côtes tropicales, mais sans repères géographiques. Le user ne comprenait pas où étaient Haïti, Suriname, Trinité. Solution : carte SVG avec flèches + noms locaux.

**Workflow :**
1. Créer `map_overlay.html` (1080×1920, fond transparent, SVG simplifié : continents en silhouettes, flèches arc, labels avec noms locaux)
2. Capturer en PNG via Playwright : `page.screenshot(path='map.png', omit_background=True)`
3. Compositer sur le segment vidéo : `ffmpeg -i video.mp4 -i map.png -filter_complex "[0:v][1:v]overlay=0:0[outv]"`

**HTML template de carte (african-heroes) :**

```html
<style>
.map-panel{position:absolute;bottom:0;left:0;right:0;height:780px;
  background:linear-gradient(0deg,rgba(10,10,15,0.92) 0%,rgba(10,10,15,0.75) 60%,transparent 100%)}
.map-svg{position:absolute;top:60px;left:50%;transform:translateX(-50%);width:900px;height:600px}
.label{position:absolute;font-weight:800;font-size:30px;text-shadow:0 2px 8px rgba(0,0,0,0.9)}
.label .dot{display:inline-block;width:16px;height:16px;border-radius:50%;margin-right:8px}
.label .sub{display:block;font-size:20px;opacity:0.8;margin-left:24px}  /* nom local */
</style>
<!-- SVG: continents simplifiés + flèches arc dasharray + ship emoji -->
<svg viewBox="0 0 900 600">
  <defs>
    <marker id="arrow"><path d="M0,0 L12,6 L0,12 Z" fill="#E8A33D"/></marker>
    <linearGradient id="arcGrad">
      <stop offset="0%" stop-color="#E8A33D" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#B5522E" stop-opacity="0.9"/>
    </linearGradient>
  </defs>
  <!-- Continent silhouettes (paths simples) -->
  <!-- Arcs dashed avec marker-end -->
  <path d="M200,300 Q400,80 660,180" fill="none" stroke="url(#arcGrad)"
        stroke-width="3" stroke-dasharray="8,6" marker-end="url(#arrow)"/>
</svg>
```

**Intégration dans build.py :**

```python
def build_video_segment(video_path, dur, out_path, beat=None):
    # ... rendu du segment normal ...
    
    # ── Map overlay (après le rendu principal) ──
    map_png = BASE / "captions" / "diaspora_map.png"
    if beat and beat.get("map_overlay") and map_png.exists():
        tmp_out = out_path.parent / (out_path.stem + "_nomap.mp4")
        out_path.rename(tmp_out)
        subprocess.run([
            "ffmpeg", "-y", "-i", str(tmp_out), "-i", str(map_png),
            "-filter_complex", "[0:v][1:v]overlay=0:0[outv]",
            "-map", "[outv]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
        ], capture_output=True, text=True)
        tmp_out.unlink(missing_ok=True)
```

**Activation conditionnelle :** Ajouter `"map_overlay": True` au beat dans `BEATS_CONFIG`. Seuls les segments géographiques reçoivent l'overlay.

**⚠ Pitfall ordre des opérations :** Le map overlay doit s'exécuter **APRÈS** le `subprocess.run(cmd)` principal qui crée `out_path`, pas avant. Sinon `out_path.rename(tmp_out)` → `FileNotFoundError`. Le bloc overlay doit venir après le check `r.returncode != 0`.

**Coût :** 0 crédit IA (juste HTML+Playwright+ffmpeg). Rapidement composable.

### 6b. Vraie carte géographique via matplotlib + Playwright composite (VALIDÉ aout 2026, après 3 itérations)

**Problème :** La solution 6 (SVG hand-drawn) a été jugée insuffisante par le user — les silhouettes continentales dessinées à la main ne ressemblaient pas à la vraie géographie. Le user a explicitement demandé "une vraie géographique et le tracer du voyage" après avoir vu une carte SVG stylisée. Itération : SVG abstrait → SVG stylisée enrichie → **matplotlib coords réelles**.

**Solution : matplotlib pour la carte (coords GPS réelles) → Playwright HTML pour le composite final.**

**Workflow en 2 étapes :**

1. **Générer la carte de base** avec matplotlib (`gen_map.py`):
   - Vraies coordonnées GPS (lon/lat) pour chaque point
   - Continents : polygones simplifiés (coastline approximations) — bien meilleurs que des formes abstraites
   - Routes : arcs quadratiques Bézier simulant la grande circulaire (midpoint poussé vers le nord)
   - Output : PNG transparent (`diaspora_map_base.png`)

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Vraies coordonnées [lon, lat]
ORIGIN = {"lon": -3.0, "lat": 6.0, "name": "Afrique de l'Ouest"}
DESTINATIONS = [
    {"lon": -72.3, "lat": 18.9, "name": "Haïti"},     # vraies coords
    {"lon": -55.9, "lat": 4.0,  "name": "Suriname"},   # vraies coords
    {"lon": -61.3, "lat": 10.7, "name": "Trinité"},    # vraies coords
]

fig, ax = plt.subplots(figsize=(10.8, 10.0), dpi=100)
fig.patch.set_alpha(0)  # fond transparent

# Continents : polygones simplifiés (axe lon/lat = pseudo-projection équirectangulaire)
ax.fill(africa_lon, africa_lat, color=(0.18, 0.31, 0.15, 0.6), edgecolor='#E8A33D', linewidth=1.5)

# Routes : arcs Bézier quadratiques (bow northward = approximation grande circule)
for dest in DESTINATIONS:
    t = np.linspace(0, 1, 50)
    mid_lon = (ORIGIN["lon"] + dest["lon"]) / 2
    mid_lat = (ORIGIN["lat"] + dest["lat"]) / 2 + 15  # bow north
    lon_arc = (1-t)**2 * ORIGIN["lon"] + 2*(1-t)*t * mid_lon + t**2 * dest["lon"]
    lat_arc = (1-t)**2 * ORIGIN["lat"] + 2*(1-t)*t * mid_lat + t**2 * dest["lat"]
    ax.plot(lon_arc, lat_arc, '--', color='#E8A33D', linewidth=2.5, alpha=0.8)
    ax.annotate('', xy=(dest["lon"], dest["lat"]), xytext=(lon_arc[-3], lat_arc[-3]),
                arrowprops=dict(arrowstyle='->', color='#E8A33D', lw=2.5))

ax.set_xlim(-100, 60); ax.set_ylim(-20, 50)
ax.set_aspect('equal'); ax.axis('off')
fig.savefig('diaspora_map_base.png', transparent=True, bbox_inches='tight', dpi=100)
```

2. **Compositer dans HTML** (`diaspora_map.html`) via Playwright:
   - `<img src="diaspora_map_base.png">` au centre
   - Bandeau sombre gradient (haut transparent → bas opaque)
   - Cards d'info en bas avec drapeaux + noms locaux + contexte spirituel
   - Capture → `diaspora_map.png` (1080×1920 transparent)

**⚠ Pitfalls matplotlib :**
- `color='rgba(46,80,38,0.6)'` → **ValueError**. Matplotlib ne supporte PAS le format CSS rgba. Utiliser des tuples : `color=(0.18, 0.31, 0.15, 0.6)`.
- Emoji (⛵) → **Glyph missing** warning (DejaVu Sans n'a pas les emojis). Remplacer par du texte ou un symbole ASCII.
- `fig.patch.set_alpha(0)` + `ax.set_facecolor('none')` pour fond vraiment transparent.

**Lien avec la solution 6 (SVG) :** La solution 6 reste valable pour des cartes très stylisées/abstraites. Pour la clarté géographique où le user doit reconnaître les continents et les positions relatives des pays, **toujours préférer matplotlib avec coords réelles**. Le user itérera invariablement vers cette demande.


## Règle de validation (à coder dans le build script)

```python
def validate_clip_vs_vo(clips, vo_durations, buffer=1.0):
    """Alerte si un clip risque de boucler."""
    warnings = []
    for name, clip_dur, vo_dur in zip(clips, vo_durations):
        needed = vo_dur + buffer
        if clip_dur < needed:
            loops = needed / clip_dur
            warnings.append(
                f"⚠ {name}: clip={clip_dur:.1f}s vs VO={needed:.1f}s "
                f"(boucle {loops:.1f}x — générer {int(loops)+1} clips supplémentaires)"
            )
    return warnings
```

Lancer cette validation AVANT le build. Si warnings → escalader vers génération multi-angle.

## Quand ce pitfall se produit

TOUT projet vidéo qui combine:
- Clips IA courts (Seedance 5s, Kling 5s, Veo 6s)
- Narration VO > 6s par segment
- Script de build qui boucle automatiquement

Aussi applicable aux skills: `cortex-leman-video-brief`, `le-contre-point-podcast` (shorts), `financial-content-pipeline`.

## ⚠ ffmpeg crop filter: variable `on` n'existe pas (aout 2026, african-heroes Abla Pokou)

Le filtre `crop` de ffmpeg **ne supporte pas** la variable `on` (frame number). C'est une variable spécifique à `zoompan`. Si on utilise `on` dans une expression `crop`, ffmpeg échoue silencieusement et déclenche le fallback (image statique sans zoom).

**Correct : utiliser `t` (temps en secondes) dans crop.**

```python
# ❌ FAUX — 'on' is zoompan-only, crop silently fails
crop_expr = f"crop=w=1080:h=1920:x='(iw-1080)/2*(on/{total_frames})':..."

# ✅ CORRECT — utiliser 't' (temps) dans crop
crop_expr = f"crop=w=1080:h=1920:x='(iw-1080)/2*(1-t/{dur:.1f})':..."
```

**Pattern Ken Burns rapide sur CPU limité (validé aout 2026) :**

1. Pre-resize l'image source en Python/PIL vers une taille légèrement overscalée (1080×1.08 = 1166px)
2. Utiliser `crop` avec expressions basées sur `t` pour un pan progressif
3. Beaucoup plus rapide que `zoompan` sur grosses images car ffmpeg travaille sur une petite image

```python
# Pre-resize en Python (rapide)
from PIL import Image
img = Image.open(src).convert("RGB")
img_resized = img.resize((int(1080*1.08), int(1920*1.08)), Image.LANCZOS)
img_resized.save(tmp_scaled, "PNG")

# ffmpeg crop avec 't' (pas 'on'!)
crop_expr = f"crop=w=1080:h=1920:x='(iw-1080)/2*(1-t/{dur:.1f})':y='(ih-1920)/2*(1-t/{dur:.1f})'"
```

**Symptôme :** build log affiche `⚠️ Ken Burns fail, fallback scale` à chaque segment. Vérifier le filtre crop pour variables invalides.

## ⚠ Pitfall libx264 preset medium timeout (1080×1920 + subs ASS — aout 2026, african-heroes Mami Wata)

Le rendu final d'une vidéo 9:16 en 1080×1920 avec overlay (caption PNG + sous-titres ASS + watermark + BGM) **dépasse systématiquement 300s** avec `libx264 -preset medium`. Sur une machine avec CPU limité (Raspberry Pi 5, 3.8GB RAM), le preset medium n'est pas viable.

**Session aout 2026 :** Build Mami Wata (9 segments, 109s total) a timeout à 300s DEUX FOIS. Le rendu était à ~95% (tous les segments en cache, il ne restait que le mux final). Le fichier `mami_wata_noloop.mp4` était incomplet (40MB, pas de durée valide via ffprobe).

**Fix : `ultrafast` + CRF 22 (build) / CRF 28 (compression TG)**

```python
# RENDU FINAL (build.py) — ultrafast au lieu de medium
cmd = [
    "ffmpeg", "-y", "-i", video_audio, "-i", bgm, "-i", watermark,
    "-filter_complex", f"[0:v][2:v]overlay=...,subtitles='{ass}'[vout];...",
    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",  # ← was "medium"/"20"
    ...
]

# COMPRESSION TG — ultrafast + CRF 28 + scale down (810×1440 au lieu de 1080×1920)
ffmpeg -y -i master.mp4 \
  -c:v libx264 -preset ultrafast -crf 28 -maxrate 3200k -bufsize 6400k \
  -vf "scale=810:1440" \
  -c:a aac -b:a 128k -movflags +faststart \
  tg_clip.mp4
```

**Impact qualité :** CRF 22 ultrafast vs CRF 20 medium = différence invisible pour le format vertical 9:16 (déjà upscalisé depuis 496×864 Seedance). Le preset n'affecte que la vitesse d'encodage, pas la qualité finale à CRF équivalent.

**Règle :** Sur CPU limité, TOUJOURS utiliser `ultrafast` pour les rendus intermédiaires et finaux. Réserver `medium`/`slow` pour les masters archivés si nécessaire (en background avec timeout 600s+).

**Pattern pour builds longs (>5 min de rendu) :** Lancer en `background=true` avec `notify_on_complete=true`. Le build tourne sans bloquer le terminal, et le résultat revient automatiquement à la fin.
