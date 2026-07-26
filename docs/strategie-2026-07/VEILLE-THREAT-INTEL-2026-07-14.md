# Veille Threat Intelligence — Cortex Leman

> **Date:** 2026-07-14
> **Source:** ArXiv Daily Report (job 0f8a90201d56)
> **Domaines scannés:** cs.AI, cs.CR, cs.CV, cs.LG
> **Papers scannés:** 80 | **Papers importants:** 11 | **High relevance:** 6 | **Alerte critique:** 1

---

## 🚨 Menaces IA émergentes (à intégrer dans l'audit compliance)

### THREAT-001: Attaques Adversariales Multimodales sur VLAs
| Champ | Valeur |
|-------|--------|
| **arXiv** | 2607.11560 |
| **Titre** | Technical Report on the CVPR 2026@AdvML Workshop Challenge |
| **Domaine** | cs.CV |
| **Relevance** | 17/20 (CRITIQUE) |
| **Publié** | 2026-07-13 |
| **Résumé** | Challenge sur les attaques adversariales multimodales contre les vision-language agents (VLAs) en conduite autonome. Couvre sécurité, vulnérabilité, défense, robustesse adversariale. |
| **Impact Cortex Leman** | Pipelines de détection de falsification documentaire (L'Oeil de Cortex) vulnérables si VLAs utilisées. Vecteurs d'attaque transférables aux pipelines vision documentaire (deepfake, falsification). |
| **Article RGPD/AI Act** | AI Act Art. 15 (Robustesse et sécurité), Art. 14 (Supervision humaine) |
| **Niveau de risque assigné** | **R3** — Double validation requise pour tout pipeline vision |
| **Statut** | ⚠️ Ticket technique créé → `TICKETS-TECHNIQUES-SECURITE.md` |

### THREAT-002: Red-Teaming Automatisé des Agents IA en Production
| Champ | Valeur |
|-------|--------|
| **arXiv** | 2607.11698 |
| **Titre** | Agent Hacks Agent: Autoresearch for Production-Agent Red-Teaming |
| **Domaine** | cs.CR |
| **Relevance** | 14/20 |
| **Publié** | 2026-07-13 |
| **Résumé** | Méthodologie de red-teaming automatisé pour agents LLM de production (Claude Code, Codex) opérant sur contenus non fiables. Optimise la détection de failles de sécurité actionnables. |
| **Impact Cortex Leman** | Agents Cortex Leman (tâches autonomes, accès documentaire) exposés à des vecteurs d'attaque via contenus non fiables traités par les agents. |
| **Article RGPD/AI Act** | RGPD Art. 32 (Sécurité), AI Act Art. 15 (Robustesse), OWASP LLM01 (Prompt Injection) |
| **Niveau de risque assigné** | **R2** par défaut, **R3** si agent a accès outil critique |
| **Statut** | ⚠️ Ticket technique créé → `TICKETS-TECHNIQUES-SECURITE.md` |

### THREAT-003: Backdoors Distribués dans Systèmes Multi-Agents
| Champ | Valeur |
|-------|--------|
| **arXiv** | 2607.11751 |
| **Titre** | Distributed Backdoors in Multi-Agent Systems |
| **Domaine** | cs.CR |
| **Relevance** | 9/20 |
| **Publié** | 2026-07-13 |
| **Résumé** | Étude des backdoors distribués exploitant la composition de multiples agents IA. |
| **Impact Cortex Leman** | Architecture multi-agents Cortex Leman (Agent Data → Raisonnement → Action) vulnérable si un composant est compromis. Data leakage possible via chaining. |
| **Article RGPD/AI Act** | RGPD Art. 25 (Privacy by Design), Art. 32 (Sécurité), AI Act Art. 15 |
| **Niveau de risque assigné** | **R3** pour tout déploiement multi-agents |
| **Statut** | 📊 Veille — surveiller évolutions |

### THREAT-004: Claims de Risque Non Vérifiés en RL Distributionnel
| Champ | Valeur |
|-------|--------|
| **arXiv** | 2607.11607 |
| **Titre** | Auditing the Risk Claims of Distributional Reinforcement Learning |
| **Domaine** | cs.AI |
| **Relevance** | 12/20 |
| **Publié** | 2026-07-13 |
| **Résumé** | Étude mesurant si les claims de risque (interprétabilité, contrôle sensible au risque, monitoring de sécurité) des agents RL distributionnels sont fiables en pratique. |
| **Impact Cortex Leman** | Si un client utilise du RL pour décision automatisée, les claims de sécurité peuvent ne pas tenir en pratique. Audit de conformité requis. |
| **Article RGPD/AI Act** | AI Act Art. 15 (Robustesse), Art. 9-10 (Gestion des risques), RGPD Art. 22 (Décision automatisée) |
| **Niveau de risque assigné** | **R3** si RL dans le pipeline client |
| **Statut** | 📊 Intégré dans checklist compliance |

---

## 📊 Mapping Compliance FR-CH

| Thème RGPD/AI Act | Papers pertinents | Action Cortex Leman | Statut |
|--------------------|--------------------|----------------------|--------|
| **AI Act Art. 14-15** (Robustesse & Sécurité) | 2607.11560, 2607.11698, 2607.11843 | Tester robustesse adversariale des modèles vision L'Oeil | 🟡 Ticket technique créé |
| **AI Act Art. 13** (Transparence) | 2607.11862, 2607.11607 | Améliorer explainability des décisions d'anomalie | 🟡 Escalade technique |
| **AI Act Art. 9-10** (Gestion des risques) | 2607.11607, 2607.11601 | Intégrer dans matrice de risque RGPD-IA | 🟢 Fait — `MATRICE-RISQUES-R1-R4.md` |
| **RGPD Art. 25** (Privacy by Design) | 2607.11577, 2607.11751 | Vérifier architectures multi-agents (data leakage) | 🟢 Checklist créée |
| **RGPD Art. 22** (Décision automatisée) | 2607.11607, 2607.11698 | Audit des agents autonomes prenant des décisions | 🟢 Checklist créée |

---

## 📋 Papers surveillés (score ≥7/20, non critiques)

| Score | Domaine | arXiv ID | Titre | Thème |
|-------|---------|----------|-------|-------|
| 11/20 | cs.CV | 2607.11588 | FoundationGeo: Spatial Pixel-Wise Fields for Geometry | Robustesse modèle |
| 10/20 | quant-ph | 2607.11843 | Input-Aware Dynamic Backdoor Attack on Quantum NNs | Backdoor, sécurité |
| 10/20 | cs.CR | 2607.11601 | Cardano's Voltaire Governance: Complete Specification | Governance, sécurité |
| 9/20 | cs.CV | 2607.11732 | GFR-SAM: Training-Free Referring Camouflaged Segmentation | Alignment, benchmark |
| 8/20 | cs.CV | 2607.11862 | Evidence-Backed Video Question Answering | Explainability, vérif. |
| 8/20 | cs.LG | 2607.11577 | Structure-Feature Aligned Graph Learning | Robustness, benchmark |
| 7/20 | cs.CV | 2607.11886 | Read It Back: MLLMs as Zero-Shot Reward Models | Alignment, vérification |

---

*Rapport source: ArXiv Daily Report 2026-07-14 (cron job 0f8a90201d56)*
*Prochain scan: 2026-07-15 09:00*
