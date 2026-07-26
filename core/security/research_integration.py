from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Mapping, Sequence


LOGGER = logging.getLogger("cortex_leman.security.research")

PAPER_REFERENCES = {
    "trust_certification": "arXiv:2607.15992",
    "trustworthy_ai_tools": "arXiv:2607.15480",
    "channelguard": "arXiv:2607.19430",
    "agentic_ai_regulation": "arXiv:2607.21345",
    "phantomseal": "arXiv:2607.20564",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "present", "valid", "complete"}
    return bool(value)


@dataclass(frozen=True)
class TrustCertificate:
    system_id: str
    level: str
    score: int
    dimension_scores: dict[str, int]
    expiry_date: datetime
    recommendations: list[str]
    issued_at: datetime
    paper_ref: str


class TrustCertificationEngine:
    DIMENSIONS = ("reliability", "safety", "fairness", "transparency", "security")

    def certify(self, system_id: str, metrics: Mapping[str, Any]) -> TrustCertificate:
        if not isinstance(system_id, str) or not system_id.strip():
            raise ValueError("system_id must be a non-empty string")
        scores: dict[str, int] = {}
        for dimension in self.DIMENSIONS:
            if dimension not in metrics:
                raise ValueError(f"missing certification metric: {dimension}")
            value = metrics[dimension]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{dimension} must be numeric")
            if not 0 <= value <= 20:
                raise ValueError(f"{dimension} must be between 0 and 20")
            scores[dimension] = int(round(value))
        score = sum(scores.values())
        if score < 60:
            level = "Bronze"
        elif score < 75:
            level = "Silver"
        elif score < 90:
            level = "Gold"
        else:
            level = "Platinum"
        recommendations = [
            f"Improve {name} controls (current score: {value}/20)."
            for name, value in scores.items() if value < 16
        ]
        if not recommendations:
            recommendations.append("Maintain continuous monitoring and annual reassessment.")
        issued = _utcnow()
        return TrustCertificate(
            system_id=system_id,
            level=level,
            score=score,
            dimension_scores=scores,
            expiry_date=issued + timedelta(days=365),
            recommendations=recommendations,
            issued_at=issued,
            paper_ref=PAPER_REFERENCES["trust_certification"],
        )


@dataclass(frozen=True)
class GapFinding:
    severity: str
    gap_name: str
    evidence: str
    remediation: str
    paper_reference: str


@dataclass(frozen=True)
class GapReport:
    overall_coverage_pct: float
    gaps: list[GapFinding]
    strengths: list[str]


class ComplianceGapScanner:
    GAP_RULES = {
        "explainability_depth": (
            ("explainability", "explanations", "explainability_depth"),
            "Provide meaningful, user- and auditor-facing explanations with depth appropriate to risk.",
        ),
        "digital_security": (
            ("security", "cybersecurity", "digital_security", "security_controls"),
            "Implement documented security controls, threat modeling, monitoring, and incident response.",
        ),
        "design_phase": (
            ("design_review", "risk_assessment", "lifecycle_governance", "design_phase"),
            "Introduce risk, human-oversight, and accountability controls during system design.",
        ),
        "data_phase": (
            ("data_governance", "data_quality", "privacy", "data_phase"),
            "Document data lineage, quality, privacy, representativeness, and retention controls.",
        ),
    }

    def scan(self, system_config: dict) -> GapReport:
        if not isinstance(system_config, dict):
            raise TypeError("system_config must be a dict")
        normalized = {str(k).lower(): v for k, v in system_config.items()}
        gaps: list[GapFinding] = []
        strengths: list[str] = []
        covered = 0
        for gap_name, (keys, remediation) in self.GAP_RULES.items():
            matched = [key for key in keys if key in normalized]
            present = any(_as_bool(normalized[key]) for key in matched)
            if present:
                covered += 1
                strengths.append(f"{gap_name} controls are represented in configuration.")
            else:
                severity = "high" if gap_name in {"digital_security", "data_phase"} else "medium"
                evidence = (
                    f"No affirmative control found; checked keys: {', '.join(keys)}."
                    if not matched else f"Configured values for {', '.join(matched)} do not indicate coverage."
                )
                gaps.append(GapFinding(
                    severity=severity,
                    gap_name=gap_name,
                    evidence=evidence,
                    remediation=remediation,
                    paper_reference=PAPER_REFERENCES["trustworthy_ai_tools"],
                ))
        return GapReport(round(covered / len(self.GAP_RULES) * 100, 2), gaps, strengths)


@dataclass(frozen=True)
class CompositionFinding:
    finding_type: str
    severity: str
    evidence: str
    remediation: str


@dataclass(frozen=True)
class CompositionReport:
    findings: list[CompositionFinding]
    composite_security_score: float
    systemic_risks: list[str]


class SystemSecurityCompositor:
    def audit_composition(self, agents: list[dict], interactions: list[dict]) -> CompositionReport:
        if not isinstance(agents, list) or not isinstance(interactions, list):
            raise TypeError("agents and interactions must be lists")
        findings: list[CompositionFinding] = []
        risks: list[str] = []
        by_id = {str(a.get("id", a.get("agent_id", i))): a for i, a in enumerate(agents)}
        edges = []
        for interaction in interactions:
            source = str(interaction.get("source", interaction.get("from", "")))
            target = str(interaction.get("target", interaction.get("to", "")))
            edges.append((source, target, interaction))
            authenticated = interaction.get("authenticated", interaction.get("auth", False))
            if not _as_bool(authenticated):
                findings.append(CompositionFinding("unauthenticated_channels", "high", f"Channel {source}->{target} lacks authentication.", "Require mutually authenticated, authorized channels."))
        for source, target, interaction in edges:
            source_cfg, target_cfg = by_id.get(source, {}), by_id.get(target, {})
            source_priv = set(source_cfg.get("privileges", source_cfg.get("permissions", [])) or [])
            target_priv = set(target_cfg.get("privileges", target_cfg.get("permissions", [])) or [])
            granted = set(interaction.get("grants", interaction.get("permissions", [])) or [])
            if granted and not granted.issubset(source_priv | target_priv):
                findings.append(CompositionFinding("privilege_escalation", "critical", f"{source}->{target} grants privileges outside declared sets.", "Enforce least privilege and validate delegated capabilities."))
            if source and target and source != target and target in by_id:
                for reverse_source, reverse_target, _ in edges:
                    if reverse_source == target and reverse_target == source:
                        findings.append(CompositionFinding("trust_transitivity", "high", f"Bidirectional trust path detected between {source} and {target}.", "Use explicit trust boundaries and non-transitive authorization."))
                        break
        graph = {source: target for source, target, _ in edges if source and target}
        for start in graph:
            seen: set[str] = set()
            current = start
            while current in graph and current not in seen:
                seen.add(current)
                current = graph[current]
            if current == start and seen:
                findings.append(CompositionFinding("data_flow_loops", "high", f"Data-flow cycle detected from {start}.", "Break cycles or add bounded, audited data-flow controls."))
                break
        unique: dict[tuple[str, str], CompositionFinding] = {(f.finding_type, f.evidence): f for f in findings}
        findings = list(unique.values())
        if findings:
            risks = sorted({f.finding_type for f in findings})
        penalty = sum({"critical": 30, "high": 20, "medium": 10, "low": 5}.get(f.severity, 10) for f in findings)
        score = round(max(0.0, 100.0 - penalty), 2)
        return CompositionReport(findings, score, risks)


@dataclass(frozen=True)
class AgentClassification:
    level: int
    action_space: str
    ai_act_obligations: list[str]
    ai_act_articles: list[str]
    requires_dpia: bool


class AgentGovernanceRules:
    def classify_agent(self, agent_config: dict) -> AgentClassification:
        if not isinstance(agent_config, dict):
            raise TypeError("agent_config must be a dict")
        explicit = agent_config.get("level")
        if explicit is not None:
            level = int(explicit)
        else:
            autonomy = float(agent_config.get("autonomy", agent_config.get("autonomy_score", 0)))
            impact = float(agent_config.get("impact", agent_config.get("risk", 0)))
            level = min(5, max(0, round((autonomy + impact) / 2)))
        if not 0 <= level <= 5:
            raise ValueError("agent level must be between 0 and 5")
        action_space = "minimal" if level <= 1 else "bounded" if level <= 3 else "broad_autonomous"
        articles: list[str] = []
        obligations: list[str] = []
        dpia = level >= 4
        if level >= 2:
            articles = ["Article 50", "Article 14"]
            obligations = ["transparency and disclosure", "effective human oversight"]
        if level >= 4:
            articles = [f"Article {n}" for n in range(9, 16)]
            obligations = ["risk management", "data governance", "technical documentation", "logging", "transparency", "human oversight", "accuracy, robustness, and cybersecurity", "DPIA"]
        return AgentClassification(level, action_space, obligations, articles, dpia)


@dataclass(frozen=True)
class SyntheticDetection:
    detected: bool
    confidence: float
    markers: list[str]


@dataclass(frozen=True)
class AuthenticityScore:
    score: int
    watermark_detected: bool
    signature_valid: bool
    provenance_complete: bool
    metadata_consistent: bool
    risk_level: str


class MediaAuthenticityScorer:
    def score_media(self, media_metadata: dict) -> AuthenticityScore:
        if not isinstance(media_metadata, dict):
            raise TypeError("media_metadata must be a dict")
        watermark = _as_bool(media_metadata.get("watermark_detected", media_metadata.get("watermark", False)))
        signature = _as_bool(media_metadata.get("signature_valid", media_metadata.get("signature", False)))
        provenance = _as_bool(media_metadata.get("provenance_complete", media_metadata.get("provenance", False)))
        consistent = _as_bool(media_metadata.get("metadata_consistent", media_metadata.get("consistent", False)))
        score = round((watermark * 25) + (signature * 30) + (provenance * 25) + (consistent * 20))
        risk = "low" if score >= 75 else "medium" if score >= 45 else "high"
        return AuthenticityScore(score, watermark, signature, provenance, consistent, risk)

    def detect_synthetic_markers(self, text: str) -> SyntheticDetection:
        """Detect synthetic content markers including ChainMark watermarks.

        Integrates with ChainMarkWatermarker (TICKET-022) for machine-readable
        watermark detection per PhantomSeal (arXiv:2607.20564).
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        markers: list[str] = []

        # Layer 1: ChainMark watermark detection (machine-readable, Art. 50)
        try:
            from core.security.watermarker import ChainMarkWatermarker
            wm = ChainMarkWatermarker()
            detection = wm.detect(text)
            if detection.is_watermarked:
                markers.append(f"chainmark_watermark (valid={detection.watermark_valid})")
        except Exception:
            pass  # Watermarker not available — fall through to heuristic

        # Layer 2: Visible markers (heuristic)
        lowered = text.lower()
        marker_terms = ("ai-generated", "synthetic media", "deepfake", "generated by", "watermark")
        markers.extend(term for term in marker_terms if term in lowered)

        confidence = min(1.0, 0.3 * len(markers))
        return SyntheticDetection(bool(markers), confidence, markers)
