---
name: ai-voice-receptionist
description: Build voice-based conversational AI agents for business call handling — qualification, lead tracking, emotional escalation, and human handoff. Single-file FastAPI + Edge TTS + LLM pipeline for rapid prototyping.
---

# AI Voice Receptionist Prototypes

Build voice-based conversational AI agents for business call handling: qualification, lead tracking, emotional escalation, and human handoff. Single-file FastAPI server + browser frontend, designed for rapid prototyping and reversibility.

## When to Use

- User wants an AI receptionist / call handler / qualification bot
- Business needs H24 call answering with lead capture
- Industry with emotional situations (débarras, medical, legal, funeral) needing human escalation
- Any voice prototype: STT → LLM → TTS pipeline

## Architecture

### Mode 1: Stack classique (VAD → STT → LLM → TTS)
```
Browser (mic + UI) → FastAPI backend
  ├── STT: Browser Web Speech API (free) or Groq Whisper API
  ├── LLM: Z.ai GLM-4.7 (OpenAI-compatible endpoint)
  ├── TTS: Edge TTS (free, no API key, FR-CH voices available)
  └── LeadTracker: stateful conversation + intent extraction
```

### Mode 2: Stack MLLM natif audio (VAD → MLLM → TTS) — 2026
```
Mic → HF speech-to-speech server (ws://localhost:8765/v1/realtime)
  ├── VAD: Silero VAD v5 (détection parole + turn-taking)
  ├── MLLM: Ultravox v0.4 (audio direct → LLM, 150ms TTFT, open weights)
  └── TTS: Qwen3-TTS (default) ou Edge TTS ou Kokoro-82M
```

**Avantages du Mode 2 pour réceptionniste :**
- **Latence**: ~150ms TTFT (Ultravox) vs ~800ms-1.2s (stack classique)
- **FR-CH accent**: Le MLLM entend directement — pas d'erreur de transcription
- **Émotion depuis la voix**: Ton tremblant, colère, hésitation détectés nativement
- **Emotional escalation améliorée**: Le modèle entend la détresse vocale, pas juste les mots
- **Paralangage**: Soupirs, hésitations, silences significatifs préservés

**Quand utiliser quel mode :**
| Critère | Mode 1 (STT) | Mode 2 (MLLM) |
|---|---|---|
| Latence critique | ❌ | ✅ |
| GPU disponible | ❌ | ✅ (Ultravox) |
| FR-CH accent lourd | ❌ (Whisper erreurs) | ✅ |
| Démo rapide / prototype | ✅ (zero infra) | ❌ |
| Émotion dans la voix | ❌ (texte only) | ✅ |
| Coût | ✅ (gratuit) | ⚠️ (GPU cloud) |

### Quickstart Mode 2 (HF speech-to-speech)
```bash
pip install speech-to-speech
# Démarrer le serveur Realtime-compatible
speech serve
# Connecter depuis un client (browser, CLI, tel)
speech-to-speech talk --url ws://127.0.0.1:8765/v1/realtime
```

Le serveur expose l'API OpenAI Realtime → compatible avec tous les clients Realtime existants.
Swap des composants via CLI flags. Voir github.com/huggingface/speech-to-speech.

### Key Design Decisions

1. **TTS = Edge TTS** (free, no key). Use `edge_tts.list_voices()` to discover valid voice names. Invalid voice → `NoAudioReceived` error.
2. **STT = Browser Web Speech API** by default (zero cost, works Chrome/Firefox). Groq Whisper as server-side fallback if needed.
3. **LLM = Z.ai coding endpoint** (`https://api.z.ai/api/coding/paas/v4`). Supports `chat/completions` with `glm-4.7`. Does NOT support `audio/transcriptions` (returns "Unknown Model").
4. **Emotional escalation**: detect keywords → switch LLM behavior to empathetic + announce human callback → stop cold qualification. **En Mode 2 MLLM**: le modèle peut aussi détecter l'émotion depuis le ton de voix lui-même.
5. **LeadTracker class**: stateful object that parses each user message for structured data (property type, city, volume, floor, urgency) via regex + keyword matching. Feeds context back to LLM.
6. **Mode 2 MLLM (Ultravox/HF s2s)**: Quand la latence et l'émotion comptent (clients B2B payants). Ultravox v0.4 = LLM + audio projector (open weights, fixie-ai/ultravox). HF speech-to-speech = pipeline complet VAD→MLLM→TTS compatible OpenAI Realtime.

## Build Steps

1. **Setup venv + deps**:
   ```bash
   uv venv .venv --python 3.11
   .venv/bin/python -m pip install fastapi "uvicorn[standard]" openai edge-tts httpx python-multipart
   ```
   Note: `"uvicorn[standard]"` (with quotes) avoids shell issues. Install deps one-by-one if bulk install times out.

2. **Load API keys** from Hermes env:
   ```bash
   set -a; source ~/.hermes/.env; set +a
   ```

3. **Create server.py** — see `templates/server_template.py` for the full pattern (system prompt, LeadTracker, FastAPI routes, TTS/STT functions).

4. **Create static/index.html** — mobile-first chat UI with:
   - Text input + voice recording button (MediaRecorder API)
   - Real-time lead tracker panel (optional, for B2B demos)
   - Scenario quick-test badges (auto-play scripted conversations for sales demos)

5. **Start server** (background, no notify — it's a daemon):
   ```bash
   .venv/bin/python server.py 8002
   ```

6. **Test** — use curl for API tests, browser for full UX:
   ```bash
   curl -s -X POST http://localhost:8002/chat -F "message=Bonjour, je voudrais un rendez-vous"
   curl -s -o test.mp3 -X POST http://localhost:8002/tts -F "text=Bonjour, ceci est un test"
   ```

## Pitfalls

- **Invalid Edge TTS voice name** → `edge_tts.exceptions.NoAudioReceived`. ALWAYS call `edge_tts.list_voices()` first. French voices: `fr-FR-DeniseNeural`, `fr-FR-EloiseNeural`, `fr-CH-ArianeNeural` (Swiss female), `fr-CH-FabriceNeural` (Swiss male).
- **Z.ai coding endpoint ≠ general endpoint**. Coding = `api.z.ai/api/coding/paas/v4`. No audio/transcriptions support (returns error 1211 "Unknown Model").
- **`browser_vision` fails with Z.ai model** (`messages.content.type is invalid`). Vision analysis returns 400. Screenshots still get saved to `~/.hermes/cache/screenshots/` — use `vision_analyze` with `image_url` pointing to the screenshot path instead, or deliver the path directly via `MEDIA:<path>`.
- **Server background launch** → use `terminal(background=true, notify_on_complete=false)` for long-lived servers. The hint about "bounded task" doesn't apply to daemons.
- **uvicorn install** → use `"uvicorn[standard]"` with quotes. Bare `uvicorn` sometimes triggers tool guardrails.
- **French city parsing** → use a known-cities list (case-insensitive match) BEFORE regex fallback. Regex `à\s+([A-Z]...)` misses lowercase input and false-positives on words like "vite", "demain".
- **Emotional keyword matching** → include both accented and unaccented variants: `"diogène"` AND `"diogene"`, `"décédé"` AND `"décédée"`.

## Emotional Escalation Pattern

For businesses involving sensitive situations (death, eviction, hoarding):

```python
EMERGENCY_KEYWORDS = [
    "décès", "décédé", "décédée", "mort", "deuil", "succession",
    "expulsion", "expulsé", "expulsée", "huissier",
    "diogène", "diogene", "insalubre",
    "urgenc", "vite", "immédiat",
]

# In LeadTracker.analyze_message():
if keyword detected:
    lead_data["emotional_flag"] = True
    lead_data["emotional_reason"] = keyword
    # LLM gets injection: "⚠️ SITUATION SENSIBLE — empathie + annonce rappel humain <30min"
    # Qualification STOPS — human takes over
```

The system prompt must instruct the LLM: "For emotional situations → empathy + announce human callback. Do NOT continue cold qualification."

## Business Model: "IA qualifie, humain ferme"

For emotionally-charged industries (débarras, medical, legal):

| What the AI does | What stays human |
|---|---|
| Answer H24 (capture nocturnal/weekend leads) | Final price negotiation |
| Pre-qualify (type, volume, city, access, urgency) | Emotional situation handling |
| Give indicative price range (never firm quote) | On-site evaluation |
| Detect emotional situations → escalate | Emergency decisions (asbestos, biohazards) |
| SMS/WhatsApp confirmation | Closing the deal |

The pitch: *"You never lose a call, even at 10pm or Sunday."* In service businesses, callers who hit voicemail call the next competitor. That's the ROI.

## Guardrails Integration (shared_ai_safety)

All voice receptionist prototypes should integrate the `~/shared_ai_safety/` package as a pre-LLM safety layer. This prevents prompt injection, blocks dangerous inputs before any LLM tokens are consumed, and provides per-domain risk classification.

### Integration (4 lines in server.py)

```python
sys.path.insert(0, os.path.expanduser("~"))
from shared_ai_safety import SecurityGuardrails, RiskClassifier, RiskLevel

# Domain profiles — patterns that elevate risk for THIS business
clf = RiskClassifier()
clf.add_domain_profile("R3", {"symptôme": "Description de symptômes médicaux"})
clf.add_domain_profile("R4", {"urgence vitale": "Urgence vitale potentielle"})
guardrails = SecurityGuardrails(risk_classifier=clf)
```

### Modified `call_llm()` signature

```python
async def call_llm(user_message: str) -> tuple:
    """Returns (reply: str, risk: RiskAssessment | None, verification: VerificationResult | None)"""
    
    # Validate BEFORE LLM call
    validation = guardrails.validate_request("user", {"type": "llm_requests", "prompt": user_message})
    
    if not validation["allowed"]:
        # R4 → safe fallback, NO LLM call
        return domain_fallback_response(validation["risk"]), validation["risk"], None
    
    # ... normal LLM flow ...
    
    # AFTER LLM: verify action claims against real executions
    verification = action_verifier.verify("user", reply)
    if verification.has_hallucinations:
        logger.warning(f"🚨 HALLUCINATION — LLM claims: {[c.action_name for c in verification.unverified_claims]}")
    
    return reply, risk, verification
```

## Action Verifier Integration (post-LLM hallucination detection)

**Problem:** LLMs claim to have done things ("RDV confirmé", "devis envoyé") without the system actually executing them. The guardrails validate input; the action verifier validates output claims against real executions.

### Integration (5 lines in server.py)

```python
from shared_ai_safety import ActionVerifier, register_medical_actions  # or register_debarras_actions

action_verifier = ActionVerifier()
register_medical_actions(action_verifier)  # pre-built action keywords

# When your code ACTUALLY does something (booking, lead creation, etc.):
action_verifier.mark_executed(user_id, "book_appointment", details={"doctor": "Dr. Martin", "time": "14:00"})

# After the LLM responds, verify its claims:
verification = action_verifier.verify(user_id, llm_reply)
# verification.has_hallucinations → True if LLM claims actions that weren't executed
# verification.trust_score → 0.0-1.0 (1.0 = all claims verified)
# verification.suggested_correction → text to append or re-prompt the LLM
```

### Endpoints — expose trust score

```python
# POST /chat JSON response:
"verification": verification.to_dict() if verification else None,
# Contains: has_hallucinations, trust_score, verified_claims, unverified_claims, suggested_correction

# POST /chat/voice headers:
"X-Trust-Score": str(round(verification.trust_score, 2)) if verification else "1.0",
"X-Hallucination": "true" if (verification and verification.has_hallucinations) else "false",
```

### Registering real actions (the critical link)

The verifier only works if `mark_executed()` is called when the system actually performs an action:

| Prototype | Action name | Where to call mark_executed() |
|-----------|------------|-------------------------------|
| Medical | `book_appointment` | Inside `book_slot()` when slot confirmed |
| Medical | `cancel_appointment` | Inside cancel handler |
| Débarras | `create_lead` | When `lead.qualified == True` |
| Débarras | `create_quote` | When quote PDF generated |
| Débarras | `schedule_visit` | When visit appointment created |

### Available presets

- `register_medical_actions(v)` — book_appointment, cancel_appointment, call_emergency
- `register_debarras_actions(v)` — create_quote, schedule_visit, create_lead

### ActionVerifier.register_action() — correct signature (Jul 2026)

The method signature is `register_action(name, keywords, severity, description, negate_patterns)` — NOT `(name, description, requires_details)` which will throw `TypeError`.

```python
from shared_ai_safety import ActionVerifier, Severity

v = ActionVerifier()
v.register_action(
    "take_order",
    keywords=["commande", "commander", "à emporter", "noté", "enregistré"],
    severity=Severity.HIGH,
    description="Prendre une commande",
)
v.register_action(
    "make_reservation",
    keywords=["réservé", "réservation", "table", "créneau"],
    severity=Severity.HIGH,
    description="Prendre une réservation",
)
```

**Pitfall**: If you get `TypeError: ActionVerifier.register_action() got an unexpected keyword argument 'requires_details'`, you are using the old API. Switch to `keywords=` + `severity=`.

### Domain-Specific Fallback Responses (R4 blocks)

| Domain | Trigger | Fallback |
|--------|---------|----------|
| Medical | "urgence vitale" | "Appelez le 144 (CH) / 15 (FR) immédiatement" |
| Débarras | "amiant", "matière dangereuse" | "Je transmets à {HUMAN} pour intervention spécialisée" |
| Any | Prompt injection | "Je n'ai pas compris, reformulez" |
| Any | Données bancaires | "Je ne peux pas traiter cela par ce canal" |

### Endpoints affected

- `POST /chat` → unpack `(reply, risk)` tuple, add `"risk": {...}` to JSON response
- `POST /chat/voice` → add `X-Risk-Level` and `X-Risk-Score` headers
- Add `GET /security/report` → expose `guardrails.get_security_report(hours=24)`

**See also:** `references/shared-ai-safety-modules.md` for complete documentation of all 7 modules (risk_matrix, classifier, guardrails, structured_logger, workflow_validator, memory_service, action_verifier) including deployment status and integration patterns.

### Deployed Prototypes

| Prototype | Port | Domain profiles | Guardrails | Action Verifier | Status |
|-----------|------|----------------|------------|-----------------|--------|
| réceptionniste-ia | 8000 | Medical R3/R4 (symptômes, urgences vitales) | ✅ Pré-LLM | ✅ Post-LLM (book_appointment) | ✅ Live |
| darkom-debarras | 8002 | Débarras R2/R3/R4 (devis, succession, amiante) | ✅ Pré-LLM | ✅ Post-LLM (create_lead) | ✅ Live |
| resto-voice-agent | 8010 | Restaurant R3/R4 (CB, allergie, réclamation) | ✅ Pré-LLM | ✅ Post-LLM (take_order, make_reservation) | ✅ Live |

## Multi-Tenant Restaurant Voice Agent Pattern

When building voice agents for restaurants (or any multi-client vertical), the architecture differs from single-domain prototypes. See `references/multi-tenant-restaurant-pattern.md` for the full implementation guide. Key differences:

### 1. JSON config per restaurant (not hardcoded)

```json
// configs/restaurant_template.json
{
  "restaurant_name": "Pizzeria Bella Italia",
  "hours": {"lundi": "11:30-14:00, 18:00-22:00", ...},
  "delivery": {"enabled": true, "zones": [...], "min_order": 15, "delivery_fee": 3.50},
  "takeaway": true,
  "reservation": {"enabled": true, "max_guests": 20},
  "menu_highlights": ["Pizzas au feu de bois", ...],
  "payment_methods": ["CB", "Espèces"],
  "transfer_phone": "+33 6 ...",
  "tts_voice": "fr-FR-DeniseNeural",
  "personality": {"name": "Lina", "tone": "chaleureuse"}
}
```

Each restaurant gets its own config file. The system prompt is **generated dynamically** from the config via `build_system_prompt(config)`.

### 2. Intent detection by weighted scoring (not first-match)

First-match keyword detection produces false positives ("vous êtes ouverts ce soir ?" → matched "ouverts" as reservation). Use weighted scoring instead:

```python
scores = {"order": 0, "reservation": 0, "info": 0}
for kw, weight in order_keywords.items():
    if kw in text_lower: scores["order"] += weight
for kw, weight in reservation_keywords.items():
    if kw in text_lower: scores["reservation"] += weight
# ... etc
best = max(scores, key=scores.get)
```

Priority overrides for safety-critical intents: `emergency` > `complaint` > `payment_info` (always checked first, before scoring).

### 3. Deterministic fallbacks (LLM-free operation)

When the LLM is unreachable (API key not resolved, network issue, rate limit), the agent must still function using deterministic responses per intent:

```python
if intent == "info" and any(w in msg for w in ["livrez", "quartier"]):
    zones = ", ".join(config["delivery"]["zones"])
    reply = f"Nous livrons à {zones}. Minimum {config['delivery']['min_order']}€."
elif intent == "payment_info":
    reply = "Pour la sécurité, je ne prends pas les numéros de carte par téléphone."
```

This ensures the prototype is testable immediately after `git clone` — no API keys required for the first demo.

### 4. Call logging + dashboard metrics

Every call logged to JSON file with: timestamp, intent, issue (resolved/transferred), transcript excerpt. Exposed via `GET /stats`:
- `today_calls`, `total_calls`
- `resolution_rate`, `transfer_rate`
- `today_intents` (dict: intent → count)
- `recent_calls` (last 10)

This data is the **sales pitch** — it proves ROI: *"Your agent answered 47 calls this week, resolved 89% without transfer, captured 12 orders."*

### 5. Webhook notification to restaurant

When an order or reservation is captured, notify the restaurant immediately via webhook (Discord/Slack/WhatsApp/Twilio SMS):

```python
async def notify_restaurant(intent, details, config):
    webhook_url = config.get("webhook_url")
    if webhook_url:
        await httpx.AsyncClient().post(webhook_url, json={"text": format_notification(intent, details)})
```

### 6. Startup

```bash
cd ~/prototypes/resto-voice-agent
python3.12 server.py --config configs/restaurant_template.json --port 8010
# Dashboard: http://localhost:8010/stats
# Test UI:  http://localhost:8010/
```

### Restaurant domain risk profiles

```python
_resto_r3 = {
    "numéro de carte": "Donnée bancaire — refuser",
    "cryptogramme": "Donnée bancaire — refuser",
    "CVV": "Donnée bancaire — refuser",
    "plainte": "Réclamation — transférer",
    "avocat": "Menace juridique — transférer",
    "hygiène": "Réclamation hygiène — transférer",
}
_resto_r4 = {
    "allergène grave": "Urgence allergie — transférer",
    "intoxication": "Urgence — transférer",
}
```

## References

- `references/edge-tts-voices.md` — Edge TTS voice discovery, error fixes, FR-CH voices
- `references/zai-api-capabilities.md` — Z.ai coding endpoint: what works, what doesn't
- `references/multi-tenant-restaurant-pattern.md` — Multi-tenant restaurant voice agent: config, scoring intents, deterministic fallbacks, dashboard metrics
