"""
Cortex Leman v5 — Tests de l'Orchestrateur et du Routeur
"""
import pytest

from core.orchestrator.intention import IntentionStore
from core.orchestrator.router import AgentRouter


class TestIntentionStore:
    """Tests du store d'intentions"""

    def test_create_intention(self):
        import uuid
        store = IntentionStore(persist_path=f"/tmp/test-intentions-create-{uuid.uuid4().hex[:8]}.json")
        intent = store.create(
            client_id="client-001",
            vertical="comptable",
            query="Analyser le bilan fiscal 2025",
        )
        assert intent.intention_id is not None
        assert intent.version == 1
        assert intent.status == "active"
        assert intent.original_query == "Analyser le bilan fiscal 2025"

    def test_revise_intention(self):
        import uuid
        store = IntentionStore(persist_path=f"/tmp/test-intentions-revise-{uuid.uuid4().hex[:8]}.json")
        intent = store.create(
            client_id="client-001", vertical="comptable",
            query="Analyser bilan",
        )
        revised = store.revise(
            intent.intention_id,
            refined_query="Analyser le bilan fiscal complet 2025 avec comparaison",
        )
        assert revised.version == 2
        assert "comparaison" in revised.refined_query

    def test_freeze_unfreeze(self):
        import uuid
        store = IntentionStore(persist_path=f"/tmp/test-intentions-freeze-{uuid.uuid4().hex[:8]}.json")
        intent = store.create(
            client_id="client-001", vertical="comptable",
            query="Test",
        )
        frozen = store.freeze(intent.intention_id)
        assert frozen.status == "frozen"

        unfrozen = store.unfreeze(intent.intention_id)
        assert unfrozen.status == "active"

    def test_get_active_for_client(self):
        import uuid
        store = IntentionStore(persist_path=f"/tmp/test-intentions-active-{uuid.uuid4().hex[:8]}.json")
        store.create(client_id="c1", vertical="comptable", query="q1")
        store.create(client_id="c1", vertical="avocat", query="q2")
        store.create(client_id="c2", vertical="comptable", query="q3")

        active_c1 = store.get_active_for_client("c1")
        assert len(active_c1) == 2


class TestAgentRouter:
    """Tests du routeur d'agents"""

    def test_data_query_routing(self):
        router = AgentRouter()
        from core.journal.models import IntentionModel
        intent = IntentionModel(
            intention_id="test",
            client_id="c1",
            vertical="comptable",
            original_query="Cherche les données du dernier bilan",
        )
        routing = router.route(intent)
        assert routing["data"] is True

    def test_reasoning_routing(self):
        router = AgentRouter()
        from core.journal.models import IntentionModel
        intent = IntentionModel(
            intention_id="test",
            client_id="c1",
            vertical="comptable",
            original_query="Compare les options et recommande la meilleure",
        )
        routing = router.route(intent)
        assert routing["reasoning"] is True

    def test_action_routing(self):
        router = AgentRouter()
        from core.journal.models import IntentionModel
        intent = IntentionModel(
            intention_id="test",
            client_id="c1",
            vertical="comptable",
            original_query="Déclenche le workflow de clôture annuelle",
        )
        routing = router.route(intent)
        assert routing["action"] is True

    def test_default_routing(self):
        router = AgentRouter()
        from core.journal.models import IntentionModel
        intent = IntentionModel(
            intention_id="test",
            client_id="c1",
            vertical="comptable",
            original_query="Bonjour",  # Pas de pattern spécifique
        )
        routing = router.route(intent)
        assert routing["data"] is True  # Par défaut
        assert routing["reasoning"] is True  # Par défaut

    def test_mediator_always_active(self):
        router = AgentRouter()
        from core.journal.models import IntentionModel
        intent = IntentionModel(
            intention_id="test",
            client_id="c1",
            vertical="comptable",
            original_query="Test",
        )
        routing = router.route(intent)
        assert routing["mediator"] is True
        assert routing["supervisor"] is True
