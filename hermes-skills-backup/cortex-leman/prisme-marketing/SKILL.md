---
name: prisme-marketing
category: cortex-leman
version: 1.2.0
description: "Use for Cortex Leman marketing or PRISME pipeline work."
metadata:
  hermes:
    tags: [cortex-leman, marketing, prisme, positioning, pricing]
  created: "2026-08-06"
  status: "validated"
  related_skills: [agent-implementation-service, l-architecte-lemanique, content-channel-branding]
---

# PRISME — Cortex Leman Marketing & Go-To-Market

PRISME is the branded marketing method for Cortex Leman. It names the existing agentic pipeline (scout→research→production→QA→delivery→learning) with a memorable French acronym, making it sellable as a product/service. Created and validated 6 August 2026.

**Trigger:** Use this skill when working on ANY Cortex Leman marketing task — positioning, pricing, content, competitor analysis, go-to-market, client acquisition, or PRISME pipeline development.

## The Method

Metaphor: a prism decomposes white light into a spectrum. One brief in → a spectrum of compliant multi-channel content out.

```
P → Pilotage     (orchestrateur: brief → workloads → fan-out agents)
R → Recherche    (scout + knowledge compiler)
I → Ingénierie   (script + assets + render)
S → Scoring      (QA vision + compliance gate RGPD/AMF/MiCA — hard rules override LLM)
M → Multi-canal  (delivery: Telegram, email, social, web, podcast)
E → Évaluation   (feedback loop → skills → templates → next cycle)
```

**3 differentiators no competitor has:**
1. Compliance gate native — pipeline stage, not add-on (covers **nLPD** + RGPD + AI Act + AMF L541-1)
2. QA vision externe — no output without external validation
3. Self-hosted, données stockées en Suisse — ⚠️ NEVER say "souverain" without technical+contractual proof (see pitfall #10)

**⚠️ Business model reality (GPT-5.6 cross-validation, Aug 2026):** Cortex Leman is a **service managé productisé**, NOT a SaaS. Cost marginal per client = 0.5-3j/mois + 2-5j/mois socle mutualisé + variance (incidents can absorb 3 unplanned days). The promise "agents that maintain themselves" is dishonest and legally risky. Always frame as **automatisation supervisée** — never "autonome." See pitfalls #13-16.

⚠️ **Compliance scope correction (GPT-5.6 cross-validation, Aug 2026):** The original scope listed RGPD/AI Act/MiCA/ZertES but **missed the nLPD suisse** (Loi fédérale sur la protection des données), which is the single most relevant data-protection law for Swiss PMEs. MiCA and ZertES are too specialized for the core pitch — keep them only for fintech/crypto verticals. The compliance gate must foreground **nLPD + RGPD (when applicable to EU-facing) + AI Act** as the core triad.

## Positioning

**Hook:** "Le partenaire opérationnel IA des PME romandes."

**Narratif "For the 99%"** (volé de Polsia @polydao, retourné contre eux, Aug 2026): Le marché IA se coupe en deux. Les 1% qui ont des équipes data/agents. Et les 99% — les PME qui copient-collient entre ChatGPT et leur métier. Cortex Leman sert les 99%. Pas besoin d'apprendre le prompt engineering. C'est notre travail.

**Persona central: "Magalie de la compta"** (volé de @LeDindonFiscal, 194 likes, Aug 2026): La comptable FR-CH qui ne sait pas coder mais a déjà les outils IA entre les mains sans le savoir. C'est elle qu'on sert.

**Editorial framing:** "IA opérationnelle et gouvernée pour PME romandes." PMEs don't buy "compliance IA" — they buy less risk, faster decisions, validated tools, operational gains without data leaks. Compliance is a component of the promise, not the product.

**Core shift:** the client stops being the queue and starts directing it. The "managed layer" insight: clients don't know how to delegate to agents — adoption coaching IS the product, not the install.

## Pricing (validated against 4 competitors, Aug 2026)

| Level | Price | Content |
|---|---|---|
| Entry (Diagnostic IA) | 500-1,500 CHF | Diagnostic de gouvernance IA: 1 workflow, 1 rapport, 1 plan d'action |
| Core (Service mensuel) | 1,500-5,000 CHF/mois | Automated content + governance pipeline PRISME |
| Scale (Licence harness) | 500-2,000 CHF/mois | Self-hosted license for agencies |

> ⚠️ Never use the word "audit" in client-facing language. See pitfall #8. The entry product is "Diagnostic de gouvernance IA et données" with explicit scope + exclusions (not legal advice, not opposable, recommend validation by Swiss lawyer when needed).

> ⚠️ **Honest pitch (GPT-5.6, Aug 2026):** NEVER say "agents that maintain themselves, 24/7, for the cost of a monthly license." This is dishonest (maintenance cost exists), legally risky (who is responsible?), and market-mismatched (PMEs want supervised results, not uncontrolled autonomy). ALWAYS use the **pilot-then-commit** pitch: *"We automate [specific process] without replacing your system. Goal: reduce delay X→Y, save Z hours/month. Sensitive actions stay human-validated. Subscription includes supervision, updates, incident management, monthly performance report. If pilot goals aren't met, no subscription."* See pitfall #14.

Products: Guide PRISME PDF (49-99 CHF), Skills pack (199-499 CHF), Formation video (299-799 CHF), Template vault (79-149 CHF).

## Diagnostic PRISME Live — Acquisition Funnel

The diagnostic is NOT a static PDF. It's a **live agentic scout** running in real-time during a 45-min video call. The prospect SEES agents working before buying.

- Phase 1 (10 min): Prospect provides URL + 1 manual process + current tools
- Phase 2 (20 min): 3 agents work in parallel (SEO, process, compliance) on shared screen
- Phase 3 (10 min): Report generated live — PRISME Score 0-100 on 6 axes + top 3 opportunities + compliance risk map + mini-boucle demo
- Phase 4 (5 min): Recommendation → upsell

Target conversion: 70%+ (vs competitor 50-60%).

Funnel: Diagnostic Express free (30 min) → 40% convert to Diagnostic Complet → 50-60% convert to PRISME subscription.

**MVP:** No fancy dashboard needed for V1. Terminal Hermes scrolling on shared screen = the "wow" effect. Dashboard HTML = V2.

## Weekly Value Ledger (retention killer feature)

Agent logs every task: what was completed, how long it would take a human, estimated $ value of time saved. Weekly report every Friday. Makes the retainer visible and justifiable. Implement as Hermes cron job.

Source: Phil Goodwin playbook via @coreyganim.

## Content Strategy (1 signed vertical media, not anonymous accounts)

> ⚠️ Correction (GPT-5.6, Aug 2026): the original "eat your own dogfood / 5 angles" strategy assumed X/Twitter threads as primary channel and anonymous branded accounts. This does NOT work in FR-CH B2B. See pitfall #9 and `references/distribution-strategy-fr-ch.md`.

**Architecture: 1 média vertical signé**
- **Profil personnel du fondateur** = primary distribution engine (LinkedIn organic > company page)
- **Newsletter** = editorial rhythm + owned audience (bi-weekly)
- **Cortex Leman** = transparent operator (not hidden, not clandestine)
- **PRISME** = backstage methodology, demonstrated by results (not jargon in cold pitches)

**4 editorial pillars:**
1. **Cas d'usage opérationnels** — concrete AI workflows (sales qualification, proposal prep, document processing). Practical proof.
2. **Gouvernance et données** — nLPD, vendor assessment, internal policies, data transfers, human oversight. Editorial moat.
3. **Tests et benchmarks** — cloud vs self-hosted, real costs, accuracy, time saved, observed risks. Original data = true differentiator.
4. **Retours terrain** — before/after, errors, limits, when automation isn't worth it. Authenticity = trust.

**Content cadence:**

| Channel | Format | Frequency |
|---|---|---|
| LinkedIn (personal profile) | Analytical post | 2x/week |
| Newsletter | Long-form email | 1x/2 weeks |
| YouTube | Video essay (5-10 min) | 1x/month |
| Website | Case study / benchmark | 1x/month |

**Mandatory regulatory content validation rule:** any content touching law (nLPD, RGPD, AI Act) must cite primary sources, date analyses, distinguish in-force vs proposed law, indicate jurisdiction, pass human validation, and publicly correct errors.

## Competitor Marketing Technique Library

Condensed patterns extracted from competitor tweet/article analysis.

### From @VibeMarketer_
- **Authority hijack** → adapt: use own case studies, not borrowed credibility
- **Abstraction ascendante** → present stack as paradigm (PRISME), not feature list
- **Shift de posture** → "stops being the queue" = central pitch
- **CTA différé** → every content ends with setup link

### From @iamsupersocks / méthode ACE
- **Branding par acronyme** → PRISME: French, searchable, proprietary
- **Name your method to sell it** — unnamed workflows don't sell
- **Boucle visible** → PRISME diagram = workflow made visible and sellable

### From @coreyganim (Managed AI Employees + pricing grid)
- **"Sell a role, not an agent"** → position as digital employee
- **Managed layer = real product** → adoption coaching IS what they pay for
- **"Anchor on hours saved, not hours worked"**
- **Transparent paid pilot** → "I'm testing, you get lower price + more attention"
- **Pricing evolution** → match price to proof: $500 setup → $250/mo pilot → $1,500 setup + $500/mo → $2,000 setup + $1,000/mo
- **Assessment as universal entry point** — 50-60% convert to implementation

### From @mathieuhq (businessfreelance.fr — best FR agent copywriting)
- **"Tu fais le facteur"** → visceral metaphor for the real pain. Adapt: "Votre [business] mérite mieux qu'un facteur."
- **"Ton problème n'est pas ton prompt"** → reframe: blame the tool, not the user. Removes shame barrier to buying.
- **Anti-hype explicit** → "Hermes ne va pas gérer ton business tout seul pendant que tu dors." Validates Cortex Leman positioning.
- **Sequential value ladder** → install → connect → memory → first task → suggest next. Strict sequence, not feature list. Mirrors PRISME étape P.
- **"Suggest next delegation" skill** → agent analyzes session logs and proposes what to delegate next. Killer retention feature — implement as Hermes skill for PRISME.
- **Landing page copy structure** → problem metaphor → reframe → anti-hype → sequential solution → before/after → 14-question FAQ. Template for Cortex Leman landing pages. Full deconstruction in references/mathieuhq-landing-page-copywriting.md.
- **DM-response growth** → answer every DM at early stage. Free, human, converts to clients.
- **Non-tech FR market validated** → "elles ont les idées, les besoins et le budget." Confirms PME FR-CH market opportunity.

### From Cody Schneider (Marketing Agent Architecture)
- **Data warehouse unified** → phase 2-3 architecture (Airbyte → ClickHouse)
- **Kill losers, promote winners** → learning loop in étape E
- **Entropy injection** → scout scans external signals continuously

### From Campaign Graph pattern (@shannholmberg)
- **Graphe swappable** → PRISME = graph where each node is a replaceable skill
- **Model routing par nœud** → different model per task

## Execution Pipeline (locked priority order, revised Aug 2026)

> Phase 1 now starts with ICP validation before content production.

0. **ICP validation interviews** — 12-15 interviews with PME romandes decision-makers before producing any content
1. Média vertical signé on LinkedIn (founder personal profile) — 2 posts/week
2. Newsletter bi-weekly — owned audience, editorial rhythm
3. Diagnostic PRISME Live — first 3 paid diagnostics = case studies
4. Guide PRISME PDF — lead magnet
5. Diagramme PRISME — visual brand asset (Le Narrateur Augmenté)
6. Page de destination — cortex-leman.ch/prisme

**Success criteria at 90 days:** 10-15 conversations with ICP profiles, 2-3 paid diagnostics, ≥1 conversion to recurring mission. If audience is >70% non-ICP (consultants, freelances, students), the editorial theme is misaligned — adjust.

## Cross-Validation Protocol (GPT-5.6 via OpenRouter)

Critical PRISME decisions (positioning, pricing, compliance scope, distribution strategy, business model, pitch) must be cross-validated by an independent LLM acting as a **contrarian strategist**. This protocol caught material errors across three rounds:
- Round 1 (nLPD, "audit" wording, anonymous pages, impression math, "souverain" claim)
- Round 2 (business model reality, dishonest pitch, productisation gate, "autonome" fear, régie-vs-produit economics, FAQ anti-objections)

**How to run:**
1. Draft the analysis/decision in GLM (primary model)
2. Send to GPT-5.6 (or Kimi 3 as second opinion) via OpenRouter with a contrarian prompt: "Tu es un stratège marketing contrarien spécialisé B2B FR-CH. Analyse cette stratégie de façon critique et honnête. Pas de flattery. Cherche les angles morts, les hypothèses non vérifiées, les erreurs culturelles FR-CH."
3. Require: specific corrections with rationale, cultural blind spots, legal risks, alternative framing
4. Patch the playbook/skill with accepted corrections, tagging them "(cross-validation [model], [date])"

**Key OpenRouter parameter:** `max_tokens: 8000+` for reasoning models, `timeout: 300s` for curl. See memory for Kimi 3 specifics.

## Key Files

- `/home/tars/cortex-leman/marketing-playbook.md` — full 12-section playbook (v1.2, GPT-5.6 cross-validated Aug 2026)
- `/home/tars/cortex-leman/audit-prisme-live-spec.md` — Diagnostic PRISME Live product spec
- `/home/tars/cortex-leman/moat-compliance-pitch.md` — Moat compliance strategy: why AI Act Art.50 is Cortex Leman's competitive advantage. C2PA signing as billable service. Roadmap (3 phases, 6 months). Includes SSL.com free cert discovery (0 CHF production C2PA signing). Aug 2026.
- `references/competitor-marketing-techniques.md` — detailed competitor technique library
- `references/mathieuhq-landing-page-copywriting.md` — best FR agent landing page copy deconstruction (Hermes Boost by Mathieu Dacheux)
- `references/distribution-strategy-fr-ch.md` — page-theme strategy analysis + corrected FR-CH distribution model (GPT-5.6 cross-validated, Aug 2026)
- `references/agent-first-product-patterns.md` — 3 architectural patterns from Comp AI CRM (evidence ledger, pitch inversion, sandbox deny-all egress) mapped to Diagnostic PRISME Live and technical defensibility
- `references/business-model-reality.md` — Ventalon cross-validation: service managé vs SaaS, productisation test, régie-vs-abonnement economics, honest pitch, FAQ anti-objections (GPT-5.6, Aug 2026)
- `references/odoo-integration-strategy.md` — Odoo as distribution channel (not métier): integrator GTM, wedge workflow, closed-action gateway architecture, 90-day plan, Odoo-specific technical pitfalls (GPT-5.6, Aug 2026)

## Pitfalls

1. **Selling features instead of transformation** — PRISME sells a posture shift ("directing the queue"), not a tool list. Always frame as paradigm, not features.
2. **Forgetting the managed layer** — the install is 20% of the value. Adoption coaching = 80%. Never deliver just the tech.
3. **Static diagnostic trap** — competitors deliver PDFs in 48h. PRISME's edge is the LIVE agentic diagnostic. Never revert to static delivery.
4. **Pricing too low** — Lead Mapping charges 99€/mo for a Google Maps scanner. PRISME does 10x more. Don't undervalue — compliance + autonomy justify premium.
5. **Not naming the method** — unnamed workflows don't sell. Always use PRISME in client-facing materials.
6. **Missing the "what else can it do?" moment** — after the first delegated task lands, the agent must proactively suggest the next delegation candidate. This is the retention loop (from @mathieuhq and Phil Goodwin). Without it, clients stall after the initial deployment.
7. **Missing nLPD suisse** — the original compliance pitch listed RGPD/AI Act/MiCA/ZertES but omitted the nLPD, which is THE core data-protection law for Swiss PMEs. Always include nLPD in the compliance triad. (GPT-5.6 cross-validation, Aug 2026.)
8. **Using "audit" in client-facing language** — the word "audit" implies formal methodology, legal responsibility, and potentially an opposable report. If Cortex Leman is not a certified auditing body, use "Diagnostic de gouvernance IA" instead, with explicit scope limitations and disclaimers. (GPT-5.6 cross-validation, Aug 2026.)
9. **Anonymous page-theme strategy for FR-CH** — the Julian Shapiro "anonymous topic page" model works at US scale but fails in FR-CH B2B where trust requires a human face. Do NOT create anonymous/branded-only social accounts for Cortex Leman distribution. Use the founder's personal profile as the primary distribution engine, with transparent Cortex Leman attribution. (GPT-5.6 cross-validation, Aug 2026.)
10. **"Self-hosted" ≠ "souverain" without proof** — buyers will ask where models are hosted, where logs go, who has data access, and what sub-processors are involved. The word "souverain" is contestable unless you can demonstrate it technically and contractually. Use with caution and prepare the full data-flow answers. (GPT-5.6 cross-validation, Aug 2026.)
11. **$22/1000-impressions math is not a valid FR-CH economic justification** — organic impressions ≠ targeted paid impressions (different audience quality). 500 followers ≠ guaranteed 1000 impressions. Don't use this metric as a go-to-market justification for FR-CH. Measure conversations, qualified pipeline, and attributable revenue instead. (GPT-5.6 cross-validation, Aug 2026.)
12. **Content that attracts peers, not buyers** — compliance/IA content attracts consultants, lawyers, students, and competitors — not PME decision-makers. Always evaluate audience composition against the ICP, not raw follower counts.
13. **Cortex Leman is NOT a SaaS** — at this stage it's a service managé productisé. Each client needs integration, connectors, validation. "Cost marginal ≈ 0" is false: 0.5-3j/mois per stabilized client + 2-5j/mois socle + incident variance. Don't pitch scalability until the productisation test is passed (pitfall #15). (GPT-5.6 cross-validation Ventalon, Aug 2026.)
14. **"Self-maintaining agents" is a dishonest pitch** — an agent cannot manage its own API changes, prompt regressions, expired secrets, corrupted data, hallucinations, cost drift, security incidents, or client process changes. A human (you) does. Honest framing: "automatisation supervisée avec détection des incidents, reprise contrôlée et maintenance incluse dans l'abonnement." Sell the result, not the agent. (GPT-5.6 cross-validation Ventalon, Aug 2026.)
15. **Productisation gate before scaling** — a framework is not a product. Before pushing to Phase 4 (scale/license), verify: onboarding <5 days, <20% custom per client, <1-2j maintenance/client/month. If these thresholds aren't met, you have a consultancy with a good internal framework, not a scalable product. Don't scale what doesn't standardize. (GPT-5.6 cross-validation Ventalon, Aug 2026.)
16. **"Autonome" is a word that hurts you** — for a PME owner, "agent autonome" triggers fear: who is responsible, where do data go, can it email the wrong client, how to audit, what if the company disappears? The first PME use cases must be: bounded, reversible, observable, low-impact, human-validated. Use: "automatisation supervisée." Avoid: "autonome, agent intelligent, décide seul, 24/7 sans intervention." (GPT-5.6 cross-validation Ventalon, Aug 2026.)
17. **Régie vs abonnement is not binary** — Ventalon's objection ("régie GCP = 12-20k/mois vs agents = 5k") is valid short-term. Break-even = 6-8 stable clients at 5k CHF. Strategy: use consulting missions to fund runway AND identify recurring problems → productize those → gradually reduce régie as MRR rises. Solo operational ceiling: 4-6 clients for managed service, 8-12 only with highly repeatable offer. (GPT-5.6 cross-validation Ventalon, Aug 2026.)
18. **Becoming an Odoo integrator is a trap** — Odoo is an excellent target market (many PME romandes use it, data is "sticky") but becoming an Odoo Partner/integrator is scope-creep suicide for a solo founder: you become "their Odoo guy" responsible for QR-facture breakage, version upgrades, and Swiss localization bugs. Instead: be the **managed-ops layer above Odoo**, distributed via existing integrators who already own the client relationship. Pick ONE wedge workflow (devis/opportunités follow-up), deploy a closed-action gateway (never let the LLM call Odoo API directly), start read-only → drafts → human-validated writes. Never touch accounting/payments/IBAN/deletions initially. And do NOT self-host Odoo for dogfooding before having a client — "the founder needs a client, not an ERP." See `references/odoo-integration-strategy.md` for the full 90-day plan + architecture + pitfalls. (GPT-5.6 cross-validation, Aug 2026.)
19. **Compliance as moat — the angle blind spot** — No enterprise agent competitor (Vercel "V", OpenAI, wrappers, agencies) mentions AI Act compliance. This is a total market blind spot (validated by Rauch/Vercel interview analysis, Aug 2026). Cortex Leman's intersection of FR-CH regulatory expertise (nLPD+RGPD+AI Act) + technical architecture (multi-provider routing, hard rules engine, C2PA signing) is not replicable by global SaaS. Window: 6-12 months before tools like Canva/Adobe integrate C2PA natively. Sell C2PA signing as a billable service (Creator/Agency/Enterprise tiers, 49-499 CHF/mois). Full strategy in `moat-compliance-pitch.md`. (Aug 2026.)
