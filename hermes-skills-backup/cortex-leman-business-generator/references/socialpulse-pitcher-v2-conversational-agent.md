---
name: socialpulse-pitcher-v2-conversational-agent
version: 1.0.0
description: |
  PITCHER v2 — Agent conversationnel WhatsApp/SMS pour SocialPulse.
  Remplace le cold outreach statique par un moteur conversationnel avec:
  state machine (10 états), détection d'intention FR (8 types),
  no-show recovery, RGPD compliance, persistence JSON.
---

# PITCHER v2 — Agent Conversationnel

## THÈSE

Inspiré du playbook Serge Gatari ("Don't Run Ads. Build a Claude Agent Swarm Instead"):
au lieu d'un cold message statique → un agent conversationnel qui qualifie, nurture,
envoie les assets au bon moment, book le RDV, gère les no-shows.

## ARCHITECTURE: STATE MACHINE CONVERSATIONNELLE

```
COLD → ENGAGED → QUALIFIED → NURTURED → BOOKED → WON
                                    ↓         ↓
                                 OBJECTION  NO_SHOW → RESCHEDULED → BOOKED
                                    ↓
                                  LOST (STOP, refus, 3x no-show)
```

### 10 états de conversation

| État | Description | Transition vers |
|------|-------------|-----------------|
| COLD | Message initial envoyé, attente réponse | ENGAGED (positif) / LOST (STOP) |
| ENGAGED | Prospect a répondu, qualification en cours | QUALIFIED / OBJECTION / LOST |
| QUALIFIED | Besoin identifié, assets prêts à envoyer | NURTURED / OBJECTION / LOST |
| NURTURED | Assets envoyés (landing + vidéo), proposition RDV | BOOKED / OBJECTION / LOST |
| BOOKED | RDV planifié | WON / NO_SHOW / LOST |
| NO_SHOW | Prospect absent au RDV | RESCHEDULED / LOST (3x) |
| RESCHEDULED | RDV re-planifié après no-show | BOOKED / LOST |
| OBJECTION | Prix ou temps → handling | NURTURED / BOOKED / LOST |
| WON | Client signé | — |
| LOST | Refusé, désinscrit (STOP), 3x no-show | — |

### 8 types d'intention détectés (regex FR)

```python
POSITIVE:      "oui", "ça m'intéresse", "pourquoi pas", "ok je veux bien"
NEGATIVE:      "non", "pas intéressé", "non merci", "laissez tomber"
QUESTION:      "combien", "?", "comment", "c'est quoi", "quels sont"
BOOKING:       "dispo", "disponible", "quand", "créneau", "se voir"
OBJECTION_PRICE: "cher", "prix", "combien ça coûte", "budget"
OBJECTION_TIME:  "pas le temps", "occupé", "plus tard", "pas maintenant"
STOP:          "stop", "désinscription", "ne plus être contacté"
NEUTRAL:       fallback
```

Priorité: STOP > OBJECTION > BOOKING > POSITIVE > NEGATIVE > QUESTION > NEUTRAL

## ADAPTER: PitcherV2Adapter

```python
class PitcherV2Adapter:
    """Étend le pattern adapter avec persistence de conversations."""

    def __init__(self, state, journal, mediateur=None):
        self.pitcher = PitcherV2(clients_dir)
        self.conv_path = Path("state/conversations.json")

    def run(self, campaign, max_pitches=10):
        # Pour chaque lead filmed:
        # 1. Generate cold message
        # 2. Init ConversationContext
        # 3. Persist dans conversations.json
        # 4. Status → pitched
```

### Persistence

Chaque conversation est sérialisée dans `state/conversations.json`:

```json
{
  "buffalo-grill": {
    "lead_name": "Buffalo Grill",
    "state": "engaged",
    "cold_message": "Bonjour Marc, ...",
    "messages": [
      {"role": "agent", "text": "...", "timestamp": "..."},
      {"role": "prospect", "text": "Oui ça m'intéresse", "timestamp": "..."}
    ],
    "assets_sent": ["landing", "video"],
    "channel": "whatsapp",
    "created_at": "...",
    "last_updated": "..."
  }
}
```

Le contexte est reconstruit à chaque réponse prospect — stateless côté agent,
stateful côté storage.

## NO-SHOW RECOVERY: DOUBLE DÉTECTION

Le no-show a deux causes qu'il faut distinguer:

### 1. Détection temporelle (watchdog)

```python
def check_no_shows(conversations: dict) -> list:
    """BOOKED + date RDV passée sans WON → NO_SHOW."""
    for ctx in conversations.values():
        if ctx.state == BOOKED and ctx.booking:
            if datetime.fromisoformat(ctx.booking["datetime"]) < now:
                ctx.state = NO_SHOW
```

### 2. Détection textuelle (prospect signale absence rétroactive)

Le prospect peut signaler un no-show DANS la conversation:
- "Désolé j'ai pas pu venir"
- "J'ai manqué le rdv"
- "Je dois annuler"
- "Pas disponible"

Pattern regex dédié (`NOSHOW_PATTERNS`) intercepté dans `_booked_response`
AVANT le routing normal d'intention.

### Breakup après 3 no-shows

```python
if ctx.no_show_count >= 3:
    ctx.state = LOST
    return "Je vois qu'on n'a pas pu se connecter. Je vous laisse, bonne continuation !"
```

## RGPD COMPLIANCE

### STOP handler

Le mot-clé "STOP" déclenche immédiatement:
1. État → LOST
2. Message de confirmation de désinscription
3. Mention suppression données sous 30 jours

### Footer obligatoire

Chaque message agent se termine par:
```
_SocialPulse — STOP pour ne plus être contacté_
```
ou
```
SocialPulse · STOP pour ne plus être contacté
```

## SALUTATION CONTEXTUELLE

**Règle**: "Bonjour {prénom}" uniquement au 1er message agent.
Ensuite: pas de salutation (conversation naturelle).

```python
agent_msgs = [m for m in ctx.messages if m["role"] == "agent"]
if len(agent_msgs) <= 1:
    salut = f"Bonjour {fn}, "
else:
    salut = ""
```

## ASSETS TIMING

Les assets ne sont PAS envoyés dans le cold message. Ils sont envoyés
au bon moment conversationnel:

| État | Asset envoyé | Condition |
|------|-------------|-----------|
| ENGAGED → QUALIFIED | Landing page | Prospect dit "oui je veux voir" |
| QUALIFIED → NURTURED | Vidéo | Prospect a vu la landing, demande plus |
| NURTURED → BOOKED | Créneaux RDV | Prospect est chaud |

## PITFALLS

### 1. f-string imbriquées en Python 3.11

**Problème**: `f"{salut}{' ' if salut else ''}Bonjour"` → SyntaxError en 3.11.

**Solution**: Calculer le préfixe en amont, pas inline.

```python
# FAUX (3.11)
salut = f"Bonjour {fn}{', ' if fn else ','}"
text = f"{salut}{' ' if salut else ''}Merci"

# CORRECT
if len(agent_msgs) <= 1:
    salut = f"Bonjour {fn}, "  # trailing space incluse
else:
    salut = ""
text = f"{salut}Merci pour votre retour !"
```

### 2. assets_sent jamais mis à jour

**Problème**: La landing URL est affichée dans le message mais `ctx.assets_sent`
reste vide → le qualifier pense que l'asset n'a pas été envoyé.

**Solution**: Toujours faire `ctx.assets_sent.append("landing")` AU MOMENT
où l'URL apparaît dans le message, pas dans un handler séparé.

### 3. No-show non détecté textuellement

**Problème**: "Désolé j'ai pas pu venir" ne matche aucun des 8 intents standards.
Le prospect reste bloqué en BOOKED.

**Solution**: Patterns `NOSHOW_PATTERNS` dédiés interceptés dans `_booked_response`
AVANT le routing d'intention normal.

## FICHIERS CLÉS

```
agents/
├── pitcher_v2.py          # Moteur conversationnel (685 lignes)
└── v2_adapter.py          # PitcherV2Adapter (+ Builder/Filmer)
state/
└── conversations.json     # Persistence des conversations
```

## INTÉGRATION ORCHESTRATOR

```python
# orchestrator.py
from v2_adapter import BuilderV2Adapter, FilmerV2Adapter, PitcherV2Adapter

self.builder = BuilderV2Adapter(self.state, self.journal)
self.filmer = FilmerV2Adapter(self.state, self.journal)
self.pitcher = PitcherV2Adapter(self.state, self.journal, self.mediateur)
```

## COMMANDES

```bash
python3 orchestrator.py --agent pitcher    # Init cold messages
python3 agents/pitcher_v2.py               # Demo conversation (simulée)
```
