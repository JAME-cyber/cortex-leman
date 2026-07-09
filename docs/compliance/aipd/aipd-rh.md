# AIPD — Vertical RH

> Surcharge du template `AIPD-TEMPLATE.md` pour la vertical **RH / Cabinet RH / DRH**.
> **Mode standard** — AI Act Annexe III: emploi, recrutement, RH = **haut risque**.

---

## 7. Données spécifiques traitées

### 7.1 Catégories de données sensibles

| Catégorie | Exemples | Base légale | Conservation |
|-----------|----------|-------------|-------------|
| Données candidats | CV, lettre, compétences, evaluations | Art. 6(1)(a) — consentement | 2 ans max (CNIL) |
| Données de recrutement | Score, ranking, entretiens | Art. 6(1)(b) — recrutement | 2 ans max |
| Données employés | Nom, adresse, salaire, évaluation | Art. 6(1)(b) — contrat travail | Durée contrat + 5 ans |
| Données de paie | Bulletins, cotisations, primes | Art. 6(1)(b) — paie | 5 ans |
| Données sensibles (si applicable) | Origine, sexe, handicap, religion | Art. 9(2)(b) — obligations employeur | Durée nécessité |
| Données de santé au travail | Visites médicales, inaptitudes | Art. 9(2)(h) — médecine du travail | Durée légale |

### 7.2 Contraintes réglementaires spécifiques

| Obligation | Référence | Implémentation Cortex Leman |
|-----------|-----------|---------------------------|
| Pas de décision RH automatique | RGPD Art. 22 + AI Act Annexe III | `rh-001`: gel automatique si décision RH |
| Anti-discrimination | Loi 2008-496 + AI Act | `rh-002`: vérification anti-biais |
| AI Act haut risque (RH) | AI Act Annexe III §4 | Documentation technique obligatoire |
| Consentement candidats | CNIL délibération | Recueilli avant tout traitement IA |
| Transparence algorithme | AI Act Art. 13 | Explicabilité des recommandations |

### 7.3 Règles JsonLogic actives (3 règles)

1. `rh-001` — Pas de décision RH automatique [CRITICAL] — gel si pattern « embauche/rejet/promotion » sans arbitrage humain
2. `rh-002` — Anti-discrimination embauche [CRITICAL] — vérification des critères discriminatoires dans les sorties
3. `rh-003` — Conservation données candidats ≤ 2 ans [HIGH] — purge automatique après durée légale

## 8. Risques spécifiques

| # | Risque | Gravité | Probabilité | Mesure Cortex Leman |
|---|--------|---------|------------|-------------------|
| RR-1 | **Discrimination algorithmique** (embauche) | 5/5 | Moyenne | `rh-002` + audit biais régulier |
| RR-2 | **Décision RH sans supervision humaine** | 5/5 | Faible | `rh-001`: gel automatique + arbitrage |
| RR-3 | **Score candidat biaisé** (genre, origine) | 4/5 | Moyenne | Audit équité + données d'entraînement |
| RR-4 | **Violation vie privée employé** | 3/5 | Faible | Minimisation + accès restreint |
| RR-5 | **Durée conservation excessive candidats** | 2/5 | Moyenne | Purge automatique 2 ans |

## 9. Validation DPO

- [ ] **AI Act haut risque** : documentation technique complétée (Art. 11)
- [ ] **Anti-discrimination** : audit d'équité algorithmique effectué
- [ ] Consentement candidats recueilli (formulaire dédié)
- [ ] Transparence : les candidats sont informés de l'usage d'IA
- [ ] DPA avec Cortex Leman signé
- [ ] Registre des traitements RH mis à jour
- [ ] Durée de conservation ≤ 2 ans pour données candidats
- [ ] Formation des recruteurs sur les biais de l'IA
- [ ] Mécanisme de recours pour les candidats documenté
- [ ] Consultation du CSE (si applicable)

> ⚠️ **NOTE AI ACT** : Les systèmes IA pour le recrutement et l'évaluation des personnes
> sont classés **haut risque** (Annexe III §4 de l'AI Act).
> Obligations renforcées : gestion des risques (Art. 9), documentation (Art. 11),
> supervision humaine (Art. 14), transparence (Art. 13), cybersécurité (Art. 15).
> La certification CE IA sera obligatoire pour cette vertical.
