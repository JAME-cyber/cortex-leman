# Plan d'Implémentation — Observabilité Agent (Post-Video Analyse)

**Source:** Analyse de "Mind the Gap (In Your Agent Observability)" — Amy Boyd & Nitya Narasimhan, Microsoft Foundry  
**Date:** 2026-05-15  
**Impact:** 4 modules à implémenter, priorisés par risque métier

---

## Ce qui existe déjà dans Cortex Leman v5

| Composant | Fichier | Status |
|-----------|---------|--------|
| Journal WORM (append-only, hash-chainé) | `core/journal/append_only_journal.py` | ✅ Opérationnel |
| Médiateur déterministe (JsonLogic) | `core/mediator/mediator.py` | ✅ Opérationnel |
| AutoDefense multi-validateur | `core/security/guardrails/autodefense.py` | ✅ 3 validateurs + vote |
| Security Auditor (5 axes OWASP) | `core/security/auditor.py` | ✅ Opérationnel |
| Superviseur (health board temps réel) | `core/agents/supervisor_agent.py` | ✅ IntentionHealth |
| Circuit Breaker | `core/security/circuit_breaker.py` | ✅ Opérationnel |
| Saga Manager (compensation) | `core/agents/saga/saga_manager.py` | ✅ Opérationnel |

## Ce qui MANQUE (gaps critiques identifiés)

### Gap 1: Tracing distribué OpenTelemetry sur le bus NATS 🔴
**Pourquoi:** Actuellement, les événements transitent sur NATS mais il n'y a pas de corrélation entre les spans d'une même intention. Impossible de reconstituer le graphe d'exécution d'une intention de bout en bout.

### Gap 2: Red Teaming automatisé (Agent hostile) 🔴
**Pourquoi:** AutoDefense détecte les injections par patterns, mais personne ne teste proactivement si les agents sont vulnérables. En métier régulé (avocat, banque, santé), c'est un gap critique.

### Gap 3: Méta-évaluateur — Les règles JsonLogic sont-elles encore pertinentes? 🟡
**Pourquoi:** Le Médiateur applique 20 règles × 6 verticales. Mais personne ne vérifie si ces règles détectent encore les vrais problèmes. Les réglementations évoluent (AI Act entre en application progressive).

### Gap 4: Observe Skill Cortex — Diagnostic automatisé depuis le journal WORM 🟡
**Pourquoi:** Le journal WORM contient tout, mais personne ne l'analyse de manière systématique. Un agent pourrait détecter les dérives, proposer des MAJ de règles, et préparer des rapports pour l'arbitrage humain.

---

## Priorisation

| # | Module | Priorité | Effort | Risque si non fait |
|---|--------|----------|--------|-------------------|
| 1 | OpenTelemetry Tracing | P0 — CRITIQUE | 3 jours | Impossible de diagnostiquer les incidents multi-agents |
| 2 | Red Teaming | P0 — CRITIQUE | 5 jours | Vulnérabilités non détectées en avocat/banque/santé |
| 3 | Méta-évaluateur | P1 — IMPORTANT | 3 jours | Règles obsolètes = faux négatifs en production |
| 4 | Observe Skill | P2 — VALEUR | 4 jours | Dérives silencieuses non détectées |

---

## Détails d'implémentation

### Module 1: `core/observability/tracing.py` — OpenTelemetry sur NATS

```
Architecture:
  Chaque événement NATS → injecte trace_id + span_id dans le payload
  L'Orchestrateur crée le trace root quand une intention naît
  Chaque agent crée un span enfant
  Le Médiateur crée un span de vérification
  Export: OTLP → Jaeger/Tempo (ou console en dev)

Nouveaux sujets NATS:
  cleman.trace.span     — Span individuel
  cleman.trace.batch    — Batch de spans pour export

Intégration:
  BaseAgent.process() → auto-wrap dans un span
  Mediator._on_agent_result() → span de vérification
  Journal WORM → trace_id dans chaque entrée
```

### Module 2: `core/security/red_team.py` — Red Teaming automatisé

```
Architecture:
  RedTeamAgent (un agent hostile contrôlé)
  Attaque les 6 verticales avec des stratégies prédéfinies:
    - Prompt injection directe
    - Prompt injection indirecte (via données)
    - Manipulation de contexte (role confusion)
    - Extraction de données sensibles
    - Contournement de guardrails
    - Épuisement (repeated edge cases)
  
  Chaque attaque → passe par le pipeline normal:
    Orchestrateur → Data/Raisonnement → Médiateur → Action
  
  Si l'attaque passe le Médiateur → VULNÉRABILITÉ CRITIQUE
  Si AutoDefense bloque → testé et validé
  
  Rapport: par verticale, taux de blocage, vecteurs réussis
  
  Sécurité:
    - Ne tourne QU'en mode test (flag --red-team)
    - Journalisé dans le WORM comme événement RED_TEAM
    - Jamais en production sans autorisation explicite
```

### Module 3: `core/mediator/meta_evaluator.py` — Méta-évaluation des règles

```
Architecture:
  Scanner périodique (cron ou on-demand):
  
  1. Lit les 7 fichiers de règles (core/mediator/rules/*.json)
  2. Analyse les entrées du journal WORM des 30 derniers jours
  3. Pour chaque règle:
     - Combien de fois a-t-elle été déclenchée? (trop = faux positifs?)
     - Y a-t-il des conflits/urgences qui n'ont matché AUCUNE règle? (faux négatifs)
     - La réglementation a-t-elle changé? (check via ArXiv pipeline)
  4. Génère un rapport:
     - Règles à supprimer (plus pertinentes)
     - Règles à ajouter (nouveaux patterns de conflit)
     - Règles à ajuster (seuils trop hauts/bas)
  5. Propose via cleman.extension.propose → Médiateur évalue → Humain arbitre
  
  JAMAIS de modification automatique des règles.
  Le méta-évaluateur propose, l'humain décide.
```

### Module 4: `core/observability/observe_skill.py` — Observe Skill Cortex

```
Architecture:
  Agent d'analyse qui lit le journal WORM et diagnostique:
  
  1. Détection de dérive:
     - Score de confiance moyen par verticale (tendance)
     - Taux de gel/conflit par verticale
     - Temps de résolution d'arbitrage
  2. Analyse des échecs:
     - Patterns récurrents dans les conflits
     - Agents qui dégradent le plus souvent
     - Verticales les plus à risque
  3. Recommandations:
     - "La verticale avocat a 40% de gels → peut-être ajuster le seuil de confiance"
     - "L'agent Data renvoie confiance <0.5 dans 30% des cas → vérifier les sources"
     - "Le pattern 'divulgation données patient' apparaît 12 fois → nouvelle règle?"
  4. Dashboard: exposure via API endpoint /api/v1/observe/dashboard
  
  Mode: lecture seule sur le journal WORM
  Jamais de modification du système en automatique.
```
