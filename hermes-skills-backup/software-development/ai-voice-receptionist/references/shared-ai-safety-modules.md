# shared_ai_safety — Complete Module Reference

**Location:** `~/shared_ai_safety/`
**Version:** v2.1.0 (34 tests, 7 modules)
**Origin:** Extracted and adapted from HELEN Workflow Manager (Dec 2025)

## Module Overview

```
~/shared_ai_safety/
├── __init__.py            # Public API — exports all 7 modules
├── risk_matrix.py         # R1-R4 definitions + RiskAssessment (Pydantic V2, immutable)
├── risk_classifier.py     # Deterministic prompt analysis → risk assignment
├── guardrails.py          # PromptSanitizer + RateLimiter + orchestration
├── structured_logger.py   # JSON logging + correlation IDs + audit trail (RGPD Art. 30)
├── workflow_validator.py  # Validates AI-generated workflows (exfil, code exec, secrets, loops)
├── memory_service.py      # Dual memory STM/LTM + compression + retrieval
├── action_verifier.py     # Detects execution hallucinations (LLM claims vs real actions)
├── test_safety.py         # 34 tests covering all modules
└── README.md
```

## Risk Levels (R1-R4)

| Level | Name | Score | Behavior |
|-------|------|-------|----------|
| R1_LOW | Low | 0.0-0.25 | Allow, log |
| R2_MODERATE | Moderate | 0.25-0.50 | Allow, flag for review |
| R3_HIGH | High | 0.50-0.75 | Allow, require human validation |
| R4_CRITICAL | Critical | 0.75-1.0 | **BLOCK** — no LLM call |

## Integration Pattern: Pre-LLM + Post-LLM Pipeline

```
User Input
    ↓
[1] GUARDRAILS (pre-LLM)
    guardrails.validate_request(user_id, {type, prompt})
    → R4? BLOCK (no tokens consumed)
    → R1-R3? Continue with risk flag
    ↓
[2] LLM CALL
    Generate response with risk context
    ↓
[3] ACTION VERIFIER (post-LLM)
    action_verifier.verify(user_id, llm_reply)
    → Compares LLM claims against mark_executed() records
    → trust_score: 0.0-1.0
    → has_hallucinations: bool
    → suggested_correction: str
    ↓
API Response: {reply, risk: {...}, verification: {...}}
Headers: X-Risk-Level, X-Risk-Score, X-Trust-Score, X-Hallucination
```

## Module Details

### 1. risk_matrix.py + risk_classifier.py

Pydantic V2 models. RiskAssessment is immutable (frozen=True).

Key APIs:
- `RiskClassifier()` — base classifier with R2-R4 keyword dictionaries
- `classifier.add_domain_profile(level, {keyword: description})` — inject domain-specific patterns
- `classifier.classify(prompt, request_type)` → RiskAssessment

Properties on RiskAssessment:
- `requires_human_validation` — True if R3+
- `is_blocking` — True if R4

### 2. guardrails.py

Orchestrates sanitizer + rate limiter + classifier.

Key APIs:
- `SecurityGuardrails(risk_classifier=clf)` — main entry point
- `guardrails.validate_request(user_id, request)` → {allowed: bool, risk: RiskAssessment}
- `guardrails.get_security_report(hours=24)` — audit summary

### 3. structured_logger.py

JSON logging with SecurityLogger, BusinessLogger, PerformanceLogger.

Key APIs:
- `setup_logging(level, log_dir)` — configure handlers
- `set_request_context(request_id, user_id)` — correlation tracking
- `SecurityLogger.log_guardrail(level, user, action, details)` — audit trail

**Status:** Available but NOT yet integrated into prototypes (they use basic logging.getLogger).

### 4. workflow_validator.py

Validates AI-generated workflows before deployment.

Key APIs:
- `WorkflowValidator()` — create validator
- `validator.validate(workflow_dict)` → list[SecurityViolation]
- Detects: arbitrary code execution, data exfiltration, secret leakage, infinite loops

**Status:** Available for HELEN-style projects. Not yet deployed.

### 5. memory_service.py

Dual memory: short-term (conversation window) + long-term (compressed experiences).

Key APIs:
- `MemoryService(repository)` — create service
- `service.get_or_create_session(user_id)` → ConversationSession
- `service.compress_if_needed(session)` — auto-compress when token limit hit
- `service.save_experience(user_id, content, tags)` — persist to LTM

**Status:** Available. Prototypes currently use flat conversation lists that grow unbounded.

### 6. action_verifier.py

Detects when LLMs claim actions that weren't actually executed.

Key APIs:
- `ActionVerifier()` — create verifier
- `v.register_action(name, keywords, severity, negate_patterns)` — declare trackable action
- `v.mark_executed(user_id, action_name, details)` — record REAL execution
- `v.verify(user_id, llm_text)` → VerificationResult

VerificationResult:
- `has_hallucinations: bool` — True if any claim is unverified
- `trust_score: float` — 0.0 (all lies) to 1.0 (all true)
- `verified_claims: list[Claim]` — claims backed by real execution
- `unverified_claims: list[Claim]` — claims with no execution record
- `suggested_correction: str` — text to fix or re-prompt the LLM
- `to_dict()` — JSON-serializable for API responses

Presets:
- `register_medical_actions(v)` — book_appointment, cancel_appointment, call_emergency
- `register_debarras_actions(v)` — create_quote, schedule_visit, create_lead

### 7. test_safety.py

34 tests covering all modules. Run with:
```bash
.venv/bin/python shared_ai_safety/test_safety.py
```

## Deployment Status

| Module | receptionniste-ia | darkom-debarras | Other projects |
|--------|-------------------|-----------------|----------------|
| guardrails (pre-LLM) | ✅ Active | ✅ Active | Available |
| action_verifier (post-LLM) | ✅ Active | ✅ Active | Available |
| structured_logger | ⬜ Not wired | ⬜ Not wired | Available |
| workflow_validator | — | — | Available |
| memory_service | ⬜ Not wired | ⬜ Not wired | Available |

## How to Integrate into a New Prototype

1. `sys.path.insert(0, os.path.expanduser("~"))`
2. Import: `from shared_ai_safety import SecurityGuardrails, RiskClassifier, ActionVerifier, register_*_actions`
3. Set up domain profiles (R2/R3/R4 keywords specific to the business)
4. In `call_llm()`: validate BEFORE LLM, verify AFTER LLM
5. In endpoints: unpack 3-tuple `(reply, risk, verification)`, expose in JSON + headers
6. Call `mark_executed()` wherever the system performs a real action
7. Test with scenarios: normal (R1), blocked (R4), hallucination (claim without execution)
