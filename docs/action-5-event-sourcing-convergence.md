# CORTEX LEMAN v5 — Architecture Event-Sourcing & Médiation

## Analyse comparative avec Jonas Templestein (AI Engineer Summit 2026)

**Source**: "Make your own event-sourced agent harness using stream processors"
**Locuteur**: Jonas Templestein (Iterate) + Misha
**Date**: Mai 2026

---

## 1. Convergence architecturale

L'approche de Jonas valide plusieurs choix fondamentaux de Cortex Leman :

### Split Reducer / Side-Effects

```
Jonas:                          Cortex Leman:
┌──────────────────┐           ┌──────────────────────────┐
│ REDUCER          │           │ RULES ENGINE (JsonLogic) │
│ fn(state, event) │  ←→→→→   │ evaluate(vertical, ctx)  │
│ → newState       │           │ → [RuleResult]           │
│ SYNCHRONE, PUR   │           │ DÉTERMINISTE, 100% PUR   │
├──────────────────┤           ├──────────────────────────┤
│ AFTER_APPEND     │           │ MÉDIATEUR ACTIONS        │
│ Side effects     │  ←→→→→   │ freeze, block, arbitrate │
│ LLM calls, HTTP  │           │ journal.append()         │
│ ASYNCHRONE       │           │ ASYNCHRONE + TRAÇABLE    │
└──────────────────┘           └──────────────────────────┘
```

**Point critique de Jonas** (32:00) :
> "Si ton programme redémarre après 100 événements, tu veux rattraper le state
> **sans rejouer les requêtes LLM**. C'est pourquoi on sépare le reducer de l'after-append."

**Notre implémentation** :
- Le `rules_engine.py` est un reducer pur (JsonLogic, synchrone)
- Les actions du Médiateur (freeze, arbitrate) sont les side effects
- Le journal WORM permet de re-dériver le state depuis les événements sans re-caller le LLM
- Les `JournalEntry` sont hash-chainées (SHA-256), immuables

### Event Sourcing = Debuggable

**Jonas** (1:55) :
> "Tout ce qui pourrait arriver est dans le log. Ce sera vraiment facile à debug."

**Cortex Leman** :
- Chaque décision du Médiateur est un événement (mediator.check, mediator.freeze, etc.)
- Les traces sont exposées via MCP (`get_trace`) et le dataset HuggingFace
- Le Trust Center montre les benchmarks de détection en temps réel

### Idempotence

**Jonas** (11:55) :
> "Si tu postes le même événement avec la même idempotence key deux fois, tu ne
> le reçois pas deux fois."

**Cortex Leman** (nouveau) :
- Champ `idempotency_key` ajouté aux `JournalEntry`
- Format: `{agent_source}:{intention_id}:{event_type}:{hash(payload)}`
- L'append_only_journal vérifie la clé avant d'appendre

---

## 2. Divergences critiques

### Auto-modification vs Médiation

| Aspect | Jonas (Iterate) | Cortex Leman |
|--------|-----------------|--------------|
| **Pattern** | Dynamic Worker Configured | Auto-extension médiationnée |
| **Code en payload** | ✅ Oui (JS string dans événement) | ❌ Non — gelé par le Médiateur |
| **Approbation** | Aucune (auto-appliqué) | Arbitrage humain obligatoire |
| **Traçabilité** | Événement loggé | Événement loggé + hash + signature |
| **Rollback** | Via event store | Via Saga pattern + compensation |

**Règle agent-ia-009** :
```
Si event_type == "extension.proposed"
  → action: freeze
  → severity: HIGH
  → références: AI Act Art. 14, RGPD Art. 22
  → workflow: EXTENSION_PROPOSED → FREEZE → ARBITRATION → APPROVED/REJECTED
```

### Edge/Public vs Haute Protection

| Aspect | Jonas | Cortex Leman |
|--------|-------|--------------|
| **Déploiement** | Edge, HTTP, publiquement routable | Mode Standard (cloud) OU Mode Haute Protection (local) |
| **Authentification** | Aucune | Obligatoire (RBAC par verticale) |
| **Souveraineté** | Non mentionnée | FR-CH, LPD, secret professionnel |

### Sub-agents

| Aspect | Jonas | Cortex Leman |
|--------|-------|--------------|
| **Pattern** | Filesystem paths (`/agents/boris/`) | NATS hierarchy (`cleman.agent.data.scan_rgpd`) |
| **Communication** | Append to child path, subscribe parent | Publish/subscribe NATS avec wildcard |
| **Isolation** | Même event store | Namespace par client_id + vertical |

---

## 3. Améliorations apportées (mai 2026)

### Action 1: Clé d'idempotence
- **Fichier**: `core/journal/models.py`
- **Champ**: `idempotency_key: Optional[str]`
- **Usage**: Garantit qu'un événement n'est jamais appendé deux fois

### Action 2: LLM Streaming comme événements
- **Nouveaux types**: `AGENT_LLM_REQUEST`, `AGENT_LLM_CHUNK`, `AGENT_LLM_RESPONSE`, `AGENT_LLM_ERROR`
- **Usage**: Logger chaque chunk LLM → permet de rejouer une conversation sans rappeler le LLM
- **Inspiration**: Jonas "everything is an event, errors too"

### Action 3: Sub-agents via hiérarchie NATS
- **Fichier**: `core/bus/subjects.py`
- **Nouveaux sujets**: `cleman.subagent.spawn/result/failed`
- **Méthodes**: `for_subagent(parent, child)`, `subagent_wildcard(parent)`
- **Pattern**: Parent spawn enfant → enfant publie → parent notifié via wildcard

### Action 4: Auto-extension médiationnée
- **Fichier**: `core/mediator/rules/agent-ia.json` (règle agent-ia-009)
- **Nouveaux types**: `EXTENSION_PROPOSED/REVIEWED/APPROVED/REJECTED/APPLIED`
- **Workflow**: Agent propose → Médiateur gèle → Humain arbitre → Extension appliquée ou rejetée
- **Sécurité**: Aucun code non-audité ne s'exécute jamais

### Action 5: Cette documentation
- **Fichier**: `docs/action-5-event-sourcing-convergence.md`

---

## 4. Leçon principale

> **"Event sourcing sans médiation = debuggable mais dangereux.
> Event sourcing avec médiation déterministe = debuggable ET conforme."**

La contribution de Jonas est architecturale (le split reducer/effects est élégant).
Notre contribution Cortex Leman est **gouvernancielle** : le même pattern, mais avec
une couche de médiation déterministe qui garantit la conformité RGPD/AI Act/secret professionnel.

**Excellence by Design** = Event Sourcing + Médiation Déterministe + Arbitrage Humain.

---

*Analyse générée par Cortex Leman v5 — Mai 2026*
*Source: Jonas Templestein, AI Engineer Summit 2026*
