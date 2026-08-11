---
name: cortex-leman-agent-patterns
category: cortex-leman
description: |
  Design patterns for building safe, maintainable Cortex Leman agents.
  Covers command risk classification (safety layer) and single-purpose tool design (decomposition pattern).
  Inspired by 12 Agentic Harness Patterns.
  See references/ for detailed implementation guides.
version: 1.0.0
---

# Cortex Leman Agent Design Patterns

Reusable design patterns for building Cortex Leman agents. Both patterns address the same core problem: agent reliability and safety.

## Pattern 1: Command Risk Classification

Safety layer for Cortex Leman agents that classifies command risks BEFORE execution. Prevents dangerous operations, enforces manual approval for critical operations, and provides audit trail.

### Risk Levels

| Level | Classification | Examples | Action |
|-------|---------------|----------|--------|
| 1 | LOW RISK (Safe) | ls, cat, echo, pwd | Auto-execute |
| 2 | MEDIUM RISK | cp, mv, pip install | Log + execute |
| 3 | HIGH RISK | rm -rf, chmod 777, sudo | Require approval |
| 4 | CRITICAL | dd, mkfs, format, :(){ :|:& };: | Block + alert |

### Implementation

1. Classify each command before execution
2. Apply appropriate action per risk level
3. Log all classified commands for audit trail
4. Never auto-execute Level 3-4 without explicit approval

**Full implementation guide:** `references/command_risk_classification.md`

---

## Pattern 2: Single-Purpose Tool Design

Decompose monolithic agent skills into single-purpose micro-tools. Each tool does ONE thing well, making code maintainable, testable, and composable.

### Problem: Monolithic Skills

Skills with too many responsibilities become unmaintainable, untestable, and fragile.

### Solution: Micro-Tool Architecture

```
BEFORE: LeGardienDesNormes (monolithic - does EVERYTHING)
  ├── audit_system()
  ├── check_compliance()
  ├── generate_report()
  ├── send_notification()
  └── update_database()

AFTER: 4 focused micro-tools
  ├── tool_compliance_check  → validates RGPD/IA compliance
  ├── tool_audit_report      → generates structured reports
  ├── tool_notification      → sends alerts via configured channels
  └── tool_evidence_store    → persists findings with provenance
```

### Principles

1. **One tool, one job**: If you need "and" in the description, split it
2. **Composable over monolithic**: Tools call each other via well-defined interfaces
3. **Testable**: Each tool can be tested independently
4. **Replaceable**: Swap one tool without affecting others

**Full implementation guide:** `references/single_purpose_tool_design.md`

---

## Pattern 4: Action Verification (Post-Execution Hallucination Detection)

**Origin**: Designed for shared_ai_safety v2.1.0 (2026-07-10). Solves "action hallucination" — LLM claims to have executed an action ("rendez-vous confirmé", "email envoyé") that the system never actually performed.

**Why it matters**: Content risk classification (Pattern 3) validates INPUT. Action verification validates OUTPUT — specifically, it checks that claims of completed actions in LLM responses correspond to actions the application code actually executed. This is a distinct failure mode from prompt injection or data leakage.

### How It Works

```
LLM Response: "Votre rendez-vous est confirmé pour mardi 14h."
                    ↓
    ClaimParser extracts action claims (regex + negate filtering)
                    ↓
    ExecutionTracker checks: did the code actually call book_appointment?
                    ↓
    Verified (✅ trust_score stays 1.0) OR Hallucination (⚠️ trust_score drops)
```

### Key Design Decisions

1. **Code marks executions, never the LLM**: `verifier.mark_executed(user_id, "book_appointment")` is called by application code AFTER the booking is real. The LLM has no way to mark executions.
2. **Negate patterns filter false positives**: "Je ne peux pas réserver", "à confirmer", "souhaitez-vous" → NOT claims. A ±60 char window around each keyword match is checked against negate regexes.
3. **Trust Score (0.0–1.0)**: Exposed in API responses (header `X-Trust-Score`) for runtime monitoring and alerting.
4. **Severity levels per action**: CRITICAL for financial/legal commitments, HIGH for appointments/bookings, MEDIUM for lead creation, LOW for cosmetic claims.

### Domain Presets

- `register_medical_actions()` — book_appointment, cancel_appointment, call_emergency
- `register_debarras_actions()` — create_quote, schedule_visit, create_lead

**Full implementation guide:** `references/action-verifier-pattern.md`

---

## Pattern 3: Content Risk Classification (R1-R4)

**Origin**: Recovered from HELEN Workflow Manager bytecode (2026-07-10). Originally designed for Swiss law firms, adaptable to any FR-CH compliance context.

**Why it matters**: Command risk classification (Pattern 1) protects the system. Content risk classification protects the USER and the CLIENT — it prevents delivering non-compliant, harmful, or legally risky LLM output.

### Risk Levels

| Level | Classification | Action |
|-------|---------------|--------|
| R1_LOW | Risque Faible | ✅ Automatisation autorisée, pas de validation humaine |
| R2_MODERATE | Risque Modéré | ⚠️ Validation humaine requise avant livraison |
| R3_HIGH | Risque Élevé | 🔸 Double validation requise |
| R4_CRITICAL | Risque Critique | 🚫 Kill Switch — blocage + alerte + escalade |

### Design Principles

1. **Fail Safe**: On error or uncertainty, default to HIGH risk — never LOW. Better to over-validate.
2. **Deterministic**: Regex pattern matching, not ML. Auditable and predictable.
3. **Immutable audit trail**: `RiskAssessment` is frozen (Pydantic `frozen=True`) — tamper-proof.
4. **Entity detection**: Scan for named entities that elevate risk (mineur, santé, données financières, partie adverse).

### Integration

This pattern is the implementation layer for Le Gardien des Normes' compliance scoring. The Gardien skill provides the regulatory framework (5 audit domains, RGPD/AI Act articles, Kill Switch conditions); this pattern provides the runtime classification engine.

**Full specification + recovered bytecode details:** `references/helen-risk-matrix-recovered.md` (in `le-gardien-des-normes` skill)

### Guardrails Stack (from HELEN)

Content risk classification is one layer of a three-layer defense:

| Layer | Purpose | Implementation |
|-------|---------|---------------|
| **PromptSanitizer** | Detect injection attempts in user input | 25+ regex patterns (prompt injection, code injection, credential leak, encoding bypass) |
| **RiskClassifier** | Classify prompt risk level R1-R4 | Deterministic pattern matching + entity detection |
| **RateLimiter** | Prevent abuse | Per-user/IP limits by request type |
| **SecurityGuardrails** | Orchestrate all layers | Blocked lists + rate limit + sanitize → block if any layer fails |

## When to Use Which Pattern

- **Command Risk Classification**: When building agents that execute terminal commands or modify system state
- **Content Risk Classification (R1-R4)**: When building agents that process user prompts or generate LLM output
- **Action Verification**: When building agents that claim to have performed actions (bookings, emails, quotes) — catches post-execution hallucinations
- **Single-Purpose Tool Design**: When an agent has grown beyond 3-4 responsibilities
- **All four together**: For production Cortex Leman agents that execute commands, process LLM prompts, claim actions, and have multiple responsibilities

---

### Reusable Package: `~/shared_ai_safety/` (v2.1.0)

The full stack has been rebuilt as a standalone Python package with **34 passing tests** across 7 modules:

```
~/shared_ai_safety/
├── risk_matrix.py       → RiskLevel (R1-R4) + RiskAssessment (Pydantic V2 immutable)
├── risk_classifier.py   → Deterministic prompt analysis → R1-R4 assignment
├── guardrails.py        → PromptSanitizer + RateLimiter + SecurityGuardrails
├── structured_logger.py → JSON logging + SecurityLogger/BusinessLogger/PerformanceLogger + correlation IDs (RGPD Art. 30)
├── workflow_validator.py→ Validates AI-generated workflows: code exec, data exfiltration, hardcoded secrets, infinite loops
├── memory_service.py    → Dual memory STM/LTM with automatic context compression (AgentScope-style)
├── action_verifier.py   → Detects action hallucinations: LLM claims vs real executions (trust score)
├── __init__.py          → Public imports (v2.1.0)
└── test_safety.py       → 34 tests (10 guardrails + 4 logger + 6 validator + 5 memory + 9 action verifier)
```

**To integrate into any agent**: `sys.path.insert(0, os.path.expanduser("~"))` then `from shared_ai_safety import SecurityGuardrails, RiskClassifier, RiskLevel, setup_logging, SecurityLogger, WorkflowValidator, MemoryService`.

**Integration guides:**
- Guardrails deployment (réceptionniste-ia + darkom-debarras): `references/shared-ai-safety-integration.md`
- HELEN module recovery technique (.pyc → source adaptation): `references/helen-module-recovery.md`
