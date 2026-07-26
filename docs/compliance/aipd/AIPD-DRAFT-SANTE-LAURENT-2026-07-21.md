# AIPD / DPIA — DRAFT Vertical SANTÉ (Dr. Sophie Laurent, Hôpital de Genève)

> **Statut :** DRAFT pré-rempli par l'Exécutant Cortex Leman le 2026-07-21
> **Base :** Surcharge `AIPD-TEMPLATE.md` + `aipd/aipd-sante.md`
> **Déclencheur :** Alerte CRITICAL #1 du rapport Compliance W29 (MFA absente sur données Art. 9)
> **À compléter par :** Tars (données techniques) + DPO Hôpital de Genève (validation)

---

## 1. Identification du traitement

| Champ | Valeur |
|-------|--------|
| **Responsable de traitement** | Hôpital de Genève (Dr. Sophie Laurent, cheffe de service) |
| **Sous-traitant** | Cortex Leman SARL (technologie multi-agents IA) |
| **DPO** | `[À RENSEIGNER — DPO Hôpital de Genève]` — `dpo@hopital-geneve.ch` |
| **Vertical** | Santé / Établissement de soins |
| **Mode** | `haute_protection` (obligatoire — données Art. 9) |
| **Date d'analyse** | 2026-07-21 |
| **Version** | 0.1 (draft) |

---

## 2. Contexte de l'AIPD

### 2.1 Pourquoi cette AIPD est déclenchée

Le rapport Compliance Hebdo W29 (réf. CL-GDN-2026-W29) a détecté le 20/07/2026 que le compte `medecin@hopital-geneve.ch` présente les gaps suivants :
- `mfa_enabled = 0` sur données de santé (Art. 9 RGPD)
- `tenant_id = NULL` (isolation absente)
- Audit trail IPs placeholder

Ces gaps constituent des manquements RGPD Art. 9 + Art. 32 + AI Act Art. 6 (système high-risk santé, Annexe III). L'AIPD est obligatoire (Art. 35 RGPD).

### 2.2 Utilisation prévue du système

Cortex Leman v5 est utilisé par le Dr. Laurent pour :
- `[À RENSEIGNER — ex : tri documentaire de dossiers patients]`
- `[À RENSEIGNER — ex : assistance à la rédaction de comptes-rendus]`
- `[À RENSEIGNER — ex : agrégation de données cliniques pour recherche]`

**Sont INTERDITS par design :**
- Diagnostic automatique (`sante-002` : gel immédiat)
- Recommandation thérapeutique automatisée
- Toute décision produisant un effet juridique sur le patient (RGPD Art. 22)

---

## 3. Données traitées (Art. 9 + Art. 30)

| Catégorie | Exemples | Base légale | Conservation |
|-----------|----------|-------------|-------------|
| Données de santé | Diagnostics, traitements, historique médical | Art. 9(2)(h) | 20 ans |
| Données admin patients | Nom, N° sécu, mutuelle | Art. 6(1)(b) + 9(2)(h) | Durée soins + 20 ans |
| Données de prescriptions | Ordonnances, allergies | Art. 9(2)(h) | 20 ans |

---

## 4. Évaluation des risques

| # | Risque | Gravité | Probabilité | Mesure Cortex Leman | Statut W29 |
|---|--------|---------|------------|---------------------|------------|
| RS-1 | Diagnostic automatique non autorisé | 5/5 | Faible | `sante-002` (gel) | ✅ En place |
| RS-2 | **Fuite de données médicales** | 5/5 | Faible | HDS + chiffrement + isolation tenant | 🔴 **MFA absente, tenant NULL** |
| RS-3 | Hallucination médicale (posologie erronée) | 5/5 | Moyenne | Confidence threshold + interdiction diagnostic | ✅ En place |
| RS-4 | **Accès non autorisé au dossier patient** | 4/5 | Élevée | RBAC + traçabilité WORM | 🔴 **MFA absente élève la probabilité** |
| RS-5 | Non-sécurisation de l'hébergement | 4/5 | Faible | `sante-001` validation HDS | `[À VÉRIFIER]` |
| RS-6 | Atteinte à la vie privée | 5/5 | Faible | Pseudonymisation + minimisation | ✅ En place |

---

## 5. Mesures de sécurité existantes et plan de remédiation

### 5.1 Mesures techniques en place

- ✅ Architecture RAG (pas de fine-tuning) — données supprimables Art. 17
- ✅ Règles `sante-001/002/003` JsonLogic actives (HDS, no diagnostic, LLM local)
- ✅ Journal WORM hash-chainé SHA-256
- ✅ Vault chiffré AES-256
- ✅ Kill Switch opérationnel

### 5.2 Plan de remédiation (suite alerte W29)

| # | Action | Référence | Deadline | Statut |
|---|--------|-----------|----------|--------|
| 1 | **Activer MFA TOTP** sur `medecin@hopital-geneve.ch` | Art. 32 + 9 | 22/07/2026 | ⏳ À exécuter (Tars) |
| 2 | **Créer tenant `hopital-geneve`** + assigner user | Art. 5(1)(f) + 10 | 03/08/2026 | ⏳ À exécuter (Tars) |
| 3 | **Vérifier hébergement HDS** (certificat) | Art. L.1111-8 CSP | 03/08/2026 | ⏳ À documenter |
| 4 | **Valider LLM local exclusif** (`sante-003`) | CSP Art. L.1111-8 | 22/07/2026 | ⏳ À auditer |
| 5 | **Procédure violation** notification ARS/CNIL < 72h | Art. 33-34 RGPD | 15/08/2026 | ⏳ À rédiger |
| 6 | **Information patients** sur l'usage d'IA | Obligation déontologique | 15/08/2026 | ⏳ À planifier |

---

## 6. Validation DPO

- [ ] MFA activée sur le compte
- [ ] Tenant créé et isolé
- [ ] Hébergement HDS certifié documenté
- [ ] LLM local exclusivement (audit provider)
- [ ] Consentement patients recueilli et documenté
- [ ] DPA Cortex Leman signé (clause données de santé)
- [ ] Registre des traitements mis à jour (Art. 30)
- [ ] Information patients
- [ ] Formation praticiens
- [ ] Procédure violation documentée (< 72h ARS/CNIL)
- [ ] Test de restauration effectué

---

## 7. Note AI Act

> ⚠️ L'AI Act (UE 2024/1689) classe les systèmes IA santé comme **high-risk** (Annexe III §5).
> Obligations applicables à Cortex Leman en tant que **Fournisseur** :
> - Documentation technique (Art. 11)
> - Gestion des risques (Art. 9)
> - Supervision humaine (Art. 14)
> - Robustesse, accuracy, cybersecurity (Art. 15)
> - Enregistrement dans la base de données EU (Art. 71)
> - **Conformité CE obligatoire** (Art. 47-49) avant mise sur le marché

Le Dr. Laurent est **Déployeur** (utilise un système IA sur le marché EU) — obligations transparence + supervision humaine (Art. 26).

---

*Draft automatique Exécutant Cortex Leman — 2026-07-21 — à itérer avec Tars et le DPO client avant validation finale.*
