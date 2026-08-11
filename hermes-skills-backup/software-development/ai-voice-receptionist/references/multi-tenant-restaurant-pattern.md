# Multi-Tenant Restaurant Voice Agent Pattern

Session-proven architecture for building voice agents that serve multiple restaurants from a single codebase. Built and tested July 2026 for `~/prototypes/resto-voice-agent/`.

## Core Difference from Single-Domain Prototypes

| Aspect | Single-domain (medical, débarras) | Multi-tenant (restaurant) |
|--------|-----------------------------------|---------------------------|
| Config | Hardcoded in server.py | JSON file per client |
| System prompt | Static string | `build_system_prompt(config)` dynamic |
| Intent detection | First-match keywords | Weighted scoring |
| LLM dependency | Required for operation | Deterministic fallbacks (testable without API keys) |
| Metrics | None | Call log + dashboard (`/stats`) |
| Notification | None | Webhook to restaurant per order/reservation |

## Architecture

```
Caller → FastAPI backend
  ├── Config loader: JSON per restaurant
  ├── Guardrails: shared_ai_safety (R3=CB/plainte, R4=allergène)
  ├── Intent detection: weighted keyword scoring
  ├── LLM: GLM via Z.ai (with deterministic fallback if unavailable)
  ├── TTS: Edge TTS (fr-FR-DeniseNeural or per-config voice)
  ├── STT: Groq Whisper (or Z.ai fallback)
  ├── Call log: JSON file (last 500 calls)
  ├── Dashboard: GET /stats (calls, intents, resolution rate)
  └── Webhook: POST to restaurant's Discord/Slack/WhatsApp per event
```

## Intent Detection: Weighted Scoring (not first-match)

First-match produces false positives. Example: "vous êtes ouverts ce soir ?" matches `ce soir` as reservation intent. Weighted scoring fixes this:

```python
def detect_intent(text: str) -> str:
    t = text.lower()

    # Priority 1-3: Safety-critical (always checked first)
    if any(w in t for w in ["allerg", "intoxication", "malade", "urgence"]):
        return "emergency"
    if any(w in t for w in ["plainte", "mécontent", "réclam", "rembourse"]):
        return "complaint"
    if any(w in t for w in ["carte bancaire", "carte bleue", "cryptogramme", "cvv"]):
        return "payment_info"

    # Scoring for ambiguous intents
    scores = {"order": 0, "reservation": 0, "info": 0}

    order_kw = {"commander": 3, "à emporter": 3, "livrer": 3, "livraison": 3, "une pizza": 2}
    for kw, w in order_kw.items():
        if kw in t: scores["order"] += w

    resa_kw = {"réserver": 3, "réservation": 3, "une table": 3, "pour personnes": 2}
    for kw, w in resa_kw.items():
        if kw in t: scores["reservation"] += w

    info_kw = {"horaire": 3, "ouvert": 3, "adresse": 3, "livrez": 3, "quartier": 2}
    for kw, w in info_kw.items():
        if kw in t: scores["info"] += w

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"
```

**Key insight**: Words like "ce soir", "pour", "demain" are NOT reliable reservation keywords — they appear in info queries too. Use high-specificity keywords ("réserver", "une table") with weight ≥3.

## Deterministic Fallbacks (LLM-free operation)

The agent must respond intelligently even when the LLM is unreachable. Per-intent fallbacks:

```python
if intent == "payment_info":
    reply = "Pour la sécurité, je ne prends jamais les numéros de carte par téléphone."
elif intent == "info":
    if any(w in msg.lower() for w in ["livrez", "quartier", "zone"]):
        # Delivery-specific info from config
        zones = ", ".join(config["delivery"]["zones"])
        reply = f"Nous livrons à {zones}. Minimum {config['delivery']['min_order']}€."
    else:
        # Hours/Address from config
        reply = f"Nous sommes ouverts {day_name} de {today_hours}. Adresse: {config['address']}."
elif intent == "order":
    reply = "Je peux prendre votre commande. Qu'est-ce qui vous ferait plaisir ?"
elif intent == "reservation":
    reply = "Je peux prendre votre réservation. Pour combien de personnes et à quelle heure ?"
```

This makes the prototype **instantly testable** after clone — the 6 test scenarios all pass without any LLM key configured.

## Call Log + Dashboard

### Log structure

```python
def log_call(intent, issue, transcript="", reply=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "intent": intent,
        "issue": issue,  # "resolved" | "transferred"
        "transcript": transcript[:200],
        "reply": reply[:200],
    }
    # Append to JSON file, keep last 500
```

### Stats endpoint

```python
def get_stats():
    return {
        "total_calls": len(logs),
        "today_calls": len(today_logs),
        "today_intents": dict(Counter(l["intent"] for l in today_logs)),
        "today_issues": dict(Counter(l["issue"] for l in today_logs)),
        "resolution_rate": resolved / total * 100,
        "transfer_rate": transferred / total * 100,
        "recent_calls": today_logs[-10:],
    }
```

### Why this matters commercially

The dashboard IS the sales pitch. When pitching a restaurant:
- *"Your agent answered 47 calls this week, 89% resolved without bothering you."*
- *"12 orders captured at hours you couldn't answer."*
- *"Only 5 calls needed your attention — all complaints or complex requests."*

This data turns an abstract AI pitch into concrete ROI.

## Config Template

```json
{
  "restaurant_name": "Pizzeria Bella Italia",
  "phone": "+33 4 50 00 00 00",
  "address": "12 Rue de la Gare, 74100 Annemasse",
  "hours": {
    "lundi": "11:30-14:00, 18:00-22:00",
    "mardi": "11:30-14:00, 18:00-22:00",
    "mercredi": "11:30-14:00, 18:00-22:00",
    "jeudi": "11:30-14:00, 18:00-22:00",
    "vendredi": "11:30-14:00, 18:00-23:00",
    "samedi": "18:00-23:00",
    "dimanche": "fermé"
  },
  "delivery": {
    "enabled": true,
    "zones": ["Annemasse", "Gaillard", "Ambilly", "Ville-la-Grand"],
    "min_order": 15,
    "delivery_fee": 3.50,
    "estimated_time": "30-45 minutes"
  },
  "takeaway": true,
  "reservation": {"enabled": true, "max_guests": 20},
  "menu_highlights": ["Pizzas au feu de bois", "Pâtes fraîches maison"],
  "payment_methods": ["CB", "Espèces", "Tickets restaurant"],
  "transfer_phone": "+33 6 00 00 00 00",
  "tts_voice": "fr-FR-DeniseNeural",
  "personality": {"name": "Lina", "tone": "chaleureuse, efficace, naturelle"}
}
```

## Webhook Notification Format

Messages sent to restaurant's Discord/Slack/WhatsApp:

```
🍽️ NOUVELLE COMMANDE (14:32)
Client: Marie - +33 6 12 34 56 78
Mode: livraison
Adresse: 5 Rue des Lilas, Annemasse
Items: 1x Pizza Margherita, 1x Tiramisu

📅 NOUVELLE RÉSERVATION (19:15)
Nom: Dupont
Couverts: 4
Date: 2026-07-15 à 20:00

🔁 TRANSFERT REQUIS (12:08)
Raison: Réclamation client
Client: Pierre +33 6 98 76 54 32
```

## Tested Scenarios (6/6 pass, no LLM required)

| Input | Expected Intent | Expected Issue |
|-------|----------------|----------------|
| "Bonjour, vous êtes ouverts ce soir ?" | info | resolved |
| "Je voudrais commander une pizza à emporter" | order | resolved |
| "Je veux réserver une table pour 4 samedi" | reservation | resolved |
| "Vous livrez dans quels quartiers ?" | info | resolved |
| "Je veux payer par carte bleue" | payment_info | resolved (refused) |
| "Je suis mécontent, je veux faire une plainte" | complaint | transferred |

## Integration with Menuo Agency Kit

The voice agent is designed as an add-on to existing restaurant service packages:

| Tier | Existing | + Voice Agent |
|------|----------|---------------|
| Essentiel (149€+79€/mois) | QR menu | — |
| Growth (690€+299€/mois) | QR + orders + reviews + Instagram | + Voice pilot 60 days |
| Performance (1490€+690€/mois) | Full + ads + loyalty | + Voice unlimited |

The voice agent becomes the differentiator vs QR-only competitors. Cross-sell from existing SocialPulse/Menuo leads (206 Segment A restaurants).
