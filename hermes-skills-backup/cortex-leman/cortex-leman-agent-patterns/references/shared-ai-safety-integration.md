# shared_ai_safety Integration Guide (v2.0.0)

## Overview

How to integrate the `~/shared_ai_safety/` package into any Cortex Leman agent or prototype.
Modules: guardrails (R1-R4), structured logger, workflow validator, memory service.

## Package Modules (v2.0.0)

| Module | Purpose | Key exports |
|--------|---------|-------------|
| `risk_matrix.py` | R1-R4 definitions + RiskAssessment | RiskLevel, RiskAssessment |
| `risk_classifier.py` | Deterministic prompt analysis | RiskClassifier |
| `guardrails.py` | Sanitizer + RateLimiter + orchestration | SecurityGuardrails, PromptSanitizer |
| `structured_logger.py` | JSON logging + audit trail (RGPD Art. 30) | setup_logging, SecurityLogger, BusinessLogger |
| `workflow_validator.py` | Validates AI-generated workflows | WorkflowValidator, SecurityViolation |
| `memory_service.py` | Dual memory STM/LTM + compression | MemoryService, ConversationSession |

---

## Guardrails Integration (4 steps)

### Step 1: Import + domain profiles

```python
import os, sys
sys.path.insert(0, os.path.expanduser("~"))
from shared_ai_safety import SecurityGuardrails, RiskClassifier, RiskLevel

clf = RiskClassifier()
clf.add_domain_profile("R3", {"symptôme": "Description de symptômes médicaux"})
clf.add_domain_profile("R4", {"urgence vitale": "Urgence vitale potentielle"})

guardrails = SecurityGuardrails(risk_classifier=clf)
```

### Step 2: Validate before LLM call

```python
async def call_llm(user_message: str) -> tuple:
    validation = guardrails.validate_request(user_id, {
        "type": "llm_requests",
        "prompt": user_message,
    })

    if not validation["allowed"]:
        risk = validation["risk"]
        return fallback_response(), risk  # R4 blocked — NO LLM tokens consumed

    risk = validation.get("risk")
    # ... proceed to LLM call ...
    return reply, risk
```

### Step 3: Return risk metadata

```python
return {
    "reply": llm_response,
    "risk": {
        "level": risk.level.value if risk else None,
        "score": risk.score if risk else None,
    } if risk else None,
}
```

### Step 4: Expose security report endpoint

```python
@app.get("/security/report")
async def security_report():
    return guardrails.get_security_report(hours=24)
```

---

## Structured Logger Integration

Replace `print()` and basic `logging.getLogger()` with structured JSON logging:

```python
from shared_ai_safety import setup_logging, SecurityLogger, BusinessLogger, set_request_context, clear_request_context

# One-time setup
logger = setup_logging(app_name="receptionniste-ia", log_dir="/var/log/receptionniste")
sec_logger = SecurityLogger(logger)
biz_logger = BusinessLogger(logger)

# Per-request correlation
set_request_context(request_id=request_id, user_id=user_id)
try:
    # ... handle request ...
    biz_logger.log_user_action("chat", user_id)
    sec_logger.log_guardrail("R4_CRITICAL", "BLOCKED", user_id, ["injection"])
finally:
    clear_request_context()
```

**Each log line is valid JSON** with timestamp, level, correlation IDs, and structured extras. Compliant with RGPD Art. 30 (traçabilité) and AI Act auditability.

---

## Workflow Validator Integration

For agents that generate workflows (n8n, automation configs) via LLM:

```python
from shared_ai_safety import WorkflowValidator

validator = WorkflowValidator(allowed_domains=["api.openai.com", "api.z.ai", "localhost"])
is_safe, violations = validator.validate_and_block(workflow_dict)

if not is_safe:
    for v in violations:
        if v.is_critical:
            # Block deployment, alert human
            sec_logger.log_security_event(f"Workflow blocked: {v.rule_id}", "critical")
    return {"error": "Workflow rejected", "violations": [str(v) for v in violations]}
```

**Detection rules:**
- `NO_ARBITRARY_CODE` — Function nodes (n8n) executing raw JS
- `NO_SHELL_EXEC` — Shell command execution nodes
- `UNKNOWN_DESTINATION` — HTTP to non-whitelisted domains (data exfiltration risk)
- `HARDCODED_SECRET` — API keys, passwords, bearer tokens in workflow parameters
- `INFINITE_LOOP` — Cycle detection in node connections

---

## Memory Service Integration

For agents with multi-turn conversations that need context management:

```python
from shared_ai_safety import MemoryService

# compress_fn is any callable: str → str (typically your LLM generate function)
memory = MemoryService(
    compress_fn=lambda prompt: llm.generate(prompt),
    max_messages=6,            # keep last 6 messages uncompressed
    compression_threshold=2000, # trigger compression at ~2000 tokens
)

session = memory.get_or_create_session(user_id)
memory.add_to_session(session, "user", user_message)
memory.add_to_session(session, "assistant", reply)

# Build LLM context: summary + recent messages + (optional) LTM retrieval
context = memory.get_context_for_llm(session, query=user_message)
```

**Compression behavior:** When token_count exceeds threshold, older messages are summarized via `compress_fn`. Summary is prepended to context as a system message.

---

## Adding to New Agents — Checklist

- [ ] `sys.path.insert(0, os.path.expanduser("~"))` before import
- [ ] Define domain profiles with `add_domain_profile()` for agent-specific R3/R4 patterns
- [ ] Call `validate_request()` as first line of `call_llm()`
- [ ] Return `(reply, risk)` tuple from `call_llm()`
- [ ] Update all endpoints calling `call_llm()` to unpack the tuple
- [ ] Add `/security/report` endpoint
- [ ] Replace `print()` with `setup_logging()` + appropriate logger
- [ ] Write a fallback response for R4 blocks (domain-specific)
- [ ] Log all R2/R3 flags for audit trail

---

## Deployed Integrations

| Agent | Port | Guardrails | Logger | Validator | Memory | Status |
|-------|------|-----------|--------|-----------|--------|--------|
| **réceptionniste-ia** | 8000 | ✅ R1-R4 (médical) | To branch | — | To branch | ✅ Guardrails deployed |
| **darkom-debarras** | 8002 | ✅ R1-R4 (débarras) | To branch | — | To branch | ✅ Guardrails deployed |

### réceptionniste-ia Domain Patterns

| Level | Patterns |
|-------|----------|
| R3 | symptôme, douleur, ordonnance, traitement, arrêt maladie |
| R4 | urgence vitale, overdose, pensées suicidaires, saignement |

### darkom-debarras Domain Patterns

| Level | Patterns |
|-------|----------|
| R2 | devis, prix, coordonnées, téléphone, rappel |
| R3 | estimation, succession, expulsion, huissier, diogène, insalubre |
| R4 | amiant, asbeste, animaux morts, cadavre, décès suspect, données bancaires |

## Candidate Integrations

| Agent | R2 patterns | R3 patterns | R4 patterns | Status |
|-------|------------|------------|------------|--------|
| **Menuo** | données client, commande, paiement | — | — | Pending |
| **SocialPulse** | lead qualification (RGPD Art. 30) | — | — | Pending |

## R4 Fallback Response Patterns by Domain

| Domain | R4 trigger | Fallback response | Pattern |
|--------|-----------|-------------------|---------|
| Medical | Urgence vitale | "Appelez le 144 (CH) / 15 (FR) immédiatement" | Emergency redirect |
| Débarras | Amiante, matière dangereuse | "Je transmets à {HUMAN} pour intervention spécialisée" | Escalate to specialist |
| Any | Données bancaires | "Je ne peux pas traiter cela par ce canal" | Refuse channel |
| Any | Prompt injection | "Je n'ai pas compris, reformulez" | Generic deflection |

---

## Pydantic V2 Pitfalls (encountered during rebuild)

1. **Immutable models**: Use `model_config = {"frozen": True}` (NOT `class Config: frozen = True` which is deprecated V1 syntax)
2. **Property delegation**: If you expose `RiskLevel.is_blocking` via `RiskAssessment`, add explicit `@property` methods — Pydantic V2 doesn't auto-delegate enum properties
3. **Module naming**: Directory names with hyphens (`shared-ai-safety`) are NOT importable as Python modules. Use underscores (`shared_ai_safety`)
