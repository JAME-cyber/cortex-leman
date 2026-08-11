# kie.ai Video Generation API — Reference (Veo 3.1)

Condensed from docs.kie.ai (juil. 2026). Endpoints vérifiés et testés via `broll_ai.py`.

## Modèle async (CRITICAL)

Toutes les tâches kie.ai sont **asynchrones**. Un `POST /generate` retourne 200 + un `taskId` — **pas** la vidéo. Il faut poller `GET /record-info?taskId=...` jusqu'à `successFlag == 1`, puis télécharger `resultUrls[]`.

Délai typique Veo 3.1 Fast 1080p: **5-15 min** selon la charge upstream Google. Lancer en arrière-plan avec polling 2 min.

## Auth

```
Authorization: Bearer $KIE_API_KEY
Content-Type: application/json
```

Clé stockée dans `~/crypto-project/.env` sous `KIE_API_KEY`. Dashboard: https://kie.ai/api-key. Le solde crédits **n'est pas lisible via API** — uniquement sur https://kie.ai/billing (login web requis).

## Endpoints Veo 3.1

### Generate — `POST https://api.kie.ai/api/v1/veo/generate`

Body params (JSON):

| Param | Type | Requis | Valeurs | Défaut |
|-------|------|--------|---------|--------|
| `prompt` | string | ✅ | Description détaillée. Pour image-to-video: décrire comment l'image doit s'animer. | — |
| `model` | enum | — | `veo3` (Quality), `veo3_fast` (Fast), `veo3_lite` (Lite) | `veo3_fast` |
| `aspect_ratio` | enum | — | `16:9`, `9:16`, `Auto` | `16:9` |
| `resolution` | enum | — | `720p`, `1080p`, `4k` | `720p` |
| `duration` | enum<int> | — | `4`, `6`, `8` | `8` |
| `generationType` | enum | — | `TEXT_2_VIDEO`, `FIRST_AND_LAST_FRAMES_2_VIDEO`, `REFERENCE_2_VIDEO` | auto (selon `imageUrls`) |
| `imageUrls` | array<string> | — | 1 image (animer autour) ou 2 images (first/last frame). | — |
| `callBackUrl` | string | — | Webhook POST au completion. | — |
| `enableTranslation` | bool | — | Traduit le prompt vers l'anglais avant génération. | `true` |
| `watermark` | string | — | Texte watermark optionnel. | — |

Réponse 200:
```json
{"code": 200, "msg": "success", "data": {"taskId": "veo_task_abcdef123456"}}
```

Codes d'erreur: `402` = crédits insuffisants, `422` = prompt rejeté (content policy), `429` = rate limit (>20 req/10s).

### Status — `GET https://api.kie.ai/api/v1/veo/record-info?taskId=...`

Réponse (succès):
```json
{
  "code": 200,
  "data": {
    "taskId": "...",
    "successFlag": 1,              // ⚠️ AU NIVEAU data, PAS data.response
    "fallbackFlag": false,
    "completeTime": 1784563062000,
    "response": {
      "resultUrls": ["https://...mp4"],
      "originUrls": ["https://...mp4"],
      "hasAudioList": [true],
      "seeds": [18999]
    }
  }
}
```

**⚠️ CRITICAL — `successFlag` est au niveau `data`, PAS `data.response`:**
```python
# ✅ CORRECT
flag = data["data"]["successFlag"]
urls = data["data"]["response"]["resultUrls"]

# ❌ FAUX (cause boucle infinie, tâche jamais détectée comme terminée)
flag = data["data"]["response"]["successFlag"]  # retourne None indéfiniment
```
`successFlag`: `0`=generating, `1`=success, `2`=failed, `3`=gen_failed. Pattern défensif recommandé: `d.get("successFlag", resp.get("successFlag"))` pour compatibilité si l'API change.

**Important**: les médias générés sont stockés **14 jours** sur kie.ai puis supprimés. Télécharger immédiatement après completion.

## Pricing (crédits → USD)

| Mode | 720p | 1080p | 4K |
|------|------|-------|-----|
| **Lite** | 30 ($0.15) | 35 ($0.175) | 150 ($0.75) |
| **Fast** | 60 ($0.30) | **65 ($0.325)** | 180 ($0.90) |
| **Quality** | 250 ($1.25) | 255 ($1.275) | 370 ($1.85) |

Pour B-roll LEC: **Fast 1080p = 65 crédits/clip**. Un short à 5 clips = 325 crédits (~$1.63).

## Autres modèles vidéo disponibles (juil. 2026)

- **Seedance 2.0 / 2.0 Mini** (ByteDance) — cinématique, bon pour B-roll stylisé
- **Kling 2.5 Turbo / 2.6** (Kling) — bon pour motion control
- **Gemini Omni** (Google) — multimodal
- **Runway** (via API) — équivalent Gen-3/Gen-4
- **Hailuo, Wan, Infinitalk, HappyHorse, OmniHuman, Volcengine** — alternatives spécialisées

Pour le détail endpoint de chaque modèle, voir https://docs.kie.ai — la sidebar "Video Models" liste les doc pages. Le pattern async (POST generate → GET record-info) est identique pour tous.

## Modèles image (déjà intégrés)

`nano-banana` (Google), `seedream` (ByteDance), `flux-2`, `gpt-image`, `grok-imagine`, `ideogram`, `recraft`, `qwen`, `topaz`. Endpoint image: voir `scripts/kieai_client.py` dans `cortex-leman-compliance-generator` ( NanoBanana). Les endpoints vidéo suivent le même pattern async mais sous `/api/v1/veo/`.

## Pitfalls

1. **Pas de lecture de solde via API** — le endpoint billing est protégé (login web). Suivre manuellement.
2. **14 jours de rétention** — télécharger les résultats immédiatement.
3. **`enableTranslation: true`** recommandé — Veo 3.1 génère mieux avec prompts anglais, même si multilingue est supporté.
4. **Rate limit**: 20 requêtes / 10s / compte. Au-delà → HTTP 429, la tâche n'est **pas** mise en file. Espacer les soumissions de 1s minimum.
5. **Audio inclus par défaut** dans les vidéos Veo 3.1, mais expérimental — peut être supprimé sur les scènes "sensibles". Pour B-roll LEC, on retire l'audio (`-an` dans ffmpeg) car le voiceover + BGM est ajouté séparément.
