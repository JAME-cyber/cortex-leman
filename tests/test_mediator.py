"""
Cortex Leman v5 — Tests du Médiateur et du moteur de règles
"""
import pytest
import json
from pathlib import Path

from core.mediator.rules_engine import RulesEngine, RuleResult


@pytest.fixture
def rules_engine(tmp_path):
    """Moteur de règles avec répertoire temporaire"""
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    # Créer un fichier de règles de test
    test_rules = {
        "vertical": "test",
        "description": "Règles de test",
        "rules": [
            {
                "id": "test-001",
                "name": "Test block rule",
                "severity": "critical",
                "condition": {"==": [{"var": "action.type"}, "forbidden"]},
                "action": "block",
                "message": "Action interdite",
            },
            {
                "id": "test-002",
                "name": "Test freeze rule",
                "severity": "high",
                "condition": {">=": [{"var": "payload.montant"}, 10000]},
                "action": "freeze",
                "message": "Montant élevé détecté",
            },
            {
                "id": "test-003",
                "name": "Test warn rule",
                "severity": "medium",
                "condition": {"!": [{"var": "user_consent"}]},
                "action": "warn",
                "message": "Consentement manquant",
            },
        ],
    }
    with open(rules_dir / "test.json", "w") as f:
        json.dump(test_rules, f)

    engine = RulesEngine(rules_dir=str(rules_dir))
    engine.load_rules()
    return engine


class TestRulesEngine:
    """Tests du moteur de règles JsonLogic"""

    def test_load_rules(self, rules_engine):
        assert "test" in rules_engine.get_all_verticals()
        assert len(rules_engine.get_rules_for_vertical("test")) == 3

    def test_block_rule_triggered(self, rules_engine):
        results = rules_engine.evaluate("test", {
            "action": {"type": "forbidden"},
            "payload": {"montant": 0},
            "user_consent": True,
        })
        triggered = [r for r in results if r.triggered]
        assert len(triggered) == 1
        assert triggered[0].action == "block"
        assert triggered[0].severity == "critical"

    def test_freeze_rule_triggered(self, rules_engine):
        results = rules_engine.evaluate("test", {
            "payload": {"montant": 15000},
        })
        triggered = [r for r in results if r.triggered]
        assert any(r.action == "freeze" for r in triggered)

    def test_warn_rule_triggered(self, rules_engine):
        results = rules_engine.evaluate("test", {
            "user_consent": False,
        })
        triggered = [r for r in results if r.triggered]
        assert any(r.action == "warn" for r in triggered)

    def test_no_rules_triggered(self, rules_engine):
        results = rules_engine.evaluate("test", {
            "action": {"type": "normal"},
            "payload": {"montant": 100},
            "user_consent": True,
        })
        triggered = [r for r in results if r.triggered]
        assert len(triggered) == 0

    def test_evaluate_critical(self, rules_engine):
        criticals = rules_engine.evaluate_critical("test", {
            "action": {"type": "forbidden"},
        })
        assert len(criticals) == 1
        assert criticals[0].severity == "critical"

    def test_unknown_vertical(self, rules_engine):
        results = rules_engine.evaluate("unknown_vertical", {})
        assert len(results) == 0


class TestConflictDetection:
    """Tests de la logique de détection de conflits"""

    def test_divergent_recommendations(self):
        """Deux agents avec recommandations divergentes"""
        from core.mediator.mediator import AgentMediator

        m = AgentMediator()
        conflict = m._compare_positions(
            "data", {"recommendation": "proceed", "confidence": 0.9},
            "reasoning", {"recommendation": "reject", "confidence": 0.8},
        )
        assert conflict is not None
        assert "Divergence" in conflict

    def test_confidence_gap_conflict(self):
        """Écart de confiance important"""
        from core.mediator.mediator import AgentMediator

        m = AgentMediator()
        conflict = m._compare_positions(
            "data", {"recommendation": "proceed", "confidence": 0.9},
            "reasoning", {"recommendation": "proceed", "confidence": 0.1},
        )
        assert conflict is not None
        assert "confiance" in conflict.lower()

    def test_no_conflict(self):
        """Agents en accord"""
        from core.mediator.mediator import AgentMediator

        m = AgentMediator()
        conflict = m._compare_positions(
            "data", {"recommendation": "proceed", "confidence": 0.8},
            "reasoning", {"recommendation": "proceed", "confidence": 0.75},
        )
        assert conflict is None
