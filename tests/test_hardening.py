"""
Cortex Leman v5 — Tests Hardening

Tests des améliorations sécurité:
- Refresh token hashé
- Rate limiter
- IntentionStore persistance
- CORS restrictif
- GuardrailPipeline singleton
"""
import os
import sys
import json
import pytest
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ["DATABASE_URL"] = "sqlite:///file::memory:?cache=shared&uri=true"
os.environ["SECRET_KEY"] = "test-hardening-key"
os.environ["JOURNAL_PATH"] = "/tmp/cortex-test-journal-hardening"


# ============================================================
# Tests Refresh Token Hash
# ============================================================

class TestRefreshTokenHash:
    """Tests du hash des refresh tokens"""

    def test_hash_token_deterministic(self):
        from core.security.auth import hash_token
        h1 = hash_token("my-refresh-token")
        h2 = hash_token("my-refresh-token")
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_hash_token_different_inputs(self):
        from core.security.auth import hash_token
        h1 = hash_token("token-1")
        h2 = hash_token("token-2")
        assert h1 != h2

    def test_hash_token_not_plain(self):
        from core.security.auth import hash_token
        token = "sensitive-refresh-token"
        hashed = hash_token(token)
        assert hashed != token
        assert token not in hashed


# ============================================================
# Tests Rate Limiter
# ============================================================

class TestRateLimiter:
    """Tests du rate limiter in-memory"""

    def test_allows_under_limit(self):
        from api.dependencies import RateLimiter
        rl = RateLimiter(max_requests=3, window_seconds=10)
        assert rl.is_allowed("ip1") is True
        assert rl.is_allowed("ip1") is True
        assert rl.is_allowed("ip1") is True

    def test_blocks_over_limit(self):
        from api.dependencies import RateLimiter
        rl = RateLimiter(max_requests=2, window_seconds=10)
        rl.is_allowed("ip1")
        rl.is_allowed("ip1")
        assert rl.is_allowed("ip1") is False

    def test_different_keys_independent(self):
        from api.dependencies import RateLimiter
        rl = RateLimiter(max_requests=1, window_seconds=10)
        assert rl.is_allowed("ip1") is True
        assert rl.is_allowed("ip2") is True  # différent = OK

    def test_reset_clears_counter(self):
        from api.dependencies import RateLimiter
        rl = RateLimiter(max_requests=1, window_seconds=10)
        rl.is_allowed("ip1")
        rl.reset("ip1")
        assert rl.is_allowed("ip1") is True

    def test_window_expiry(self):
        from api.dependencies import RateLimiter
        rl = RateLimiter(max_requests=1, window_seconds=0)  # window=0 → expire immédiatement
        rl.is_allowed("ip1")
        time.sleep(0.01)
        assert rl.is_allowed("ip1") is True  # window expirée


# ============================================================
# Tests IntentionStore Persistance
# ============================================================

class TestIntentionStorePersistence:
    """Tests de la persistance fichier de l'IntentionStore"""

    def test_create_and_persist(self):
        from core.orchestrator.intention import IntentionStore
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "intentions.json")
            store = IntentionStore(persist_path=path)

            intention = store.create(
                client_id="client-1",
                vertical="comptable",
                query="Test query",
                context={"key": "value"},
            )

            assert intention.intention_id
            assert intention.client_id == "client-1"

            # Vérifier la persistance fichier
            data = json.loads(open(path).read())
            assert intention.intention_id in data
            assert data[intention.intention_id]["client_id"] == "client-1"

    def test_load_from_file(self):
        from core.orchestrator.intention import IntentionStore
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "intentions.json")

            # Créer et persister
            store1 = IntentionStore(persist_path=path)
            intention = store1.create(
                client_id="client-1", vertical="comptable", query="Test"
            )
            iid = intention.intention_id

            # Recharger depuis le fichier
            store2 = IntentionStore(persist_path=path)
            loaded = store2.get(iid)
            assert loaded is not None
            assert loaded.client_id == "client-1"
            assert loaded.vertical == "comptable"

    def test_freeze_persists(self):
        from core.orchestrator.intention import IntentionStore
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "intentions.json")
            store = IntentionStore(persist_path=path)
            intention = store.create(
                client_id="client-1", vertical="avocat", query="Test"
            )
            iid = intention.intention_id

            store.freeze(iid)

            # Recharger
            store2 = IntentionStore(persist_path=path)
            loaded = store2.get(iid)
            assert loaded.status == "frozen"

    def test_get_active_for_client(self):
        from core.orchestrator.intention import IntentionStore
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "intentions.json")
            store = IntentionStore(persist_path=path)

            store.create(client_id="c1", vertical="comptable", query="Q1")
            store.create(client_id="c1", vertical="avocat", query="Q2")
            store.create(client_id="c2", vertical="sante", query="Q3")

            active = store.get_active_for_client("c1")
            assert len(active) == 2

            active_c2 = store.get_active_for_client("c2")
            assert len(active_c2) == 1


# ============================================================
# Tests GuardrailPipeline Singleton
# ============================================================

class TestGuardrailSingleton:
    """Tests que le guardrail est réutilisé (pas recréé à chaque appel)"""

    def test_llm_service_guardrail_lazy_init(self):
        from core.integrations.llm.provider import LLMService
        service = LLMService()
        assert service._guardrail is None

        guard = service._get_guardrail()
        assert guard is not None

        # Deuxième appel → même instance
        guard2 = service._get_guardrail()
        assert guard is guard2


# ============================================================
# Tests CORS Configuration
# ============================================================

class TestCORSConfig:
    """Tests de la configuration CORS"""

    def test_cors_origins_from_settings(self):
        from core.config import settings
        origins = settings.api_cors_origins.split(",")
        assert len(origins) >= 1
        assert "http://localhost:3000" in origins


# ============================================================
# Tests Metrics Protection
# ============================================================

class TestMetricsProtection:
    """Tests que le endpoint /metrics nécessite admin"""

    def test_metrics_requires_auth(self):
        """Le endpoint /metrics doit être protégé (test structurel)"""
        # Vérifier que le handler a une dépendance auth
        from api.main import app
        from fastapi.routing import APIRoute

        metrics_route = None
        for route in app.routes:
            if isinstance(route, APIRoute) and route.path == "/metrics":
                metrics_route = route
                break

        assert metrics_route is not None, "/metrics route non trouvée"
        # Vérifier qu'il y a au moins une dépendance (auth)
        assert len(metrics_route.dependant.dependencies) > 0, (
            "/metrics doit avoir au moins une dépendance d'authentification"
        )


# ============================================================
# Tests Vault Pagination
# ============================================================

class TestVaultPagination:
    """Tests de la pagination du vault"""

    def test_list_documents_default_limit(self):
        from core.integrations.knowledge_vault.vault import KnowledgeVault
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = KnowledgeVault(vault_path=tmpdir)
            vault.create_client_space("client-1", "comptable")

            # Créer quelques documents
            for i in range(5):
                vault.store_document("client-1", f"doc-{i}", f"content {i}")

            docs = vault.list_documents("client-1")
            assert len(docs) == 5

    def test_list_documents_with_offset(self):
        from core.integrations.knowledge_vault.vault import KnowledgeVault
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = KnowledgeVault(vault_path=tmpdir)
            vault.create_client_space("client-1", "comptable")

            for i in range(5):
                vault.store_document("client-1", f"doc-{i}", f"content {i}")

            page1 = vault.list_documents("client-1", limit=2, offset=0)
            page2 = vault.list_documents("client-1", limit=2, offset=2)

            assert len(page1) == 2
            assert len(page2) == 2
            # Pages différentes
            page1_ids = {d["doc_id"] for d in page1}
            page2_ids = {d["doc_id"] for d in page2}
            assert page1_ids.isdisjoint(page2_ids)
