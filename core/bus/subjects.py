"""
Cortex Leman v5 — NATS Subjects Registry

Tous les sujets du bus de coordination.
Convention: cleman.<domain>.<action>.<vertical?>
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Subjects:
    """Registry immutable des sujets NATS"""

    # Orchestrateur → Agents
    INTENTION_NEW: str = "cleman.intention.new"
    INTENTION_REVISE: str = "cleman.intention.revise"
    INTENTION_CANCEL: str = "cleman.intention.cancel"
    INTENTION_ROUTE: str = "cleman.intention.route"

    # Résultats génériques (publié par tous les agents)
    AGENT_RESULT: str = "cleman.agent.result"

    # Agent Data
    DATA_QUERY: str = "cleman.data.query"
    DATA_RESULT: str = "cleman.data.result"
    DATA_SCAN_INTERNAL: str = "cleman.data.scan.internal"
    DATA_SCAN_EXTERNAL: str = "cleman.data.scan.external"

    # Agent Raisonnement
    REASONING_ANALYZE: str = "cleman.reasoning.analyze"
    REASONING_RESULT: str = "cleman.reasoning.result"
    REASONING_COMPARE: str = "cleman.reasoning.compare"
    REASONING_RECOMMEND: str = "cleman.reasoning.recommend"
    REASONING_REFLECT: str = "cleman.reflection.check"  # Reflection Node (JP Morgan pattern)

    # Agent Action
    ACTION_EXECUTE: str = "cleman.action.execute"
    ACTION_RESULT: str = "cleman.action.result"
    ACTION_COMPENSATE: str = "cleman.action.compensate"
    ACTION_NOTIFY: str = "cleman.action.notify"

    # Agent Superviseur / Validation
    VALIDATE_REQUEST: str = "cleman.validate.request"
    VALIDATE_RESULT: str = "cleman.validate.result"

    # Médiateur
    MEDIATOR_CHECK: str = "cleman.mediator.check"
    MEDIATOR_CONFLICT: str = "cleman.mediator.conflict"
    MEDIATOR_FREEZE: str = "cleman.mediator.freeze"
    MEDIATOR_DEGRADED_FREEZE: str = "cleman.mediator.degraded_freeze"  # P0: mode dégradé
    MEDIATOR_UNFREEZE: str = "cleman.mediator.unfreeze"

    # Arbitrage humain
    ARBITRATION_REQUEST: str = "cleman.arbitration.request"
    ARBITRATION_DECISION: str = "cleman.arbitration.decision"
    ARBITRATION_PRECEDENT: str = "cleman.arbitration.precedent"
    ARBITRATION_ESCALATION: str = "cleman.arbitration.escalation"  # P0: escalade suppléant
    ARBITRATION_TIMEOUT: str = "cleman.arbitration.timeout"        # P0: timeout arbitre

    # System
    SYSTEM_HEALTH: str = "cleman.system.health"
    SYSTEM_ERROR: str = "cleman.system.error"
    SYSTEM_AUDIT: str = "cleman.system.audit"

    # Compliance
    COMPLIANCE_CHECK: str = "cleman.compliance.check"
    COMPLIANCE_REPORT: str = "cleman.compliance.report"

    @classmethod
    def for_client(cls, client_id: str) -> str:
        """Prefix subject with client namespace for isolation"""
        return f"cleman.client.{client_id}"

    @classmethod
    def for_vertical(cls, vertical: str) -> str:
        """Prefix subject with vertical namespace"""
        return f"cleman.vertical.{vertical}"


subjects = Subjects()
