# Action Verification Pattern — Post-Execution Hallucination Detection

**Module**: `shared_ai_safety/action_verifier.py`
**Version**: 1.0 (2026-07-10)
**Tests**: 9 (34 total in shared_ai_safety)

---

## Problem

LLMs hallucinate completed actions. They say "your appointment is confirmed" or "the email has been sent" when no such action was executed by the system. This is distinct from:

- **Prompt injection** (input-side attack) — handled by guardrails
- **Data leakage** (output contains sensitive data) — handled by workflow_validator
- **Silent drift** (model behavior changes over time) — handled by monitoring

Action hallucination is the LLM **fabricating a success claim** for a side-effect action it cannot actually perform.

---

## Architecture

```
ActionVerifier
├── ActionRegistry      → declares actions the system CAN perform
│   └── ActionDef       → name, keywords[], severity, negate_patterns[]
├── ExecutionTracker    → records what the code ACTUALLY executed
│   └── Execution       → action_name, user_id, timestamp, details, success
├── ClaimParser         → extracts action claims from LLM text
│   └── Claim           → action_name, matched_keyword, snippet, status, severity
└── verify()            → orchestrates: parse → compare → result
    └── VerificationResult → has_hallucinations, trust_score, unverified_claims, suggested_correction
```

---

## Integration Pattern (4 lines)

```python
from shared_ai_safety import ActionVerifier, register_medical_actions

verifier = ActionVerifier()
register_medical_actions(verifier)

# --- In application code, AFTER actually performing the action ---
if appointment_booked:
    verifier.mark_executed(user_id, "book_appointment")

# --- After LLM responds, BEFORE delivering to user ---
result = verifier.verify(user_id, llm_response)
if result.has_hallucinations:
    # Options: log, alert, strip the claim, force LLM re-generation
    logger.warning(f"Action hallucination: {result.to_dict()}")
    # The suggested_correction can be fed back to the LLM
```

---

## Negate Pattern Filtering

The ClaimParser filters false positives using a ±60 char window around each keyword match:

**Default negate patterns** (applied to all actions):
- `je ne peux pas`, `impossible de`, `n'a pas pu`
- `cannot`, `can't`, `unable to`
- `pas encore`, `à confirmer`
- `souhaitez-vous`, `voulez-vous`
- `je vais`, `on va`, `nous allons`

**Example**: "Je ne peux pas confirmer que l'email envoyé sera livré" → NOT a claim (negated).

**Action-specific negate patterns** can be added via `negate_patterns` parameter.

---

## Severity Levels

| Severity | Use Case | Example |
|----------|----------|---------|
| CRITICAL | Financial/legal commitments | "Contrat signé", "paiement effectué" |
| HIGH | Bookings, appointments, notifications | "RDV confirmé", "email envoyé" |
| MEDIUM | Lead creation, status changes | "Demande enregistrée" |
| LOW | Cosmetic/preference claims | "J'ai noté votre préférence" |

---

## Domain Presets

### Medical (register_medical_actions)

| Action | Keywords (subset) | Severity |
|--------|-------------------|----------|
| book_appointment | "rendez-vous confirmé", "créneau réservé", "rdv pris" | HIGH |
| cancel_appointment | "rendez-vous annulé", "annulation confirmée" | HIGH |
| call_emergency | "j'ai appelé le 15", "urgence contactée" | CRITICAL |

### Debarras (register_debarras_actions)

| Action | Keywords (subset) | Severity |
|--------|-------------------|----------|
| create_quote | "devis envoyé", "devis préparé" | HIGH |
| schedule_visit | "visite planifiée", "intervention programmée" | MEDIUM |
| create_lead | "demande enregistrée", "votre dossier est créé" | MEDIUM |

---

## Trust Score

- `1.0` = all claims verified (or no claims made)
- `0.5` = half of claims are hallucinations
- `0.0` = every claimed action is fabricated

Expose in API responses via header `X-Trust-Score` for monitoring/alerting.

---

## Testing

```
test_action_verified       — action claimed + executed → VERIFIED
test_action_hallucination  — action claimed but NOT executed → hallucination
test_action_negate         — "je ne peux pas" → NOT a claim
test_action_multiple       — mix of verified + hallucinated → partial trust
test_action_no_claim       — neutral response → no hallucination
test_action_correction     — suggested_correction generated
test_action_trust_score    — 2/3 verified → trust_score ≈ 0.667
test_medical_preset        — register_medical_actions works
test_debarras_preset       — register_debarras_actions works
```

---

## Pitfalls

1. **Never let the LLM call `mark_executed()`** — only application code marks real executions. The LLM produces text, not actions.
2. **Keyword overlap** — if "mail envoyé" is a substring of "email envoyé", both keywords match the same text. The parser uses a per-action `action_claimed` flag to ensure one claim per action maximum.
3. **Negate window too narrow** — if the negate phrase is >60 chars from the keyword, it won't be detected. For long sentences, consider widening the window.
4. **Missing actions** — if the system performs an action that isn't registered, the verifier can't detect hallucinations for it. Register all critical actions upfront.
5. **User-scoped tracking** — executions are tracked per user_id. If the same user has multiple concurrent sessions, consider adding a session_id scoping.
