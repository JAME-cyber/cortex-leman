# AIPD — Vertical SANTÉ

> Surcharge du template `AIPD-TEMPLATE.md` pour la vertical **Santé / Clinique / Établissement de soins**.
> **Mode haute protection obligatoire** — Données de santé Art. 9 RGPD, LPM, HDS.

---

## 7. Données spécifiques traitées

### 7.1 Catégories de données sensibles

| Catégorie | Exemples | Base légale | Conservation |
|-----------|----------|-------------|-------------|
| **Données de santé** | Diagnostics, traitements, résultats d'examens, historique médical | Art. 9(2)(h) — soins de santé | 20 ans (recommandé) |
| Données administratives patients | Nom, date de naissance, N° sécu, mutuelle | Art. 6(1)(b) + Art. 9(2)(h) | Durée soins + 20 ans |
| Données de prescriptions | Ordonnances, posologies, allergies | Art. 9(2)(h) — prescription médicale | 20 ans |
| Données de facturation | Actes, tarifs, remboursements | Art. 6(1)(b) — facturation | 10 ans |
| Données de recherche (si applicable) | Données pseudonymisées pour études | Art. 9(2)(j) — recherche + autorisation CNIL | Selon protocole |

### 7.2 Contraintes réglementaires spécifiques

| Obligation | Référence | Implémentation Cortex Leman |
|-----------|-----------|---------------------------|
| Hébergement données de santé certifié | Art. L.1111-8 CSP (FR) / nEPR (CH) | HDS certifié ou infrastructure équivalente |
| Aucun diagnostic automatique | AI Act Art. 6(2) + RGPD Art. 22 | `sante-002`: gel automatique si diagnostic |
| Consentement patient | Art. 9(2)(a) RGPD | Recueilli avant traitement |
| Chiffrement renforcé | LPM / CSP | AES-256 + TLS 1.3 |
| Data residency EU/CH | CSP + LPM | Validation onboarding |
| LLM local obligatoire | Prudence (données de santé) | `sante-003`: mode cloud interdit |

### 7.3 Règles JsonLogic actives (3 règles)

1. `sante-001` — Données de santé: hébergement certifié [CRITICAL] — vérification HDS/nEPR au runtime
2. `sante-002` — Aucun diagnostic automatique [CRITICAL] — gel immédiat si pattern « diagnostic » ou « traitement » détecté
3. `sante-003` — LLM local obligatoire [CRITICAL] — même logique que `avocat-002`

## 8. Risques spécifiques

| # | Risque | Gravité | Probabilité | Mesure Cortex Leman |
|---|--------|---------|------------|-------------------|
| RS-1 | **Diagnostic ou recommandation thérapeutique automatisé** | 5/5 | Faible | `sante-002`: gel immédiat + arbitrage |
| RS-2 | **Fuite de données médicales** | 5/5 | Faible | HDS + chiffrement + isolation tenant |
| RS-3 | **Hallucination médicale** (posologie erronée) | 5/5 | Moyenne | Confidence threshold + interdiction diagnostic |
| RS-4 | **Accès non autorisé au dossier patient** | 4/5 | Faible | RBAC + traçabilité WORM |
| RS-5 | **Non-sécurisation de l'hébergement** | 4/5 | Faible | `sante-001`: validation HDS à l'onboarding |
| RS-6 | **Atteinte à la vie privée (divulgation)** | 5/5 | Faible | Pseudonymisation + minimisation |

## 9. Validation DPO

- [ ] Hébergement certifié HDS (ou équivalent CH) documenté
- [ ] **Aucun diagnostic automatique** : mécanisme documenté et testé
- [ ] LLM local exclusivement (pas de cloud pour données de santé)
- [ ] Consentement patients recueilli et documenté
- [ ] DPA avec Cortex Leman signé (clause données de santé)
- [ ] Registre des traitements mis à jour
- [ ] Information des patients sur l'usage d'IA dans les soins
- [ ] Formation des praticiens sur les limites de l'IA
- [ ] Comité d'éthique consulté (si établissement public)
- [ ] Procédure de violation documentée (notification ARS/CNIL < 72h)
- [ ] Test de restauration effectué

> ⚠️ **NOTE CRITIQUE** : L'AI Act classe les systèmes IA de santé comme **haut risque** (Annexe III).
> Obligations : documentation technique (Art. 11), gestion des risques (Art. 9), supervision humaine (Art. 14).
> La certification CE IA sera obligatoire à terme pour cette vertical.
