# Cortex Leman v5 — Documentation de Certification

## Guide d'audit pour les organismes de certification tiers

**Version:** 5.0.0  
**Date:** Avril 2026  
**Classification:** Confidentiel — Usage certification uniquement  
**Référentiel:** ISO/IEC 42001:2023 + RGPD + AI Act + Droit FR-CH

---

## Table des matières

1. [Périmètre de certification](#1-périmètre-de-certification)
2. [Architecture technique auditée](#2-architecture-technique-auditée)
3. [Journal d'audit immuable](#3-journal-daudit-immuable)
4. [Mécanismes de conformité](#4-mécanismes-de-conformité)
5. [Supervision humaine](#5-supervision-humaine)
6. [Mode Haute Protection (Edge)](#6-mode-haute-protection)
7. [Tests de vérification](#7-tests-de-vérification)
8. [Procédures d'audit](#8-procédures-daudit)

---

## 1. Périmètre de certification

### Modules soumis à audit

| Module | Fichier | Fonction |
|--------|---------|----------|
| Journal WORM | `core/journal/append_only_journal.py` | Traçabilité opposable |
| Médiateur | `core/mediator/mediator.py` | Conformité réglementaire |
| Moteur de règles | `core/mediator/rules_engine.py` | Évaluation JsonLogic |
| Arbitrage humain | `core/arbitration/arbitration_service.py` | Supervision humaine |
| Circuit Breaker | `core/security/circuit_breaker.py` | Résilience agents |
| Saga Manager | `core/agents/saga/saga_manager.py` | Rollback par compensation |
| Verrous distribués | `core/security/distributed_lock.py` | Protection ressources |
| Compliance Gateway | `core/compliance/gateway.py` | Rapports automatiques |
| Bus NATS | `core/bus/nats_client.py` | Coordination agents |
| Orchestrateur | `core/orchestrator/conversationnal.py` | Orchestration événementielle |
| LLM Provider | `core/integrations/llm/provider.py` | Isolation données |
| Knowledge Vault | `core/integrations/knowledge_vault/vault.py` | Stockage isolé |

### Normes et réglementations couvertes

- **ISO/IEC 42001:2023** — Système de management de l'IA
- **RGPD (UE) 2016/679** — Protection des données
- **AI Act (UE) 2024/1689** — Intelligence artificielle
- **Code Pénal Français Art. 321** — Secret professionnel (avocats)
- **Loi fédérale sur les banques Art. 47** — Secret bancaire (Suisse)
- **LPM** — Protection des patients (santé)
- **LPD/LFPD** — Protection des données (Suisse)

---

## 2. Architecture technique auditée

### Flux de données

```
[Client] → [API FastAPI :8000]
              ↓
[Orchestrateur Conversationnel]
              ↓
[Bus NATS JetStream] → [Agent Data] → [Résultat]
              ↓              ↓
        [Agent Raisonnement] → [Résultat]
              ↓              ↓
        [Agent Action (Saga)] → [Résultat]
              ↓
[Agent Médiateur] → vérification règles JsonLogic
              ↓ (si conflit)
[Agent Superviseur] → state verification
              ↓ (si gel)
[Interface Arbitrage] → Décision humaine signée
              ↓
[Journal Append-Only] → Hash-chainage SHA-256
```

### Principes de conception

1. **Immuabilité** : Le journal est append-only, hash-chainé, signé HMAC
2. **Isolation** : Chaque client a son namespace NATS + son espace vault
3. **Supervision** : L'humain est arbitre, pas valideur (dossier contradictoire)
4. **Résilience** : Circuit breakers, Saga pattern, verrous distribués
5. **Localité** : Mode Haute Protection = zéro appel réseau externe

---

## 3. Journal d'audit immuable

### Caractéristiques techniques

- **Format** : JSON-L (une entrée par ligne)
- **Hash** : SHA-256, chaîné (chaque entrée contient le hash de la précédente)
- **Signature** : HMAC-SHA256 avec clé dédiée
- **Stockage** : Fichier par jour (`journal-YYYY-MM-DD.jsonl`)
- **WORM** : Écriture seule, pas de modification ni suppression possible
- **Vérification** : Endpoint `/api/v1/journal/verify` pour contrôle d'intégrité

### Preuve de non-répudiation

Chaque entrée contient :
- `entry_id` : UUID unique
- `sequence` : Numéro monotone croissant
- `timestamp` : Horodatage UTC avec timezone
- `previous_hash` : Hash de l'entrée précédente
- `entry_hash` : Hash du contenu + previous_hash
- `signature` : HMAC signé

### Test de vérification

```bash
# Vérifier l'intégrité de la chaîne
curl http://localhost:8001/api/v1/journal/verify

# Consulter le journal
curl "http://localhost:8001/api/v1/journal?limit=100"
```

---

## 4. Mécanismes de conformité

### Règles par verticale

6 verticales avec règles JsonLogic évaluables par tout auditeur :

| Verticale | Fichier | Règles | Référence |
|-----------|---------|--------|-----------|
| Comptable | `rules/comptable.json` | 5 | RGPD Art. 22, anti-blanchiment |
| Avocat | `rules/avocat.json` | 4 | Art. 321 CP, LPM |
| Santé | `rules/sante.json` | 3 | LPM, HDS, AI Act High Risk |
| Banque | `rules/banque.json` | 3 | Art. 47 LB, FINMA, anti-blanchiment |
| Startup | `rules/startup.json` | 2 | RGPD, DPIA |
| RH | `rules/rh.json` | 3 | AI Act, anti-discrimination |

### Actions du Médiateur

- **block** : Opération bloquée immédiatement (données sensibles hors périmètre)
- **freeze** : Gel de l'intention + demande d'arbitrage obligatoire
- **arbitrate** : Demande d'arbitrage sans gel
- **warn** : Avertissement journalisé
- **require_audit** : Exigence de traçabilité

---

## 5. Supervision humaine

### Interface d'arbitrage

Quand le Médiateur gèle une intention, l'interface affiche :
- Les positions contradictoires avec sources et niveaux de confiance
- Les références réglementaires applicables
- La simulation d'impact de chaque choix
- Un champ de justification obligatoire

### Traçabilité de la décision

```json
{
  "arbitration_id": "uuid",
  "arbiter_id": "expert-001",
  "arbiter_name": "Marie Dupont",
  "decision": "approve",
  "justification": "Les données sont suffisantes...",
  "selected_position": "data",
  "signed_at": "2026-04-24T18:30:00Z",
  "timestamp_token": "rfc3161_token",
  "precedent_value": "weak"
}
```

### Précédents

Les décisions d'arbitrage sont enregistrées comme précédents :
- **weak** : Première occurrence
- **moderate** : 2ème occurrence similaire
- **strong** : 3+ occurrences (peut enrichir le Médiateur)

---

## 6. Mode Haute Protection (Edge)

### Déploiement

```bash
# Installation appliance K3s (3 nœuds)
bash edge/k3s-install.sh

# Installation Ollama (LLM local)
bash edge/ollama-setup.sh

# Déploiement agents
k3s kubectl apply -f edge/manifests/
```

### Garanties techniques

| Garantie | Mécanisme | Vérification |
|----------|-----------|-------------|
| Aucune connexion sortante | iptables bloque tout sauf DNS/NTP | `iptables -L OUTPUT` |
| LLM local uniquement | Ollama sur localhost:11434 | `curl localhost:11434/api/tags` |
| Journal interne | Fichier local, réplication signée | `/api/v1/journal/verify` |
| mTLS entre agents | Certificats auto-signés | Vérifier config K3s |
| Données chiffrées | AES-256 au repos | Vérifier `.env.haute_protection` |

### Verticales requérant le Mode Haute Protection

- **Avocat** : Art. 321 CP (secret professionnel inviolable)
- **Banque** : Art. 47 LB (secret bancaire suisse)
- **Santé** : LPM + HDS (données de santé)

---

## 7. Tests de vérification

### Suite de tests automatisés

```bash
cd cortex-leman-v5
source .venv/bin/activate
python -m pytest tests/ -v

# Résultat attendu: 51 passed
```

### Tests manuels d'audit

#### 7.1 Test d'intégrité du journal
```bash
curl http://localhost:8001/api/v1/journal/verify
# Attendu: {"valid": true, "errors": []}
```

#### 7.2 Test de conformité par verticale
```bash
# Vérifier les règles chargées
curl http://localhost:8001/api/v1/mediator/rules
# Attendu: 6 verticales

# Vérifier data residency
curl "http://localhost:8001/api/v1/compliance/data-residency?vertical=avocat"
# Attendu: required_residency: CH
```

#### 7.3 Test de circuit breaker
```bash
curl http://localhost:8001/api/v1/agents/status
# Attendu: état des circuit breakers par agent
```

#### 7.4 Test de rapport de conformité
```bash
curl http://localhost:8001/api/v1/compliance/report/daily
# Attendu: rapport avec métriques, statut, intégrité journal
```

#### 7.5 Test d'arbitrage humain
```bash
# Lister les arbitrages en attente
curl http://localhost:8001/api/v1/arbitrations

# Soumettre une décision
curl -X POST "http://localhost:8001/api/v1/arbitrations/{id}/decide?arbiter_id=expert-001&arbiter_name=Expert&decision=approve&justification=Test&selected_position=data"
```

---

## 8. Procédures d'audit

### Audit annuel recommandé

1. **Vérification du code source** des mécanismes de conformité
2. **Test de pénétration** du mode Haute Protection (isolation réseau)
3. **Vérification du journal** : télécharger tous les fichiers JSONL, exécuter `verify_integrity()`
4. **Revue des règles** : vérifier que chaque règle JsonLogic correspond à une obligation réglementaire
5. **Test de reprise** : simuler un conflit → gel → arbitrage → reprise
6. **Vérification data residency** : confirmer que les données des verticales régulées restent dans le périmètre géographique requis

### Organismes de certification recommandés

- **LSTI** — Laboratoire de Sécurité des Technologies de l'Information
- **SGS** — Société Générale de Surveillance
- **AFNOR** — Association Française de Normalisation (ISO/IEC 42001)
- **SWISS SIG** — Certification suisse (pour le mode CH)

### Label proposé

**"IA de Confiance pour Professions Régulées FR-CH"**

Ce label atteste que :
- L'humain reste décisionnaire à chaque étape critique
- Le journal d'audit est immuable et opposable
- Les données sensibles ne quittent jamais l'infrastructure certifiée
- Les règles de conformité sont vérifiables par tout auditeur
- Le système résiste aux défaillances d'agents (circuit breakers, saga)
