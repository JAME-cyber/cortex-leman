# Cortex Leman v5 — Livre Blanc

# Mode Dégradé Conforme : Quand la Confiance se Construit en Parallèle

**Comment transformer un gel de sécurité en opportunité d'enrichissement pour l'arbitrage humain**

---

**Auteurs :** Cortex Leman Engineering Team  
**Version :** 1.0 — Sprint 2  
**Date :** 30 avril 2026  
**Classification :** Public  

---

## Résumé exécutif

Dans les systèmes de confiance IA pour professions régulées, le gel préventif est un mécanisme essentiel. Quand un conflit est détecté entre agents, l'exécution doit être suspendue. Mais suspendre **toute** l'analyse pendant le gel crée un paradoxe : l'humain qui doit arbitrer reçoit un dossier **incomplet**, car les agents Data et Raisonnement ont été arrêtés en même temps que l'Agent Action.

Cortex Leman v5 résout ce paradoxe avec le **mode dégradé conforme** : un état `DEGRADED_FROZEN` où seul l'Agent Action est bloqué, tandis que les agents Data et Raisonnement continuent de travailler pour enrichir le dossier d'arbitrage.

Ce livre blanc détaille l'architecture, les compromis, la robustesse et les questions ouvertes de cette approche. Il s'adresse aux architectes système, auditeurs de certification et décideurs techniques dans les professions régulées.

---

## Table des matières

1. [Le problème du gel total](#1-le-problème-du-gel-total)
2. [Architecture du mode dégradé](#2-architecture-du-mode-dégradé)
3. [State Machine enrichie](#3-state-machine-enrichie)
4. [Flux de données en mode dégradé](#4-flux-de-données-en-mode-dégradé)
5. [Escalade et arbitrage](#5-escalade-et-arbitrage)
6. [Seuils paramétrables par verticale](#6-seuils-paramétrables-par-verticale)
7. [Horodatage qualifié RFC 3161](#7-horodatage-qualifié-rfc-3161)
8. [Questions de robustesse](#8-questions-de-robustesse)
9. [Résultats et métriques](#9-résultats-et-métriques)
10. [Feuille de route](#10-feuille-de-route)

---

## 1. Le problème du gel total

### 1.1 Le gel classique dans les systèmes de confiance

Dans un système de confiance IA, le gel préventif fonctionne ainsi :

```
Conflit détecté → Gel immédiat → Tous les agents s'arrêtent → Arbitrage humain → Dégel
```

Ce modèle est simple et sûr. Il garantit qu'aucune action irréversible n'est exécutée pendant un conflit. C'est le modèle qu'utilisent la plupart des systèmes de conformité.

### 1.2 Le paradoxe de l'information incomplète

Le problème survient au moment de l'arbitrage. L'expert humain doit trancher entre deux positions contradictoires. Mais s'il a fallu 2 heures pour l'escalade et l'arbitrage, le dossier qu'il reçoit contient :

- La position de l'Agent Data au moment du gel (possiblement partielle)
- La position de l'Agent Raisonnement au moment du gel (possiblement basée sur des données incomplètes)
- **Aucune information nouvelle** collectée pendant les 2 heures de gel

C'est le paradoxe : le gel protège le système, mais affaiblit la qualité de la décision humaine.

### 1.3 Illustration concrète

**Scénario :** Un cabinet comptable franco-suisse traite une déclaration fiscale. L'Agent Data rapporte un montant de 12 000 CHF. L'Agent Raisonnement recommande la prudence (déduction fiscale potentiellement non éligible). Le Médiateur détecte le conflit et gèle.

**Avec gel total :** L'expert-comptable reçoit un dossier basé sur le montant initial de 12 000 CHF. Il ne sait pas que l'Agent Data avait commencé à trouver des justificatifs supplémentaires qui pourraient valider la déduction.

**Avec gel dégradé :** L'Agent Data continue de chercher. Pendant les 2 heures d'attente, il trouve 3 justificatifs supplémentaires qui confirment l'éligibilité de la déduction. L'Agent Raisonnement réévalue sa position avec les nouvelles données. L'expert-comptable reçoit un dossier **enrichi** et peut trancher en toute connaissance de cause.

---

## 2. Architecture du mode dégradé

### 2.1 Principe

Le mode dégradé conforme introduit un nouvel état dans la state machine : `DEGRADED_FROZEN`. Dans cet état :

| Agent | Statut | Raison |
|-------|--------|--------|
| Action | **Bloqué** | Aucune exécution transactionnelle |
| Data | **Actif** | Continue la recherche pour enrichir le dossier |
| Raisonnement | **Actif** | Continue l'analyse avec les nouvelles données |
| Superviseur | **Actif** | Observe et journalise |

### 2.2 Implémentation dans le Médiateur

Le Médiateur est le composant central qui décide du mode de gel. Quand il crée un conflit, il choisit entre :

- **Gel complet** (`FROZEN`) : pour les cas critiques (règle `block`, violation Art. 321 CP, etc.)
- **Gel dégradé** (`DEGRADED_FROZEN`) : pour les conflits où Data et Raisonnement peuvent encore apporter de la valeur

```python
# Médiateur — choix du mode de gel
async def _create_conflict(self, ..., degraded: bool = False):
    # Gel dégradé par défaut pour les conflits non critiques
    from core.orchestrator.intention import intention_store
    intention_store.freeze(intention_id, reason=reason, degraded=degraded)
```

### 2.3 Règles de routage dans le Médiateur

Quand le Médiateur reçoit un résultat d'agent pour une intention en état dégradé :

```python
if intention_store.is_degraded_frozen(intention_id):
    if agent_source == "action":
        # Action bloqué — mode dégradé
        return
    else:
        # Data/Raisonnement continuent → enrichissement
        self._agent_positions[intention_id][agent_source] = result
        await bus.publish(subjects.MEDIATOR_DEGRADED_FREEZE, {
            "event": "enrichment",
            "positions": self._agent_positions[intention_id],
        })
```

### 2.4 Agent Action — protection double

L'Agent Action vérifie `is_action_blocked()` qui retourne `True` pour **les deux** modes de gel :

```python
def is_action_blocked(self, intention_id: str) -> bool:
    state = self._states.get(intention_id)
    return state in (IntentionState.FROZEN, IntentionState.DEGRADED_FROZEN)
```

Cette méthode garantit que l'Action ne peut **jamais** s'exécuter pendant un gel, quel qu'en soit le mode.

---

## 3. State Machine enrichie

### 3.1 Avant Sprint 2

```
CREATED → ROUTED → PROCESSING → FROZEN → ARBITRATING → UNFROZEN → PROCESSING
```

### 3.2 Après Sprint 2

```
CREATED → ROUTED → PROCESSING ─┬→ FROZEN → ARBITRATING → UNFROZEN → PROCESSING
                                ├→ DEGRADED_FROZEN → ARBITRATING → UNFROZEN
                                └→ DEGRADED_FROZEN → FROZEN (escalade critique)
```

### 3.3 Nouvelles transitions

| From | To | Trigger | Raison |
|------|----|---------|--------|
| PROCESSING | DEGRADED_FROZEN | Médiateur | Conflit non critique |
| ROUTED | DEGRADED_FROZEN | Médiateur | Conflit précoce |
| DEGRADED_FROZEN | ARBITRATING | Humain | Début arbitrage |
| DEGRADED_FROZEN | FROZEN | Médiateur | Escalade (risque découvert) |
| DEGRADED_FROZEN | CANCELLED | Utilisateur | Annulation |

### 3.4 Nouvelles méthodes de vérification

```python
store.is_fully_frozen(intention_id)    # True si FROZEN uniquement
store.is_degraded_frozen(intention_id) # True si DEGRADED_FROZEN uniquement
store.is_action_blocked(intention_id)  # True si FROZEN OU DEGRADED_FROZEN
```

---

## 4. Flux de données en mode dégradé

### 4.1 Flux nominal (sans conflit)

```
Intention → Orchestrateur → Data + Raisonnement → Médiateur vérifie → Action exécute
```

### 4.2 Flux avec gel dégradé

```
Intention → Orchestrateur → Data + Raisonnement → Médiateur détecte conflit
                                                      │
                                          ┌───────────┴───────────┐
                                          │                       │
                                    Action: BLOQUÉ          Data: CONTINUE
                                    (is_action_blocked)     (enrichit positions)
                                                                  │
                                                          Raisonnement: CONTINUE
                                                          (analyse avec nouvelles données)
                                                                  │
                                                          Chaque résultat → bus.publish(
                                                              MEDIATOR_DEGRADED_FREEZE,
                                                              event: "enrichment"
                                                          )
                                                                  │
                                                          Dashboard arbitrage mis à jour
                                                                  │
                                                          Arbitre humain → dossier ENRICHI
                                                                  │
                                                          submit_decision() → dégel
```

### 4.3 Publication des enrichissements

Chaque résultat produit par Data ou Raisonnement pendant le gel dégradé est publié sur `cleman.mediator.degraded_freeze` avec :

```json
{
  "intention_id": "uuid",
  "agent_source": "data",
  "event": "enrichment",
  "message": "Agent data a enrichi le dossier pendant le gel dégradé",
  "positions": {
    "data": {"recommendation": "execute", "confidence": 0.87, "sources": [...]},
    "reasoning": {"recommendation": "caution", "confidence": 0.65}
  }
}
```

---

## 5. Escalade et arbitrage

### 5.1 File d'escalade configurable

L'arbitrage inclut désormais une file d'escalade automatique :

```
expert (2h) → expert_suppleant (4h) → associe (8h) → admin (blocage)
```

Chaque niveau est :
- **Horodaté** dans le journal WORM
- **Journalisé** avec l'historique complet dans `escalation_history`
- **Annulé** automatiquement si une décision est soumise avant le timeout

### 5.2 Interaction gel dégradé / escalade

Le mode dégradé prend tout son sens pendant l'escalade :

| Phase | Timer escalade | Agents actifs | Dossier arbitrage |
|-------|---------------|---------------|-------------------|
| Expert | 0-2h | Data + Raisonnement | Enrichissement continu |
| Suppléant | 2-6h | Data + Raisonnement | Enrichissement continu |
| Associé | 6-14h | Data + Raisonnement | Enrichissement continu |

**Résultat :** quel que soit le niveau d'escalade qui répond, l'arbitre bénéficie d'un dossier plus complet qu'avec un gel total.

### 5.3 Persistance de l'historique d'escalade

Chaque étape d'escalade est :
1. Journalisée dans le WORM (`JournalEventType.ARBITRATION_REQUESTED` avec payload `event: "escalation"`)
2. Stockée dans le dashboard (`escalation_history` array)
3. Consultable via l'API (`GET /api/v1/arbitrations/{id}`)

### 5.4 Limitation identifiée

⚠️ Les timers d'escalade sont des `asyncio.Task` en mémoire. Si le service redémarre, les timers en cours sont perdus.

**Mitigation :** chaque redémarrage recharge les arbitrages `pending` depuis la persistance. Un mécanisme de re-scheduling des timers au démarrage est prévu au Sprint 3 (via NATS KV ou Redis).

---

## 6. Seuils paramétrables par verticale

### 6.1 Le problème du seuil unique

Un seuil de gel unique (ex: 10 000 CHF) ne reflète pas la réalité des métiers régulés :

- **Cabinet comptable :** 10 000 CHF est une déclaration significative
- **Banque :** 10 000 CHF est une transaction ordinaire (le seuil KYC est à 15 000 CHF)
- **Cabinet d'avocats :** le montant est souvent secondaire — c'est le type d'action qui compte (transfert de dossier, requête LLM externe)
- **Établissement de santé :** le montant est irrelevant — c'est le type de données qui compte (données de santé, diagnostic)

### 6.2 Solution : seuils par verticale

```python
self._freeze_thresholds = {
    "comptable": 10_000,   # Seuil standard
    "banque": 15_000,      # KYC renforcé FINMA
    "avocat": 0,           # Pas de seuil montant — gel par type d'action
    "sante": 0,            # Pas de seuil montant — gel par type de données
    "startup": 10_000,     # Seuil standard
    "rh": 10_000,          # Seuil standard
}
```

### 6.3 Seuil configurable par environnement

Le seuil par défaut est configurable via `.env` :

```bash
MEDIATOR_DEFAULT_FREEZE_THRESHOLD=10000
```

En production, chaque déploiement peut ajuster ce seuil sans toucher au code.

### 6.4 Null-safety du seuil

Pour les verticales sans seuil montant (avocat, santé), le seuil est à `0`. Le Médiateur ne déclenche **jamais** le gel par défaut pour ces verticales — seules les règles JsonLogic explicites s'appliquent :

- Avocat : gel si `action.type == "data_transfer"` ou `llm_provider == "external"`
- Santé : gel si `data_category == "donnees_sante"` ou `action.type == "diagnostic"`

---

## 7. Horodatage qualifié RFC 3161

### 7.1 Pourquoi l'HMAC ne suffit pas

Le journal WORM utilise HMAC-SHA-256 pour signer chaque entrée. C'est suffisant pour l'intégrité, mais pas pour la preuve juridique. Un HMAC prouve que l'entrée a été signée avec une clé connue, mais ne prouve pas **quand** elle a été signée (l'horodatage est dans les données, pas dans la signature).

Pour qu'un avocat puisse opposer le journal en justice, il faut un **horodatage qualifié** : un tiers de confiance (TSA) atteste cryptographiquement que les données existaient à un instant précis.

### 7.2 Architecture du service d'horodatage

```
Données → SHA-256 hash → Requête RFC 3161 → TSA (SwissSign/Certigna) → Token qualifié
                                                        │
                                              (si indisponible)
                                                        │
                                                  Fallback HMAC local
                                                  (non qualifié, journalisé)
```

### 7.3 Providers supportés

| Provider | Statut | Qualification | Usage |
|----------|--------|---------------|-------|
| SwissSign | Production | ✅ ZertES (Suisse) | Cabinets CH |
| Certigna | Production | ✅ eIDAS (France) | Cabinets FR |
| DigiCert | Test | ❌ Non certifié | Validation |
| HMAC local | Dev | ❌ Non qualifié | Développement |

### 7.4 Mode air-gap

En mode Haute Protection (infrastructure locale, air-gap), le système ne peut pas joindre un TSA externe. Deux options :

1. **Appliance TSA locale** : SwissSign propose des appliances qualifiées pour les réseaux isolés
2. **Documentation explicite** : documenter que les signatures HMAC sont utilisées dans ce cadre, avec les risques juridiques associés

L'auditeur devra valider l'option retenue.

---

## 8. Questions de robustesse

Cette section documente les questions ouvertes identifiées lors de l'implémentation. Elles seront résolues dans les sprints suivants.

### 8.1 Race condition dégel/résultat en vol

**Problème :** Si l'arbitrage est résolu (dégel) alors qu'un résultat Data ou Raisonnement est encore en vol sur le bus NATS, ce résultat pourrait ne pas être intégré au dashboard d'arbitrage.

**Scénario :**
1. Intention en `DEGRADED_FROZEN`
2. Agent Data publie un résultat sur `cleman.agent.result`
3. Simultanément, l'arbitre soumet sa décision → dégel → `PROCESSING`
4. Le Médiateur reçoit le résultat de Data mais l'intention n'est plus `DEGRADED_FROZEN`
5. Le résultat est traité comme un résultat normal (pas un enrichissement)

**Impact :** L'information n'est pas perdue (elle est dans `agent_positions` et le journal WORM), mais elle n'est pas marquée comme "enrichissement de gel" dans le dashboard.

**Mitigation actuelle :** `agent_positions` du Médiateur reste accessible en lecture après le dégel. Le dashboard peut consolider en lisant le journal WORM.

**Solution planifiée (Sprint 3) :** Ajouter une fenêtre de consolidation de 5 secondes après le dégel. Pendant cette fenêtre, les résultats en vol sont capturés et explicitement ajoutés au dashboard d'arbitrage.

### 8.2 Persistance des timers d'escalade

**Problème :** Les timers d'escalade sont des `asyncio.Task` en mémoire. Si le service redémarre, les timers en cours sont perdus et les escalades ne se déclenchent pas.

**Scénario :**
1. Arbitrage assigné à l'expert avec timeout 2h
2. Le service redémarre après 1h
3. Le timer est perdu
4. L'expert n'est jamais escaladé au suppléant

**Impact :** Un arbitrage peut rester en attente indéfiniment après un redémarrage.

**Mitigation actuelle :** Les arbitrages `pending` sont rechargés au démarrage, mais les timers ne sont pas re-programmés.

**Solution planifiée (Sprint 3) :** Persister les timers dans NATS KV ou Redis avec calcul du temps restant au redémarrage.

### 8.3 Mode dégradé et verticalités sans seuil montant

**Problème :** Pour les verticalités avocat et santé (seuil = 0), le gel par défaut basé sur le montant ne se déclenche jamais. Seules les règles JsonLogic explicites s'appliquent.

**Question :** Que se passe-t-il si une situation inédite (non couverte par les règles existantes) se produit dans ces verticalités ?

**Réponse actuelle :** Le Médiateur a un filet de sécurité `default_freeze` qui se déclenche pour les verticalités sensibles avec montant. Pour avocat/santé, ce filet ne s'active pas par montant. Mais le Médiateur détecte aussi les conflits entre agents (divergence de recommandation, écart de confiance) qui peuvent déclencher un gel indépendamment du montant.

**Recommandation :** Ajouter des tests d'intégration spécifiques pour un dossier médical et un transfert de fonds sans montant, pour vérifier que les règles JsonLogic couvrent ces cas.

### 8.4 Horodatage en mode air-gap

**Problème :** En mode Haute Protection (air-gap), le système ne peut pas joindre un TSA externe. Le fallback HMAC local n'est pas qualifié au sens eIDAS/ZertES.

**Question :** Les signatures HMAC sont-elles acceptables dans un cadre air-gap ?

**Réponse :** C'est un choix à documenter explicitement. Les auditeurs suisses (FINMA, OAR) peuvent accepter une documentation claire des limitations. Pour la certification L4, une appliance TSA locale qualifiée est recommandée.

---

## 9. Résultats et métriques

### 9.1 Tests

| Catégorie | Tests | Statut |
|-----------|-------|--------|
| Mode dégradé conforme | 11 | ✅ Pass |
| Escalade arbitrage | 7 | ✅ Pass |
| Seuils paramétrables | 6 | ✅ Pass |
| Horodatage RFC 3161 | 7 | ✅ Pass |
| **Total Sprint 2** | **31** | **✅ 31/31** |
| Tests existants (non-régression) | 40 | ✅ Pass |

### 9.2 Nouveaux sujets NATS

| Sujet | Usage |
|-------|-------|
| `cleman.mediator.degraded_freeze` | Enrichissement pendant gel dégradé |
| `cleman.arbitration.escalation` | Notification d'escalade |
| `cleman.arbitration.timeout` | Notification de timeout |

### 9.3 Nouveaux états

| État | Description |
|------|-------------|
| `DEGRADED_FROZEN` | Action bloqué, Data/Raisonnement actifs |

### 9.4 Nouvelles méthodes

| Méthode | Retour |
|---------|--------|
| `is_fully_frozen(id)` | `True` si `FROZEN` |
| `is_degraded_frozen(id)` | `True` si `DEGRADED_FROZEN` |
| `is_action_blocked(id)` | `True` si gel complet OU dégradé |

---

## 10. Feuille de route

### Sprint 3 (P1/P2)

| Priorité | Action | Statut |
|----------|--------|--------|
| P1 | Fenêtre de consolidation post-dégel (5s) | Planifié |
| P1 | Persistance timers escalade (NATS KV) | Planifié |
| P2 | Policy Manager UI (CRUD règles) | Planifié |
| P2 | Bac à sable règles (dry-run) | Planifié |
| P2 | Tests d'intégration verticales sans montant | Planifié |

### Sprint 4 (P3)

| Priorité | Action | Statut |
|----------|--------|--------|
| P3 | Haute disponibilité Orchestrateur (leader election) | Planifié |
| P3 | Signature électronique ZertES/eIDAS | Planifié |
| P3 | Appliance TSA locale (air-gap) | Étude |

---

## Conclusion

Le mode dégradé conforme est une contribution architecturale significative au domaine de la confiance IA régulée. Il démontre qu'il est possible de **concilier sécurité et efficacité** : l'exécution est protégée (Action bloqué) pendant que l'information est enrichie (Data/Raisonnement actifs).

Les 31 tests qui valident cette fonctionnalité, combinés aux 40 tests de non-régression, fournissent une base solide pour la certification. Les questions de robustesse identifiées (race condition, persistance des timers, horodatage air-gap) sont documentées et planifiées.

Cortex Leman v5 continue de démontrer qu'un système de confiance IA peut être **déterministe là où il faut, et intelligent là où on peut** — même pendant un gel.

---

*Ce livre blanc a été produit à partir du code source Cortex Leman v5.2*  
*246/246 tests ✅ • 51 endpoints • 33 sujets NATS • 22 règles JsonLogic • 6 verticales FR-CH*
