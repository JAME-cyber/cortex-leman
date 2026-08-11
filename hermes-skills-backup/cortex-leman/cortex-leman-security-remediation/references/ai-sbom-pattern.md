# AI SBOM Pattern — Implementation Guide

**Origin**: TICKET-028, Cortex Leman v5 (2026-07-26)
**Paper**: arXiv:2607.17242 (A Large-Scale Measurement of AI Bill of Materials Completeness)
**Regulation**: AI Act Art. 11 (technical documentation), Art. 13 (transparency), RGPD Art. 30 (registre)

## Module API

```python
from core.compliance.ai_sbom import AISBOMGenerator, ModelComponent, AIActRiskTier
from core.compliance.cortex_sbom import get_cortex_sbom, get_cortex_sbom_markdown

# Pre-populated SBOM (8 models)
sbom_json = get_cortex_sbom()          # → CycloneDX 1.6 dict
sbom_md   = get_cortex_sbom_markdown() # → table

# Build from scratch (client audit)
gen = AISBOMGenerator()
gen.add_model(ModelComponent(
    name="mistralai/mistral-small-3.1-24b-instruct",
    version="3.1-24b-instruct",
    supplier="Mistral AI",
    jurisdiction="FR/EU",
    purpose="content generation and decision support",
    risk_tier="limited",
    data_categories=["user prompts", "documents"],
    license="Apache-2.0",
    model_card_url="https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503",
    security_assessment=True,
    evaluated_date="2026-01-15",
    cross_border_transfer=False,
))
gen.add_data_flow("model_a", "model_b", "description", ["data_type"])
sbom = gen.generate()               # → CycloneDX 1.6 JSON dict
md   = gen.generate_markdown()      # → human-readable table

# Validate against AI Act
gaps_11 = gen.validate_ai_act_art11(sbom)  # → list[str]
gaps_13 = gen.validate_ai_act_art13(sbom)
```

## CycloneDX 1.6 Output Structure

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "serialNumber": "urn:uuid:cortex-leman-ai-sbom",
  "version": 1,
  "metadata": {
    "timestamp": "2026-07-26T...",
    "tools": [{"vendor": "Cortex Leman", "name": "AI SBOM Generator", "version": "5.0"}]
  },
  "components": [
    {
      "type": "machine-learning-model",
      "bom-ref": "urn:ai:model:mistralai-mistral-small...",
      "name": "mistralai/mistral-small-3.1-24b-instruct",
      "version": "3.1-24b-instruct",
      "supplier": {"name": "Mistral AI"},
      "licenses": [{"license": {"name": "Apache-2.0"}}],
      "externalReferences": [{"type": "website", "url": "https://..."}],
      "properties": [
        {"name": "ai:jurisdiction", "value": "FR/EU"},
        {"name": "ai:purpose", "value": "content generation and decision support"},
        {"name": "ai:risk-tier", "value": "limited"},
        {"name": "ai:security-assessment", "value": true},
        {"name": "ai:cross-border-transfer", "value": false},
        {"name": "ai:cross-border-legal-basis", "value": "not-applicable"},
        {"name": "ai:evaluated-date", "value": "2026-01-15"},
        {"name": "ai:data-category", "value": "user prompts"},
        {"name": "ai:data-category", "value": "documents"}
      ]
    }
  ],
  "dependencies": [
    {"ref": "urn:ai:model:model-a...", "dependsOn": ["urn:ai:model:model-b..."]}
  ]
}
```

## AI Act Validation Rules

### Art. 11 (Technical Documentation)

Each component is checked for:
- `name`, `version`, `supplier` present
- `ai:jurisdiction`, `ai:purpose`, `ai:risk-tier` properties present
- `ai:data-category` present (at least one)
- `ai:security-assessment` is `True`
- `ai:evaluated-date` present
- SBOM metadata includes tool identification + timestamp

### Art. 13 (Transparency)

Each component is checked for:
- `ai:purpose`, `ai:risk-tier`, `ai:jurisdiction` present
- `externalReferences` present (model card URL)
- `ai:cross-border-transfer` present
- `ai:data-category` present

## Cortex Leman Model Inventory (8 models)

| Model | Supplier | Jurisdiction | Risk | Cross-border | Assessed |
|---|---|---|---|---|---|
| mistralai/mistral-small-3.1-24b-instruct | Mistral AI | FR/EU | limited | no | yes |
| llama3.1:8b | Meta | US/local on-premise | limited | no | yes |
| llama3.1:8b (High Protection) | Meta | US/local air-gapped | limited | no | yes |
| anthropic/claude-sonnet-4 | Anthropic | US | limited | **yes** | no |
| openai/gpt-5.6-luna | OpenAI | US | limited | **yes** | no |
| Ed25519 watermarking | Cortex Leman | local | minimal | no | yes |
| Chandra OCR 2 | Datalab | US | minimal | **yes** | no |
| text-embedding | OpenRouter/local | FR/EU or local | minimal | **yes** | no |

### Known Gaps

- `anthropic/claude-sonnet-4`, `openai/gpt-5.6-luna`, `Chandra OCR 2`, `text-embedding` lack `security_assessment=True` and `evaluated_date`. Art. 11 validation will flag these.
- Models without `model_card_url` fail Art. 13. `Ed25519 watermarking` and `text-embedding` have no card.

## Test Matrix (6 tests)

| Test | What it validates |
|---|---|
| `test_cyclonedx_format_validity` | Output is valid CycloneDX 1.6 with components + dependencies |
| `test_art11_gap_detection` | Missing security assessment + data categories + eval date → gaps reported |
| `test_art13_gap_detection` | Missing model card → transparency gap reported |
| `test_risk_tier_classification` | content_generation→limited, automated_decision→high, social_scoring→unacceptable, biometric→high |
| `test_cross_border_flag` | Claude (US) has cross_border=true; Mistral (FR/EU) has false |
| `test_markdown_generation` | Markdown table starts with header, includes model names |

## Dependencies

- None external (pure Python stdlib: `dataclasses`, `datetime`, `re`, `json`, `logging`)
- No model/API access required
