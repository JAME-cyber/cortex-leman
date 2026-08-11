---
name: hermes-llm-cost-tracking
description: "Cost tracking + budget observabilité + protocole anti-sycophancie pour LLM agents Hermes. Pricing table (usage_pricing.py), journal de coût (hermes_cost_audit.py), critique automatique des analyses (anti_sycophancy.py). Couche observabilité économique et épistémique pour borner l'autonomie agentique."
version: 1.0.0
author: Hermes Agent (Tars)
license: MIT
metadata:
  hermes:
    tags: [cost-tracking, pricing, observability, hermes, budget]
    related_skills: [bounded-agent-execution, hermes-agent]
category: devops
---

# Hermes LLM Cost Tracking

## Quoi

Infrastructure d'observabilité économique pour Hermes: suivre, calculer et auditer le coût réel des appels LLM par session, modèle, et workflow.

## Pourquoi

**Problème observé (27/07/2026):** GLM-5.2 — 10.6M input tokens, 1.3M output sur 7 jours — coût affiché: **$0.0000**. Le modèle principal de Tars était invisible dans le tracking parce que son provider (Z.ai) n'était pas enregistré dans le pricing table.

**Racine:** Hermes collecte déjà les données d'usage (tokens, model, provider) dans SQLite. Ce qui manquait n'était pas un middleware — c'était juste l'entrée pricing et un outil de lecture.

**Solution:** 3 composants:
1. Pricing entries dans `agent/usage_pricing.py`
2. Provider recognition dans `resolve_billing_route()`
3. Script d'audit `~/.hermes/scripts/hermes_cost_audit.py`

---

## Architecture Hermes (comment le coût est tracké)

```
Appel LLM
  ↓
Agent runtime
  ↓ enregistre usage dans SQLite
state.db
├── sessions: tokens, model, provider, tool_calls, cost_status
└── session_model_usage: breakdown par modèle × task (main, compression, title_generation)
  ↓
agent/usage_pricing.py
├── _OFFICIAL_DOCS_PRICING: Dict[(provider, model)] → PricingEntry
├── resolve_billing_route(model, provider, base_url) → BillingRoute
└── estimate_usage_cost(model, usage, ...) → CostResult
  ↓
agent/insights.py — engine d'analytics (hermes insights)
```

**Tables SQLite clés:**

| Table | Granularité | Colonnes importantes |
|---|---|---|
| `sessions` | 1 ligne par session | input_tokens, output_tokens, billing_provider, estimated_cost_usd, cost_status |
| `session_model_usage` | 1 ligne par (session × modèle × task) | model, task, input_tokens, output_tokens, api_call_count |

---

## Ajouter un nouveau provider pricing (3 étapes)

### Étape 1: Ajouter les PricingEntry

Dans `~/.hermes/hermes-agent/agent/usage_pricing.py`, dict `_OFFICIAL_DOCS_PRICING`:

```python
("zai", "glm-5.2"): PricingEntry(
    input_cost_per_million=Decimal("1.40"),
    output_cost_per_million=Decimal("4.40"),
    cache_read_cost_per_million=Decimal("0.26"),
    source="official_docs_snapshot",
    source_url="https://z.ai/model-api",
    pricing_version="zai-pricing-2026-07",
),
```

Répéter pour chaque modèle du provider. La clé est `(provider_lowercase, model_lowercase)`.

### Étape 2: Ajouter la reconnaissance provider

Dans `resolve_billing_route()` — ajouter AVANT le fallback `custom`/`unknown`:

```python
if provider_name in {"zai", "zhipu"} or base_url_host_matches(base_url or "", "z.ai"):
    return BillingRoute(provider="zai", model=model.split("/")[-1],
                        base_url=base_url or "", billing_mode="official_docs_snapshot")
```

### Étape 3: Vérifier

```bash
cd ~/.hermes/hermes-agent && python3 -c "
from agent.usage_pricing import estimate_usage_cost, CanonicalUsage, has_known_pricing
usage = CanonicalUsage(input_tokens=1000000, output_tokens=100000)
result = estimate_usage_cost('glm-5.2', usage, provider='zai')
print(result)
print('Has pricing?', has_known_pricing('glm-5.2', 'zai'))
"
# Attendu: CostResult(amount_usd=Decimal('1.84'), status='estimated', ...)
```

---

## Script d'audit — `hermes_cost_audit.py`

Localisation: `~/.hermes/scripts/hermes_cost_audit.py`

### Usage

```bash
# Rapport 7 jours (format terminal)
python3 ~/.hermes/scripts/hermes_cost_audit.py --days 7

# Rapport avec alerte budget
python3 ~/.hermes/scripts/hermes_cost_audit.py --days 7 --budget 50

# Détail d'une session spécifique (JSON)
python3 ~/.hermes/scripts/hermes_cost_audit.py --session <session_id> --json

# Rapport JSON complet
python3 ~/.hermes/scripts/hermes_cost_audit.py --days 1 --json
```

### Output du rapport terminal

Le rapport produit:
1. **Overview** — sessions, coût total, coût moyen, tokens, API calls
2. **Cost by model** — répartition par modèle avec barres visuelles
3. **Cost by task** — main vs compression vs title_generation
4. **Pricing coverage** — % de sessions avec pricing connu (si <100%, il manque un provider)
5. **Top 5 expensive sessions** — identification des workflows coûteux
6. **Budget alert** — INFO (50%) / WARNING (75%) / EXCEEDED (100%) / CRITICAL (150%)

### Schéma du journal JSON

```json
{
  "generated_at": "ISO timestamp",
  "period_days": 7,
  "summary": {
    "total_sessions": 106,
    "total_cost_usd": 73.29,
    "total_input_tokens": 9684722,
    "total_output_tokens": 1176689,
    "total_api_calls": 3217,
    "avg_cost_per_session": 0.69
  },
  "pricing_coverage": {
    "sessions_with_pricing": 97,
    "sessions_without_pricing": 9,
    "pct_sessions_priced": 91.5
  },
  "cost_by_model": { "glm-5.2": {"cost": 83.04, "tokens": 11.9M, "calls": 3686} },
  "cost_by_task": { "main": {"cost": 83.30, "calls": 3679} },
  "top_5_expensive_sessions": [...],
  "budget_alert": {"level": "EXCEEDED", "pct": 147.0, "budget": 50, "actual": 73.29}
}
```

---

## Providers enregistrés

| Provider | Date ajout | Modèles | Source pricing |
|---|---|---|---|
| Z.ai (Zhipu) | 2026-07-27 | GLM-5.2, 5.1, 5, 5-turbo, 4.7, 4.7-flashx, 4.6, 4.5 | z.ai/model-api |
| OpenAI | bundled | GPT-5.6 Sol/Terra/Luna + variants | openai.com |
| Anthropic | bundled | Claude Opus/Sonnet series | platform.claude.com |
| DeepSeek | bundled | v4-pro, v4-flash | api-docs.deepseek.com |
| Google | bundled | Gemini 2.5 Pro/Flash | ai.google.dev |
| Fireworks | bundled | GLM, Kimi, DeepSeek hosted | docs.fireworks.ai |

Pour ajouter un provider: voir `references/hermes-pricing-extension.md`.

---

## Pièges

| Piège | Symptôme | Fix |
|---|---|---|
| Provider non-enregistré | $0.0000 partout, cost_status="unknown" | Ajouter PricingEntry + resolve_billing_route |
| Provider `auto` avec base_url | billing_provider="auto" mais base_url contient le domaine | base_url_host_matches() le détectera — vérifier que le match est bon |
| Double provider (direct + OpenRouter) | GLM via Z.ai ET via OpenRouter | Le pricing OpenRouter est récupéré via API dynamique, ne pas dupliquer dans le dict |
| cache_write "Limited-time Free" | Z.ai offre le cache write gratuitement | Omettre cache_write_cost_per_million (None = non facturé) |
| Modèle avec préfixe provider | `openai/gpt-5.6-luna` | model.split("/")[-1] le strip automatiquement |

---

## Métrique clé

**Le coût d'un workflow réussi et validé**, pas le coût brut d'un modèle.

Un workflow qui coûte $5 mais produit un livrable validé est plus rentable qu'un workflow à $0.50 qui échoue et doit être repris. Le journal de coût doit donc être croisé avec le taux de succès des workflows pour être interprétable.

---

## Données réelles (7 jours, 20-27 juillet 2026)

| Métrique | Valeur |
|---|---|
| Sessions | 106 |
| Coût total | $73.29 |
| Coût moyen/session | $0.69 |
| Top session | $13.97 (624 API calls, "Organisation journée") |
| Répartition | GLM-5.2: 99%, GLM-4.7 (compression): 2% |

---

## Protocole anti-sycophancie (Phase 2)

Les LLM flattent par défaut. Sans protocole structuré, l'agent produit des analyses flatteuses au lieu de rigoureuses. Sal Khan le dit lui-même — il force l'IA à "be critical of me".

**Fichier:** `~/.hermes/scripts/anti_sycophancy.py`

### Couche 1: Rule-based (gratuit, instantané)

```bash
python3 ~/.hermes/scripts/anti_sycophancy.py --file analyse.txt
echo "Texte" | python3 ~/.hermes/scripts/anti_sycophancy.py
```

Détecte: langage promotionnel (révolutionnaire, game-changer), faux dilemmes (soit/soit), conflits d'intérêts (notre produit, on lance), chiffres non sourcés. Produit un score 0-100.

| Niveau | Score | Action |
|---|---|---|
| LOW | 0-14 | OK |
| CAUTION | 15-39 | Review recommandé |
| WARNING | 40-69 | Révision requise avant exécution |
| CRITICAL | 70-100 | Analyse non fiable |

### Couche 2: LLM adversarial (optionnel, ~$0.01-0.05)

```bash
python3 ~/.hermes/scripts/anti_sycophancy.py --file analyse.txt --model glm-5.2
```

8 étapes: classification claims (fait/interprétation/recommandation), ≥2 objections fortes, hypothèses fragiles, données manquantes, conséquences d'erreur, contraintes dures, niveau de confiance, verdict (peut **refuser de conclure**).

**Règle:** le LLM n'est jamais l'autorité finale sur les sujets réglementés (AMF L541-1, RGPD, AI Act). Le moteur de règles dures override.

### Validation empirique (27/07/2026)

Test sur analyse Khan avec erreurs volontaires → Couche 1: 27/100 (CAUTION), détecté chiffres $3K/$10K non sourcés. Couche 2 (GLM-5.2): verdict "données insuffisantes", identifié conflit d'intérêts (lancement Constellation). Test contrôle (texte neutre sourcé): 0/100, zéro faux positif.

Pour les détails complets de l'implémentation: voir `references/anti-sycophancy-implementation.md`.

---

## Phase 3: Dossier de preuves (`hermes_portfolio.py`)

**Fichier:** `~/.hermes/scripts/hermes_portfolio.py`

Génère un dossier Markdown qui documente des workflows réels exécutés avec leurs métriques vérifiables. Au lieu de clamer "on peut lancer 100 agents", on prouve avec des données réelles.

```bash
# Portfolio 30 jours (Markdown)
python3 ~/.hermes/scripts/hermes_portfolio.py --days 30 --output portfolio.md

# Uniquement les workflows avec ≥20 tool calls (complexes)
python3 ~/.hermes/scripts/hermes_portfolio.py --days 30 --min-tools 20

# Détail d'une session précise
python3 ~/.hermes/scripts/hermes_portfolio.py --session <session_id>

# JSON pour pipeline
python3 ~/.hermes/scripts/hermes_portfolio.py --days 30 --json
```

Le portfolio produit:
1. **Résumé exécutif** — total workflows, coût, tool calls, tokens, coût moyen, diversité outils
2. **Split autonomie** — workflows cron (autonomes) vs interactifs, avec coûts séparés
3. **Types de workflows** — classification automatique (ArXiv scan, compliance, content, dev, research…)
4. **Cards détaillés** — par workflow: session ID, date, durée, modèle, coût, tous les tools avec counts
5. **Méthodologie** — source de données, critères d'inclusion, limitations

### Données réelles (30 jours, juin-juillet 2026)

| Métrique | Valeur |
|---|---|
| Workflows documentés | 90 |
| Coût total | $194.85 |
| Workflows autonomes (cron) | 30 (5% du coût) |
| Workflows interactifs | 60 |
| Diversité moyenne | 9.9 outils/workflow |

---

## Fichiers de référence et scripts

- **`references/hermes-pricing-extension.md`** — Procédure détaillée pour ajouter un provider au pricing table
- **`references/cost-tracking-implementation.md`** — Architecture du cost tracking, provider "auto", références pricing croisées Z.ai/OpenRouter/Fireworks
- **`references/cortex-leman-integration-points.md`** — Points d'insertion anti-sycophancie dans les workflows Cortex Leman (LEC Scout, Architecte, Gardien)
- **`references/model-routing-for-agent-autonomy.md`** — L1-L6 autonomy scale, model selection by role (orchestrator vs subagent vs cross-validator), delegation.config settings, blocking factors for L5 overnight autonomy
- **`scripts/hermes_cost_audit.py`** — Script d'audit de coût (--days, --budget, --session)
- **`scripts/anti_sycophancy.py`** — Protocole anti-sycophancie (rule-based + LLM adversarial 8 étapes)
- **`scripts/hermes_portfolio.py`** — Dossier de preuves: portfolio de workflows autonomes

---

## Lien avec autres skills

- **bounded-agent-execution** — Borne #2 (Budget) référence ce skill pour l'implémentation
- **stage-execution-loop** — L'audit de palier doit vérifier le coût réel vs budget + étape 1b-bis anti-sycophancie
- **hermes-agent** — Configuration des providers et models

## Pattern d'intégration anti-sycophancie dans workflows tiers

Quand on intègre `anti_sycophancy.py` dans un skill de workflow existant, la technique est reproductible:

1. **Mapper les étapes** — identifier où le LLM produit un verdict/score/analyse (Étape N)
2. **Identifier l'autorité finale** — guardrails, kill switch, human approval (Étape N+1)
3. **Insérer Étape Nb** entre N et N+1 — la gate anti-sycophancie
4. **Définir score→action** spécifique au domaine (LOW=pass, CAUTION=penalty, WARNING=re-collecte, CRITICAL=reject)
5. **Lister patterns spécifiques** au domaine (signaux financiers, claims compliance, ROI…)

**Intégrations actives (Cortex Leman, 2026-07-27):**

| Skill | Point d'insertion | CAUTION | WARNING |
|---|---|---|---|
| `lec-scout` | Étape 4b (avant guardrails) | Penalty Axe 2 | Re-collecte 2 sources |
| `l-architecte-lemanique` | `calculate-roi` + `final-decision` | Re-validate sources | ROI>1000% bloqué |
| `le-gardien-des-normes` | Rapport hebdo (avant livraison) | Review sources | Rapport bloqué, human review |

Détail complet: `references/cortex-leman-integration-points.md`

---

## Déploiement et versionning (repo `tars-arsenal`)

**Repo:** `JAME-cyber/tars-arsenal` (private)

### Pourquoi un repo dédié (pas un fork upstream)

Le `usage_pricing.py` modifié et les skills Cortex Leman n'ont aucun intérêt pour l'upstream NousResearch — c'est du spécifique Tars. Un fork obligerait à gérer des merges upstream réguliers pour 1 fichier.

### Règle de séparation: transportable vs local

| Élément | Repo `tars-arsenal` | Local `~/.hermes/` seulement |
|---|---|---|
| Scripts standalone (`*.py`) | ✅ Versionnés | Copie live |
| Skill générique (`hermes-llm-cost-tracking`) | ✅ Versionné | Copie live |
| Patch `usage_pricing.py` | ✅ Diff (`patches/`) | Réappliquer après update Hermes |
| Skills Cortex Leman patchés | ❌ Liés à l'env local | ✅ Restent ici |

### Setup nouveau serveur (3 commandes)

```bash
git clone https://github.com/JAME-cyber/tars-arsenal.git
cp tars-arsenal/scripts/*.py ~/.hermes/scripts/
cd ~/.hermes/hermes-agent && git apply /path/to/tars-arsenal/patches/hermes-agent/usage_pricing-zai.patch
```

**⚠️ Après chaque update Hermes:** le patch `usage_pricing-zai.patch` peut casser si le fichier upstream change. Re-générer le diff avec `git diff agent/usage_pricing.py > patches/hermes-agent/usage_pricing-zai.patch`.

---

## Sources

- Implémentation prototype (27/07/2026): pricing Z.ai + script d'audit
- Analyse croisée GLM-5.2 × GPT-5.6-luna vidéo Sal Khan "Boring Industries" — $1.2M API bill de Khan Academy a motivé le cost tracking
- Données réelles state.db Tars (106 sessions, 7 jours)
- Repo versionné: `JAME-cyber/tars-arsenal` (private, commit `8b787f6`)
