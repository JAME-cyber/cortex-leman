"""
Tests — Modules Observabilité Intercom-Inspired Cortex Leman v5

9. ComplianceSkill — Unité atomique de savoir métier
10. AutoApprover — Auto-approbation avec backtesting
11. SessionMiner — Mining des traces WORM
"""
import pytest
import json
from datetime import datetime, timezone


# ============================================================
# Module 9: ComplianceSkill + SkillRegistry
# ============================================================

class TestComplianceSkill:

    def test_skill_creation(self):
        from core.observability.compliance_skill import ComplianceSkill, SkillDomain, SkillConfidence

        skill = ComplianceSkill(
            skill_id="test-skill",
            name="Test Skill",
            vertical="comptable",
            domain=SkillDomain.FISCAL,
            confidence=SkillConfidence.MEDIUM,
            trigger_patterns=["déduction", "fiscal", "impôt"],
        )
        assert skill.skill_id == "test-skill"
        assert skill.domain == SkillDomain.FISCAL

    def test_skill_matching(self):
        from core.observability.compliance_skill import ComplianceSkill, SkillDomain

        skill = ComplianceSkill(
            skill_id="test-match",
            trigger_patterns=["déduction fiscale", "optimisation fiscale"],
        )

        # High match
        score_high = skill.matches_problem("Peut-on déduire les frais de déduction fiscale ?")
        assert score_high > 0.3

        # No match
        score_none = skill.matches_problem("Quel temps fait-il à Paris ?")
        assert score_none < 0.1

    def test_skill_invoke_no_engines(self):
        from core.observability.compliance_skill import ComplianceSkill, SkillDomain

        skill = ComplianceSkill(
            skill_id="test-invoke",
            name="Test",
            vertical="comptable",
            domain=SkillDomain.FISCAL,
        )

        result = skill.invoke("Question test", context={"amount": 100})
        assert result["skill_id"] == "test-invoke"
        assert result["recommendation"] == "safe"
        assert "invoked_at" in result

    def test_skill_invoke_with_rules(self):
        from core.observability.compliance_skill import ComplianceSkill, SkillDomain

        skill = ComplianceSkill(
            skill_id="test-rules",
            vertical="comptable",
            domain=SkillDomain.FISCAL,
            rule_ids=["comptable-001"],
        )

        class MockRulesEngine:
            def evaluate(self, vertical, context):
                class R:
                    rule_id = "comptable-001"
                    triggered = True
                    action = "freeze"
                    severity = "high"
                    message = "Montant élevé"
                return [R()]

        result = skill.invoke("Question test", context={}, rules_engine=MockRulesEngine())
        assert result["recommendation"] == "freeze"
        assert len(result["rules_results"]) == 1

    def test_skill_serialization(self):
        from core.observability.compliance_skill import ComplianceSkill, SkillDomain, SkillConfidence

        skill = ComplianceSkill(
            skill_id="test-ser",
            name="Test",
            vertical="avocat",
            domain=SkillDomain.PROFESSIONAL_SECRET,
            confidence=SkillConfidence.HIGH,
            trigger_patterns=["secret professionnel"],
        )
        d = skill.to_dict()
        assert d["skill_id"] == "test-ser"
        assert d["domain"] == "professional_secret"
        assert d["confidence"] == "high"


class TestSkillRegistry:

    def test_registry_register(self):
        from core.observability.compliance_skill import SkillRegistry, ComplianceSkill

        registry = SkillRegistry()
        skill = ComplianceSkill(skill_id="r1", vertical="comptable", trigger_patterns=["test"])
        sid = registry.register(skill)
        assert sid == "r1"
        assert len(registry.get_all_skills()) == 1

    def test_registry_find_matching(self):
        from core.observability.compliance_skill import SkillRegistry, ComplianceSkill

        registry = SkillRegistry()
        registry.register(ComplianceSkill(
            skill_id="fiscal", vertical="comptable",
            trigger_patterns=["déduction fiscale", "impôt sur les sociétés"],
        ))
        registry.register(ComplianceSkill(
            skill_id="secret", vertical="avocat",
            trigger_patterns=["secret professionnel", "dossier client"],
        ))

        matches = registry.find_matching("Peut-on déduire les frais de déduction fiscale ?")
        assert len(matches) > 0
        assert matches[0][0].skill_id == "fiscal"
        assert matches[0][1] > 0  # Score > 0

    def test_registry_find_by_vertical(self):
        from core.observability.compliance_skill import SkillRegistry, ComplianceSkill

        registry = SkillRegistry()
        registry.register(ComplianceSkill(skill_id="c1", vertical="comptable", trigger_patterns=["test"]))
        registry.register(ComplianceSkill(skill_id="c2", vertical="comptable", trigger_patterns=["test"]))
        registry.register(ComplianceSkill(skill_id="a1", vertical="avocat", trigger_patterns=["test"]))

        comp = registry.get_skills_by_vertical("comptable")
        assert len(comp) == 2
        avoc = registry.get_skills_by_vertical("avocat")
        assert len(avoc) == 1

    def test_registry_find_filtered(self):
        from core.observability.compliance_skill import SkillRegistry, ComplianceSkill, SkillDomain

        registry = SkillRegistry()
        registry.register(ComplianceSkill(
            skill_id="fiscal", vertical="comptable", domain=SkillDomain.FISCAL,
            trigger_patterns=["impôt"],
        ))
        registry.register(ComplianceSkill(
            skill_id="gdpr", vertical="rh", domain=SkillDomain.GDPR,
            trigger_patterns=["données personnelles"],
        ))

        matches = registry.find_matching("Impôt sur les sociétés", vertical="comptable")
        assert all(s.vertical == "comptable" for s, _ in matches)

    def test_seed_skills(self):
        from core.observability.compliance_skill import SkillRegistry, seed_skills

        registry = SkillRegistry()
        count = seed_skills(registry)
        assert count >= 6  # 6 verticals minimum

        stats = registry.get_stats()
        assert stats["total_skills"] >= 6
        assert "comptable" in stats["by_vertical"]

    def test_skill_guide(self):
        from core.observability.compliance_skill import SkillGuide

        guide = SkillGuide(
            title="Test Guide",
            steps=["Step 1", "Step 2"],
            warnings=["Warning 1"],
            legal_references=["Art. 1"],
        )
        d = guide.to_dict()
        assert d["title"] == "Test Guide"
        assert len(d["steps"]) == 2


# ============================================================
# Module 10: AutoApprover
# ============================================================

class TestAutoApprover:

    def test_auto_approve_safe_operation(self):
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision

        approver = AutoApprover()
        request = ApprovalRequest(
            request_id="test-001",
            vertical="comptable",
            operation_type="data_query",
            confidence=0.95,
        )

        result = approver.evaluate(request)
        assert result.decision == ApprovalDecision.AUTO_APPROVED
        assert result.risk_level.value == "low"

    def test_reject_blocked_operation(self):
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision

        approver = AutoApprover()
        request = ApprovalRequest(
            request_id="test-002",
            vertical="comptable",
            operation_type="data_transfer",
            confidence=0.99,
        )

        result = approver.evaluate(request)
        assert result.decision == ApprovalDecision.REJECTED
        assert result.risk_level.value == "critical"

    def test_reject_high_amount(self):
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision

        approver = AutoApprover()
        request = ApprovalRequest(
            request_id="test-003",
            vertical="banque",
            operation_type="data_query",
            confidence=0.95,
            amount=15000.0,
        )

        result = approver.evaluate(request)
        assert result.decision == ApprovalDecision.NEEDS_ARBITRATION

    def test_needs_review_triggered_rule(self):
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision

        approver = AutoApprover()
        request = ApprovalRequest(
            request_id="test-004",
            vertical="comptable",
            operation_type="data_query",
            confidence=0.95,
        )

        rules = [{"rule_id": "r1", "triggered": True, "action": "warn", "severity": "medium"}]
        result = approver.evaluate(request, rules_results=rules)
        assert result.decision == ApprovalDecision.NEEDS_REVIEW
        assert result.rules_triggered == 1

    def test_reject_blocked_rule(self):
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision

        approver = AutoApprover()
        request = ApprovalRequest(
            request_id="test-005",
            vertical="avocat",
            operation_type="data_query",
            confidence=0.95,
        )

        rules = [{"rule_id": "r1", "triggered": True, "action": "block", "severity": "critical"}]
        result = approver.evaluate(request, rules_results=rules)
        assert result.decision == ApprovalDecision.REJECTED

    def test_needs_review_low_confidence(self):
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision

        approver = AutoApprover()
        request = ApprovalRequest(
            request_id="test-006",
            vertical="comptable",
            operation_type="data_query",
            confidence=0.6,  # Below 0.85 threshold
        )

        result = approver.evaluate(request)
        assert result.decision == ApprovalDecision.NEEDS_REVIEW

    def test_needs_review_failed_eval(self):
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision

        approver = AutoApprover()
        request = ApprovalRequest(
            request_id="test-007",
            vertical="comptable",
            operation_type="data_query",
            confidence=0.95,
        )

        evals = [{"rubric_id": "r1", "score": 0.3}]  # Below 0.8 threshold
        result = approver.evaluate(request, eval_results=evals)
        assert result.decision == ApprovalDecision.NEEDS_REVIEW

    def test_auto_approve_all_pass(self):
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision

        approver = AutoApprover()
        request = ApprovalRequest(
            request_id="test-008",
            vertical="comptable",
            operation_type="fiscal_info",
            confidence=0.92,
        )

        rules = [
            {"rule_id": "r1", "triggered": False, "action": "warn", "severity": "medium"},
            {"rule_id": "r2", "triggered": False, "action": "warn", "severity": "low"},
        ]
        evals = [
            {"rubric_id": "e1", "score": 0.95},
            {"rubric_id": "e2", "score": 0.88},
        ]

        result = approver.evaluate(request, rules_results=rules, eval_results=evals)
        assert result.decision == ApprovalDecision.AUTO_APPROVED
        assert result.rules_checked == 2
        assert result.evals_passed == 2

    def test_auto_approver_stats(self):
        from core.observability.auto_approver import AutoApprover, ApprovalRequest

        approver = AutoApprover()
        # 2 auto-approved
        for _ in range(2):
            approver.evaluate(ApprovalRequest(
                vertical="comptable", operation_type="data_query", confidence=0.95,
            ))
        # 1 rejected
        approver.evaluate(ApprovalRequest(
            vertical="comptable", operation_type="data_transfer", confidence=0.99,
        ))

        stats = approver.get_stats()
        assert stats["total_evaluations"] == 3
        assert stats["auto_approved"] == 2
        assert stats["rejected"] == 1

    def test_auto_approver_backtest(self):
        from core.observability.auto_approver import AutoApprover

        approver = AutoApprover()

        # Créer des mock golden cases
        class MockCase:
            def __init__(self, vertical, label):
                self.vertical = vertical
                self.expected_label = type('L', (), {'value': label})()
                self.input_text = "Test"
                self.output_text = "Response"

        cases = [
            MockCase("comptable", "pass"),
            MockCase("comptable", "pass"),
            MockCase("comptable", "fail"),
            MockCase("avocat", "pass"),
            MockCase("avocat", "fail"),
        ]

        bt = approver.backtest(cases)
        assert bt.total_cases == 5
        assert isinstance(bt.precision, float)
        assert isinstance(bt.recall, float)
        d = bt.to_dict()
        assert "total_cases" in d

    def test_approval_result_serialization(self):
        from core.observability.auto_approver import ApprovalResult, ApprovalDecision, ApprovalRisk

        result = ApprovalResult(
            result_id="test",
            decision=ApprovalDecision.AUTO_APPROVED,
            risk_level=ApprovalRisk.LOW,
            confidence=0.95,
            reasoning="All checks passed",
        )
        d = result.to_dict()
        assert d["decision"] == "auto_approved"
        assert d["risk_level"] == "low"


# ============================================================
# Module 11: SessionMiner
# ============================================================

class TestSessionMiner:

    def _make_entries(self, n=20, vertical="comptable", agent="data", confidence=0.85):
        entries = []
        for i in range(n):
            entries.append({
                "event_type": "agent.result",
                "client_id": "test",
                "vertical": vertical,
                "agent_source": agent,
                "intention_id": f"int-{i % 5}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {"confidence": confidence},
            })
        return entries

    def test_miner_empty(self):
        from core.observability.session_miner import SessionMiner

        miner = SessionMiner()
        report = miner.mine([])
        assert report.total_entries_analyzed == 0

    def test_miner_basic(self):
        from core.observability.session_miner import SessionMiner

        miner = SessionMiner()
        entries = self._make_entries(50, vertical="comptable", confidence=0.9)
        report = miner.mine(entries)

        assert report.total_entries_analyzed == 50
        assert len(report.skill_metrics) > 0
        d = report.to_dict()
        assert "skill_metrics" in d

    def test_miner_failure_patterns(self):
        from core.observability.session_miner import SessionMiner

        entries = self._make_entries(30, vertical="banque", confidence=0.4)
        # Ajouter beaucoup de conflits
        for i in range(15):
            entries.append({
                "event_type": "mediator_conflict",
                "vertical": "banque",
                "agent_source": "data",
                "intention_id": f"conflict-{i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {"reason": "KYC threshold exceeded"},
            })

        miner = SessionMiner()
        report = miner.mine(entries)

        # Should detect failure patterns
        conflict_patterns = [p for p in report.failure_patterns if p.failure_type == "mediator_conflict"]
        assert len(conflict_patterns) > 0
        assert conflict_patterns[0].occurrence_count > 0

    def test_miner_dark_corners(self):
        from core.observability.session_miner import SessionMiner

        # Only comptable traces → other verticals are dark corners
        entries = self._make_entries(50, vertical="comptable")

        miner = SessionMiner()
        report = miner.mine(entries)

        # Should detect missing verticals
        assert len(report.dark_corners) > 0
        dark_verticals = {d.vertical for d in report.dark_corners}
        assert "avocat" in dark_verticals or "banque" in dark_verticals

    def test_miner_golden_candidates(self):
        from core.observability.session_miner import SessionMiner

        entries = []
        # PASS candidate: high confidence, no conflict
        for i in range(5):
            entries.append({
                "event_type": "intention_created",
                "vertical": "comptable",
                "agent_source": "data",
                "intention_id": "good-int",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {"original_query": "Quelle TVA en Suisse ?"},
            })
            entries.append({
                "event_type": "agent.result",
                "vertical": "comptable",
                "agent_source": "data",
                "intention_id": "good-int",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {"confidence": 0.95, "result": "TVA 8.1%"},
            })

        # FAIL candidate: with conflict
        for i in range(3):
            entries.append({
                "event_type": "intention_created",
                "vertical": "banque",
                "agent_source": "data",
                "intention_id": "bad-int",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {"original_query": "Comment contourner KYC ?"},
            })
            entries.append({
                "event_type": "agent.result",
                "vertical": "banque",
                "agent_source": "data",
                "intention_id": "bad-int",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {"confidence": 0.3, "result": "..."},
            })
            entries.append({
                "event_type": "mediator_conflict",
                "vertical": "banque",
                "agent_source": "mediator",
                "intention_id": "bad-int",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {},
            })

        miner = SessionMiner()
        report = miner.mine(entries)

        fail_cands = [c for c in report.golden_case_candidates if c["expected_label"] == "fail"]
        pass_cands = [c for c in report.golden_case_candidates if c["expected_label"] == "pass"]
        assert len(fail_cands) > 0
        assert len(pass_cands) > 0

    def test_miner_confidence_correlation(self):
        from core.observability.session_miner import SessionMiner

        entries = []
        # High confidence → success
        for i in range(10):
            entries.append({
                "event_type": "agent.result",
                "vertical": "comptable",
                "agent_source": "data",
                "intention_id": f"hconf-{i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {"confidence": 0.9},
            })

        # Low confidence → conflicts
        for i in range(10):
            entries.append({
                "event_type": "agent.result",
                "vertical": "banque",
                "agent_source": "data",
                "intention_id": f"lconf-{i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {"confidence": 0.3},
            })
            entries.append({
                "event_type": "mediator_conflict",
                "vertical": "banque",
                "agent_source": "mediator",
                "intention_id": f"lconf-{i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {},
            })

        miner = SessionMiner()
        report = miner.mine(entries)

        corr = report.confidence_vs_success
        assert isinstance(corr, dict)
        # Le bucket 0.85-1.0 devrait avoir un meilleur success_rate que 0.3-0.5
        high_bucket = corr.get("0.85-1.0", {}).get("success_rate", 0)
        low_bucket = corr.get("0.0-0.3", {}).get("success_rate", 1)
        assert high_bucket >= low_bucket

    def test_miner_recommendations(self):
        from core.observability.session_miner import SessionMiner

        entries = self._make_entries(50, vertical="comptable", confidence=0.3)
        # Add errors
        for i in range(5):
            entries.append({
                "event_type": "agent_error",
                "vertical": "comptable",
                "agent_source": "data",
                "intention_id": f"err-{i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {},
            })

        miner = SessionMiner()
        report = miner.mine(entries)

        assert len(report.recommendations) > 0
        cats = {r["category"] for r in report.recommendations}
        assert "golden_dataset" in cats  # Always recommended

    def test_skill_metrics_serialization(self):
        from core.observability.session_miner import SkillMetrics

        m = SkillMetrics(
            skill_id="test",
            vertical="comptable",
            total_invocations=100,
            successful=80,
            failed=15,
            blocked_by_mediator=5,
            pass_rate=0.8,
        )
        d = m.to_dict()
        assert d["pass_rate"] == 0.8
        assert d["total_invocations"] == 100


# ============================================================
# Integration: Full Intercom-inspired pipeline
# ============================================================

class TestIntercomPipelineIntegration:

    def test_full_intercom_pipeline(self):
        """
        Pipeline complet inspiré d'Intercom:
        1. SessionMiner analyse le WORM
        2. Génère des golden case candidats
        3. Skills matchent les problèmes
        4. AutoApprover décide des approbations
        """
        from core.observability.compliance_skill import SkillRegistry, ComplianceSkill, seed_skills
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision
        from core.observability.session_miner import SessionMiner

        # 1. Seed les skills
        registry = SkillRegistry()
        seed_skills(registry)
        assert len(registry.get_all_skills()) >= 6

        # 2. Trouver le skill fiscal
        matches = registry.find_matching("Peut-on déduire 80K CHF sans justificatif ?", vertical="comptable")
        assert len(matches) > 0
        fiscal_skill = matches[0][0]

        # 3. Invoquer le skill
        result = fiscal_skill.invoke(
            "Peut-on déduire 80K CHF ?",
            context={"amount": 80000},
        )
        assert result["skill_id"] != ""

        # 4. Auto-approver
        approver = AutoApprover()
        request = ApprovalRequest(
            vertical="comptable",
            operation_type="fiscal_info",
            confidence=0.95,
        )
        approval = approver.evaluate(request)
        assert approval.decision == ApprovalDecision.AUTO_APPROVED

        # 5. SessionMiner
        miner = SessionMiner()
        entries = [
            {"event_type": "agent.result", "vertical": "comptable", "agent_source": "data",
             "intention_id": f"int-{i}", "timestamp": datetime.now(timezone.utc).isoformat(),
             "payload": {"confidence": 0.9}}
            for i in range(20)
        ]
        report = miner.mine(entries)
        assert report.total_entries_analyzed == 20
        assert len(report.recommendations) > 0

    def test_skill_to_auto_approver_flow(self):
        """
        Flux: skill détecte un problème → auto-approver décide
        """
        from core.observability.compliance_skill import SkillRegistry, ComplianceSkill, seed_skills
        from core.observability.auto_approver import AutoApprover, ApprovalRequest, ApprovalDecision

        registry = SkillRegistry()
        seed_skills(registry)

        # L'agent détecte un problème bancaire AML
        matches = registry.find_matching("Comment structurer des virements pour éviter le KYC ?")
        assert len(matches) > 0

        # L'auto-approver bloque l'opération
        approver = AutoApprover()
        request = ApprovalRequest(
            vertical="banque",
            operation_type="data_transfer",  # blocked operation
            confidence=0.99,
        )
        result = approver.evaluate(request)
        assert result.decision == ApprovalDecision.REJECTED
