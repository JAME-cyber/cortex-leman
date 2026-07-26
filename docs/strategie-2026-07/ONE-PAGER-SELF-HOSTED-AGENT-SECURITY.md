# ONE-PAGER — Offre "Self-Hosted Agent Security"

> **Date:** 2026-07-25
> **Auteur:** Le Gardien des Normes (Cortex Leman)
> **Destinataire:** Thierry (validation commerciale) + Le Narrateur (mise en forme)
> **Statut:** Draft — en attente de validation Thierry
> **Source veille:** ArXiv Daily 25/07 (`0f8a90201d56`) — cluster émergent "self-hosted agent security" (4 papiers R≥8 en 5 jours)
> **Positionnement:** Offre N°7 — distincte des 6 offres existantes (AI Act 2 août, Certification IA, AI Red Team, Audit Biais, Watermarking, Audit RGPD classique)

---

## 💡 Le constat — un angle mort stratégique du marché FR-CH

**Les PME FR-CH qui déploient des agents IA en on-prem (pour souveraineté des données Art. 9) sont exposées à une nouvelle classe de menaces que les DPO et cabinets RGPD classiques ne savent pas détecter.**

4 papiers ArXiv publiés en 5 jours (20-24/07/2026) révèlent que **les défenses OS traditionnelles sont insuffisantes pour les agents IA auto-hébergés** :

| arXiv | Apport | Score |
|-------|--------|-------|
| [2607.19433](https://arxiv.org/abs/2607.19433) | **Chronos Vulnerability** — persistance temporelle : payload dormant dans la mémoire long-terme, invisible à l'audit, déclenchable ultérieurement | 9/20 |
| [2607.17986](https://arxiv.org/abs/2607.17986) | **Self-State Attacks** — compromission du runtime agent (variables, contexte, call stack), contourne les sandbox OS classiques | 9/20 |
| [2607.18063](https://arxiv.org/abs/2607.18063) | **Adaptive Adversaries** — benchmark attaques multi-tours multi-LLM, les agents apprennent à contourner les guardrails statiques | 9/20 |
| [2607.19267](https://arxiv.org/abs/2607.19267) | **CI/CD as Attack Surface** — détournement des pipelines de build : code malveillant validé par les tests mais actif en prod | 9/20 |

**Traduction marché :** un DPO classique audite la conformité documentaire. Un RSSI classique audite le périmètre OS/réseau. **Personne n'audite le runtime de l'agent IA lui-même** — c'est le gap que Cortex Leman comble.

---

## 🎯 L'offre Cortex Leman — "Self-Hosted Agent Security Audit"

**Positionnement :** audit technique spécialisé pour les agents IA déployés en on-prem / cloud privé / souveraineté. On ne valide pas la conformité papier — on **exécute les vecteurs d'attaque documentés** contre le runtime agent en production pour mesurer l'exposition réelle.

### Pourquoi cette offre est distincte des 6 existantes

| Offre | Angle | Recouvrement |
|-------|-------|--------------|
| AI Act 2 août | Conformité réglementaire deadline | ✗ Papier, pas technique |
| Certification IA Indépendante | Tierce partie, 8 blocs | ✗ Macro, pas runtime agent |
| AI Red Team | 7 attaques sur agents cloud | ⚠️ Partiel — pas focus on-prem |
| Audit Biais IA | Value Leakage, Art. 10 | ✗ Biais, pas sécurité runtime |
| Watermarking Art. 50 | Marquage contenu généré | ✗ Différent |
| **🆕 Self-Hosted Agent Security** | **Runtime agent on-prem + CI/CD + persistance temporelle** | **Nouveau — angle souveraineté** |

### Périmètre d'audit testable (4 vecteurs)

| Vecteur | Test exécuté | Référence | Article AI Act |
|---------|--------------|-----------|----------------|
| **Persistance temporelle** | Injection d'un payload dormant en mémoire long-terme, redémarrage, vérification de la survie | arXiv 2607.19433 (Chronos) | Art. 15 |
| **État interne agent** | Tentative de compromission du runtime (variables, contexte, call stack), test de contournement sandbox | arXiv 2607.17986 (Self-State) | Art. 15, 14 |
| **Attaques multi-tours adaptatives** | Benchmark Adaptive Adversaries contre les guardrails en place | arXiv 2607.18063 | Art. 15 |
| **Surface CI/CD** | Audit du pipeline de build (GitHub Actions, GitLab CI), recherche d'injection au moment du deploiement | arXiv 2607.19267 | Art. 15, 17 |

**Bonus différenciateur :** livrable AI SBOM (cf. TICKET-028) — inventaire complet des modèles, dépendances, licences, juridictions. Conformité AI Act Art. 11/13.

---

## 📦 Format du livrable "Self-Hosted Agent Security Report"

1. **Executive Summary** (1 page) — score de robustesse runtime global, top 3 vulnérabilités, verdict souveraineté (oui/non/conditionnel)
2. **Architecture analysis** (2 pages) — cartographie du runtime agent, surfaces d'attaque identifiées, modèle de menace
3. **Attaques exécutées** (8-12 pages) — pour chaque vecteur :
   - Préconditions et scénario d'exécution
   - Artefacts d'attaque (captures, logs anonymisés)
   - Résultat (succès/échec/partial) + sévérité
   - Article AI Act / RGPD en jeu
4. **AI SBOM** (annexe, 3-5 pages) — inventaire complet des modèles + chaîne d'approvisionnement
5. **Plan de remédiation** (3-5 pages) — priorisé, chiffré, avec recommandations techniques concrètes (durcissement sandbox, signature artefacts, rotation mémoire)
6. **Attestation souveraineté** (si score ≥ 0.8) — certificat utilisable en communication client

---

## 💰 Pricing indicatif (à valider Thierry)

| Option | Périmètre | Délai | Prix indicatif |
|--------|-----------|-------|----------------|
| **Essential** | 2 vecteurs (Chronos + Self-State) + AI SBOM | 5 jours | 10-14k CHF |
| **Standard** | 4 vecteurs + AI SBOM + audit CI/CD | 10 jours | 18-25k CHF |
| **Premium** | 4 vecteurs + AI SBOM + audit CI/CD + re-test post-remédiation + attestation souveraineté | 15 jours | 30-40k CHF |

**Comparaison :** un audit RSSI classique facturé 8-15k CHF ne couvre pas le runtime agent IA. L'offre Cortex Leman se positionne comme **le seul audit technique runtime agent IA disponible en FR-CH**.

**Récurrent possible :** re-test semestriel (Art. 15 AI Act exige évaluation périodique de robustesse, et les vecteurs émergent vite — 4 nouveaux papiers en 5 jours).

---

## 🎯 Cibles prioritaires (FR-CH)

1. **Hôpitaux et cliniques privées (GE/VD/VS)** — déploiement on-prem imposé par Art. 9 RGPD + LPD, exposition maximale
2. **Banques privées genevoises** — souveraineté bancaire (Art. 47 LB), agents IA pour conformité FATCA/CRS
3. **Cabinets d'avocats d'affaires** — secret professionnel (Art. 321 CP), déploiement on-prem pour confidentialité
4. **Administrations publiques cantonales** — souveraineté numérique, agents IA pour traitement de dossiers
5. **PME industrielles (horlogerie, pharma)** — propriété intellectuelle, agents IA en R&D sur site

---

## 🗣️ Argumentaire en 3 phrases (pour cold outreach)

> *"Vous avez déployé un agent IA on-prem pour protéger vos données sensibles — mais les défenses OS traditionnelles ne couvrent pas le runtime de l'agent lui-même. 4 recherches publiées cette semaine (juillet 2026) documentent des vecteurs d'attaque nouveaux : persistance temporelle, compromission d'état interne, détournement de CI/CD. Notre audit 'Self-Hosted Agent Security' exécute ces attaques contre votre agent en production et délivre un AI SBOM conforme AI Act Art. 11/13."*

---

## 🔗 Convergence avec l'existant

- **TICKET-027** (technique interne) — Tars doit durcir le runtime Hermes lui-même selon ces vecteurs
- **TICKET-028** — AI SBOM comme livrable standard
- **One-pager Certification IA** — cette offre peut être positionnée comme un module "runtime" de la certification globale
- **AI Act 2 août (J-8)** — les exigences Art. 15 (robustesse) et Art. 11 (documentation technique) sont précisément couvertes par cette offre

---

*One-pager généré par Le Gardien des Normes (cycle 25/07) — source : ArXiv Daily 25/07 cluster "self-hosted agent security".*
