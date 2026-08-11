# Cortex Leman Database Schema — Compliance Reference

**Database:** `/home/tars/cortex-leman-v5/data/cortex-leman.db` (SQLite)
**Last verified:** 2026-05-04

## Tables

### `users` (12 rows — compliance-critical)

| Column | Type | Compliance Relevance |
|--------|------|---------------------|
| `id` | TEXT (UUID) | Identifiant pour droit à l'oubli (Art. 17) |
| `email` | TEXT | Donnée personnelle — base légale requise |
| `full_name` | TEXT | Donnée personnelle |
| `organization` | TEXT | Permet identification tenant |
| `role` | TEXT | ADMIN / EXPERT / OPERATOR — RBAC check |
| `status` | TEXT | ACTIVE / INACTIVE |
| `primary_vertical` | TEXT | COMPTABLE / AVOCAT / SANTE / BANQUE / STARTUP / RH |
| `allowed_verticals` | TEXT (JSON array) | Contrôle d'accès par vertical |
| `tenant_id` | TEXT (FK→tenants) | ⚠️ Actuellement NULL pour tous les users — gap isolation |
| `consent_given` | BOOLEAN | Art. 7 RGPD — vérifier que = 1 |
| `consent_date` | DATETIME | Art. 7 RGPD — vérifier présence |
| `data_retention_days` | INTEGER | Art. 5(1)(e) — défaut 365 jours |
| `mfa_enabled` | BOOLEAN | Art. 32 — ⚠️ Actuellement 0 pour tous les users |
| `mfa_secret` | TEXT | Null si MFA non activé |
| `must_change_password` | BOOLEAN | Sécurité initiale |
| `last_login` | DATETIME | Détection comptes inactifs |
| `login_count` | INTEGER | Activité |
| `refresh_token` | TEXT | Donnée sensible — vérifier rotation |

### `tenants` (0 rows — gap critique)

| Column | Type | Compliance Relevance |
|--------|------|---------------------|
| `id` | TEXT (UUID) | PK |
| `name` | TEXT | Nom organisation |
| `domain` | TEXT | Domaine email |
| `plan` | TEXT | Plan souscription |
| `max_users` | INTEGER | Limite |
| `max_intentions_per_day` | INTEGER | Limite usage IA |
| `active_verticals` | TEXT (JSON) | Verticals activés |
| `data_residency` | TEXT | ⚠️ Art. 44-49 RGPD — zone de résidence des données |
| `custom_rules` | TEXT (JSON) | Règles personnalisées |
| `owner_email` | TEXT | Responsable de traitement |
| `dpo_email` | TEXT | Art. 37 RGPD — DPO obligatoire si données sensibles |
| `retention_policy_days` | INTEGER | Art. 5(1)(e) |

**⚠️ Gap :** Table vide = pas d'isolation multi-tenant, pas de DPO configuré, pas de data_residency documenté.

### `audit_logs` (60 rows — updated 2026-05-11)

| Column | Type | Compliance Relevance |
|--------|------|---------------------|
| `id` | INTEGER | PK |
| `user_id` | TEXT (FK) | Qui a fait l'action |
| `user_email` | TEXT | Redondance pour traçabilité |
| `action` | TEXT | login_success, login_failed, agent_chat, tenant_onboarded |
| `resource_type` | TEXT | Type de ressource |
| `resource_id` | TEXT | ID de la ressource |
| `ip_address` | TEXT | ⚠️ Affiche "testclient" — IPs réelles non capturées |
| `user_agent` | TEXT | Navigateur/client |
| `details` | TEXT | Détails additionnels |
| `success` | BOOLEAN | Succès/échec |
| `error_message` | TEXT | Message d'erreur si échec |
| `tenant_id` | TEXT | Tenant concerné |
| `vertical` | TEXT | Vertical concerné |
| `intention_id` | TEXT | ID d'intention IA |
| `created_at` | DATETIME | Horodatage Art. 5(2) |

### `api_keys` (0 rows)

| Column | Type | Compliance Relevance |
|--------|------|---------------------|
| `id` | TEXT (UUID) | PK |
| `user_id` | TEXT (FK) | Propriétaire |
| `key_hash` | TEXT | Hash de la clé (pas de stockage en clair ✓) |
| `key_prefix` | TEXT | Préfixe pour identification |
| `name` | TEXT | Nom de la clé |
| `status` | TEXT | Statut |
| `scopes` | TEXT (JSON) | Permissions |
| `allowed_verticals` | TEXT (JSON) | Restriction par vertical |
| `rate_limit` | INTEGER | Limitation d'usage |
| `expires_at` | DATETIME | Expiration — Art. 5(1)(e) |
| `last_used` | DATETIME | Dernière utilisation |
| `use_count` | INTEGER | Nombre d'utilisations |

## Requêtes de Compliance (Python)

```python
import sqlite3

def check_compliance(db_path="/home/tars/cortex-leman-v5/data/cortex-leman.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    results = {}
    
    # 1. MFA Check
    c.execute("SELECT email, primary_vertical FROM users WHERE mfa_enabled = 0")
    results["mfa_disabled"] = c.fetchall()
    
    # 2. Tenant Isolation
    c.execute("SELECT email, organization FROM users WHERE tenant_id IS NULL")
    results["no_tenant"] = c.fetchall()
    c.execute("SELECT count(*) FROM tenants")
    results["tenant_count"] = c.fetchone()[0]
    
    # 3. Consent Check
    c.execute("SELECT email FROM users WHERE consent_given = 0 OR consent_date IS NULL")
    results["no_consent"] = c.fetchall()
    
    # 4. IP Logging
    c.execute("SELECT DISTINCT ip_address FROM audit_logs")
    results["ip_addresses"] = c.fetchall()
    
    # 5. High-Risk Verticals
    c.execute("SELECT email, primary_vertical, mfa_enabled FROM users WHERE primary_vertical IN ('SANTE', 'BANQUE')")
    results["high_risk_users"] = c.fetchall()
    
    # 6. DPO Check
    c.execute("SELECT name, dpo_email FROM tenants WHERE dpo_email IS NULL OR dpo_email = ''")
    results["no_dpo"] = c.fetchall()
    
    # 7. Retention Policy
    c.execute("SELECT email, data_retention_days FROM users WHERE data_retention_days IS NULL OR data_retention_days = 0")
    results["no_retention"] = c.fetchall()
    
    # 8. Failed Logins
    c.execute("SELECT user_email, count(*) FROM audit_logs WHERE action = 'login_failed' GROUP BY user_email")
    results["failed_logins"] = c.fetchall()
    
    conn.close()
    return results
```

## Verticals et Réglementations Applicables

| Vertical | Données Sensibles | RGPD Art. 9 | AI Act High-Risk | LPD | DPIA Requise |
|----------|-------------------|-------------|------------------|-----|-------------|
| SANTE | Données de santé | ✅ Oui | ✅ Art. 6(2) | ✅ Art. 2 | ✅ Art. 35 |
| BANQUE | Données financières | ✅ Oui | ✅ Art. 6(2) | ✅ Art. 2 | ✅ Art. 35 |
| AVOCAT | Secret professionnel | ✅ Oui | ⚠️ Possible | ✅ Art. 2 | ⚠️ À évaluer |
| COMPTABLE | Données fiscales | ✅ Oui | ⚠️ Possible | ✅ Art. 2 | ⚠️ À évaluer |
| RH | Données employés | ✅ Oui | ✅ Art. 6(2) | ✅ Art. 2 | ✅ Art. 35 |
| STARTUP | Variable | ⚠️ Possible | ⚠️ Possible | ⚠️ Variable | ⚠️ À évaluer |

## Pièges Identifiés

1. **`tenant_id` NULL pour tous les users** — Pas d'isolation des données entre organisations
2. **`ip_address` = "testclient"** — Proxy non configuré pour capturer les IPs réelles
3. **MFA non activé** — Données sensibles sans 2FA = violation Art. 32
4. **Table `tenants` vide** — Pas de DPO, pas de data_residency, pas de owner_email
5. **Email invalide** — Format `gmail:com` au lieu de `gmail.com` détecté
