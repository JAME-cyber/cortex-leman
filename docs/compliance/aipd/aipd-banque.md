# AIPD — Vertical BANQUE

> Surcharge du template `AIPD-TEMPLATE.md` pour la vertical **Banque / Finance / Gestion d'actifs**.
> **Mode haute protection obligatoire** — Secret bancaire Art. 47 LB, LBA, KYC/AML.

---

## 7. Données spécifiques traitées

### 7.1 Catégories de données sensibles

| Catégorie | Exemples | Base légale | Conservation |
|-----------|----------|-------------|-------------|
| **Secret bancaire** | Transactions, soldes, historique, avoirs | Art. 47 LB (absolu) | 10 ans (LBA) |
| Données KYC/AML | Identité, source de fonds, PEP, sanctions | Art. 3+ LBA + Gafi | 10 ans après fin relation |
| Données de transaction | Virements, paiements, cartes | Art. 6(1)(b) — service bancaire | 5 ans (CbD2) |
| Données de crédit | Score, garanties, encours | Art. 6(1)(b) — crédit | Durée prêt + 5 ans |
| Données de trading | Ordres, portefeuilles, performances | Art. 6(1)(b) — gestion | 7 ans (MiFID II) |

### 7.2 Contraintes réglementaires spécifiques

| Obligation | Référence | Implémentation Cortex Leman |
|-----------|-----------|---------------------------|
| Secret bancaire absolu | Art. 47 LB | LLM local OBLIGATOIRE — infrastructure CH |
| KYC renforcé ≥ 15K CHF | LBA / Gafi | Seuil gel `banque-001`: 15 000 CHF |
| Data residency CH exclusive | Art. 47 LB | Validation onboarding |
| LBA — obligation de signaler | Art. 9 LBA | Agent Action : gel si soupçon |
| MiFID II — best execution | MiFID II Art. 27 | Agent Raisonnement : vérification |
| Pas de LLM cloud | Secret bancaire | `banque-002`: infrastructure CH obligatoire |

### 7.3 Règles JsonLogic actives (3 règles)

1. `banque-001` — Secret bancaire absolu [CRITICAL] — blocage si données transitent hors CH
2. `banque-002` — Infrastructure CH obligatoire [CRITICAL] — vérification `data_residency == "CH"` au runtime
3. `banque-003` — KYC renforcé ≥ 15K CHF [CRITICAL] — gel automatique si montant ≥ seuil sans validation KYC

## 8. Risques spécifiques

| # | Risque | Gravité | Probabilité | Mesure Cortex Leman |
|---|--------|---------|------------|-------------------|
| RB-1 | **Violation du secret bancaire** | 5/5 | Faible | LLM local + infrastructure CH |
| RB-2 | **Blanchiment non détecté** | 5/5 | Faible | Seuil KYC 15K + règles AML |
| RB-3 | **Hallucination sur exposition financière** | 4/5 | Moyenne | Confidence threshold + arbitrage |
| RB-4 | **Exécution automatique d'ordre erroné** | 5/5 | Faible | Gel montant > 15K + arbitrage humain |
| RB-5 | **Data residency hors CH** | 5/5 | Faible | Validation onboarding + monitoring |
| RB-6 | **Conformité MiFID II** | 3/5 | Faible | Agent Raisonnement + règles |

## 9. Validation DPO

- [ ] **Secret bancaire Art. 47 LB** : garanties documentées et testées
- [ ] LLM local exclusivement — infrastructure suisse certifiée
- [ ] Data residency CH vérifiée (certificat hébergeur suisse)
- [ ] DPA avec Cortex Leman signé (clause secret bancaire)
- [ ] Procédures KYC/AML documentées et conformes LBA
- [ ] Registre des traitements mis à jour
- [ ] FINMA informée si applicable (concession bancaire)
- [ ] Audit de sécurité annuel (norme ISO 27001 ou équivalent)
- [ ] Procédure de violation (notification FINMA + DPA < 72h)
- [ ] Test de restauration effectué
- [ ] Formation obligatoire collaborateurs

> ⚠️ **NOTE CRITIQUE** : Le secret bancaire suisse (Art. 47 LB) est d'ordre public.
> Toute violation, même involontaire via un LLM cloud, constitue un délit pénal.
> Le compliance officer bancaire doit valider ce document conjointement avec le DPO.
