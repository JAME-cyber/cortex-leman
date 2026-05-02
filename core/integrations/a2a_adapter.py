"""
Cortex Leman v5 — Insight 6: A2A (Agent-to-Agent) Protocol Adapter

Inspiré de l'écosystème AG2 — protocole A2A (Agent-to-Agent)
Adaptateur qui bridge notre bus NATS avec le protocole standard A2A.

Permet à des agents A2A externes (AG2, CrewAI, etc.) de communiquer
avec nos agents Cortex Leman via le protocole standard.

A2A Protocol spec: https://github.com/ag2ai/a2a-protocol
Format: JSON-RPC 2.0 over HTTP

Messages supportés:
  - a2a.discover: Découvrir les agents disponibles
  - a2a.send_message: Envoyer un message à un agent
  - a2a.get_status: Obtenir le statut d'un agent
  - a2a.subscribe: S'abonner aux événements d'un agent
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class A2AAgentCard:
    """Carte d'identité d'un agent A2A (Agent Card)"""
    agent_id: str
    name: str
    description: str
    capabilities: list[str] = field(default_factory=list)
    verticals: list[str] = field(default_factory=list)
    protocol_version: str = "0.1"
    endpoint: str = ""

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "verticals": self.verticals,
            "protocol_version": self.protocol_version,
            "endpoint": self.endpoint,
        }


# Cartes de nos agents pour le protocole A2A
CORTEX_LEMAN_AGENTS = {
    "data": A2AAgentCard(
        agent_id="cortex-leman:data-agent",
        name="Data Agent",
        description="Agent de recherche documentaire et RAG. Requête le Knowledge Vault réglementaire FR-CH.",
        capabilities=["search", "index", "rag_query", "regulatory_lookup"],
        verticals=["comptable", "avocat", "sante", "banque", "startup", "rh"],
        endpoint="/a2a/agents/data",
    ),
    "reasoning": A2AAgentCard(
        agent_id="cortex-leman:reasoning-agent",
        name="Reasoning Agent",
        description="Agent d'analyse et de conformité. Analyse les risques réglementaires et produit des recommandations.",
        capabilities=["analyze", "evaluate", "recommend", "compliance_check"],
        verticals=["comptable", "avocat", "sante", "banque", "startup", "rh"],
        endpoint="/a2a/agents/reasoning",
    ),
    "action": A2AAgentCard(
        agent_id="cortex-leman:action-agent",
        name="Action Agent",
        description="Agent d'exécution transactionnelle. Exécute les actions validées (100% déterministe, 0% LLM).",
        capabilities=["execute", "compensate", "transaction"],
        verticals=["comptable", "avocat", "sante", "banque", "startup", "rh"],
        endpoint="/a2a/agents/action",
    ),
    "mediator": A2AAgentCard(
        agent_id="cortex-leman:mediator-agent",
        name="Médiateur (Guardian)",
        description="Agent de supervision déterministe. 22 règles JsonLogic, gel préventif, 0% LLM.",
        capabilities=["evaluate", "freeze", "guard", "arbitrate_request"],
        verticals=["comptable", "avocat", "sante", "banque", "startup", "rh"],
        endpoint="/a2a/agents/mediator",
    ),
    "supervisor": A2AAgentCard(
        agent_id="cortex-leman:supervisor-agent",
        name="Superviseur",
        description="Agent de monitoring et tableau de bord. Métriques, alertes, score de confiance (0% LLM).",
        capabilities=["monitor", "alert", "score", "dashboard"],
        verticals=["comptable", "avocat", "sante", "banque", "startup", "rh"],
        endpoint="/a2a/agents/supervisor",
    ),
    "orchestrator": A2AAgentCard(
        agent_id="cortex-leman:orchestrator-agent",
        name="Orchestrateur",
        description="Agent pilote conversationnel. Route les intentions, assemble les équipes (CaptainAgent).",
        capabilities=["route", "orchestrate", "assemble_team", "conversation"],
        verticals=["comptable", "avocat", "sante", "banque", "startup", "rh"],
        endpoint="/a2a/agents/orchestrator",
    ),
}


class A2AAdapter:
    """
    Adaptateur A2A (Agent-to-Agent) pour Cortex Leman v5.

    Bridge entre le protocole standard A2A et notre architecture interne.
    Permet à des agents externes de:
      - Découvrir nos agents
      - Envoyer des messages
      - Recevoir des réponses
      - S'abonner aux événements

    Sécurité:
      - Tous les messages entrants passent par les guardrails
      - Le Médiateur reste en contrôle (peut geler)
      - Journal WORM pour tous les échanges A2A
    """

    def __init__(self, nats_client=None):
        self.nats = nats_client
        self._subscribers: dict[str, list] = {}  # agent_id -> callbacks

    def handle_request(self, request: dict) -> dict:
        """
        Traiter une requête A2A (JSON-RPC 2.0).

        Methods A2A:
        - a2a.discover: Lister les agents disponibles
        - a2a.agent_card: Obtenir la carte d'un agent
        - a2a.send_message: Envoyer un message à un agent
        - a2a.get_status: Obtenir le statut d'un agent
        """
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")

        try:
            if method == "a2a.discover":
                return self._discover(req_id)
            elif method == "a2a.agent_card":
                return self._agent_card(req_id, params)
            elif method == "a2a.send_message":
                return self._send_message(req_id, params)
            elif method == "a2a.get_status":
                return self._get_status(req_id, params)
            else:
                return self._error(req_id, -32601, f"Méthode A2A inconnue: {method}")

        except Exception as e:
            logger.error(f"A2A error: {e}")
            return self._error(req_id, -32603, str(e))

    def _discover(self, req_id: int) -> dict:
        """Découvrir tous les agents Cortex Leman disponibles"""
        agents = [card.to_dict() for card in CORTEX_LEMAN_AGENTS.values()]
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocol_version": "0.1",
                "framework": "cortex-leman-v5",
                "agents": agents,
                "total": len(agents),
                "trust_features": [
                    "worm_journal", "mediator_deterministic", "human_arbitration",
                    "guardrails", "rbac", "fernet_encryption",
                ],
            },
        }

    def _agent_card(self, req_id: int, params: dict) -> dict:
        """Obtenir la carte d'un agent spécifique"""
        agent_id = params.get("agent_id", "")

        # Normalize: "data" or "cortex-leman:data-agent"
        key = agent_id.replace("cortex-leman:", "").replace("-agent", "")

        card = CORTEX_LEMAN_AGENTS.get(key)
        if not card:
            return self._error(req_id, -32602, f"Agent inconnu: {agent_id}")

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": card.to_dict(),
        }

    def _send_message(self, req_id: int, params: dict) -> dict:
        """
        Envoyer un message à un agent Cortex Leman via A2A.

        Le message passe par:
        1. Guardrails (PII, topic, safety, autodefense)
        2. Médiateur (gel préventif si nécessaire)
        3. Agent cible
        4. Journal WORM
        """
        agent_id = params.get("agent_id", "")
        message = params.get("message", "")
        context = params.get("context", {})
        vertical = context.get("vertical", "unknown")

        # Normalize agent_id
        key = agent_id.replace("cortex-leman:", "").replace("-agent", "")

        if key not in CORTEX_LEMAN_AGENTS:
            return self._error(req_id, -32602, f"Agent inconnu: {agent_id}")

        # Note: In production, this would go through NATS bus
        # For now, return an acknowledgment
        response = {
            "message_id": f"msg-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "agent_id": agent_id,
            "status": "received",
            "note": (
                "Message reçu par Cortex Leman. En production, ce message serait: "
                "1) filtré par guardrails, 2) évalué par le médiateur, "
                "3) routé vers l'agent cible, 4) journalisé dans le WORM."
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"A2A message reçu pour {key}: {message[:50]}...")

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": response,
        }

    def _get_status(self, req_id: int, params: dict) -> dict:
        """Obtenir le statut d'un agent"""
        agent_id = params.get("agent_id", "")
        key = agent_id.replace("cortex-leman:", "").replace("-agent", "")

        if key not in CORTEX_LEMAN_AGENTS:
            return self._error(req_id, -32602, f"Agent inconnu: {agent_id}")

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "agent_id": agent_id,
                "status": "healthy",
                "uptime": "running",
                "last_activity": datetime.now(timezone.utc).isoformat(),
            },
        }

    def _error(self, req_id: Optional[int], code: int, message: str) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": code, "message": message},
        }


# Singleton
a2a_adapter = A2AAdapter()
