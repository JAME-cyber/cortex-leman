---
name: cortex-leman-compliance-agent
category: cortex-leman
version: 1.0.0
description: |
  Agent-consumable RGPD-IA compliance skill for FR-CH SMEs.
  Works with any coding agent (Codex, Cursor, Claude Code, Hermes).
  Provides regulatory context + audit checklists + compliance validation prompts.
  Not a website. Not a SaaS. Context that agents consume.

triggers:
  - "audit rgpd"
  - "compliance check"
  - "rgpd-ia"
  - "conformité ia"
  - "ai act compliance"
  - "check rgpd"
  - "audit ia"
  - "gdpr check"
  - "privacy audit"

compatibility:
  hermes: true
  codex: true
  cursor: true
  claude_code: true
  any_agent: true
---

# Cortex Leman — Compliance Agent Skill

## WHAT THIS IS

A **context layer** that makes any coding agent into an RGPD-IA compliance auditor for FR-CH SMEs.

You don't go to a website. You don't upload documents. The agent already has your code, your config, your architecture — this skill gives it the **regulatory context** to audit compliance.

**Philosophy:** Less UI, more context. The agent is the interface.

## QUICK START (Any Agent)

### Codex
```
/install-skill cortex-leman-compliance-agent
Then: "Audit my codebase for RGPD-IA compliance"
```

### Cursor
Add to `.cursorrules`:
```
When I say "audit rgpd", load the Cortex Leman compliance context and run a full RGPD-IA audit on the current project.
```

### Hermes
Already available as skill. Trigger: "audit rgpd" or "compliance check".

### Claude Code
Add to `CLAUDE.md`:
```
Use cortex-leman-compliance-agent skill for RGPD-IA compliance audits on FR-CH projects.
```

---

## COMPLIANCE CONTEXT (Agent Knowledge)

This is the core knowledge any agent needs to perform RGPD-IA audits in FR-CH.

### Jurisdiction Map

| Jurisdiction | Core Law | Data Authority | Key Difference |
|---|---|---|---|
| EU | RGPD (2016/679) + AI Act (2024/1689) | CNIL / EDPB | AI Act mandatory risk classification |
| CH | LPD (nLDP from Sep 2023) | PFPDT | No AI Act (but voluntary alignment), adequacy with EU |
| FR-CH Cross-border | Both apply simultaneously | Both authorities | Double compliance, transfer documentation required |

### AI Act Risk Classification (Mandatory for EU)

| Risk Level | Examples | Obligations | Cortex Leman Default |
|---|---|---|---|
| Minimal | Spam filters, AI gaming | None | Document only |
| Limited | Chatbots, content generators | Art. 52: Transparency (user must know it's AI) | Most SME agents start here |
| High | HR screening, credit scoring, medical AI | Full DPIA, conformity assessment, human oversight, CE marking | Requires Phase 3 audit |
| Unacceptable | Social scoring, manipulative AI | Banned | Kill Switch immediately |

### FR-CH Specific Constraints

**Swiss data residency (LPD Art. 16):**
- Swiss data can go to EU (adequacy decision exists)
- Swiss data going outside EU/CH = requires SCCs or specific justification
- Swiss clients: document data flows CH→EU→US carefully

**French sectoral rules:**
- Medical: HLS + LPM (données de santé)
- Legal: Secret professionnel (Art. 321 CP)
- Banking: Secret bancaire (Art. 47 LB) + FINMA
- HR: Art. 22 RGPD (profiling) + biais detection mandatory

---

## AUDIT CHECKLIST (Agent Executable)

When triggered, the agent MUST run through ALL 5 domains systematically.

### Domain 1: Data Collection (Art. 5, 6, 13 RGPD / Art. 10, 52 AI Act)

**Agent checks in codebase:**
- [ ] Personal data collection points identified (forms, APIs, cookies, logs)
- [ ] Legal basis documented for each collection (consent/contract/legitimate interest/legal obligation)
- [ ] Privacy notice accessible at each collection point
- [ ] Data minimization: only fields actually needed are collected
- [ ] No hardcoded PII in source code or config files

**Red flags in code:**
```python
# ❌ BAD: Collecting more than needed
user_data = {"name": ..., "email": ..., "address": ..., "phone": ..., "birthday": ..., "ssn": ...}

# ✅ GOOD: Minimal collection with documented basis
# Legal basis: Art. 6(1)(b) - contract performance
user_data = {"name": ..., "email": ...}  # Only what's needed for service
```

- [ ] No PII in URLs, logs, or error messages
- [ ] Consent mechanism present if Art. 6(1)(a) is the basis
- [ ] Separate consent for each processing purpose

### Domain 2: Cross-Border Transfers (Art. 44-49 RGPD / Art. 27-28 AI Act)

**Agent checks in codebase:**
- [ ] API endpoints identified: where does data go?
- [ ] LLM provider endpoints documented (OpenAI = US, Anthropic = US, etc.)
- [ ] Cloud hosting location identified (AWS region, GCP region, etc.)
- [ ] Standard Contractual Clauses (SCCs) documented for non-adequate transfers
- [ ] Data residency config matches legal requirements

**Red flags in code:**
```python
# ❌ BAD: No documentation of where data goes
response = openai.ChatCompletion.create(...)  # Data goes to US — is this documented?

# ✅ GOOD: Documented transfer with legal basis
# Data transfer: EU→US via OpenAI API
# Legal basis: SCCs + Art. 49(1)(a) consent (documented in privacy policy)
# Adequacy: EU-US Data Privacy Framework (if applicable)
response = openai.ChatCompletion.create(...)
```

- [ ] Swiss clients: LPD adequacy documented for CH→EU transfers
- [ ] No direct transfers to non-adequate countries without SCCs

### Domain 3: Consent & Transparency (Art. 7, 52 RGPD/AI Act)

**Agent checks in codebase:**
- [ ] Consent is opt-in, not pre-checked
- [ ] Withdrawal mechanism exists and is as easy as giving consent
- [ ] AI transparency: users know when they interact with AI (Art. 52 AI Act)
- [ ] No dark patterns in consent flows
- [ ] Separate consent per purpose

**Red flags in code:**
```html
<!-- ❌ BAD: Pre-checked consent -->
<input type="checkbox" checked> I agree to the privacy policy

<!-- ✅ GOOD: Explicit opt-in -->
<input type="checkbox" id="consent"> <label for="consent">I agree to the privacy policy</label>
```

- [ ] AI-generated content clearly labeled
- [ ] Human oversight before AI output reaches end users (for high-risk)

### Domain 4: Data Security (Art. 25, 32 RGPD / Art. 9, 15 AI Act)

**Agent checks in codebase:**
- [ ] Encryption at rest (AES-256 or equivalent)
- [ ] Encryption in transit (TLS 1.2+, preferably 1.3)
- [ ] No secrets/API keys in source code
- [ ] RBAC or equivalent access control implemented
- [ ] Input validation on all user-facing endpoints
- [ ] Output validation on AI-generated content (no eval/exec)
- [ ] Rate limiting on API endpoints

**Red flags in code:**
```python
# ❌ BAD: Secrets in code
OPENAI_API_KEY = "sk-abc123..."

# ❌ BAD: No input validation
@app.post("/user")
def create_user(data: dict):  # No validation, no schema
    db.insert(data)

# ❌ BAD: Executing AI output
exec(ai_generated_code)  # LLM02: Never trust AI output as executable

# ✅ GOOD: Env-based secrets, validation, schema
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

class UserCreate(BaseModel):
    name: str = Field(max_length=100)
    email: EmailStr

@app.post("/user")
def create_user(data: UserCreate):
    sanitized = data.model_dump()
    db.insert(sanitized)
```

- [ ] Session timeouts configured (default: 30min for sensitive data)
- [ ] PII not logged or masked in logs
- [ ] Backup and recovery procedures documented

### Domain 5: Data Subject Rights (Art. 17, 19 RGPD / Art. 12, 20 AI Act)

**Agent checks in codebase:**
- [ ] Data deletion endpoint exists (right to erasure)
- [ ] Deletion propagates to all sub-processors
- [ ] Data portability endpoint exists (Art. 20)
- [ ] Retention periods configured and enforced
- [ ] Deletion within 30 days guaranteed

**Red flags in code:**
```python
# ❌ BAD: No deletion mechanism
# Users can be created but never deleted

# ✅ GOOD: Right to erasure implementation
@app.delete("/user/{user_id}")
def delete_user(user_id: str):
    user = db.get(user_id)
    # Notify sub-processors
    for processor in sub_processors:
        processor.notify_deletion(user_id)
    # Anonymize or delete
    db.delete(user_id)
    audit_log("deletion", user_id, reason="art_17_request")
```

---

## 4 AI-SPECIFIC DIMENSIONS (Cortex Leman Differentiator)

These 4 dimensions are what separate a Cortex Leman audit from a standard RGPD audit. No classical auditor covers these.

### A. AI Autonomy Level

**Assess in codebase:**
- [ ] Level identified: Low / Medium / High
- Low = human approves every AI action
- Medium = AI acts, human reviews outputs
- High = AI acts autonomously, alerts on exceptions only

**Scoring impact:**
- Low = +0 risk points
- Medium = +2 risk points (traceability required)
- High = +5 risk points (DPIA mandatory)

**Default recommendation:** Start low. Earn trust. Expand gradually.

### B. Architecture: RAG > Fine-Tuning

**Position:** For FR-CH SMEs, RAG is systematically recommended over fine-tuning.

**Why (RGPD):**
- RAG: data in controllable index, auditable, deletable (Art. 17)
- Fine-tuning: data baked into model, opaque, impossible to delete individually
- RAG: data transfers documentable (Art. 44-49)
- Fine-tuning: training data hard to trace

**Why (technical - Stanford CS230):**
- Fine-tuning = overfitting risk, model goes stale fast
- Case Slack: fine-tuning regressed general capabilities
- RAG = debuggable, easy to update, less RGPD risk

**Fine-tuning justified ONLY if:**
- Ultra-specific output format that prompts can't produce reliably
- Latency/cost requirements need a small model
- 1000+ labeled examples of high quality
- Task stable across model upgrades

### C. AI Traceability

**"LLM Traces Are Non-Negotiable"** — Stanford CS230

**Without traces = impossible to justify an AI decision before the CNIL.**

**Agent checks:**
- [ ] Every LLM prompt logged
- [ ] Every LLM response logged
- [ ] Every tool call logged
- [ ] Timing per pipeline component
- [ ] Component evaluations (objective: assertions, subjective: LLM judges)
- [ ] End-to-end evaluations before deployment
- [ ] Log retention policy defined

**Recommended tools:** LangSmith, Braintrust, Helicone, Arize

**⚠️ Reasoning Opacity Risk (frontier models):** Models with extended chain-of-thought (Fable 5, GPT-o series, GLM with thinking) can develop dense internal shorthand that becomes incomprehensible to humans. Anthropic's own system cards document this as a safety concern. If the client uses models with extended reasoning:
- Request sample CoT outputs from production prompts and check human-readability
- Verify logging captures full reasoning traces (many APIs strip thinking tokens by default)
- Flag opacity risk in audit report and recommend periodic human review of CoT samples
- See `references/ai-reasoning-opacity-fable5.md` for the Fable 5 leak case study and business argument for clients

### D. AI Accountability & Guardrails

**Principle:** The AI has no legal personality. The employee/company is responsible for AI outputs, not the model provider.

**3 mandatory guardrail levels:**

| Level | Guardrail | When Required | Articles |
|---|---|---|---|
| 1 — Transparency | Indicate user interacts with AI | Always (any AI with user interaction) | Art. 52 AI Act |
| 2 — Terms + Human Oversight | CG mentioning hallucinations + human check before client delivery | Any AI generating content for third parties | Art. 7 RGPD, Art. 14 AI Act |
| 3 — Full Documentation + DPIA | Technical doc, DPIA, CE marking, complete traces | High-risk domains (legal, HR, health, finance) | Art. 35 RGPD, Art. 6-9 AI Act |

**AI Act role identification for clients:**
- Provider: Creates AI from scratch → full technical doc + CE
- Deployer: Uses AI on EU market → transparency + human oversight + DPIA if high-risk
- Importer: Brings foreign AI to EU → verify provider compliance
- Distributor: Makes AI available without creating it → info + cooperation

---

## COMPLIANCE SCORING

```
Score = 0      : Non-conforme (violation flagrante, preuve irrefutable)
Score = 0.2-0.4: Partiellement conforme (violations mineures)
Score = 0.5-0.7: Conformite intermediaire (gaps a combler)
Score = 0.8-0.9: Largement conforme (ameliorations mineures)
Score = 1      : Pleinement conforme (toutes les preuves irrefutables)
```

**Color code:**
- 🟢 Score ≥ 0.8
- 🟠 0.5 ≤ Score < 0.8
- 🔴 Score < 0.5

**Kill Switch conditions (AUTO-ACTIVATE):**
1. Critical RGPD violation on sensitive data (health, financial, legal)
2. Illegal transfer to non-adequate country
3. Total absence of consent on sensitive data processing
4. Unsecured storage of health/financial data
5. Any violation risking CNIL sanction > 30K€

---

## AUDIT OUTPUT FORMAT

When the agent completes an audit, it MUST produce:

### 1. Executive Summary
```
Cortex Leman — RGPD-IA Compliance Audit
Date: YYYY-MM-DD | Client: [name] | Sector: [vertical]
Overall Score: X.XX / 1.0
Kill Switch Status: [ACTIVE/STANDBY/INACTIVE]
```

### 2. Domain Scores
```
Domain 1 — Data Collection:      X.XX 🟢/🟠/🔴
Domain 2 — Cross-Border:         X.XX 🟢/🟠/🔴
Domain 3 — Consent:              X.XX 🟢/🟠/🔴
Domain 4 — Security:             X.XX 🟢/🟠/🔴
Domain 5 — Data Subject Rights:  X.XX 🟢/🟠/🔴
```

### 3. AI Dimension Scores
```
A. Autonomy Level:    [Low/Medium/High] — +N risk points
B. Architecture:      [RAG/Fine-tune/Hybrid] — [justification]
C. Traceability:      X.XX — [tool recommendation if <0.8]
D. Accountability:    Level [1/2/3] guardrails — [gaps]
```

### 4. Violations (prioritized)
```
CRITICAL: [description] — Art. XX RGPD / AI Act — Action: [immediate step]
HIGH:     [description] — Art. XX RGPD / AI Act — Deadline: 7-14 days
MEDIUM:   [description] — Art. XX RGPD / AI Act — Deadline: 30 days
LOW:      [description] — Best practice — Deadline: 14 days
```

### 5. 90-Day Conformity Plan
```
Phase 1 (Days 1-30):   Critical violations — [actions]
Phase 2 (Days 31-60): Major gaps — [actions]
Phase 3 (Days 61-90):  Improvements — [actions]
```

---

## VERTICAL QUICK-CONFIGS

Pre-built configurations for common FR-CH verticals. Agent applies these when client sector is identified.

### Cabinet Comptable
- Risk: Limited | Data: Financial | Residency: CH/EU
- Guardrails: No definitive fiscal advice, anonymize logs, session_timeout 30min
- Key check: Fiscal data cross-border documentation

### Cabinet d'Avocats
- Risk: HIGH | Data: Legal (secret professionnel Art. 321 CP) | Residency: CH mandatory
- Guardrails: NEVER cross-dossier access, AES-256, PGP emails, state_verification required
- Key check: Inter-dossier isolation + data residency CH

### Clinique / Santé
- Risk: HIGH | Data: Health (Art. 9 RGPD + LPM) | Residency: CH mandatory
- Guardrails: BLOCK medical dossier access, no diagnostics, mandatory PII anonymization
- Key check: DPIA + health data encryption + no diagnostic capability

### Banque / Finance
- Risk: HIGH | Data: Financial (Art. 47 LB + FINMA) | Residency: CH mandatory
- Guardrails: No investment advice, auto SAR, human_decision_required on transactions
- Key check: Secret bancaire + FINMA compliance + SAR automation

### Startup Tech
- Risk: Limited | Data: Technical | Residency: Flexible
- Guardrails: Mask secrets/API keys, blocked: [deploy_production, billing_changes]
- Key check: Secret management + no eval/exec on AI output

### Cabinet RH / Recrutement
- Risk: HIGH (Annexe III emploi) | Data: HR | Residency: EU
- Guardrails: NEVER autonomous selection, bias detection mandatory, human_oversight: true
- Key check: Art. 22 profiling + bias detection + DPIA

---

## PITFALLS

- ❌ Never accept incomplete or ambiguous "evidence"
- ❌ Never negotiate on RGPD/AI Act requirements
- ❌ Never validate a dossier with critical violations
- ❌ Never ignore recent CNIL decisions (check last 30 days)
- ❌ Never produce vague recommendations

- ✅ Always require documented evidence
- ✅ Always cite exact RGPD/AI Act articles
- ✅ Always activate Kill Switch on critical risks
- ✅ Always check regulatory updates from last 30 days
- ✅ Always produce an operational action plan

---

## RELATION TO LE GARDIEN DES NORMES

This skill and `le-gardien-des-normes` share the same regulatory content but serve different contexts:
- **Le Gardien des Normes** = Hermes-native compliance officer. Includes DB queries, cron monitoring, weekly checklists, cortex-leman.db integration. Use when auditing inside the Hermes ecosystem.
- **cortex-leman-compliance-agent** = Agent-agnostic compliance context. No DB dependencies, no Hermes-specific tooling. Use when the audit needs to run on Codex, Cursor, Claude Code, or any agent outside Hermes.

When both are available (Hermes session), prefer `le-gardien-des-normes` for deeper integration. Use `cortex-leman-compliance-agent` for portability and cross-agent distribution.

- **Audit baseline (cortex-leman-v5):** `references/audit-baseline-v5.md` — first live audit, score 0.72, with specific violations and codebase findings

## REFERENCES

- RGPD: Regulation EU 2016/679
- AI Act: Regulation EU 2024/1689
- LPD (CH): Federal Act on Data Protection (nLDP, Sept 2023)
- CNIL decisions: cnil.fr
- EDPB guidelines: edpb.europa.eu
- CJEU case law: curia.europa.eu
- PFPDT (CH): edoeb.admin.ch
- Stanford CS230 Study Guide (April 2026): AI autonomy, RAG vs fine-tuning, traceability
- arXiv:2602.20021: State verification (anti-fake-report)

---

**This skill makes any agent a RGPD-IA compliance auditor. No website. No upload. Just context.**

## SUPPORT FILES

- `references/prompt-templates.md` — Universal, short, and vertical-specific prompts for any agent
- `references/audit-baseline-v5.md` — First live audit on cortex-leman-v5, score 0.72, violations and codebase findings
- `references/ai-reasoning-opacity-fable5.md` — Fable 5 CoT leak case study: reasoning opacity as AI Act auditability risk, with business argument for clients
- `cursorrules.md` — Drop-in rules for Cursor IDE
- `CLAUDE.md` — Drop-in rules for Claude Code
