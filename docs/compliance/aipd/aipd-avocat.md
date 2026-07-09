# AIPD — Vertical AVOCAT

> Surcharge du template `AIPD-TEMPLATE.md` pour la vertical **Avocat / Cabinet d'avocats**.
> **Mode haute protection obligatoire** — Secret professionnel Art. 321 CP, Art. 47 LB.

---

## 7. Données spécifiques traitées

### 7.1 Catégories de données sensibles

| Catégorie | Exemples | Base légale | Conservation |
|-----------|----------|-------------|-------------|
| **Secret professionnel** | Correspondance avocat-client, stratégies juridiques, mémos | Art. 321 CP (protection absolue) | Durée dossier + 10 ans |
| Données de procédure | Conclusions, assignations, jugements, pièces | Art. 6(1)(b) — mission juridique | Durée procédure + 10 ans |
| Données de consulting | Contrats, négociations, due diligences | Art. 6(1)(b) — mission conseil | 10 ans (obligation déontologique) |
| Données personnelles clients | Nom, coordonnées, situation familiale/financière | Art. 6(1)(b) + Art. 9 | Durée dossier + 5 ans |
| Données biométriques (si applicable) | Signature électronique | Art. 9(2) — consentement explicite | Durée nécessité |

### 7.2 Contraintes réglementaires spécifiques

| Obligation | Référence | Implémentation Cortex Leman |
|-----------|-----------|---------------------------|
| Secret professionnel absolu | Art. 321 CP, Art. 47 LB | LLM local OBLIGATOIRE — aucun transit cloud |
| Data residency CH | Art. 47 LB, RODF | Infrastructure suisse exclusive |
| Email professionnel | RODF | Validé à l'onboarding (`_validate_compliance`) |
| Pas de partage inter-client | Secret professionnel | Vault isolé par tenant |
| Journalisation infalsifiable | Art. 321 CP (preuve) | WORM + SHA-256 + RFC 3161 |

### 7.3 Règles JsonLogic actives (4 règles)

1. `avocat-001` — Secret professionnel absolu [CRITICAL] — blocage si données transitent hors infrastructure locale
2. `avocat-002` — LLM local obligatoire [CRITICAL] — vérification du provider LLM au runtime
3. `avocat-003` — Data residency CH [CRITICAL] — blocage si `compliance.data_residency != "CH"`
4. `avocat-004` — Email professionnel [HIGH] — rejet des domaines personnels lors de l'onboarding

## 8. Risques spécifiques

| # | Risque | Gravité | Probabilité | Mesure Cortex Leman |
|---|--------|---------|------------|-------------------|
| RA-1 | **Violation du secret professionnel** (transit cloud) | 5/5 | Faible | `avocat-002`: LLM local + validation onboarding |
| RA-2 | **Communication à un tiers non autorisé** | 5/5 | Faible | Isolation tenant + RBAC strict |
| RA-3 | **Hallucination juridique** (référence inexistante) | 4/5 | Moyenne | Confidence threshold 0.3 + arbitrage humain |
| RA-4 | **Accès data residency hors CH** | 5/5 | Faible | `avocat-003` + surveillance continue |
| RA-5 | **Perte de dossier client** | 4/5 | Faible | Vault chiffré + backup + réplication CH |
| RA-6 | **Conflit d'intérêts non détecté** | 3/5 | Moyenne | Agent Data + vérification croisée |

## 9. Validation DPO

- [ ] **Secret professionnel Art. 321 CP** : garanties documentées
- [ ] LLM local exclusivement (pas de cloud/hybride)
- [ ] Data residency CH vérifiée (certificat hébergeur suisse)
- [ ] Email professionnel vérifié (pas de gmail/outlook/hotmail)
- [ ] DPA avec Cortex Leman signé incluant clause secret professionnel
- [ ] Registre des traitements mis à jour (dossiers, procédures, consulting)
- [ ] Information des clients sur l'usage d'IA (obligation déontologique)
- [ ] Formation obligatoire des collaborateurs sur le secret professionnel numérique
- [ ] Audit annuel de sécurité effectué
- [ ] Procédure de violation de données documentée (notification CNIL/PPDT en < 72h)

> ⚠️ **NOTE CRITIQUE** : La violation du secret professionnel est un délit pénal (Art. 321 CP).
> Toute faiblesse dans la chaîne de traitement IA est potentiellement constitutive d'infraction.
> Le DPO et le Bâtonnier doivent valider conjointement ce document.
