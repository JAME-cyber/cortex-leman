"""
Cortex Leman v5 — Agent Superviseur (Observateur Continu)

V2: Observateur continu du graphe de confiance.
- Écoute TOUS les résultats d'agents en temps réel (pas seulement terminal)
- Maintient un tableau de bord de santé par intention
- Peut alerter l'orchestrateur et le médiateur
- Journalise chaque observation pour audit trail
- L'humain est arbitre, pas valideur — le superviseur prépare les dossiers d'arbitrage
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from core.agents.base_agent import BaseAgent
from core.bus.subjects import subjects
from core.bus.nats_client import bus
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)


class IntentionHealth:
    """Tableau de bord santé d'une intention — suivi en temps réel"""

    def __init__(self, intention_id: str):
        self.intention_id = intention_id
        self.created_at = datetime.now(timezone.utc)
        self.agent_results: dict[str, dict] = {}       # agent_name → dernier résultat
        self.check_runs: int = 0
        self.conflicts_detected: int = 0
        self.frozen_count: int = 0
        self.overall_confidence: float = 1.0
        self.last_activity: datetime = datetime.now(timezone.utc)
        self.completed: bool = False

    def update_agent_result(self, agent_name: str, result: dict) -> None:
        """Enregistrer un résultat d'agent"""
        self.agent_results[agent_name] = {
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "confidence": result.get("confidence", 0.5),
        }
        self.last_activity = datetime.now(timezone.utc)
        self._recalculate_confidence()

    def mark_check(self) -> None:
        self.check_runs += 1

    def mark_conflict(self) -> None:
        self.conflicts_detected += 1

    def mark_frozen(self) -> None:
        self.frozen_count += 1

    def _recalculate_confidence(self) -> None:
        """Recalculer la confiance globale à partir des résultats agents"""
        if not self.agent_results:
            self.overall_confidence = 1.0
            return
        confidences = [
            v["confidence"] for v in self.agent_results.values()
            if isinstance(v.get("confidence"), (int, float))
        ]
        self.overall_confidence = (
            sum(confidences) / len(confidences) if confidences else 0.5
        )

    @property
    def is_degraded(self) -> bool:
        """L'intention est dégradée si confiance < 0.5 ou conflits ≥ 2"""
        return self.overall_confidence < 0.5 or self.conflicts_detected >= 2

    @property
    def stale_seconds(self) -> float:
        """Secondes depuis la dernière activité"""
        return (datetime.now(timezone.utc) - self.last_activity).total_seconds()

    def to_dict(self) -> dict:
        return {
            "intention_id": self.intention_id,
            "overall_confidence": round(self.overall_confidence, 2),
            "agents_reported": list(self.agent_results.keys()),
            "check_runs": self.check_runs,
            "conflicts_detected": self.conflicts_detected,
            "frozen_count": self.frozen_count,
            "is_degraded": self.is_degraded,
            "stale_seconds": self.stale_seconds,
            "completed": self.completed,
        }


class SupervisorAgent(BaseAgent):
    """
    Agent Superviseur V2 — Observateur Continu du Graphe de Confiance.

    Différences V1 → V2:
    - V1: valideur terminal (reçoit VALIDATE_REQUEST en fin de chaîne)
    - V2: observateur permanent (écoute AGENT_RESULT + MEDIATOR_CONFLICT + ARBITRATION_DECISION)

    Rôle: préparer les dossiers d'arbitrage, détecter les dégradations,
    alerter l'orchestrateur, journaliser chaque observation.
    """

    def __init__(self):
        super().__init__(
            name="supervisor",
            subscribe_subjects=[subjects.VALIDATE_REQUEST],
        )
        self._health_board: dict[str, IntentionHealth] = {}
        self._max_health_entries = 5_000  # Limite mémoire

    async def start(self) -> None:
        """Démarrage avec abonnements étendus"""
        await super().start()

        # Abonnements continus — le superviseur voit TOUT
        await bus.subscribe(subjects.AGENT_RESULT, self._on_any_agent_result)
        await bus.subscribe(subjects.MEDIATOR_CONFLICT, self._on_conflict)
        await bus.subscribe(subjects.MEDIATOR_FREEZE, self._on_freeze)
        await bus.subscribe(subjects.ARBITRATION_DECISION, self._on_arbitration_done)

        logger.info("Superviseur V2: observateur continu démarré")

    # === Observateurs continus ===

    async def _on_any_agent_result(self, data: dict, meta: dict) -> None:
        """Chaque résultat d'agent est observé en temps réel"""
        intention_id = data.get("intention_id")
        agent_source = data.get("agent_source", "unknown")
        result = data.get("result", {})

        if not intention_id:
            return

        # Maintenir le tableau de bord
        health = self._get_or_create_health(intention_id)
        health.update_agent_result(agent_source, result)

        # Journaliser l'observation
        journal.append(
            event_type=JournalEventType.AGENT_RESULT,
            client_id=data.get("client_id", "unknown"),
            vertical=data.get("vertical", "unknown"),
            agent_source="supervisor",
            intention_id=intention_id,
            payload={
                "observed_agent": agent_source,
                "confidence": result.get("confidence", 0.5),
                "overall_health": health.to_dict(),
            },
        )

        # Si dégradé, alerter
        if health.is_degraded:
            logger.warning(
                f"Superviseur: intention {intention_id[:8]}... DÉGRADÉE "
                f"(confiance={health.overall_confidence:.2f}, "
                f"conflits={health.conflicts_detected})"
            )
            await bus.publish("cleman.supervisor.alert", {
                "intention_id": intention_id,
                "alert_type": "degraded",
                "health": health.to_dict(),
            })

    async def _on_conflict(self, data: dict, meta: dict) -> None:
        """Conflit Médiateur → comptabiliser"""
        intention_id = data.get("intention_id")
        if intention_id:
            health = self._get_or_create_health(intention_id)
            health.mark_conflict()

    async def _on_freeze(self, data: dict, meta: dict) -> None:
        """Gel Médiateur → comptabiliser"""
        intention_id = data.get("intention_id")
        if intention_id:
            health = self._get_or_create_health(intention_id)
            health.mark_frozen()

    async def _on_arbitration_done(self, data: dict, meta: dict) -> None:
        """Arbitrage résolu → journaliser la résolution"""
        intention_id = data.get("intention_id")
        if intention_id:
            journal.append(
                event_type=JournalEventType.ARBITRATION_DECISION,
                client_id=data.get("client_id", "unknown"),
                vertical=data.get("vertical", "unknown"),
                agent_source="supervisor",
                intention_id=intention_id,
                payload={
                    "conflict_id": data.get("conflict_id"),
                    "decision": data.get("decision"),
                    "arbiter": data.get("arbiter_name"),
                },
            )

    # === Validation (rétrocompatible V1) ===

    async def process(self, data: dict, meta: dict) -> dict:
        """Validation d'un résultat d'agent (legacy + enrichi)"""
        intention_id = data.get("intention_id", "unknown")
        agent_source = data.get("agent_source", "unknown")
        result = data.get("result", {})

        logger.info(
            f"Superviseur: validation résultat de {agent_source} "
            f"pour intention {intention_id[:8]}..."
        )

        # Vérification enrichie avec contexte du health board
        health = self._health_board.get(intention_id)

        state_check = self._verify_state(result)
        hallucination_check = self._check_hallucination(result)
        coherence_check = self._check_coherence(result)
        context_check = self._check_context(health)

        all_checks = [state_check, hallucination_check, coherence_check, context_check]
        all_passed = all(c.get("passed", False) for c in all_checks)

        if not all_passed:
            failed_checks = [c for c in all_checks if not c.get("passed")]
            return {
                "recommendation": "requires_human_review",
                "confidence": 0.3,
                "checks": {
                    "state": state_check,
                    "hallucination": hallucination_check,
                    "coherence": coherence_check,
                    "context": context_check,
                },
                "issues": [c.get("issue", "") for c in failed_checks],
                "risks": ["validation_failed"],
                "health_snapshot": health.to_dict() if health else None,
            }

        return {
            "recommendation": "approved",
            "confidence": 0.9,
            "checks": {
                "state": state_check,
                "hallucination": hallucination_check,
                "coherence": coherence_check,
                "context": context_check,
            },
            "health_snapshot": health.to_dict() if health else None,
        }

    # === Vérifications ===

    def _verify_state(self, result: dict) -> dict:
        if not result:
            return {"passed": False, "issue": "Résultat vide"}
        if not isinstance(result, dict):
            return {"passed": False, "issue": "Résultat non structuré"}
        return {"passed": True}

    def _check_hallucination(self, result: dict) -> dict:
        confidence = result.get("confidence", 0)
        if confidence < 0.3:
            return {
                "passed": False,
                "issue": f"Confiance trop basse: {confidence}",
            }
        return {"passed": True, "confidence": confidence}

    def _check_coherence(self, result: dict) -> dict:
        recommendation = result.get("recommendation")
        if not recommendation:
            return {"passed": False, "issue": "Pas de recommandation"}
        return {"passed": True, "recommendation": recommendation}

    def _check_context(self, health: Optional[IntentionHealth]) -> dict:
        """Vérification contextuelle enrichie — nouveauté V2"""
        if not health:
            return {"passed": True, "note": "Pas de contexte health board"}
        if health.conflicts_detected >= 3:
            return {
                "passed": False,
                "issue": f"Trop de conflits: {health.conflicts_detected}",
            }
        if health.stale_seconds > 300:
            return {
                "passed": False,
                "issue": f"Intention inactive depuis {int(health.stale_seconds)}s",
            }
        return {"passed": True}

    # === Helpers ===

    def _get_or_create_health(self, intention_id: str) -> IntentionHealth:
        if intention_id not in self._health_board:
            self._health_board[intention_id] = IntentionHealth(intention_id)

            # Purger les intentions complétées/stales si trop nombreuses
            if len(self._health_board) > self._max_health_entries:
                stale = [
                    iid for iid, h in self._health_board.items()
                    if h.completed or h.stale_seconds > 3600
                ]
                for iid in stale[:len(stale) // 2]:
                    del self._health_board[iid]
                if stale:
                    logger.debug(f"Superviseur: purge {len(stale)} entrées stales")

        return self._health_board[intention_id]

    def get_health_board(self) -> dict:
        """Retourner l'état complet du tableau de bord"""
        return {
            iid: health.to_dict()
            for iid, health in self._health_board.items()
        }

    def get_intention_health(self, intention_id: str) -> Optional[dict]:
        """Retourner la santé d'une intention spécifique"""
        health = self._health_board.get(intention_id)
        return health.to_dict() if health else None
