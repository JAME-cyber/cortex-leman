# Unified Outro — Outro animé commun à toute une campagne

## Problème

Une campagne vidéo (5-10 clips) a besoin d'un outro cohérent (brand identity, silhouettes, tagline). Deux approches s'offrent — et l'utilisateur a corrigé l'agent DEUX FOIS dans la même session :

### Corrections reçues (juil. 2026, Culture en Saveur)

1. **Agent crée un CTA statique PIL** → User: "Je veux la vidéo background sunset"
   - **Leçon** : quand l'utilisateur a envoyé une vidéo de référence avec un outro animé (silhouettes enfants, gradient coucher de soleil), il veut le **vrai footage vidéo animé**, pas une recréation statique en PIL/image.

2. **Agent veut overlay les prix sur le sunset** → User: "Tu overlays pas les prix sur le background sunset vidéo, les prix sont toujours un clip à part"
   - **Leçon** : le outro visuel et le pricing card sont **deux segments séparés**. Le sunset/silhouettes vient APRÈS le pricing, pas en-dessous.

3. **Agent veut inventer de nouveaux prix** → User: "Tu peux garder les prix déjà actuellement de chaque vidéo"
   - **Leçon** : toujours **extraire le pricing exact des build scripts existants** (grep `CHF`, `prix`, `formule`) avant toute modification. Ne pas reformuler.

## Architecture correcte : Body → Pricing existant → Outro unifié

```
[Contenu/VO/pricing card EXISTANT] → [clip sunset silhouettes ~4s] → fin
         (inchangé, propre à chaque vidéo)        (commun à toute la campagne)
```

- Le pricing reste **tel quel** dans chaque vidéo (ne pas toucher)
- Le outro est un **clip vidéo séparé** (pas un overlay, pas une image)
- L'outro est **le même** pour toutes les vidéos → cohérence de campagne

## Technique : batch append outro sur N vidéos

### Préparation

```bash
# 1. Extraire le clip outro de la vidéo de référence
ffmpeg -y -i reference.mp4 -ss 15 -to 19.2 \
  -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an \
  outro_bg.mp4
```

### Append batch (script Python)

```python
import subprocess
from pathlib import Path

SUNSET_CLIP = "outro_bg.mp4"  # 4.2s, 720x1280, no audio
MUSIC = "assets/music/afroswing_v2.mp3"

def append_outro(video_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),       # 0: main video
        "-i", SUNSET_CLIP,            # 1: outro (no audio)
        "-i", str(MUSIC),             # 2: music track
        "-filter_complex",
        "[1:v]scale=720:1280,fps=30[outro_v];"
        "[0:v]scale=720:1280,fps=30[main_v];"
        "[main_v][outro_v]concat=n=2:v=1:a=0[vout];"
        "[2:a]atrim=20:24.2,asetpts=PTS-STARTPTS,"
        "afade=t=out:st=3.0:d=1.2,volume=0.25[outro_music];"
        "[0:a]anull[main_a];"
        "[main_a][outro_music]concat=n=2:v=0:a=1[aout]",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k", "-r", "30",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=300)
```

### Points critiques

- **Audio outro** : musique seule (pas de VO), volume réduit (~0.25), fade-out sur les derniers 1-1.5s
- **Scale uniforme** : tout passer en 720×1280@30fps avant concat pour éviter les sauts
- **Ne pas re-encoder le body** si possible — mais le concat filter requiert un re-encode complet
- **Compression TG séparée** : après le concat, compresser avec `-crf 26 -maxrate 3200k -preset fast`

## ⚠ Pitfall : clip outro plus court que la VO CTA (coupure de fin)

**Session juil. 2026 (CES T4 funnel)** : La VO CTA durait 9.4s ("Réservez vos places ! Du 10 au 14 août, à Petit-Lancy. 85 francs la semaine, 55 la demi-journée.") mais le clip sunset faisait 4.2s. La vidéo coupait en plein milieu de "Petit-Lancy". L'utilisateur a rapporté : "ça coupe trop vite petit lancy".

**Fix : Ping-pong (forward + reverse + forward)**

Étendre le clip outro en concaténant forward → reverse → forward, puis trim à la durée voulue. L'effet aller-retour est invisible (respiration naturelle) et le mouvement reste continu.

```python
def extend_clip_pingpong(src, target_duration):
    """Extend a short clip to target_duration via forward+reverse+forward."""
    src_dur = ffprobe_dur(src)
    # Scale to target resolution first
    scaled = tmp / "scaled.mp4"
    run(["ffmpeg", "-y", "-i", src,
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
         "-r", str(FPS), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
         "-an", str(scaled)])

    # Create reversed version
    reversed = tmp / "reversed.mp4"
    run(["ffmpeg", "-y", "-i", scaled, "-vf", "reverse",
         "-r", str(FPS), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
         "-an", str(reversed)])

    # Concat: forward + reverse + forward (3 × src_dur = 12.6s for a 4.2s clip)
    pp_list = tmp / "pp.txt"
    with open(pp_list, "w") as f:
        f.write(f"file '{scaled.absolute()}'\n")
        f.write(f"file '{reversed.absolute()}'\n")
        f.write(f"file '{scaled.absolute()}'\n")

    out = tmp / "extended.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(pp_list),
         "-t", f"{target_duration:.1f}",
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
         "-an", str(out)])
    return out
```

**Formule** : `clips_needed = ceil(target_duration / src_dur)`, alterner forward/reverse. Pour 4.2s → 10.9s : forward(4.2) + reverse(4.2) + forward(4.2) = 12.6s, trim à 10.9s.

**⚠ ERREUR de syntaxe ffmpeg** : ne PAS essayer de tout faire en un seul filter_complex avec `split` + `reverse` + `concat` — le label output disparaît. Faire en 3 passes séparées (scale → reverse → concat) pour éviter les erreurs de filter graph.

**Quand utiliser** :
- Clip outro < durée VO CTA → ping-pong pour étendre
- Clip Seedance 5s qui doit couvrir une VO 9-10s → peut aussi utiliser slow-mo (voir `clip-vo-timing.md` §2) si l'écart est < 15%. Pour les outros où le mouvement est lent/paysage, le ping-pong est préférable au slow-mo extrême (>1.3x).

## Checklist unified outro

1. ✅ Extraire le clip outro animé de la vidéo de référence (`ffprobe` pour timestamps exacts)
2. ✅ Vérifier qu'il n'y a pas de texte gravé dans l'outro (sinon overlay/text burn-in à masquer)
3. ✅ Préparer la piste musique (segment ~4-5s avec fade-out)
4. ✅ **⚠ Comparer durée clip outro vs durée VO CTA** — si VO > clip, étendre via ping-pong (section ci-dessus)
5. ✅ Pour chaque vidéo : concat body + outro (ne pas toucher au body ni au pricing)
6. ✅ Compresser pour livraison TG
7. ✅ Valider durée finale + cohérence visuelle + **VO CTA se termine avant la fin de la vidéo**

## Pitfall : "recréer au lieu de couper"

L'utilisateur fournit une vidéo de référence avec un segment qu'il aime → **couper et incorporer le footage**, pas le recréer en PIL/canvas/code. Voir aussi `references/cta-unification.md` (section "CTA Segment Swap").

## Pitfall : confondre overlay et outro séparé

- ❌ Overlay = texte/image par-dessus un background vidéo → l'utilisateur a explicitement rejeté cette approche pour les prix
- ✅ Outro séparé = clip animé ajouté APRÈS le pricing card existant, sans le modifier

L'exception : si l'utilisateur demande explicitement un overlay (texte sur vidéo animée), alors utiliser une PNG transparente. Mais par défaut, **segment séparé**.
