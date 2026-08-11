# API KIE.ai — Quirks et patterns validés (juillet 2026)

## Modèle disponible : Grok Imagine (text-to-image)

### Endpoint working

```
POST https://api.kie.ai/api/v1/jobs/createTask
Authorization: Bearer ${KIE_AI_API_KEY}
Content-Type: application/json
```

### Payload validé

```json
{
  "model": "grok-imagine/text-to-image",
  "input": {
    "prompt": "...",
    "aspect_ratio": "9:16",
    "quality": "standard"
  }
}
```

Réponse : `taskId`. Poll `GET /api/v1/jobs/recordInfo?taskId=...` jusqu'à `state=success`, puis `resultJson.resultUrls` (array de 6 URLs).

### Coût

- 4 credits = $0.02 pour 6 images 9:16
- Délai ~15s

## Chat models — NON disponibles sur compte basic

**Perdu 15 min à explorer**. Ne pas répéter.

### Endpoints testés (tous KO sur compte basic)

| Endpoint | Statut |
|---|---|
| `POST /api/v1/jobs/createTask` (model=gpt-5.6 etc.) | 422 "model not supported" |
| `POST /api/v1/chat/completions` | 500 "Operation not found" |
| `POST /openai/v1/chat/completions` | 422 "model is not supported" |

### Modèles testés en vain

`gpt-5.6`, `gpt-5-6-luna`, `gpt-5-6-terra`, `gpt-5-6-sol`, `gpt-5.5`, `gpt-4o`,
`gemini-3-flash`, `gemini-3-flash-openai`, `gemini-2.5-flash`, `grok-4-5`,
`grok-4.5`, `grok-4-3`, `claude-sonnet-5`, `claude-haiku-4.5`, `claude-opus-4.7`,
`deepseek-v4`, `deepseek-chat`.

### Conclusion

- Le compte KIE.ai basic n'a accès qu'aux modèles image/vidéo, pas aux chat.
- Pour générer un script : l'écrire directement (l'agent LLM courant le fait),
  ou utiliser un autre provider (Anthropic direct, OpenAI direct, etc.).

## Ken Burns effect vertical 9:16 — éviter zoompan

### Problème

`zoompan` ffmpeg est **10x trop lent** en vertical 1080×1920. Un clip de 9s
peut prendre >2 minutes à encoder, voire timeout à 180s.

### Pattern alternatif validé (pan animé)

```python
# Scale up 30% pour donner du headroom au pan
# puis crop 1080×1920 avec offset x animé par t
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-loop", "1", "-framerate", "24", "-t", str(DURATION),
    "-i", IMAGE,
    "-vf", (
        "scale=1404:-2,"
        f"crop=1080:1920:x='(in_w-1080)/2 - (in_w-1080)/2*0.3*(t/{DURATION})':y='(in_h-1920)/2',"
        "format=yuv420p"
    ),
    "-c:v", "libx264", "-preset", "fast", "-crf", "21",
    "-pix_fmt", "yuv420p", "-r", "24",
    OUTPUT
]
```

- Hook (9s) : pan gauche → droite (offset `-` sur x)
- CTA (5s) : pan droite → gauche (offset `+` sur x)

### Alternative écartée

```
zoompan=z='min(zoom+0.0008,1.10)':d=24*DUR:s=1080x1920:fps=24
```

Fonctionne mais **beaucoup trop lent** en vertical.

## edge-tts — voix françaises valides (juillet 2026)

### Masculines

- `fr-FR-HenriNeural` — voix principale hôte (L'EFFET COMPOSÉ)

### Féminines

- `fr-FR-DeniseNeural` — analyste Claire (claire, posée)
- `fr-FR-EloiseNeural` — alternative plus jeune
- `fr-FR-VivienneMultilingualNeural` — plus grave, internationale

### ❌ N'existe pas (erreur `NoAudioReceived`)

- `fr-FR-JennyNeural`

### edge-tts 7.x — WordBoundary cassé

L'événement `WordBoundary` n'est plus émis en 7.x. Workaround : distribution
proportionnelle des mots par durée totale pour générer des sous-titres.

## Audio BGM standard

- Fichier : `/home/tars/crypto-project/audio/bgm_stellardrone.mp3`
- Ducking : `volume=0.08` (~-22 dB) avec fades 2s in/out
- Mix : `amix=inputs=2:duration=shortest`

## Encodage final

- Podcast : MP3 192k
- Clips : MP4 H.264 crf=21, preset=fast, 24fps, 1080×1920, yuv420p
