# Hermes Pricing Extension — Pattern pour ajouter un provider

## Contexte

Hermes collecte les données d'usage LLM dans SQLite (`~/.hermes/state.db`), tables `sessions` et `session_model_usage`. Mais si le pricing d'un modèle n'est pas enregistré dans `agent/usage_pricing.py`, le coût affiche $0.0000 même avec des millions de tokens.

**Cas réel (27/07/2026):** GLM-5.2 via Z.ai — 10.6M input tokens, 1.3M output tokens sur 7 jours, coût affiché: $0.0000. Après ajout du pricing: $83.04 réel.

## Architecture du pricing Hermes

```
agent/usage_pricing.py
├── _OFFICIAL_DOCS_PRICING: Dict[tuple[provider, model], PricingEntry]
│     Clé = (provider_lowercase, model_lowercase)
│   Valeur = PricingEntry(input_per_M, output_per_M, cache_read_per_M, source, ...)
├── resolve_billing_route(model, provider, base_url) → BillingRoute
│   Mappe provider/base_url → provider canonique (openai, anthropic, fireworks, zai, ...)
├── _lookup_official_docs_pricing(route) → PricingEntry | None
│   Lookup direct dans le dict
└── estimate_usage_cost(model, usage, provider, base_url) → CostResult
    Fonction principale appelée par insights.py
```

## Procédure d'ajout d'un provider (3 étapes)

### Étape 1: Ajouter les PricingEntry

Dans `_OFFICIAL_DOCS_PRICING`, ajouter les entrées `(provider, model)`:

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

### Étape 2: Ajouter la reconnaissance du provider dans resolve_billing_route()

```python
if provider_name in {"zai", "zhipu"} or base_url_host_matches(base_url or "", "z.ai"):
    return BillingRoute(provider="zai", model=model.split("/")[-1],
                        base_url=base_url or "", billing_mode="official_docs_snapshot")
```

**Important:** cette ligne doit aller AVANT le fallback `custom`/`unknown` à la fin de la fonction.

### Étape 3: Vérifier

```bash
cd ~/.hermes/hermes-agent && python3 -c "
from agent.usage_pricing import estimate_usage_cost, CanonicalUsage, has_known_pricing
usage = CanonicalUsage(input_tokens=1000000, output_tokens=100000)
result = estimate_usage_cost('glm-5.2', usage, provider='zai')
print(result)
print('Has pricing?', has_known_pricing('glm-5.2', 'zai'))
"
```

Attendu: `CostResult(amount_usd=Decimal('1.84'), status='estimated', ...)`

## Providers ajoutés (historique)

| Provider | Date | Modèles | Source pricing |
|---|---|---|---|
| Z.ai (Zhipu) | 2026-07-27 | GLM-5.2, 5.1, 5, 5-turbo, 4.7, 4.7-flashx, 4.6, 4.5 | z.ai/model-api |

## Pièges

1. **Provider `auto`**: Hermes peut enregistrer `billing_provider=auto` avec le base_url. Le resolver utilise `base_url_host_matches()` pour reconnaître le domaine. S'assurer que le base_url est bien détecté.

2. **Cas du double provider**: GLM peut être servi via Z.ai direct OU via OpenRouter. Le pricing OpenRouter est récupéré dynamiquement via l'API models, pas via le dict statique. Ne pas dupliquer.

3. **cache_write "Limited-time Free"**: Z.ai offre le cache write storage gratuitement pour l'instant. On omet `cache_write_cost_per_million` (None = non facturé séparément).

4. **Modèle avec préfixe provider**: `openai/gpt-5.6-luna` — le resolver strip le préfixe `openai/` automatiquement via `model.split("/")[-1]`.
