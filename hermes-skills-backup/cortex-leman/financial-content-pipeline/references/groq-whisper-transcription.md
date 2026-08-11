# Transcription audio rapide via API Groq Whisper

## Problème

Sur CPU Core 2 Duo P8700, Whisper local (`tiny` ou `base`) prend **>10 min pour 10 min d'audio**. Inutilisable pour extraire du signal depuis des podcasts/vidéos YouTube.

## Solution : API Groq `whisper-large-v3-turbo`

La clé `GROQ_API_KEY` est déjà configurée dans `~/.hermes/config.yaml` (provider `stt.groq`). Le modèle `whisper-large-v3-turbo` offre une qualité équivalente à `whisper-large-v3` avec une latence drastiquement réduite.

### Pipeline complet (3 étapes)

```bash
# 1. Télécharger l'audio via yt-dlp
yt-dlp -x --audio-format mp3 -o "/tmp/audio.mp3" "<URL_YOUTUBE>"

# 2. Si >25MB, splitter en segments <25MB (limite API Groq)
ffmpeg -i /tmp/audio.mp3 -f segment -segment_time 600 -c copy /tmp/audio_part_%02d.mp3

# 3. Transcrire chaque segment
GROQ_KEY=$(python3 -c "import yaml; c=yaml.safe_load(open('$HOME/.hermes/config.yaml')); print(c.get('stt',{}).get('groq',{}).get('api_key',''))")

for f in /tmp/audio_part_*.mp3; do
  curl -s https://api.groq.com/openai/v1/audio/transcriptions \
    -H "Authorization: Bearer $GROQ_KEY" \
    -F "file=@$f" \
    -F "model=whisper-large-v3-turbo" \
    -F "response_format=text" >> /tmp/transcript.txt
done
```

### Performance mesurée (2026-07-22)

| Audio | Durée | Taille | Transcription | Qualité |
|---|---|---|---|---|
| 10 min YouTube → 3 segments × ~22MB | 10:00 | 65 MB | **11 secondes** | Excellente (FR + sigles techniques) |
| Même audio, Whisper `base` local | 10:00 | — | >10 min (estimé, abandonné) | Inférieure |

### Coût

Gratuit (tier Groq free). Limite de rate : ~30 min/jour en free tier.

### Limites

- **25 MB par requête** → splitter les fichiers longs. `ffmpeg -f segment -segment_time 600` (10 min/segment) fonctionne bien.
- Pas de timestamps mot par mot en mode `response_format=text`. Pour des timestamps, utiliser `response_format=verbose_json` (mais output plus volumineux).
- Le modèle peut rater des sigles très techniques — toujours vérifier les passages clés manuellement.

## Extraction de signal mineur depuis une transcription

Une fois la transcription obtenue, si la source est globalement hors périmètre mais contient un angle pertinent:

1. **Scan manuel** du transcript pour identifier les segments pertinents (recherche par mots-clés du périmètre LEC: infrastructure, sécurité, semi-conducteurs, IA, data center)
2. **Isoler** le passage (copier le texte autour de la mention)
3. **Évaluer** l'angle isolé via les critères scout (généralement BORDERLINE 5-6/10)
4. **Enrichir** avec sources primaires externes via Apify `rag_web_browser`
5. **Re-scorer** — un BORDERLINE peut monter à GO si les sources primaires confirment et chiffrent

## Alternatives testées et rejetées

| Méthode | Résultat | Raison de l'échec |
|---|---|---|
| `youtube-transcript-api` Python | ❌ Aucun caption track | Vidéo sans sous-titres YouTube |
| API YouTube `timedtext` direct | ❌ Réponse vide | Pas de captions auto-générées |
| `web_extract` sur l'URL YouTube | ❌ Contenu vide | JS-rendered, pas de transcript dans le HTML |
| Whisper `base`/`tiny` local | ⏱️ >10 min | CPU Core 2 Duo trop lent |
| KIE.ai API (proxy) | ❌ 403 | Bloqué sur compte basic |

La solution Groq est la seule qui fonctionne de bout en bout dans l'environnement actuel.
