"""
Cortex Leman v5 — Orchestrateur Conversationnel

Hub permanent, événementiel, conversationnel.
Maintient les intentions, route vers les agents, gère les boucles feedback.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from core.bus.nats_client import bus
from core.bus.subjects import subjects
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType
from core.orchestrator.intention import intention_store
from core.orchestrator.router import router

logger = logging.getLogger(__name__)


class ConversationnalOrchestrator:
    """
    Orchestrateur conversationnel Cortex Leman v5.
    
    - Reçoit les événements via le bus NATS
    - Maintient les intentions versionnées
    - Route dynamiquement vers les agents
    - Gère les boucles feedback
    - Ne force PAS un chemin séquentiel
    """

    def __init__(self):
        self._running = False
        self._active_conversations: dict[str, dict] = {}

    async def start(self) -> None:
        """Démarrer l'orchestrateur et s'abonner au bus"""
        await bus.connect()

        # Abonnements aux événements
        await bus.subscribe(subjects.INTENTION_NEW, self._on_new_intention)
        await bus.subscribe(subjects.INTENTION_REVISE, self._on_revise_intention)
        await bus.subscribe(subjects.AGENT_RESULT, self._on_agent_result)
        await bus.subscribe(subjects.MEDIATOR_CONFLICT, self._on_mediator_conflict)
        await bus.subscribe(subjects.ARBITRATION_DECISION, self._on_arbitration_decision)
        await bus.subscribe(subjects.VALIDATE_RESULT, self._on_validation_result)

        # Journal: démarrage système
        journal.append(
            event_type=JournalEventType.SYSTEM_START,
            client_id="system",
            vertical="system",
            agent_source="orchestrator",
            intention_id="system",
            payload={"version": "5.0.0", "mode": "conversationnel"},
        )

        self._running = True
        logger.info("Orchestrateur conversationnel démarré")

    async def stop(self) -> None:
        """Arrêt propre"""
        self._running = False
        await bus.close()
        logger.info("Orchestrateur arrêté")

    # === Handlers d'événements ===

    async def _on_new_intention(self, data: dict, meta: dict) -> None:
        """Nouvelle intention reçue → créer, router, dispatcher"""
        client_id = data.get("client_id", "unknown")
        vertical = data.get("vertical", "comptable")
        query = data.get("query", "")
        context = data.get("context", {})

        # 1. Créer l'intention
        intention = intention_store.create(
            client_id=client_id,
            vertical=vertical,
            query=query,
            context=context,
        )

        # 2. Journaliser
        journal.append(
            event_type=JournalEventType.INTENTION_CREATED,
            client_id=client_id,
            vertical=vertical,
            agent_source="orchestrator",
            intention_id=intention.intention_id,
            payload={
                "query": query,
                "version": 1,
            },
        )

        # 3. Router vers les agents
        routing = router.route(intention)

        # 4. Mettre à jour les agents assignés
        assigned = [k for k, v in routing.items() if v]
        intention_store.revise(intention.intention_id, assigned_agents=assigned)

        # 5. Dispatcher en parallèle vers chaque agent
        if routing.get("data"):
            await bus.publish(subjects.DATA_QUERY, {
                "intention_id": intention.intention_id,
                "client_id": client_id,
                "vertical": vertical,
                "query": intention.refined_query,
                "context": intention.context,
            })

        if routing.get("reasoning"):
            await bus.publish(subjects.REASONING_ANALYZE, {
                "intention_id": intention.intention_id,
                "client_id": client_id,
                "vertical": vertical,
                "query": intention.refined_query,
                "context": intention.context,
            })

        if routing.get("action"):
            await bus.publish(subjects.ACTION_EXECUTE, {
                "intention_id": intention.intention_id,
                "client_id": client_id,
                "vertical": vertical,
                "query": intention.refined_query,
                "context": intention.context,
            })

        # 6. Envoyer au Médiateur pour vérification continue
        await bus.publish(subjects.MEDIATOR_CHECK, {
            "intention_id": intention.intention_id,
            "client_id": client_id,
            "vertical": vertical,
            "routing": routing,
        })

        logger.info(
            f"Intention {intention.intention_id[:8]} créée → "
            f"agents: {assigned}"
        )

    async def _on_revise_intention(self, data: dict, meta: dict) -> None:
        """Révision d'intention (reformulation, précision, bifurcation)"""
        intention_id = data.get("intention_id")
        refined_query = data.get("refined_query")
        context_update = data.get("context_update", {})

        intention = intention_store.revise(
            intention_id=intention_id,
            refined_query=refined_query,
            context_update=context_update,
        )

        journal.append(
            event_type=JournalEventType.INTENTION_REVISED,
            client_id=intention.client_id,
            vertical=intention.vertical,
            agent_source="orchestrator",
            intention_id=intention_id,
            payload={"version": intention.version, "refined_query": refined_query},
        )

        # Re-router avec la nouvelle intention
        routing = router.route(intention)
        await bus.publish(subjects.MEDIATOR_CHECK, {
            "intention_id": intention_id,
            "client_id": intention.client_id,
            "vertical": intention.vertical,
            "routing": routing,
        })

    async def _on_agent_result(self, data: dict, meta: dict) -> None:
        """Résultat d'un agent → journaliser + transmettre au Médiateur"""
        intention_id = data.get("intention_id")
        agent_source = data.get("agent_source", "unknown")

        journal.append(
            event_type=JournalEventType.AGENT_RESULT,
            client_id=data.get("client_id", "unknown"),
            vertical=data.get("vertical", "unknown"),
            agent_source=agent_source,
            intention_id=intention_id,
            payload=data.get("result", {}),
        )

        # Transmettre au Médiateur pour validation continue
        await bus.publish(subjects.MEDIATOR_CHECK, {
            "intention_id": intention_id,
            "agent_source": agent_source,
            "result": data.get("result", {}),
            "client_id": data.get("client_id"),
            "vertical": data.get("vertical"),
        })

        # Transmettre au Superviseur
        await bus.publish(subjects.VALIDATE_REQUEST, {
            "intention_id": intention_id,
            "agent_source": agent_source,
            "result": data.get("result", {}),
        })

    async def _on_mediator_conflict(self, data: dict, meta: dict) -> None:
        """Conflit détecté par le Médiateur → geler + demander arbitrage"""
        intention_id = data.get("intention_id")
        conflict_id = data.get("conflict_id")

        # Geler l'intention
        intention_store.freeze(intention_id)

        journal.append(
            event_type=JournalEventType.MEDIATOR_FREEZE,
            client_id=data.get("client_id", "unknown"),
            vertical=data.get("vertical", "unknown"),
            agent_source="mediator",
            intention_id=intention_id,
            payload={
                "conflict_id": conflict_id,
                "reason": data.get("reason"),
                "positions": data.get("positions"),
            },
        )

        # Demander arbitrage humain
        await bus.publish(subjects.ARBITRATION_REQUEST, {
            "intention_id": intention_id,
            "conflict_id": conflict_id,
            "positions": data.get("positions", {}),
            "reason": data.get("reason", ""),
            "severity": data.get("severity", "medium"),
        })

        logger.warning(
            f"INTENTION GELÉE {intention_id[:8]}... conflit={conflict_id[:8]}..."
        )

    async def _on_arbitration_decision(self, data: dict, meta: dict) -> None:
        """Décision d'arbitrage → dégeler + reprendre le flux"""
        intention_id = data.get("intention_id")
        conflict_id = data.get("conflict_id")
        decision = data.get("decision")

        # Dégeler
        intention_store.unfreeze(intention_id)

        journal.append(
            event_type=JournalEventType.ARBITRATION_DECISION,
            client_id=data.get("client_id", "unknown"),
            vertical=data.get("vertical", "unknown"),
            agent_source="arbitration",
            intention_id=intention_id,
            payload={
                "conflict_id": conflict_id,
                "arbiter": data.get("arbiter_name"),
                "decision": decision,
                "justification": data.get("justification"),
                "selected_position": data.get("selected_position"),
            },
        )

        # Re-dispatcher vers les agents avec la décision
        await bus.publish(subjects.INTENTION_REVISE, {
            "intention_id": intention_id,
            "context_update": {
                "arbitration": {
                    "conflict_id": conflict_id,
                    "decision": decision,
                    "selected_position": data.get("selected_position"),
                }
            },
        })

        logger.info(
            f"Arbitrage résolu {intention_id[:8]}... → {decision}"
        )

    async def _on_validation_result(self, data: dict, meta: dict) -> None:
        """Résultat de validation finale"""
        intention_id = data.get("intention_id")
        status = data.get("status")

        if status == "approved":
            intention_store.complete(intention_id)
            journal.append(
                event_type=JournalEventType.INTENTION_CANCELLED,
                client_id=data.get("client_id", "unknown"),
                vertical=data.get("vertical", "unknown"),
                agent_source="supervisor",
                intention_id=intention_id,
                payload={"final_status": "completed"},
            )

    # === API publique ===

    async def submit_intention(
        self,
        client_id: str,
        vertical: str,
        query: str,
        context: dict = None,
    ) -> str:
        """Soumettre une nouvelle intention (point d'entrée principal)"""
        await bus.publish(subjects.INTENTION_NEW, {
            "client_id": client_id,
            "vertical": vertical,
            "query": query,
            "context": context or {},
        })
        # L'intention sera créée par le handler async
        # Pour simplifier, on retourne l'ID via le store
        active = intention_store.get_active_for_client(client_id)
        if active:
            return active[-1].intention_id
        return ""

    async def get_status(self) -> dict:
        """Statut de l'orchestrateur"""
        return {
            "running": self._running,
            "bus_connected": bus.connected,
            "journal_sequence": journal.sequence,
            "journal_last_hash": journal.last_hash[:16] + "...",
        }


# Singleton
orchestrator = ConversationnalOrchestrator()
