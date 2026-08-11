# kie.ai Seedance 2.0 API — Reference

Condensed from docs.kie.ai/market/bytedance/seedance-2 (juil. 2026). Testé via `scripts/test_seedance_promo.py`.

**⚠️ Endpoints DIFFÉRENTS de Veo 3.1** — Seedance utilise `/api/v1/jobs/`, Veo utilise `/api/v1/veo/`. Voir `references/kieai-video-api.md` dans `le-contre-point-podcast` pour Veo.

## Auth

```
Authorization: Bearer $KIE_AI_API_KEY
Content-Type: application/json
```

Clé: variable d'environnement `KIE_AI_API_KEY`. Dashboard: https://kie.ai/api-key.

**Solde crédits via API**: `GET https://api.kie.ai/api/v1/chat/credit` → `{"code":200,"msg":"success","data":1008.0}`. **Lisible via API** (contrairement à Veo 3.1).

## Endpoints

### Create task — `POST https://api.kie.ai/api/v1/jobs/createTask`

Body:
```json
{
  "model": "bytedance/seedance-2",
  "input": {
    "prompt": "Description textuelle (3-20000 chars)",
    "generate_audio": true,
    "resolution": "720p",
    "aspect_ratio": "9:16",
    "duration": 10,
    "nsfw_checker": false,
    "first_frame_url": null,
    "last_frame_url": null,
    "reference_image_urls": [],
    "reference_video_urls": [],
    "reference_audio_urls": []
  }
}
```

| Param | Type | Requis | Valeurs | Défaut |
|-------|------|--------|---------|--------|
| `model` | enum | ✅ | `bytedance/seedance-2`, `bytedance/seedance-2-fast`, `bytedance/seedance-2-mini` | — |
| `prompt` | string | ✅ | 3-20000 chars | — |
| `resolution` | enum | — | `480p`, `720p`, `1080p`, `4k` | `720p` |
| `aspect_ratio` | enum | — | `1:1`, `4:3`, `3:4`, `16:9`, `9:16`, `21:9`, `adaptive` | `16:9` |
| `duration` | int | — | 4-15 (seconds) | `5` |
| `generate_audio` | bool | — | `true` / `false` | `true` |
| `first_frame_url` | string | — | URL ou `asset://{assetId}` | — |
| `last_frame_url` | string | — | URL ou `asset://{assetId}` | — |
| `reference_image_urls` | array | — | Max 9 images (jpeg/png/webp/bmp/tiff/gif), <30MB chacune | — |
| `reference_video_urls` | array | — | Max 3 vidéos (mp4/mov), 480p/720p, 2-15s, <50MB | — |
| `reference_audio_urls` | array | — | Max 3 audio (wav/mp3), 2-15s, <15MB | — |
| `callBackUrl` | string | — | Webhook POST au completion | — |
| `nsfw_checker` | bool | — | Désactive content filtering si `false` | — |

**⚠️ Mutuellement exclusifs**: Image-to-Video (first/last frame) et Multimodal Reference (reference_image_urls) ne peuvent PAS être utilisés simultanément.

Réponse 200:
```json
{"code": 200, "msg": "success", "data": {"taskId": "37f94a7074b1697846150f4dfde93dae", "recordId": "37f94a7074b1697846150f4dfde93dae"}}
```

### Poll status — `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId={taskId}`

**⚠️ Endpoint de polling**: `/api/v1/jobs/recordInfo` (PAS `/api/v1/jobs/{taskId}` qui retourne 404).

Réponse:
```json
{
  "code": 200,
  "data": {
    "taskId": "...",
    "model": "bytedance/seedance-2",
    "state": "success",
    "resultJson": "{\"resultUrls\":[\"https://...mp4\"]}"
  }
}
```

**Task states**: `waiting` → `queuing` → `generating` → `success` | `fail`

**⚠️ Structure différente de Veo 3.1**:
- Veo: `data.successFlag` (0/1/2/3), `data.response.resultUrls`
- Seedance: `data.state` ("waiting"/"success"/"fail"), `data.resultJson` (string JSON à parser, contient `resultUrls`)

### Download video — `POST https://api.kie.ai/api/v1/common/download-url`

**⚠️ OBLIGATOIRE** — le download direct de l'URL `resultUrls[0]` retourne **403 Forbidden**. Il faut passer par cet endpoint:

Body: `{"url": "https://tempfile.aiquickdraw.com/seedance/....mp4"}` → retourne URL signée Cloudflare R2 valide **20 minutes**.

```python
dl_result = api_request("/api/v1/common/download-url", "POST", {"url": result_url})
signed_url = dl_result["data"]  # puis urllib.urlopen(signed_url)
```

Le `templates/seedance_generate.py` fait déjà ceci automatiquement dans sa fonction `download_video()`.

## Pricing Seedance 2.0

| Résolution | Durée 5s | Durée 10s |
|-----------|----------|-----------|
| 480p | ~200 crédits | ~400 crédits |
| 720p | ~205 crédits | ~410 crédits |
| 1080p | ~210 crédits | ~420 crédits |
| 4K | ~300 crédits | ~600 crédits |

(Pricing approximatif jul 2026 — vérifier https://kie.ai/pricing)

**Rétention**: vidéos stockées 14 jours, puis suppression automatique. Télécharger immédiatement.

## Modèles Seedance disponibles

| Modèle | Endpoint model | Usage |
|--------|---------------|-------|
| Seedance 2.0 | `bytedance/seedance-2` | Qualité max, défaut |
| Seedance 2.0 Fast | `bytedance/seedance-2-fast` | Génération plus rapide |
| Seedance 2.0 Mini | `bytedance/seedance-2-mini` | Coût réduit |
| Seedance 1.5 Pro | `bytedance/seedance-1-5-pro` | Version précédente |

## Pitfalls

1. **Wrong polling endpoint** — utiliser `/api/v1/jobs/recordInfo?taskId=X` (PAS `/api/v1/jobs/{taskId}` qui retourne 404). Le script original a timeout 10 min pour cette raison.
2. **Lost task_id** — si le script foreground timeout, le `taskId` est perdu. **Toujours** sauvegarder le task_id dans un fichier (`/tmp/seedance_task_id.txt`) immédiatement après création.
3. **`resultJson` est un string** — `json.loads(data["resultJson"])` pour récupérer le dict avec `resultUrls[]`.
4. **Download URL expire en 20 min** — utiliser `/api/v1/common/download-url` pour régénérer si nécessaire. Les URLs directes dans `resultUrls` expirent après 24h.
5. **14 jours de rétention** — les fichiers générés sont supprimés après 14 jours. Télécharger et stocker localement.
6. **Duration max 15s** — pour des vidéos plus longues, générer plusieurs clips de 10-15s et concaténer avec ffmpeg.
7. **Format audio** — `generate_audio: true` produit une vidéo avec audio natif. Pour Shorts avec VO séparée, mettre `false` pour éviter l'interférence audio.
