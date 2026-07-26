from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Any, Optional


@dataclass
class ModelComponent:
    name: str
    version: str
    supplier: str
    jurisdiction: str
    purpose: str
    risk_tier: str
    data_categories: list[str] = field(default_factory=list)
    license: Optional[str] = None
    model_card_url: Optional[str] = None
    security_assessment: bool = False
    evaluated_date: Optional[str] = None
    cross_border_transfer: bool = False

    def __post_init__(self) -> None:
        valid_tiers = {"minimal", "limited", "high", "unacceptable"}
        if self.risk_tier not in valid_tiers:
            raise ValueError(f"Invalid AI Act risk tier: {self.risk_tier}")
        if not self.name.strip() or not self.version.strip():
            raise ValueError("Model name and version are required")
        if not self.supplier.strip() or not self.jurisdiction.strip():
            raise ValueError("Supplier and jurisdiction are required")


class AIActRiskTier:
    @staticmethod
    def classify_model(name: str, purpose: str, capabilities: list[str] | tuple[str, ...] | set[str]) -> str:
        text = " ".join([name, purpose, *[str(value) for value in capabilities]]).lower()
        if any(token in text for token in ("social_scoring", "social scoring", "social-scoring")):
            return "unacceptable"
        if any(token in text for token in ("automated_decision", "automated decision", "automatic decision")):
            return "high"
        if any(token in text for token in ("biometric", "face recognition", "emotion recognition")):
            return "high"
        if any(token in text for token in ("content_generation", "content generation", "generative")):
            return "limited"
        if any(token in text for token in ("decision_support", "decision support", "recommendation")):
            return "limited"
        return "minimal"


class AISBOMGenerator:
    def __init__(self) -> None:
        self._models: list[ModelComponent] = []
        self._flows: list[dict[str, Any]] = []

    def add_model(self, component: ModelComponent) -> None:
        if not isinstance(component, ModelComponent):
            raise TypeError("component must be a ModelComponent")
        self._models.append(component)

    def add_data_flow(
        self,
        source: str,
        target: str,
        description: str,
        data_types: list[str] | tuple[str, ...],
    ) -> None:
        if not source or not target:
            raise ValueError("Data-flow source and target are required")
        self._flows.append({
            "source": source,
            "target": target,
            "description": description,
            "data_types": list(data_types),
        })

    @staticmethod
    def _slug(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "component"

    def _component_ref(self, component: ModelComponent, index: int) -> str:
        return f"urn:ai:model:{self._slug(component.name)}:{self._slug(component.version)}:{index}"

    def _references(self) -> dict[str, str]:
        return {
            component.name: self._component_ref(component, index)
            for index, component in enumerate(self._models, start=1)
        }

    def generate(self) -> dict[str, Any]:
        references = self._references()
        components: list[dict[str, Any]] = []
        for index, model in enumerate(self._models, start=1):
            properties: list[dict[str, Any]] = [
                {"name": "ai:jurisdiction", "value": model.jurisdiction},
                {"name": "ai:purpose", "value": model.purpose},
                {"name": "ai:risk-tier", "value": model.risk_tier},
                {"name": "ai:security-assessment", "value": model.security_assessment},
                {"name": "ai:cross-border-transfer", "value": model.cross_border_transfer},
                {"name": "ai:cross-border-legal-basis", "value": "RGPD Art. 44-49" if model.cross_border_transfer else "not-applicable"},
            ]
            if model.evaluated_date:
                properties.append({"name": "ai:evaluated-date", "value": model.evaluated_date})
            for category in model.data_categories:
                properties.append({"name": "ai:data-category", "value": category})

            component: dict[str, Any] = {
                "type": "machine-learning-model",
                "bom-ref": self._component_ref(model, index),
                "name": model.name,
                "version": model.version,
                "supplier": {"name": model.supplier},
                "properties": properties,
            }
            if model.license:
                component["licenses"] = [{"license": {"name": model.license}}]
            if model.model_card_url:
                component["externalReferences"] = [{"type": "website", "url": model.model_card_url}]
            components.append(component)

        dependencies: list[dict[str, Any]] = []
        for flow in self._flows:
            source_ref = references.get(flow["source"], f"urn:ai:system:{self._slug(flow['source'])}")
            target_ref = references.get(flow["target"], f"urn:ai:system:{self._slug(flow['target'])}")
            dependencies.append({"ref": source_ref, "dependsOn": [target_ref]})

        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "serialNumber": "urn:uuid:cortex-leman-ai-sbom",
            "version": 1,
            "metadata": {
                "timestamp": timestamp,
                "tools": [{"vendor": "Cortex Leman", "name": "AI SBOM Generator", "version": "5.0"}],
            },
            "components": components,
            "dependencies": dependencies,
        }

    def generate_markdown(self) -> str:
        lines = [
            "# Cortex Leman AI SBOM",
            "",
            "| Model | Version | Supplier | Jurisdiction | Purpose | Risk | Cross-border | Security assessment |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for model in self._models:
            lines.append(
                f"| {model.name} | {model.version} | {model.supplier} | {model.jurisdiction} | "
                f"{model.purpose} | {model.risk_tier} | {'yes' if model.cross_border_transfer else 'no'} | "
                f"{'yes' if model.security_assessment else 'no'} |"
            )
        lines.extend(["", f"Data flows: {len(self._flows)}", ""])
        for flow in self._flows:
            types = ", ".join(flow["data_types"]) or "unspecified"
            lines.append(f"- **{flow['source']} → {flow['target']}**: {flow['description']} ({types})")
        return "\n".join(lines)

    @staticmethod
    def _properties(component: dict[str, Any]) -> dict[str, Any]:
        return {item.get("name", ""): item.get("value") for item in component.get("properties", [])}

    def validate_ai_act_art11(self, sbom: dict[str, Any]) -> list[str]:
        gaps: list[str] = []
        components = sbom.get("components", [])
        if not components:
            return ["No AI model components are documented"]
        required = ("name", "version", "supplier")
        for component in components:
            label = component.get("name", "unnamed component")
            for field_name in required:
                if not component.get(field_name):
                    gaps.append(f"{label}: missing {field_name}")
            properties = self._properties(component)
            for field_name in ("ai:jurisdiction", "ai:purpose", "ai:risk-tier"):
                if not properties.get(field_name):
                    gaps.append(f"{label}: missing {field_name}")
            if "ai:data-category" not in properties:
                gaps.append(f"{label}: training or processing data categories are not documented")
            if not properties.get("ai:security-assessment", False):
                gaps.append(f"{label}: security assessment is missing or not confirmed")
            if not properties.get("ai:evaluated-date"):
                gaps.append(f"{label}: evaluation date is missing")
        if not sbom.get("metadata", {}).get("tools"):
            gaps.append("Metadata does not identify the SBOM generation tool")
        if not sbom.get("metadata", {}).get("timestamp"):
            gaps.append("Metadata timestamp is missing")
        return gaps

    def validate_ai_act_art13(self, sbom: dict[str, Any]) -> list[str]:
        gaps: list[str] = []
        components = sbom.get("components", [])
        if not components:
            return ["No models are available for transparency assessment"]
        for component in components:
            label = component.get("name", "unnamed component")
            properties = self._properties(component)
            for field_name in ("ai:purpose", "ai:risk-tier", "ai:jurisdiction"):
                if not properties.get(field_name):
                    gaps.append(f"{label}: missing transparency field {field_name}")
            if not component.get("externalReferences"):
                gaps.append(f"{label}: model card or public technical reference is missing")
            if "ai:cross-border-transfer" not in properties:
                gaps.append(f"{label}: cross-border data-transfer status is missing")
            if "ai:data-category" not in properties:
                gaps.append(f"{label}: data categories are not disclosed")
        return gaps
