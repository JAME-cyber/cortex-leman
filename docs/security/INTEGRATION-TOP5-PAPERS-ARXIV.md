# Intégration Top 5 Papers ArXiv → Modules Compliance Cortex Leman v5

**Date:** 2026-07-26
**Source:** `docs/strategie-2026-07/ARGUMENTAIRE-ACADEMIQUE-ARXIV-2026-07.md`

## Mapping Papers → Code

| Paper | arXiv | R | Module | Capacité |
|---|---|---|---|---|
| Closing the AI Trust Gap | 2607.15992 | 12 | `TrustCertificationEngine` | Certification outcome-based (Bronze→Platinum) |
| Critical Analysis of Trustworthy AI Tools | 2607.15480 | 12 | `ComplianceGapScanner` | Détection 4 gaps (explainability, security, design, data) |
| ChannelGuard | 2607.19430 | 9 | `SystemSecurityCompositor` | Audit compositionnel multi-agent |
| Regulating Autonomous and Agentic AI | 2607.21345 | 13 | `AgentGovernanceRules` | Classification autonomie 0-5 → obligations AI Act |
| PhantomSeal | 2607.20564 | 11 | `MediaAuthenticityScorer` | Score authenticité média + détection deepfake |

## Architecture

Module unique : `core/security/research_integration.py` (287 lignes)
Tests : `tests/test_research_integration.py` (15 tests, 15/15 ✅)

```
core/security/research_integration.py
├── PAPER_REFERENCES (dict, citation tracking)
├── TrustCertificationEngine
│   └── certify() → TrustCertificate
├── ComplianceGapScanner
│   └── scan() → GapReport
├── SystemSecurityCompositor
│   └── audit_composition() → CompositionReport
├── AgentGovernanceRules
│   └── classify_agent() → AgentClassification
└── MediaAuthenticityScorer
    ├── score_media() → AuthenticityScore
    └── detect_synthetic_markers() → SyntheticDetection
        └── integrates ChainMarkWatermarker.detect() (TICKET-022)
```

## Détail par Paper

### 1. TrustCertificationEngine — arXiv:2607.15992

**Finding original:** *"La réglementation seule ne suffit pas. Le marché nécessite une couche de certification indépendante qui rende la trustworthiness mesurable et commercialement récompensée."*

**Implémentation:**
- 5 dimensions outcome-based : reliability, safety, fairness, transparency, security
- Chaque dimension scorée 0-20 (total 0-100)
- 4 niveaux de certification : Bronze (<60), Silver (60-74), Gold (75-89), Platinum (90+)
- Recommandations automatiques pour dimensions < 16/20
- Certificat expire après 1 an

### 2. ComplianceGapScanner — arXiv:2607.15480

**Finding original:** *"Les outils Trustworthy AI actuels ont 4 gaps majeurs : explainability, sécurité numérique, phase design, phase data."*

**Implémentation:**
- Scan system_config pour 4 gaps documentés
- GapFinding avec severity, evidence, remediation, paper_reference
- Couverture % = gaps couverts / total
- Permet de positionner Cortex Leman contre NIST AI RMF / ISO 42001

### 3. SystemSecurityCompositor — arXiv:2607.19430

**Finding original:** *"La sécurité individuelle des modèles ne compose pas en sécurité système multi-agent."*

**Implémentation:**
- Détection 4 risques émergents :
  - `privilege_escalation` — privilèges accordés hors declared sets
  - `unauthenticated_channels` — canaux sans authentification
  - `data_flow_loops` — cycles dans le graphe d'interactions
  - `trust_transitivity` — confiance bidirectionnelle non-validée
- Composite security score (pénalité par finding)
- Invalide l'approche "modèle-par-modèle"

### 4. AgentGovernanceRules — arXiv:2607.21345

**Finding original:** *"Les niveaux d'autonomie mappent aux obligations AI Act."*

**Implémentation:**
- Classification automatique niveau 0-5 (à partir de autonomy + impact scores)
- Mapping obligations par niveau :
  - Level 0-1 : minimal
  - Level 2-3 : Art. 50 (transparence) + Art. 14 (oversight humain)
  - Level 4-5 : Art. 9-15 (haut-risque) + DPIA obligatoire
- Action space classification : minimal / bounded / broad_autonomous

### 5. MediaAuthenticityScorer — arXiv:2607.20564

**Finding original:** *"Framework technique pour mesure deepfake et authenticité média."*

**Implémentation:**
- `score_media()` : score 0-100 sur 4 critères (watermark, signature, provenance, metadata)
- `detect_synthetic_markers()` : intégration **ChainMarkWatermarker** (TICKET-022) + heuristique visible markers
- Risk level : low (≥75), medium (≥45), high (<45)
- Score < 50 = probable contenu synthétique sans marquage (risque Art. 50)

## Intégrations cross-modules

| Module | Intégration |
|---|---|
| ChainMarkWatermarker (TICKET-022) | `MediaAuthenticityScorer.detect_synthetic_markers()` |
| SecurityAuditor (auditor.py) | `ComplianceGapScanner` utilise même format Finding |
| AppendOnlyJournal | Logging via `logging.getLogger("cortex_leman.security.research")` |

## Tests (15/15 ✅)

| Test | Couverture |
|---|---|
| `test_all_certification_levels` | Bronze/Silver/Gold/Platinum |
| `test_trust_certificate_rejects_out_of_range` | Validation bornes 0-20 |
| `test_trust_certificate_recommendations_for_low_dimensions` | Recommandations auto |
| `test_all_gap_types` | 4 gaps détectés sur config vide |
| `test_gap_scanner_finds_no_gaps_when_all_covered` | 0 gaps sur config complète |
| `test_composition_risk_detection` | privilege_escalation + unauthenticated + trust_transitivity |
| `test_composition_detects_data_flow_loop` | Cycle A→B→A détecté |
| `test_composition_clean_system_no_findings` | Système sain = score 100 |
| `test_agent_levels_0_3_5` | Classification 3 niveaux |
| `test_agent_level_2_requires_transparency` | Art. 50 à partir de level 2 |
| `test_agent_autonomy_inferred_from_scores` | Inférence niveau depuis autonomy+impact |
| `test_media_high_and_low_scores` | Score 100 vs 0 |
| `test_media_partial_score` | Score partiel (25/100) |
| `test_synthetic_detection_finds_chainmark_watermark` | Intégration ChainMark |
| `test_paper_references_complete` | 5 papers référencés |
