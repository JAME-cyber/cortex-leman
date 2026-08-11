# kie.ai Seedream 5.0 Image API — Reference

Testé via `~/culture-en-saveur/scripts/gen_papercraft_programme_v2.py` (juil. 2026).

## Auth

Identique à Seedance video: `Authorization: Bearer $KIE_AI_API_KEY`.

## Endpoints

### Create task — `POST https://api.kie.ai/api/v1/jobs/createTask`

Body:
```json
{
  "model": "seedream/5-pro-text-to-image",
  "input": {
    "prompt": "Description (long prompts OK)",
    "aspect_ratio": "3:4",
    "quality": "high",
    "output_format": "png",
    "nsfw_checker": false
  }
}
```

| Param | Type | Requis | Valeurs | Défaut |
|-------|------|--------|---------|--------|
| `model` | enum | ✅ | `seedream/5-pro-text-to-image`, `seedream/5-lite-text-to-image`, `seedream/4-5-text-to-image` | — |
| `prompt` | string | ✅ | Pas de limite stricte observée (prompts 2000+ chars OK) | — |
| `aspect_ratio` | enum | — | `1:1`, `4:3`, `3:4`, `16:9`, `9:16`, `21:9` | `1:1` |
| `quality` | enum | — | `low`, `medium`, `high` | `high` |
| `output_format` | enum | — | `png`, `jpg`, `webp` | `png` |
| `nsfw_checker` | bool | — | `false` pour désactiver | — |

**⚠️ PAS de `negative_prompt`** — cet endpoint ne supporte pas les prompts négatifs. Intégrer les exclusions dans le prompt positif ("NO cold blue tones").

**⚠️ `4:5` NON supporté** — utiliser `3:4` pour portrait vertical poster.

Réponse 200:
```json
{"code": 200, "msg": "success", "data": {"taskId": "abc123...", "recordId": "abc123..."}}
```

### Poll status — `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId={taskId}`

Même endpoint que Seedance video. **⚠️ Champs camelCase différents des conventions Python**:

| Champ API (camelCase) | ❌ Ne PAS utiliser |
|----------------------|-------------------|
| `data.taskId` | ~~`data.task_id`~~ |
| `data.state` | (correct) |
| `data.resultJson` | (correct, string JSON à parser) |
| `data.creditsConsumed` | ~~`data.credits_consumed`~~ |

**States observés**: `"generating"` → `"success"` (minuscule, PAS `"SUCCEEDED"`).

`resultJson` est un **string JSON** contenant:
```json
{"resultUrls": ["https://tempfile.aiquickdraw.com/seedream5pro/....png"]}
```

### Download image

**Contrairement à Seedance video**, le download direct de l'URL fonctionne (pas besoin de `/api/v1/common/download-url`). Un simple `requests.get(url)` télécharge l'image.

## Coût

~14 crédits/image (~$0.14) pour Seedream 5.0 Pro haute qualité, quel que soit le format.

## Temps de génération observés

| Format | Complexité | Temps typique |
|--------|-----------|---------------|
| 9:16 | Standard | ~150s |
| 3:4 | Standard | ~150-170s |
| 16:9 | Triptyque multi-éléments | ~300-330s |

**⚠️ Le `KieClient.gen_image()` interne (`~/african-heroes/scripts/kie_client.py`) a un timeout de polling de 300s**. Pour les prompts 16:9 complexes, ce timeout est dépassé. Workaround: appeler l'API directement avec un timeout de 600s (voir `~/culture-en-saveur/scripts/gen_papercraft_programme_v2.py`).

## KieClient wrapper (`~/african-heroes/scripts/kie_client.py`)

```python
from kie_client import KieClient
kc = KieClient()  # reads KIE_API_KEY from env

# Signature réelle:
kc.gen_image(
    prompt="...",
    out_path="output.png",
    model="seedream_5_pro",     # défaut
    aspect_ratio="9:16",       # défaut
    quality="high",            # défaut
    output_format="png",       # défaut
    skip_if_exists=True,       # défaut
)
# ❌ PAS de paramètre negative_prompt
# ❌ PAS de paramètre timeout (hardcodé 300s dans _poll_task)
```

**Pour des générations longues (16:9 complexe)**, bypasser KieClient et appeler l'API directement avec polling custom (timeout=600s).

## Pitfalls

1. **`taskId` camelCase** — `r.json()["data"]["taskId"]`, pas `["task_id"]`. Erreur KeyError silencieuse.
2. **`state: "success"` minuscule** — un check `if state in ("SUCCEEDED", "SUCCESS")` ne matche jamais → boucle infinie jusqu'au timeout.
3. **Timeout 300s insuffisant pour 16:9** — le poll interne de KieClient timeout avant que l'image soit prête. L'image EST générée côté serveur, mais le client ne la récupère pas.
4. **Pas de `negative_prompt`** — intégrer les exclusions dans le prompt positif ("NO cold blue tones, no watermark").
5. **Download direct OK** — contrairement aux vidéos Seedance, pas besoin de `/api/v1/common/download-url`. L'URL `tempfile.aiquickdraw.com/seedream5pro/` est publiquement accessible.
