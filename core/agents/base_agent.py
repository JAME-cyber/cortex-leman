"""
Cortex Leman v5 — Agent de Base

Classe abstraite pour tous les agents du graphe.
Chaque agent: souscrit au bus, publie ses résultats, gère le cycle de vie.
"""
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from core.bus.nats_client import bus
from core.bus.subjects import subjects
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType
from core.security.circuit_breaker import circuit_registry

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Agent de base Cortex Leman v5.
    
    Cycle de vie:
    1. start() → connexion bus + abonnement sujets
    2. process() → traitement métier (à implémenter)
    3. publish_result() → publication du résultat
    """

    def __init__(self, name: str, subscribe_subjects: list[str] = None):
        self.name = name
        self.agent_id = f"{name}-{uuid.uuid4().hex[:8]}"
        self._subscribe_subjects = subscribe_subjects or []
        self._running = False

    async def start(self) -> None:
        """Démarrer l'agent"""
        for subject in self._subscribe_subjects:
            await bus.subscribe(
                subject,
                self._handle_message,
                queue=f"agent-{self.name}",
            )

        self._running = True
        logger.info(f"Agent [{self.name}] démarré ({self.agent_id})")

    async def stop(self) -> None:
        """Arrêter l'agent"""
        self._running = False
        logger.info(f"Agent [{self.name}] arrêté")

    async def _handle_message(self, data: dict, meta: dict) -> None:
        """
        Handler principal avec circuit breaker et gestion d'erreurs.
        """
        cb = circuit_registry.get(self.name)
        if not cb.allow_request():
            logger.warning(f"Agent [{self.name}] bloqué par circuit breaker")
            return

        intention_id = data.get("intention_id", "unknown")
        client_id = data.get("client_id", "unknown")
        vertical = data.get("vertical", "unknown")

        try:
            result = await self.process(data, meta)
            cb.record_success()

            if result:
                await self._publish_result(
                    intention_id=intention_id,
                    client_id=client_id,
                    vertical=vertical,
                    result=result,
                )

        except Exception as e:
            cb.record_failure()
            logger.error(f"Agent [{self.name}] erreur: {e}")

            journal.append(
                event_type=JournalEventType.AGENT_ERROR,
                client_id=client_id,
                vertical=vertical,
                agent_source=self.name,
                intention_id=intention_id,
                payload={"error": str(e), "agent": self.name},
            )

    @abstractmethod
    async def process(self, data: dict, meta: dict) -> dict:
        """Traitement métier — à implémenter par chaque agent"""
        pass

    async def _publish_result(
        self,
        intention_id: str,
        client_id: str,
        vertical: str,
        result: dict,
    ) -> None:
        """Publier un résultat sur le bus"""
        await bus.publish(subjects.AGENT_RESULT, {
            "intention_id": intention_id,
            "client_id": client_id,
            "vertical": vertical,
            "agent_source": self.name,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
