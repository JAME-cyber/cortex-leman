# Cortex Leman v5 — Questions d'Audit

> Document préparatoire à l'audit de certification L4.
> Organisation par domaine. Chaque question inclut la référence réglementaire,
> la réponse attendue, et le fichier/endpoint concerné.

**Version :** 5.2 — Sprint 2  
**Dernière mise à jour :** 30 avril 2026

---

## Table des matières

1. [Gouvernance & Conformité](#1-gouvernance--conformité)
2. [Architecture & Séparation des pouvoirs](#2-architecture--séparation-des-pouvoirs)
3. [Journal WORM & Traçabilité](#3-journal-worm--traçabilité)
4. [Médiateur & Règles JsonLogic](#4-médiateur--règles-jsonlogic)
5. [Arbitrage Humain & Escalade](#5-arbitrage-humain--escalade)
6. [Mode Dégradé Conforme](#6-mode-dégradé-conforme)
7. [Sécurité & Chiffrement](#7-sécurité--chiffrement)
8. [Données Personnelles & RGPD](#8-données-personnelles--rgpd)
9. [LLM & Maîtrise des modèles](#9-llm--maîtrise-des-modèles)
10. [Infrastructure & Déploiement](#10-infrastructure--déploiement)
11. [RAG & Vectoriel](#11-rag--vectoriel)
12. [Protocoles externes (MCP/A2A)](#12-protocoles-externes-mcpa2a)
13. [Tests & Qualité](#13-tests--qualité)
14. [Continuité de service](#14-continuité-de-service)

---

## 1. Gouvernance & Conformité

### Q1.1 — Quel est le cadre juridique applicable ?

**Références :** RGPD (UE 2016/679), AI Act (UE 2024/1689), Code pénal suisse Art. 321, Loi sur les banques Art. 47, LPM, LBA, nLPD, ZertES

**Réponse attendue :**
- Le système opère dans un cadre **bifront** franco-suisse
- 6 verticales réglementées avec références spécifiques par métier
- Le mode Haute Protection garantit la résidence des données en Suisse (FINMA/Art. 47 LB)
- Conformité AI Act : le système est classé **high-risk** pour santé et bancaire

**Preuve :** `core/mediator/rules/*.json`, `core/config.py` → `compliance_data_residency`

---

### Q1.2 — Qui est responsable du traitement ?

**Référence :** RGPD Art. 4(17), Art. 28

**Réponse attendue :**
- Le cabinet/client est **responsable de traitement**
- Cortex Leman est **sous-traitant** en mode SaaS
- En mode Haute Protection (edge), le client héberge lui-même → il est responsable ET sous-traitant
- Le modèle `TenantModel` prépare le multi-tenancy avec DPO désigné (`dpo_email`)

**Preuve :** `core/db/models.py` → `TenantModel.dpo_email`, `data_residency`

---

### Q1.3 — Comment le consentement est-il recueilli ?

**Référence :** RGPD Art. 6, Art. 7, Art. 9 (données sensibles)

**Réponse attendue :**
- Chaque utilisateur a `consent_given: bool` et `consent_date: datetime`
- Pour les données de santé (Art. 9) : consentement explicite vérifié par la règle `sante-003`
- Le RAG implémente le droit à l'oubli : `DELETE /api/v1/rag/client/{client_id}`
- Durée de rétention configurable par tenant : `data_retention_days`

**Preuve :** `core/db/models.py` → `UserModel.consent_given`, `core/integrations/rag/__init__.py` → `delete_client_data()`

---

### Q1.4 — Quelle est la politique de rétention des données ?

**Référence :** RGPD Art. 5(1)(e), LPM Art. 321

**Réponse attendue :**
- Journal WORM : rétention 365 jours par défaut (configurable via `nats_max_age_days`)
- Documents clients : `data_retention_days` par utilisateur (défaut 365)
- Précédents d'arbitrage : conservation permanente (precedents.json)
- Le RAG nettoie les collections client sur demande (`delete_client_data`)

**Preuve :** `core/config.py`, `core/journal/append_only_journal.py`

---

## 2. Architecture & Séparation des pouvoirs

### Q2.1 — Comment la séparation des pouvoirs est-elle garantie ?

**Réponse attendue :**
- **Orchestrateur** : route les intentions, ne prend JAMAIS de décision de gel
- **Médiateur** : décide du gel, ne route JAMAIS les intentions
- **Agent Action** : exécute, ne décide JAMAIS du gel — vérifie `is_action_blocked()` en premier
- **Superviseur** : observe, n'interfère JAMAIS dans les décisions
- **Arbitrage** : l'humain tranche, l'IA ne fait que préparer le dossier

**Preuve :**
- `core/mediator/mediator.py` → ne publie jamais sur `INTENTION_ROUTE`
- `core/agents/action_agent.py` → vérifie `is_action_blocked()` avant exécution
- `core/orchestrator/conversationnal.py` → ne publie jamais sur `MEDIATOR_FREEZE`

---

### Q2.2 — Qui a le dernier mot entre l'Orchestrateur et le Médiateur ?

**Réponse attendue :**
- Le Médiateur est **prioritaire** sur l'Orchestrateur pour toute décision de gel
- L'Orchestrateur ne peut PAS passer outre un gel — c'est architecturalement impossible :
  1. L'Orchestrateur publie sur `MEDIATOR_CHECK` avant de router vers l'Action
  2. L'Action vérifie `is_action_blocked()` en PREMIER, avant toute exécution
  3. Le Médiateur peut geler même sans requête de l'Orchestrateur (via `AGENT_RESULT`)
- Le gel dégradé respecte le même principe : Action bloqué, Data/Raisonnement continuent

**Preuve :** `core/agents/action_agent.py` lignes 79-107, `core/mediator/mediator.py` → `_on_agent_result`

---

### Q2.3 — Quels composants utilisent un LLM et lesquels sont déterministes ?

**Réponse attendue :**

| Composant | LLM ? | Raison |
|-----------|-------|--------|
| Orchestrateur | Oui | Compréhension du langage naturel |
| Agent Data | Oui | Recherche sémantique |
| Agent Raisonnement | Oui | Analyse juridique |
| **Agent Action** | **NON** | Exécution programmatique |
| **Médiateur** | **NON** | 22 règles JsonLogic déterministes |
| **Superviseur V2** | **NON** | Seuils numériques + health board |
| **Journal WORM** | **NON** | SHA-256 + HMAC |
| **AutoDefense** | **NON** | 3 validateurs regex + vote majoritaire |

**Preuve :** chaque agent a son fichier dans `core/agents/`, les agents programmatiques n'importent jamais le LLM provider

---

### Q2.4 — Comment les intentions évoluent-elles dans le système ?

**Réponse attendue :**
State machine à 10 états avec transitions validées :

```
created → routed → processing → frozen → arbitrating → unfrozen → processing
                                → degraded_frozen → arbitrating
                  → failed
                  → completed
```

Chaque transition est journalisée dans `IntentionStore._history` avec horodatage, trigger et raison.

**Preuve :** `core/orchestrator/intention.py` → `VALID_TRANSITIONS`, `_transition()`

---

## 3. Journal WORM & Traçabilité

### Q3.1 — Comment le journal garantit-il l'intégrité ?

**Réponse attendue :**
- Append-only : pas de modification, pas de suppression
- Hash-chainage SHA-256 : chaque entrée contient le hash de la précédente
- Signature HMAC : chaque entrée est signée avec la clé `journal_signing_key`
- Vérification en continu : `verify_integrity()` parcourt toute la chaîne
- Fichier journal par jour : rotation automatique

**Preuve :** `core/journal/append_only_journal.py` → `_compute_hash()`, `_sign_entry()`, `verify_integrity()`

---

### Q3.2 — Que se passe-t-il si une écriture échoue ?

**Réponse attendue :**
- Le séquenceur est rollbacké (`self._sequence -= 1`)
- Une `RuntimeError` est levée — l'appelant doit la gérer
- Le hash de la chaîne n'est pas mis à jour → la prochaine écriture chaîne sur le dernier hash valide
- Le journal ne peut PAS être dans un état incohérent (atomic write via fichier `.tmp` → `replace()`)

**Preuve :** `core/journal/append_only_journal.py` → `append()`, bloc try/except

---

### Q3.3 — Combien d'événements sont journalisés ?

**Réponse attendue :** 18 types d'événements couvrant :
- Intentions (created, revised, cancelled, routed)
- Agents (query, result, error)
- Médiateur (check, conflict, freeze, unfreeze)
- Arbitrage (requested, decision, precedent)
- Actions (executed, compensated)
- Compliance (check, violation)
- Système (start, health, error)

**Preuve :** `core/journal/models.py` → `JournalEventType`

---

### Q3.4 — L'horodatage est-il qualifié au sens eIDAS/ZertES ?

**Réponse attendue :**
- En mode développement : HMAC local (non qualifié, pour tests uniquement)
- En mode production : connecteur RFC 3161 vers SwissSign (ZertES) ou Certigna (eIDAS)
- Configuration via `ARBITRATION_TIMESTAMP_PROVIDER` dans `.env`
- Fallback automatique vers HMAC si le TSA distant est indisponible
- Le token qualifié est persisté dans `data/journal/timestamps/` pour vérification ultérieure
- Le champ `qualified: true/false` dans le token distingue les deux modes

**Preuve :** `core/security/timestamp.py` → `TimestampService`, `RFC3161Timestamp`

---

## 4. Médiateur & Règles JsonLogic

### Q4.1 — Combien de règles le Médiateur applique-t-il ?

**Réponse attendue :** 22 règles réparties sur 6 verticales :
- Comptable : 7 règles (gel montant, déduction fiscale, etc.)
- Avocat : 4 règles (secret professionnel, LLM local, conclusions, data residency)
- Santé : 3 règles (HDS, diagnostic automatique, consentement)
- Banque : 3 règles (secret bancaire, infrastructure CH, KYC ≥ 15K)
- RH : 3 règles (anti-discrimination, etc.)
- Startup : 2 règles

Plus un gel par défaut configurable par verticale.

**Preuve :** `core/mediator/rules/*.json`, `core/mediator/rules_engine.py`

---

### Q4.2 — Les règles peuvent-elles être modifiées sans toucher au code ?

**Réponse attendue :**
- Oui. Les règles sont dans des fichiers JSON externes (`core/mediator/rules/*.json`)
- Le `RulesEngine` les charge dynamiquement via `load_rules()`
- Un redémarrage du service recharge les règles
- En mode production, un endpoint `GET /api/v1/mediator/rules` permet de lister les règles actives
- Un Policy Manager UI est prévu au Sprint 3

---

### Q4.3 — Comment les seuils de gel sont-ils déterminés ?

**Réponse attendue :**
- Chaque verticale a un seuil propre dans `mediator._freeze_thresholds` :
  - Comptable : 10 000 CHF (défaut configurable)
  - Banque : 15 000 CHF (KYC renforcé)
  - Avocat : 0 (gel par type d'action, pas par montant)
  - Santé : 0 (gel par type de données, pas par montant)
  - Startup/RH : 10 000 CHF (défaut)
- Le seuil par défaut est configurable via `MEDIATOR_DEFAULT_FREEZE_THRESHOLD` dans `.env`
- Les règles JsonLogic propres à chaque verticale s'appliquent EN PLUS du seuil

**Preuve :** `core/mediator/mediator.py` → `_freeze_thresholds`, `core/config.py`

---

### Q4.4 — Comment le Médiateur gère-t-il les comparaisons avec des valeurs manquantes ?

**Réponse attendue :**
- Le wrapper `jsonLogic` est **null-safe** : toute comparaison numérique avec `None` retourne `False` au lieu de crasher
- Un montant absent ne déclenche jamais de gel par défaut
- Le fallback natif implémente la même logique null-safe

**Preuve :** `core/mediator/rules_engine.py` → wrapper null-safe

---

## 5. Arbitrage Humain & Escalade

### Q5.1 — Comment l'arbitrage est-il structuré ?

**Réponse attendue :**
1. Le Médiateur détecte un conflit → gel (complet ou dégradé)
2. L'ArbitrationService prépare un dashboard avec les positions contradictoires
3. L'expert humain voit : recommandation de chaque agent, confiance, sources, risques, références réglementaires
4. L'expert tranche avec : décision (approve/reject/modify), justification textuelle, position sélectionnée
5. La décision est : signée, horodatée, enregistrée comme précédent, journalisée WORM

**Preuve :** `core/arbitration/arbitration_service.py` → `prepare_arbitration()`, `submit_decision()`

---

### Q5.2 — Que se passe-t-il si l'arbitre ne répond pas ?

**Réponse attendue :**
- File d'escalade configurable : `expert → expert_suppleant → associe`
- Timeouts configurables : `2h → 4h → 8h` par défaut
- À chaque timeout, le système :
  1. Journalise l'escalade dans le WORM (niveau from → to)
  2. Assigne le dashboard à l'arbitre suivant
  3. Met à jour la deadline
- Si tous les niveaux sont épuisés : statut `escalation_exhausted`, notification admin

**Preuve :** `core/arbitration/arbitration_service.py` → `_escalation_loop()`

---

### Q5.3 — L'historique d'escalade est-il persisté ?

**Réponse attendue :**
- Oui. Chaque escalade est journalisée dans le WORM via `JournalEventType.ARBITRATION_REQUESTED` avec payload `event: "escalation"`
- Le dashboard stocke aussi l'historique dans `escalation_history` (en mémoire + persisté dans les arbitrages pending)
- ⚠️ Point de robustesse identifié : les timers asyncio sont volatils au redémarrage. Une persistance NATS KV ou Redis des timers en cours est recommandée pour la certification L4.

**Preuve :** `core/arbitration/arbitration_service.py` → `_escalation_loop()`, journalisation dans le WORM

---

### Q5.4 — Comment les précédents d'arbitrage enrichissent-ils le système ?

**Réponse attendue :**
- Chaque décision est sauvegardée dans `data/precedents.json`
- La force du précédent évolue : `weak → moderate → strong` selon le nombre de décisions similaires
- Les précédents sont consultables via `GET /api/v1/arbitrations/precedents`
- Dans le futur, les précédents pourront enrichir les règles JsonLogic automatiquement

**Preuve :** `core/arbitration/arbitration_service.py` → `_save_precedent()`

---

## 6. Mode Dégradé Conforme

### Q6.1 — Qu'est-ce que le mode dégradé conforme ?

**Réponse attendue :**
- État `DEGRADED_FROZEN` : l'Agent Action est bloqué, mais Data et Raisonnement continuent de travailler
- Objectif : enrichir le dossier d'arbitrage pendant le gel, réduire la latence perçue
- L'arbitre humain reçoit un dossier plus complet quand il tranche
- Chaque résultat de Data/Raisonnement pendant le gel dégradé est publié sur `cleman.mediator.degraded_freeze` avec `event: "enrichment"`

**Preuve :** `core/orchestrator/intention.py` → `IntentionState.DEGRADED_FROZEN`, `core/mediator/mediator.py` → gestion dégradé

---

### Q6.2 — Comment éviter les race conditions dégel/résultat en vol ?

**Réponse attendue :**
- ⚠️ Point identifié : si l'arbitrage est résolu (dégel) alors qu'un résultat Data/Raisonnement est en vol sur le bus, ce résultat pourrait être perdu
- Solution actuelle : le Médiateur stocke les positions dans `_agent_positions` qui persiste au-delà du dégel
- Recommandation Sprint 3 : ajouter une fenêtre de consolidation de 5 secondes après le dégel pour capturer les résultats en vol
- Le dashboard d'arbitrage doit lire `agent_positions` même après le dégel pour consolider

---

### Q6.3 — Peut-on passer du mode dégradé au gel complet ?

**Réponse attendue :**
- Oui. La transition `DEGRADED_FROZEN → FROZEN` est autorisée dans la state machine
- Cas d'usage : si un résultat Data en mode dégradé révèle un risque critique supplémentaire
- Le Médiateur peut décider d'escalader le gel de dégradé → complet

**Preuve :** `core/orchestrator/intention.py` → `VALID_TRANSITIONS[DEGRADED_FROZEN]` inclut `FROZEN`

---

## 7. Sécurité & Chiffrement

### Q7.1 — Quelles mesures de chiffrement sont en place ?

**Référence :** RGPD Art. 32

**Réponse attendue :**
- **At-rest :** chiffrement Fernet (AES-128-CBC) pour les PII et secrets clients (`core/security/encryption.py`)
- **In-transit :** TLS sur tous les endpoints API
- **Journal :** HMAC-SHA-256 sur chaque entrée
- **Clés :** rotation supportée via `SECRET_KEY` et `journal_signing_key` dans `.env`
- **mTLS :** supporté mais désactivé par défaut (`MTLS_ENABLED=false`)

**Preuve :** `core/security/encryption.py`, `core/config.py` → `encryption_enabled`

---

### Q7.2 — Comment les mots de passe sont-ils protégés ?

**Réponse attendue :**
- Hash bcrypt via passlib (`password_hash` dans `UserModel`)
- Pas de stockage en clair — seul le hash est en base
- Politique de changement forcé : `must_change_password` pour les comptes seedés
- JWT avec access token (30 min) + refresh token (7 jours)

**Preuve :** `core/security/auth.py` → `hash_password()`, `verify_password()`

---

### Q7.3 — Comment fonctionne l'AutoDefense ?

**Réponse attendue :**
- 3 validateurs indépendants en parallèle (inspiré du paper AG2 AutoDefense)
- Chaque validateur analyse le prompt utilisateur pour détecter :
  - Les tentatives de jailbreak
  - Les injections de prompt
  - Les demandes hors périmètre
- Vote majoritaire : si 2/3 validateurs bloquent → le prompt est rejeté
- Résultat journalisé dans le WORM

**Preuve :** `core/security/guardrails/autodefense.py`

---

### Q7.4 — Quels sont les Contrôle d'Accès ?

**Réponse attendue :**
- RBAC à 4 niveaux : `admin > expert > operator > viewer`
- Permissions par ressource (users, intentions, arbitrations, compliance, vault, etc.)
- API keys avec scopes et rate limiting
- Audit de toutes les actions sensibles dans `audit_logs`

**Preuve :** `core/security/auth.py` → `PERMISSIONS`, `has_permission()`

---

## 8. Données Personnelles & RGPD

### Q8.1 — Comment le droit à l'oubli est-il implémenté ?

**Référence :** RGPD Art. 17

**Réponse attendue :**
- Endpoint dédié : `DELETE /api/v1/rag/client/{client_id}`
- Supprime la collection ChromaDB du client (tous les chunks vectorisés)
- Le journal WORM conserve la trace de la suppression (immuabilité légale)
- Les intentions et rapports du client sont marqués comme supprimés

**Preuve :** `core/integrations/rag/__init__.py` → `delete_client_data()`

---

### Q8.2 — L'isolation des données entre clients est-elle garantie ?

**Réponse attendue :**
- RAG : collections ChromaDB séparées par client (`cl_{hash(client_id)}`)
- Journal : filtrage par `client_id` dans les requêtes
- API : vérification RBAC + tenant_id (Sprint 2.2)
- Mode Haute Protection : données physiquement sur l'infrastructure du client

**Preuve :** `core/integrations/rag/__init__.py` → `_get_collection()`, hash MD5 du client_id

---

### Q8.3 — Les données sensibles (santé, bancaire) ont-elles un traitement spécifique ?

**Référence :** RGPD Art. 9, LPM, Art. 47 LB

**Réponse attendue :**
- Santé : hébergement HDS obligatoire (règle `sante-001`), consentement explicite (`sante-003`)
- Banque : infrastructure en Suisse obligatoire (règle `banque-002`), secret bancaire (`banque-001`)
- Avocat : aucune donnée ne sort du cabinet (règle `avocat-001`), LLM local uniquement (`avocat-002`)
- Chiffrement Fernet des PII en base

**Preuve :** `core/mediator/rules/sante.json`, `banque.json`, `avocat.json`

---

## 9. LLM & Maîtrise des modèles

### Q9.1 — Quels modèles de langage sont utilisés ?

**Réponse attendue :**
- Mode Standard : OpenRouter (cloud), modèle configurable (`mistral-small-3.1-24b-instruct` par défaut)
- Mode Haute Protection : Ollama (local), modèle configurable (`mistral:7b` recommandé)
- Le provider est configurable via `LLM_PROVIDER` et `LLM_BASE_URL`
- Timeout configurable : `LLM_TIMEOUT = 60s` par défaut

**Preuve :** `core/integrations/llm/provider.py`, `core/config.py`

---

### Q9.2 — Le système peut-il fonctionner sans LLM ?

**Réponse attendue :**
- Oui, partiellement. Les composants déterministes (Médiateur, Action, Superviseur, Journal) fonctionnent sans LLM
- L'Orchestrateur, l'Agent Data et l'Agent Raisonnement nécessitent un LLM
- Si le LLM est indisponible : le Circuit Breaker ouvre, les intentions en attente sont reportées, le journal enregistre l'erreur
- Le système ne plante jamais à cause d'un LLM indisponible

**Preuve :** `core/security/circuit_breaker.py`

---

### Q9.3 — Comment les hallucinations sont-elles détectées ?

**Réponse attendue :**
- Le Superviseur vérifie la confiance des résultats : si < 0.3 → `hallucination_check` échoue
- L'Agent Raisonnement doit citer ses sources (skill requirement)
- Le RAG injecte du contexte réel dans les prompts LLM pour ancrer les réponses
- L'AutoDefense analyse les sorties pour détecter les incohérences

**Preuve :** `core/agents/supervisor_agent.py` → `_check_hallucination()`

---

## 10. Infrastructure & Déploiement

### Q10.1 — Quelle est l'infrastructure minimale ?

**Réponse attendue :**
- Docker Compose avec 4 services : NATS, Redis, PostgreSQL, API
- Requirements : Python 3.12, 2 GB RAM minimum, 10 GB stockage
- Mode Haute Protection : K3s sur infrastructure locale (edge)

**Preuve :** `docker-compose.yml`, `edge/k3s-install.sh`

---

### Q10.2 — Comment la CI/CD garantit-elle la qualité ?

**Réponse attendue :**
- GitHub Actions avec 5 jobs :
  1. Backend : 8 groupes de tests en matrice × pytest + coverage ≥ 60%
  2. Frontend : npm ci → TypeScript check → build production
  3. Docker : build image + Trivy security scan (HIGH/CRITICAL)
  4. Security : pip-audit + npm audit
  5. Deploy : déploiement preview sur staging (main only)
- Services CI : PostgreSQL 16 + Redis 7

**Preuve :** `.github/workflows/ci.yml`

---

### Q10.3 — Quelle est la politique de sauvegarde ?

**Réponse attendue :**
- Journal WORM : fichiers JSON-L avec rotation journalière
- PostgreSQL : sauvegardes via Alembic migrations
- ChromaDB : persistance locale dans `data/chroma_db`
- Docker volumes : `nats-data`, `redis-data`, `postgres-data`, `journal-data`, `reports-data`

**Preuve :** `docker-compose.yml` → volumes, `alembic/`

---

## 11. RAG & Vectoriel

### Q11.1 — Quel moteur de recherche sémantique est utilisé ?

**Réponse attendue :**
- ChromaDB avec embeddings `all-MiniLM-L6-v2` (local, pas d'API externe)
- Chunking : 500 caractères avec overlap de 50
- Métrique : cosinus (cosine similarity)
- Haute Protection : tout reste en local, aucun appel externe

**Preuve :** `core/integrations/rag/__init__.py` → `RAGService`

---

### Q11.2 — Les documents réglementaires sont-ils vectorisés ?

**Réponse attendue :**
- Oui. 6 fichiers JSON dans `data/vault/regulatory/` (un par verticale)
- Chargement via `POST /api/v1/rag/regulatory/seed`
- Recherche par verticale : filtrage `vertical` dans ChromaDB
- Endpoint de stats : `GET /api/v1/rag/stats`

**Preuve :** `data/vault/regulatory/*.json`, `core/integrations/rag/__init__.py` → `index_regulatory()`

---

## 12. Protocoles externes (MCP/A2A)

### Q12.1 — Quels protocoles d'interopérabilité sont supportés ?

**Réponse attendue :**
- **MCP** (Model Context Protocol) : expose le RAG via JSON-RPC 2.0 sur `POST /mcp`
  - Tools : `rag_search`, `rag_regulatory`, `rag_stats`
  - Compatible Claude Desktop, Cursor, etc.
- **A2A** (Agent-to-Agent) : bridge NATS ↔ protocole A2A sur `POST /a2a`
  - Messages : discover, send_message, get_status, subscribe
  - Compatible AG2, CrewAI, agents tiers

**Preuve :** `core/integrations/mcp_server.py`, `core/integrations/a2a_adapter.py`

---

### Q12.2 — Les protocoles externes contournent-ils le Médiateur ?

**Réponse attendue :**
- Non. Les requêtes MCP et A2A passent par l'API FastAPI qui est soumise au même Contrôle d'accès RBAC
- Toute action résultant d'une requête MCP/A2A suit le même flux : Intention → Orchestrateur → Agents → Médiateur → Journal WORM
- Les protocoles externes sont des interfaces, pas des circuits courts

---

## 13. Tests & Qualité

### Q13.1 — Quelle est la couverture de tests ?

**Réponse attendue :**
- **246 tests** sur 11 fichiers de test
- Coverage minimum : 60% (imposé par CI)
- Répartition :
  - `test_ag2_insights.py` : 39 tests (MCP, A2A, AutoDefense, Tracing)
  - `test_auth.py` : 41 tests (JWT, RBAC, CRUD utilisateurs)
  - `test_e2e_trust_graph.py` : 42 tests (flux complets end-to-end)
  - `test_hardening.py` : 17 tests (sécurité, encryption)
  - `test_integrations.py` : 15 tests (LLM, n8n, vault, RAG)
  - `test_journal.py` : 8 tests (WORM, intégrité, hash)
  - `test_llm_rag.py` : 21 tests (LLM provider, RAG ChromaDB)
  - `test_mediator.py` : 10 tests (règles JsonLogic)
  - `test_orchestrator.py` : 9 tests (intention, routage)
  - `test_saga.py` : 13 tests (saga, compensation, freeze)
  - `test_sprint2_p0_p1.py` : 31 tests (mode dégradé, escalade, seuils, horodatage)

**Preuve :** `tests/`, `.github/workflows/ci.yml` → coverage --fail-under=60

---

### Q13.2 — Les tests couvrent-ils les cas de gel et d'arbitrage ?

**Réponse attendue :**
- Oui. `test_saga.py` teste le gel complet (`test_frozen_intention_blocks_action`)
- `test_sprint2_p0_p1.py` teste le gel dégradé, les transitions d'état, les seuils par verticale
- `test_mediator.py` teste le déclenchement des règles block/freeze/warn
- `test_e2e_trust_graph.py` teste les flux complets incluant gel et arbitrage

---

## 14. Continuité de service

### Q14.1 — Que se passe-t-il si NATS est indisponible ?

**Réponse attendue :**
- Le Circuit Breaker ouvre après 5 échecs consécutifs
- Les agents ne peuvent plus communiquer → les intentions restent en `PROCESSING`
- Le journal WORM continue d'écrire en local (pas de dépendance NATS)
- Au redémarrage NATS : les agents se reconnectent et reprennent les intentions en attente

---

### Q14.2 — Que se passe-t-il si Redis est indisponible ?

**Réponse attendue :**
- Les verrous distribués ne peuvent plus être acquis → l'Agent Action ne peut pas exécuter de nouvelles opérations
- Les opérations en cours (verrou déjà acquis) continuent normalement
- Le cache est perdu → performance dégradée mais pas de perte de données

---

### Q14.3 — Quel est le RTO/RPO ?

**Réponse attendue :**
- RPO (Recovery Point Objective) : dépend de la fréquence de sauvegarde PostgreSQL (à définir en production)
- RTO (Recovery Time Objective) : redémarrage Docker Compose ≈ 2 minutes
- Mode Haute Protection : redémarrage K3s + Ollama ≈ 5 minutes
- ⚠️ Pas de haute disponibilité active (pas de leader election) — prévu Sprint 4

---

*Document généré automatiquement à partir du code source Cortex Leman v5.2*  
*Dernière vérification : 30 avril 2026 — 246/246 tests ✅*
