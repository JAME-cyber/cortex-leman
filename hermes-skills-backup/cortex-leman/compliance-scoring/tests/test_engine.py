"""
Tests for the compliance engine.

Run: pytest ~/.hermes/skills/cortex-leman/compliance-scoring/tests/ -v
"""

import sys
import os

# Ensure package is importable
# Add both the skills dir and its parent so 'compliance_scoring' resolves
_tests_dir = os.path.dirname(os.path.abspath(__file__))
_package_dir = os.path.dirname(_tests_dir)
_parent_dir = os.path.dirname(_package_dir)
sys.path.insert(0, _package_dir)  # compliance_scoring as top-level
sys.path.insert(0, os.path.join(_package_dir, '..'))  # parent dir

from compliance_scoring.engine import ComplianceEngine
from compliance_scoring.models import (
    AuditInput,
    ChecklistResponse,
    ClassificationLevel,
    ColorCode,
)
from compliance_scoring.scoring.weights import get_regulation_weights, normalize_weights
from compliance_scoring.scoring.thresholds import classify, classify_domain


# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

def _perfect_responses(engine: ComplianceEngine) -> dict:
    """Generate perfect (all 1.0) responses for all checklist items."""
    items = engine.get_all_checklist_items()
    return {
        item["id"]: ChecklistResponse(
            item_id=item["id"],
            score=1.0,
            evidence="Parfaitement conforme",
        )
        for item in items
    }


def _zero_responses(engine: ComplianceEngine) -> dict:
    """Generate zero (all 0.0) responses."""
    items = engine.get_all_checklist_items()
    return {
        item["id"]: ChecklistResponse(
            item_id=item["id"],
            score=0.0,
            evidence="Non conforme",
        )
        for item in items
    }


def _mixed_responses(engine: ComplianceEngine) -> dict:
    """Generate mixed responses (some 1.0, some 0.5, some 0.0)."""
    items = engine.get_all_checklist_items()
    responses = {}
    for i, item in enumerate(items):
        if i % 3 == 0:
            score = 1.0
        elif i % 3 == 1:
            score = 0.5
        else:
            score = 0.0
        responses[item["id"]] = ChecklistResponse(
            item_id=item["id"],
            score=score,
        )
    return responses


# ---------------------------------------------------------------------------
# Engine tests
# ---------------------------------------------------------------------------

class TestEngine:
    """Tests for the main ComplianceEngine."""

    def test_engine_initialization(self):
        engine = ComplianceEngine()
        assert engine is not None
        summary = engine.get_domains_summary()
        assert summary["total_domains"] == 20  # 10 RGPD + 6 AI Act + 4 LPD/CH
        assert summary["total_criteria"] > 0
        assert summary["total_checklist_items"] > 50

    def test_perfect_score(self):
        engine = ComplianceEngine()
        responses = _perfect_responses(engine)
        audit_input = AuditInput(
            client_id="TEST-PERFECT",
            sector="tech",
            jurisdiction="FR_CH",
            responses=responses,
        )
        result = engine.run_audit(audit_input)
        assert result.global_score >= 0.85
        assert result.classification == ClassificationLevel.PLEINEMENT_CONFORME
        assert result.color == ColorCode.VERT
        assert result.attestation_eligible is True
        assert result.kill_switch.activated is False
        assert len(result.all_violations) == 0

    def test_zero_score(self):
        engine = ComplianceEngine()
        responses = _zero_responses(engine)
        audit_input = AuditInput(
            client_id="TEST-ZERO",
            sector="health",
            jurisdiction="FR",
            responses=responses,
        )
        result = engine.run_audit(audit_input)
        assert result.global_score < 0.20
        assert result.classification == ClassificationLevel.NON_CONFORME
        assert result.color == ColorCode.ROUGE
        assert result.attestation_eligible is False
        assert result.kill_switch.activated is True

    def test_mixed_score(self):
        engine = ComplianceEngine()
        responses = _mixed_responses(engine)
        audit_input = AuditInput(
            client_id="TEST-MIXED",
            sector="finance",
            jurisdiction="FR_CH",
            responses=responses,
        )
        result = engine.run_audit(audit_input)
        assert 0.20 < result.global_score < 0.85
        # Should have violations
        assert len(result.all_violations) > 0

    def test_domain_scores_present(self):
        engine = ComplianceEngine()
        responses = _perfect_responses(engine)
        audit_input = AuditInput(
            client_id="TEST-DOMAINS",
            sector="other",
            jurisdiction="FR_CH",
            responses=responses,
        )
        result = engine.run_audit(audit_input)
        assert len(result.domain_scores) == 20
        # Check RGPD domains
        rgpd_domains = [ds for ds in result.domain_scores if ds.regulation == "RGPD"]
        assert len(rgpd_domains) == 10
        # Check AI Act domains
        ai_domains = [ds for ds in result.domain_scores if ds.regulation == "AI_ACT"]
        assert len(ai_domains) == 6
        # Check LPD/CH domains
        lpd_domains = [ds for ds in result.domain_scores if ds.regulation == "LPD_CH"]
        assert len(lpd_domains) == 4

    def test_recommendations_generated(self):
        engine = ComplianceEngine()
        responses = _zero_responses(engine)
        audit_input = AuditInput(
            client_id="TEST-RECS",
            sector="retail",
            jurisdiction="FR",
            responses=responses,
        )
        result = engine.run_audit(audit_input)
        assert len(result.recommendations) > 0
        # Should contain critical recommendations
        has_critical = any("🔴" in r for r in result.recommendations)
        assert has_critical

    def test_citations_traceable(self):
        engine = ComplianceEngine()
        responses = _perfect_responses(engine)
        audit_input = AuditInput(
            client_id="TEST-CITE",
            sector="other",
            jurisdiction="FR_CH",
            responses=responses,
        )
        result = engine.run_audit(audit_input)
        assert len(result.citations) > 0
        # Check citation format
        for citation in result.citations:
            assert citation.source in ("RGPD", "AI_ACT", "LPD_CH")
            assert citation.article_id.startswith(citation.source)
            assert len(citation.excerpt) > 0

    def test_result_to_dict(self):
        engine = ComplianceEngine()
        responses = _perfect_responses(engine)
        audit_input = AuditInput(
            client_id="TEST-DICT",
            sector="tech",
            jurisdiction="FR",
            responses=responses,
        )
        result = engine.run_audit(audit_input)
        d = result.to_dict()
        assert "global_score" in d
        assert "classification" in d
        assert "attestation_eligible" in d
        assert "regulation_weights" in d
        assert "domain_scores" in d
        assert d["attestation_eligible"] is True

    def test_sector_ai_higher_ai_act_weight(self):
        """Tech/AI sectors should have higher AI Act weight."""
        weights_fr = get_regulation_weights("tech", "FR")
        weights_other = get_regulation_weights("retail", "FR")
        assert weights_fr["AI_ACT"] > weights_other["AI_ACT"]

    def test_jurisdiction_fr_no_lpd(self):
        """France-only should have zero LPD/CH weight."""
        weights = get_regulation_weights("other", "FR")
        assert weights["LPD_CH"] == 0.0

    def test_jurisdiction_ch_higher_lpd(self):
        """Switzerland should have higher LPD/CH weight."""
        weights = get_regulation_weights("other", "CH")
        assert weights["LPD_CH"] >= 0.40

    def test_weights_sum_to_one(self):
        for sector in ["health", "finance", "retail", "public", "tech", "ai", "other"]:
            for jurisdiction in ["FR", "CH", "FR_CH"]:
                weights = get_regulation_weights(sector, jurisdiction)
                total = sum(weights.values())
                assert abs(total - 1.0) < 0.001, f"Weights don't sum to 1.0 for {sector}/{jurisdiction}: {total}"


# ---------------------------------------------------------------------------
# Classification tests
# ---------------------------------------------------------------------------

class TestClassification:
    def test_vert(self):
        level, color = classify(0.90)
        assert level == ClassificationLevel.PLEINEMENT_CONFORME
        assert color == ColorCode.VERT

    def test_orange_clair(self):
        level, color = classify(0.78)
        assert level == ClassificationLevel.LARGEMENT_CONFORME
        assert color == ColorCode.ORANGE_CLAIR

    def test_orange_fonce(self):
        level, color = classify(0.55)
        assert level == ClassificationLevel.PARTIELLEMENT_CONFORME
        assert color == ColorCode.ORANGE_FONCE

    def test_rouge(self):
        level, color = classify(0.30)
        assert level == ClassificationLevel.NON_CONFORME
        assert color == ColorCode.ROUGE

    def test_boundary_085(self):
        level, color = classify(0.85)
        assert level == ClassificationLevel.PLEINEMENT_CONFORME

    def test_boundary_070(self):
        level, color = classify(0.70)
        assert level == ClassificationLevel.LARGEMENT_CONFORME

    def test_boundary_050(self):
        level, color = classify(0.50)
        assert level == ClassificationLevel.PARTIELLEMENT_CONFORME

    def test_domain_classify_more_lenient(self):
        # Domain thresholds are more lenient
        # At 0.66: global gives PARTIELLEMENT (threshold 0.70), domain gives LARGEMENT (threshold 0.65)
        level_g, _ = classify(0.66)  # Global: PARTIELLEMENT_CONFORME (needs 0.70)
        level_d, _ = classify_domain(0.66)  # Domain: LARGEMENT_CONFORME (needs 0.65)
        # Compare by severity order, not alphabetical
        from compliance_scoring.models import ClassificationLevel
        severity_order = [ClassificationLevel.NON_CONFORME, ClassificationLevel.PARTIELLEMENT_CONFORME,
                          ClassificationLevel.LARGEMENT_CONFORME, ClassificationLevel.PLEINEMENT_CONFORME]
        assert severity_order.index(level_d) > severity_order.index(level_g)


# ---------------------------------------------------------------------------
# Legacy API test (backward compatibility)
# ---------------------------------------------------------------------------

class TestLegacyAPI:
    def test_generate_score_report_format(self):
        engine = ComplianceEngine()
        criteria_results = {
            'rgpd_principes': {'score': 0.9, 'violations': []},
            'rgpd_droits': {'score': 0.3, 'violations': ['Missing consent mechanism']},
            'rgpd_obligations': {'score': 0.7, 'violations': []},
        }
        report = engine.generate_score_report(criteria_results, sector='health')
        assert "global_score" in report
        assert "classification" in report
        assert "kill_switch" in report
        assert "regulation_weights" in report

    def test_legacy_report_has_action_required(self):
        engine = ComplianceEngine()
        criteria_results = {
            'rgpd_transferts': {'score': 0.2, 'violations': ['Transfert US sans CSC']},
        }
        report = engine.generate_score_report(criteria_results)
        assert "action_required" in report["classification"]


# ---------------------------------------------------------------------------
# Checklist coverage test
# ---------------------------------------------------------------------------

class TestChecklistCoverage:
    def test_all_domains_have_checklists(self):
        engine = ComplianceEngine()
        summary = engine.get_domains_summary()
        for domain in summary["domains"]:
            assert domain["checklist_items"] > 0, f"Domain {domain['id']} has no checklist items"

    def test_rgpd_has_10_domains(self):
        engine = ComplianceEngine()
        rgpd = [d for d in engine.domains if d.regulation == "RGPD"]
        assert len(rgpd) == 10

    def test_ai_act_has_6_domains(self):
        engine = ComplianceEngine()
        ai = [d for d in engine.domains if d.regulation == "AI_ACT"]
        assert len(ai) == 6

    def test_lpd_has_4_domains(self):
        engine = ComplianceEngine()
        lpd = [d for d in engine.domains if d.regulation == "LPD_CH"]
        assert len(lpd) == 4


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])


# ---------------------------------------------------------------------------
# Claude review: additional edge case tests
# ---------------------------------------------------------------------------

class TestEdgeCasesClaudeReview:
    """Tests identified as missing by Claude code review."""

    def test_partial_responses_one_domain_only(self):
        """Only one domain has responses, others should not penalize."""
        engine = ComplianceEngine()
        # Only answer rgpd_principes questions
        rgpd_items = [i for i in engine.get_all_checklist_items() if i["domain_id"] == "rgpd_principes"]
        responses = {
            item["id"]: ChecklistResponse(item_id=item["id"], score=0.9, evidence="OK")
            for item in rgpd_items
        }
        audit_input = AuditInput(
            client_id="TEST-PARTIAL",
            sector="other",
            jurisdiction="FR",
            responses=responses,
        )
        result = engine.run_audit(audit_input)
        # RGPD principles should be high, but other domains should not drag global to 0
        rgpd_principles = next(ds for ds in result.domain_scores if ds.domain_id == "rgpd_principes")
        assert rgpd_principles.score >= 0.85
        # Global should still be calculated (not 0)
        assert result.global_score > 0.0
        # Kill switch should not trigger just because domains are unanswered
        assert not result.kill_switch.activated

    def test_all_responses_neutral_05(self):
        """All responses at 0.5 should give a moderate score, not zero."""
        engine = ComplianceEngine()
        items = engine.get_all_checklist_items()
        responses = {
            item["id"]: ChecklistResponse(item_id=item["id"], score=0.5)
            for item in items
        }
        audit_input = AuditInput(
            client_id="TEST-NEUTRAL",
            sector="other",
            jurisdiction="FR",
            responses=responses,
        )
        result = engine.run_audit(audit_input)
        assert 0.40 < result.global_score < 0.60

    def test_empty_responses_dict(self):
        """Empty responses dict should handle gracefully."""
        engine = ComplianceEngine()
        audit_input = AuditInput(
            client_id="TEST-EMPTY",
            sector="health",
            jurisdiction="CH",
            responses={},
        )
        result = engine.run_audit(audit_input)
        assert result.global_score == 0.0  # No data = no score
        # No violations since no criteria were evaluated
        assert len(result.all_violations) == 0
        # Kill switch should NOT trigger (nothing was evaluated)
        assert not result.kill_switch.activated

    def test_invalid_response_scores_clamped(self):
        """Response scores outside 0-1 should be handled gracefully."""
        engine = ComplianceEngine()
        items = engine.get_all_checklist_items()
        if not items:
            return
        # Use an out-of-range score
        responses = {
            items[0]["id"]: ChecklistResponse(item_id=items[0]["id"], score=1.5),
            items[1]["id"]: ChecklistResponse(item_id=items[1]["id"], score=-0.5),
        }
        audit_input = AuditInput(
            client_id="TEST-INVALID",
            sector="other",
            jurisdiction="FR",
            responses=responses,
        )
        # Should not crash
        result = engine.run_audit(audit_input)
        assert result is not None

    def test_performance_full_audit_under_5_seconds(self):
        """Full audit with all 172 items should complete in under 5 seconds."""
        import time
        engine = ComplianceEngine()
        items = engine.get_all_checklist_items()
        responses = {
            item["id"]: ChecklistResponse(item_id=item["id"], score=0.8, evidence="Doc")
            for item in items
        }
        audit_input = AuditInput(
            client_id="TEST-PERF",
            sector="tech",
            jurisdiction="FR_CH",
            responses=responses,
        )
        start = time.time()
        result = engine.run_audit(audit_input)
        elapsed = time.time() - start
        assert elapsed < 5.0, f"Audit took {elapsed:.2f}s, exceeds 5s threshold"
        assert result.global_score >= 0.8, f"Score {result.global_score:.3f} too low"

    def test_ai_act_article_5_references(self):
        """AI Act prohibited practices should reference Art. 5, not Art. 6."""
        engine = ComplianceEngine()
        ai_domains = [d for d in engine.domains if d.regulation == "AI_ACT"]
        classification_domain = next(d for d in ai_domains if d.id == "aiact_classification")
        for criterion in classification_domain.criteria:
            if "notation sociale" in criterion.title or "Manipulation" in criterion.title:
                assert criterion.article_id.startswith("AI_ACT.5"), \
                    f"Prohibited practice '{criterion.title}' should reference Art. 5, got {criterion.article_id}"

    def test_kill_switch_not_triggered_by_unanswered(self):
        """Kill switch should NOT trigger when domains have 0 responses."""
        engine = ComplianceEngine()
        audit_input = AuditInput(
            client_id="TEST-KS-UNANSWERED",
            sector="other",
            jurisdiction="FR",
            responses={},
        )
        result = engine.run_audit(audit_input)
        # Kill switch should NOT activate for unanswered domains
        assert not result.kill_switch.activated

    def test_legacy_sanitized_keys(self):
        """Legacy API should handle special characters in domain keys."""
        engine = ComplianceEngine()
        criteria_results = {
            'rgpd/transferts (hors-UE)': {'score': 0.3, 'violations': ['No CSC']},
        }
        # Should not crash with special characters
        report = engine.generate_score_report(criteria_results)
        assert "global_score" in report
