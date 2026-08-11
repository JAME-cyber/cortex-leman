# Variante E — Assemblage vidéo B-roll IA (recipe technique)

Validé en production : projet Sankofa/african-heroes, Queen Nzinga, 2026-07-22.
6 clips Seedance 2.0 Fast (480p, 9:16, 5s) → build_v3.py → montage 9 beats, ~90s.

## Architecture du build

```
build_v3.py
├── 9 beats (BEATS_CONFIG) : 7 vidéo + 1 image fallback + 1 CTA fullscreen
├── Captions : Playwright HTML → PNG (cache dans captions_v3/)
├── Segments : clip vidéo → scale 1080x1920 → loop/trim → overlay caption
├── Concat : demuxer concat (-c copy)
├── Audio : concat MP3 TTS → mux AAC
├── Final : subs ASS + BGM + watermark (single pass, preset medium crf 20)
└── Outro : concat outro signature (filter_complex)
```

## Scale + loop/trim des clips vidéo

### Problème
Seedance 2.0 Fast sort en 496×864 (9:16 natif, ~2370 kbps, H.264, 5s).
Les beats TTS font 5-20s. Il faut scale → 1080×1920 ET gérer la durée.

### Solution

⚠️ **Utiliser `tpad` (freeze frame), JAMAIS `stream_loop`** (validé 2026-07-22). `stream_loop` crée des boucles visibles — le spectateur voit le clip se répéter. `tpad=stop_mode=clone` fige la dernière frame pour couvrir la durée restante, ce qui est naturel et professionnel.

```python
def build_video_segment(video_path, dur, out_path):
    """Scale 496x864 → 1080x1920, play once then freeze last frame."""
    clip_dur = get_dur(str(video_path))
    if clip_dur <= 0:
        raise RuntimeError(f"invalid clip duration: {clip_dur}")

    if dur <= clip_dur + 0.3:
        # TRIM : prendre les N premières secondes
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-t", f"{dur:.3f}",
            "-vf", "scale=1080:1920:flags=lanczos,format=yuv420p",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
            "-an", "-r", "24",
            str(out_path)
        ]
    else:
        # FREEZE FRAME : jouer le clip une fois, puis figer la dernière frame
        freeze_dur = dur - clip_dur
        vf = (
            f"scale=1080:1920:flags=lanczos,"
            f"tpad=stop_mode=clone:stop_duration={freeze_dur:.3f},"
            f"format=yuv420p"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
            "-an", "-r", "24",
            "-t", f"{dur:.3f}",
            str(out_path)
        ]
    r = subprocess.run(cmd, capture_output=True, text=True)
```

**Pourquoi pas Ken Burns ?** La vidéo IA a déjà son propre mouvement caméra/action. Un crop animé par-dessus = double motion désorientant. Scale simple suffit.

**Pourquoi `lanczos` ?** Upscale 496→1080 (2.2x). Lanczos préserve les détails mieux que bilinear/default. Le coût CPU est négligeable vs l'encode x264.

## Overlay caption (2 couches)

```python
def overlay_caption(broll_video, caption_png, dur, out_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(broll_video),                    # b-roll vidéo (1080x1920)
        "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
        "-i", str(caption_png),                    # caption PNG transparente
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
    ]
```

⚠️ **`omit_background=True` OBLIGATOIRE** sur les captions (hérité Variante D). Voir SKILL.md.

## Caption en HAUT (préférence Sankofa)

Différence vs Variante D (caption en bas) : le gradient sombre part du **top** pour laisser le bas libre aux sous-titres ASS.

```css
.desc-bar {
    position: absolute; top: 0; left: 0; right: 0;
    background: linear-gradient(to bottom,
        rgba(26,26,26,0.97) 0%,
        rgba(26,26,26,0.92) 55%,
        rgba(26,26,26,0) 100%);
    padding: 70px 60px 100px 60px;
    min-height: 520px;
}
```

## Cache de segments (reprise après timeout)

⚠️ **CRITIQUE** : la fonction `get_dur()` doit être défensive — ffprobe retourne une string vide sur les MP4 corrompus/incomplets (ex: process tué pendant encodage → `moov atom not found`). Sans try/except, le cache check lui-même crash avec `ValueError: could not convert string to float: ''`. Ce bug a fait échouer le build **3 fois** en production (Sankofa 2026-07-22).

```python
def get_dur(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except (ValueError, AttributeError):
        return -1.0   # sentinel → fichier corrompu ou introuvable

# Avant de construire un segment
seg = TMP_DIR / f"seg_{i:02d}.mp4"
if seg.exists():
    existing_dur = get_dur(str(seg))
    if existing_dur >= dur - 0.2:  # tolérance 200ms
        print(f"    [seg {i}] (cached)")
        seg_paths.append(seg)
        continue
    else:
        # Fichier corrompu (existing_dur = -1.0) — supprimer et reconstruire
        seg.unlink()

# Aussi cacher le b-roll intermédiaire
base_video = TMP_DIR / f"broll_{i:02d}.mp4"
if base_video.exists():
    if get_dur(str(base_video)) < 0:
        base_video.unlink()
if not base_video.exists():
    build_video_segment(video_path, dur, base_video)
```

**Pourquoi cacher les intermédiaires ?** Sur CPU P8700, un segment prend 30-90s. Un timeout à 600s interrompt le build en plein milieu. Le cache permet de relancer sans tout recommencer.

## Assemblage final (single pass)

```python
# Tout en une passe : subs ASS + watermark + BGM
cmd = [
    "ffmpeg", "-y",
    "-i", str(video_audio),       # vidéo concaténée + audio TTS
    "-i", str(BGM_PATH),          # BGM loop
    "-i", str(watermark_path),    # watermark PNG
    "-filter_complex",
    f"[0:v][2:v]overlay=x=W-w-20:y=H-h-20,"
    f"subtitles='{ass_escaped}'[vout];"           # subs + watermark
    f"[1:a]volume=-28dB,afade=t=in:st=0:d=1,"
    f"afade=t=out:st={dur_total-2}:d=2[bgm];"     # BGM ducked
    f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]",
    "-map", "[vout]", "-map", "[aout]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k", "-shortest",
    "-pix_fmt", "yuv420p", "-r", "24",
    str(out_path)
]
```

⚠️ **Preset `medium` sur le pass final uniquement.** Sur CPU P8700, cette passe prend **5-8 min** pour ~90s de vidéo 1080×1920. Toujours en `background=true`.

## Outro signature (concat final)

```python
r = subprocess.run([
    "ffmpeg", "-y",
    "-i", str(out_path),
    "-i", str(outro_path),
    "-filter_complex",
    "[0:v]fps=24,setsar=1[mainv];"
    "[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=24[outrov];"
    "[mainv][0:a][outrov][1:a]concat=n=2:v=1:a=1[vout][aout]",
    "-map", "[vout]", "-map", "[aout]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p", "-r", "24",
    str(final_path)
], capture_output=True, text=True)
```

## BEATS_CONFIG — mapping clips vidéo → beats

```python
BEATS_CONFIG = [
    {
        "id": "01_hook",
        "video": "02_tapis_scene.mp4",       # clip vidéo Seedance
        "caption": "1626. Un gouverneur...",
        "kicker": "Le défi",
        "fullscreen": False,
    },
    # ...
    {
        "id": "08_legacy",
        "video": None,                        # pas de clip → fallback image
        "image": "05_statue_luanda.png",     # image statique + Ken Burns
        "caption": "...",
        "kicker": "L'héritage",
        "fullscreen": False,
    },
    {
        "id": "09_cta",
        "video": None,
        "caption": "SANKOFA\nRetourne la chercher.",
        "kicker": "Abonne-toi",
        "fullscreen": True,                   # slide plein écran (CTA)
    },
]
```

## Coûts réels (production Nzinga)

| Élément | Coût | Quantité | Total |
|---------|------|----------|-------|
| Clip vidéo Seedance 2.0 Fast 480p 9:16 5s | 77.5 cr | 6 | 465 cr |
| Build (ffmpeg, CPU) | $0 | 1 | $0 |
| **Total** | | | **465 cr (~$2.33)** |

Solde initial : 1007.5 cr → solde final : 542.5 cr.

## Pièges

1. **Timeout foreground (600s)** : le build complet dépasse 600s sur CPU lent. Toujours `background=true` + `notify_on_complete=true`. Le cache de segments permet de reprendre.

2. **Segment corrompu si timeout pendant encodage** : si le process est tué pendant le pass final, le MP4 de sortie est incomplet (`moov atom not found`). Le cache ne le couvre pas — le segment final n'est pas un segment individuel. Solution : re-lancer le build (les segments intermédiaires sont cached, seul le pass final refait).

3. **`get_dur()` sur fichier incomplet → `ValueError`** : `ffprobe` retourne une string vide si le MP4 est corrompu. **Toujours** wrap dans un try/except retourant `-1.0` comme sentinel, et **supprimer le fichier corrompu** dans le cache check (`seg.unlink()`) avant de reconstruire. Voir le bloc de code "Cache de segments" ci-dessus pour le pattern complet. Ce bug a fait perdre ~20 min de debug en production (3 crashes en chaîne avant que la cause racine soit identifiée).

4. **ffprobe JSON output parfois vide** : `ffprobe -of json` peut retourner `{}` sur certains fichiers. Préférer `-of csv=p=0` (simple float string) qui est plus fiable.

5. **Ne pas oublier l'outro/watermark** (user correction "Oublie rien met la signature aussi") : l'outro signature + watermark sont dans le script mais peuvent être skip si le process timeout avant l'étape 6. Vérifier la présence de l'outro dans le fichier final via `ffprobe` durée > somme des beats TTS.
