# Teaser 100% Clean — Éviter le recyclage de clips long-form

## Problème
Quand on crée un teaser court (15-22s) à partir d'une vidéo long-form déjà rendue (ex: V1 PRO 100s qui a du texte burned-in sur chaque segment), on obtient:
- Texte original du long-form toujours visible sur les clips extraits
- Nouveaux sous-titres/overlays du teaser qui se superposent par-dessus
- Double texte illisible → rejet utilisateur

## Solution: Build à partir d'assets propres

### Assets nécessaires (zéro texte burned-in)
1. **Intro steam/spice** — `assets/intro_steam_spice.mp4` (3s, 1080x1920, 30fps)
2. **Hook card wax** — Background PIL procedural (voir `procedural-bg-patterns.md`) + texte drawtext en overlay
3. **Clips Seedance** — `assets/seedance_new/v1_00.mp4`, `v1_01.mp4` (720x1280, 5s, clean)
4. **Papercraft posters** — `assets/posters_papercraft/poster_{egypte,cameroun,somalie}.png` → ffmpeg zoompan + drawtext overlay (pays + plats)
5. **End card** — `renders/pro_build/end_card_v2.png` (contient déjà toutes les infos)

### Structure (21.5s)
| Time | Source | Durée | Notes |
|------|--------|-------|-------|
| 0-3s | intro_steam_spice | 3s | Conversion 30→24fps requise |
| 3-5s | hook_card (wax bg + PIL texte) | 2s | Fade in/out sur alpha |
| 5-8s | seed1 (v1_00.mp4) | 3s | Scale 720→1080 |
| 8-11s | seed2 (v1_01.mp4) | 3s | Scale 720→1080 |
| 11-12.5s | poster_egypte + overlay | 1.5s | zoompan + drawtext |
| 12.5-14s | poster_cameroun + overlay | 1.5s | zoompan + drawtext |
| 14-15.5s | poster_somalie + overlay | 1.5s | zoompan + drawtext |
| 15.5-18.5s | catering_hero.mp4 | 3s | Scale 720→1080 |
| 18.5-21.5s | end_card_v2.png | 3s | zoompan subtle |

### ffmpeg drawtext pour overlays pays
```python
vf = (
    f"drawtext=fontfile='{FONT_DIR}/Montserrat-Bold.ttf':"
    f"text='{country}':fontsize=52:fontcolor=0xF5E8D3:"
    f"x=(w-text_w)/2:y=h*0.15:"
    f"borderw=3:bordercolor=0x000000,"
    f"drawtext=fontfile='{FONT_DIR}/Montserrat-Regular.ttf':"
    f"text='{dishes}':fontsize=28:fontcolor=0xD88A22:"
    f"x=(w-text_w)/2:y=h*0.85:"
    f"borderw=2:bordercolor=0x000000"
)
```

### Script de référence
`scripts/build_teaser_clean.py` — Build complet avec VO edge-tts + musique afrobeat + TG compress.

### Audio
- VO dédiée (edge-tts DeniseNeural, rate=-5%): hook + body + cta
- **Musique: `afroswing_v2.mp3` à volume=0.12** (alignée sur T2/Catering — cohérence cross-vidéo obligatoire pour toute la campagne)
- Pad VO avec `apad=pad_dur=N` pour couvrir la durée vidéo complète

### TG compression
```
ffmpeg -crf 30 -maxrate 2500k -bufsize 5000k -preset slow -b:a 96k
```
Cible: ~2-2.5MB pour 21s en 720x1280.

## Text QA — OBLIGATOIRE avant livraison

Voir `text-qa-checklist.md` pour la checklist complète. Points clés pour le teaser:
- **VO**: vérifier les accords verbe-sujet en français ("Inscrivez-vous" pas "Inscrivez")
- **Overlays pays**: vérifier l'orthographe des noms de plats (Hawawshi, Falafel, Beignets, Sambusa, Canjeero)
- **End card**: cross-checker lieu, dates, prix contre le flyer officiel
