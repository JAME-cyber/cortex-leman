import pytest

from core.security.research_integration import (
    AgentGovernanceRules,
    ComplianceGapScanner,
    MediaAuthenticityScorer,
    SystemSecurityCompositor,
    TrustCertificationEngine,
)


def test_all_certification_levels():
    engine = TrustCertificationEngine()
    assert engine.certify("a", {d: 10 for d in engine.DIMENSIONS}).level == "Bronze"
    assert engine.certify("b", {d: 12 for d in engine.DIMENSIONS}).level == "Silver"
    assert engine.certify("c", {d: 16 for d in engine.DIMENSIONS}).level == "Gold"
    assert engine.certify("d", {d: 18 for d in engine.DIMENSIONS}).level == "Platinum"


def test_all_gap_types():
    report = ComplianceGapScanner().scan({})
    assert {gap.gap_name for gap in report.gaps} == {
        "explainability_depth", "digital_security", "design_phase", "data_phase"
    }


def test_composition_risk_detection():
    report = SystemSecurityCompositor().audit_composition(
        [{"id": "a", "privileges": ["read"]}, {"id": "b", "privileges": ["read"]}],
        [{"source": "a", "target": "b", "authenticated": False, "grants": ["admin"]},
         {"source": "b", "target": "a", "authenticated": True}],
    )
    types = {finding.finding_type for finding in report.findings}
    assert {"unauthenticated_channels", "privilege_escalation", "trust_transitivity"} <= types


def test_agent_levels_0_3_5():
    rules = AgentGovernanceRules()
    assert rules.classify_agent({"level": 0}).level == 0
    level_three = rules.classify_agent({"level": 3})
    assert level_three.ai_act_articles == ["Article 50", "Article 14"]
    level_five = rules.classify_agent({"level": 5})
    assert level_five.requires_dpia and level_five.ai_act_articles[0] == "Article 9"


def test_media_high_and_low_scores():
    scorer = MediaAuthenticityScorer()
    high = scorer.score_media({"watermark": True, "signature": True, "provenance": True, "consistent": True})
    low = scorer.score_media({})
    assert high.score == 100 and high.risk_level == "low"
    assert low.score == 0 and low.risk_level == "high"
    assert scorer.detect_synthetic_markers("AI-generated deepfake").detected


# ── Extended coverage (paper-specific edge cases) ──

def test_trust_certificate_rejects_out_of_range():
    engine = TrustCertificationEngine()
    with pytest.raises(ValueError):
        engine.certify("x", {d: 25 for d in engine.DIMENSIONS})
    with pytest.raises(ValueError):
        engine.certify("x", {d: -1 for d in engine.DIMENSIONS})


def test_trust_certificate_recommendations_for_low_dimensions():
    engine = TrustCertificationEngine()
    cert = engine.certify("sys", {"reliability": 8, "safety": 18, "fairness": 18, "transparency": 18, "security": 18})
    assert any("reliability" in r for r in cert.recommendations)


def test_gap_scanner_finds_no_gaps_when_all_covered():
    report = ComplianceGapScanner().scan({
        "explainability": True, "security": True,
        "design_review": True, "data_governance": True,
    })
    assert len(report.gaps) == 0
    assert report.overall_coverage_pct == 100.0


def test_composition_detects_data_flow_loop():
    report = SystemSecurityCompositor().audit_composition(
        [{"id": "x"}, {"id": "y"}],
        [{"source": "x", "target": "y", "authenticated": True},
         {"source": "y", "target": "x", "authenticated": True}],
    )
    assert any(f.finding_type == "data_flow_loops" for f in report.findings) or \
           any(f.finding_type == "trust_transitivity" for f in report.findings)


def test_composition_clean_system_no_findings():
    report = SystemSecurityCompositor().audit_composition(
        [{"id": "a", "privileges": ["read"]}, {"id": "b", "privileges": ["read"]}],
        [{"source": "a", "target": "b", "authenticated": True, "grants": ["read"]}],
    )
    assert len(report.findings) == 0
    assert report.composite_security_score == 100.0


def test_agent_level_2_requires_transparency():
    rules = AgentGovernanceRules()
    result = rules.classify_agent({"level": 2})
    assert "Article 50" in result.ai_act_articles
    assert not result.requires_dpia


def test_agent_autonomy_inferred_from_scores():
    rules = AgentGovernanceRules()
    high_auto = rules.classify_agent({"autonomy": 5, "impact": 5})
    assert high_auto.level == 5
    low_auto = rules.classify_agent({"autonomy": 0, "impact": 0})
    assert low_auto.level == 0


def test_media_partial_score():
    scorer = MediaAuthenticityScorer()
    result = scorer.score_media({"watermark": True, "signature": False, "provenance": False, "consistent": False})
    assert result.score == 25
    assert result.risk_level == "high"


def test_synthetic_detection_finds_chainmark_watermark():
    """ChainMark integration: watermarked text is detected as synthetic by PhantomSeal scorer."""
    from core.security.watermarker import ChainMarkWatermarker
    wm = ChainMarkWatermarker(tenant_id="test")
    watermarked = wm.watermark("This is a sufficiently long legal response with multiple words.", visible=False)
    scorer = MediaAuthenticityScorer()
    detection = scorer.detect_synthetic_markers(watermarked.text)
    assert detection.detected
    assert any("chainmark" in m for m in detection.markers)


def test_paper_references_complete():
    from core.security.research_integration import PAPER_REFERENCES
    expected = {"trust_certification", "trustworthy_ai_tools", "channelguard",
                "agentic_ai_regulation", "phantomseal"}
    assert set(PAPER_REFERENCES.keys()) == expected
