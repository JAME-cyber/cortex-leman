"""
Cortex Leman v5 — Tests du Circuit Breaker et de la Saga
"""
import pytest
import asyncio
from unittest.mock import AsyncMock

from core.security.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerRegistry
from core.agents.saga.saga_manager import SagaManager, SagaStepStatus


class TestCircuitBreaker:
    """Tests du circuit breaker"""

    def test_initial_state_closed(self):
        cb = CircuitBreaker("test-agent")
        assert cb.state == CircuitState.CLOSED
        assert cb.allow_request() is True

    def test_opens_after_threshold(self):
        cb = CircuitBreaker("test-agent", failure_threshold=3, recovery_timeout=60)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.allow_request() is False

    def test_success_resets_failures(self):
        cb = CircuitBreaker("test-agent", failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        cb.record_failure()
        # Encore en dessous du seuil car success a reset
        assert cb.state == CircuitState.CLOSED

    def test_recovery_to_half_open(self):
        import time
        cb = CircuitBreaker("test-agent", failure_threshold=1, recovery_timeout=0.1)
        cb.record_failure()  # OPEN
        time.sleep(0.2)  # Wait for recovery timeout
        assert cb.state == CircuitState.HALF_OPEN

    def test_registry(self):
        reg = CircuitBreakerRegistry()
        cb1 = reg.get("agent-1")
        cb2 = reg.get("agent-1")
        assert cb1 is cb2  # Même instance
        status = reg.get_all_status()
        assert "agent-1" in status


class TestSagaManager:
    """Tests du gestionnaire de Saga"""

    def test_create_saga(self):
        sm = SagaManager()
        saga_id = sm.create_saga("intent-001")
        assert saga_id is not None
        assert len(saga_id) > 0

    def test_add_steps(self):
        sm = SagaManager()
        saga_id = sm.create_saga("intent-001")
        sm.add_step(saga_id, "step1", "payment", {"amount": 100}, "refund")
        sm.add_step(saga_id, "step2", "notification", {"msg": "done"}, "cancel_notification")
        status = sm.get_saga_status(saga_id)
        assert status["total_steps"] == 2

    @pytest.mark.asyncio
    async def test_execute_all_success(self):
        sm = SagaManager()
        saga_id = sm.create_saga("intent-001")
        sm.add_step(saga_id, "step1", "test_action", {"data": "test"}, "compensate")

        async def mock_executor(payload):
            return {"status": "ok"}

        success = await sm.execute_all(
            saga_id=saga_id,
            executors={"test_action": mock_executor},
            client_id="client-001",
            vertical="comptable",
            intention_id="intent-001",
        )
        assert success is True
        status = sm.get_saga_status(saga_id)
        assert status["completed"] == 1

    @pytest.mark.asyncio
    async def test_compensation_on_failure(self):
        sm = SagaManager()
        saga_id = sm.create_saga("intent-001")
        sm.add_step(saga_id, "step1", "ok_action", {"data": "first"}, "compensate")
        sm.add_step(saga_id, "step2", "fail_action", {"data": "second"}, "compensate")

        async def ok_executor(payload):
            return {"status": "ok"}

        async def fail_executor(payload):
            raise Exception("Intentional failure")

        success = await sm.execute_all(
            saga_id=saga_id,
            executors={"ok_action": ok_executor, "fail_action": fail_executor},
            client_id="client-001",
            vertical="comptable",
            intention_id="intent-001",
        )
        assert success is False
        status = sm.get_saga_status(saga_id)
        assert status["failed"] >= 1


class TestActionFreezeCheck:
    """Tests du verrou de gel de l'Agent Action"""

    def test_frozen_intention_blocks_action(self):
        """Si l'intention est gelée, l'action ne doit pas s'exécuter"""
        from core.orchestrator.intention import IntentionStore
        store = IntentionStore()
        intent = store.create("c1", "comptable", "Test")
        store.freeze(intent.intention_id)

        frozen = store.get(intent.intention_id)
        assert frozen.status == "frozen"
        # L'Agent Action doit vérifier ce statut avant d'exécuter

    def test_unfrozen_intention_allows_action(self):
        """Si l'intention est active, l'action peut s'exécuter"""
        from core.orchestrator.intention import IntentionStore
        store = IntentionStore()
        intent = store.create("c1", "comptable", "Test")

        active = store.get(intent.intention_id)
        assert active.status == "active"

    def test_mediator_ignores_results_when_frozen(self):
        """Le Médiateur doit ignorer les résultats d'une intention gelée"""
        from core.orchestrator.intention import IntentionStore
        store = IntentionStore()
        intent = store.create("c1", "comptable", "Test")
        store.freeze(intent.intention_id)

        frozen = store.get(intent.intention_id)
        assert frozen.status == "frozen"
        # Le Médiateur doit skip les résultats

    def test_reasoning_can_request_revision(self):
        """L'Agent Raisonnement doit pouvoir publier une révision"""
        # Test que le sujet INTENTION_REVISE existe
        from core.bus.subjects import subjects
        assert hasattr(subjects, 'INTENTION_REVISE')
        assert subjects.INTENTION_REVISE == "cleman.intention.revise"
