# Unified Intro Stinger — Signature de marque en ouverture

## Problème

Une campagne de N vidéos doit s'ouvrir de façon cohérente. Le stinger (signature animée + audio de marque) est l'équivalent du "logo ident" TV — il signe chaque clip comme appartenant à la même famille.

**Session juil. 2026 (Culture en Saveur)** : 7 vidéos existaient déjà avec leurs intro/CTA propres. L'utilisateur a vu le stinger (`signature_ces_stingered.mp4`, 3.5s) et a dit "c'est notre signature" → le prépendre à toutes les vidéos.

## Architecture complète : Stinger → Body → Outro

```
[Stinger ~3.5s] → [Contenu + pricing card EXISTANT] → [Outro unifié ~4s]
 (brand signature)      (propre à chaque vidéo)        (commun, voir unified-outro.md)
```

Structure 3-segments en une seule passe ffmpeg :

```python
import subprocess
from pathlib import Path

STINGER = "assets/signature_ces_stingered.mp4"   # 3.5s, 1080x1920, has audio
SUNSET  = "renders/sunset_bg.mp4"                 # 4.2s, 720x1280, no audio
MUSIC   = "assets/music/afroswing_v2.mp3"

def build_branded(src_path, out_path):
    """
    Prepend stinger + append sunset outro in ONE ffmpeg pass.
    4 inputs: stinger, main video, sunset clip, music track.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", str(STINGER),    # 0: stinger (has audio)
        "-i", str(src_path),   # 1: main video (has audio)
        "-i", SUNSET,          # 2: sunset bg (no audio)
        "-i", str(MUSIC),      # 3: music for outro
        "-filter_complex",
        # Video: scale everything to 720x1280@30 then concat 3 segments
        "[0:v]scale=720:1280,fps=30[sting_v];"
        "[1:v]scale=720:1280,fps=30[main_v];"
        "[2:v]scale=720:1280,fps=30[sun_v];"
        "[sting_v][main_v][sun_v]concat=n=3:v=1:a=0[vout];"
        # Audio: stinger audio → video audio → music fade-out for outro
        "[3:a]atrim=20:24.2,asetpts=PTS-STARTPTS,"
        "afade=t=out:st=3.0:d=1.2,volume=0.25[outro_mus];"
        "[0:a]anull[sting_a];"
        "[1:a]anull[main_a];"
        "[sting_a][main_a][outro_mus]concat=n=3:v=0:a=1[aout]",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k", "-r", "30",
        str(out_path)
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=600)
```

## Points critiques

1. **Stinger garde son audio** — Le stinger a sa propre piste audio (signature sonore de marque). Ne pas la remplacer par la musique de fond.
2. **⚠ SÉPARATION AUDIO STINGER → VO/MUSIQUE (pitfall critique)** — Si le stinger est prépendu ET que VO + musique démarrent à 0s, les pistes se chevauchent. L'utilisateur a corrigé ça: "il faut bien séparer le son entre notre signature intro et le début des vidéos car les sons se chevauchent". **Fix**: retarder VO et musique avec `adelay`:
   ```python
   # Stinger (3.5s) joue SEUL avec son propre audio
   # Musique démarre à 3.7s (200ms de respiration après stinger)
   # VO démarre à 3.9s (après le hook visuel)
   filter = (
       "[sting_a]volume=1.0[a_sting];"           # stinger à volume plein
       "[vo]volume=2.5,adelay=200|200[a_vo];"    # VO démarre 200ms après fin stinger
       "[mus]volume=0.12,adelay=3700|3700,"      # musique à 3.7s
       "afade=t=out:st={dur-2}:d=2[a_mus];"      # fade-out 2s avant fin
       "[a_sting][a_vo][a_mus]amix=inputs=3:duration=longest:normalize=0"
   )
   ```
   **Règle**: stinger audio = isolé. VO + musique = décalées de ≥200ms après la fin du stinger. JAMAIS de chevauchement.
3. **Resolutions mixtes** — Le stinger peut être en 1080x1920 (qualité sup), le body en 720x1280. Tout scaler à 720x1280@30fps avant concat avec `scale=720:1280,fps=30`.
3. **Le body n'est pas touché** — Pricing, VO, contenu restent inchangés. Le stinger est un PREFIXE pur.
4. **Audio concat 3-segments** — `concat=n=3:v=0:a=1` sur 3 flux audio : stinger_audio → body_audio → outro_music_fadeout.

## Compression escalation

Après ajout du stinger (+3.5s), certaines vidéos dépassent 5MB même après CRF 26 :

| Cas | Commande | Résultat typique |
|-----|----------|-----------------|
| Standard (<45s) | `-crf 26 -maxrate 3200k -bufsize 6400k` | 3-5MB |
| Heavy (>50s, ex: T4 53s) | `-crf 28 -maxrate 2800k -bufsize 5600k` | 7-9MB |
| Ultra (>60s) | Scale 540:960 + `-crf 30 -maxrate 2000k` | 4-5MB |

Toujours tenter le standard d'abord, vérifier la taille, puis escalader si >8MB.

## Checklist branded wrapper

1. ✅ Vérifier que le stinger existe et a une piste audio (`ffprobe`)
2. ✅ Préparer le clip outro (`sunset_bg.mp4` ou équivalent)
3. ✅ Préparer le segment musique pour l'outro (atrim + fade-out, volume ~0.25)
4. ✅ Batch-process toutes les vidéos avec le même filter_complex
5. ✅ Compresser pour TG (escalader CRF si nécessaire)
6. ✅ Valider durée finale (body + 3.5s stinger + 4.2s outro)

## Distinction avec unified-outro.md

- `unified-outro.md` couvre l'outro seul (append après le CTA)
- `unified-intro-stinger.md` (ce fichier) couvre le **wrapper complet 3-segments** : stinger + body + outro
- Les deux patterns sont complémentaires et utilisés ensemble dans la même campagne
