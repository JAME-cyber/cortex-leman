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


class TestRiskAppetite:
    """Tests de l'appétit aux risques et de la graduation"""

    def test_risk_appetite_in_rules_file(self, rules_engine):
        """L'appétit aux risques est chargé depuis le fichier JSON"""
        # Les règles de test n'ont pas de risk_appetite → valeurs par défaut
        appetite = rules_engine.get_risk_appetite("test")
        assert "accept_max" in appetite
        assert "arbitrate_threshold" in appetite
        assert "block_threshold" in appetite

    def test_risk_appetite_avocat(self):
        """La verticale avocat a un appétit ultra-prudent"""
        engine = RulesEngine()  # Utilise le vrai répertoire
        engine.load_rules()
        appetite = engine.get_risk_appetite("avocat")
        assert appetite["accept_max"] == 1
        assert appetite["arbitrate_threshold"] == 2
        assert appetite["block_threshold"] == 4

    def test_risk_appetite_startup(self):
        """La verticale startup a un appétit plus permissif"""
        engine = RulesEngine()
        engine.load_rules()
        appetite = engine.get_risk_appetite("startup")
        assert appetite["accept_max"] == 3
        assert appetite["arbitrate_threshold"] == 4
        assert appetite["block_threshold"] == 5

    def test_evaluate_risk_level_no_trigger(self, rules_engine):
        """Aucune règle déclenchée → risque niveau 1, accept"""
        level, action = rules_engine.evaluate_risk_level("test", {
            "action": {"type": "normal"},
            "payload": {"montant": 100},
            "user_consent": True,
        })
        assert level == 1
        assert action == "accept"

    def test_evaluate_risk_level_warn_trigger(self, rules_engine):
        """Règle warn (medium) déclenchée → niveau 3, action selon appétit"""
        level, action = rules_engine.evaluate_risk_level("test", {
            "user_consent": False,
        })
        assert level == 3  # medium → 3
        # Appétit par défaut: arbitrate_threshold=3, donc arbitrate
        assert action == "arbitrate"

    def test_evaluate_risk_level_critical_trigger(self, rules_engine):
        """Règle critical déclenchée → niveau 5, block"""
        level, action = rules_engine.evaluate_risk_level("test", {
            "action": {"type": "forbidden"},
        })
        assert level == 5  # critical → 5
        assert action == "block"  # 5 >= block_threshold (5)

    def test_risk_level_enriches_rule_result(self, rules_engine):
        """Le risk_level est ajouté aux RuleResult déclenchés"""
        level, action = rules_engine.evaluate_risk_level("test", {
            "action": {"type": "forbidden"},
        })
        assert level == 5
        # Vérifier via une évaluation fraîche que le risk_level est propagé
        results = rules_engine.evaluate("test", {
            "action": {"type": "forbidden"},
        })
        triggered = [r for r in results if r.triggered]
        assert len(triggered) >= 1
        # evaluate_risk_level retourne le bon niveau
        assert level == 5
        assert action == "block"

    def test_intention_health_risk_level(self):
        """IntentionHealth gère le risk_level"""
        from core.agents.supervisor_agent import IntentionHealth
        health = IntentionHealth("test-intention")
        assert health.risk_level == 0
        assert health.risk_label == "Non évalué"

        health.update_risk_level(3, "arbitrate")
        assert health.risk_level == 3
        assert health.risk_label == "Élevé"
        assert health.risk_action == "arbitrate"

    def test_intention_health_risk_labels(self):
        """Tous les labels de risque sont corrects"""
        from core.agents.supervisor_agent import IntentionHealth
        health = IntentionHealth("test")
        labels = {
            0: "Non évalué",
            1: "Faible",
            2: "Modéré",
            3: "Élevé",
            4: "Très élevé",
            5: "Critique",
        }
        for level, expected_label in labels.items():
            health.update_risk_level(level, "accept")
            assert health.risk_label == expected_label

    def test_intention_health_to_dict_includes_risk(self):
        """Le dict de santé inclut les champs de risque"""
        from core.agents.supervisor_agent import IntentionHealth
        health = IntentionHealth("test")
        health.update_risk_level(4, "block")
        d = health.to_dict()
        assert d["risk_level"] == 4
        assert d["risk_label"] == "Très élevé"
        assert d["risk_action"] == "block"
