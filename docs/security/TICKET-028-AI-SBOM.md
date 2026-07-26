# TICKET-028 — AI SBOM (Bill of Materials) pour la chaîne de modèles

**Statut:** ✅ IMPLÉMENTÉ
**Priorité:** P1 (émergent réglementaire)
**Date:** 2026-07-26
**Source:** ArXiv 2607.17242 — *A Large-Scale Measurement of AI Bill of Materials Completeness*
**Référence:** AI Act Art. 11 (documentation technique), Art. 13 (transparence), RGPD Art. 30 (registre)

## Ce qui a été livré

| Composant | Description |
|---|---|
| `core/compliance/ai_sbom.py` | Générateur AI SBOM au format CycloneDX 1.6 (208 lignes) |
| `core/compliance/cortex_sbom.py` | SBOM pré-rempli avec les 8 modèles de la stack Cortex Leman |
| `tests/test_ai_sbom.py` | 6 tests : format CycloneDX, Art. 11 gaps, Art. 13 gaps, risk tiers, cross-border, markdown |

## Format — CycloneDX 1.6

Le module génère un SBOM au standard CycloneDX 1.6 avec extensions AI/ML :

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "components": [
    {
      "type": "machine-learning-model",
      "name": "mistralai/mistral-small-3.1-24b-instruct",
      "supplier": {"name": "Mistral AI"},
      "properties": [
        {"name": "ai:jurisdiction", "value": "FR/EU"},
        {"name": "ai:risk-tier", "value": "limited"},
        {"name": "ai:cross-border-transfer", "value": false},
        {"name": "ai:security-assessment", "value": true}
      ]
    }
  ]
}
```

## Inventaire Cortex Leman

| Model | Supplier | Juridiction | Risk Tier | Cross-border |
|---|---|---|---|---|
| mistralai/mistral-small-3.1-24b-instruct | Mistral AI | FR/EU | limited | non |
| llama3.1:8b | Meta | US/local on-premise | limited | non |
| llama3.1:8b (High Protection) | Meta | US/local air-gapped | limited | non |
| anthropic/claude-sonnet-4 | Anthropic | US | limited | **oui** |
| openai/gpt-5.6-luna | OpenAI | US | limited | **oui** |
| Ed25519 watermarking | Cortex Leman | local | minimal | non |
| Chandra OCR 2 | Datalab | US | minimal | **oui** |
| text-embedding | OpenRouter/local | FR/EU or local | minimal | **oui** |

## Validation AI Act

- `validate_ai_act_art11()`: vérifie documentation technique (nom, version, supplier, juridiction, purpose, risk tier, data categories, security assessment, evaluated date)
- `validate_ai_act_art13()`: vérifie transparence (purpose, risk tier, juridiction, model card, cross-border, data categories)

## Usage commercial

1. **SBOM interne** : `get_cortex_sbom()` → JSON CycloneDX pour audits réglementaires
2. **Livrable client** : `get_cortex_sbom_markdown()` → table lisible pour les rapports d'audit
3. **Template client** : `AISBOMGenerator()` vide → ajouter les modèles du client → générer CycloneDX
4. **Gap analysis** : `validate_ai_act_art11/13()` → liste de gaps à remédier pour conformité
