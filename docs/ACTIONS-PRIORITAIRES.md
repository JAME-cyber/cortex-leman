# Actions Prioritaires Cortex Leman
Dernière mise à jour: 2026-07-26

---

## 🔁 Cycle 2026-07-26

**Inputs traités :** jobs nouveaux / mis à jour depuis cycle 25/07.

| Rapport | Job ID | Run | Statut | Output exploitable |
|---------|--------|-----|--------|--------------------|
| **ArXiv Daily 26/07** | `0f8a90201d56` | 26/07 10:02 | ✅ **Succès — synthèse hebdomadaire consolidée** | 🆕 **1 nouveau cluster** non couvert : Machine Unlearning Equity (4 papers R:8, RGPD Art. 17). Le reste = consolidation Mon-Fri déjà traitée cycle 25/07. |
| CNIL Sanction 26/07 | `7d92c44685ae` | 26/07 10:00 | ✅ `[SILENT]` nominal | ℹ️ Aucune sanction < 72h — job fonctionne correctement |
| Brief RGPD-IA Hebdo 15/07 | `476112fc9e18` | 15/07 12:54 | ✅ Succès | ℹ️ Déjà traité cycle 18/07 |
| Weekly Report S28 17/07 | `a7cbd0ff1c22` | 24/07 18:02 | ✅ Succès | ℹ️ Déjà traité cycle 18/07 |

**Signaux ce cycle (delta 25/07 → 26/07) :**

🟢 **Nouveau cluster equity / droit à l'oubli IA** — la synthèse dominicale identifie un angle mort de nos offres : le **machine unlearning** peut désavantager systématiquement certaines classes démographiques (4 papers R:8 convergents). Risque RGPD Art. 17 + Art. 9 inédit. One-pager N°8 créé.

🟢 **Corpus académique consolidé** — les 5 papiers R≥10 dominants de la semaine sont désormais capturés dans un argumentaire réutilisable (citations directes + hooks commerciaux). Top 3 à citer dans toutes propositions : *Closing the AI Trust Gap* (R:12), *Critical Analysis of Trustworthy AI Tools* (R:12), *ChannelGuard* (R:9).

🔴 **DEADLINE CRITICAL OFFICIELLEMENT DÉPASSÉE (J+5) — 5e vérification DB lecture seule :**
- Score global compliance : **0.30/1.00** — **inchangé depuis W29 (6e point de contrôle consécutif)**
- **0/4 comptes Santé/Banque/Avocat** ont la MFA activée (toujours `mfa_enabled = 0`)
- **0/8 tenants** créés (table `tenants` vide, 12/12 users `tenant_id = NULL`)
- **100% IPs placeholder** dans audit_logs (`testclient`×48, `127.0.0.1`×10, `None`×5)
- **Email invalide** `jame.callaghan@gmail:com` toujours non corrigé
- **Dernier log d'activité : 2026-05-31** (système dormant 56 jours)
- **Kill Switch TOUJOURS ARMÉ** — 0 remédiation exécutée par Tars entre 20/07 et 26/07 (6 jours)

---

## ✅ Exécutées ce cycle (2026-07-26)

| # | Action | Fichier créé/maj | Source |
|---|--------|------------------|--------|
| 1 | **Statut jour J+5 deadline CRITICAL** — 5e vérification DB lecture seule consécutive, constat : 0/5 actions remédiées en 144h+, Kill Switch toujours armé, système dormant 56j | `docs/compliance/STATUT-DEADLINE-CRITICAL-2026-07-26.md` | Vérif DB directe (Python sqlite3, `?mode=ro`) |
| 2 | **One-pager commercial "Droit à l'Oubli IA Équitable"** prêt (8e offre) — cluster Machine Unlearning Equity (4 papers R:8), pricing 4.5-18k CHF, 5 cibles, J-7 | `docs/strategie-2026-07/ONE-PAGER-DROIT-OUBLI-EQUITABLE-IA.md` | ArXiv 26/07 cluster unlearning |
| 3 | **Argumentaire académique ArXiv juillet 2026** créé — corpus complet des 5 papiers R≥10 + 7 vecteurs sécurité + 5 papiers equity, citations directes réutilisables dans propositions | `docs/strategie-2026-07/ARGUMENTAIRE-ACADEMIQUE-ARXIV-2026-07.md` | Synthèse ArXiv hebdo 26/07 |
| 4 | Mise à jour du présent fichier de suivi | `docs/ACTIONS-PRIORITAIRES.md` | Synthèse cycle |

---

## 🔁 Cycle 2026-07-25

**Inputs traités :** jobs nouveaux / mis à jour depuis cycle 23/07.

| Rapport | Job ID | Run | Statut | Output exploitable |
|---------|--------|-----|--------|--------------------|
| **ArXiv Daily 25/07** | `0f8a90201d56` | 25/07 09:11 | ✅ **Succès (rapport delta complet `show=1000`)** | 🆕 **3 nouveaux clusters** non couverts : self-hosted agent security (4 papers R≥8), AI SBOM, RAIL Guard + nouveaux vecteurs vision/biométrie |
| CNIL Sanction 25/07 | `7d92c44685ae` | 25/07 09:33 | ✅ `[SILENT]` nominal | ℹ️ Aucune sanction < 72h — job fonctionne correctement |
| Brief RGPD-IA Hebdo 15/07 | `476112fc9e18` | 15/07 12:54 | ✅ Succès | ℹ️ Déjà traité cycle 18/07 |
| Weekly Report S28 17/07 | `a7cbd0ff1c22` | 24/07 18:02 | ✅ Succès | ℹ️ Déjà traité cycle 18/07 |

**Signaux ce cycle (delta 23/07 → 25/07) :**

🟢 **Veille ArXiv rétablie** — le rapport 25/07 (delta week-end, `show=1000`) a compensé l'échec 23/07 (HTTP 429) et révèle que la pagination limitée à 50 des cycles précédents manquait **~64% des signaux pertinents** sur cs.AI/CV/LG. Le rapport complet identifie **7 papiers R≥10** (dont 4 nouveaux non couverts) + 3 clusters émergents.

🔴 **DEADLINE CRITICAL OFFICIELLEMENT DÉPASSÉE (J+3) — 4e vérification DB lecture seule :**
- Score global compliance : **0.30/1.00** — **inchangé depuis W29 (5e point de contrôle consécutif)**
- **0/4 comptes Santé/Banque/Avocat** ont la MFA activée (toujours `mfa_enabled = 0`)
- **0/8 tenants** créés (table `tenants` vide, 12/12 users `tenant_id = NULL`)
- **100% IPs placeholder** dans audit_logs (`testclient`×48, `127.0.0.1`×10, `None`×5)
- **Email invalide** `jame.callaghan@gmail:com` toujours non corrigé
- **Dernier log d'activité : 2026-05-31** (système dormant 55 jours)
- **Kill Switch TOUJOURS ARMÉ** — 0 remédiation exécutée par Tars entre 20/07 et 25/07 (5 jours)

🆕 **3 nouveaux clusters stratégiques identifiés :**
1. **Self-hosted agent security** (4 papers R≥8) — angle mort du marché, opportunité commerciale directe (one-pager N°7 créé)
2. **AI SBOM** (Art. 11/13 AI Act) — convergent avec TICKET-022 + TICKET-027, livrable standard futur
3. **RAIL Guard** (boucle évaluation→remédiation) — remède direct au gap interne (deadline CRITICAL non exécutée)

---

## ✅ Exécutées ce cycle (2026-07-25)

| # | Action | Fichier créé/maj | Source |
|---|--------|------------------|--------|
| 1 | **Statut jour J+3 deadline CRITICAL** — 4e vérification DB lecture seule consécutive, constat : 0/5 actions remédiées en 120h+, Kill Switch toujours armé, système dormant 55j | `docs/compliance/STATUT-DEADLINE-CRITICAL-2026-07-25.md` | Vérif DB directe (Python sqlite3, `?mode=ro`) |
| 2 | **TICKET-027** créé — Sécuriser agents auto-hébergés (cluster Chronos + Self-State + CI/CD, 4 papers R≥8, P1) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 25/07 |
| 3 | **TICKET-028** créé — Adopter AI SBOM (SPDX/CycloneDX extension IA, AI Act Art. 11/13, P1) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 25/07 (2607.17242) |
| 4 | **TICKET-029** créé — Évaluer RAIL Guard comme socle boucle évaluation→remédiation (P2) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 25/07 (2607.16215) |
| 5 | **One-pager commercial "Self-Hosted Agent Security"** prêt (7e offre) — angle runtime agent on-prem, pricing 10-40k CHF, 5 cibles FR-CH, J-8 | `docs/strategie-2026-07/ONE-PAGER-SELF-HOSTED-AGENT-SECURITY.md` | ArXiv 25/07 cluster self-hosted |
| 6 | **Checklist compliance Phase 13** ajoutée (5 sections : runtime agents, AI SBOM, RAIL Guard, vision/biométrie, guardrails) | `docs/compliance/CHECKLIST-COMPLIANCE-IA.md` | ArXiv 25/07 |
| 7 | Mise à jour du présent fichier de suivi | `docs/ACTIONS-PRIORITAIRES.md` | Synthèse cycle |

---

## 🔁 Cycle 2026-07-23

**Inputs traités :** jobs nouveaux / mis à jour depuis cycle 22/07.

| Rapport | Job ID | Run | Statut | Output exploitable |
|---------|--------|-----|--------|--------------------|
| ArXiv Daily 23/07 | `0f8a90201d56` | 23/07 09:05 | ❌ **ÉCHEC (HTTP 429)** | ⚠️ Scan impossible — service surchargé. Aucune nouvelle veille. Dernier ArXiv exploitable : 22/07 |
| CNIL Sanction 23/07 | `7d92c44685ae` | 23/07 09:34 | ✅ `[SILENT]` nominal | ℹ️ Aucune sanction < 72h — job fonctionne correctement |
| Brief RGPD-IA Hebdo 15/07 | `476112fc9e18` | 15/07 12:54 | ✅ Succès | ℹ️ Déjà traité cycle 18/07 |
| Weekly Report S28 17/07 | `a7cbd0ff1c22` | 17/07 18:04 | ✅ Succès | ℹ️ Déjà traité cycle 18/07 |

**Signaux ce cycle (delta 22/07 → 23/07) :**

🔴 **DEADLINE CRITICAL OFFICIELLEMENT DÉPASSÉE (J+1) — vérification DB lecture seule :**
- Score global compliance : **0.30/1.00** — **inchangé depuis W29 (4e point de contrôle consécutif)**
- **0/4 comptes Santé/Banque/Avocat** ont la MFA activée (toujours `mfa_enabled = 0`)
- **0/8 tenants** créés (table `tenants` vide, 12/12 users `tenant_id = NULL`)
- **100% IPs placeholder** dans audit_logs (`testclient`×48, `127.0.0.1`×10, `None`×5)
- **Email invalide** `jame.callaghan@gmail:com` toujours non corrigé
- **Dernier log d'activité : 2026-05-31** (système dormant 53 jours)
- **Kill Switch TOUJOURS ARMÉ** — 0 remédiation exécutée par Tars entre 20/07 et 23/07

⚠️ **Aucune nouvelle veille** ce cycle (ArXiv 429). Le matériel commercial créé cycles précédents reste non activé (4 one-pagers + 2 templates).

---

## ✅ Exécutées ce cycle (2026-07-23)

| # | Action | Fichier créé/maj | Source |
|---|--------|------------------|--------|
| 1 | **Statut jour J+1 deadline CRITICAL** — 3e vérification DB lecture seule consécutive, constat : 0/5 actions remédiées en 72h, Kill Switch toujours armé, système dormant 53j | `docs/compliance/STATUT-DEADLINE-CRITICAL-2026-07-23.md` | Vérif DB directe (Python sqlite3, `?mode=ro`) |
| 2 | Mise à jour du présent fichier de suivi | `docs/ACTIONS-PRIORITAIRES.md` | Synthèse cycle |

---

## 🔁 Cycle 2026-07-22

**Inputs traités :** jobs nouveaux / mis à jour depuis cycle 21/07.

| Rapport | Job ID | Run | Statut | Output exploitable |
|---------|--------|-----|--------|--------------------|
| **ArXiv Daily 22/07** | `0f8a90201d56` | 22/07 11:36 | ✅ Succès (Apify) | 🆕 **NON INJECTÉ au prompt mais lu sur disque** — 5 papers R ≥ 10 dont 2 × R:12 (ChainMark watermarking + Engineering Trustworthy Agentic AI) |
| CNIL Sanction 21/07 | `7d92c44685ae` | 21/07 16:39 | ✅ `[SILENT]` nominal | ℹ️ Aucune sanction < 72h — job fonctionne correctement |
| daily-briefing 22/07 | `ed760e5da98e` | 22/07 11:25 | ❌ **ÉCHEC (8e jour)** | ⚠️ Drift config modèle — fix trivial non appliqué |
| rebooking-toiletteur 21/07 | `b2c3718fe9d0` | 21/07 16:11 | ❌ **ÉCHEC (7e jour)** | ⚠️ Même cause, même fix |

**Signaux nouveaux ce cycle (delta 21/07 → 22/07) :**

🔴 **DEADLINE CRITICAL DÉPASSÉE — vérification DB lecture seule :**
- Score global compliance : **0.30/1.00** — **inchangé depuis W29**
- **0/4 comptes Santé/Banque/Avocat** ont la MFA activée (toujours `mfa_enabled = 0`)
- **0/8 tenants** créés (table `tenants` vide, 12/12 users `tenant_id = NULL`)
- **100% IPs placeholder** dans audit_logs (`testclient`×48, `127.0.0.1`×10, `None`×5)
- **Email invalide** `jame.callaghan@gmail:com` toujours non corrigé
- **Dernier log d'activité : 2026-05-31** (système dormant 52 jours)
- **Kill Switch TOUJOURS ARMÉ** — aucune remédiation exécutée par Tars entre 21/07 et 22/07

🆕 **5 nouveaux papers R ≥ 10 (ArXiv 22/07) :**
- 2607.18445 (ChainMark, R:12) — watermarking LLM model-free, **opportunité produit AI Act Art. 50** (J-11)
- 2607.18548 (Engineering Trustworthy Agentic AI, R:12) — **cadre d'audit structurant**
- 2607.18847 (Data Leakage Prevention, R:11) — hardening agents contre prompt injection
- 2607.18243 (Risque résiduel quantifié, R:10) — framework CPSAINT/FRIESA-K
- 2607.19146 (Sarus HE, R:10) — privacy-by-design multi-vendor

---

## ✅ Exécutées ce cycle (2026-07-22)

| # | Action | Fichier créé/maj | Source |
|---|--------|------------------|--------|
| 1 | **Statut jour J deadline CRITICAL** — vérification lecture seule DB, constat : 0/5 actions remédiées, Kill Switch toujours armé | `docs/compliance/STATUT-DEADLINE-CRITICAL-2026-07-22.md` | Vérif DB directe |
| 2 | **One-pager commercial "Watermarking AI Act Art. 50"** prêt (5e offre) — angle ChainMark model-free, pricing 5-14k CHF, J-11 | `docs/strategie-2026-07/ONE-PAGER-WATERMARKING-IA-ART-50.md` | ArXiv 22/07 (2607.18445) |
| 3 | **TICKET-022** créé — Évaluer ChainMark comme socle watermarking (P1, J-11) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 22/07 |
| 4 | **TICKET-023** créé — Intégrer survey "Engineering Trustworthy Agentic AI" comme cadre d'audit (P1) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 22/07 |
| 5 | **TICKET-024** créé — Prévention proactive fuites de données agents (P1, R:11) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 22/07 |
| 6 | **TICKET-025** créé — Framework quantitatif risque résiduel CPSAINT/FRIESA-K (P2) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 22/07 |
| 7 | **TICKET-026** créé — Évaluer Sarus homomorphic encryption comme pattern privacy-by-design (P2) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 22/07 |
| 8 | **Matrice Threat Intel 22/07** consolidée — section 3.bis (5 papers, signal dominant + Safety Drift) | `docs/compliance/MATRICE-RISQUES-R1-R4.md` | ArXiv 22/07 |
| 9 | **Checklist compliance Phase 12** ajoutée (mesures watermarking, trustworthiness, hardening, monitoring continu) | `docs/compliance/CHECKLIST-COMPLIANCE-IA.md` | ArXiv 22/07 |
| 10 | Mise à jour du présent fichier de suivi | `docs/ACTIONS-PRIORITAIRES.md` | Synthèse cycle |

---

## ✅ Exécutées cycle précédent (2026-07-21)

| # | Action | Fichier créé/maj | Source |
|---|--------|------------------|--------|
| 1 | **Procédure de remédiation CRITICAL rédigée** — actions pas-à-pas pour Tars (3 alertes CRITICAL deadline 22/07 + 2 HIGH + checklist levée Kill Switch + effort estimé 6jh) | `docs/compliance/PROCEDURE-REMÉDIATION-CRITICAL-2026-07-21.md` | Compliance W29 |
| 2 | **AIPD Draft Santé** pré-rempli (Dr. Laurent, Hôpital de Genève) — déclencheur Art. 35 RGPD + AI Act high-risk | `docs/compliance/aipd/AIPD-DRAFT-SANTE-LAURENT-2026-07-21.md` | Compliance W29 Alerte #1 |
| 3 | **AIPD Draft Banque** pré-rempli (T. Müller, UBank SA) — secret bancaire Art. 47 LB | `docs/compliance/aipd/AIPD-DRAFT-BANQUE-UBANK-2026-07-21.md` | Compliance W29 Alerte #2 |
| 4 | **AIPD Draft Avocat** pré-rempli (P. Martin) — secret professionnel Art. 321 CP + cross-border CH→EU | `docs/compliance/aipd/AIPD-DRAFT-AVOCAT-MARTIN-2026-07-21.md` | Compliance W29 Alerte #3 |
| 5 | **TICKET-019** créé — Isolation multi-tenant absente (table `tenants` vide, 12/12 users NULL) — P1 préalable Kill Switch | `docs/TICKETS-TECHNIQUES-SECURITE.md` | Compliance W29 Alerte #4 |
| 6 | **TICKET-020** créé — Capturer IPs réelles (middleware FastAPI + SHA-256 hashing + anonymisation 13 mois) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | Compliance W29 Alerte #5 |
| 7 | **TICKET-021** créé — Évaluer "Zero Hallucination by Construction" (layered oversight, 2607.17883) comme pattern d'architecture | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 21/07 |
| 8 | **One-pager commercial "Audit Biais IA"** prêt — angle Value Leakage + AI Act Art. 50, pricing 6-25k CHF, 5 cibles FR-CH, J-12 | `docs/strategie-2026-07/ONE-PAGER-AUDIT-BIAIS-IA.md` | ArXiv 21/07 (2607.14345 + 2607.16903 + 2607.14782) |
| 9 | **Checklist compliance enrichie** — Phases 9 (Threat Intel 21/07), 10 (mesures Compliance W29), 11 (procédure violation <72h) | `docs/compliance/CHECKLIST-COMPLIANCE-IA.md` | ArXiv 21/07 + Compliance W29 |
| 10 | Mise à jour du présent fichier de suivi | `docs/ACTIONS-PRIORITAIRES.md` | Synthèse cycle |

---

## ✅ Exécutées cycle précédent (2026-07-20)

| # | Action | Fichier créé/maj | Source |
|---|--------|------------------|--------|
| 1 | **One-pager commercial "Certification IA Indépendante"** prêt (distinct de AI Red Team) — positionnement tierce-partie, périmètre 8 blocs AI Act+RGPD, pricing 5-20k CHF, 5 cibles FR-CH, pitch avocat J-13 | `docs/strategie-2026-07/ONE-PAGER-CERTIFICATION-IA-INDEPENDANTE.md` | ArXiv 20/07 (2607.15992 + 2607.16130 + 2503.01816) |
| 2 | **TICKET-016** créé — Cognitive Firewall zero-trust multi-gate (2607.01277, P1, 17/20) — architecture LLM safety au-delà du guardrail mono-gate actuel | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 20/07 |
| 3 | **TICKET-017** créé — Audit checkpoints LLM "abliterated" (2607.01854 + 2607.13162, P2) — pour PME déployant LLM open-source (Mistral/Llama/Qwen) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 20/07 |
| 4 | **TICKET-018** créé — Primitives "Stop Means Stop" (2607.14166, P1) — convergent avec TICKET-015 Permission UX | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 20/07 |
| 5 | Checklist compliance IA enrichie (7 nouvelles mesures Threat Intel 20/07) | `docs/compliance/CHECKLIST-COMPLIANCE-IA.md` | ArXiv 20/07 |
| 6 | Mise à jour du présent fichier de suivi | `docs/ACTIONS-PRIORITAIRES.md` | Synthèse cycle |

---

## ✅ Exécutées cycle précédent (2026-07-19)

| Rapport | Job ID | Run | Statut | Output exploitable |
|---------|--------|-----|--------|--------------------|
| ArXiv Daily Scan (delta weekend) | 0f8a90201d56 | 19/07 11:05 | ✅ Succès | ✅ Oui — 6 alertes manquées, 3 signaux stratégiques nouveaux |
| RAG Auto-Ingestion | b7ee11e86eb1 | 19/07 11:00 | ✅ Succès | ✅ `+6 ~979 err0 chunks=6503` — nominal |
| Rebooking Send | 1eb8d1919038 | 19/07 10:57 | ✅ Succès (dry-run) | ✅ 7 messages SIMULÉS, outbox conservé |
| Rebooking Toiletteur | b2c3718fe9d0 | 19/07 10:57 | ❌ **ÉCHEC** (drift config) | ⚠️ Toujours cassé — escalade technique ré-ouverte |
| Daily Briefing | ed760e5da98e | 19/07 10:57 | ❌ **ÉCHEC** (drift config) | ⚠️ Toujours cassé — escalade technique ré-ouverte |
| Alerte Sanction CNIL/PFPDT | 7d92c44685ae | 18/07 11:15 | ✅ `[SILENT]` | ✅ Aucune sanction détectée |
| Brief RGPD-IA Hebdo | 476112fc9e18 | 15/07 12:54 | ✅ Succès | ✅ Déjà traité cycle 18/07 |
| Weekly Report S28 | a7cbd0ff1c22 | 17/07 18:04 | ✅ Succès | ✅ Déjà traité cycle 18/07 |

**Note cycle :** ArXiv weekend = listings Fri 17/07 (réouverture Lundi 20/07). Le delta 19/07 a néanmoins capté 6 alertes + 3 signaux stratégiques nouveaux manqués par le scan complet 18/07. Le job ArXiv reste opérationnel via fallback Apify (web_search Hermes indispo — FIRECRAWL non configuré).

---

## ✅ Exécutées ce cycle (2026-07-19)

| # | Action | Fichier créé/maj | Source |
|---|--------|------------------|--------|
| 1 | **TICKET-013** créé — Politique formelle validation Skills (Agent Skill Security, 2607.13987, 17/20) — 4 vecteurs : squatting, poisoning, privilege escalation, cross-skill leakage | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 19/07 delta |
| 2 | **TICKET-014** créé — Évaluer 2607.14006 comme socle d'offre "AI Red Team" (42pp, 17/20) — opportunité produit différenciante | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 19/07 delta |
| 3 | **TICKET-015** créé — Aligner UX client + escalade Hermes avec Agent Permission UX (2607.13718, AI Act Art. 14) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv 19/07 delta |
| 4 | Checklist compliance IA enrichie (4 nouvelles mesures Threat Intel 19/07) | `docs/compliance/CHECKLIST-COMPLIANCE-IA.md` | ArXiv 19/07 delta |
| 5 | **One-pager commercial "AI Red Team"** prêt (positionnement, périmètre 7 attaques, pricing 8-35k CHF, 5 cibles FR-CH, argumentaire 3 phrases) | `docs/strategie-2026-07/ONE-PAGER-AI-RED-TEAM.md` | ArXiv 19/07 delta, signal #2 convergent |
| 6 | Mise à jour du présent fichier de suivi | `docs/ACTIONS-PRIORITAIRES.md` | Synthèse cycle |

---

## ✅ Exécutées cycle précédent (2026-07-18)

| # | Action | Fichier | Source |
|---|--------|---------|--------|
| 1 | TICKET-009 créé — Traccia, socle observabilité IA OpenTelemetry (P1, 20/20) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv Daily 18/07 |
| 2 | TICKET-010 créé — Bad Memory + MemPoison, audit mémoire persistante (P0) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv Daily 18/07 |
| 3 | TICKET-011 créé — FlowGuard, sécurité runtime MCP (P1) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv Daily 18/07 |
| 4 | TICKET-012 créé — Politique supply-chain skills externes (P2) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv Daily 18/07 |
| 5 | Matrice Threat Intel cycle 18/07 consolidée | `docs/compliance/MATRICE-THREAT-INTEL-2026-07-18.md` | ArXiv Daily 18/07 |
| 6 | Checklist compliance IA enrichie (5 mesures Threat Intel 18/07) | `docs/compliance/CHECKLIST-COMPLIANCE-IA.md` | ArXiv Daily 18/07 |
| 7 | Template cold outreach CNIL prêt (2 angles A/B testables) | `docs/strategie-2026-07/TEMPLATE-OUTREACH-CNIL-SANCTIONS.md` | Weekly Report S28 |
| 8 | Template témoignage client Hayal Grill prêt | `docs/strategie-2026-07/TEMOIGNAGE-CLIENT-HAYAL-GRILL.md` | Weekly Report S28 |

---

## ✅ Exécutées cycle 2026-07-17

| # | Action | Fichier | Source |
|---|--------|---------|--------|
| 1 | One-pager commercial "AI Act 2 août 2026" prêt à envoyer | `docs/compliance/ONE-PAGER-AI-ACT-2-AOUT-2026.md` | Weekly Report + Brief RGPD-IA 15/07 |
| 2 | TICKET-006 créé — hash journal WORM cassé (P1, blocker audit) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | Weekly Report 10/07 |
| 3 | TICKET-007 créé — robustesse jailbreak modèles quantifiés (JADR) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv Daily 15/07 |
| 4 | TICKET-008 créé — audit registre skills (skills hallucinées) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv Daily 15/07 |

---

## ✅ Exécutées cycle 2026-07-14

| # | Action | Fichier | Source |
|---|--------|---------|--------|
| 1 | Matrice de risques R1-R4 formalisée | `docs/compliance/MATRICE-RISQUES-R1-R4.md` | Skill le-gardien-des-normes |
| 2 | Veille Threat Intel consolidée (4 menaces) | `docs/strategie-2026-07/VEILLE-THREAT-INTEL-2026-07-14.md` | ArXiv Daily 14/07 |
| 3 | 5 tickets techniques créés (TICKET-001 à 005) | `docs/TICKETS-TECHNIQUES-SECURITE.md` | ArXiv Daily + Weekly Report |
| 4 | Checklist compliance IA 8 phases | `docs/compliance/CHECKLIST-COMPLIANCE-IA.md` | Skill le-gardien-des-normes |

---

## 🟡 Escalade technique (Tars)

| Priorité | Ticket | Action | Contexte | Statut |
|---|----------|--------|--------|----------|--------|
| **P0** | **🚨 Compliance W29 — DEADLINE DÉPASSÉE J+5 (26/07)** | **Exécuter la procédure de remédiation CRITICAL** (`PROCEDURE-REMÉDIATION-CRITICAL-2026-07-21.md`). Vérification DB 26/07 : **0/5 actions remédiées en 144h+**. MFA toujours absente sur 4 comptes Santé/Banque/Avocat, tenants vides, IPs placeholder, email invalide. ~5h de travail. Voir `STATUT-DEADLINE-CRITICAL-2026-07-26.md` | Compliance W29 (`0dc376b91586`) 20/07 12:06 | 🔴 **DÉPASSÉ J+5 — URGENCE CRITIQUE ACCUMULATIVE (6e point de contrôle, J-7 AI Act)** |
| **P0** | **ArXiv Daily 429 récurrent (résolu ce cycle)** | Le scan ArXiv 23/07 a échoué (HTTP 429), mais **le rapport 25/07 a compensé** via delta complet `show=1000`. Vérifier si la pagination doit être standardisée à `show=1000` pour éviter les angles morts (64% de signaux manqués avec `show=50`) | ArXiv 23/07 → 25/07 (`0f8a90201d56`) | 🟢 **Résolu ce cycle — mais config pagination à valider** |
| **P1** | **—** | **Réparer `daily-briefing` (job ed760e5da98e)** — drift config modèle. Une commande: `hermes cron update ed760e5da98e provider=zai model=glm-5.2` | Weekly Report S28 §2 | ❌ **ÉCHEC 11e jour consécutif** |
| **P1** | **—** | **Réparer `rebooking-toiletteur` (job b2c3718fe9d0)** — même cause, même fix | Weekly Report S28 §2 | ❌ **ÉCHEC 10e jour consécutif** |
| **P1** | **🆕 TICKET-027** | **Sécuriser les agents auto-hébergés** (cluster Chronos + Self-State + CI/CD, 4 papers R≥8) — runtime agent on-prem, exposition directe Santé/Banque/Avocat | ArXiv 25/07 | 🟠 Nouveau 25/07 — vecteur critique émergent |
| **P1** | **🆕 TICKET-028** | Adopter AI SBOM (SPDX/CycloneDX IA, Art. 11/13) — générer SBOM interne + template client | ArXiv 25/07 (2607.17242) | 🟠 Nouveau 25/07 — convergent TICKET-022/027 |
| **P0** | **TICKET-010** | **Auditer la mémoire persistante Hermes contre Bad Memory / MemPoison (1227 cas documentés)** — impact direct sur la stack | ArXiv 18/07, 2607.14611 + 2607.14651 | 🔴 Toujours ouvert |
| **P1** | **TICKET-019** | **Isolation multi-tenant absente** — table `tenants` vide (vérifié 22/07), 12/12 users `tenant_id=NULL`. Créer 8 tenants + assigner + tester isolation. Préalable à la levée Kill Switch | Compliance W29 Alerte #4 | 🔴 Inchangé 22/07 — deadline 03/08 |
| **P1** | **TICKET-020** | **Capturer IPs réelles dans audit_logs** — vérifié 22/07 : 100% placeholders (`testclient`×48). Middleware FastAPI + SHA-256 hashing + anonymisation 13 mois | Compliance W29 Alerte #5 | 🔴 Inchangé 22/07 — deadline 03/08 |
| **P1** | **🆕 TICKET-022** | Évaluer ChainMark (2607.18445) comme socle watermarking AI Act Art. 50 — J-11 avant 2 août | ArXiv 22/07 | 🟠 Nouveau 22/07 — opportunité produit |
| **P1** | **🆕 TICKET-023** | Intégrer survey "Engineering Trustworthy Agentic AI" (2607.18548) comme cadre d'audit (5 dimensions) | ArXiv 22/07 | 🟠 Nouveau 22/07 — différenciateur méthodologique |
| **P1** | **🆕 TICKET-024** | Prévention proactive des fuites de données agents (2607.18847, R:11) | ArXiv 22/07 | 🟠 Nouveau 22/07 — Art. 32 RGPD |
| **P2** | **TICKET-021** | Évaluer "Zero Hallucination by Construction" (2607.17883) comme pattern d'architecture | ArXiv 21/07 | Ouvert 21/07 |
| **P1** | **TICKET-016** | Évaluer Cognitive Firewall (zero-trust multi-gate) pour les agents en production | ArXiv 20/07, 2607.01277 | Ouvert 20/07 |
| **P1** | **TICKET-018** | Durcir primitives "Stop Means Stop" (objectif arrêt < 5s pour R3/R4) | ArXiv 20/07, 2607.14166 | Ouvert 20/07 |
| **P1** | TICKET-013 | Formaliser la politique de validation Skills (anti-squatting + sandbox + revue) | ArXiv 19/07, 2607.13987 | Ouvert 19/07 |
| **P1** | TICKET-015 | Aligner UX client + mécanisme d'escalade Hermes avec Agent Permission UX (AI Act Art. 14) | ArXiv 19/07, 2607.13718 | Ouvert 19/07 |
| **P1** | TICKET-009 | Évaluer Traccia (OpenTelemetry) comme socle d'observabilité agent IA — 20/20 | ArXiv 18/07, 2607.14309 | Ouvert 18/07 |
| **P1** | TICKET-011 | Tester FlowGuard sur serveurs MCP Apify/n8n (validation runtime) | ArXiv 18/07, 2607.14754 | Ouvert 18/07 |
| **P1** | TICKET-006 | Corriger le hash journal WORM cassé (ligne 9) — blocker audit | Weekly Report 10/07 §2 | Ouvert 17/07 |
| **P1** | TICKET-001 | Durcir les pipelines vision contre les attaques adversariales (VLAs) | ArXiv 2607.11560 | Ouvert 14/07 |
| **P1** | TICKET-002 | Intégrer le red-teaming d'agents en production | ArXiv 2607.11698 | Ouvert 14/07 |
| **P2** | **🆕 TICKET-029** | Évaluer RAIL Guard comme socle boucle évaluation→remédiation (2607.16215) — remède au gap interne (deadline CRITICAL non exécutée) | ArXiv 25/07 | 🟡 Nouveau 25/07 — opportunité méthodologique |
| **P2** | **🆕 TICKET-025** | Adopter framework quantitatif risque résiduel CPSAINT/FRIESA-K (2607.18243) | ArXiv 22/07 | Ouvert 22/07 |
| **P2** | **🆕 TICKET-026** | Évaluer Sarus homomorphic encryption comme pattern privacy-by-design (2607.19146) | ArXiv 22/07 | Ouvert 22/07 |
| **P2** | **TICKET-017** | Auditer checkpoints LLM "abliterated" (refus retirés) — Mistral/Llama/Qwen | ArXiv 20/07, 2607.01854 + 2607.13162 | Ouvert 20/07 |
| **P2** | TICKET-014 | Évaluer 2607.14006 comme socle d'offre "AI Red Team" | ArXiv 19/07, 2607.14006 | Ouvert 19/07 |
| **P2** | TICKET-012 | Politique supply-chain pour skills externes | ArXiv 18/07, 2607.15143 | Ouvert 18/07 |
| **P2** | TICKET-003 | Vérifier l'intégrité multi-agents (backdoors distribués) | ArXiv 2607.11751 | Ouvert 14/07 |
| **P2** | TICKET-004 | Déployer le dashboard compliance React | Weekly Report + BUSINESS-CASE-v2 | Ouvert 14/07 |
| **P2** | TICKET-005 | Améliorer l'explainability des décisions d'anomalie | ArXiv 2607.11862 + AI Act Art. 13 | Ouvert 14/07 |
| **P2** | TICKET-007 | Tester la robustesse jailbreak des modèles quantifiés (JADR) | ArXiv 2607.12792 | Ouvert 17/07 |
| **P2** | TICKET-008 | Auditer le registre de skills Hermes (skills hallucinées) | ArXiv 2607.12340 | Ouvert 17/07 |

---

## 🔴 Escalade humaine (Thierry)

| Priorité | Action | Contexte | Statut |
|----------|--------|----------|--------|
| **🔴 HAUTE — URGENTE** | **🆕 Valider le one-pager "Droit à l'Oubli IA Équitable"** créé ce cycle (26/07) — 8e offre, cluster Machine Unlearning Equity (4 papers R:8 ArXiv 07/2026), pricing 4.5-18k CHF, 5 cibles (assurances, hôpitaux, banques, RH tech, legaltech). Angle inédit : le droit à l'oubli IA peut déclencher une discrimination involontaire (Art. 9 RGPD). Décision : standalone ou module de l'Audit Biais IA ? | ArXiv 26/07 (cluster equity/unlearning) | 🆕 Nouveau 26/07 |
| **🔴 HAUTE — URGENTE** | **🆕 Décision Kill Switch / reprise activité** — le rapport W29 révèle score global 0.30 (CRITIQUE), 3 alertes CRITICAL avec deadline 22/07 (**dépassée J+5**), Kill Switch ARMÉ. Le système est dormant (0 activité 56j). Décisions à prendre : (1) valider l'exécution de la procédure de remédiation par Tars (6jh), (2) décider si la reprise d'activité est prioritaire vs la prospection commerciale, (3) arbitrer la communication aux 3 clients concernés (Dr. Laurent, T. Müller, P. Martin) | Compliance W29 | 🔴 **DÉCISION BLOQUANTE — 6e escalade consécutive** |
| **Haute** | **🆕 Valider le one-pager "Self-Hosted Agent Security"** créé ce cycle (25/07) — 7e offre, angle runtime agent on-prem, pricing 10-40k CHF, J-8. Distincte des 6 offres précédentes, cible les PME avec déploiement on-prem (Santé/Banque/Avocat/Administration). Décision : standalone, bundle, ou module de la Certification IA ? | ArXiv 25/07 (cluster self-hosted, 4 papers R≥8) | 🆕 Nouveau 25/07 |
| **Haute** | **Valider le one-pager "Audit Biais IA"** créé 21/07 — angle Value Leakage + AI Act Art. 50, pricing 6-25k CHF. Distinct des 3 one-pagers précédents. 4 offres Cortex Leman désormais prêtes (AI Act 2 août, Certification IA, AI Red Team, Audit Biais). Décision : standalone, bundle, ou suite cohérente ? | ArXiv 21/07 (2607.14345 + 2607.14782 + 2607.16903) | Ouvert 21/07 |
| **Haute** | **Valider le one-pager "Certification IA Indépendante"** créé 20/07 — offre tierce-partie AI Act, pricing 5-20k CHF. Fenêtre J-12 (avant 2 août) | ArXiv 20/07 (2607.15992 + 2607.16130) | Ouvert 20/07 |
| **Haute** | **Déclencher le premier outreach** — 20 prospects cette semaine, utiliser `TEMPLATE-OUTREACH-CNIL-SANCTIONS.md` (2 angles A/B). Le matériel est prêt | Weekly Report S28 action Top 3 #2 | Récurrent — matériel prêt depuis 18/07 |
| **Haute** | **Formaliser le témoignage Hayal Grill** — template `TEMOIGNAGE-CLIENT-HAYAL-GRILL.md` à remplir. Obtenir citation + 2 captures | Weekly Report S28 action Top 3 #3 | Récurrent — matériel prêt depuis 18/07 |
| **Haute** | **Valider et envoyer le one-pager "AI Act 2 août"** à 10 cabinets FR-CH. **J-12 aujourd'hui** | One-pager créé 17/07 | Récurrent — J-12 |
| **Haute** | **Valider le one-pager "AI Red Team"** créé 19/07 — positionnement, pricing 8-35k CHF, 5 cibles FR-CH | ArXiv 19/07, one-pager créé 19/07 | Ouvert 19/07 |
| **Haute** | **Téléphoner à 20 décideurs réels** (cabinets d'avocats genevois, fiducies lausannoises, PME santé vaudoises) | Weekly Report 10/07 action Top 3 #1 | Récurrent — non démarré |
| **Moyenne** | Valider stratégiquement les menaces IA émergentes (21 tickets ouverts) — prioriser lesquelles adresser d'abord | ArXiv Daily 14→21/07 | Récurrent |

---

## 📊 Notes sur la qualité des rapports injectés

**Cycle 25/07 — veille rétablie (delta `show=1000`), 3 nouveaux clusters identifiés, deadline CRITICAL en aggravation J+3.**

**Inputs traités ce 25/07 :**
- ✅ **ArXiv Daily 25/07 = succès** — rapport delta week-end complet (`show=1000`) qui compense l'échec 23/07 (429) et révèle que la pagination `show=50` des cycles précédents manquait ~64% des signaux sur cs.AI/CV/LG. 7 papiers R≥10 dont 4 nouveaux, 3 clusters émergents.
- ✅ **CNIL Sanction 25/07 = `[SILENT]`** — comportement nominal (aucune sanction < 72h).
- ℹ️ Brief RGPD-IA Hebdo (15/07) et Weekly Report S28 : déjà traités.

**🔴 Signal dominant ce cycle : la deadline CRITICAL s'aggrave (J+3) pendant que la veille s'accélère.** 4e point de contrôle DB lecture seule consécutif (20→22→23→25/07) : **0 des 5 actions de remédiation exécutées en 120h+**. La base est strictement figée depuis 5 jours. Le Kill Switch reste armé. La fenêtre de remédiation avant AI Act 2 août (**J-8**) se referme.

**Signaux critiques consolidés :**
1. **Score compliance 0.30 (CRITIQUE)** — inchangé depuis W29 (5e point de contrôle). Risque reputational majeur : on ne peut pas vendre un audit compliance avec un score interne de 0.30.
2. **Kill Switch ARMÉ (J+3)** — en l'état, toute reprise d'activité reste interdite par la politique du Gardien.
3. **Deadline CRITICAL dépassée depuis 22/07 (72h+)** — manquement RGPD Art. 32/9 actif et non résolu, risque juridique accumulatif quotidien.
4. **Système dormant** (55 jours, dernier login admin 31/05) — réduit le risque opérationnel immédiat mais pas le risque juridique.

**🟢 Nouveau ce cycle — la veille ArXiv a produit un signal商业 fort :**
- **Cluster "self-hosted agent security"** (4 papers R≥8) → one-pager N°7 créé (Self-Hosted Agent Security Audit). C'est un angle mort du marché FR-CH : les DPO et RSSI classiques ne savent pas auditer le runtime agent IA on-prem.
- **AI SBOM** (Art. 11/13) → TICKET-028, livrable standard futur des audits.
- **RAIL Guard** (boucle évaluation→remédiation) → TICKET-029, remède direct au gap interne.

**⚠️ Points de blocage technique persistants :**
1. **`daily-briefing` (11e jour) + `rebooking-toiletteur` (10e jour) cassés** — drift config modèle. Fix trivial : 1 commande par job.
2. **`web_search` Hermes indisponible** (FIRECRAWL non configuré) — le fallback Apify RAG a fonctionné ce cycle, mais la pagination `show=50` par défaut manquait 64% des signaux. **Recommandation : standardiser `show=1000` dans le prompt du job ArXiv.**

**Diagnostic commercial consolidé :** la pile de matériel commercial prêt-à-envoyer s'étoffe (7 one-pagers) mais reste non activée :

| One-pager | Créé | Statut |
|-----------|------|--------|
| `ONE-PAGER-AI-ACT-2-AOUT-2026.md` | 17/07 | À envoyer (J-8) |
| `TEMPLATE-OUTREACH-CNIL-SANCTIONS.md` | 18/07 | À utiliser |
| `TEMOIGNAGE-CLIENT-HAYAL-GRILL.md` | 18/07 | À remplir |
| `ONE-PAGER-AI-RED-TEAM.md` | 19/07 | À valider |
| `ONE-PAGER-CERTIFICATION-IA-INDEPENDANTE.md` | 20/07 | À valider |
| `ONE-PAGER-AUDIT-BIAIS-IA.md` | 21/07 | À valider |
| `ONE-PAGER-WATERMARKING-IA-ART-50.md` | 22/07 | À valider |
| **🆕 `ONE-PAGER-SELF-HOSTED-AGENT-SECURITY.md`** | **25/07** | **À valider** |

**Le paradoxe persistant (J-8) :** la veille a produit 7 one-pagers commerciaux différenciés, MAIS le score compliance interne reste à 0.30 et la deadline CRITICAL est dépassée de 3 jours. **Il faut résoudre le gap interne avant de vendre de l'audit compliance — sinon l'argumentaire est vide.** Le rapport ArXiv 25/07 le confirme lui-même : *A Critical Analysis of Trustworthy AI Tools* (2607.15480) trouve que la majorité des outils compliance ne couvrent pas les exigences réglementaires — notre cas interne en est l'illustration.

**J-8 avant AI Act 2 août** — fenêtre commerciale ET fenêtre de remédiation interne se referment simultanément.

---

## 📜 Historique des cycles

- **26/07** — Synthèse ArXiv hebdo (consolidation Mon-Fri + 1 nouveau cluster equity/unlearning). 5e vérification DB : deadline CRITICAL **J+5**, 0/5 remédiées en 144h+, Kill Switch armé, système dormant 56j. One-pager N°8 (Droit à l'Oubli IA Équitable) + argumentaire académique ArXiv juillet créés.
- **25/07** — Veille rétablie (delta `show=1000`, 7 papers R≥10, 3 clusters émergents). 4e vérification DB : deadline CRITICAL J+3, 0/5 remédiées en 120h+, Kill Switch armé, système dormant 55j. 3 tickets (027/028/029) + one-pager N°7 (Self-Hosted Agent Security) créés.
- **23/07** — Veille interrompue (ArXiv 429). 3e vérification DB : deadline CRITICAL J+1, 0/5 remédiées, Kill Switch armé. Statut J+1 créé.
- **22/07** — ArXiv 22/07 traité (5 papers R≥10 dont ChainMark watermarking). 2e vérification DB : jour J, 0/5 remédiées. 5 tickets + one-pager watermarking créés.
- **21/07** — Compliance W29 traité (3 alertes CRITICAL deadline 22/07). Procédure remédiation + 3 AIPD drafts + one-pager Audit Biais créés.
- **20/07** — ArXiv 20/07 traité. One-pager Certification IA + 3 tickets créés.
- **19/07** — ArXiv delta weekend. One-pager AI Red Team + 3 tickets créés.
- **18/07** — ArXiv 18/07 traité. Template outreach CNIL + témoignage Hayal Grill créés.
- **17/07** — One-pager AI Act 2 août créé.
