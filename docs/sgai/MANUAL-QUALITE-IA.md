# 📋 SGAI — Manuel Qualité IA Cortex Leman v5
## Conforme ISO/IEC 42001:2023 (Système de Management de l'IA)
## Créé : 2026-05-27 | Version : 1.0
## Exigence : Audit o3 (ISO 42001 Lead Auditor), Phase 1

════════════════════════════════════════════════════════════
  1. POLITIQUE DE CONFORMITÉ IA
════════════════════════════════════════════════════════════

**Engagement** : Cortex Leman v5 fournit une infrastructure de conformité
IA pour les professions régulées franco-suisses. Notre engagement :

1. **Déterminisme critique** : Le Médiateur n'utilise JAMAIS de LLM pour les décisions de gel/blocage. Les règles sont 100% JsonLogic.
2. **Transparence totale** : Chaque décision est tracée dans le journal WORM hash-chainé, consultable par tout auditeur.
3. **Arbitrage humain** : L'IA ne décide jamais seule. Toute action bloquée nécessite un arbitrage humain.
4. **Conformité by design** : RGPD, AI Act, secret professionnel FR-CH sont encodés dans les règles, pas ajoutés après coup.
5. **Minimisation des données** : Le journal WORM applique la minimisation RGPD art. 5-1c et le chiffrement AES-256 au repos.
6. **Amélioration continue** : Revue trimestrielle des règles, du journal, et des précédents d'arbitrage.

**Signé** : Fondateur Cortex Leman
**Date** : 27 mai 2026
**Revue** : Trimestrielle

════════════════════════════════════════════════════════════
  2. PÉRIMÈTRE DU SGAI (ISO 42001, clause 4)
════════════════════════════════════════════════════════════

**Frontières du système** :
- Produit : Cortex Leman v5 — Infrastructure d'audit IA
- Verticales : comptable, avocat, santé, banque, startup, RH
- Zones géographiques : France, Suisse (conformité FR-CH)
- Déploiement : Mode Standard (cloud) + Mode Haute Protection (edge K3s)

**Exclusions** :
- Les modèles LLM tiers (OpenRouter, Ollama) ne sont PAS dans le périmètre.
  Cortex Leman les utilise comme composants, avec évaluation des risques.
- Les agents IA des clients finaux ne sont PAS dans le périmètre.
  Cortex Leman audite leurs actions, ne les développe pas.

**Parties intéressées** :

| Partie | Intérêt | Exigence |
|--------|---------|----------|
| Clients (cabinets régulés) | Conformité IA | Audit traçable, certificat via tiers |
| Certificateurs (Big 4) | Outil d'audit fiable | Données structurées, export, WORM intègre |
| Régulateurs (CNIL, FINMA) | Respect réglementaire | Registre traitements, DPIA, transparence |
| Ordres professionnels | Standard métier | Serment numérique, règles validées |
| Utilisateurs finaux | Protection données | Minimisation, droit d'accès, purge |

════════════════════════════════════════════════════════════
  3. GOUVERNANCE (ISO 42001, clause 5-6)
════════════════════════════════════════════════════════════

**3.1 Rôles et responsabilités**

| Rôle | Responsable | Mission |
|------|-------------|---------|
| Responsable SGAI | Fondateur | Politique, revues, objectifs |
| DPO (externe) | À nommer | Conformité RGPD, registre traitements |
| Comité d'éthique IA | 3 membres externes | Revue des règles, arbitrages litigieux |
| Responsable technique | Fondateur | Implémentation, sécurité, ops |
| Auditeur interne | À nommer | Revue SGAI semestrielle |

**3.2 Comité d'éthique IA**

Composition (minimum) :
- 1 avocat spécialisé droit numérique (FR ou CH)
- 1 DPO certifié
- 1 expert IA / data science

Mandat :
- Se réunit trimestriellement
- Revue des règles JsonLogic (pertinence, biais, lacunes)
- Revue des précédents d'arbitrage (jurisprudence)
- Avis sur les évolutions réglementaires
- Rapport annuel public (anonymisé)

**3.3 Objectifs mesurables**

| Objectif | KPI | Cible 2026 |
|----------|-----|------------|
| Intégrité du journal | WORM verify = valid | 100% |
| Temps de réponse Médiateur | Latence mediator_check | < 100ms |
| Couverture réglementaire | Articles AI Act mappés | 100% (art. 9-17) |
| Conformité RGPD | Audit RGPD interne | Score ≥ 8/10 |
| Disponibilité | Uptime plateforme | 99.5% |
| Incidents de conformité | Violations/trimestre | 0 |

════════════════════════════════════════════════════════════
  4. GESTION DES RISQUES IA (ISO 42001, clause 7-8)
════════════════════════════════════════════════════════════

**4.1 Registre des risques IA**

| ID | Risque | Probabilité | Impact | Mitigation | Statut |
|----|--------|-------------|--------|------------|--------|
| R01 | LLM hallucine dans Agent Raisonnement | Élevée | Moyen | Médiateur bloquant + Reflection Node | Actif |
| R02 | Fuite secret professionnel via logs | Moyen | Critique | WORM v2 chiffrement AES-256 + minimisation | Actif |
| R03 | Règle JsonLogic trop rigide | Moyen | Moyen | Comité éthique revue trimestrielle | Planifié |
| R04 | Attaque injection via MCP | Moyen | Élevé | Validation input + circuit breaker | Planifié |
| R05 | Indisponibilité LLM | Élevée | Moyen | Fallback models + Mode Haute Protection local | Actif |
| R06 | Biais discriminatoire dans règles | Faible | Critique | Audit externe annuel + comité éthique | Planifié |
| R07 | Non-conformité AI Act art. 61-62 | Moyen | Élevé | Post-market monitoring (à implémenter) | Planifié |
| R08 | Vendor lock-in Microsoft MCP | Élevée | Élevé | Agnostisme multi-interface (REST+SDK+CLI) | Actif |

**4.2 Critères d'acceptabilité du risque (AI Act art. 9)**

| Niveau | Définition | Action |
|--------|-----------|--------|
| 1-2 (Low/Medium) | Acceptable avec monitoring | Suivi trimestriel |
| 3 (High) | Nécessite mitigation | Plan d'action 30 jours |
| 4-5 (Critical/Block) | Inacceptable | Gel immédiat + arbitrage |

════════════════════════════════════════════════════════════
  5. GESTION DES INCIDENTS (ISO 42001, clause 10.2)
════════════════════════════════════════════════════════════

**5.1 Classification des incidents**

| Sévérité | Définition | SLA réponse | SLA résolution | Notification |
|----------|-----------|-------------|----------------|--------------|
| P1 — Critique | Fuite données, violation secret pro | 1h | 24h | Autorités sous 72h |
| P2 — Élevée | Règle contournée, gel non fonctionnel | 4h | 48h | Client + interne |
| P3 — Moyenne | Latence élevée, erreur non bloquante | 24h | 5 jours | Interne |
| P4 — Faible | Bug cosmétique, log manquant | 72h | 14 jours | Interne |

**5.2 Procédure d'incident**

1. **Détection** : Monitoring automatique + signalement utilisateur
2. **Triage** : Classification sévérité dans les 30 minutes
3. **Containement** : Isolation du composant affecté
4. **Investigation** : Analyse WORM + logs + reproduction
5. **Résolution** : Correctif + déploiement
6. **Communication** : Notification client/régulateur selon SLA
7. **Post-mortem** : Document publié dans les 7 jours
8. **Prévention** : Règle JsonLogic ou contrôle ajouté si applicable

**5.3 Post-market monitoring (AI Act art. 61-62)**

- Scan automatique quotidien des métriques de conformité
- Alerte si : taux de gel > 5%, confiance moyenne < 0.5, WORM integrity fail
- Rapport mensuel automatique au comité d'éthique
- Notification aux autorités dans les 15 jours si incident sérieux (art. 62)

════════════════════════════════════════════════════════════
  6. MAÎTRISE DES FOURNISSEURS (ISO 42001, clause 8.3)
════════════════════════════════════════════════════════════

| Fournisseur | Service | Risque | Contrôle |
|-------------|---------|--------|----------|
| OpenRouter | LLM cloud (mode Standard) | Transfert EU→US | EU-US DPF, fallback local |
| Ollama | LLM local (mode Haute Protection) | Aucun transfert | Isolation réseau K3s |
| NATS (Synadia) | Bus événementiel | Dépendance | On-premise possible |
| Redis | Cache + locks | Données transitoires | Purge automatique |
| Azure (si client) | Hébergement client | Data residency | Mode Haute Protection local |

Évaluation fournisseur : annuelle, documentée dans le registre des risques.

════════════════════════════════════════════════════════════
  7. CONFORMITÉ RÉGLEMENTAIRE (AI Act + RGPD + Secret pro)
════════════════════════════════════════════════════════════

**7.1 Référentiel de contrôle AI Act**

| Article | Exigence | Implémentation Cortex | Statut |
|---------|----------|----------------------|--------|
| 9 | Risk management | Médiateur + rules + registre risques | ✅ |
| 10 | Data governance | Documentation LLM tiers + audit | 📋 |
| 11 | Technical documentation | WORM + export audit | ✅ |
| 13 | Transparency | Journal public + score conformité | ✅ |
| 14 | Human oversight | Arbitrage humain obligatoire | ✅ |
| 15 | Accuracy/robustness | Circuit breaker + saga + tests | ✅ |
| 17 | QMS | Ce document (SGAI) | 📋 |
| 61-62 | Post-market monitoring | Monitoring + alertes | 📋 |

**7.2 Référentiel RGPD**

| Article | Exigence | Implémentation Cortex | Statut |
|---------|----------|----------------------|--------|
| 5-1a | Finalité | Politique SGAI + registre traitements | ✅ |
| 5-1b | Minimisation | PayloadMinimizer + purge | ✅ |
| 5-1c | Exactitude | Hash-chain WORM | ✅ |
| 5-1e | Conservation | Purge automatique 24 mois | ✅ |
| 6 | Base légale | Matrice base légale (TreatmentRegistry) | ✅ |
| 9 | Données sensibles | Chiffrement AES-256 + Haute Protection | ✅ |
| 30 | Registre traitements | TreatmentRegistry | ✅ |
| 35 | DPIA | Auto-générée par verticale | ✅ |
| 44+ | Transferts | Mode Haute Protection = zero transfert | ✅ |

**7.3 Référentiel Secret professionnel**

| Texte | Exigence | Implémentation Cortex | Statut |
|-------|----------|----------------------|--------|
| CP 321 (CH) | Secret avocat | Chiffrement WORM + K3s local | ✅ |
| LB 47 (CH) | Secret bancaire | Mode Haute Protection zero cloud | ✅ |
| LPM (CH) | Données santé | HDS + K3s local | 📋 |
| CNB 2023-14 (FR) | Convention avocat-prestataire | Template convention | 📋 |

Légende : ✅ Implémenté | 📋 En cours / planifié

════════════════════════════════════════════════════════════
  8. REVUE DE DIRECTION (ISO 42001, clause 9)
════════════════════════════════════════════════════════════

Fréquence : trimestrielle
Participants : Responsable SGAI + Comité d'éthique + DPO

Ordre du jour type :
1. Revue des KPIs conformité
2. Analyse des incidents du trimestre
3. Revue des précédents d'arbitrage
4. Mise à jour du registre des risques
5. Veille réglementaire (nouveaux textes, jurisprudence)
6. Retour du comité d'éthique
7. Plan d'action pour le trimestre suivant

Livrable : PV de revue archivé dans le WORM

════════════════════════════════════════════════════════════
  9. AMÉLIORATION CONTINUE (ISO 42001, clause 10)
════════════════════════════════════════════════════════════

Mécanismes :
- **Precedent Store** : Chaque arbitrage crée un précédent qui enrichit le Médiateur
- **Meta-evaluation** : Audit automatique des règles JsonLogic
- **Golden Dataset** : Cas de test de référence pour non-régression
- **Adversarial Judge** : Test adversarial des décisions du Médiateur
- **Comité d'éthique** : Revue humaine trimestrielle des règles
- **Audit externe** : Annuel par certificateur accrédité

════════════════════════════════════════════════════════════
  10. APPROBATION
════════════════════════════════════════════════════════════

| Rôle | Nom | Date | Signature |
|------|-----|------|-----------|
| Responsable SGAI | Fondateur Cortex Leman | 2026-05-27 | [à signer] |
| DPO | À nommer | — | — |
| Comité éthique (président) | À nommer | — | — |

Prochaine revue : Septembre 2026
