#!/usr/bin/env python3
"""
AI VOICE RECEPTIONIST — Server Template
========================================
Copy this file, customize SYSTEM_PROMPT + LeadTracker fields + business config.
Requires: fastapi, uvicorn[standard], edge-tts, httpx, python-multipart

Usage:
  set -a; source ~/.hermes/.env; set +a
  python server.py [PORT]
  → http://localhost:PORT
"""

import os, sys, io, json, re, asyncio
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import edge_tts, httpx, uvicorn

# ─── CONFIG ────────────────────────────────────────────
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.z.ai/api/coding/paas/v4")
LLM_API_KEY  = os.environ.get("GLM_API_KEY", "")
LLM_MODEL    = "glm-4.7"
TTS_VOICE    = "fr-CH-ArianeNeural"  # Run edge_tts.list_voices() to discover

COMPANY_NAME   = "Your Company"
HUMAN_NAME     = "The Human"  # Who gets escalation callbacks
PRICE_RANGE    = "à partir de 250€ selon volume"

# ─── SYSTEM PROMPT ─────────────────────────────────────
SYSTEM_PROMPT = f"""Tu es la réceptionniste IA de {COMPANY_NAME}.

Ton rôle: accueillir, qualifier la demande, donner une fourchette de prix indicative,
et transmettre à {HUMAN_NAME} qui rappellera pour confirmer.

CONTRAINTES:
- Réponses CONCISES (2-3 phrases max, style oral)
- JAMAIS de devis ferme — toujours "fourchette" ou "{HUMAN_NAME} confirmera"
- Si situation difficile → empathie + escalade immédiate vers {HUMAN_NAME}
"""

# ─── EMOTIONAL KEYWORDS ────────────────────────────────
EMERGENCY_KEYWORDS = [
    "décès", "décédé", "décédée", "mort", "deuil", "succession",
    "expulsion", "expulsé", "huissier", "diogène", "diogene",
    "urgenc", "vite", "immédiat",
]

# ─── LEAD TRACKER ──────────────────────────────────────
class LeadTracker:
    """Stateful conversation tracker. Customize fields per business type."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.conversation = []
        self.lead_data = {
            # Customize these fields per business:
            "property_type": None,
            "city": None,
            "volume": None,
            "urgency": None,
            # Standard fields (keep these):
            "emotional_flag": False,
            "emotional_reason": None,
            "escalated": False,
            "qualified": False,
            "timestamp": datetime.now().isoformat(),
        }
        self.lead_id = f"LEAD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def analyze_message(self, text: str) -> list:
        """Parse user message, extract structured data, detect emotion. Returns flags."""
        text_lower = text.lower()
        flags = []

        # Emotional detection
        for kw in EMERGENCY_KEYWORDS:
            if kw in text_lower:
                self.lead_data["emotional_flag"] = True
                if not self.lead_data["emotional_reason"]:
                    self.lead_data["emotional_reason"] = kw
                flags.append(f"⚠️ EMOTIONAL: {kw}")

        # --- Add business-specific parsing here ---
        # Example: city detection with known-cities list
        known_cities = ["Genève", "Lausanne", "Annemasse", "Annecy"]
        for city in known_cities:
            if city.lower() in text_lower and not self.lead_data["city"]:
                self.lead_data["city"] = city
                break

        self._check_qualified()
        return flags

    def _check_qualified(self):
        """Define when lead is 'qualified' (all required fields filled)."""
        d = self.lead_data
        self.lead_data["qualified"] = bool(d["city"] and d["volume"])

    def get_status(self) -> dict:
        return {
            "lead_id": self.lead_id,
            "data": self.lead_data,
            "qualified": self.lead_data["qualified"],
            "needs_escalation": self.lead_data["emotional_flag"] and not self.lead_data["escalated"],
        }

    def escalate(self):
        self.lead_data["escalated"] = True

lead = LeadTracker()

# ─── LLM CALL ──────────────────────────────────────────
async def call_llm(user_message: str) -> str:
    flags = lead.analyze_message(user_message)

    escalation = ""
    if lead.lead_data["emotional_flag"] and not lead.lead_data["escalated"]:
        escalation = f"\n⚠️ SITUATION SENSIBLE ({lead.lead_data.get('emotional_reason')}). Empathie + annonce rappel {HUMAN_NAME} <30min. STOP qualification."
        lead.escalate()

    closing = ""
    if lead.lead_data["qualified"]:
        closing = f"\n✅ LEAD QUALIFIÉ — Demande le numéro de téléphone et annonce que {HUMAN_NAME} rappellera."

    context = SYSTEM_PROMPT + f"\n\nLEAD: {json.dumps(lead.lead_data, ensure_ascii=False)}" + escalation + closing

    messages = [{"role": "system", "content": context}, *lead.conversation, {"role": "user", "content": user_message}]

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{LLM_BASE_URL}/chat/completions",
                json={"model": LLM_MODEL, "messages": messages, "max_tokens": 300, "temperature": 0.7},
                headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"})
            resp.raise_for_status()
            reply = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"[Erreur LLM: {str(e)[:80]}]"

    lead.conversation.append({"role": "user", "content": user_message})
    lead.conversation.append({"role": "assistant", "content": reply})
    return reply

# ─── TTS ───────────────────────────────────────────────
async def text_to_speech(text: str) -> bytes:
    clean = text.replace("*", "").replace("#", "").replace("|", "")
    communicate = edge_tts.Communicate(clean, TTS_VOICE)
    audio = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.write(chunk["data"])
    return audio.getvalue()

# ─── FASTAPI ───────────────────────────────────────────
app = FastAPI(title=f"{COMPANY_NAME} Receptionist")
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    html = static_dir / "index.html"
    return HTMLResponse(html.read_text()) if html.exists() else HTMLResponse("<h1>No index.html</h1>")

@app.post("/chat")
async def chat_text(message: str = Form(...)):
    reply = await call_llm(message)
    return {"reply": reply, "lead": lead.get_status()}

@app.post("/tts")
async def tts_endpoint(text: str = Form(...)):
    return StreamingResponse(io.BytesIO(await text_to_speech(text)), media_type="audio/mpeg")

@app.get("/lead")
async def get_lead():
    return lead.get_status()

@app.get("/reset")
async def reset():
    lead.reset()
    return {"status": "reset", "lead_id": lead.lead_id}

# ─── STARTUP ───────────────────────────────────────────
if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"\n  {COMPANY_NAME} — AI Receptionist → http://localhost:{port}\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
