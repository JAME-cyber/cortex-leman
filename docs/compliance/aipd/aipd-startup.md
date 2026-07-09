# AIPD — Vertical STARTUP

> Surcharge du template `AIPD-TEMPLATE.md` pour la vertical **Startup / Tech / SaaS**.
> **Mode standard** — Profilage possible, consentement requis.

---

## 7. Données spécifiques traitées

### 7.1 Catégories de données

| Catégorie | Exemples | Base légale | Conservation |
|-----------|----------|-------------|-------------|
| Données utilisateurs | Email, nom, préférences, usage | Art. 6(1)(b) — service | Durée compte + 3 ans |
| Données de tracking | Pages visitées, clics, conversions | Art. 6(1)(a) — consentement | 13 mois (recommandé CNIL) |
| Données de paiement | CB, historique, abonnements | Art. 6(1)(b) — contractual | 10 ans (obligation comptable) |
| Données de profiling | Segments, scores, recommandations | Art. 6(1)(a) — consentement explicite | Durée consentement |
| Cookies/trackers | Identifiants, device fingerprint | Art. 6(1)(a) — consentement | 13 mois max |

### 7.2 Contraintes réglementaires

| Obligation | Référence | Implémentation Cortex Leman |
|-----------|-----------|---------------------------|
| Consentement cookies | ePrivacy + CNIL | `startup-001`: consentement obligatoire |
| DPIA si profiling | RGPD Art. 35(1) | `startup-002`: DPIA si profiling détecté |
| Droit d'opposition profilage | RGPD Art. 21 | API `/api/v1/data/object` |
| Portabilité | RGPD Art. 20 | Export JSON/CSV |

### 7.3 Règles JsonLogic actives (2 règles)

1. `startup-001` — Consentement cookies/data [MEDIUM]
2. `startup-002` — DPIA si profiling [HIGH]

## 8. Risques spécifiques

| # | Risque | Gravité | Probabilité | Mesure Cortex Leman |
|---|--------|---------|------------|-------------------|
| RS-1 | **Profilage sans consentement** | 3/5 | Moyenne | `startup-002` + validation |
| RS-2 | **Données de tracking excessives** | 2/5 | Élevée | Minimisation + durée max 13 mois |
| RS-3 | **Recommandation biaisée (IA)** | 2/5 | Moyenne | Audit diversité + monitoring |
| RS-4 | **Faille sécurité (API)** | 3/5 | Faible | Rate limiting + OWASP compliance |
| RS-5 | **Non-respect droit d'oubli** | 3/5 | Faible | API suppression + purge vault |

## 9. Validation DPO

- [ ] Politique de cookies documentée et conforme
- [ ] Bannière cookies conforme (CNIL / ePrivacy)
- [ ] DPIA complétée SI profiling activé
- [ ] DPA avec Cortex Leman signé
- [ ] Registre des traitements mis à jour
- [ ] Mention légale + politique de confidentialité publiées
- [ ] Droit d'accès, rectification, suppression testés
- [ ] Processus de consentement documenté
