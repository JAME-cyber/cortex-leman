# Cortex Leman v5 — Base de Connaissance

> Documentation technique exhaustive du projet. Référence unique pour
> développeurs, auditeurs, et intégrateurs.

**Version :** 5.2 — Sprint 2  
**Dernière mise à jour :** 30 avril 2026

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Structure du projet](#2-structure-du-projet)
3. [Architecture des agents](#3-architecture-des-agents)
4. [Bus NATS — Sujets et protocole](#4-bus-nats--sujets-et-protocole)
5. [State Machine des Intentions](#5-state-machine-des-intentions)
6. [Médiateur & Règles JsonLogic](#6-médiateur--règles-jsonlogic)
7. [Journal WORM](#7-journal-worm)
8. [Arbitrage Humain & Escalade](#8-arbitrage-humain--escalade)
9. [Mode Dégradé Conforme](#9-mode-dégradé-conforme)
10. [Sécurité](#10-sécurité)
11. [RAG ChromaDB](#11-rag-chromadb)
12. [LLM Provider](#12-llm-provider)
13. [Frontend](#13-frontend)
14. [API Reference](#14-api-reference)
15. [Configuration (.env)](#15-configuration-env)
16. [Base de données](#16-base-de-données)
17. [Monitoring & Tracing](#17-monitoring--tracing)
18. [CI/CD](#18-cicd)
19. [Déploiement](#19-déploiement)
20. [Verticales Métier](#20-verticales-métier)
21. [Tests](#21-tests)
22. [Glossaire](#22-glossaire)

---

## 1. Vue d'ensemble

### Concept

Cortex Leman v5 est un **graphe de confiance IA** pour professions régulées franco-suisses. Il orchestre des agents IA (Data, Raisonnement, Action) sous la supervision d'un Médiateur déterministe et d'un arbitrage humain.

### Principes fondamentaux

| Principe | Implémentation |
|----------|---------------|
| Déterministe là où il faut | Médiateur, Action, Superviseur, Journal — 100% programmatique |
| Intelligent là où on peut | Orchestrateur, Data, Raisonnement — LLM-powered |
| L'humain décide, l'IA prépare | Arbitrage structuré avec justification obligatoire |
| Tout est tracé | Journal WORM SHA-256 chainé + HMAC signé |
| Gel par défaut | Action bloquée si verticale sensible + montant élevé |

### Chiffres clés

| Métrique | Valeur |
|----------|--------|
| Fichiers source | 118 |
| Lignes de code | 28K+ |
| Endpoints API | 51 |
| Sujets NATS | 33 |
| Tests | 246 |
| Règles JsonLogic | 22 |
| Verticales | 6 |
| Fichiers de test | 11 |

---

## 2. Structure du projet

```
cortex-leman-v5/
├── alembic/                    # Migrations base de données
│   ├── env.py
│   └── versions/
│       └── f94c56f6cc71_initial_tables.py
├── api/                        # API Gateway FastAPI
│   ├── main.py                 # 51 endpoints
│   └── dependencies.py         # Auth context, DB session
├── core/
│   ├── agents/                 # 5 agents + base
│   │   ├── base_agent.py       # Classe abstraite BaseAgent
│   │   ├── data_agent.py       # Agent Data (LLM)
│   │   ├── reasoning_agent.py  # Agent Raisonnement (LLM)
│   │   ├── action_agent.py     # Agent Action (programmatique)
│   │   ├── supervisor_agent.py # Superviseur V2 (programmatique)
│   │   ├── saga/               # Saga Manager + compensation
│   │   └── prompts/            # Skills Markdown par agent
│   │       ├── data.md
│   │       ├── reasoning.md
│   │       ├── action.md
│   │       ├── mediator.md
│   │       ├── orchestrator.md
│   │       └── supervisor.md
│   ├── arbitration/            # Arbitrage humain + escalade
│   │   └── arbitration_service.py
│   ├── bus/                    # Bus événementiel NATS
│   │   ├── nats_client.py      # Client NATS JetStream
│   │   └── subjects.py         # 33 sujets immutables
│   ├── compliance/             # Compliance Gateway
│   │   └── gateway.py
│   ├── config.py               # Pydantic Settings
│   ├── db/                     # SQLAlchemy models
│   │   ├── models.py           # Users, API keys, Audit logs, Tenants
│   │   └── session.py          # Engine + SessionFactory
│   ├── integrations/
│   │   ├── a2a_adapter.py      # Agent-to-Agent Protocol
│   │   ├── mcp_server.py       # Model Context Protocol
│   │   ├── knowledge_vault/    # Vault documentaire
│   │   ├── llm/                # LLM provider (OpenRouter/Ollama)
│   │   ├── n8n/                # n8n workflow client
│   │   └── rag/                # RAG ChromaDB vectoriel
│   ├── journal/                # Journal WORM
│   │   ├── append_only_journal.py
│   │   └── models.py           # JournalEntry, IntentionModel, ConflictRecord
│   ├── mediator/               # Médiateur déterministe
│   │   ├── mediator.py         # Agent Médiateur
│   │   ├── rules_engine.py     # Moteur JsonLogic
│   │   └── rules/              # 6 fichiers de règles JSON
│   │       ├── avocat.json     # 4 règles
│   │       ├── banque.json     # 3 règles
│   │       ├── comptable.json  # 7 règles
│   │       ├── rh.json         # 3 règles
│   │       ├── sante.json      # 3 règles
│   │       └── startup.json    # 2 règles
│   ├── orchestrator/           # Hub conversationnel
│   │   ├── conversationnal.py  # Orchestrateur principal
│   │   ├── intention.py        # IntentionStore + State Machine
│   │   └── router.py           # Routage dynamique
│   └── security/
│       ├── auth.py             # JWT + RBAC + 4 rôles
│       ├── audit.py            # Audit logging
│       ├── circuit_breaker.py  # Circuit Breaker (seuil 5)
│       ├── distributed_lock.py # Verrou distribué Redis
│       ├── encryption.py       # Chiffrement Fernet at-rest
│       ├── guardrails/
│       │   └── autodefense.py  # Multi-agent defense
│       └── timestamp.py        # Horodatage RFC 3161
├── data/
│   ├── intentions.json          # Persistance des intentions
│   ├── precedents.json          # Précédents d'arbitrage
│   ├── journal/                 # Fichiers WORM (1/jour)
│   ├── reports/                 # Rapports compliance
│   └── vault/
│       ├── catalog.json
│       └── regulatory/          # 6 docs réglementaires
├── docs/
├── edge/                        # Déploiement K3s + Ollama
├── frontend/                    # React 19 + Vite + TS
│   └── src/
│       ├── App.tsx
│       ├── LandingPage.tsx
│       ├── pages/
│       │   ├── DashboardPage.tsx
│       │   └── LoginPage.tsx
│       ├── components/
│       │   ├── AgentFlowAnimation.tsx
│       │   ├── ChatPanel.tsx
│       │   └── MarketSection.tsx
│       ├── hooks/useAuth.ts
│       └── lib/api.ts
├── infrastructure/              # Configs K3s + NATS
├── monitoring/
│   ├── metrics.py               # Prometheus
│   ├── tracing.py               # OpenTelemetry
│   └── grafana-dashboard.json
├── mvp/                         # Landing page MVP
├── scripts/                     # Scripts de déploiement
├── tests/                       # 11 fichiers, 246 tests
├── .env.example                 # Template configuration
├── docker-compose.yml           # 4 services
├── Dockerfile
├── architecture.html            # Diagramme SVG interactif
└── requirements.txt
```

---

## 3. Architecture des agents

### 3.1 BaseAgent

Classe abstraite commune. Chaque agent hérite de `BaseAgent`.

```python
class BaseAgent:
    name: str
    subscribe_subjects: list[str]
    
    async def start() -> None      # Connexion bus + abonnements
    async def process(data, meta)  # Traitement principal (override)
    async def stop() -> None       # Déconnexion propre
```

**Fichier :** `core/agents/base_agent.py`

### 3.2 Orchestrateur

**Fichier :** `core/orchestrator/conversationnal.py`  
**Type :** LLM-powered  
**Skill :** Maître de Cérémonie Lémanique

**Abonnements NATS (6) :**
| Sujet | Action |
|-------|--------|
| `cleman.intention.new` | Nouvelle intention → routage |
| `cleman.intention.revise` | Révision d'intention |
| `cleman.agent.result` | Résultat d'agent → vérification |
| `cleman.mediator.conflict` | Conflit → préparation arbitrage |
| `cleman.arbitration.decision` | Décision humaine → dégel |
| `cleman.validate.result` | Validation supervisée |

**Responsabilités :**
- Hub conversationnel permanent
- Intention versionnée (v1 → v2 → ...)
- Routage dynamique par contenu
- Assemblée d'agents dynamique (`POST /api/v1/agents/assemble-team`)
- Ne prend JAMAIS de décision de gel

### 3.3 Agent Data

**Fichier :** `core/agents/data_agent.py`  
**Type :** LLM-powered  
**Skill :** Veilleur de Sources / Hermétique CH

**Responsabilités :**
- Recherche asynchrone sur le bus
- Sources citées et vérifiables
- Haute Protection : sources locales uniquement
- Peut continuer en mode dégradé (enrichit le dossier d'arbitrage)

### 3.4 Agent Raisonnement

**Fichier :** `core/agents/reasoning_agent.py`  
**Type :** LLM-powered  
**Skill :** Juriste-Analyste Lémanique

**Responsabilités :**
- Analyse juridico-financière
- Compare minimum 2 options
- Publie `INTENTION_REVISE` si conflit interne
- Références réglementaires FR-CH
- Peut continuer en mode dégradé (enrichit le dossier d'arbitrage)

### 3.5 Agent Action

**Fichier :** `core/agents/action_agent.py`  
**Type :** 100% PROGRAMMATIQUE — aucun LLM

**Responsabilités :**
- Vérifie `is_action_blocked()` AVANT toute exécution (gel complet ou dégradé)
- Verrou distribué Redis sur l'intention
- Saga avec compensation en cas d'échec
- Circuit Breaker contre les pannes en cascade
- Journal WORM de chaque action

**Points de contrôle :**
```
1. is_action_blocked() → bloqué si gel complet OU dégradé
2. dist_lock.acquire() → un seul agent par intention
3. circuit_breaker.allow() → pas de surcharge
4. saga.execute() → exécution avec compensation
5. journal.append() → traçabilité
```

### 3.6 Superviseur V2

**Fichier :** `core/agents/supervisor_agent.py`  
**Type :** 100% PROGRAMMATIQUE

**Abonnements NATS (4) :**
| Sujet | Action |
|-------|--------|
| `cleman.agent.result` | Observation de TOUS les résultats |
| `cleman.mediator.conflict` | Comptage conflits |
| `cleman.mediator.freeze` | Comptage gels |
| `cleman.arbitration.decision` | Journalisation résolution |

**Health Board (`IntentionHealth`) :**
- Confiance globale par intention
- Nombre de conflits détectés
- Nombre de gels
- Staleness (secondes depuis dernière activité)
- `is_degraded` : confiance < 0.5 OU conflits ≥ 2

**Responsabilités :**
- Observer SANS interférer
- Préparer les dossiers d'arbitrage
- Alerter si dégradé (`cleman.supervisor.alert`)
- Journaliser chaque observation

---

## 4. Bus NATS — Sujets et protocole

**Fichier :** `core/bus/subjects.py`  
**Client :** `core/bus/nats_client.py`

### Registry des 33 sujets

| Domaine | Sujet | Description |
|---------|-------|-------------|
| Intention | `cleman.intention.new` | Nouvelle intention |
| | `cleman.intention.revise` | Révision |
| | `cleman.intention.cancel` | Annulation |
| | `cleman.intention.route` | Routage agents |
| Agent | `cleman.agent.result` | Résultat générique |
| Data | `cleman.data.query` | Requête data |
| | `cleman.data.result` | Résultat data |
| | `cleman.data.scan.internal` | Scan interne |
| | `cleman.data.scan.external` | Scan externe |
| Raisonnement | `cleman.reasoning.analyze` | Analyse |
| | `cleman.reasoning.result` | Résultat |
| | `cleman.reasoning.compare` | Comparaison |
| | `cleman.reasoning.recommend` | Recommandation |
| Action | `cleman.action.execute` | Exécuter |
| | `cleman.action.result` | Résultat |
| | `cleman.action.compensate` | Compensation saga |
| | `cleman.action.notify` | Notification |
| Validation | `cleman.validate.request` | Demande validation |
| | `cleman.validate.result` | Résultat validation |
| Médiateur | `cleman.mediator.check` | Vérification |
| | `cleman.mediator.conflict` | Conflit détecté |
| | `cleman.mediator.freeze` | Gel complet |
| | `cleman.mediator.degraded_freeze` | Gel dégradé (P0) |
| | `cleman.mediator.unfreeze` | Dégel |
| Arbitrage | `cleman.arbitration.request` | Demande arbitrage |
| | `cleman.arbitration.decision` | Décision humaine |
| | `cleman.arbitration.precedent` | Précédent enregistré |
| | `cleman.arbitration.escalation` | Escalade suppléant (P0) |
| | `cleman.arbitration.timeout` | Timeout arbitre (P0) |
| Compliance | `cleman.compliance.check` | Vérification compliance |
| | `cleman.compliance.report` | Rapport compliance |
| Système | `cleman.system.health` | Health global |
| | `cleman.system.error` | Erreur système |
| | `cleman.system.audit` | Événement audit |

### Isolation

```python
subjects.for_client("client-123")  # → "cleman.client.client-123"
subjects.for_vertical("avocat")     # → "cleman.vertical.avocat"
```

---

## 5. State Machine des Intentions

**Fichier :** `core/orchestrator/intention.py`

### États (10)

```
CREATED → ROUTED → PROCESSING → FROZEN → ARBITRATING → UNFROZEN → PROCESSING
                              → DEGRADED_FROZEN → ARBITRATING
                              → DEGRADED_FROZEN → FROZEN (escalade)
                  → COMPLETED
                  → FAILED
                  → CANCELLED
```

### Transitions valides

| From | To |
|------|----|
| CREATED | ROUTED, CANCELLED |
| ROUTED | PROCESSING, FROZEN, DEGRADED_FROZEN, CANCELLED |
| PROCESSING | FROZEN, DEGRADED_FROZEN, COMPLETED, FAILED |
| DEGRADED_FROZEN | ARBITRATING, FROZEN, CANCELLED |
| FROZEN | ARBITRATING, CANCELLED |
| ARBITRATING | UNFROZEN, CANCELLED |
| UNFROZEN | PROCESSING, FROZEN |

### Méthodes clés

```python
store.freeze(intention_id, reason="...", degraded=True)   # Gel dégradé
store.freeze(intention_id, reason="...", degraded=False)  # Gel complet
store.is_fully_frozen(intention_id)                       # True si FROZEN
store.is_degraded_frozen(intention_id)                    # True si DEGRADED_FROZEN
store.is_action_blocked(intention_id)                     # True si gel complet OU dégradé
store.get_history(intention_id)                           # Historique des transitions
```

### Persistance

- Fichier JSON avec atomic write (`.tmp` → `replace()`)
- Chemin configurable : `./data/intentions.json`
- Chargement au démarrage pour survie au redémarrage

---

## 6. Médiateur & Règles JsonLogic

**Fichiers :**
- `core/mediator/mediator.py` — Agent Médiateur
- `core/mediator/rules_engine.py` — Moteur de règles
- `core/mediator/rules/*.json` — 6 fichiers de règles

### Actions possibles

| Action | Effet |
|--------|-------|
| `block` | Blocage immédiat + gel complet |
| `freeze` | Gel complet + arbitrage obligatoire |
| `arbitrate` | Demande d'arbitrage sans gel |
| `warn` | Warning dans les logs |
| `require_audit` | Audit renforcé journalisé |

### Seuils par verticale

| Verticale | Seuil montant | Logique de gel |
|-----------|--------------|----------------|
| Comptable | 10 000 CHF | Montant + règles fiscales |
| Avocat | 0 (désactivé) | Par type d'action (transfert, LLM externe) |
| Santé | 0 (désactivé) | Par type de données (santé, diagnostic) |
| Banque | 15 000 CHF | KYC renforcé |
| Startup | 10 000 CHF | Défaut |
| RH | 10 000 CHF | Défaut |

### Modes de gel

| Mode | Agents bloqués | Agents actifs | Sujet NATS |
|------|---------------|---------------|------------|
| Complet (`FROZEN`) | Tous | Aucun | `cleman.mediator.freeze` |
| Dégradé (`DEGRADED_FROZEN`) | Action | Data, Raisonnement | `cleman.mediator.degraded_freeze` |

### Null-safety

Le wrapper `jsonLogic` est null-safe : toute comparaison numérique avec `None` retourne `False`. Un montant absent ne déclenche jamais de gel.

---

## 7. Journal WORM

**Fichier :** `core/journal/append_only_journal.py`

### Caractéristiques

| Propriété | Implémentation |
|-----------|---------------|
| Append-only | Pas de modification ni suppression |
| Hash-chainé | SHA-256, chaque entrée lie vers la précédente |
| Signé | HMAC-SHA-256 avec clé configurable |
| Horodaté | UTC avec timezone |
| Persisté | Un fichier JSON-L par jour |
| Vérifiable | `verify_integrity()` parcourt toute la chaîne |

### Format d'une entrée

```json
{
  "entry_id": "uuid",
  "sequence": 42,
  "timestamp": "2026-04-30T14:30:00+00:00",
  "event_type": "mediator.conflict",
  "client_id": "client-123",
  "vertical": "comptable",
  "agent_source": "mediator",
  "intention_id": "uuid",
  "payload": {...},
  "previous_hash": "sha256...",
  "entry_hash": "sha256...",
  "signature": "hmac..."
}
```

### 18 types d'événements

Voir `core/journal/models.py` → `JournalEventType`

---

## 8. Arbitrage Humain & Escalade

**Fichier :** `core/arbitration/arbitration_service.py`

### Flux complet

```
1. Conflit détecté → Médiateur gèle l'intention
2. ArbitrationService.prepare_arbitration()
   - Dashboard avec positions contradictoires
   - Assignation à l'arbitre principal
   - Timer d'escalade démarré
3. [Attente décision OU timeout → escalade]
4. submit_decision() par l'humain
   - Annulation du timer d'escalade
   - Signature + horodatage
   - Enregistrement comme précédent
   - Journalisation WORM
5. Dégel + reprise du flux
```

### File d'escalade

| Niveau | Rôle | Timeout défaut |
|--------|------|---------------|
| 1 | `expert` (arbitre principal) | 2h |
| 2 | `expert_suppleant` | 4h |
| 3 | `associe` (associé cabinet) | 8h |

Configuration via `ARBITRATION_ESCALATION_CHAIN` et `ARBITRATION_ESCALATION_TIMEOUT_HOURS`.

### Force des précédents

| Force | Condition |
|-------|-----------|
| `weak` | Première occurrence |
| `moderate` | 1 décision similaire antérieure |
| `strong` | 2+ décisions similaires |

---

## 9. Mode Dégradé Conforme

**Statut :** Implémenté Sprint 2 (P0)

### Principe

Quand un conflit est détecté et que la situation n'est pas critique (pas de règle `block`), le Médiateur gèle en mode **dégradé** :
- ✅ Agent Data continue → enrichit le dossier
- ✅ Agent Raisonnement continue → enrichit le dossier
- ❌ Agent Action bloqué → aucune exécution

### Résultats publiés pendant le gel dégradé

```json
{
  "intention_id": "...",
  "agent_source": "data",
  "event": "enrichment",
  "message": "Agent data a enrichi le dossier pendant le gel dégradé",
  "positions": {"data": {...}, "reasoning": {...}}
}
```

### Race condition dégel/résultat en vol

**Problème identifié :** si l'arbitrage est résolu alors qu'un résultat Data/Raisonnement est en vol sur le bus, ce résultat pourrait ne pas être intégré au dashboard.

**Mitigation actuelle :** `agent_positions` du Médiateur reste accessible en lecture après le dégel.

**Recommandation Sprint 3 :** ajouter une fenêtre de consolidation de 5s après le dégel.

---

## 10. Sécurité

### 10.1 Authentification

**Fichier :** `core/security/auth.py`

- JWT access token (30 min) + refresh token (7 jours)
- Mots de passe bcrypt
- API keys avec scopes et rate limiting
- 7 comptes démo pré-configurés

### 10.2 RBAC

| Rôle | Permissions |
|------|------------|
| `admin` | CRUD users, full system access |
| `expert` | Intentions, arbitrage, compliance, vault |
| `operator` | Intentions lecture, vault lecture |
| `viewer` | Dashboard lecture seule |

### 10.3 Circuit Breaker

**Fichier :** `core/security/circuit_breaker.py`

- Seuil : 5 échecs consécutifs
- Recovery : 60 secondes en half-open
- Max requêtes half-open : 3

### 10.4 Chiffrement Fernet

**Fichier :** `core/security/encryption.py`

- Chiffrement at-rest pour PII et secrets
- AES-128-CBC via Fernet (cryptography)
- Rotation des clés supportée

### 10.5 AutoDefense

**Fichier :** `core/security/guardrails/autodefense.py`

- 3 validateurs indépendants en parallèle
- Vote majoritaire (2/3 = blocage)
- Anti-jailbreak + anti-prompt-injection

### 10.6 Horodatage RFC 3161

**Fichier :** `core/security/timestamp.py`

| Provider | Qualifié | Usage |
|----------|---------|-------|
| `swisssign` | ✅ ZertES | Production CH |
| `certigna` | ✅ eIDAS | Production FR |
| `digicert` | ❌ Non certifié | Tests |
| `local_hmac` | ❌ Dev only | Développement |

Fallback automatique vers HMAC si TSA indisponible.

---

## 11. RAG ChromaDB

**Fichier :** `core/integrations/rag/__init__.py`

### Caractéristiques

| Propriété | Valeur |
|-----------|--------|
| Vector store | ChromaDB (persistant) |
| Embeddings | all-MiniLM-L6-v2 (local) |
| Chunking | 500 caractères, overlap 50 |
| Métrique | Cosine similarity |
| Isolation | Collection par client (hash MD5) |

### Collections

- `cl_{hash}` : documents client (isolés)
- `cl_regulatory` : textes réglementaires (partagé, filtré par vertical)

### Droit à l'oubli

```python
rag.delete_client_data("client-123")  # Supprime la collection
```

---

## 12. LLM Provider

**Fichier :** `core/integrations/llm/provider.py`

| Mode | Provider | Modèle défaut |
|------|----------|---------------|
| Standard | OpenRouter | mistral-small-3.1-24b-instruct |
| Haute Protection | Ollama | mistral:7b |

Configuration via `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_MODEL`.

---

## 13. Frontend

**Répertoire :** `frontend/src/`

| Tech | Version |
|------|---------|
| React | 19.2.5 |
| Vite | 8.0.10 |
| TypeScript | 6.0.2 |
| React Router | 6.30.3 |
| Lucide React | 1.11.0 |

### Pages

| Page | Fichier | Description |
|------|---------|-------------|
| Landing | `LandingPage.tsx` | Page marketing + démo verticales |
| Login | `pages/LoginPage.tsx` | Authentification JWT |
| Dashboard | `pages/DashboardPage.tsx` | 6 sections, agent flow |

### Composants

- `AgentFlowAnimation.tsx` — Animation du flux d'agents
- `ChatPanel.tsx` — Chat conversationnel
- `MarketSection.tsx` — Section marché vertical
- `VerticalDemoResult.tsx` — Résultat démo par verticale

---

## 14. API Reference

**Fichier :** `api/main.py` — 51 endpoints

### Par domaine

| Domaine | Endpoints | Routes clés |
|---------|-----------|-------------|
| Système | 2 | `/health`, `/metrics` |
| Auth | 7 | `/auth/login`, `/auth/register`, `/auth/api-keys` |
| Admin | 3 | `/admin/users`, `/admin/audit` |
| Intentions | 3 | `/intentions`, `/intentions/{id}/history` |
| Arbitrage | 4 | `/arbitrations`, `/arbitrations/{id}/decide`, `/arbitrations/precedents` |
| Journal | 2 | `/journal`, `/journal/verify` |
| Agents | 2 | `/agents/status`, `/agents/assemble-team` |
| Compliance | 3 | `/compliance/report/daily`, `/compliance/data-residency` |
| Médiateur | 2 | `/mediator/rules`, `/mediator/conflicts` |
| LLM | 2 | `/llm/health`, `/llm/generate` |
| n8n | 3 | `/n8n/health`, `/n8n/workflows`, `/n8n/trigger` |
| Vault | 5 | `/vault/clients`, `/vault/documents`, `/vault/search` |
| RAG | 5 | `/rag/search`, `/rag/index`, `/rag/stats`, `/rag/client/{id}` |
| Chat+Protocoles | 4 | `/chat`, `/mcp`, `/a2a`, `/guardrails/autodefense` |

---

## 15. Configuration (.env)

**Fichier :** `.env.example`

### Variables clés

| Variable | Défaut | Description |
|----------|--------|-------------|
| `APP_MODE` | `standard` | `standard` ou `haute_protection` |
| `NATS_URL` | `nats://localhost:4222` | Bus événementiel |
| `JOURNAL_SIGNING_KEY` | `change_this` | Clé HMAC du journal |
| `LLM_PROVIDER` | `openrouter` | `openrouter` ou `ollama` |
| `MEDIATOR_DEFAULT_FREEZE_THRESHOLD` | `10000` | Seuil gel par défaut (CHF) |
| `ARBITRATION_ESCALATION_CHAIN` | `["expert", "expert_suppleant", "associe"]` | Chaîne d'escalade |
| `ARBITRATION_ESCALATION_TIMEOUT_HOURS` | `[2.0, 4.0, 8.0]` | Timeouts par niveau |
| `ARBITRATION_TIMESTAMP_PROVIDER` | `local_hmac` | Provider horodatage RFC 3161 |
| `ENCRYPTION_ENABLED` | `true` | Chiffrement Fernet at-rest |
| `DATABASE_URL` | SQLite dev / PostgreSQL prod | Base de données |

---

## 16. Base de données

**Fichier :** `core/db/models.py`

### Tables

| Table | Description |
|-------|-------------|
| `users` | Utilisateurs avec RBAC, PII chiffrable |
| `api_keys` | Clés API avec scopes et rate limiting |
| `audit_logs` | Journal d'audit DB (complément WORM) |
| `tenants` | Multi-tenancy (Sprint 2.2) |

### Migrations

Alembic avec fichier initial : `alembic/versions/f94c56f6cc71_initial_tables.py`

---

## 17. Monitoring & Tracing

### Prometheus

**Fichier :** `monitoring/metrics.py`

- Endpoint `/metrics` au format Prometheus
- Counters, Histograms, Gauges
- Registry custom

### OpenTelemetry

**Fichier :** `monitoring/tracing.py`

- Distributed tracing multi-agents
- Dégradation gracieuse si OTel non installé
- Spans par agent (latence, health)

### Grafana

**Fichier :** `monitoring/grafana-dashboard.json`

- Dashboard pré-configuré pour Cortex Leman

---

## 18. CI/CD

**Fichier :** `.github/workflows/ci.yml`

### Pipeline (5 jobs)

| Job | Trigger | Actions |
|-----|---------|---------|
| Backend | Push + PR | 8 matrix groups × pytest + coverage ≥ 60% |
| Frontend | Push + PR | npm ci → tsc → build → artifact |
| Docker | Push main | Build + Trivy security scan |
| Security | Push + PR | pip-audit + npm audit |
| Deploy | Push main | Staging deploy |

---

## 19. Déploiement

### Mode Standard

```bash
docker-compose up -d
# NATS + Redis + PostgreSQL + API
# LLM: OpenRouter (cloud)
```

### Mode Haute Protection

```bash
./edge/k3s-install.sh
./edge/ollama-setup.sh
# K3s + Ollama (local)
# LLM: Ollama (local, air-gap possible)
```

---

## 20. Verticales Métier

### Comptable (7 règles)
- Références : RGPD, LBA, AFC, NEP
- Seuil gel : 10 000 CHF
- Docs seed : 5

### Avocat (4 règles)
- Références : CP Art. 321, nLPD, déontologie
- Seuil gel : 0 (par type d'action)
- Mode requis : Haute Protection
- Docs seed : 4

### Santé (3 règles)
- Références : RGPD, LPM, FMH, HDS
- Seuil gel : 0 (par type de données)
- Mode requis : Haute Protection
- Docs seed : 3

### Banque (3 règles)
- Références : LB Art. 47, FINMA, Bâle
- Seuil gel : 15 000 CHF (KYC renforcé)
- Mode requis : Haute Protection
- Docs seed : 3

### Startup (2 règles)
- Références : AI Act, RGPD
- Seuil gel : 10 000 CHF
- Mode requis : Standard
- Docs seed : 2

### RH (3 règles)
- Références : AI Act, Code travail
- Seuil gel : 10 000 CHF
- Mode requis : Standard / Haute
- Docs seed : 3

---

## 21. Tests

### Répartition

| Fichier | Tests | Couverture |
|---------|-------|------------|
| `test_ag2_insights.py` | 39 | MCP, A2A, AutoDefense, Tracing |
| `test_auth.py` | 41 | JWT, RBAC, CRUD |
| `test_e2e_trust_graph.py` | 42 | Flux complets E2E |
| `test_hardening.py` | 17 | Sécurité, encryption |
| `test_integrations.py` | 15 | LLM, n8n, vault, RAG |
| `test_journal.py` | 8 | WORM, intégrité, hash |
| `test_llm_rag.py` | 21 | LLM provider, RAG ChromaDB |
| `test_mediator.py` | 10 | Règles JsonLogic |
| `test_orchestrator.py` | 9 | Intention, routage |
| `test_saga.py` | 13 | Saga, compensation, freeze |
| `test_sprint2_p0_p1.py` | 31 | Mode dégradé, escalade, seuils, RFC 3161 |
| **Total** | **246** | |

### Exécution

```bash
# Tous les tests
.venv/bin/python -m pytest tests/ -v

# Tests Sprint 2 uniquement
.venv/bin/python -m pytest tests/test_sprint2_p0_p1.py -v

# Coverage
.venv/bin/python -m pytest tests/ --cov=core --cov-report=html
```

---

## 22. Glossaire

| Terme | Définition |
|-------|------------|
| **WORM** | Write Once Read Many — journal append-only immuable |
| **JsonLogic** | Moteur de règles déterministe basé sur JSON |
| **HMAC** | Hash-based Message Authentication Code |
| **TSA** | Time Stamp Authority — autorité d'horodatage |
| **RFC 3161** | Protocole d'horodatage qualifié |
| **ZertES** | Loi suisse sur les services de certification |
| **eIDAS** | Règlement européen sur l'identification électronique |
| **MCP** | Model Context Protocol — protocole d'accès RAG |
| **A2A** | Agent-to-Agent Protocol |
| **RBAC** | Role-Based Access Control |
| **Saga** | Pattern de transaction distribuée avec compensation |
| **Circuit Breaker** | Pattern de protection contre les pannes en cascade |
| **Fernet** | Format de chiffrement symétrique (AES-128-CBC) |
| **ChromaDB** | Vector store pour recherche sémantique |
| **RAG** | Retrieval-Augmented Generation |
| **NATS JetStream** | Bus de messages persistant |
| **K3s** | Kubernetes léger pour déploiement edge |
| **DEGRADED_FROZEN** | État où Action est bloqué mais Data/Raisonnement continuent |

---

*Base de connaissance générée à partir du code source Cortex Leman v5.2*  
*246/246 tests ✅ • 51 endpoints • 33 sujets NATS • 22 règles JsonLogic*
