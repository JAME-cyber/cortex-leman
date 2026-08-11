# ArXiv Research → Compliance Module Integration

**Session**: 2026-07-26
**Module**: `core/security/research_integration.py` (287 lines)
**Tests**: `tests/test_research_integration.py` (15 tests, 15/15 ✅)

## Paper → Class Mapping

| Paper | arXiv | R | Class | Key Method | Regulatory Hook |
|---|---|---|---|---|---|
| Closing the AI Trust Gap | 2607.15992 | 12 | `TrustCertificationEngine` | `certify(system_id, metrics) → TrustCertificate` | Outcome-based certification (not checkbox) |
| Critical Analysis of Trustworthy AI Tools | 2607.15480 | 12 | `ComplianceGapScanner` | `scan(system_config) → GapReport` | 4 documented gaps vs NIST/ISO |
| ChannelGuard | 2607.19430 | 9 | `SystemSecurityCompositor` | `audit_composition(agents, interactions) → CompositionReport` | Art. 32 + Art. 35 (systemic risk) |
| Regulating Autonomous and Agentic AI | 2607.21345 | 13 | `AgentGovernanceRules` | `classify_agent(config) → AgentClassification` | Art. 9-15 + Art. 14 + Art. 50 |
| PhantomSeal | 2607.20564 | 11 | `MediaAuthenticityScorer` | `score_media(metadata) → AuthenticityScore` | Art. 50 (transparency/deepfakes) |

## Architecture

```
core/security/research_integration.py
├── PAPER_REFERENCES (dict, citation tracking)
├── TrustCertificationEngine
│   └── certify() → TrustCertificate
│       Dimensions: reliability, safety, fairness, transparency, security (0-20 each)
│       Levels: Bronze (<60), Silver (60-74), Gold (75-89), Platinum (90+)
│       Expiry: 365 days
├── ComplianceGapScanner
│   └── scan() → GapReport
│       4 gaps: explainability_depth, digital_security, design_phase, data_phase
│       Coverage % = covered / total
├── SystemSecurityCompositor
│   └── audit_composition() → CompositionReport
│       Detects: privilege_escalation, unauthenticated_channels,
│                 data_flow_loops, trust_transitivity
│       Score: 100 - penalty (critical=30, high=20, medium=10)
├── AgentGovernanceRules
│   └── classify_agent() → AgentClassification
│       Levels 0-5: 0-1 minimal, 2-3 Art.50+14, 4-5 Art.9-15+DPIA
│       Action space: minimal / bounded / broad_autonomous
└── MediaAuthenticityScorer
    ├── score_media() → AuthenticityScore
    │   Score: watermark(25) + signature(30) + provenance(25) + metadata(20)
    │   Risk: low (≥75), medium (≥45), high (<45)
    └── detect_synthetic_markers() → SyntheticDetection
        Layer 1: ChainMarkWatermarker.detect() integration
        Layer 2: visible keyword heuristics
```

## Cross-Module Wiring

| New Class | Connects To | How |
|---|---|---|
| `MediaAuthenticityScorer.detect_synthetic_markers()` | `ChainMarkWatermarker.detect()` (TICKET-022) | Imports watermarker, runs detect(), adds watermark to markers list |
| `ComplianceGapScanner` | `SecurityAuditor.Finding` format | Same severity model (high/medium), same gap/remediation structure |
| All classes | `logging.getLogger("cortex_leman.security.research")` | Consistent logger namespace |

## Test Matrix

| Test | What it covers |
|---|---|
| `test_all_certification_levels` | Bronze/Silver/Gold/Platinum thresholds |
| `test_trust_certificate_rejects_out_of_range` | Validation: scores must be 0-20 |
| `test_trust_certificate_recommendations_for_low_dimensions` | Auto-recommendations for dims < 16/20 |
| `test_all_gap_types` | 4 gaps detected on empty config |
| `test_gap_scanner_finds_no_gaps_when_all_covered` | 0 gaps on full config, 100% coverage |
| `test_composition_risk_detection` | privilege_escalation + unauthenticated + trust_transitivity |
| `test_composition_detects_data_flow_loop` | Cycle detection in interaction graph |
| `test_composition_clean_system_no_findings` | Clean system = score 100 |
| `test_agent_levels_0_3_5` | Classification at 3 autonomy levels |
| `test_agent_level_2_requires_transparency` | Art. 50 triggers at level 2 |
| `test_agent_autonomy_inferred_from_scores` | Infers level from autonomy + impact |
| `test_media_high_and_low_scores` | Score 100 (all present) vs 0 (none) |
| `test_media_partial_score` | Partial: watermark only = 25/100 |
| `test_synthetic_detection_finds_chainmark_watermark` | ChainMark integration end-to-end |
| `test_paper_references_complete` | All 5 papers referenced in PAPER_REFERENCES |

## LLM Generation Workflow (GPT-5.6 via OpenRouter)

### Prompt Structure

```
"You are a senior AI compliance engineer. Generate production Python for Cortex Leman v5."
→ For each paper: class name, key method signature, dataclass fields, arXiv ID
→ "Output ONLY valid JSON with keys 'module' and 'tests'"
→ response_format: {"type": "json_object"}
→ temperature: 0.2, max_tokens: 16000
```

### Post-Generation Steps

1. Write module + tests to `/tmp/`
2. Validate: all classes present? arXiv refs present? (string search)
3. Copy to project (`core/security/`, `tests/`)
4. Enhance tests beyond LLM-generated baseline (edge cases, cross-module integration)
5. Run pytest, fix failures
6. Write documentation (`docs/security/`)

### Pitfall: subprocess env inheritance

When the OpenRouter API key is in the shell environment (not config.yaml), calling `subprocess.run(["bash", "-c", "grep config.yaml"])` to extract it fails because the child process doesn't inherit env vars set by Hermes. **Fix**: use `os.environ.get("OPENROUTER_API_KEY")` directly in the Python script.
