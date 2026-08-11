# kie.ai — Modèles vidéo (catalogue, pricing, usage LEC)

kie.ai n'est pas qu'un proxy image (Grok Imagine). C'est aussi un agrégateur de modèles **text-to-video / image-to-video** avec la même clé (`KIE_API_KEY`, déjà dans l'environnement). Ce document capture le catalogue vidéo, la grille tarifaire exacte, et la règle d'usage dans le pipeline LEC.

## Catalogue vidéo (état juil. 2026, 87 modèles au total)

| Modèle | Provider | Modes | Pertinence LEC |
|--------|----------|-------|----------------|
| **Veo 3.1** | Google | T2V, I2V, Reference2V | ✅ B-roll photoréaliste (datacenters, GPU, clean rooms) |
| **Veo 3.1 Fast** | Google | T2V, I2V | ✅ Idéal prototypage (rapide, ~30% moins cher) |
| **Seedance 2 / 2.0 Mini** | ByteDance | T2V, I2V, V2V | ✅ B-roll cinématique, cohérence multi-shot |
| **Kling 2.5 Turbo** | Kling | T2V, I2V | ✅ B-roll stylisé |
| **Grok Imagine 1.5** | xAI | T2V, I2V | ⚠️ À tester |
| Seedream 5.0 Pro | ByteDance | T2V, I2V | image-seule (pas vidéo) |

> La page market (https://kie.ai/market) liste 22 providers. Filtrer "Video Models" dans la sidebar docs pour la liste exhaustive.

## Pricing Veo 3.1 (le plus pertinent pour LEC)

Grille en crédits (1 credit ≈ $0.005, conversion indiquée sur la page modèle). **High-tier top-ups (+10% bonus) réduisent le coût effectif de ~10%.**

| Mode | 720p | 1080p | 4K |
|------|------|-------|-----|
| **Lite** (T2V/I2V/Ref2V) | 30 cr ($0.15) | 35 cr ($0.175) | 150 cr ($0.75) |
| **Fast** (T2V/I2V/Ref2V) | 60 cr ($0.30) | 65 cr ($0.325) | 180 cr ($0.90) |
| **Quality** (T2V/I2V) | 250 cr ($1.25) | 255 cr ($1.275) | 370 cr ($1.85) |

**Coût estimé par short LEC** (~5 clips B-roll 4-6s en 1080p Fast) : 5 × $0.325 = **~$1.63 / short**.

## Règle d'usage LEC : B-ROLL UNIQUEMENT

⚠️ **L'IA vidéo photoréaliste est INCOMPATIBLE avec les slides textuelles LEC.** Les modèles vidéo actuels (Veo, Seedance, Kling) hallucinent le texte : caractères déformés, mots inventés, scorecards illisibles. La valeur ajoutée LEC (script bear, scorecard, analyse chiffrée) serait détruite.

| Cas d'usage | IA vidéo ? | Pourquoi |
|-------------|------------|----------|
| B-roll métaphorique (datacenter, GPU racks, clean room, carte géo) | ✅ OUI | Pas de texte à générer, pure ambiance visuelle |
| Slides avec texte/chiffres/scorecards | ❌ NON | Texte halluciné, illisible |
| Hook visuel plein écran | ⚠️ Test | Acceptable si pas de texte overlay critique |
| CTA / bumper marque | ❌ NON | Garder l'intro/outro signature existante (déterministe) |

**Séparation des pipelines** : si on expérimente l'IA vidéo B-roll, construire un pipeline **parallèle** qui ne touche pas au pipeline principal (slides HTML). Remplacer uniquement les segments Ken Burns / b-roll existants par des clips IA, jamais les slides pédagogiques.

**Test minimal avant industrialisation** : générer 3 clips Veo 3.1 Fast 1080p pour UN short existant (ex: video2 CoreWeave — datacenters/GPU), remplacer 3 Ken Burns, comparer côte à côte. Si la valeur est probante → dupliquer. Si ça distrait du message → abandonner.

## Seedance 2.0 Fast — testé en production (2026-07-22)

### Endpoint validé (API Market unifiée)

```
POST https://api.kie.ai/api/v1/jobs/createTask
```

Body :
```json
{
  "model": "bytedance/seedance-2-fast",
  "input": {
    "prompt": "...",
    "resolution": "480p",
    "aspect_ratio": "9:16",
    "duration": 5,
    "generate_audio": false
  }
}
```

⚠️ **Structure nested `input: {}` obligatoire** (contrairement à Veo3 qui utilise des params flat top-level). Un body flat retourne `{"code":500,"msg":"Server exception"}` — erreur trompeuse qui ressemble à un serveur down mais indique juste un mauvais format de body.

### Paramètres Seedance 2.0 Fast

| Param | Valeurs | Défaut |
|-------|---------|--------|
| `prompt` | 3-20000 chars | requis |
| `resolution` | `480p`, `720p` | `720p` |
| `aspect_ratio` | `1:1`, `4:3`, `3:4`, `16:9`, `9:16`, `21:9`, `adaptive` | `16:9` |
| `duration` | 4-15 (int, seconds) | 5 |
| `generate_audio` | bool | `true` |
| `first_frame_url` | URL ou `asset://{assetId}` (image-to-video) | — |
| `last_frame_url` | URL ou `asset://{assetId}` | — |
| `reference_image_urls` | array, max 9 | — |

### Mesures réelles

| Métrique | Valeur |
|----------|--------|
| **Coût (480p, 9:16, 5s)** | **77.5 crédits (~$0.39)** |
| **Latence** | ~2 min (create → result) |
| **Output** | MP4 H.264, 496×864, 24fps, ~2373 kbps, 1.4 MB |
| **State pendant processing** | `"waiting"` |
| **State final** | `"success"` |

### Comparaison Seedance vs Veo 3.1 pour LEC

Seedance 480p 77.5 credits est **plus cher** que Veo 3.1 Fast 720p (60 credits) pour **moins de résolution**. Veo 3.1 reste le meilleur rapport qualité/prix pour le B-roll LEC. Seedance est pertinent quand :
- On a besoin de son style cinématique spécifique
- On utilise l'image-to-video avec first/last frame (Seedance gère mieux ce mode)
- Le contenu est narratif/historique (african-heroes) plutôt que financier

## API : endpoints vidéo — DEUX patterns validés

⚠️ **DEUX familles d'API coexistent** selon le modèle :

| API Path | Modèles | Endpoints | Status field |
|----------|---------|-----------|-------------|
| **Dedicated Veo API** | `veo3`, `veo3_fast`, `veo3_lite` | `/api/v1/veo/generate`, `/api/v1/veo/record-info` | `data.successFlag` (0/1/2/3) |
| **Market Jobs API** | Seedance, Kling, Wan, et tous les autres | `/api/v1/jobs/createTask`, `/api/v1/jobs/recordInfo` | `data.state` ("waiting"/"success"/"fail") |

**Méthode fiable pour trouver l'endpoint d'un modèle** : consulter `https://docs.kie.ai/llms.txt` qui liste tous les modèles avec leurs URLs `.md`. Chaque `.md` contient l'OpenAPI spec complète (endpoint, body schema, paramètres).

**Différences critiques entre les deux APIs :**
- **Body structure** : Veo = params flat (`{prompt, model, aspect_ratio}`) ; Market = nested (`{model, input: {prompt, ...}}`)
- **Result location** : Veo = `data.response.resultUrls[]` ; Market = `json.loads(data.resultJson).resultUrls`
- **Status field** : Veo = `successFlag` (int) ; Market = `state` (string)
- **Error on wrong family** : 400 ou 500 générique — ne pas confondre avec un vrai serveur down

## Solde / crédits — LISIBLE via API

**Validé 2026-07-22.** Le solde EST lisible via API (contrairement aux notes précédentes) :

```
GET https://api.kie.ai/api/v1/chat/credit
Authorization: Bearer $KIE_API_KEY
```

Réponse : `{"code": 200, "msg": "success", "data": 96.0}` — `data` est un float représentant les crédits restants.

De plus, la réponse `recordInfo` inclut un champ `creditsConsumed` par tâche — utile pour le suivi budget temps réel sans poller le solde.

Exemple : Seedance 2.0 Fast 480p 9:16 5s = **77.5 crédits** consommés (mesuré en production).

## Batch parallel generation (ThreadPoolExecutor)

**Validé 2026-07-22 — 6 clips Seedance générés en parallèle pour african-heroes (Nzinga).**

Le pattern `gen_videos.py` : un script définit une liste `SCENES` (name + prompt), lance `ThreadPoolExecutor(max_workers=3)` qui soumet chaque scène via `kie_client.gen_video()`. Chaque worker crée la task, poll jusqu'à completion, télécharge.

**Pourquoi 3 workers** : Kie.ai n'a pas de rate limit documenté pour les tâches asynchrones, mais 3 workers équilibrent le débit et le risque de 429. Le rate limit documenté (20 req/10s) s'applique aux soumissions, pas au polling.

### Recovery timeout

Un clip peut timeout individuellement (300s default du wrapper) alors que les autres réussissent. **Pattern de recovery** : ne pas relancer tout le batch — le wrapper `gen_video()` skip les fichiers existants (`if out_path.exists(): return True`). Relancer le script ou le clip manquant suffit.

**Données de production** : 6 clips Seedance 480p 9:16 5s → 5/6 réussis au premier passage (1 timeout à 300s), 6e réussi au retry individuel. Total ~7.5 min de génération pour 6 clips en parallèle vs ~12 min en séquentiel.

### Template

`templates/gen_videos_batch.py` — script paramétrable : éditer `SCENES` list, configurer `OUT_DIR`, lancer. Skip automatique des clips existants, summary avec crédits consommés.

Le point d'entrée canonique pour découvrir tous les modèles et endpoints kie.ai :

```
https://docs.kie.ai/llms.txt
```

Liste tous les modèles avec leurs URLs `.md` (ex: `https://docs.kie.ai/market/bytedance/seedance-2-fast.md`). Chaque `.md` contient l'OpenAPI spec complète. **Toujours commencer par `llms.txt`** pour trouver le `model` exact et l'endpoint — ne pas deviner.

## Clé API

- `KIE_API_KEY` (ou `KIE_AI_API_KEY` en fallback) — **déjà dans l'environnement** (`.env`). Aucun setup supplémentaire.
- Client image existant (référence) : `~/.hermes/skills/cortex-leman/cortex-leman-compliance-generator/scripts/kieai_client.py` (NanoBanana, pattern async task + polling).
- Pour la vidéo : créer un `kieai_video_client.py` sur le même pattern, avec l'endpoint du modèle cible (Veo 3.1 Fast recommandé pour démarrer).
