"""
Tests — LiteLLM Provider + Model Router

Valide le routing par verticale, le fallback, et l'intégration LiteLLM.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os


# ============================================================
# Model Router
# ============================================================

class TestModelRouter:
    """Tests du routeur de modèles par verticale"""

    def test_default_model_when_no_routing(self):
        """Sans routing configuré, utiliser le modèle par défaut"""
        from core.agents.reflection import ReflectionNode  # just to check imports work
        from core.integrations.llm.provider import ModelRouter
        from core.config import settings

        router = ModelRouter()
        model_id, label = router.resolve_model("unknown_vertical")
        # Doit contenir le provider par défaut
        assert settings.llm_provider in model_id or "openrouter" in model_id

    def test_vertical_routing_comptable(self):
        """Verticale comptable doit router vers le modèle configuré"""
        from core.integrations.llm.provider import ModelRouter
        router = ModelRouter()
        model_id, label = router.resolve_model("comptable")
        # Doit contenir claude (configuré pour comptable)
        assert "claude" in model_id.lower() or "anthropic" in model_id.lower()

    def test_vertical_routing_avocat(self):
        """Verticale avocat doit router vers le modèle configuré"""
        from core.integrations.llm.provider import ModelRouter
        router = ModelRouter()
        model_id, label = router.resolve_model("avocat")
        assert "claude" in model_id.lower() or "anthropic" in model_id.lower()

    def test_vertical_routing_startup(self):
        """Verticale startup doit router vers mistral (économique)"""
        from core.integrations.llm.provider import ModelRouter
        router = ModelRouter()
        model_id, label = router.resolve_model("startup")
        assert "mistral" in model_id.lower()

    def test_vertical_routing_sante(self):
        """Verticale santé doit router vers le modèle configuré"""
        from core.integrations.llm.provider import ModelRouter
        router = ModelRouter()
        model_id, label = router.resolve_model("sante")
        assert "gpt" in model_id.lower() or "openai" in model_id.lower()

    def test_high_protection_forces_ollama(self):
        """Mode Haute Protection doit forcer Ollama"""
        from core.integrations.llm.provider import ModelRouter
        with patch("core.integrations.llm.provider.settings") as mock_settings:
            mock_settings.app_mode = "haute_protection"
            mock_settings.llm_high_protection_model = "llama3.1:8b"
            mock_settings.llm_vertical_routing = {}
            mock_settings.llm_model = "mistralai/mistral-small-3.1-24b-instruct"
            mock_settings.llm_provider = "ollama"
            router = ModelRouter()
            router._is_high_protection = True
            router._high_protection_model = "llama3.1:8b"
            model_id, label = router.resolve_model("comptable")
            assert "ollama" in model_id

    def test_force_local_overrides_routing(self):
        """force_local=True doit forcer Ollama même en mode Standard"""
        from core.integrations.llm.provider import ModelRouter
        router = ModelRouter()
        router._high_protection_model = "llama3.1:8b"
        model_id, label = router.resolve_model("comptable", force_local=True)
        assert "ollama" in model_id

    def test_get_routing_table(self):
        """La table de routing doit lister toutes les verticales"""
        from core.integrations.llm.provider import ModelRouter
        router = ModelRouter()
        table = router.get_routing_table()
        assert isinstance(table, dict)
        # Au moins les 6 verticales
        assert len(table) >= 6
        for vertical in ["comptable", "avocat", "sante", "banque", "startup", "rh"]:
            assert vertical in table
            assert "model" in table[vertical]
            assert "full_id" in table[vertical]


# ============================================================
# LLM Service
# ============================================================

class TestLLMService:
    """Tests du service LLM unifié"""

    def test_singleton_exists(self):
        """Le singleton llm_service doit exister"""
        from core.integrations.llm import llm_service
        assert llm_service is not None

    def test_stats_initial(self):
        """Les stats initiales doivent être à 0"""
        from core.integrations.llm.provider import LLMService
        service = LLMService()
        stats = service.get_stats()
        assert stats["total_calls"] == 0
        assert stats["total_tokens"] == 0

    def test_get_routing_table(self):
        """Le service doit exposer la table de routing"""
        from core.integrations.llm.provider import LLMService
        service = LLMService()
        table = service.get_routing_table()
        assert "mode" in table
        assert "default_model" in table
        assert "vertical_routing" in table
        assert "default_provider" in table

    def test_is_local_standard_mode(self):
        """Mode Standard: is_local doit être False"""
        from core.integrations.llm.provider import LLMService
        service = LLMService()
        # En mode standard par défaut
        assert service.is_local is False

    def test_provider_name(self):
        """Le provider name doit correspondre aux settings"""
        from core.integrations.llm.provider import LLMService
        service = LLMService()
        assert service.provider_name == "openrouter"

    @pytest.mark.asyncio
    async def test_generate_with_model_override(self):
        """Un model_override doit être respecté"""
        from core.integrations.llm.provider import LLMService
        service = LLMService()

        # Mock LiteLLM
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage.total_tokens = 50
        mock_response.model = "test-model"

        with patch("core.integrations.llm.provider.litellm") as mock_litellm:
            mock_litellm.acompletion = AsyncMock(return_value=mock_response)
            result = await service.generate(
                system_prompt="test",
                user_prompt="hello",
                model_override="ollama/llama3.1:8b",
            )
            assert result["text"] == "Test response"
            # Vérifier que le modèle override a été utilisé
            call_kwargs = mock_litellm.acompletion.call_args[1]
            assert "ollama/llama3.1:8b" in call_kwargs["model"]

    @pytest.mark.asyncio
    async def test_generate_handles_auth_error(self):
        """Erreur d'auth doit retourner error, pas crash"""
        from core.integrations.llm.provider import LLMService
        import litellm

        service = LLMService()

        with patch("core.integrations.llm.provider.litellm") as mock_litellm:
            mock_litellm.acompletion = AsyncMock(
                side_effect=litellm.AuthenticationError(
                    message="Invalid API key",
                    model="test",
                    llm_provider="openrouter",
                )
            )
            mock_litellm.AuthenticationError = litellm.AuthenticationError
            result = await service.generate(
                system_prompt="test",
                user_prompt="hello",
            )
            assert result.get("error", "").startswith("auth_error")

    @pytest.mark.asyncio
    async def test_generate_handles_timeout(self):
        """Timeout doit retourner error, pas crash"""
        from core.integrations.llm.provider import LLMService
        import litellm

        service = LLMService()

        mock_acompletion = AsyncMock(
            side_effect=litellm.Timeout(
                message="Request timed out",
                model="test",
                llm_provider="openrouter",
            )
        )

        with patch("core.integrations.llm.provider.litellm.acompletion", mock_acompletion):
            result = await service.generate(
                system_prompt="test",
                user_prompt="hello",
            )
            assert result.get("error") == "timeout"

    @pytest.mark.asyncio
    async def test_fallback_on_model_not_found(self):
        """Model not found doit déclencher le fallback"""
        from core.integrations.llm.provider import LLMService
        import litellm

        service = LLMService()

        # Mock: premier appel → not found, deuxième appel (fallback) → success
        mock_response_ok = MagicMock()
        mock_response_ok.choices = [MagicMock()]
        mock_response_ok.choices[0].message.content = "Fallback response"
        mock_response_ok.usage.total_tokens = 30
        mock_response_ok.model = "fallback-model"

        mock_acompletion = AsyncMock(
            side_effect=[
                litellm.NotFoundError(
                    message="Model not found",
                    model="bad-model",
                    llm_provider="openrouter",
                ),
                mock_response_ok,
            ]
        )

        with patch("core.integrations.llm.provider.litellm.acompletion", mock_acompletion):
            result = await service.generate(
                system_prompt="test",
                user_prompt="hello",
            )
            assert result["text"] == "Fallback response"
            assert result.get("fallback") is True


# ============================================================
# Config
# ============================================================

class TestLLMConfig:
    """Tests de la configuration LLM"""

    def test_config_has_vertical_routing(self):
        from core.config import settings
        assert hasattr(settings, "llm_vertical_routing")
        routing = settings.llm_vertical_routing
        assert isinstance(routing, dict)
        assert len(routing) >= 6

    def test_config_has_high_protection_model(self):
        from core.config import settings
        assert hasattr(settings, "llm_high_protection_model")
        assert settings.llm_high_protection_model == "llama3.1:8b"

    def test_config_reflection(self):
        from core.config import settings
        assert hasattr(settings, "reflection_enabled")
        assert settings.reflection_enabled is True

    def test_all_verticals_have_routing(self):
        from core.config import settings
        for v in ["comptable", "avocat", "sante", "banque", "startup", "rh"]:
            assert v in settings.llm_vertical_routing, f"Missing routing for {v}"
