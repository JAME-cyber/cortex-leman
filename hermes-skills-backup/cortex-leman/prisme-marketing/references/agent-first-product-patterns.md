# Agent-First Product Patterns (from Comp AI CRM analysis)

> Source: trycompai/crm (7.4k⭐ Aug 2026) — github.com/trycompai/crm
> tweet: x.com/RoundtableSpace/status/2085610640857567447
> 3 architectural patterns stolen and mapped to Cortex Leman product design.

## Pattern 1: Evidence Ledger (replaces opaque scoring)

**Comp CRM concept:** The agent never guesses. No tool accepts a confidence score — "a model asked to grade its own certainty will be wrong in the direction that makes it look useful." Instead, tools report what they observed, and a ledger prices the evidence. Strong evidence writes to the record. Weak evidence becomes a suggestion a human settles.

**Application — Diagnostic PRISME Live:**

The diagnostic does NOT deliver "Score conformité 73/100". It delivers a **ledger d'évidence**:

```
RISQUE: Pas de registre des activités de traitement (nLPD art. 9)
  SOURCE: Entretien DPO + scan politique interne
  FORCE: Forte (documenté, vérifié)
  JURIDICTION: Suisse
  DATE: 2026-08-07
  STATUT: En vigueur
  → ACTION: Créer le registre. Template fourni.

RISQUE: Données client transmises à ChatGPT sans DPA
  SOURCE: Scan configuration + entretien IT
  FORCE: Forte (config constatée)
  JURIDICTION: nLPD art. 9 + RGPD art. 28
  DATE: 2026-08-07
  STATUT: En vigueur
  → ACTION: Conclure un accord de sous-traitance. Migration self-hosted recommandée.
```

**Why it's a moat:** A buyer can verify every line. It's the opposite of a generic scoring PDF. It also satisfies pitfall #12 (Section 11.2 du playbook) — regulatory content must cite primary sources.

**Implementation note:** The SCOUT-3 (Diagnostic conformité) agent should output structured evidence records, not a single score. The PRISME score is a *summary* of the ledger, not a replacement.

## Pattern 2: "The CRM is where the agent keeps its notes" (pitch inversion)

**Comp CRM concept:** "The agent is not a feature of the CRM; the CRM is where the agent keeps its notes."

**Application — Cortex Leman pitch:**

> "PRISME n'est pas une feature de votre marketing. Votre marketing est le journal de travail des agents."

This clarifies the positioning: the client doesn't buy a tool with AI in it. They buy agents that work, and the content/site/reports are **artifacts** of that work. The weekly value ledger (already in the skill) is an example — it's the agent's journal, not a marketing dashboard.

## Pattern 3: Sandbox deny-all egress (makes "self-hosted" defensible)

**Comp CRM concept:** The sandbox has bash/grep/glob + `/workspace` but **deny-all egress** and **never DATABASE_URL**. Rationale: "a shell with credentials and egress is exfiltration-shaped even in an internal tool; a shell with neither is a text processor."

**Application — Cortex Leman technical defensibility:**

This is the answer to pitfall #10 ("self-hosted ≠ souverain"). The stack can adopt:

- Diagnostic skills run in sandbox
- Egress = deny-all by default
- Agent never has access to client credentials
- Sensitive data never transits through a shell

This transforms "souverain" (contestable) into "deny-all egress, no credentials in sandbox" (demonstrable, auditable). A serious buyer asking "where are the models, where are the logs, who has access" gets a concrete technical answer, not a marketing claim.

## Why Comp CRM is NOT a competitor

- It's a sales CRM (contact enrichment, pipeline tracking), not a marketing/compliance pipeline
- No compliance gate, no nLPD/RGPD/AI Act awareness
- No content production capability
- Different target (sales teams vs PME governance)

But it IS the **4th validation of the "graph engineering" pattern** (after Claude Code, Campaign Graph, DeerFlow): durable agent schedules, filesystem-first tooling, work queues with `FOR UPDATE SKIP LOCKED`.

## Technical stack notes (for reference, not for adoption)

- **eve** (Vercel's durable agent framework): tool = file, skill = markdown, schedule = file. Sessions survive redeploys. Worth monitoring — conceptually close to Hermes but with native persistence.
- Single-tenant by design: "An organizationId that is always the same value is a column, an index and a permissions check that buys nothing."
- Intelligence never lives in the API: "Nest reports that something happened; the agent decides what it means."
