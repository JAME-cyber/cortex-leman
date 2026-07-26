import json

from core.compliance.ai_sbom import AIActRiskTier, AISBOMGenerator, ModelComponent
from core.compliance.cortex_sbom import get_cortex_sbom, get_cortex_sbom_markdown


def test_cyclonedx_format_validity():
    sbom = get_cortex_sbom()
    assert sbom["bomFormat"] == "CycloneDX"
    assert sbom["specVersion"] == "1.6"
    assert isinstance(sbom["components"], list)
    assert isinstance(sbom["dependencies"], list)
    json.dumps(sbom)


def test_art11_gap_detection():
    generator = AISBOMGenerator()
    generator.add_model(ModelComponent(
        name="x", version="1", supplier="S", jurisdiction="FR/EU", purpose="test",
        risk_tier="minimal", data_categories=[], security_assessment=False,
    ))
    gaps = generator.validate_ai_act_art11(generator.generate())
    assert any("security assessment" in gap for gap in gaps)
    assert any("data categories" in gap for gap in gaps)
    assert any("evaluation date" in gap for gap in gaps)


def test_art13_gap_detection():
    generator = AISBOMGenerator()
    generator.add_model(ModelComponent(
        name="x", version="1", supplier="S", jurisdiction="FR/EU", purpose="test",
        risk_tier="minimal", data_categories=["prompts"], security_assessment=True,
        evaluated_date="2025-01-01",
    ))
    gaps = generator.validate_ai_act_art13(generator.generate())
    assert any("model card" in gap for gap in gaps)


def test_risk_tier_classification():
    assert AIActRiskTier.classify_model("x", "write text", ["content_generation"]) == "limited"
    assert AIActRiskTier.classify_model("x", "approve benefits", ["automated_decision"]) == "high"
    assert AIActRiskTier.classify_model("x", "rank citizens", ["social_scoring"]) == "unacceptable"
    assert AIActRiskTier.classify_model("x", "face matching", ["biometric"]) == "high"


def test_cross_border_flag():
    components = {component["name"]: component for component in get_cortex_sbom()["components"]}
    props = {item["name"]: item["value"] for item in components["anthropic/claude-sonnet-4"]["properties"]}
    assert props["ai:cross-border-transfer"] is True
    props = {item["name"]: item["value"] for item in components["mistralai/mistral-small-3.1-24b-instruct"]["properties"]}
    assert props["ai:cross-border-transfer"] is False


def test_markdown_generation():
    markdown = get_cortex_sbom_markdown()
    assert markdown.startswith("# Cortex Leman AI SBOM")
    assert "| Model | Version |" in markdown
    assert "anthropic/claude-sonnet-4" in markdown
