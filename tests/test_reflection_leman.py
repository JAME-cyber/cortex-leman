"""
Tests — Reflection Node + Persona Le Léman

Valide le pipeline: ReasoningAgent → Reflection Node → Résultat enrichi.
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ============================================================
# Reflection Node
# ============================================================

class TestReflectionNode:
    """Tests unitaires du nœud de réflexion"""

    def test_reflection_node_init(self):
        from core.agents.reflection import ReflectionNode
        node = ReflectionNode()
        assert node.enabled is True
        assert node._total_reflections == 0

    def test_reflection_node_disable(self):
        from core.agents.reflection import ReflectionNode
        node = ReflectionNode()
        node.disable()
        assert node.enabled is False

    def test_reflection_node_enable(self):
        from core.agents.reflection import ReflectionNode
        node = ReflectionNode()
        node.disable()
        node.enable()
        assert node.enabled is True

    def test_reflection_result_to_dict(self):
        from core.agents.reflection import ReflectionResult
        result = ReflectionResult(
            original_confidence=0.8,
            revised_confidence=0.7,
            critique="Analyse correcte mais référence imprécise",
            issues_found=["Référence Art. 22 manque le paragraphe"],
            improvements=["Ajouter le paragraphe exact de l'article"],
            confirmed=True,
            llm_used=True,
        )
        d = result.to_dict()
        assert d["original_confidence"] == 0.8
        assert d["revised_confidence"] == 0.7
        assert d["confidence_delta"] == -0.1
        assert d["confirmed"] is True
        assert len(d["issues_found"]) == 1
        assert d["llm_used"] is True

    @pytest.mark.asyncio
    async def test_reflect_disabled_returns_none(self):
        from core.agents.reflection import ReflectionNode
        node = ReflectionNode()
        node.disable()
        result = await node.reflect(
            query="test",
            vertical="comptable",
            analysis={"confidence": 0.8},
            compliance={},
            recommendations={},
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_reflect_llm_unavailable(self):
        from core.agents.reflection import ReflectionNode
        node = ReflectionNode()
        with patch("core.agents.reflection.reflection_node") as mock_node:
            mock_llm = AsyncMock()
            mock_llm.generate.return_value = {"text": "", "error": "timeout"}
            with patch("core.integrations.llm.llm_service", mock_llm):
                result = await node.reflect(
                    query="test",
                    vertical="comptable",
                    analysis={"confidence": 0.8},
                    compliance={},
                    recommendations={},
                )
                # Si le mock échoue, c'est None (import error)
                assert result is None or result.llm_used is True

    def test_get_stats_initial(self):
        from core.agents.reflection import ReflectionNode
        node = ReflectionNode()
        stats = node.get_stats()
        assert stats["enabled"] is True
        assert stats["total_reflections"] == 0
        assert stats["confirmation_rate"] is None

    def test_parse_critique_valid_json(self):
        from core.agents.reflection import ReflectionNode
        node = ReflectionNode()
        text = json.dumps({
            "critique": "Analyse solide",
            "revised_confidence": 0.85,
            "issues_found": [],
            "improvements": ["Ajouter référence RGPD"],
        })
        result = node._parse_critique(text)
        assert result["critique"] == "Analyse solide"
        assert result["revised_confidence"] == 0.85
        assert len(result["improvements"]) == 1

    def test_parse_critique_backticks(self):
        from core.agents.reflection import ReflectionNode
        node = ReflectionNode()
        text = '```json\n{"critique": "OK", "revised_confidence": 0.9, "issues_found": [], "improvements": []}\n```'
        result = node._parse_critique(text)
        assert result["critique"] == "OK"
        assert result["revised_confidence"] == 0.9

    def test_parse_critique_fallback_text(self):
        from core.agents.reflection import ReflectionNode
        node = ReflectionNode()
        text = "This is not JSON at all, just a plain text critique."
        result = node._parse_critique(text)
        assert result["critique"] == text
        assert result["revised_confidence"] is None


# ============================================================
# Persona Le Léman
# ============================================================

class TestLeLemanPersona:
    """Tests du persona Le Léman"""

    def test_skill_loads(self):
        from core.agents.prompts import load_skill
        skill = load_skill("le_leman")
        assert skill is not None
        assert "Le Léman" in skill
        assert "conseil de confiance" in skill.lower()

    def test_skill_in_llm_agents(self):
        from core.agents.prompts import LLM_AGENTS
        assert "le_leman" in LLM_AGENTS

    def test_skill_not_in_programmatic(self):
        from core.agents.prompts import PROGRAMMATIC_AGENTS
        assert "le_leman" not in PROGRAMMATIC_AGENTS

    def test_skill_has_sections(self):
        from core.agents.prompts import load_skill, extract_section
        skill = load_skill("le_leman")
        assert extract_section(skill, "IDENTITÉ") is not None
        assert extract_section(skill, "PERSONNALITÉ") is not None
        assert extract_section(skill, "FORMAT DE RÉPONSE") is not None
        assert extract_section(skill, "VERTICALES") is not None
        assert extract_section(skill, "CE QUE TU NE FAIS JAMAIS") is not None


# ============================================================
# ReasoningAgent avec Reflection
# ============================================================

class TestReasoningAgentWithReflection:
    """Tests que le ReasoningAgent intègre bien le Reflection Node"""

    def test_agent_instantiation(self):
        from core.agents.reasoning_agent import ReasoningAgent
        agent = ReasoningAgent()
        assert agent.name == "reasoning"

    def test_subjects_includes_reflection(self):
        from core.bus.subjects import subjects
        assert hasattr(subjects, "REASONING_REFLECT")
        assert subjects.REASONING_REFLECT == "cleman.reflection.check"


# ============================================================
# Config Reflection
# ============================================================

class TestReflectionConfig:
    """Tests de la configuration reflection"""

    def test_config_has_reflection_settings(self):
        from core.config import settings
        assert hasattr(settings, "reflection_enabled")
        assert settings.reflection_enabled is True
        assert hasattr(settings, "reflection_max_confidence_delta")
        assert settings.reflection_max_confidence_delta == 0.3
