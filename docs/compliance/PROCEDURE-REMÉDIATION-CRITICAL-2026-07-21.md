# Procédure de Remédiation — Alertes CRITICAL Compliance W29

> **Créé :** 2026-07-21 (mardi)
> **Source :** Rapport Compliance Hebdo W29 (`0dc376b91586`, 20/07 12:06)
> **Destinataire :** Tars (exécution technique) + Thierry (décision reprise activité)
> **Urgence :** 🔴 **Deadline 22 juillet 2026 (demain)** pour les 3 alertes CRITICAL
> **État système :** Kill Switch 🟡 ARMÉ — système dormant (0 activité 50 jours)

---

## Contexte — pourquoi c'est urgent

Le rapport hebdo du Gardien des Normes a détecté **3 alertes CRITICAL** sur la base de données réelle Cortex Leman (`cortex-leman.db`, 12 users, 63 logs). Ces alertes correspondent à des manquements RGPD/AI Act/LPD qui exposent à des sanctions CNIL/HOPD/PFPDT > 30K€ par compte. Bien que le système soit dormant (0 activité depuis le 31/05), **toute reprise d'activité sans résolution préalable est interdite** par la politique de Kill Switch du Gardien.

**Score global compliance : 0.30 / 1.00 (non conforme)**

---

## 🔴 ALERTE #1 — Compte SANTÉ sans MFA

| Champ | Valeur |
|---|---|
| **Client** | Dr. Sophie Laurent — `medecin@hopital-geneve.ch` (Hôpital de Genève) |
| **Vertical** | SANTÉ 🩺 |
| **Régulation** | RGPD Art. 9 (données de santé) + Art. 32 (sécurité) + AI Act Art. 6 (haut risque) |
| **Gap** | `mfa_enabled = 0` sur compte traitant des données de santé |
| **Risque sanction** | CNIL/HOPD > 30 000 € (cf. sanction IQVIA 5 M€ du 26/05/2026) |
| **Deadline** | **22 juillet 2026 (48h à compter du 20/07)** |

### Action à exécuter (Tars)

1. **Activer MFA** sur le compte `medecin@hopital-geneve.ch` (TOTP obligatoire, SMS interdit pour Art. 9)
2. **Notifier le client** par email sécurisé que la MFA est désormais obligatoire
3. **Lancer la DPIA** Santé (Art. 35 RGPD) — draft pré-rempli disponible : `docs/compliance/aipd/AIPD-DRAFT-SANTE-LAURENT-2026-07-21.md`
4. **Mettre à jour le registre des traitements** (Art. 30 RGPD)
5. **Documenter** dans audit_logs : `action="mfa_enable", target="medecin@hopital-geneve.ch", reason="critical_compliance_W29"`

### Référence réglementaire

> Art. 32 RGPD — « Le responsable du traitement et le sous-traitant mettent en œuvre les mesures techniques et organisationnelles appropriées afin de garantir un niveau de sécurité adapté au risque […] la pseudonymisation et le chiffrement des données personnelles. »
> Art. 9 RGPD — données de santé = catégorie spéciale, mesures renforcées obligatoires.
> AI Act Art. 6 — systèmes IA high-risk (santé Annexe III) exigent documentation technique + gestion des risques.

---

## 🔴 ALERTE #2 — Compte BANQUE sans MFA

| Champ | Valeur |
|---|---|
| **Client** | Thomas Müller — `analyste@ubank.ch` (UBank SA) |
| **Vertical** | BANQUE 🏦 |
| **Régulation** | RGPD Art. 32 + AI Act Art. 6 (haut risque financier) + LPD Art. 7 |
| **Gap** | `mfa_enabled = 0` sur compte bancaire suisse. Données financières sans 2FA |
| **Risque sanction** | PFPDT CH + FINMA + Art. 47 LB (secret bancaire) |
| **Deadline** | **22 juillet 2026** |

### Action à exécuter (Tars)

1. **Activer MFA** sur le compte `analyste@ubank.ch`
2. **Vérifier** que le provider LLM associé est bien **local** (Art. 47 LB) — si cloud détecté, bloquer immédiatement
3. **Vérifier data residency = CH** (`banque-002`)
4. **Lancer la DPIA** Banque — draft disponible : `docs/compliance/aipd/AIPD-DRAFT-BANQUE-UBANK-2026-07-21.md`
5. **Documenter** dans audit_logs

### Référence réglementaire

> Art. 47 LB (Loi sur les banques, Suisse) — secret bancaire absolu. Toute faille de sécurité = délit pénal.
> LPD Art. 7 (Suisse) — mesures techniques appropriées pour données personnelles sensibles.

---

## 🔴 ALERTE #3 — Cross-border CH→EU non documenté

| Champ | Valeur |
|---|---|
| **Clients concernés** | Pierre Martin (`avocat@martin-avocat.ch`) + 2 autres clients `.ch` |
| **Vertical** | AVOCAT ⚖️ (et cross-vertical) |
| **Régulation** | LPD Art. 16 (transfert hors Suisse) + RGPD Art. 44-49 |
| **Gap** | 3 clients suisses sans clauses contractuelles standard (CSC) documentées ni décision d'adéquation tracée. Comptes sans MFA + sans isolation tenant |
| **Risque** | PFPDT CH + CNIL FR (si transfert vers UE non documenté) |
| **Deadline** | **22 juillet 2026** |

### Action à exécuter (Tars)

1. **Identifier le flux réel** : où sont hébergées les données des 3 clients `.ch` ? (vérifier hébergeur, région cloud)
2. **Documenter le mécanisme de transfert** applicable :
   - Décision d'adéquation UE→CH (la Suisse est reconnue adéquate par la UE depuis 2000, révision en cours)
   - **CSC (Clauses Contractuelles Type)** Commission UE 2021/914 si transfert UE→tiers
   - **Tombeau suisse** (FADP) si transfert CH→UE
3. **Rédiger/vérifier les CSC** entre Cortex Leman SARL (sous-traitant) et chaque client `.ch` (responsable de traitement)
4. **Activer MFA** sur les 3 comptes concernés
5. **Lancer la DPIA** Avocat — draft disponible : `docs/compliance/aipd/AIPD-DRAFT-AVOCAT-MARTIN-2026-07-21.md`

### Référence réglementaire

> LPD Art. 16 (Suisse) — « Les données personnelles ne peuvent être communiquées à l'étranger que si […] la protection des données est garantie. »
> RGPD Art. 44-49 — mécanismes de transfert international (décision d'adéquation, CSC, BCR, dérogations).

---

## 🟠 ALERTE #4 — Isolation multi-tenant absente (HIGH)

| Champ | Valeur |
|---|---|
| **Client** | TOUS (12/12 users) |
| **Régulation** | RGPD Art. 5(1)(f) (confidentialité) + AI Act Art. 10 (qualité données) |
| **Gap** | Table `tenants` VIDE (0 rows). 2 events `tenant_onboarded` loggés mais aucune entrée persistée. TOUS les users ont `tenant_id = NULL` → mélange potentiel de données inter-organisations |
| **Deadline** | 3 août 2026 |

### Action à exécuter (Tars) — voir TICKET-019

1. **Créer 8 tenants** (un par organisation identifiée dans la DB) :
   - Hôpital de Genève (Dr. Laurent)
   - UBank SA (T. Müller)
   - Martin Avocat (P. Martin)
   - Dupont Comptable (M. Dupont)
   - Groupe RH (J. Moreau)
   - Startup Paris (L. Dubois)
   - J. Callaghan (à corriger d'abord : `gmail:com` → `gmail.com`)
   - Cortex Leman Admin (interne)
2. **Assigner chaque user** à son `tenant_id`
3. **Configurer `dpo_email`** par tenant
4. **Tester l'isolation** : un user du tenant A ne peut pas voir les données du tenant B

---

## 🟠 ALERTE #5 — Audit trail non exploitable (HIGH)

| Champ | Valeur |
|---|---|
| **Client** | Système global |
| **Régulation** | RGPD Art. 30 (registre) + Art. 5(2) (traçabilité) |
| **Gap** | 100% des IPs sont des placeholders (`None`, `127.0.0.1`, `testclient`). Sur 63 logs : **aucune IP réelle client**. Audit trail inutilisable en cas d'investigation CNIL |
| **Deadline** | 3 août 2026 |

### Action à exécuter (Tars) — voir TICKET-020

1. **Configurer un middleware FastAPI** qui capture l'IP réelle du client (`X-Forwarded-For` après validation du reverse proxy)
2. **Hasher l'IP** (SHA-256 + sel) avant stockage — pas de stockage en clair (minimisation)
3. **Anonymiser** après 13 mois (délai CNIL recommandé pour IPs)
4. **Documenter** le mécanisme dans le registre des traitements

---

## ✅ Checklist de levée du Kill Switch

Le Kill Switch peut être levé uniquement quand **toutes** ces conditions sont remplies :

- [ ] MFA activée sur 12/12 comptes (priorité Santé → Banque → Avocat → Admin)
- [ ] 8 tenants créés + tous les users assignés
- [ ] CSC cross-border documentées pour les 3 clients `.ch`
- [ ] DPIA Santé, Banque, Avocat rédigées et validées par le DPO
- [ ] Capture IP réelle opérationnelle (middleware + hashing)
- [ ] Email invalide `jame.callaghan@gmail:com` corrigé
- [ ] Procédure de violation documentée (notification CNIL/PFPDT < 72h)
- [ ] Politique de rétention par vertical (pas 365j uniforme)

**Validation finale :** Le Gardien des Normes. Aucune levée sans validation explicite du Gardien après re-scan complet.

---

## 📊 Priorisation et effort estimé

| # | Action | Priorité | Effort | Dépendance |
|---|--------|----------|--------|------------|
| 1 | MFA 3 comptes CRITICAL | 🔴 P0 | 1h | — |
| 2 | Documentation cross-border CH→EU | 🔴 P0 | 4h | Identification hébergeur |
| 3 | Correction email invalide | 🟠 P1 | 5 min | — |
| 4 | Création 8 tenants | 🟠 P1 | 1j | TICKET-019 |
| 5 | Capture IP réelle | 🟠 P1 | 1j | TICKET-020 |
| 6 | DPIA 3 verticals | 🟡 P2 | 3j | Drafts prêts dans `docs/compliance/aipd/` |
| 7 | Politique rétention par vertical | 🟡 P2 | 1j | — |

**Effort total avant levée Kill Switch : ~6 jours-homme.** Ceci est l'estimation basse si les DPIA drafts (déjà préparés) sont validées sans itération majeure.

---

## Signatures

- **Procédure rédigée par :** Exécutant Cortex Leman (cron) — 2026-07-21
- **Procédure à valider par :** Tars (exécution) + Le Gardien des Normes (validation finale)
- **Procédure à décider par :** Thierry (levée Kill Switch / reprise activité)

*Document de procédure — ne remplace pas la décision humaine. En cas de doute sur la portée d'une action, escalader avant d'exécuter.*
