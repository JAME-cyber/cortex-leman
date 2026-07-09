# AIPD — Vertical COMPTABLE

> Surcharge du template `AIPD-TEMPLATE.md` pour la vertical **Comptable / Cabinet d'expertise comptable**.

---

## 7. Données spécifiques traitées

### 7.1 Catégories de données sensibles

| Catégorie | Exemples | Base légale | Conservation |
|-----------|----------|-------------|-------------|
| Données financières | Bilans, comptes de résultat, déclarations fiscales | Art. 6(1)(b) — mission comptable | 10 ans (obligation légale) |
| Données fiscales | Déclarations IS, TVA, IR, base imposable | Art. 6(1)(b) — mission fiscale | 6 ans (droit de contrôle) |
| Pièces comptables | Factures, reçus, relevés bancaires | Art. 6(1)(b) — obligation comptable | 10 ans (Code de commerce) |
| Données de paie | Bulletins de salaire, cotisations | Art. 6(1)(b) — mission sociale | 5 ans |
| Données personnelles salariés | Nom, adresse, N° sécu, salaire | Art. 6(1)(b) + Art. 9 (données sensibles) | 5 ans |

### 7.2 Traitements à risque

| Traitement | Risque AI Act | Règle Cortex Leman |
|-----------|--------------|-------------------|
| Analyse fiscale automatisée | Décision produisant effets juridiques (Art. 22 RGPD) | `comptable-001`: Aucune décision fiscale automatique |
| Transfert données hors EU | Non-conformité RGPD | `comptable-002`: Données client en EU uniquement |
| Optimisation fiscale IA | Recommandation biaisée | `comptable-003`: Validation humaine obligation |

### 7.3 Règles JsonLogic actives (12 règles)

1. `comptable-001` — Aucune décision fiscale automatique [CRITICAL]
2. `comptable-002` — Données client en EU uniquement [HIGH]
3. `comptable-003` à `comptable-012` — Toutes implémentées et testées
   - Voir `core/mediator/rules/comptable.json` pour les expressions JsonLogic complètes
   - Testées dans `tests/test_mediator.py` et `tests/test_sprint2_p0_p1.py`

## 8. Risques spécifiques

| # | Risque | Gravité | Probabilité | Mesure Cortex Leman |
|---|--------|---------|------------|-------------------|
| RC-1 | Erreur de calcul fiscal avec impact financier client | 4/5 | Moyenne | Gel automatique > 10 000 € + arbitrage |
| RC-2 | Recommandation fiscale non conforme ( législation ) | 4/5 | Faible | Agent Raisonnement + règles JsonLogic |
| RC-3 | Accès non autorisé aux données fiscales d'un client | 3/5 | Faible | Isolation tenant + RBAC |
| RC-4 | Perte de pièces comptables | 4/5 | Faible | Vault chiffré + backup |
| RC-5 | Retard de déclaration dû à un blocage système | 3/5 | Faible | Timeout dégradé 30 min + escalade |

## 9. Validation DPO

- [ ] Données financières identifiées et classifiées
- [ ] Base légale validée pour chaque traitement
- [ ] Durées de conservation conformes (10 ans pièces, 6 ans fiscal, 5 ans social)
- [ ] DPA avec Cortex Leman signé
- [ ] Registre des traitements mis à jour
- [ ] Information des personnes concernées (clients + salariés)
- [ ] Test de restauration de données effectué
- [ ] Formation des utilisateurs sur l'outil IA
