# Cortex Leman v5 — Audit Baseline (2026-06-04)

First live audit using cortex-leman-compliance-agent on the actual codebase.

## Overall Score: 0.72/1.0 🟠

## Domain Scores

- **D1 Data Collection:** 0.75 🟠 — `user_consent` in rules engine ✅, vertical routing ✅, no auto privacy notice
- **D2 Cross-Border:** 0.65 🟠 — Model-agnostic via LiteLLM ✅, Mode Haute Protection (Ollama local) ✅, cloud endpoints not explicitly documented
- **D3 Consent:** 0.70 🟠 — Rules engine blocks without consent ✅, 2FA OFF by default 🔴
- **D4 Security:** 0.78 🟠 — API keys via env ✅, RBAC ✅, append-only journal ✅, hardcoded password in tests 🔴
- **D5 Data Rights:** 0.70 🟠 — Delete permission in RBAC ✅, no explicit deletion endpoint with sub-processor propagation

## AI Dimensions

- **A. Autonomy:** Medium (+2 risk) — Agent acts, human reviews. Rules engine + guardrails. Not yet proactive.
- **B. Architecture:** RAG ✅ — Knowledge vault + vertical registry, no fine-tuning. Matches Cortex Leman recommendation.
- **C. Traceability:** 0.80 🟢 — Append-only journal, trace_id in eval pipeline, WORM logging.
- **D. Accountability:** Level 2-3 — Guardrails per vertical ✅, consent checks ✅, Art. 52 AI transparency label missing in UI.

## Critical/High Violations

1. **2FA disabled by default** (Art. 32) — `"two_factor": False` in onboarding. Especially critical for santé/banque verticals.
2. **Hardcoded password in tests** (Art. 32) — `"admin_password": "S3cur3P@ss!"` in test_onboarding.py.

## Medium Violations

3. Cross-border data flow not explicitly documented (Art. 44-49)
4. No explicit right-to-erasure endpoint with sub-processor propagation (Art. 17)

## Low Violations

5. AI transparency label missing (Art. 52 AI Act)

## Key Codebase Findings

- LLM provider: `core/integrations/llm/provider.py` — LiteLLM-based, 18+ providers, vertical routing
- Mode Haute Protection: Ollama local, zero external calls (good for santé/banque)
- Rules engine: `core/arbitration/arbitration_service.py` — JsonLogic-based guardrails
- Journal: `core/journal/append_only_journal.py` — WORM audit logging
- Onboarding: `two_factor: False` default is a compliance gap for high-risk verticals

## Next Audit

Re-run after Phase 1 fixes (2FA default + test password removal). Expected score: ~0.82 🟢
