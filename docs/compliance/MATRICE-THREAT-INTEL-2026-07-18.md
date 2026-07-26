# Matrice Threat Intel — Cycle 2026-07-18

> **Source:** ArXiv Daily Scan 18/07/2026 (job 0f8a90201d56) — 272 papers scannés, 14 alertes critiques (≥15/20), 3 parfaits (20/20), 33 high-relevance (≥10).
> **Cycle précédent:** 14/07 (VEILLE-THREAT-INTEL-2026-07-14.md).
> **Objet:** Consolidation des menaces IA émergentes pour la posture compliance Cortex Leman.

---

## Signaux stratégiques convergents (3)

Ces 3 signaux émergent du scan du 18/07 et modifient la carte de risque Cortex Leman :

### 1. Sécurité des agents à mémoire persistante — **IMPACT DIRECT**

3 papiers indépendants reconnaissent la mémoire cross-session comme nouvelle surface d'attaque :
- **Bad Memory** (arXiv 2607.14611) — injection via fichiers mémoire persistants
- **MemPoison** (arXiv 2607.14651) — 1227 cas documentés
- **Context Contamination** (arXiv 2607.14493) — empoisonnement des logs LLM

**Conséquence Cortex Leman :** l'architecture agent s'appuie massivement sur la mémoire cross-session. Une instruction injectée aujourd'hui peut compromettre des sessions futures, y compris sur d'autres dossiers clients. **→ TICKET-010 (P0).**

### 2. AI Act operationalization — **FENÊTRE COMMERCIALE**

Traccia (20/20) + Global Index 2026 + Fairness-Privacy marquent la transition de la théorie réglementaire vers les outils concrets.

**Conséquence Cortex Leman :** se positionner sur la vague "compliance tooling" comme différenciateur commercial direct face aux auditeurs RGPD classiques. **→ TICKET-009 (P1) + one-pager commercial à préparer.**

### 3. MCP security — **OPPORTUNITÉ EARLY-ADOPTER**

FlowGuard révèle que le protocole MCP manque de validateurs runtime. Première recherche académique dédiée.

**Conséquence Cortex Leman :** comme la stack repose sur MCP (Apify, n8n), on est parfaitement placé pour être early-adopter. **→ TICKET-011 (P1).**

---

## Top 5 alertes critiques (≥16/20)

| # | Score | arXiv | Thème | Action Cortex Leman | Ticket |
|---|-------|-------|-------|---------------------|--------|
| 1 | 20/20 | 2607.14309 | **Traccia — Observabilité IA OpenTelemetry** | POC + socle d'évidence Gardien des Normes | TICKET-009 (P1) |
| 2 | 20/20 | 2607.14607 | **Fairness-Privacy Trade-offs subpopulation** | Intégrer dans checklist audit (healthcare/finance/legal) | — Checklist |
| 3 | 20/20 | 2607.14945 | **Introspective Attention Modulation — Safety T2I** | Veille L'Oeil de Cortex (alternative au classifier gating) | — Veille |
| 4 | 16/20 | 2607.14611 | **Bad Memory — Prompt injection via mémoire agent** | **Audit sandbox mémoire immédiat** | **TICKET-010 (P0)** |
| 5 | 12/20* | 2607.14754 | **FlowGuard — Sécurité MCP runtime** | Tester sur Apify/n8n + politique onboarding MCP | TICKET-011 (P1) |

*FlowGuard = priorité stratégique malgré score 12/20 (1er papier dédié MCP).

---

## Cartographie compliance par article

| Article RGPD / AI Act | Papers pertinents | Action Cortex Leman |
|-----------------------|-------------------|---------------------|
| **AI Act Art. 12 (Logging/Observabilité)** | 2607.14309 (Traccia) | Déployer OpenTelemetry — socle d'évidence RGPD/AI Act (TICKET-009) |
| **AI Act Art. 9-10 (Risques & Data Governance)** | 2607.14607, 2607.14570, 2607.15081 | Auditer trade-off fairness↔privacy ; monitorer fine-tuning |
| **AI Act Art. 14-15 (Oversight & Robustesse)** | 2607.14611, 2607.14651, 2607.14493, 2607.14754 | **Durcir sécurité agents mémoire + MCP** (TICKET-010 P0, TICKET-011 P1) |
| **AI Act Art. 50 (Transparence contenu synthétique)** | 2607.14945, 2607.14194, 2607.15246 | Concept suppression + attention modulation pour T2I/T2V clients |
| **RGPD Art. 5/9 (Minimisation & Données sensibles)** | 2607.14607, 2607.14811, 2607.14205 | Audit membership inference subpopulation ; privacy RAG dynamique |
| **RGPD Art. 17 (Effacement/Unlearning)** | 2607.14945, 2607.14194, 2607.14521 | Concept erasure inference-time — voie pratique pour droit à l'oubli |
| **RGPD Art. 25 (Privacy by Design)** | 2607.14570, 2607.15143 | Monitoring structurel par défaut + validation supply chain (TICKET-012) |
| **RGPD Art. 32 (Sécurité)** | 2607.14611, 2607.14754, 2607.14493, 2607.14651 | Sandboxing mémoire agent + détection runtime MCP |

---

## Veille à suivre (ne pas actionner ce cycle)

| Paper | Pourquoi suivre |
|-------|-----------------|
| 2607.14442 — Disclosure Divergence | Méthodologie LLM-based de détection d'incohérences documentaires — transposable à L'Oeil de Cortex (Kbis/statuts vs pratiques) |
| 2607.14782 — Global Index Responsible AI 2026 | Cadre UNESCO pour positionnement FR-CH Cortex Leman |
| 2607.14945 — Introspective Attention Modulation | Safety T2I robuste aux bypass LoRA/fine-tuning |
| 2607.14194 — SIRUS Concept Suppression T2V | Voie pragmatique pour droit à l'oubli RGPD Art. 17 sur modèles génératifs clients |

---

## Tickets ouverts ce cycle

| Ticket | Priorité | Menace | Source |
|--------|----------|--------|--------|
| **TICKET-009** | P1 | Traccia — Observabilité IA (OpenTelemetry) | arXiv 2607.14309 |
| **TICKET-010** | **P0** | Bad Memory + MemPoison (mémoire agent) | arXiv 2607.14611 + 2607.14651 |
| **TICKET-011** | P1 | FlowGuard — Sécurité MCP runtime | arXiv 2607.14754 |
| **TICKET-012** | P2 | Supply-chain skills externes | arXiv 2607.15143 |

---

*Le Gardien des Normes — Matrice Threat Intel cycle 2026-07-18. Croisement avec matrice R1-R4 et checklist compliance dans `MATRICE-RISQUES-R1-R4.md` et `CHECKLIST-COMPLIANCE-IA.md`.*
