# Analyse Concurrentielle : Credo AI · Scytale · Deel
## Patterns à inspirer pour Cortex Leman v5 — Excellence by Design

---

## 1. CREDO AI — ⭐⭐⭐⭐⭐ Le leader AI Governance

**Positionnement** : Plateforme de gouvernance IA pour Fortune 500
**Clients** : Grandes entreprises, Forrester Leader 2025, cité par Gartner
**Message clé** : *"Govern AI Everywhere"* · *"Measurable Trust at Scale"*

### Ce qu'ils font d'EXCEPTIONNEL

| Pattern | Description | Adaptation Cortex Leman |
|---------|-------------|------------------------|
| **Governance Knowledge Graph** | Graphe de connaissances reliant modèles, risques, policies, regulations | Notre Graphe de Confiance est DÉJÀ ce pattern. Mais Credo le visualise |
| **AI Registry & Discovery** | Catalogue automatique de TOUS les systèmes IA (agents, modèles, apps) | Ajouter un onglet "Registre IA" dans le dashboard |
| **Runtime Governance** | Gouvernance en temps réel pendant l'exécution des agents | Notre Médiateur le fait — mais il faut le MONTRER visuellement |
| **Pre-Built Policy Packs** | Packs de conformité prêts à déployer (EU AI Act, NIST, ISO 42001, SOC 2) | Nos rules/*.json = policy packs. Les rendre visibles + téléchargeables |
| **Multi-Layer Governance** | Gouvernance modèle + agent + application en une seule plateforme | Notre stack 5 agents = exactement ça. Le documenter visuellement |
| **Continuous, Not Point-in-Time** | Monitoring continu, pas des audits ponctuels | Notre journal WORM + compliance gateway = continu. Montrer le flux temps réel |
| **Audit-Ready Documentation** | Génération automatique de docs prêtes pour audit | Ajouter export PDF/CSV du journal + compliance reports |
| **Risk Intelligence Dashboard** | Évaluation continue des risques biais, sécurité, privacy | Ajouter un score de risque par vertical dans le dashboard |

### Leur UX remarquable
- **3 phases visuelles** : Discover & Register → Assess & Deploy → Monitor & Respond
- Chaque phase a ses propres métriques et widgets
- Les frameworks réglementaires sont affichés comme des badges actifs (EU AI Act ✓, ISO 42001 ✓)
- Les risques sont classifiés par sévérité avec code couleur

---

## 2. SCYTALE.AI — ⭐⭐⭐⭐⭐ Le meilleur UX GRC du marché

**Positionnement** : Hub de conformité IA pour startups → enterprises
**Clients** : 1000+ entreprises, G2 Leader GRC 2026, AWS Partner of the Year
**Message clé** : *"Compliance that never clocks out"*

### Ce qu'ils font d'EXCEPTIONNEL

| Pattern | Description | Adaptation Cortex Leman |
|---------|-------------|------------------------|
| **Multi-Agent Suite** | 5 agents spécialisés : Gap Scanner, Evidence Reviewer, Governance Engine, Security Responder, Vendor Intel | Notre 5 agents correspond. Mais Scytale les montre comme une "suite" avec avatars |
| **Staged Pricing** | 3 niveaux clairs : Build Starter → Build DFY → Build Stronger | Créer 3 plans : Starter (1 vertical) → Pro (3 verticals) → Enterprise (all + on-premise) |
| **Compliance Intelligence Engine** | "Le tissu entre votre infrastructure et chaque framework" | Notre Médiateur = ce tissu. Appeler ça "Compliance Intelligence" |
| **Gap Scanner & Remediator** | Scan continu des lacunes de conformité + suggestions de remediation | Ajouter un endpoint `/api/v1/compliance/gap-scan` qui retourne les écarts |
| **Trust Center public** | Page publique de confiance montrant certifications et statut | Ajouter une page publique `/trust-center` avec statut conformité |
| **Framework Gallery** | 60+ frameworks affichés comme une galerie (SOC 2, ISO 27001, GDPR, HIPAA...) | Créer une vue "Frameworks" avec nos verticals + frameworks applicables |
| **AI Security Questionnaires** | Remplissage automatique des questionnaires de sécurité | Ajouter un endpoint de génération automatique |
| **Continuous Compliance Badge** | Badge live "Currently Compliant" qu'on peut embed | API publique `/api/v1/public/compliance-status` |

### Leur UX remarquable
- **Onboarding par stage** : Startup / Growth / Enterprise — chaque stage a son propre flow
- **"How it works" en 3 étapes** : Connect your stack → AI scans and collects → Continuous compliance
- **Dashboard avec signaux** : Les gaps sont des "signals" avec sévérité, pas des erreurs
- **Dark mode par défaut** avec code couleur (rouge = gap, vert = compliant, jaune = in progress)

---

## 3. DEEL.COM — ⭐⭐⭐⭐⭐ L'expérience utilisateur de référence

**Positionnement** : Plateforme globale RH/Paie, "Hire, manage, pay anyone anywhere"
**Clients** : 10000+ entreprises, valorisation $12B
**Message clé** : *"Everything included"* · *"Built-in compliance"*

### Ce qu'ils font d'EXCEPTIONNEL

| Pattern | Description | Adaptation Cortex Leman |
|---------|-------------|------------------------|
| **Built-in Compliance** | La conformité est INVISIBLE — elle juste fonctionne en arrière-plan | Notre Médiateur doit être ressenti comme "ça juste marche" |
| **One Modern Experience** | Interface unifiée : pas de modes séparés, tout est intégré | Dashboard unifié avec sidebar — on l'a. Renforcer l'intégration |
| **Workflow Automation** | "Workflows you can build in minutes" | Ajouter un builder de workflows de conformité (no-code) |
| **AI Assistant** | "Meet your new legal and HR assistant" intégré dans la plateforme | Notre Chat Agent = exactement ça. Le rendre plus pro-actif |
| **G2 Leader Badge** | Preuve sociale omniprésente (4.8/5, 5687+ reviews) | Ajouter badges de conformité (RGPD ✓, AI Act ✓, ISO 42001 ✓) |
| **Customer Stories** | Témoignages clients avec cas d'usage précis | Ajouter des témoignages par vertical dans la landing page |
| **Pricing transparent** | Plans clairs avec features visibles | Pricing visible sur la landing page |
| **Never Miss Regulatory Changes** | Alertes automatiques sur les changements réglementaires | Notre ArXiv pipeline + apply_to_cortex = ce pattern. L'exploiter |

### Leur UX remarquable
- **Onboarding en 60 secondes** : Email → Dashboard → Action
- **Empty states utiles** : Chaque vue vide a des suggestions d'actions concrètes
- **Feedback instantané** : Toast notifications pour chaque action
- **CTAs contextuels** : Le bouton d'action change selon le contexte
- **International by default** : Le multi-pays n'est pas une option, c'est le standard

---

## 4. SYNTHÈSE — Les 12 Patterns à Implémenter

### P0 — Ce qui nous différencie (cette semaine)

| # | Pattern inspiré de | Implémentation Cortex Leman | Effort |
|---|-------------------|----------------------------|--------|
| 1 | **Credo AI** | **Registre IA** — Vue listant tous les agents, leur statut, modèle utilisé, score de risque | 1j |
| 2 | **Scytale** | **Compliance Score Widget** — Score global avec décomposition par framework (RGPD, AI Act, LPD) | 4h |
| 3 | **Scytale** | **Gap Scanner** — Endpoint + vue listant les écarts de conformité avec suggestions | 1j |
| 4 | **Deel** | **Toast Notifications** — Feedback visuel instantané après chaque action | 4h |
| 5 | **Credo AI** | **Pipeline visuel animé** — Le flow Intention → Médiateur → Agent → Guardrails → Journal en temps réel sur le dashboard | 4h |

### P1 — Ce qui nous amène au niveau enterprise

| # | Pattern inspiré de | Implémentation Cortex Leman | Effort |
|---|-------------------|----------------------------|--------|
| 6 | **Scytale** | **Trust Center public** — Page publique `/trust-center` montrant statut conformité | 1j |
| 7 | **Credo AI** | **Audit-Ready Export** — Export PDF/CSV du journal + rapports de conformité | 1j |
| 8 | **Scytale** | **3 plans de pricing** — Starter (1 vertical) / Pro (3 verticals) / Enterprise (all + on-premise) | 4h |
| 9 | **Deel** | **Regulatory Change Alerts** — Notifications automatiques quand le ArXiv pipeline détecte un changement | 4h |

### P2 — Ce qui nous met au-dessus de tous

| # | Pattern inspiré de | Implémentation Cortex Leman | Effort |
|---|-------------------|----------------------------|--------|
| 10 | **Credo AI** | **Risk Intelligence Dashboard** — Heat map des risques par vertical, modèle, agent | 2j |
| 11 | **Scytale** | **AI Questionnaire Auto-fill** — Remplissage automatique des questionnaires de sécurité | 2j |
| 12 | **Deel** | **Workflow Builder** — Interface no-code pour créer des workflows de conformité | 1sem |

---

## 5. LE MOAT UNIQUE DE CORTEX LEMAN

Ce qu'**AUCUN** des trois n'a :

| Notre avantage | Pourquoi c'est un moat |
|----------------|----------------------|
| **Médiateur déterministe (JsonLogic)** | Credo AI a du runtime governance mais pas de médiateur explicite. Scytale n'en a pas du tout |
| **Journal WORM hash-chainé** | Scytale a de l'audit trail mais pas immuable. Credo AI a du monitoring mais pas WORM |
| **Arbitrage humain avec précédents** | Personne ne fait ça. Credo AI a des "human-in-the-loop" mais pas de système de précédents |
| **Verticalisation FR-CH** | Deel est global mais pas verticalisé. Credo AI est horizontal. Personne ne fait FR-CH régulé |
| **AutoDefense multi-agent (3 validateurs)** | Pattern unique — 3 agents qui votent sur chaque output |
| **Graphe de Confiance 5 agents** | Credo AI a une "Governance Knowledge Graph" mais pas une architecture 5 agents pair-à-pair |

### Positionnement concurrentiel

```
                    AI Governance
                         ↑
                  Credo AI ●
                         |
       GRC/Compliance    |     AI Agent Platform
             ←───────────┼───────────→
                  Scytale●              ● Deel
                         |
                         |
                   Cortex Leman ● ← Unique: Compliance-First AI Trust
                         |           avec Arbitrage Humain
                    FR-CH Régulé
```

**Cortex Leman est le seul à être simultanément** :
- 🤖 AI Agent Platform (comme Deel)
- 🛡️ AI Governance (comme Credo AI)
- 📋 GRC Automatisé (comme Scytale)
- 🇫🇷🇨🇭 Spécialisé FR-CH régulé (personne)

---

## 6. FEUILLE DE ROUTE EXCELLENCE

### Sprint 1 (cette semaine) — "Trust Layer Visible"
- [ ] Registre IA (inspiré Credo AI)
- [ ] Compliance Score Widget (inspiré Scytale)
- [ ] Toast Notifications (inspiré Deel)
- [ ] Pipeline visuel animé temps réel
- [ ] Gap Scanner basique

### Sprint 2 (semaine suivante) — "Enterprise Ready"
- [ ] Trust Center public
- [ ] Audit-Ready Export (PDF/CSV)
- [ ] Pricing page avec 3 plans
- [ ] Regulatory Change Alerts
- [ ] Framework Gallery (RGPD, AI Act, LPD, ISO 42001)

### Sprint 3 (mois suivant) — "Above All"
- [ ] Risk Intelligence Dashboard avec heat map
- [ ] AI Questionnaire Auto-fill
- [ ] Workflow Builder no-code
- [ ] API publique pour intégrations
- [ ] Certification ISO 42001 du système lui-même
