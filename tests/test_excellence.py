"""
Tests — Excellence by Design: validation, erreurs, isolation, edge cases.
"""
import pytest
from datetime import datetime, timezone


# ============================================================
# 1. Hiérarchie d'erreurs
# ============================================================

class TestErrors:

    def test_invalid_vertical_error(self):
        from core.observability.errors import InvalidVerticalError

        err = InvalidVerticalError("pizza")
        assert "pizza" in str(err)
        assert err.vertical == "pizza"
        d = err.to_dict()
        assert d["error_type"] == "InvalidVerticalError"
        assert "allowed" in d["details"]

    def test_empty_input_error(self):
        from core.observability.errors import EmptyInputError

        err = EmptyInputError("input_text")
        assert "input_text" in str(err)
        assert err.details["field"] == "input_text"

    def test_invalid_score_error(self):
        from core.observability.errors import InvalidScoreError

        err = InvalidScoreError(1.5)
        assert "1.5" in str(err)

    def test_skill_not_found_error(self):
        from core.observability.errors import SkillNotFoundError

        err = SkillNotFoundError("fake-id")
        assert "fake-id" in str(err)

    def test_rubric_not_found_error(self):
        from core.observability.errors import RubricNotFoundError

        err = RubricNotFoundError("r1", "comptable")
        assert "r1" in str(err)
        assert "comptable" in str(err)

    def test_case_not_found_error(self):
        from core.observability.errors import CaseNotFoundError

        err = CaseNotFoundError("c1")
        assert "c1" in str(err)

    def test_duplicate_case_error(self):
        from core.observability.errors import DuplicateCaseError

        err = DuplicateCaseError("abc123", "existing-1")
        assert "abc123" in str(err)
        assert "existing-1" in str(err)

    def test_backtest_insufficient_data_error(self):
        from core.observability.errors import BacktestInsufficientDataError

        err = BacktestInsufficientDataError(3, 50)
        assert "3" in str(err)
        assert "50" in str(err)

    def test_error_hierarchy(self):
        from core.observability.errors import (
            CortexObservabilityError, ValidationError,
            InvalidVerticalError, EmptyInputError,
        )

        assert issubclass(InvalidVerticalError, ValidationError)
        assert issubclass(ValidationError, CortexObservabilityError)
        assert issubclass(EmptyInputError, ValidationError)

    def test_all_errors_serializable(self):
        from core.observability.errors import (
            CortexObservabilityError, SkillNotFoundError,
            RubricNotFoundError, CaseNotFoundError, DuplicateCaseError,
            BacktestInsufficientDataError, EvalExecutionError,
        )
        import json

        errors = [
            CortexObservabilityError("test", module="test"),
            SkillNotFoundError("s1"),
            RubricNotFoundError("r1", "v1"),
            CaseNotFoundError("c1"),
            DuplicateCaseError("h1", "e1"),
            BacktestInsufficientDataError(5, 50),
            EvalExecutionError("r1", "OOM"),
        ]
        for err in errors:
            d = err.to_dict()
            json_str = json.dumps(d)
            assert "error_type" in json_str


# ============================================================
# 2. Validation helpers
# ============================================================

class TestValidation:

    def test_validate_vertical_ok(self):
        from core.observability.context import validate_vertical

        assert validate_vertical("comptable") == "comptable"
        assert validate_vertical("AVOCAT") == "avocat"
        assert validate_vertical(" Banque ") == "banque"

    def test_validate_vertical_rejects(self):
        from core.observability.context import validate_vertical
        from core.observability.errors import InvalidVerticalError

        with pytest.raises(InvalidVerticalError):
            validate_vertical("pizza")

        with pytest.raises(InvalidVerticalError):
            validate_vertical("")

    def test_validate_non_empty_ok(self):
        from core.observability.context import validate_non_empty

        assert validate_non_empty("hello") == "hello"
        assert validate_non_empty("  hello  ") == "hello"

    def test_validate_non_empty_rejects(self):
        from core.observability.context import validate_non_empty
        from core.observability.errors import EmptyInputError

        with pytest.raises(EmptyInputError):
            validate_non_empty("")

        with pytest.raises(EmptyInputError):
            validate_non_empty("   ")

        with pytest.raises(EmptyInputError):
            validate_non_empty(None)

    def test_validate_score_ok(self):
        from core.observability.context import validate_score

        assert validate_score(0.0) == 0.0
        assert validate_score(1.0) == 1.0
        assert validate_score(0.5) == 0.5

    def test_validate_score_rejects(self):
        from core.observability.context import validate_score
        from core.observability.errors import InvalidScoreError

        with pytest.raises(InvalidScoreError):
            validate_score(-0.1)

        with pytest.raises(InvalidScoreError):
            validate_score(1.5)

        with pytest.raises(InvalidScoreError):
            validate_score("bad")


# ============================================================
# 3. ObservabilityContext isolation
# ============================================================

class TestContext:

    def test_context_creates_fresh(self):
        from core.observability.context import ObservabilityContext

        ctx = ObservabilityContext()
        assert ctx.auto_approver is not None
        assert ctx.skill_registry is not None
        assert ctx.eval_router is not None

    def test_context_seeded(self):
        from core.observability.context import ObservabilityContext

        ctx = ObservabilityContext(seed=True)
        assert len(ctx.skill_registry.get_all_skills()) >= 6
        assert len(ctx.eval_router.get_rubrics("comptable")) > 0

    def test_context_isolation(self):
        from core.observability.context import ObservabilityContext

        ctx1 = ObservabilityContext(seed=True)
        ctx2 = ObservabilityContext(seed=True)

        # Modify ctx1
        ctx1.auto_approver.evaluate(
            type('R', (), {
                'request_id': 't', 'vertical': 'comptable',
                'operation_type': 'data_query', 'confidence': 0.95,
                'client_id': '', 'intention_id': '',
                'agent_source': '', 'context': {}, 'amount': None,
            })()
        )

        # ctx2 should be unaffected
        assert ctx2.auto_approver.get_stats()["total_evaluations"] == 0

    def test_context_reset(self):
        from core.observability.context import ObservabilityContext
        from core.observability.auto_approver import ApprovalRequest

        ctx = ObservabilityContext(seed=True)
        ctx.auto_approver.evaluate(ApprovalRequest(
            vertical="comptable", operation_type="data_query", confidence=0.95,
        ))
        assert ctx.auto_approver.get_stats()["total_evaluations"] == 1

        ctx.reset_all()
        assert ctx.auto_approver.get_stats()["total_evaluations"] == 0

    def test_context_default_singleton(self):
        from core.observability.context import get_context

        ctx1 = get_context()
        ctx2 = get_context()
        assert ctx1 is ctx2  # Même instance


# ============================================================
# 4. Input guards on public methods
# ============================================================

class TestInputGuards:

    def test_auto_approver_rejects_empty_vertical(self):
        from core.observability.auto_approver import AutoApprover, ApprovalRequest
        from core.observability.errors import EmptyInputError

        approver = AutoApprover()
        with pytest.raises(EmptyInputError):
            approver.evaluate(ApprovalRequest(
                vertical="", operation_type="data_query", confidence=0.9,
            ))

    def test_auto_approver_rejects_none_request(self):
        from core.observability.auto_approver import AutoApprover

        approver = AutoApprover()
        with pytest.raises(ValueError):
            approver.evaluate(None)

    def test_skill_invoke_rejects_empty_problem(self):
        from core.observability.compliance_skill import ComplianceSkill
        from core.observability.errors import EmptyInputError

        skill = ComplianceSkill(skill_id="test")
        with pytest.raises(EmptyInputError):
            skill.invoke("")

    def test_skill_invoke_rejects_whitespace_problem(self):
        from core.observability.compliance_skill import ComplianceSkill
        from core.observability.errors import EmptyInputError

        skill = ComplianceSkill(skill_id="test")
        with pytest.raises(EmptyInputError):
            skill.invoke("   ")


# ============================================================
# 5. Edge cases — robustesse
# ============================================================

class TestEdgeCases:

    def test_skill_matching_empty_patterns(self):
        from core.observability.compliance_skill import ComplianceSkill

        skill = ComplianceSkill(trigger_patterns=[])
        assert skill.matches_problem("anything") == 0.0

    def test_skill_matching_empty_problem(self):
        from core.observability.compliance_skill import ComplianceSkill

        skill = ComplianceSkill(trigger_patterns=["test"])
        assert skill.matches_problem("") == 0.0

    def test_golden_case_round_trip_preserves_label(self):
        from core.observability.golden_dataset import GoldenCase, CaseLabel, CaseOrigin

        original = GoldenCase(
            case_id="rt-1",
            vertical="banque",
            input_text="Test KYC",
            output_text="Résponse KYC",
            expected_label=CaseLabel.WARN,
            origin=CaseOrigin.RED_TEAM,
            justification="Test round-trip",
        )
        d = original.to_dict()
        restored = GoldenCase.from_dict(d)

        assert restored.case_id == "rt-1"
        assert restored.expected_label == CaseLabel.WARN
        assert restored.origin == CaseOrigin.RED_TEAM

    def test_auto_approver_with_none_amount(self):
        """Montant None ne doit pas crasher"""
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision

        approver = AutoApprover()
        result = approver.evaluate(ApprovalRequest(
            request_id="test",
            vertical="comptable",
            operation_type="data_query",
            confidence=0.95,
            amount=None,
        ))
        assert result.decision == ApprovalDecision.AUTO_APPROVED

    def test_auto_approver_with_negative_amount(self):
        """Montant négatif ne doit pas crasher"""
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision

        approver = AutoApprover()
        result = approver.evaluate(ApprovalRequest(
            request_id="test",
            vertical="comptable",
            operation_type="data_query",
            confidence=0.95,
            amount=-100,
        ))
        assert result.decision == ApprovalDecision.AUTO_APPROVED

    def test_session_miner_with_garbage_entries(self):
        """Le miner doit résister aux entrées malformées"""
        from core.observability.session_miner import SessionMiner

        entries = [
            {},  # Empty
            {"event_type": "garbage"},
            {"event_type": "agent.result", "payload": "not_a_dict"},
            None,  # Null
        ]
        miner = SessionMiner()
        # Should not raise
        report = miner.mine([e for e in entries if e])
        assert report.total_entries_analyzed >= 0

    def test_eval_router_with_empty_output(self):
        """EvalRouter ne doit pas crasher sur un output vide"""
        from core.observability.eval_router import EvalRouter

        router = EvalRouter()
        router.load_rubrics()
        results = router.evaluate(
            vertical="comptable",
            input_text="Question",
            output_text="",
        )
        # Should return results (possibly low scores)
        assert isinstance(results, list)

    def test_experiment_with_empty_change(self):
        """RuleExperiment ne doit pas crasher avec un RuleChange vide"""
        from core.observability.rule_experiment import RuleExperiment, RuleChange

        exp = RuleExperiment()
        cases = [type('C', (), {
            'vertical': 'comptable', 'case_id': f'c-{i}',
            'input_text': f'Q{i}', 'output_text': f'A{i}',
            'expected_label': type('L', (), {'value': 'pass'})(),
        })() for i in range(10)]

        change = RuleChange(vertical="comptable", before={}, after={})
        report = exp.run_experiment(change=change, test_cases=cases)
        assert report.experiment_id != ""

    def test_backtest_result_edge_cases(self):
        from core.observability.auto_approver import BacktestResult

        # Zero cases
        bt = BacktestResult()
        assert bt.precision == 0.0
        assert bt.recall == 0.0
        d = bt.to_dict()
        assert "total_cases" in d
