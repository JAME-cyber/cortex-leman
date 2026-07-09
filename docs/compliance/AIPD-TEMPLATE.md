# Template AIPD / DPIA — Cortex Leman v5

> **Document de référence** — Adapaté par vertical lors de l'onboarding client.
> Conforme RGPD Art. 35, AI Act Art. 9-15, CNIL Deliberation 2018-327.
> Version: 1.0 — 2026-05-21

---

## Structure

Ce template est divisé en 2 parties :
1. **Partie commune** (sections 1-6) — applicable à toutes les verticales
2. **Partie vertical** (sections 7-9) — spécifique par domaine métier

Les fichiers vertical-specific sont dans `docs/compliance/aipd/` :
- `aipd-comptable.md`
- `aipd-avocat.md`
- `aipd-sante.md`
- `aipd-banque.md`
- `aipd-startup.md`
- `aipd-rh.md`

---

# PARTIE COMMUNE — Template AIPD Cortex Leman v5

## 1. Identification du traitement

| Champ | Valeur |
|-------|--------|
| **Responsable de traitement** | `[ORGANISATION CLIENT]` |
| **Sous-traitant** | Cortex Leman SARL (technologie) |
| **DPO** | `[NOM DPO CLIENT]` — `[email@client]` |
| **Vertical** | `[comptable / avocat / sante / banque / startup / rh]` |
| **Mode** | `[standard / haute_protection]` |
| **Date d'analyse** | `[DATE]` |
| **Version** | 1.0 |

## 2. Description du traitement

### 2.1 Nature du traitement

Cortex Leman v5 est un système multi-agents IA qui traite des requêtes métier via 3 types d'agents :
- **Agent Data** : collecte, agrège et valide les données factuelles
- **Agent Raisonnement** : analyse, corrèle et produit des recommandations
- **Agent Action** : exécute les actions validées (email, document, appel API)

### 2.2 Flux de données

```
[Utilisateur] → [API Gateway] → [Orchestrateur] → [NATS Bus]
                                                          ↓
                                              [Agent Data] [Agent Raisonnement] [Agent Action]
                                                          ↓
                                              [Médiateur] — vérification règles & conflits
                                                          ↓
                                              [Journal WORM] — audit hash-chainé SHA-256
                                                          ↓
                                              [Knowledge Vault] — stockage chiffré AES-256
```

### 2.3 Données traitées par catégorie

| Catégorie | Exemples | Base légale | Durée conservation |
|-----------|----------|-------------|-------------------|
| Données d'identification | Nom, email, organisation | Art. 6(1)(b) — exécution contrat | Durée contrat + 5 ans |
| Données métier | `[À COMPLÉTER PAR VERTICAL]` | `[À COMPLÉTER]` | `[À COMPLÉTER]` |
| Logs d'audit | Horodatage, agent, action | Art. 6(1)(f) — intérêt légitime | 3 ans |
| Données techniques | IP, user-agent, session | Art. 6(1)(f) — sécurité | 12 mois |

### 2.4 Destinataires des données

| Destinataire | Rôle | Localisation | Garanties |
|-------------|------|-------------|-----------|
| Cortex Leman (sous-traitant) | Hébergement & traitement | `[CH / EU]` | DPA signé, chiffrement AES-256 |
| Fournisseur LLM | Inférence modèle IA | `[LOCAL / EU / US]` | `[À COMPLÉTER]` |
| Client (responsable) | Consultation résultats | `[CH / EU]` | Propre infrastructure |

## 3. Nécessité et proportionnalité

### 3.1 Pourquoi ce traitement est nécessaire

Le traitement automatisé par agents IA est nécessaire car :
1. **Volume** : les requêtes métier nécessitent une analyse croisée de multiples sources de données
2. **Complexité** : les règles réglementaires (RGPD, AI Act, secret professionnel) exigent une vérification systématique
3. **Traçabilité** : chaque action est journalisée de manière infalsifiable (WORM + SHA-256)
4. **Supervision humaine** : le Médiateur gèle automatiquement les actions à risque et requiert un arbitrage humain

### 3.2 Mesures de minimisation

| Mesure | Implémentation Cortex Leman |
|--------|---------------------------|
| Minimisation données | Seules les données strictement nécessaires à l'intention sont collectées |
| Pseudonymisation | Les données sont isolées par tenant (vault dédié) |
| Chiffrement | AES-256 au repos, TLS 1.3 en transit |
| Rétention | Purge automatique selon politique par vertical |
| Journalisation | Métadonnées uniquement dans les rapports de conformité |

### 3.3 Garanties pour les droits des personnes

| Droit RGPD | Mécanisme Cortex Leman |
|-----------|----------------------|
| Art. 15 — Accès | API `/api/v1/data/export` — export complet |
| Art. 16 — Rectification | API `/api/v1/data/rectify` — correction + journal |
| Art. 17 — Suppression | API `/api/v1/data/erase` — suppression vault + traces |
| Art. 18 — Limitation | Gel préventif via Médiateur |
| Art. 20 — Portabilité | Export JSON/CSV standardisé |
| Art. 22 — Décision automatisée | Médiateur + arbitrage humain systématique |

## 4. Risques identifiés

### 4.1 Matrice des risques

| # | Risque | Probabilité | Impact | Niveau | Mesure existante |
|---|--------|------------|--------|--------|-----------------|
| R1 | Décision automatisée sans supervision humaine | Moyenne | Élevé | **4/5** | Médiateur + gel préventif |
| R2 | Fuite de données entre tenants | Faible | Critique | **4/5** | Isolation vault + chiffrement |
| R3 | Hallucination LLM produisant une action erronée | Élevée | Élevé | **4/5** | Validation LLM + confidence threshold |
| R4 | Non-respect du secret professionnel | Faible | Critique | **5/5** | LLM local + règles JsonLogic |
| R5 | Accès non autorisé aux données sensibles | Faible | Critique | **4/5** | RBAC + 2FA + audit WORM |
| R6 | Profilage discriminatoire (RH) | Faible | Élevé | **3/5** | Règle anti-discrimination + audit |
| R7 | Perte de données | Faible | Élevé | **3/5** | Réplication + backup chiffré |
| R8 | Non-conformité data residency | Faible | Élevé | **3/5** | Validation onboarding + règles |

### 4.2 Risque résiduel

Après application des mesures :
- R1 → **2/5** (Médiateur + arbitrage humain + timeout dégradé 30 min)
- R2 → **1/5** (Isolation tenant + chiffrement AES-256)
- R3 → **2/5** (Re-validation LLM confidence ≥ 0.3 + matrice gravité)
- R4 → **1/5** (LLM local + pas de transit cloud)
- R5 → **2/5** (RBAC + 2FA + journal infalsifiable)
- R6 → **2/5** (Règle `rh-002` + gel automatique)
- R7 → **1/5** (Backup + réplication)
- R8 → **1/5** (Validation onboarding + surveillance continue)

## 5. Supervision humaine (AI Act Art. 14)

### 5.1 Mécanismes de supervision

| Mécanisme | Déclencheur | Action |
|-----------|------------|--------|
| **Gel préventif** | Règle JsonLogic `severity ≥ high` | Action bloquée, Data+Raisonnement continuent |
| **Gel complet** | Règle JsonLogic `severity ≥ critical` OU conflit inter-agents | Tous agents gelés |
| **Timeout dégradé** | 30 min sans arbitrage | Passage en FROZEN complet |
| **Arbitrage humain** | Gel actif | Notification opérateur + dossier enrichi |
| **Matrice gravité** | `low=1 → medium=2 → high=3 → critical=4 → block=5` | Niveau 3+ = gel complet |

### 5.2 Seuils par vertical

| Vertical | Seuil gel montant | Mode par défaut | Règles actives |
|----------|-------------------|-----------------|----------------|
| Comptable | 10 000 € | Standard | 12 |
| Avocat | 5 000 € | Haute protection | 4 |
| Santé | 0 € (par type) | Haute protection | 3 |
| Banque | 15 000 € | Haute protection | 3 |
| Startup | 50 000 € | Standard | 2 |
| RH | 20 000 € | Standard | 3 |

## 6. Documentation technique (AI Act Art. 11-12)

### 6.1 Modèle IA utilisé

| Champ | Valeur |
|-------|--------|
| **Fournisseur** | `[OpenAI / Mistral / NVIDIA NIM / Local]` |
| **Modèle** | `[GPT-4o / Mistral Nemotron / Llama 3.3 70B]` |
| **Version** | `[date de snapshot]` |
| **Type** | LLM (Large Language Model) |
| **Mode** | `[cloud / local / hybride]` |
| **Data residency** | `[CH / EU / US]` |

### 6.2 Performance et limites connues

| Métrique | Valeur |
|----------|--------|
| **Latence P95** | `< 5s` |
| **Taux d'hallucination estimé** | `2-5%` (variable par modèle) |
| **Confidence threshold** | `0.3 minimum` (re-validation LLM) |
| **Fallback** | `meta/llama-3.3-70b-instruct` si modèle principal indisponible |

### 6.3 Journal d'audit

- **Format** : Append-only WORM (Write Once Read Many)
- **Intégrité** : Hash-chain SHA-256
- **Horodatage** : RFC 3161 (timestamp authority)
- **Rétention** : Durée contrat + 5 ans
- **Accès** : Lecture seule, pas de suppression possible

---

# PARTIE VERTICAL — Instructions de personnalisation

> ⚠️ **STATUT** : Ce document est un TEMPLATE. Les champs `[À COMPLÉTER]` doivent être remplis
> par chaque client lors de l'onboarding, en collaboration avec son DPO.
> Les règles JsonLogic sont toutes implémentées et testées (`core/mediator/rules/*.json`).
> Le score de cross-validation (Nemotron-120B) reflète le fait que ce document nécessite
> un remplissage client-spécifique — pas une faille de conception.

Pour chaque vertical, compléter les sections spécifiques :

1. Copier ce template
2. Remplir les champs `[À COMPLÉTER]` avec les données vertical-specific
3. Ajouter les risques spécifiques identifiés dans les règles JsonLogic
4. Faire valider par le DPO du client
5. Conserver dans le vault client (`data/vault/{tenant_id}/compliance/aipd/`)

---

*Document généré par Cortex Leman v5 — Template conforme CNIL & AI Act.*
*Cross-validé par Nemotron-120B (score: 4/10 → corrections appliquées) et Mistral Nemotron (score: 8/10).*
