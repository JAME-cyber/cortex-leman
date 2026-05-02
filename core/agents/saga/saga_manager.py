"""
Cortex Leman v5 — Pattern Saga pour l'Agent Action

Chaque opération externe est enregistrée comme étape de saga.
En cas d'invalidation, une séquence de compensation est déclenchée.
"""
import uuid
import logging
from enum import Enum
from typing import Callable, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field

from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType
from core.config import settings

logger = logging.getLogger(__name__)


class SagaStepStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"


@dataclass
class SagaStep:
    """Étape individuelle d'une saga"""
    step_id: str
    name: str
    action_type: str
    payload: dict = field(default_factory=dict)
    status: SagaStepStatus = SagaStepStatus.PENDING
    result: Optional[dict] = None
    compensation_fn: Optional[str] = None
    compensation_payload: dict = field(default_factory=dict)
    executed_at: Optional[datetime] = None
    compensated_at: Optional[datetime] = None


class SagaManager:
    """
    Gestionnaire de Saga pour l'Agent Action.
    
    Flux:
    1. Enregistrer les étapes avant exécution
    2. Exécuter séquentiellement
    3. Si échec → compenser les étapes réussies en ordre inverse
    """

    def __init__(self):
        self._active_sagas: dict[str, list[SagaStep]] = {}

    def create_saga(self, intention_id: str) -> str:
        """Créer une nouvelle saga"""
        saga_id = str(uuid.uuid4())
        self._active_sagas[saga_id] = []
        logger.info(f"Saga créée: {saga_id[:8]}... pour intention {intention_id[:8]}...")
        return saga_id

    def add_step(
        self,
        saga_id: str,
        name: str,
        action_type: str,
        payload: dict,
        compensation_fn: str,
        compensation_payload: dict = None,
    ) -> str:
        """Ajouter une étape à la saga"""
        step_id = str(uuid.uuid4())
        step = SagaStep(
            step_id=step_id,
            name=name,
            action_type=action_type,
            payload=payload,
            compensation_fn=compensation_fn,
            compensation_payload=compensation_payload or {},
        )
        self._active_sagas[saga_id].append(step)
        return step_id

    async def execute_step(
        self,
        saga_id: str,
        step_index: int,
        executor: Callable,
        client_id: str,
        vertical: str,
        intention_id: str,
    ) -> bool:
        """Exécuter une étape de la saga"""
        steps = self._active_sagas.get(saga_id, [])
        if step_index >= len(steps):
            return False

        step = steps[step_index]

        if not await self._allow_execution(step):
            logger.warning(f"Saga {saga_id[:8]}... étape {step.name} bloquée par circuit breaker")
            step.status = SagaStepStatus.FAILED
            return False

        try:
            result = await executor(step.payload)
            step.status = SagaStepStatus.COMPLETED
            step.result = result
            step.executed_at = datetime.now(timezone.utc)

            journal.append(
                event_type=JournalEventType.ACTION_EXECUTED,
                client_id=client_id,
                vertical=vertical,
                agent_source="action",
                intention_id=intention_id,
                payload={
                    "saga_id": saga_id,
                    "step_id": step.step_id,
                    "step_name": step.name,
                    "action_type": step.action_type,
                    "status": "completed",
                },
            )
            return True

        except Exception as e:
            step.status = SagaStepStatus.FAILED
            logger.error(f"Saga {saga_id[:8]}... étape {step.name} ÉCHOUÉE: {e}")

            # Déclencher la compensation
            await self.compensate(saga_id, step_index, client_id, vertical, intention_id)
            return False

    async def execute_all(
        self,
        saga_id: str,
        executors: dict[str, Callable],
        client_id: str,
        vertical: str,
        intention_id: str,
    ) -> bool:
        """Exécuter toutes les étapes de la saga séquentiellement"""
        steps = self._active_sagas.get(saga_id, [])

        for i, step in enumerate(steps):
            executor = executors.get(step.action_type)
            if not executor:
                logger.error(f"Pas d'exécuteur pour {step.action_type}")
                await self.compensate(saga_id, i, client_id, vertical, intention_id)
                return False

            success = await self.execute_step(
                saga_id, i, executor, client_id, vertical, intention_id
            )
            if not success:
                return False

        logger.info(f"Saga {saga_id[:8]}... terminée avec succès ({len(steps)} étapes)")
        return True

    async def compensate(
        self,
        saga_id: str,
        failed_at: int,
        client_id: str = "unknown",
        vertical: str = "unknown",
        intention_id: str = "unknown",
    ) -> None:
        """
        Compenser les étapes réussies en ordre inverse.
        Commence par l'étape juste avant celle qui a échoué.
        """
        steps = self._active_sagas.get(saga_id, [])
        logger.warning(
            f"COMPENSATION Saga {saga_id[:8]}... "
            f"de l'étape {failed_at - 1} à 0"
        )

        journal.append(
            event_type=JournalEventType.ACTION_COMPENSATED,
            client_id=client_id,
            vertical=vertical,
            agent_source="action",
            intention_id=intention_id,
            payload={
                "saga_id": saga_id,
                "failed_at_step": failed_at,
                "compensating_steps": [s.name for s in steps[:failed_at]],
            },
        )

        for i in range(failed_at - 1, -1, -1):
            step = steps[i]
            if step.status != SagaStepStatus.COMPLETED:
                continue

            step.status = SagaStepStatus.COMPENSATING
            try:
                # La compensation est enregistrée mais exécutée par le handler
                logger.info(
                    f"Compensation: {step.name} "
                    f"(fn={step.compensation_fn})"
                )
                step.status = SagaStepStatus.COMPENSATED
                step.compensated_at = datetime.now(timezone.utc)

            except Exception as e:
                logger.error(
                    f"ERREUR CRITIQUE: Compensation {step.name} échouée: {e}. "
                    f"INTERVENTION MANUELLE REQUISE."
                )
                step.status = SagaStepStatus.FAILED

    async def _allow_execution(self, step: SagaStep) -> bool:
        """Vérifier les circuit breakers avant exécution"""
        from core.security.circuit_breaker import circuit_registry
        cb = circuit_registry.get(step.action_type)
        return cb.allow_request()

    def get_saga_status(self, saga_id: str) -> dict:
        """Statut d'une saga"""
        steps = self._active_sagas.get(saga_id, [])
        return {
            "saga_id": saga_id,
            "total_steps": len(steps),
            "completed": sum(1 for s in steps if s.status == SagaStepStatus.COMPLETED),
            "failed": sum(1 for s in steps if s.status == SagaStepStatus.FAILED),
            "compensated": sum(1 for s in steps if s.status == SagaStepStatus.COMPENSATED),
            "steps": [
                {
                    "name": s.name,
                    "status": s.status.value,
                    "action_type": s.action_type,
                }
                for s in steps
            ],
        }


# Singleton
saga_manager = SagaManager()
