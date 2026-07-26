from __future__ import annotations

from .ai_sbom import AIActRiskTier, AISBOMGenerator, ModelComponent


def _tier(name: str, purpose: str, capabilities: list[str]) -> str:
    return AIActRiskTier.classify_model(name, purpose, capabilities)


def get_cortex_sbom() -> dict:
    generator = AISBOMGenerator()
    generator.add_model(ModelComponent(
        name="mistralai/mistral-small-3.1-24b-instruct", version="3.1-24b-instruct",
        supplier="Mistral AI", jurisdiction="FR/EU", purpose="content generation and decision support",
        risk_tier=_tier("Mistral Small", "content generation and decision support", ["content_generation"]),
        data_categories=["user prompts", "documents", "conversation metadata"],
        license="Apache-2.0", model_card_url="https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503",
        security_assessment=True, evaluated_date="2025-01-15", cross_border_transfer=False,
    ))
    generator.add_model(ModelComponent(
        name="llama3.1:8b", version="3.1-8b", supplier="Meta", jurisdiction="US/local on-premise",
        purpose="content generation and decision support",
        risk_tier=_tier("Llama 3.1", "content generation and decision support", ["content_generation"]),
        data_categories=["user prompts", "documents"], license="Llama 3.1 Community License",
        model_card_url="https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_1/",
        security_assessment=True, evaluated_date="2025-01-15", cross_border_transfer=False,
    ))
    generator.add_model(ModelComponent(
        name="llama3.1:8b (High Protection Mode)", version="3.1-8b", supplier="Meta",
        jurisdiction="US/local air-gapped", purpose="content generation and decision support",
        risk_tier=_tier("Llama 3.1", "content generation and decision support", ["content_generation"]),
        data_categories=["high-protection user prompts", "sensitive documents"], license="Llama 3.1 Community License",
        model_card_url="https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_1/",
        security_assessment=True, evaluated_date="2025-01-15", cross_border_transfer=False,
    ))
    generator.add_model(ModelComponent(
        name="anthropic/claude-sonnet-4", version="sonnet-4", supplier="Anthropic", jurisdiction="US",
        purpose="client-selected content generation and decision support",
        risk_tier=_tier("Claude Sonnet 4", "client-selected content generation", ["content_generation"]),
        data_categories=["client prompts", "client documents"], model_card_url="https://www.anthropic.com/claude",
        security_assessment=False, evaluated_date=None, cross_border_transfer=True,
    ))
    generator.add_model(ModelComponent(
        name="openai/gpt-5.6-luna", version="5.6-luna", supplier="OpenAI", jurisdiction="US",
        purpose="external content generation and decision support",
        risk_tier=_tier("GPT-5.6-Luna", "external content generation", ["content_generation"]),
        data_categories=["user prompts", "documents"], model_card_url="https://openai.com/",
        security_assessment=False, evaluated_date=None, cross_border_transfer=True,
    ))
    generator.add_model(ModelComponent(
        name="Ed25519 watermarking", version="local", supplier="Cortex Leman", jurisdiction="local",
        purpose="local output watermarking", risk_tier="minimal", data_categories=["generated output metadata"],
        license="MIT", security_assessment=True, evaluated_date="2025-01-20", cross_border_transfer=False,
    ))
    generator.add_model(ModelComponent(
        name="Chandra OCR 2", version="2", supplier="Datalab", jurisdiction="US",
        purpose="document text extraction", risk_tier="minimal", data_categories=["document images", "extracted text"],
        model_card_url="https://www.datalab.to/", security_assessment=False, cross_border_transfer=True,
    ))
    generator.add_model(ModelComponent(
        name="text-embedding", version="provider-or-local", supplier="OpenRouter / local runtime",
        jurisdiction="FR/EU or local", purpose="semantic search and retrieval", risk_tier="minimal",
        data_categories=["document text", "search queries", "vector representations"],
        security_assessment=False, cross_border_transfer=True,
    ))
    generator.add_data_flow("mistralai/mistral-small-3.1-24b-instruct", "Ed25519 watermarking", "Generated responses are locally watermarked", ["generated text"])
    generator.add_data_flow("Chandra OCR 2", "mistralai/mistral-small-3.1-24b-instruct", "Extracted text may be supplied to the primary model", ["document images", "extracted text"])
    return generator.generate()


def get_cortex_sbom_markdown() -> str:
    generator = AISBOMGenerator()
    sbom = get_cortex_sbom()
    for component in sbom.get("components", []):
        properties = {item["name"]: item.get("value") for item in component.get("properties", [])}
        generator.add_model(ModelComponent(
            name=component["name"], version=component["version"], supplier=component["supplier"]["name"],
            jurisdiction=properties.get("ai:jurisdiction", "unknown"), purpose=properties.get("ai:purpose", "unknown"),
            risk_tier=properties.get("ai:risk-tier", "minimal"),
            data_categories=[item["value"] for item in component.get("properties", []) if item.get("name") == "ai:data-category"],
            license=(component.get("licenses", [{}])[0].get("license", {}).get("name") if component.get("licenses") else None),
            model_card_url=(component.get("externalReferences", [{}])[0].get("url") if component.get("externalReferences") else None),
            security_assessment=bool(properties.get("ai:security-assessment", False)),
            evaluated_date=properties.get("ai:evaluated-date"),
            cross_border_transfer=bool(properties.get("ai:cross-border-transfer", False)),
        ))
    return generator.generate_markdown()
