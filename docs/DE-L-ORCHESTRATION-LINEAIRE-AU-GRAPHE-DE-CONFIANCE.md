# Cortex Leman — De l'Orchestration Linéaire au Graphe de Confiance

**Document technique v5.0** — Dernière mise à jour : 24 avril 2026
**Statut :** Sprint 1 complété ✅ | Sprint 2 prêt 🔜

---

## Table des matières

1. [Pourquoi le pipeline a échoué](#1-pourquoi-le-pipeline-a-échoué)
2. [Le nouveau paradigme : Graphe de Confiance](#2-le-nouveau-paradigme--graphe-de-confiance)
3. [Architecture v5 complète](#3-architecture-v5-complète)
4. [Les 5 agents reconfigurés](#4-les-5-agents-reconfigurés)
5. [Le Médiateur — composant de sécurité central](#5-le-médiateur--composant-de-sécurité-central)
6. [Scénario de conflit type (validé)](#6-scénario-de-conflit-type-validé)
7. [Conformité réglementaire](#7-conformité-réglementaire)
8. [Données et datasets réglementaires](#8-données-et-datasets-réglementaires)
9. [Skills des agents IA](#9-skills-des-agents-ia)
10. [Bilan technique](#10-bilan-technique)

---

## 1. Pourquoi le pipeline a échoué

### Ce qu'était la v4.1

La version 4.1 utilisait un **pipeline séquentiel à 5 étapes** :

```
INTENTION → RECHERCHE → ANALYSE → EXECUTION → VALIDATION
   ↓           ↓           ↓           ↓           ↓
Orchestrateur  Agent Data  Raisonnement  Action    Superviseur
(routeur)     (scan)      (compare)    (exécute)  (valide)
```

### Les 5 failles identifiées

| # | Faille | Conséquence | Gravité |
|---|--------|-------------|---------|
| 1 | **Orchestrateur = simple aiguilleur** | Ne peut pas réviser l'intention en cours de traitement | HIGH |
| 2 | **Agent Data en vase clos** | Ne sait pas si le Raisonnement a besoin de compléments | MEDIUM |
| 3 | **Raisonnement sans boucle de rétroaction** | Détecte un conflit mais ne peut pas faire réviser l'intention | HIGH |
| 4 | **Action sans verrou de sécurité** | Peut exécuter une décision contestée au même moment | **CRITICAL** |
| 5 | **Superviseur trop tardif** | Ne voit que le résultat final, laisse passer les conflits | HIGH |

### Exemple concret du risque

```
Cabinet comptable → "Déduire 85 000 CHF R&D"

Pipeline v4.1:
  Data → "Circulaire AFC autorise déduction B1"
  Raisonnement → "Mais CA > 500K, B1 exclue"  ← personne n'écoute
  Action → EXÉCUTE B1 (85K)                    ← DANGER
  Superviseur → "Problème détecté"              ← TROP TARD

Résultat: Redressement fiscal potentiel pour le client.
```

---

## 2. Le nouveau paradigme : Graphe de Confiance

### Principes fondamentaux

1. **Pair-à-pair asynchrone** — les agents communiquent via un bus d'événements, pas en chaîne
2. **Médiateur transverse** — surveille en continu, peut geler à tout moment
3. **Gel préventif** — si conflit détecté, tout s'arrête avant exécution
4. **Humain arbitre, pas valideur** — l'expert tranche les exceptions, il ne valide pas chaque étape
5. **Médiateur = déterministe** — JsonLogic uniquement, jamais de LLM dans le rôle de sécurité

### La différence visuelle

```
AVANT (v4.1 — pipeline fragile):
  A → B → C → D → E
  • Linéaire, bloquant, sans retour

APRÈS (v5 — graphe de confiance):
       ┌──────────────────────┐
       │   ORCHESTRATEUR      │
       │   (hub permanent)    │
       └──────────┬───────────┘
                  │ NATS JetStream
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    ┌──────┐ ┌──────────┐ ┌──────┐
    │ DATA │ │RAISONNEM.│ │ACTION│
    │+comp.│ │+révision │ │+gel  │
    └──┬───┘ └────┬─────┘ │+saga │
       └──────┬───┘        └──┬───┘
       ┌──────▼────────────────▼───┐
       │      MÉDIATEUR            │
       │  22 règles JsonLogic      │
       │  Gel préventif            │
       └──────────┬────────────────┘
       ┌──────────▼────────────────┐
       │     SUPERVISEUR V2        │
       │  Observateur continu      │
       │  Health board temps réel  │
       └──────────┬────────────────┘
       ┌──────────▼────────────────┐
       │    ARBITRAGE HUMAIN       │
       │  L'expert décide          │
       └───────────────────────────┘
```

---

## 3. Architecture v5 complète

### Bus d'événements NATS JetStream

13 sujets organisés en 5 catégories :

```
Intentions:
  cleman.intention.new        — Nouvelle intention
  cleman.intention.revise     — Révision d'intention (par Raisonnement ou post-arbitrage)

Agents:
  cleman.data.query           — Requête vers Agent Data
  cleman.reasoning.analyze    — Analyse par Agent Raisonnement
  cleman.action.execute       — Exécution par Agent Action
  cleman.agent.result         — Résultat d'un agent (tous agents)

Médiateur:
  cleman.mediator.check       — Vérification explicite
  cleman.mediator.conflict    — Conflit détecté
  cleman.mediator.freeze      — Gel d'intention

Validation:
  cleman.validate.request     — Demande de validation (Superviseur)
  cleman.validate.result      — Résultat de validation

Arbitrage:
  cleman.arbitration.request  — Demande d'arbitrage humain
  cleman.arbitration.decision — Décision d'arbitrage
```

### Intention versionnée

```python
# États possibles d'une intention
active    → en cours de traitement
frozen    → gelée par le Médiateur (conflit détecté)
completed → traitée avec succès

# Exemple de cycle complet
v1: active   → créée par l'Orchestrateur
v2: frozen   → gelée par le Médiateur (conflit data vs raisonnement)
v3: active   → dégelée après arbitrage humain
v4: completed → action exécutée, journal complété
```

### Journal WORM

- Append-only, hash-chainé SHA-256
- Chaque entrée : `hash = SHA-256(previous_hash + payload + timestamp)`
- Fichiers : `data/journal/journal-{date}.jsonl`
- 106 entrées dans le journal actuel

### Sécurité multicouche

| Couche | Mécanisme | Fichier |
|--------|-----------|---------|
| Gel | Médiateur vérifie chaque résultat | `core/mediator/mediator.py` |
| Verrou | Action vérifie `intention.status != "frozen"` | `core/agents/action_agent.py` |
| Exclusion | Verrou distribué Redis | `core/security/distributed_lock.py` |
| Transaction | Saga avec compensation | `core/agents/saga/saga_manager.py` |
| Protection | Circuit breaker (seuil 5 échecs) | `core/security/circuit_breaker.py` |
| Traçabilité | Journal WORM immuable | `core/journal/append_only_journal.py` |
| Résidence | Compliance Gateway | `core/compliance/gateway.py` |

---

## 4. Les 5 agents reconfigurés

### Agent Data (`core/agents/data_agent.py`)

**Avant :** scanne les sources, retourne des résultats, ne parle à personne.

**Après :**
- Écoute `cleman.data.query` sur le bus NATS
- Publie résultats + scores de confiance sur `cleman.agent.result`
- **NOUVEAU :** écoute `cleman.data.complement` pour les demandes de complément
- Mode Haute Protection : sources locales uniquement

### Agent Raisonnement (`core/agents/reasoning_agent.py`)

**Avant :** compare, analyse, recommande. Ne dialogue qu'avec Data en entrée.

**Après :**
- Même logique d'analyse
- **NOUVEAU :** peut publier `cleman.intention.revise` si incohérence détectée
- Triggers de révision élargis : `threshold_exceeded`, `conflicting_data`, `compliance_violation`, confiance < 0.3
- Cible prioritaire pour intégration LLM (Sprint 2)

### Agent Action (`core/agents/action_agent.py`)

**Avant :** exécute sans filet. Peut agir pendant que la décision est contestée.

**Après :**
- **NOUVEAU :** vérifie `intention.status == "frozen"` AVANT chaque exécution
- **NOUVEAU :** verrou distribué Redis sur chaque intention
- Saga avec compensation pour chaque action externe
- Circuit breaker contre les échecs répétés
- **JAMAIS de LLM** — exécution transactionnelle pure

### Agent Superviseur V2 (`core/agents/supervisor_agent.py`)

**Avant :** valideur terminal. Voit le résultat final seulement.

**Après :**
- **Observateur continu** — écoute TOUS les résultats en temps réel
- 4 abonnements bus : `AGENT_RESULT`, `MEDIATOR_CONFLICT`, `MEDIATOR_FREEZE`, `ARBITRATION_DECISION`
- Maintient un **health board par intention** (`IntentionHealth`)
- Détecte les dégradations (confiance < 0.5 ou ≥ 2 conflits)
- Alerte via `cleman.supervisor.alert` si intention dégradée
- Prépare les dossiers d'arbitrage pour l'humain
- **JAMAIS de LLM**

### Orchestrateur conversationnel (`core/orchestrator/conversationnal.py`)

**Avant :** intervenait uniquement à l'étape 1 pour comprendre et router.

**Après :**
- Hub permanent, pas une étape séquentielle
- 6 abonnements NATS permanents
- Intention versionnée (création, révision, gel, dégel, complétion)
- Route dynamiquement via le Router (patterns regex + overrides par verticale)
- Peut réviser, préciser, bifurquer l'intention à tout moment

---

## 5. Le Médiateur — composant de sécurité central

### Pourquoi il ne doit JAMAIS utiliser de LLM

| Raison | Détail |
|--------|--------|
| **Non-déterminisme** | Un LLM peut ne pas geler une intention qu'il devrait geler |
| **Latence** | Ajoute 500ms-5s par vérification, or il intercepte CHAQUE résultat |
| **Auditabilité** | JsonLogic est reproductible, un LLM ne l'est pas |
| **Certification** | Aucun auditeur LSTI/SGS/AFNOR ne certifiera un gel probabiliste |

### Règles JsonLogic (22 règles)

| Verticale | Règles | Exemples |
|-----------|--------|----------|
| Comptable | 7 | Gel si déduction > 50K, gel si conflit de sources, arbitrage si > 10K |
| Avocat | 4 | Secret professionnel, data residency CH, confiance basse |
| Santé | 3 | Données patient, consentement, diagnostic IA |
| Banque | 3 | Secret bancaire, infrastructure CH, KYC/AML |
| RH | 3 | Anti-discrimination, décision auto, biais |
| Startup | 2 | Transparence IA, DPIA |

### Gel par défaut (ajout Sprint 1)

Si vertical sensible (comptable, avocat, banque, santé) ET montant ≥ 10K ET aucune règle explicite ne couvre le cas → **gel préventif par précaution**.

### Détection de contradictions

Le Médiateur compare les positions des agents :

1. **Recommandations divergentes** — Data dit "option A", Raisonnement dit "option B"
2. **Écart de confiance** — écart > seuil entre deux agents
3. **Risques non partagés** — un agent signale un risque que l'autre ignore

---

## 6. Scénario de conflit type (validé)

### Situation

**Cabinet :** Fiduciaire Léman & Associés, Genève
**Requête :** "Déterminer si la société peut déduire 85 000 CHF d'investissement en R&D"

### Flux réel dans v5

```
1. Orchestrateur
   → Intention int-9801 créée (v1, status=active)
   → Router: {data: True, reasoning: True, action: False, mediator: True}
   → Publié sur cleman.data.query ET cleman.reasoning.analyze

2. Agent Data
   → Résultat: "Déduction B1 autorisée si investissement > 80K (Circ. AFC n°42)"
   → Confiance: 0.92
   → Publié sur cleman.agent.result

3. Agent Raisonnement
   → Résultat: "CA 520K > seuil 500K, déduction B2 plafonnée 65K"
   → Confiance: 0.88
   → Risque: threshold_exceeded
   → Publié INTENTION_REVISE + résultat sur cleman.agent.result

4. Médiateur (intercepte les deux résultats)
   → _compare_positions: "Divergence: data recommande 'Déduction B1' mais reasoning 'Déduction B2'"
   → comptable-006 déclenché: montant 85000 >= 50000 → freeze
   → comptable-007 déclenché: contradiction_count > 0 → freeze
   → GEL IMMÉDIAT de l'intention int-9801
   → Publié sur cleman.mediator.conflict + cleman.mediator.freeze

5. Action (n'a jamais été activé — le Router ne route pas vers Action pour une analyse)

6. Superviseur V2
   → Health board: confiance=0.90, conflits=1, degraded=False
   → Observation journalisée dans le WORM

7. Interface d'arbitrage
   → Option A (Data): B1, 85K, confiance 92%
   → Option B (Raisonnement): B2, 65K, confiance 88%
   → Expert choisit B: "Application stricte du seuil, prudence"

8. Après arbitrage
   → Dégel → intention v3 active
   → Pour exécuter la provision: NOUVELLE intention "Exécuter provision 65K"
   → Router: {action: True} → Action exécute via saga
```

### Ce qui a changé par rapport au pipeline v4.1

| Étape | v4.1 (pipeline) | v5 (graphe) |
|-------|-----------------|-------------|
| Data publie | Passe au suivant | Médiateur intercepte en temps réel |
| Raisonnement contredit | Personne n'écoute | Raisonnement publie INTENTION_REVISE |
| Action | Exécute B1 (85K) ❌ | **Jamais activé** (gel + bon routage) |
| Superviseur | Voit le problème trop tard | Observe en continu, alimente le health board |
| Expert | Valide a posteriori | **Arbitre** entre options contradictoires |

---

## 7. Conformité réglementaire

### Cadre juridique couvert

| Réglementation | Articles | Verticales |
|----------------|----------|------------|
| RGPD | Art. 22 (décision auto), Art. 9 (santé), Art. 35 (DPIA) | Toutes |
| AI Act | Art. 6 (risque élevé), Art. 52 (transparence) | Santé, RH, Startup |
| Code pénal CH | Art. 321 (secret professionnel) | Avocat |
| Loi bancaire CH | Art. 47 (secret bancaire) | Banque |
| LPM | Données médicales, HDS | Santé |
| LBA | Art. 9 (seuil 10K) | Comptable, Banque |
| nLPD | Art. 5 (données sensibles), Art. 16-19 (transfert) | Avocat, Santé |
| FINMA | Circ. 2008/3 (infrastructure CH) | Banque |

### Deux modes de déploiement

**Standard (Cloud/OpenRouter)**
- LLM via OpenRouter (multi-modèles)
- NATS + Redis cloud
- Adapté : startup, comptable, RH

**Haute Protection (Edge/Ollama)**
- K3s + Ollama local (zero appel externe)
- Compliance Gateway bloque les requêtes sortantes
- **Obligatoire :** avocat (Art. 321 CP), banque (Art. 47 LB), santé (LPM)

---

## 8. Données et datasets réglementaires

### Seed data — 20 documents réglementaires

| Verticale | Documents | Références |
|-----------|-----------|------------|
| Comptable | 5 | RGPD Art. 22, Circ. AFC n°42, LBA, NEP, CO 957 |
| Avocat | 4 | CP 321, nLPD 5, nLPD 16-19, Déontologie 12bis |
| Santé | 3 | LPM 3, RGPD 9 + LPM 7, AI Act 6 |
| Banque | 3 | LB 47, FINMA 2008/3, LBA 3-7 |
| Startup | 2 | AI Act 52, RGPD 35 |
| RH | 3 | AI Act 6/Annexe III, RGPD 22, Loi 2008-496 |

Chaque document est lié à ses règles JsonLogic via le champ `applicable_rules`.

### Pourquoi pas les datasets B2B industry

Les datasets B2B (firmographics, leads, intent data) concernent le **sales et marketing**. Cortex Leman est une **infrastructure de confiance IA pour professions régulées**. Notre équivalent :

| Dataset B2B industry | Notre équivalent Cortex Leman |
|----------------------|-------------------------------|
| Firmographics | Profil client (vertical, cabinet) dans IntentionStore |
| Contacts | 7 comptes démo avec rôles et verticales |
| Signaux commerciaux | Signaux réglementaires (circulaires, seuils modifiés) |
| Interaction data | Journal WORM (106 entrées hash-chainées) |
| Données transactionnelles | Résultats d'agents + Sagas |

---

## 9. Skills des agents IA

### 3 agents LLM + 3 agents programmatiques

| Agent | Type | Skill | LLM ? |
|-------|------|-------|-------|
| Raisonnement | LLM | Juriste-Analyste Lémanique | Sprint 2 |
| Orchestrateur | LLM | Maître de Cérémonie Lémanique | Sprint 2 |
| Data | LLM partiel | Veilleur de Sources / Hermétique CH | Sprint 3 |
| Action | Programmatif | Exécuteur Fidèle | **JAMAIS** |
| Médiateur | Programmatif | Œil de Cortex | **JAMAIS** |
| Superviseur | Programmatif | Observateur Continu | **JAMAIS** |

### Structure d'un skill LLM (format industry adapté)

```markdown
# Skill: Agent Raisonnement — Juriste-Analyste Lémanique

## RÔLE
Analyste juridico-financier spécialiste du droit franco-suisse.

## TON
Rigoureux, prudent, nuancé.

## CONNAISSANCES
- FR: RGPD, AI Act, Code de commerce
- CH: nLPD, LPM, LB, Code des obligations
- 6 verticales avec référentiels dédiés

## OUTILS
- Contexte ERP (lecture seule)
- Résultats de l'Agent Data
- Moteur JsonLogic (lecture)

## WORKFLOW
1. Recevoir faits de Data
2. Identifier textes applicables
3. Comparer 2+ options avec base légale
4. Si incohérence: publier INTENTION_REVISE
5. Retourner résultat structuré

## GARDE-FOUS
- TOUJOURS citer la base légale
- TOUJOURS signaler une incertitude
- JAMAIS de contournement réglementaire
- Confiance < 0.3 → révision automatique
```

### Chargeur de skills

`core/agents/prompts/__init__.py` fournit :
- `load_skill(agent_name)` — charge le Markdown
- `build_system_prompt(agent, vertical, context)` — construit le prompt complet
- `list_available_skills()` — liste les 6 skills
- Retourne `None` pour les agents programmatiques

---

## 10. Bilan technique

### Chiffres

| Métrique | Valeur |
|----------|--------|
| Fichiers | 89 |
| Lignes de code Python | 6 484 |
| Lignes totales | 10 000+ |
| Tests | **89/89 ✅** |
| Endpoints API | 28 |
| Règles JsonLogic | 22 |
| Documents réglementaires | 20 |
| Skills agents | 6 (3 LLM + 3 programmatiques) |
| Sujets NATS | 13 |
| Verticales métier | 6 |

### Score de maturité : **6.5/10**

| Domaine | Score | Commentaire |
|---------|-------|-------------|
| Architecture | **9/10** | Graphe de confiance complet, pas encore prouvé en prod |
| Agents | **8/10** | Reconfigurés, LLM pas encore branché |
| Sécurité | **7/10** | 22 règles, gel, saga, mais journal disque brisé |
| Tests | **8/10** | 89/89, mais simulés sans vrai bus NATS |
| Intégrations | **6/10** | Implémentées, pas connectées à de vrais services |
| Frontend | **5/10** | MVP HTML, pas React, pas d'auth JWT |
| Données | **4/10** | 20 docs seed, pas de base vectorielle |
| Documentation | **8/10** | 4 docs de qualité |
| Ops | **6/10** | Docker + K3s, jamais testé en prod |
| Skills | **7/10** | Structurés, pas encore consommés |

### Prochaines étapes (Sprint 2)

1. **Brancher le LLM** dans le Raisonnement (appeler `generate_for_agent`)
2. **Auth JWT** (remplacer les 7 comptes en dur)
3. **Persistance Redis** pour IntentionStore
4. **React frontend** (remplacer le HTML monolithique)
5. **Base vectorielle ChromaDB** dans Knowledge Vault

---

## Fichiers du projet

```
cortex-leman-v5/
├── api/
│   └── main.py                          # 28 endpoints FastAPI
├── core/
│   ├── agents/
│   │   ├── prompts/                     # 6 skills agents
│   │   │   ├── reasoning.md            # Juriste-Analyste Lémanique
│   │   │   ├── orchestrator.md         # Maître de Cérémonie
│   │   │   ├── data.md                 # Veilleur de Sources
│   │   │   ├── action.md               # Programmatique
│   │   │   ├── mediator.md             # Programmatique
│   │   │   ├── supervisor.md           # Programmatique
│   │   │   └── __init__.py             # Chargeur de skills
│   │   ├── saga/
│   │   │   └── saga_manager.py         # Saga + compensation
│   │   ├── base_agent.py               # Subscribe + process + publish
│   │   ├── data_agent.py               # Agent Data
│   │   ├── reasoning_agent.py          # Agent Raisonnement
│   │   ├── action_agent.py             # Agent Action
│   │   └── supervisor_agent.py         # Superviseur V2
│   ├── arbitration/
│   │   └── arbitration_service.py      # Arbitrage + précédents
│   ├── bus/
│   │   ├── nats_client.py              # Bus NATS JetStream
│   │   └── subjects.py                 # 13 sujets
│   ├── compliance/
│   │   └── gateway.py                  # Compliance Gateway
│   ├── integrations/
│   │   ├── knowledge_vault/vault.py    # Knowledge Vault
│   │   ├── llm/provider.py             # OpenRouter + Ollama
│   │   └── n8n/client.py               # 12 workflows
│   ├── journal/
│   │   ├── append_only_journal.py      # Journal WORM
│   │   └── models.py                   # Pydantic models
│   ├── mediator/
│   │   ├── mediator.py                 # Médiateur transverse
│   │   ├── rules_engine.py             # Moteur JsonLogic
│   │   └── rules/                      # 6 verticales × 22 règles
│   ├── orchestrator/
│   │   ├── conversationnal.py          # Hub permanent
│   │   ├── intention.py                # Store versionné
│   │   └── router.py                   # Routage dynamique
│   └── security/
│       ├── circuit_breaker.py          # Protection échecs
│       └── distributed_lock.py         # Verrou Redis
├── data/
│   ├── journal/                        # Journal WORM fichiers
│   └── vault/
│       └── regulatory/                 # 20 docs réglementaires
├── docs/
│   ├── DEPLOYMENT.md                   # Guide déploiement
│   └── certification/CERTIFICATION-GUIDE.md
├── edge/
│   ├── k3s-install.sh                  # K3s appliance
│   ├── ollama-setup.sh                 # LLM local
│   └── manifests/deployment.yaml       # K8s manifests
├── mvp/
│   ├── frontend/index.html             # Dashboard MVP
│   └── docs/MVP-PRODUCT-GUIDE.md
├── tests/                              # 89 tests
├── architecture.html                   # Architecture visuelle
├── docker-compose.yml                  # NATS + Redis + Ollama
└── pyproject.toml                      # Config projet
```

---

*Graphe de confiance. Déterministe là où il faut. Intelligent là où on peut.*
