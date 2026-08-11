# xAI Imagine Direct API (grok-imagine-image)

> Recipe testée 2026-07-18. À n'utiliser que si kie.ai est indisponible.
> **Coût: $2/image standard, $5/image quality** — kie.ai = $0.003/image.

## Modèles disponibles (GET /v1/models)

```
grok-4.20-0309-non-reasoning   grok-4.20-0309-reasoning
grok-4.20-multi-agent-0309     grok-4.3    grok-4.5
grok-build-0.1
grok-imagine-image             ← image standard ($2)
grok-imagine-image-quality     ← image quality ($5)
grok-imagine-video             grok-imagine-video-1.5
```

**TTS absent** : aucun modèle `tts`/`voice`/`speech` → endpoint `/v1/audio/speech` retourne 403 "Team is not authorized" (restriction plan, pas clé).

## Endpoint image (working)

```python
import urllib.request, json, base64, os

with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if line.startswith("XAI_API_KEY="):
            key = line.strip().split("=",1)[1]

url = "https://api.x.ai/v1/images/generations"
body = json.dumps({
    "model": "grok-imagine-image",       # NE PAS utiliser "grok-2-image" (404)
    "prompt": "Data center, blue lights, cinematic, 9:16 vertical",
    "n": 1,
    "response_format": "b64_json"         # OBLIGATOIRE — "url" retourne un 403 au download
}).encode()
req = urllib.request.Request(url, data=body, headers={
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
})
with urllib.request.urlopen(req, timeout=120) as r:
    data = json.loads(r.read())

# Coût
cost_usd = data["usage"]["cost_in_usd_ticks"] / 1e8   # = 2.0
# Image
img_bytes = base64.b64decode(data["data"][0]["b64_json"])
```

## Pièges constatés

| Test | Résultat |
|---|---|
| `grok-2-image` model | ❌ 404 "model does not exist" |
| `response_format: "url"` | ❌ URL `imgen.x.ai` → HTTP 403 au download (même avec bearer) |
| `response_format: "b64_json"` | ✅ Fonctionne, image en base64 |
| Download via `urllib.urlretrieve(url)` | ❌ 403 (URL signée expirée ou restreinte) |
| Download avec `Authorization: Bearer` header | ❌ 403 aussi |
| `/v1/audio/speech` (TTS) | ❌ 403 "Team not authorized" (tous les modèles de voix) |

## Verdict usage projet

- **Chat Grok** : ✅ via xAI direct (déjà routé via OpenRouter aussi).
- **Images** : ❌ **toujours kie.ai** (proxy, $0.003/image, même moteur). Voir `references/kie-ai-api-quirks.md`.
- **TTS** : ❌ plan xAI sans Voice → rester sur edge-tts.

## Mémo économie

Pour une série 3 acteurs × 4 visuels = 12 images :
- kie.ai : **$0.04**
- xAI direct standard : **$24** (600x plus)
- xAI direct quality : **$60** (1500x more)
