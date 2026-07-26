# AIPD / DPIA — DRAFT Vertical AVOCAT (Pierre Martin, Martin Avocat)

> **Statut :** DRAFT pré-rempli par l'Exécutant Cortex Leman le 2026-07-21
> **Base :** Surcharge `AIPD-TEMPLATE.md` + `aipd/aipd-avocat.md`
> **Déclencheur :** Alerte CRITICAL #3 du rapport Compliance W29 (cross-border CH→EU non documenté + MFA absente)
> **À compléter par :** Tars (données techniques) + Pierre Martin (responsable de traitement) + Bâtonnier (validation déontologique)

---

## 1. Identification du traitement

| Champ | Valeur |
|-------|--------|
| **Responsable de traitement** | Pierre Martin — Martin Avocat (cabinet individuel) |
| **Sous-traitant** | Cortex Leman SARL |
| **DPO** | Pierre Martin (cabinet individuel — DPO internalisé) — `avocat@martin-avocat.ch` |
| **Vertical** | Avocat / Cabinet juridique |
| **Mode** | `haute_protection` (obligatoire — secret professionnel Art. 321 CP) |
| **Date d'analyse** | 2026-07-21 |
| **Version** | 0.1 (draft) |

---

## 2. Contexte de l'AIPD

### 2.1 Pourquoi cette AIPD est déclenchée

Le rapport Compliance Hebdo W29 a détecté le 20/07/2026 :
- `mfa_enabled = 0` sur compte avocat suisse
- `tenant_id = NULL`
- **Cross-border CH→EU non documenté** (Alerte #3 — 3 clients `.ch` concernés)
- Transfert international sans CSC ni décision d'adéquation tracée

Ces gaps violent le secret professionnel absolu (Art. 321 CP), la LPD Art. 16, et le RGPD Art. 44-49. Délit pénal possible (Art. 321 CP est d'ordre public).

### 2.2 Utilisation prévue du système

Cortex Leman v5 est utilisé par P. Martin pour :
- `[À RENSEIGNER — ex : analyse documentaire de pièces de procédure]`
- `[À RENSEIGNER — ex : rédaction assistance de conclusions]`
- `[À RENSEIGNER — ex : due diligence contractuelle]`

**Sont INTERDITS par design :**
- Transit cloud de correspondance avocat-client (`avocat-001/002`)
- LLM non local (`avocat-002`)
- Partage inter-client (secret professionnel)
- Data residency hors CH (`avocat-003`)

---

## 3. Données traitées (Art. 321 CP + Art. 30 RGPD)

| Catégorie | Exemples | Base légale | Conservation |
|-----------|----------|-------------|-------------|
| Secret professionnel | Correspondance avocat-client, stratégies | Art. 321 CP (absolu) | Durée dossier + 10 ans |
| Procédure | Conclusions, assignations, jugements | Art. 6(1)(b) | Procédure + 10 ans |
| Consulting | Contrats, due diligences | Art. 6(1)(b) | 10 ans (déontologique) |
| Clients | Nom, situation familiale/financière | Art. 6(1)(b) + 9 | Dossier + 5 ans |

---

## 4. Évaluation des risques

| # | Risque | Gravité | Probabilité | Mesure Cortex Leman | Statut W29 |
|---|--------|---------|------------|---------------------|------------|
| RA-1 | **Violation secret professionnel** (transit cloud) | 5/5 | Élevée | `avocat-002` LLM local + validation onboarding | 🔴 **Cross-border non doc. élève probabilité** |
| RA-2 | Communication à tiers non autorisé | 5/5 | Faible | Isolation tenant + RBAC | 🔴 **Tenant NULL** |
| RA-3 | Hallucination juridique (réf. inexistante) | 4/5 | Moyenne | Confidence 0.3 + arbitrage humain | ✅ En place |
| RA-4 | **Data residency hors CH** | 5/5 | Élevée | `avocat-003` + surveillance | 🔴 **À vérifier (cross-border non doc.)** |
| RA-5 | Perte de dossier client | 4/5 | Faible | Vault chiffré + backup CH | ✅ En place |
| RA-6 | Conflit d'intérêts non détecté | 3/5 | Moyenne | Agent Data + cross-check | ✅ En place |

---

## 5. Plan de remédiation (suite alerte W29)

| # | Action | Référence | Deadline | Statut |
|---|--------|-----------|----------|--------|
| 1 | **Activer MFA** sur `avocat@martin-avocat.ch` | Art. 321 CP + LPD 7 | 22/07/2026 | ⏳ À exécuter (Tars) |
| 2 | **Vérifier provider LLM = LOCAL** | Art. 321 CP + `avocat-002` | 22/07/2026 | ⏳ À auditer |
| 3 | **Vérifier data residency = CH** | Art. 321 CP + RODF | 22/07/2026 | ⏳ À documenter |
| 4 | **Rédiger CSC cross-border CH→EU** | LPD Art. 16 + RGPD 44-49 | 22/07/2026 | ⏳ À rédiger (Procédure §3) |
| 5 | **Créer tenant `martin-avocat`** | Art. 5(1)(f) + secret prof. | 03/08/2026 | ⏳ À exécuter (Tars) |
| 6 | **DPA avec clause secret professionnel** | Art. 321 CP | 03/08/2026 | ⏳ À vérifier |
| 7 | **Procédure violation** notification Bâtonnier + PFPDT < 72h | Art. 33-34 RGPD | 15/08/2026 | ⏳ À rédiger |
| 8 | **Information clients** sur usage d'IA | Obligation déontologique | 15/08/2026 | ⏳ À planifier |

---

## 6. Validation DPO + Bâtonnier

- [ ] MFA activée sur le compte
- [ ] Provider LLM vérifié LOCAL exclusivement
- [ ] Data residency CH vérifiée (certificat hébergeur)
- [ ] Email professionnel vérifié (pas de gmail/outlook)
- [ ] DPA Cortex Leman signé incluant clause secret professionnel
- [ ] Registre des traitements mis à jour
- [ ] CSC cross-border documentées
- [ ] Information clients sur usage IA (déontologique)
- [ ] Formation collaborateurs sur secret professionnel numérique
- [ ] Audit annuel sécurité
- [ ] Procédure violation documentée (< 72h PFPDT + Bâtonnier)
- [ ] **Validation Bâtonnier** (obligatoire — Art. 321 CP)

---

## 7. Note Secret Professionnel + AI Act

> ⚠️ **Délit pénal potentiel.** Art. 321 CP (Code pénal suisse) protège le secret professionnel de l'avocat de manière absolue. Toute faiblesse dans la chaîne de traitement IA est potentiellement constitutive d'infraction pénale (Art. 321 al. 2 CP).
>
> Le DPO ET le Bâtonnier doivent valider conjointement ce document.
> L'AI Act classe certains systèmes IA juridiques comme high-risk (Annexe III §5a pour accès à la justice).

---

*Draft automatique Exécutant Cortex Leman — 2026-07-21 — à itérer avec Tars, P. Martin et le Bâtonnier avant validation finale.*
