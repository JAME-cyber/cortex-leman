# Analyse AG2 (anciennement AutoGen) → Cortex Leman v5
# Framework multi-agent open-source — Analyse comparative et inspiration

## Source
https://ag2.ai/ (4 pages : Home, Research, Ecosystem, Blog)
Anciennement Microsoft AutoGen — fork communautaire indépendant
Fondateur : Qingyun Wu (Penn State → AG2 Inc.)

---

## 1. QU'EST AG2 ?

### Définition
> "AG2 is the open-source Python framework for building, orchestrating,
> and scaling multi-agent AI systems. Production-ready agent orchestration
> from the creators of AutoGen."

### Tagline : **"Build Systems, Not Prompts"**

AG2 est un **Agent Operating System (AgentOS)** — un framework Python qui permet
de créer, orchestrer et scaler des systèmes multi-agents IA. C'est l'évolution
production-ready d'AutoGen (Microsoft Research).

### Chiffres clés
- **50K+ GitHub Stars**
- **#1 twice on Hugging Face**
- **#1 AgentProphet Arena**
- **Best Paper ICLR 2024 LLM Agent Workshop**
- **NeurIPS 2025 competition winner**
- **16 papers peer-reviewed**
- Partenaires : AWS, Databricks, Google Cloud, IBM, Linux Foundation

---

## 2. ARCHITECTURE AG2 — Concepts Clés

### A. Multi-Agent Conversation Framework
- Agents qui conversent entre eux pour résoudre des tâches complexes
- **ConversationalOrchestrator** → notre concept presque identique
- **Group Chat** → plusieurs agents collaborent dans un "chat room"
- **Handoffs** → un agent passe le relais à un autre

### B. Protocoles ouverts supportés
| Protocole | Description | Pertinence Cortex Leman |
|---|---|---|
| **A2A** | Agent-to-Agent communication | 🔥 Notre bus NATS fait du A2A propriétaire |
| **MCP** | Model Context Protocol | 🔥 Connecter data sources (comme notre RAG) |
| **AG-UI** | Agent-to-User Interface | 🔥 Notre ChatPanel est un AG-UI basique |
| **A2UI** | AI-to-User Interface (génératif) | ⭐ Frontend dynamique adaptatif |
| **AgentSpec** | Spécification agent (Oracle) | 📋 Standard de définition d'agents |
| **AGNTCY** | Interopérabilité multi-framework | 📋 Standard de communication |

### C. Concepts architecturaux
1. **CaptainAgent** → Agent qui assemble dynamiquement une équipe d'agents
   (proche de notre Orchestrateur + Router)
2. **StateFlow** → Workflows pilotés par états (proche de notre intention store)
3. **Swarm** → Agents qui se passent le relais via handoffs
4. **Parallel Execution** → Exécution parallèle d'agents (70-75% plus rapide)
5. **AutoDefense** → Multi-agent defense contre jailbreaks (🔥 pour nos guardrails)
6. **Self-Evolving Agents** → Agents qui s'améliorent autonomement

### D. Recherche (16 papers)
| Paper | Conférence | Pertinence |
|---|---|---|
| AutoGen: Multi-agent conversation | COLM 2024 (Best Paper) | Notre base conceptuelle |
| Absolute Zero: Self-play reasoning | NeurIPS 2025 | Auto-amélioration sans données |
| Which Agent Causes Failures? | ICML 2025 | 🔥 Debug de notre graphe de confiance |
| AutoDefense: Multi-Agent Defense | arXiv 2024 | 🔥 Defense contre jailbreaks |
| StateFlow: State-Driven Workflows | COLM 2024 | Notre intention store |
| CaptainAgent: Team Assembly | arXiv 2024 | Notre router dynamique |
| BEST-Route: Adaptive LLM Routing | ICML 2025 | 🔥 Notre router modèle |
| AutoGenBench | AG2 Blog | Benchmarking agents |

### E. Produits
1. **AG2 Framework** (open-source, Python, pip install ag2)
2. **AG2 Studio** → Workflows visuels construits par conversation (no-code)
3. **AG2 Playground** → Démo live, agents orchestrent en temps réel
4. **AgentOS** → OS pour agents universels
5. **Universal Agent** → Concept d'agent unique qui peut tout faire

### F. Use Cases documentés
| Use Case | Client | Résultat |
|---|---|---|
| Due Diligence multi-agent | TinyFish | Due diligence investisseur en minutes |
| Immigration Law | Boundless | 90% réduction temps traitement documents |
| Business Management | Cegid Pulse OS | Ops business en langage naturel |
| Cosmologie | Cambridge CMBAGENT | 100x analyse plus rapide |
| RAG Chatbot | Fortune 500 | 50M+ records en <30s |
| Web Automation | AgentWeb | Deep research automatisé |
| Data Integration | Nexla | Pipelines data en langage naturel |
| Production agents | Walmart + Google | Production-grade deployment |

---

## 3. COMPARAISON AG2 vs CORTEX LEMAN

### A. Similitudes frappantes

| Concept | AG2 | Cortex Leman v5 |
|---|---|---|
| Multi-agent conversation | Group Chat | Orchestrateur conversationnel |
| Agent spécialisés | Captain + team | 6 agents spécialisés |
| Routing dynamique | CaptainAgent | Router + patterns |
| State management | StateFlow | Intention Store (freeze/unfreeze) |
| Guardrails | AutoDefense | GuardrailPipeline (PII, topic, safety) |
| RAG | Intégré | ChromaDB + Knowledge Vault |
| Journal/Tracing | OpenTelemetry | Journal WORM hash-chainé |
| Parallel exec | Supporté | Saga manager (compensation) |
| Ecosystem | Protocoles ouverts | NATS (propriétaire) |

### B. Différences fondamentales

| Dimension | AG2 | Cortex Leman v5 |
|---|---|---|
| **Nature** | Framework (boîte à outils) | Application (solution clé en main) |
| **Target** | Développeurs / Enterprise | Professions réglementées FR-CH |
| **Philosophie** | "Build systems, not prompts" | "Build trust, not risks" |
| **Conformité** | ❌ Aucune | ✅ RGPD, AI Act, CP 321, LB 47, LPM |
| **Secret pro** | ❌ Aucun | ✅ Architecture dédiée |
| **Médiateur** | ❌ Aucun | ✅ JsonLogic déterministe (0% LLM) |
| **Arbitrage humain** | ❌ Aucun | ✅ Obligatoire sur gel |
| **Journal WORM** | ❌ Tracing OpenTelemetry | ✅ Hash-chain SHA-256 + HMAC |
| **Certification** | ❌ Aucune | ✅ Guide certification intégré |
| **Mode local** | ❌ Cloud-first | ✅ K3s + Ollama offline |
| **Verticals** | ❌ Horizontal | ✅ 6 verticals réglementées |
| **Onboarding** | ❌ Documentation développeur | ✅ Wizard 5 min par vertical |
| **Règles métier** | ❌ Aucune | ✅ 22 règles JsonLogic |
| **UI** | ❌ Playground démo | ✅ Landing + Login + Dashboard + Chat |
| **Tests** | ❌ Framework non testé | ✅ 159 tests automatisés |
| **Pricing** | ❌ Open-source gratuit | ✅ SaaS 49-299€/mois |

### C. Positionnement relatif

```
┌────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                        │
│                                                                │
│   AG2 (framework)    LangChain    CrewAI    AutoGen (legacy)  │
│   → Outils pour construire des systèmes multi-agents          │
│   → Développeurs écrivent du code                              │
│   → Aucune conformité, aucun audit                             │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                           │
│                                                                │
│   ★ Cortex Leman v5 ★                                         │
│   → Solution clé en main pour professions réglementées        │
│   → L'utilisateur final n'écrit PAS de code                   │
│   → Conformité native, audit trail, arbitrage humain          │
│   → PEUT utiliser AG2 comme framework sous-jacent              │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                    MARKET LAYER                                │
│                                                                │
│   Genspark / Accio Work / ChatGPT                              │
│   → Solutions grand public / PME horizontales                 │
│   → Productivité générale, zéro réglementaire                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Conclusion : AG2 est un framework INFRASTRUCTURE.
Cortex Leman est une APPLICATION qui pourrait utiliser AG2.**

---

## 4. CE QU'ON INSPIRE D'AG2

### A. Court terme — Intégrer immédiatement

#### 1. AutoDefense → Renforcer nos guardrails
Le paper "AutoDefense: Multi-Agent LLM Defense against Jailbreak Attacks"
montre comment utiliser plusieurs agents pour détecter les attaques.

**Action :** Ajouter un 4ème guardrail "Multi-Agent Defense" dans notre pipeline.
Au lieu d'un seul check PII, avoir 2-3 agents légers qui valident en parallèle.

#### 2. StateFlow → Améliorer notre Intention Store
AG2 utilise des "state-driven workflows" — chaque intention a un état
machine (created → processing → frozen → arbitrated → resolved).

**Action :** Notre Intention Store a déjà freeze/unfreeze. Ajouter un
state machine complet avec transitions et guards.

#### 3. CaptainAgent → Améliorer notre Router
Le concept de "CaptainAgent" qui assemble dynamiquement une équipe.

**Action :** Notre Router sélectionne déjà des agents par pattern.
Ajouter le concept de "team assembly" — pour une intention complexe,
assembler une sous-équipe d'agents dynamiquement.

#### 4. OpenTelemetry Tracing → Compléter notre monitoring
AG2 utilise OpenTelemetry pour tracer les flux multi-agents.

**Action :** Ajouter OpenTelemetry tracing à nos agents, en plus de
nos métriques Prometheus existantes. Permet de voir le graphe
d'exécution complet.

### B. Moyen terme — Architecture

#### 5. A2A Protocol → Ouvrir notre bus NATS
AG2 supporte le protocole A2A (Agent-to-Agent).

**Action :** Implémenter un adaptateur A2A sur notre bus NATS.
Permet à des agents AG2 externes de communiquer avec nos agents Cortex Leman.
Positionne Cortex Leman comme "trusted agent in an open ecosystem".

#### 6. MCP Integration → Connecter des data sources
Model Context Protocol permet de connecter des sources de données.

**Action :** Ajouter un serveur MCP à notre RAG ChromaDB. Permet
à des agents MCP externes de requêter notre Knowledge Vault.

#### 7. AG-UI Protocol → Enrichir notre ChatPanel
AG-UI est un protocole standard pour les interfaces agent-utilisateur.

**Action :** Rendre notre ChatPanel compatible AG-UI. Permet
d'utiliser des composants frontend AG-UI (CopilotKit, etc.).

### C. Long terme — Vision

#### 8. AG2 comme framework sous-jacent ?
AG2 est open-source, Python, production-ready.

**Option A : Continuer avec notre architecture custom (recommandé)**
- ✅ Contrôle total sur la conformité
- ✅ Pas de dépendance externe critique
- ✅ Code adapté aux exigences réglementaires
- ❌ Maintenance plus lourde

**Option B : Migrer les agents vers AG2**
- ✅ Framework éprouvé (50K+ stars)
- ✅ Protocoles ouverts intégrés
- ✅ Écosystème riche
- ❌ Perte de contrôle sur le Médiateur (doit rester 0% LLM)
- ❌ Couche d'abstraction qui peut masquer des problèmes de conformité
- ❌ Dépendance à un framework externe

**Recommandation : Hybride (Option A + intégrations ciblées)**
- Garder notre architecture custom
- Ajouter des adaptateurs A2A/MCP/AG-UI pour interopérabilité
- S'inspirer des papers AutoDefense, StateFlow, CaptainAgent
- Ne PAS dépendre d'AG2 comme framework

---

## 5. USE CASES AG2 → APPLICATIONS CORTEX LEMAN

### A. Due Diligence multi-agent (AG2 × TinyFish)
**AG2 :** "Build a team of AI agents that runs investor-grade due diligence"
**Cortex Leman :** Due diligence réglementaire avec conformité

```
Due Diligence AG2:
  Agent Research → scrape web
  Agent Analyse → évalue les risques
  Agent Report → génère le rapport

Due Diligence Cortex Leman:
  Data Agent → RAG ChromaDB (sources réglementaires)
  Reasoning Agent → analyse risques + conformité
  Médiateur → gel si montant > seuil
  Superviseur → score de confiance
  Arbitrage humain → validation finale
  Journal WORM → preuve d'audit
```

### B. Immigration Law (AG2 × Boundless → 90% faster)
**AG2 :** "90% reduction in document processing time"
**Cortex Leman :** Traitement documents juridiques avec secret avocat

```
Boundless AG2: Traitement documents immigration
Cortex Leman:  Traitement documents juridiques FR-CH
               + Art. 321 CP (secret avocat)
               + Mode Haute Protection (Ollama local)
               + Journal WORM (preuve pour le barreau)
```

### C. Business Management (AG2 × Cegid Pulse OS)
**AG2 :** "Natural language business operations"
**Cortex Leman :** Opérations comptables conformes

```
Cegid AG2:     Ops business en langage naturel
Cortex Leman:  Ops comptables en langage naturel
               + Règles comptables (6 JsonLogic rules)
               + Gel préventif si montant ≥ 50K
               + Journal WORM (preuve pour l'expert-comptable)
               + RAG avec textes fiscaux FR-CH
```

---

## 6. PROTOCOLES OUVERTS — PLAN D'ACTION

### Pourquoi c'est stratégique pour Cortex Leman

Si nous supportons les protocoles ouverts (A2A, MCP, AG-UI), nous devenons :
1. **Compatible** avec l'écosystème AG2 (50K+ développeurs)
2. **Interoperable** avec d'autres frameworks
3. **Extensible** sans réinventer la roue
4. **Crédible** technologiquement (standards ouverts)

### Plan d'implémentation

```
Sprint 4: MCP Server (expose notre RAG via MCP)
  → agents MCP externes peuvent requêter notre Knowledge Vault
  → 1-2 semaines d'effort

Sprint 5: A2A Adapter (bridge NATS ↔ A2A)
  → agents AG2 externes peuvent communiquer avec nos agents
  → 2-3 semaines d'effort

Sprint 6: AG-UI Protocol (frontend compatible)
  → utiliser des composants AG-UI standards dans notre ChatPanel
  → 1-2 semaines d'effort

Total : 4-7 semaines pour rejoindre l'écosystème ouvert
```

---

## 7. CE QU'AG2 N'A PAS (NOTRE MOAT)

| Feature | AG2 | Cortex Leman |
|---|---|---|
| Médiateur déterministe (0% LLM) | ❌ | ✅ |
| Journal WORM hash-chainé | ❌ | ✅ |
| Arbitrage humain obligatoire | ❌ | ✅ |
| Règles métier JsonLogic (22 règles) | ❌ | ✅ |
| 6 verticals réglementées | ❌ | ✅ |
| Conformité RGPD/AI Act native | ❌ | ✅ |
| Secret professionnel (CP 321) | ❌ | ✅ |
| Mode offline (K3s + Ollama) | ❌ | ✅ |
| UI complète (Landing + Dashboard + Chat) | ❌ Playground only | ✅ |
| Onboarding wizard par vertical | ❌ | ✅ |
| Certification guide | ❌ | ✅ |
| Pricing B2B SaaS | ❌ OSS | ✅ |

---

## 8. BLOG POSTS À ÉTUDIER

| Post | Date | Insight pour Cortex Leman |
|---|---|---|
| A2UI: Giving Agents Expression | Mar 2026 | Frontend génératif pour nos agents |
| Studio: Visual Workflows by Conversation | Mar 2026 | Builder de workflows no-code |
| Due Diligence with TinyFish | Mar 2026 | Use case Due Diligence applicable |
| Playground: Go Play with Multi-Agent AI | Mar 2026 | Démo live sans compte |
| Agents Need Interfaces (AG-UI) | Feb 2026 | Protocole interface standard |
| Tracing in an Agentic World | Feb 2026 | OpenTelemetry pour agents |
| Beyond AutoGen: Why AG2 | Jan 2026 | Évolution research → production |
| Boundless Immigration Law | Sep 2025 | 90% faster = notre promesse |
| Cegid Pulse OS | Aug 2025 | ERP + IA = notre vertical comptable |
| Parallel Agent Execution | Apr 2025 | 70-75% plus rapide |

---

## 9. CONCLUSION STRATÉGIQUE

### AG2 en une phrase
> "AG2 est le framework open-source de référence pour construire des systèmes
> multi-agents. Mais c'est un framework, pas une application. Et il ignore
> totalement le réglementaire."

### Cortex Leman en une phrase
> "Cortex Leman est une application clé-en-main qui résout un problème
> spécifique (conformité IA réglementée FR-CH) avec une architecture
> inspirée des meilleurs frameworks multi-agents."

### Relation idéale
```
AG2 = Framework (infra) → potentiellement utilisé SOUS Cortex Leman
Cortex Leman = Application (solution) → utilise des concepts AG2

"AG2 construit les routes. Cortex Leman construit les voitures
avec ceinture de sécurité, airbag et assurance."
```

### 3 actions immédiates
1. **Installer `ag2`** et tester le framework pour évaluer l'intégration
2. **Ajouter MCP Server** sur notre RAG (exposition standardisée)
3. **Implémenter AutoDefense** dans nos guardrails (multi-agent defense)

### 3 inspirations architecturales
1. **StateFlow** → State machine pour notre Intention Store
2. **CaptainAgent** → Team assembly dynamique dans notre Router
3. **OpenTelemetry** → Distributed tracing pour notre monitoring

### Risque
- AG2 pourrait ajouter des features "compliance" → nous devons avoir
  une avance de 12+ mois sur le vertical réglementaire FR-CH.
- **Mitigation** : Notre moat n'est pas technique (AG2 peut copier),
  c'est **réglementaire** (conformité, certification, secret pro, audit).
