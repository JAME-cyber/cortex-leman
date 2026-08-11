# CLAUDE.md — Cortex Leman Compliance Agent

## Compliance Audit Trigger

When the user asks to "audit rgpd", "check compliance", "rgpd-ia", or "conformité ia":

### Step 1: Load Context
Read this file for the full RGPD-IA compliance framework for FR-CH SMEs.

### Step 2: Scan Codebase
- Identify personal data collection points (forms, APIs, cookies, logs)
- Map data flows (where data goes, especially LLM API calls)
- Check for hardcoded PII/secrets
- Verify encryption (at rest + in transit)
- Check consent mechanisms
- Verify deletion/retention implementations

### Step 3: Score 5 Domains
| Domain | Articles | Key Checks |
|---|---|---|
| Data Collection | Art. 5,6,13 | Legal basis, minimization, no hardcoded PII |
| Cross-Border | Art. 44-49 | API endpoint locations, SCCs, data residency |
| Consent | Art. 7,52 | Opt-in, withdrawal, AI transparency |
| Security | Art. 25,32 | Encryption, RBAC, no eval/exec on AI output |
| Data Rights | Art. 17,19 | Deletion endpoint, retention, propagation |

### Step 4: 4 AI Dimensions (Cortex Leman Differentiator)
A. Autonomy Level: Low(+0) / Medium(+2) / High(+5) risk points
B. Architecture: RAG > Fine-tuning (deletable, debuggable, auditable)
C. Traceability: All prompts/responses logged → Art. 30 compliance
D. Accountability: Transparency → Terms+Oversight → Full DPIA

### Step 5: Report
- Overall score (0-1), Kill Switch status
- Domain scores with 🟢🟠🔴
- Violations prioritized (CRITICAL → LOW)
- 90-Day Conformity Plan

### Kill Switch: AUTO-ACTIVATE on
- Sensitive data without legal basis
- Illegal transfer to non-adequate country
- No consent on sensitive data
- Unsecured health/financial data
- CNIL sanction risk >30K€
