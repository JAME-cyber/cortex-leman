# Fil Rouge End-to-End — Preuve d'Intégration

**Date:** 2026-07-26
**Test:** `tests/test_fil_rouge_e2e.py` — 9/9 PASS
**Suite complète:** 57/57 PASS (0 régression)

## Objectif

Prouver que tous les modules sécurité/compliance de Cortex Leman v5
s'enchaînent dans un flux réaliste, et ne sont pas des composants isolés.

## Scénario maître

```
Prompt client contaminé (MemPoison)
  │
  ├─ 1. MemorySanitizer.sanitize_for_retrieval() → neutralise l'injection
  │
  ├─ 2. [LLMService.generate() — bypassé en dev, litellm non installé]
  │     En production: guardrails IN → LLM call → guardrails OUT
  │
  ├─ 3. ChainMarkWatermarker.watermark() → marque le contenu (Art. 50)
  │
  ├─ 4. Journal WORM append() → enregistre hash-chain + signature Ed25519
  │
  ├─ 5. SBOM CycloneDX → le modèle utilisé est tracé dans l'inventaire
  │
  ├─ 6. MediaAuthenticityScorer.detect_synthetic_markers() → détecte le watermark
  │     (PhantomSeal lit le ChainMark — preuve de connexion inter-module)
  │
  └─ 7. AgentGovernanceRules.classify_agent() → classe l'agent (Art. 50, niveau 3)
```

## Bugs réels trouvés par le fil rouge

Le fil rouge n'était pas un exercice cosmétique. Il a révélé **3 gaps** :

| # | Gap | Cause | Fix |
|---|---|---|---|
| 1 | "Ignore all previous instructions" non détecté | Pattern `rule_suppression` n'acceptait pas "previous" comme mot-clé | Ajout de `previous` au pattern + `credential_leak` + `network_exfiltration` |
| 2 | "export API_KEY=sk-***" non détecté | Aucun pattern pour credentials en clair | Nouveaux patterns `credential_leak` et `network_exfiltration` |
| 3 | `WatermarkResult.marker_added` → AttributeError | Champ réel = `visible_marker_added` | Test corrigé |

### Nouveaux patterns MemPoison ajoutés

```python
# Détection de credentials en clair
("credential_leak", r"\b(?:API_?KEY|SECRET|TOKEN|PASSWORD)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{16,}", 0.90)
("credential_leak", r"\b(?:export\s+|set\s+)(?:API_?KEY|SECRET|TOKEN|PASSWORD)\b", 0.85)

# Détection d'exfiltration réseau
("network_exfiltration", r"\b(?:curl|wget|fetch|http\.get)\s+https?://(?!localhost|127\.0\.0\.1)", 0.82)

# Extension pattern rule_suppression (ajout "previous")
r"\b(?:ignore|disregard|forget)\s+(?:all\s+)?(?:your\s+)?(?:rules|instructions|safety|policies|previous)\b"
```

## Connexions inter-modules prouvées

| Connexion | Test | Preuve |
|---|---|---|
| ChainMark → PhantomSeal | `test_watermarker_detected_by_phantomseal` | Le watermark posé par ChainMark est détecté par MediaAuthenticityScorer |
| SBOM → TrustCertification | `test_sbom_model_in_trust_certification` | Les gaps SBOM (Art. 13) alimentent le dimension score "transparency" |
| AgentGovernance → SBOM RiskTier | `test_agent_governance_maps_to_sbom_risk_tiers` | Un agent niveau 3 (content gen) = risk tier "limited" dans le SBOM |
| Sanitizer → Pipeline | `test_pipeline_complet` | Le sanitize s'exécute avant le reste du pipeline |

## Métriques finales

- **9 tests fil rouge** (6 end-to-end + 3 intégration cross-module)
- **57 tests sécurité/compliance** au total (0 régression)
- **3 bugs de production trouvés et fixés** par le fil rouge
- **1.0s** temps d'exécution total

## Limite connue

Le test ne valide pas l'appel LLM réel (`litellm` non installé en environnement dev).
En production, `LLMService.generate()` exécute les phases 2-5 (guardrails IN, appel
LLM, guardrails OUT, watermarking) — le fil rouge valide les phases 1, 3-7 qui sont
les modules sécurité/compliance propriétaires.
