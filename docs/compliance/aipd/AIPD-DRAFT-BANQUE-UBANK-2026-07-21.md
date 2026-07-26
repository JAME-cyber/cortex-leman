# AIPD / DPIA — DRAFT Vertical BANQUE (Thomas Müller, UBank SA)

> **Statut :** DRAFT pré-rempli par l'Exécutant Cortex Leman le 2026-07-21
> **Base :** Surcharge `AIPD-TEMPLATE.md` + `aipd/aipd-banque.md`
> **Déclencheur :** Alerte CRITICAL #2 du rapport Compliance W29 (MFA absente sur données financières)
> **À compléter par :** Tars (données techniques) + Compliance Officer UBank SA

---

## 1. Identification du traitement

| Champ | Valeur |
|-------|--------|
| **Responsable de traitement** | UBank SA (Thomas Müller, analyste) |
| **Sous-traitant** | Cortex Leman SARL |
| **DPO** | `[À RENSEIGNER — DPO UBank SA]` — `dpo@ubank.ch` |
| **Vertical** | Banque / Finance |
| **Mode** | `haute_protection` (obligatoire — secret bancaire Art. 47 LB) |
| **Date d'analyse** | 2026-07-21 |
| **Version** | 0.1 (draft) |

---

## 2. Contexte de l'AIPD

### 2.1 Pourquoi cette AIPD est déclenchée

Le rapport Compliance Hebdo W29 a détecté le 20/07/2026 :
- `mfa_enabled = 0` sur compte bancaire suisse
- `tenant_id = NULL`
- Data residency CH non vérifiée formellement
- Cross-border CH→EU non documenté (Alerte #3)

Ces gaps violent le secret bancaire absolu (Art. 47 LB), la LPD Art. 7, et AI Act Art. 6 (high-risk financier). Sanction pénale possible (Art. 47 LB est d'ordre public).

### 2.2 Utilisation prévue du système

Cortex Leman v5 est utilisé par T. Müller pour :
- `[À RENSEIGNER — ex : analyse KYC/AML automatisée]`
- `[À RENSEIGNER — ex : agrégation données marché]`
- `[À RENSEIGNER — ex : assistance reporting réglementaire]`

**Sont INTERDITS par design :**
- Exécution automatique d'ordre > 15K CHF sans validation humaine (`banque-003`)
- Transit de données bancaires hors infrastructure suisse (`banque-001/002`)
- Décisions de crédit automatisées (AI Act Art. 6)

---

## 3. Données traitées (Art. 47 LB + LPD + Art. 30)

| Catégorie | Exemples | Base légale | Conservation |
|-----------|----------|-------------|-------------|
| Secret bancaire | Transactions, soldes, avoirs | Art. 47 LB (absolu) | 10 ans (LBA) |
| KYC/AML | Identité, source de fonds, PEP | LBA Art. 3+ + Gafi | 10 ans après fin relation |
| Transactions | Virements, paiements, cartes | Art. 6(1)(b) | 5 ans (CbD2) |
| Crédit | Score, garanties, encours | Art. 6(1)(b) | Durée prêt + 5 ans |

---

## 4. Évaluation des risques

| # | Risque | Gravité | Probabilité | Mesure Cortex Leman | Statut W29 |
|---|--------|---------|------------|---------------------|------------|
| RB-1 | **Violation du secret bancaire** | 5/5 | Faible | LLM local + infra CH | 🔴 **MFA absente + cross-border non doc.** |
| RB-2 | Blanchiment non détecté | 5/5 | Faible | Seuil KYC 15K (`banque-003`) | ✅ En place |
| RB-3 | Hallucination sur exposition financière | 4/5 | Moyenne | Confidence threshold + arbitrage | ✅ En place |
| RB-4 | **Exécution automatique d'ordre erroné** | 5/5 | Faible | Gel > 15K + arbitrage humain | ✅ En place |
| RB-5 | **Data residency hors CH** | 5/5 | Faible | `banque-002` + monitoring | 🔴 **À vérifier formellement** |
| RB-6 | Conformité MiFID II | 3/5 | Faible | Agent Raisonnement + règles | ✅ En place |

---

## 5. Plan de remédiation (suite alerte W29)

| # | Action | Référence | Deadline | Statut |
|---|--------|-----------|----------|--------|
| 1 | **Activer MFA** sur `analyst@ubank.ch` | Art. 47 LB + LPD 7 | 22/07/2026 | ⏳ À exécuter (Tars) |
| 2 | **Vérifier provider LLM = LOCAL** (Art. 47 LB) | Art. 47 LB + `banque-002` | 22/07/2026 | ⏳ À auditer |
| 3 | **Vérifier data residency = CH** | Art. 47 LB | 22/07/2026 | ⏳ À documenter (certificat hébergeur) |
| 4 | **Créer tenant `ubank-sa`** | Art. 5(1)(f) + 10 | 03/08/2026 | ⏳ À exécuter (Tars) |
| 5 | **DPA avec clause secret bancaire** signé | Art. 47 LB | 03/08/2026 | ⏳ À vérifier |
| 6 | **CSC cross-border CH→EU** documentées | LPD Art. 16 + RGPD 44-49 | 22/07/2026 | ⏳ À rédiger (voir Procédure §3) |
| 7 | **Procédure violation** notification FINMA + PFPDT < 72h | Art. 33-34 RGPD + LBA | 15/08/2026 | ⏳ À rédiger |

---

## 6. Validation DPO

- [ ] MFA activée sur le compte
- [ ] Provider LLM vérifié LOCAL exclusivement (pas de cloud)
- [ ] Data residency CH vérifiée (certificat hébergeur suisse)
- [ ] DPA Cortex Leman signé (clause secret bancaire explicite)
- [ ] Procédures KYC/AML documentées et conformes LBA
- [ ] CSC cross-border documentées
- [ ] Registre des traitements mis à jour
- [ ] FINMA informée si applicable (concession bancaire)
- [ ] Audit sécurité annuel ISO 27001 ou équivalent
- [ ] Procédure violation (< 72h FINMA + PFPDT)
- [ ] Formation obligatoire collaborateurs
- [ ] Test de restauration effectué

---

## 7. Note AI Act + Secret Bancaire

> ⚠️ **Délit pénal potentiel.** Art. 47 LB (Loi sur les banques, Suisse) est d'ordre public. Toute violation, même involontaire via un LLM cloud, constitue un délit pénal (Art. 47 al. 4 LB).
>
> Le compliance officer bancaire ET le DPO doivent valider conjointement ce document.
> L'AI Act (UE 2024/1689) classe les systèmes IA financier comme high-risk (Annexe III §5b pour établissements de crédit).

---

*Draft automatique Exécutant Cortex Leman — 2026-07-21 — à itérer avec Tars et le compliance officer UBank avant validation finale.*
