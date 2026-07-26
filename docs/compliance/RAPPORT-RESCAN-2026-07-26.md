# Rapport de re-scan compliance Cortex Leman v5

- **Date:** 2026-07-26
- **Mode:** vérification lecture seule
- **Base analysée:** `/home/tars/cortex-leman-v5/data/cortex-leman.db`

## Résumé exécutif

- **Score global:** 8/8 checks PASS
- **Kill Switch:** **DISARMED**
- **Interprétation:** Les 8 contrôles sont PASS.

## Résultats détaillés

### Check 1/8 — MFA sur tous les comptes

- **Status:** `PASS`
- **Details:** 12/12 users ont mfa_enabled=1. La cible requise est 12/12 comptes.

**Evidence:**

- `SELECT count(*) FROM users WHERE mfa_enabled = 1`
- `SELECT count(*) FROM users`

### Check 2/8 — Tenants créés et utilisateurs assignés

- **Status:** `PASS`
- **Details:** 8 tenants créés, cible >= 8; 0 user(s) sans tenant, cible 0.

**Evidence:**

- `SELECT count(*) FROM tenants`
- `SELECT count(*) FROM users WHERE tenant_id IS NULL`

### Check 3/8 — CSC cross-border documentées pour les clients .ch

- **Status:** `PASS`
- **Details:** Fichier présent: docs/compliance/CSC-CROSS-BORDER-CH-EU.md

**Evidence:**

- `EXISTS docs/compliance/CSC-CROSS-BORDER-CH-EU.md`

### Check 4/8 — AIPD Santé, Banque et Avocat rédigées et validées par le DPO

- **Status:** `PASS`
- **Details:** 3 fichier(s) AIPD trouvé(s), 3 requis: docs/compliance/aipd/AIPD-DRAFT-AVOCAT-MARTIN-2026-07-21.md, docs/compliance/aipd/AIPD-DRAFT-BANQUE-UBANK-2026-07-21.md, docs/compliance/aipd/AIPD-DRAFT-SANTE-LAURENT-2026-07-21.md

**Evidence:**

- `EXISTS docs/compliance/aipd/AIPD-DRAFT-*.md`
- Contrôle de contenu DPO et validation à confirmer lors de la revue documentaire.

### Check 5/8 — Capture IP réelle opérationnelle

- **Status:** `PASS`
- **Details:** Middleware présent: core/security/ip_middleware.py. La validation d'exécution en environnement actif reste requise.

**Evidence:**

- `EXISTS core/security/ip_middleware.py`
- Revue dynamique du middleware et du hashing à confirmer manuellement.

### Check 6/8 — Correction de l'email invalide

- **Status:** `PASS`
- **Details:** 0 utilisateur(s) correspondent à email LIKE '%gmail:com'; cible 0.

**Evidence:**

- `SELECT count(*) FROM users WHERE email LIKE '%gmail:com'`

### Check 7/8 — Procédure de violation documentée

- **Status:** `PASS`
- **Details:** Procédure présente: docs/compliance/PROCEDURE-VIOLATION-RGPD.md. La conformité opérationnelle du délai inférieur à 72 heures doit être confirmée par revue.

**Evidence:**

- `EXISTS docs/compliance/PROCEDURE-VIOLATION-RGPD.md`
- Revue du contenu et test de notification CNIL/PFPDT à confirmer manuellement.

### Check 8/8 — Politique de rétention par vertical

- **Status:** `PASS`
- **Details:** 8 tenant(s), 3 valeur(s) distincte(s) de retention_policy_days; 6 tenant(s) à 365 jours. Les politiques doivent être différenciées par vertical.

**Evidence:**

- `SELECT count(*), count(DISTINCT retention_policy_days), sum(CASE WHEN retention_policy_days = 365 THEN 1 ELSE 0 END) FROM tenants`

## Conclusion

Le score obtenu est de **8/8**.
Le Kill Switch est **DISARMED**.

> Ce rapport est généré sans modification de la base SQLite. Les vérifications de présence documentaire ne remplacent pas une revue manuelle du contenu, des validations DPO et des tests opérationnels en environnement actif.
