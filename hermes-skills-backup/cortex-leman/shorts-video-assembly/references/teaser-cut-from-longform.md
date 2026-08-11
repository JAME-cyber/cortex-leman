# Teaser cut — Recyclage clips depuis vidéo long-form

> ⚠️ **AVERTISSEMENT (juil. 2026)**: Cette approche (cut from long-form + sous-titres en haut) a été **REJETÉE par l'utilisateur**. Les clips du V1 PRO ont du texte burned-in intrinsèque que les sous-titres en haut ne résolvent pas — l'utilisateur a dit "ça passe pas du tout". La technique documentée dans `clean-teaser-build.md` (build à partir d'assets 100% propres) est l'approche validée. Ce fichier est conservé pour référence et cas où le recyclage est acceptable (clips source sans texte burned-in).

Technique pour produire un teaser 15-22s à partir d'une vidéo principale (90-100s+), sans regénérer de contenu IA. Utilisé pour Culture en Saveur (V1 PRO → teaser WhatsApp/Reels, juil. 2026).

## Principe

1. **Extraire** les meilleurs moments (4-6 clips de 3-4s) via `ffmpeg -ss START -t DURATION`
2. **Prépendre un hook card** (2s) avec message punchy sur fond brandé (wax, terracotta, etc.)
3. **Appender l'end card** existante (4s) pour les infos de contact
4. **Générer une VO dédiée** plus courte et punchy (pas la VO originale)
5. **Sous-titres ASS en HAUT** (Alignment 8) car les clips source ont déjà du texte burned-in

## Structure type (22s)

| Segment | Durée | Source |
|---------|-------|--------|
| Hook card (flash text) | 2s | PIL générée |
| Clip 1 (action) | 4s | Extrait V1 PRO |
| Clip 2 (contexte) | 4s | Extrait V1 PRO |
| Clip 3 (programme) | 4s | Extrait V1 PRO |
| Clip 4 (valeurs) | 4s | Extrait V1 PRO |
| End card | 4s | Image existante |

## Audio

- **VO dédiée** — ne PAS réutiliser la VO longue. Edge-tts avec hook punchy (ex: "La semaine avant la rentrée, vos enfants cuisinent l'Afrique !")
- **Pad l'audio** si VO < vidéo: `apad=pad_dur=N` puis `amix` avec musique à 0.12
- **Musique**: même track que la vidéo originale pour cohérence

## ffmpeg référence

```bash
# Extraction
ffmpeg -y -i source.mp4 -ss 11.0 -t 4.0 -an -c:v libx264 -crf 20 -pix_fmt yuv420p -r 24 clip.mp4

# Concat
printf "file 'hook.mp4'\nfile 'clip1.mp4'\n..." > concat.txt
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy video.mp4

# Audio pad + mix
ffmpeg -y -i vo.mp3 -i music.mp3 -filter_complex \
  "[0:a]apad=pad_dur=8[vo_pad];[1:a]atrim=0:22,volume=0.12,afade=t=in:st=0:d=0.5,afade=t=out:st=20:d=1.5[bg];[vo_pad][bg]amix=inputs=2:duration=longest:normalize=0[out]" \
  -map "[out]" -t 22 -c:a aac -b:a 128k audio.aac

# Final mux + subtitles
ffmpeg -y -i video.mp4 -i audio.aac -vf "subtitles=subs.ass" -c:v libx264 -crf 22 -map 0:v:0 -map 1:a:0 -t 22 final.mp4
```
