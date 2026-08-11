---
name: lec-scout
description: "Scout LEC autonome: évalue un signal entrant (URL, alerte, prompt) selon 5 axes, rend un verdict GO/NO-GO pour déclencher le pipeline clip L'EFFET COMPOSÉ."
version: 1.1.0
metadata:
  hermes:
    tags: [lec, scout, judge, pipeline, finance, effet-compose]
---

# LEC Scout — Cerveau de Jugement

Évalue un signal entrant et décide s'il mérite de déclencher le pipeline complet de production d'un clip L'EFFET COMPOSÉ.

## Critères de Jugement (authorité absolue)

Les critères sont définis dans `/home/tars/crypto-project/SCOUT_CRITERIA.md`. **Toujours charger ce fichier avant d'évaluer.**

5 axes, 0-2 points chacun, score max 10:
1. Pertinence LEC (infra physique cotée Euronext)
2. Densité chiffrée (≥3 chiffres sourcés = 2)
3. Qualité source (institutionnelle = 2, spécialisée = 1)
4. Angle original (data rare = 2, sujet saturé = 0)
5. Conformité AMF L541-1 (analyse = 2, conseil d'achat = 0)

**Seuils:** ≥7 = GO (pipeline), 5-6 = BORDERLINE (monitor), <5 = NO-GO (skip).

## Workflow (obligatoire)

### Étape 1 — Chargement contexte
```bash
# Charger critères
read_file: /home/tars/crypto-project/SCOUT_CRITERIA.md
# Charger mémoire projet (rappels sourcés, clips déjà faits, angles traités)
search_files: pattern="*" target="files" path="/home/tars/crypto-project/CHANNEL"
```

### Étape 2 — Collecte du signal
Si le signal est une URL:
```bash
python3 /home/tars/crypto-project/fetch_source.py "<URL>" --json --no-cache
```
Si c'est une alerte/prompt texte: utiliser directement.

### Étape 3 — Enrichissement (si source faible)
Si le signal a un bon angle mais source faible (Axe 3 = 0-1):
- Lancer `fetch_source.py` sur 2-3 sources complémentaires (IEA, Reuters, DigiTimes)
- Rejuger avec les sources enrichies

**⚠️ Pattern paywall DigiTimes (fréquent):** `fetch_source.py` retourne `status: 200` mais le contenu de l'article est derrière paywall premium. On ne récupère que `title` + `meta_description` + 1-2 paragraphes d'intro. Indicateurs de paywall: `<div id="article-lock-inline">` dans le HTML, ou moins de 3 paragraphes `<p class="p1">` extraits, ou meta_description tronquée par "...".
Si paywall confirmé: **Axe 2 (Densité chiffrée) = 0/2 automatiquement** car aucun chiffre sourcé accessible.
Pour récupérer un score viable, enrichir via `mcp__apify__apify__rag_web_browser` (web_search nécessite Firecrawl configuré — souvent absent). Chercher 3-4 sources ouvertes sur les mots-clés du signal, puis scorer avec ces sources complémentaires. L'article DigiTimes original reste la source du *signal* mais les *chiffres* doivent venir des sources ouvertes.

📖 **Recipe complète** (indicateurs paywall, étapes Apify, sources ouvertes typiques par sujet, exemple Trumpf) : `financial-content-pipeline/references/digitimes-paywall-workaround.md`.

### Étape 4 — Évaluation LLM (brouillon)
Scorer chaque axe avec justification. Produire un verdict LLM au format JSON structuré (voir SCOUT_CRITERIA.md). Ce verdict est **provisoire**.

### Étape 4b — Anti-sycophancie (gate de rigueur)

Le verdict LLM de l'Étape 4 est encore provisoire. Avant de passer aux guardrails, on vérifie qu'il n'est pas biaisé par du hype ou des chiffres non sourcés:

```bash
# Couche 1: rule-based (gratuit, instantané)
python3 ~/.hermes/scripts/anti_sycophancy.py --file /tmp/scout_verdict.txt

# Couche 2: LLM adversarial (recommandé sur signaux financiers)
python3 ~/.hermes/scripts/anti_sycophancy.py --file /tmp/scout_verdict.txt --model glm-5.2 --json
```

**Règles de décision selon le score anti-sycophancie:**

| Score | Niveau | Action |
|---|---|---|
| 0-14 | LOW | Continuer vers guardrails (Étape 5) |
| 15-39 | CAUTION | Re-score Axe 2 (Densité chiffrée) avec -1 penalty. Si chiffres non sourcés détectés, Axe 2 = 0/2 forcé |
| 40-69 | WARNING | Re-collecter 2 sources supplémentaires (Étape 3). Rejuger avec sources enrichies |
| 70+ | CRITICAL | Verdict LLM rejeté. Recommencer l'évaluation ou NO-GO |

**Patterns fréquents à surveiller sur signaux financiers:**
- "opportunité unique", "inévitable" → score CAUTION minimum
- Chiffres $/% sans "selon", "source", URL → Axe 2 = 0/2
- Mention d'un produit/compagnie avec valorisation → conflit d'intérêt potentiel

### Étape 5 — Guardrails (authorité finale)
Le verdict LLM passe par le moteur de règles dures qui peut l'override:

```bash
python3 /home/tars/crypto-project/lec_guardrails.py \
  --signal "<texte signal>" \
  --verdict '{"verdict":"GO","score":8}'
```

Si le guardrails retourne `passed: false`, le verdict final est **NO-GO forcé** quel que soit le score LLM. Le guardrails est l'autorité de conformité AMF — le LLM ne peut pas le contourner.

### Étape 6 — Action selon verdict final
- **GO (≥7, guardrails OK)**: Rédiger le script + disclaimer AMF (obligatoire si valeurs mentionnées) + notification Telegram.
- **BORDERLINE (5-6)**: Logger dans `/home/tars/crypto-project/CHANNEL/scout_log.md`, monitorer.
- **NO-GO (<5 ou guardrails override)**: Skip, logger avec raison (score faible OU règle violée).

## Format de sortie (toujours)

Réponse en 2 parties:
1. **Verdict court** (1 ligne): `VERDICT: GO 8/10 — ASML otage Taiwan — pipeline déclenché`
2. **Détail JSON** complet (bloc de code)

## Anti-patterns (à éviter)

- ❌ Ne jamais déclencher le pipeline sans avoir scoré explicitement les 5 axes
- ❌ Ne jamais scorer Axe 5 (AMF) à 2 si le signal mentionne une valeur cotée par son ticker sans disclaimer
- ❌ Ne pas confondre "sujet intéressant" et "clip réalisable" (sans chiffres sourcés = pas de clip)
- ❌ Ne pas ré-évaluer un sujet déjà traité dans `/CHANNEL/` sans angle neuf (vérifier d'abord)
- ❌ Ne pas scorer Axe 4 (Angle original) à 2 sur un simple titre paywallé — sans contenu, impossible de juger l'originalité réelle

## Conflit d'intérêt

Le scout est l'autorité de jugement. Le pipeline (génération script + rendu) est un consommateur. Si le scout est incertain, il log en BORDERLINE et attend un signal convergent.

## Logs

Tous les verdicts sont ajoutés à `/home/tars/crypto-project/CHANNEL/scout_log.md`:
```
- [2026-07-18 20:00] URL: <url> | VERDICT: GO 8/10 | Angle: ASML otage Taiwan
- [2026-07-18 21:00] URL: <url> | VERDICT: NO-GO 3/10 | Hors périmètre (crypto buzz)
```

## Webhook trigger

Le scout est déclenché via webhook `POST /webhooks/lec-scout`. Le payload DOIT contenir `"event_type": "signal"` ou le POST est silencieusement ignoré:
```json
{
  "event_type": "signal",
  "signal": "Texte du signal ou résumé",
  "url": "https://source-optionnelle.com",
  "source": "nom-source"
}
```
Header: `X-Webhook-Signature: <HMAC-SHA256 du body avec le secret de la subscription>`.
Voir `references/webhook-trigger-format.md` pour le script curl complet.
Script utilitaire: `scripts/scout_trigger.sh` — wrappeur bash qui signe et POST automatiquement (lit le secret depuis `~/.hermes/webhook_subscriptions.json`).
```
bash scripts/scout_trigger.sh "https://digitimes.com/news/..."
bash scripts/scout_trigger.sh "TSMC annonce 659M EUR subsidies"
```
