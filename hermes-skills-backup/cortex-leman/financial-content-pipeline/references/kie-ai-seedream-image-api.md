# kie.ai Seedream 5.0 Pro — Image Generation API

Modèle texte-vers-image haute qualité (2048×2048 natif, aspect ratio configurable). Alternative à Grok Imagine pour des illustrations détaillées (portraits historiques, scènes narratives, cartes).

## Endpoints

### 1. Create Task (async)

```
POST https://api.kie.ai/api/v1/jobs/createTask
Authorization: Bearer $KIE_AI_API_KEY
Content-Type: application/json

{
  "model": "seedream/5-pro-text-to-image",
  "input": {
    "prompt": "...",
    "aspect_ratio": "9:16",        // "1:1", "16:9", "9:16", "4:3", "3:4"
    "quality": "high",              // "standard" | "high"
    "output_format": "png",         // "png" | "jpeg" | "webp"
    "nsfw_checker": false
  }
}
```

**Réponse** :
```json
{
  "code": 200,
  "data": { "taskId": "9026687bc249e74f72bebd4b44f5aaea" }
}
```

### 2. Poll Task (recordInfo)

```
GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=<taskId>
Authorization: Bearer $KIE_AI_API_KEY
```

**Réponse (success)** :
```json
{
  "code": 200,
  "data": {
    "taskId": "...",
    "state": "success",            // "queued" | "processing" | "success" | "fail"
    "resultJson": "{\"resultUrls\": [\"https://tempfile.aiquickdraw.com/p/<id>.png\"]}",
    "failMsg": null
  }
}
```

⚠️ `resultJson` est une **string JSON** — pas un objet direct. Il faut `json.loads(data["resultJson"])` pour extraire `resultUrls`.

### 3. Download

L'URL dans `resultUrls[0]` est publique (pas d'auth), download direct via `requests.get()`.

## Pattern Python réutilisable

```python
import requests, json, time, os

KIE_KEY = os.environ.get("KIE_AI_API_KEY")  # ou grep depuis .env
API = "https://api.kie.ai/api/v1/jobs"

def generate_image(prompt, aspect_ratio="9:16", quality="high", timeout=180):
    """Create + poll + return image bytes."""
    # Create
    r = requests.post(f"{API}/createTask",
        headers={"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"},
        json={"model": "seedream/5-pro-text-to-image",
              "input": {"prompt": prompt, "aspect_ratio": aspect_ratio,
                        "quality": quality, "output_format": "png", "nsfw_checker": False}},
        timeout=30)
    r.raise_for_status()
    task_id = r.json()["data"]["taskId"]

    # Poll
    for _ in range(timeout // 5):
        r = requests.get(f"{API}/recordInfo", params={"taskId": task_id},
                       headers={"Authorization": f"Bearer {KIE_KEY}"}, timeout=15)
        data = r.json().get("data", {})
        if data.get("state") == "success":
            urls = json.loads(data.get("resultJson", "{}")).get("resultUrls", [])
            if urls:
                return requests.get(urls[0], timeout=30).content
        elif data.get("state") == "fail":
            raise RuntimeError(f"Task failed: {data.get('failMsg')}")
        time.sleep(5)
    raise TimeoutError(f"Task {task_id} timed out")
```

## Quirks

- **Timeouts fréquents** : Seedream peut prendre 2-6 min/image. Prévoir un polling avec timeout généreux (180-360s). Sur charge élevée, ~40% des tâches timeout.
- **Retry pattern** : les timeouts ne sont pas des échecs définitifs — relancer la même tâche fonctionne souvent (le modèle ne facture pas les tâches échouées).
- **Pas de seed control** : contrairement à Grok Imagine (6 variants par appel), Seedream génère une seule image. Pour des variants, appeler N fois avec des prompts légèrement modifiés.
- **Coût** : ~$0.01-0.03/image selon qualité. Vérifier le dashboard https://kie.ai/billing pour le solde exact.
- **Qualité vs Grok Imagine** : Seedream 5.0 Pro est supérieur pour les scènes narratives complexes (personnages, décors, composition historique). Grok Imagine reste bon pour les visuels abstraits/data center.

## Modèles image disponibles sur kie.ai

| Modèle | ID | Usage | Force |
|---|---|---|---|
| **Seedream 5.0 Pro** | `seedream/5-pro-text-to-image` | Scènes narratives, portraits, illustrations détaillées | Texte détaillé, composition complexe |
| Grok Imagine | `grok-imagine/text-to-image` | Visuels ambiance (data centers, tech) | Rapide, bon marché, 6 variants |
| GPT Image 2 | `gpt-image-2` | Visuels polyvalents | Alternative |
| Ideogram v3 | `ideogram-v3` | Texte dans l'image | Logos, typographie |

## Comparaison Seedream vs Grok Imagine (LEÇON 2026-07-21)

| Critère | Grok Imagine | Seedream 5.0 Pro |
|---|---|---|
| Latence | ~30s | 100-280s (mesuré 2026-07-24) |
| Variants par appel | 6 | 1 |
| Qualité narrative | Bon | Excellent (scènes complexes) |
| Coût/image | $0.003 (~5.5 cr) | **14 crédits/image** (mesuré 2026-07-24) |
| Fiabilité | Haute | Moyenne (retry nécessaire) |

**Choix par défaut** : Grok Imagine pour les clips finance (ambiance tech, rapidité, 6 variants). Seedream pour les projets historiques/narratifs (portraits, scènes d'action, illustrations détaillées).

### Génération parallèle Seedream (VALIDÉ 2026-07-24, projet Culture en Saveur)

7 images 9:16 quality=high générées avec ThreadPoolExecutor(max_workers=3). Résultats mesurés :

| Métrique | Valeur |
|---|---|
| Coût/image | 14 crédits Seedream 5-pro |
| Latence min | 100s (03_immersion_cooking) |
| Latence max | 280s (06_offre_famille) |
| Latence médiane | ~166s |
| Total 7 images | 98 crédits |
| Parallélisme | 3 workers concurrents — pas de rate limit observé |

**Pattern validé** : chaque worker fait createTask → poll recordInfo toutes les 10s → download. Les 7 tâches peuvent tourner en parallèle sans 429 (kie.ai limite = 20 req/10s, 3 workers polling à 10s = bien en-dessous).

**Fallback gradient ffmpeg** : si une image abstraite (background CTA, texture) prend trop de temps ou si les crédits sont épuisés, générer un gradient local via `ffmpeg -f lavfi -i "color=..."` (1s, 0 crédit). Valable seulement pour des backgrounds purs, pas pour des scènes narratives.

## Source

Pattern validé sur projet Sankofa (african-heroes), 2026-07-21 (9 images, retry). Parallélisation validée projet Culture en Saveur, 2026-07-24 (7 images ThreadPoolExecutor-3).
