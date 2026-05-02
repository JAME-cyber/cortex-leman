"""
Cortex Leman v5 — Journal Append-Only Models

Modèles Pydantic pour les entrées du journal d'audit.
Chaque entrée est immuable, horodatée, hash-chainée.
"""
from enum import Enum
from typing import Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


class JournalEventType(str, Enum):
    """Types d'événements enregistrés dans le journal"""
    # Intentions
    INTENTION_CREATED = "intention.created"
    INTENTION_REVISED = "intention.revised"
    INTENTION_CANCELLED = "intention.cancelled"
    INTENTION_ROUTED = "intention.routed"

    # Agents
    AGENT_QUERY = "agent.query"
    AGENT_RESULT = "agent.result"
    AGENT_ERROR = "agent.error"

    # Médiateur
    MEDIATOR_CHECK = "mediator.check"
    MEDIATOR_CONFLICT = "mediator.conflict"
    MEDIATOR_FREEZE = "mediator.freeze"
    MEDIATOR_UNFREEZE = "mediator.unfreeze"

    # Arbitrage
    ARBITRATION_REQUESTED = "arbitration.requested"
    ARBITRATION_DECISION = "arbitration.decision"
    ARBITRATION_PRECEDENT = "arbitration.precedent"

    # Actions
    ACTION_EXECUTED = "action.executed"
    ACTION_COMPENSATED = "action.compensated"

    # Compliance
    COMPLIANCE_CHECK = "compliance.check"
    COMPLIANCE_VIOLATION = "compliance.violation"

    # Système
    SYSTEM_START = "system.start"
    SYSTEM_HEALTH = "system.health"
    SYSTEM_ERROR = "system.error"


class JournalEntry(BaseModel):
    """
    Entrée immuable du journal d'audit.
    Hash-chainée: chaque entrée contient le hash de la précédente.
    """
    entry_id: str = Field(..., description="UUID unique")
    sequence: int = Field(..., description="Numéro de séquence monotone")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: JournalEventType
    client_id: str
    vertical: str
    agent_source: str  # Nom de l'agent qui a produit l'événement
    intention_id: str  # Référence vers l'intention métier
    payload: dict[str, Any] = Field(default_factory=dict)
    previous_hash: str = Field(default="GENESIS")
    entry_hash: str = Field(default="", description="Calculé automatiquement")
    signature: Optional[str] = Field(default=None, description="Signature électronique")

    model_config = ConfigDict(frozen=True)  # Immuabilité garantie


class IntentionModel(BaseModel):
    """
    Représentation évolutive de l'intention métier.
    Versionnée: chaque modification crée une nouvelle version.
    """
    intention_id: str
    client_id: str
    vertical: str
    version: int = 1
    original_query: str
    refined_query: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)
    status: str = "active"  # active | frozen | completed | cancelled
    assigned_agents: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    regulatory_references: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    parent_intention_id: Optional[str] = None  # Pour les bifurcations


class ConflictRecord(BaseModel):
    """Enregistrement d'un conflit détecté par le Médiateur"""
    conflict_id: str
    intention_id: str
    agent_positions: dict[str, dict] = Field(default_factory=dict)
    conflict_reason: str
    severity: str = "medium"  # low | medium | high | critical
    frozen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False
    arbitration_id: Optional[str] = None


class ArbitrationDecision(BaseModel):
    """Décision d'arbitrage humain"""
    arbitration_id: str
    conflict_id: str
    intention_id: str
    arbiter_id: str  # Identité de l'humain
    arbiter_name: str
    decision: str  # approve | reject | modify
    justification: str
    selected_position: str  # Agent choisi
    modifications: dict[str, Any] = Field(default_factory=dict)
    signed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    timestamp_token: Optional[str] = None  # RFC 3161
    precedent_value: str = "none"  # none | weak | strong
