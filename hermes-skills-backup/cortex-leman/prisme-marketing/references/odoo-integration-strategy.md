# Odoo Integration Strategy for Cortex Leman

> Source: 2 rounds of GPT-5.6 contrarian analysis (Aug 7, 2026)
> Trigger: founder observed PME romandes widely use Odoo; proposed becoming Odoo Partner + integrating agents via API.
> Status: **STRATEGY DECIDED** — Odoo is a distribution channel, not a métier. Client-first, not build-first.

## Core Verdict

**Odoo is an excellent target market, but becoming an Odoo integrator is a trap for a solo founder.**

Two separate analyses confirmed the same conclusion:
1. **Round 1** (partner + API strategy): don't become integrator; be the managed-ops layer above Odoo, distributed via existing integrators.
2. **Round 2** (self-hosting for dogfooding): don't install Odoo now; "the founder needs a client, not an ERP."

## Why NOT to become Odoo Partner (Round 1)

- **Scope creep trap**: Odoo = universe of services (analysis, config, data migration, Swiss localization, modules, training, support). Client sees you as "their Odoo guy," not their AI operator.
- **Hidden costs**: certifications, sales targets, pre-sales unpaid work, permanent support, commercial pressure to sell licenses.
- **Responsibility inflation**: when QR-facture breaks after update, they call you — not Odoo.
- **Solo credibility gap**: a solo "Gold" partner without a team can look artificial.
- **Rate illusion**: 800-1500 CHF/day seems great, but factor in pre-sales, meetings, documentation, version management, collections, unpaid periods.

## Why NOT to self-host Odoo now (Round 2)

- **Infrastructure**: 3.8GB RAM = lab OK, production NO. Odoo + PostgreSQL + Hermes + spikes = OOM killer.
- **Fake case study**: founder is admin+user+integrator+provider — bypasses every obstacle a real client wouldn't allow. "Marketing de laboratoire."
- **Procrastination productive**: version selection, Docker, reverse proxy, TLS, QR-factures, TVA, modules — each task feels legitimate, none generates a client.
- **Bad arbitrage**: 2-5h/month lost to fragmented tools vs 30-80h to install/configure/secure/maintain Odoo. At 0 clients, the ERP overhead exceeds the problem it solves.

## The Strategy That WON

### Positioning

> "Cortex Leman devient le spécialiste romand d'un processus opérationnel précis, automatisé et supervisé dans Odoo, distribué via les intégrateurs qui possèdent déjà les clients."

Odoo = **distribution channel + anchoring**, not a new métier.

### Go-to-market via existing integrators

Integrators have: client base, trust, technical access, implementation knowledge.
They lack: agentic skills, time to supervise IA workflows, a recurring results-based offer.

**Proposition to integrators:**
- Cortex doesn't resell ERP licenses
- Cortex doesn't take over their maintenance
- Integrator keeps the Odoo relationship
- Cortex deploys + supervises a defined workflow
- Revenue share or lead referral
- Clearly separated responsibilities

### The wedge workflow

> **Suivi automatique et supervisé des opportunités et devis Odoo.**

- Detect quotes without response
- Analyze CRM history
- Prepare contextualized follow-up
- Propose next activity
- Get human validation
- Write result to Odoo
- Measure follow-up + conversion rate

**Why this workflow:** close to revenue, moderate risk, measurable, frequent, data already available. No accounting, no payments, no danger.

### Cases to AVOID initially

Invoices, accounting entries, payments, IBAN changes, HR decisions, data deletion, access rights changes, bulk catalog modifications, multi-module workflows.

### Architecture: closed-action gateway (NOT direct API calls)

The LLM must NEVER produce arbitrary API calls. It selects an action from a closed catalog:

```
search_customer → create_lead_draft → prepare_quotation_draft → add_internal_note → get_overdue_invoices
```

Gateway enforces: strict JSON schemas, field allowlists, operation allowlists, amount controls, idempotency keys, timeouts, retry limits, rate limiting, secret masking, audit logs, versioned compatibility.

### Deployment progression

1. **Read-only** (observation + reporting)
2. **Suggestions** (drafts, notes)
3. **Write with human validation**
4. **Limited automation of reversible actions only**

Never: autonomous accounting, payments, IBAN, suppressions, irreversible actions.

### Security constraints for client-side Odoo access

- Dedicated service account with minimal privileges
- Allowlist of Odoo models, fields, and operations
- Independent audit journal (not just Odoo's own logs)
- Network: prefer outbound connector installed at client site over inbound API exposure
- LLM prompt injection defense: agent reads Odoo text (emails, notes, descriptions) = indirect injection surface

## 90-Day Plan (if Odoo becomes a confirmed segment)

| Week | Action | Gate |
|---|---|---|
| S1 | Interview 10+ PME Odoo users + integrators. Confirm 1 workflow is painful (3x minimum). | 3+ pain confirmations |
| S2 | Deploy disposable sandbox Odoo (separate VPS). Build read-only adapter → draft creation → human validation. 5-min demo. | Working demo |
| S3-4 | Sell 3 paid pilots (not free). Setup fee + 30-45 days + KPIs before/after. | 3 signed pilots |
| S5-8 | Deliver. Measure: tasks executed, human time saved, proposal acceptance rate, correction rate, API failures, LLM cost per workflow. | 2/3 convert to subscription |
| S9-12 | Decision: if 2/3 convert + same workflow covers 80% + setup reproducible + supervision low → evaluate Odoo Partner status. Else: drop or pivot. | Go/no-go |

## Technical pitfalls specific to Odoo

1. **Community ≠ Enterprise feature parity** — especially accounting. Don't assume Community replaces "5 tools."
2. **Swiss localization** — TVA, QR-factures, sequences, currencies, rounding, accounting requirements. Not details.
3. **Upgrades break third-party modules** — always.
4. **Naive field writes ≠ business method calls** — `write()` doesn't trigger Odoo's expected workflow transitions. Use business methods.
5. **Server actions + automated actions create side effects** — a write can cascade.
6. **Attachments grow storage + backups fast**.
7. **Email is a major complexity source** — SMTP, deliverability, inbound aliases, threading.
8. **Multi-company + record rules** are easy to misconfigure.
9. **Client environments are heterogeneous** — formalize a compatibility matrix, don't promise "Odoo-compatible."
10. **API evolution** — XML-RPC/JSON-RPC being superseded by newer JSON API. Build versioned adapter, not scattered RPC calls.
