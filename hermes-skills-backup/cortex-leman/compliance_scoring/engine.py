"""
Compliance Engine v5 — Main evaluation engine for Cortex Leman.

This is the primary entry point for running compliance audits.
It replaces the old score.py while maintaining API compatibility.

Usage:
    from compliance_scoring import ComplianceEngine

    engine = ComplianceEngine()
    result = engine.run_audit(audit_input)
    print(result.to_dict())
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .models import (
    AuditInput,
    AuditResult,
    ChecklistResponse,
    ClassificationLevel,
    Citation,
    ColorCode,
    CriteriaDomain,
    DomainScore,
    KillSwitchResult,
    Violation,
)
from .criteria import ALL_DOMAINS, RGPD_DOMAINS, AI_ACT_DOMAINS, LPD_CH_DOMAINS
from .scoring.evaluator import evaluate_all_domains
from .scoring.weights import get_regulation_weights, normalize_weights
from .scoring.thresholds import classify, worst_domain_color, COLOR_MAP


# Domain-to-regulation mapping
_REGULATION_DOMAINS = {
    "RGPD": RGPD_DOMAINS,
    "AI_ACT": AI_ACT_DOMAINS,
    "LPD_CH": LPD_CH_DOMAINS,
}


class ComplianceEngine:
    """
    Deterministic compliance scoring engine.

    Covers RGPD (10 domains), AI Act (6 domains), LPD/CH (4 domains).
    All scoring is based on checklist responses — no LLM involvement.

    The engine produces:
    - Global score (0.0-1.0)
    - Per-domain scores
    - Classification (VERT/ORANGE_CLAIR/ORANGE_FONCE/ROUGE)
    - Traceable citations for every finding
    - Kill switch evaluation
    - Actionable recommendations
    """

    def __init__(self, custom_domains: Optional[List[CriteriaDomain]] = None):
        """
        Initialize engine with criteria domains.

        Args:
            custom_domains: Optional override for default criteria domains.
                           If provided, replaces ALL_DOMAINS.
        """
        self.domains = custom_domains or ALL_DOMAINS
        self._domain_map = {d.id: d for d in self.domains}

    def run_audit(
        self,
        audit_input: AuditInput,
        audit_id: Optional[str] = None,
    ) -> AuditResult:
        """
        Run a full compliance audit.

        Args:
            audit_input: Audit input with client info, sector, jurisdiction, and responses
            audit_id: Optional audit ID. Auto-generated if not provided.

        Returns:
            Complete AuditResult with scores, violations, citations, and recommendations
        """
        audit_id = audit_id or str(uuid.uuid4())[:8]
        timestamp = datetime.now(timezone.utc).isoformat()

        # Step 1: Get regulation weights based on sector and jurisdiction
        regulation_weights = get_regulation_weights(audit_input.sector, audit_input.jurisdiction)

        # Step 2: Evaluate all domains
        domain_scores = evaluate_all_domains(self.domains, audit_input.responses)

        # Step 3: Calculate regulation-level scores
        regulation_scores: Dict[str, float] = {}
        for reg_name, domains in _REGULATION_DOMAINS.items():
            reg_domain_scores = [ds for ds in domain_scores if ds.domain_id in {d.id for d in domains}]
            if reg_domain_scores:
                regulation_scores[reg_name] = (
                    sum(ds.score for ds in reg_domain_scores) / len(reg_domain_scores)
                )
            else:
                regulation_scores[reg_name] = 0.0

        # Step 4: Calculate global weighted score
        global_score = sum(
            regulation_scores.get(reg, 0.0) * weight
            for reg, weight in regulation_weights.items()
            if weight > 0
        )
        global_score = min(1.0, max(0.0, global_score))

        # Step 5: Classification
        classification, color = classify(global_score)

        # Step 6: Kill switch check
        kill_switch = self._evaluate_kill_switch(domain_scores)

        # Step 7: Collect all violations and citations
        all_violations: List[Violation] = []
        all_citations: List[Citation] = []
        for ds in domain_scores:
            all_violations.extend(ds.violations)
            all_citations.extend(ds.citations)

        # Step 8: Generate recommendations
        recommendations = self._generate_recommendations(
            domain_scores, all_violations, classification
        )

        # Step 9: Determine attestation eligibility
        attestation_eligible = (
            classification == ClassificationLevel.PLEINEMENT_CONFORME
            and not kill_switch.activated
            and len(all_violations) == 0
        )

        return AuditResult(
            audit_id=audit_id,
            timestamp=timestamp,
            global_score=global_score,
            classification=classification,
            color=color,
            domain_scores=domain_scores,
            all_violations=all_violations,
            kill_switch=kill_switch,
            recommendations=recommendations,
            citations=all_citations,
            attestation_eligible=attestation_eligible,
            regulation_weights=regulation_weights,
            metadata={
                "client_id": audit_input.client_id,
                "sector": audit_input.sector,
                "jurisdiction": audit_input.jurisdiction,
                "total_checklist_items": sum(ds.total_items for ds in domain_scores),
                "answered_items": sum(ds.answered_items for ds in domain_scores),
                "completion_rate": (
                    sum(ds.answered_items for ds in domain_scores)
                    / max(1, sum(ds.total_items for ds in domain_scores))
                ),
            },
        )

    def _evaluate_kill_switch(self, domain_scores: List[DomainScore]) -> KillSwitchResult:
        """
        Evaluate kill switch conditions.

        Kill switch activates if:
        - Any domain score < 0.25
        - Any critical violation detected
        """
        # Check domain scores (only for evaluated domains)
        for ds in domain_scores:
            if ds.answered_items == 0:
                continue  # Skip unevaluated domains
            if ds.score < 0.25:
                critical_violations = [v for v in ds.violations if v.severity == "critical"]
                return KillSwitchResult(
                    activated=True,
                    reason=f"Domaine '{ds.domain_name}' ({ds.domain_id}) score = {ds.score:.2f} < 0.25",
                    domain_id=ds.domain_id,
                    violations=critical_violations,
                )

        # Check for critical violations
        for ds in domain_scores:
            critical_violations = [v for v in ds.violations if v.severity == "critical"]
            if critical_violations:
                return KillSwitchResult(
                    activated=True,
                    reason=f"Violation critique détectée dans '{ds.domain_name}' : {critical_violations[0].description}",
                    domain_id=ds.domain_id,
                    violations=critical_violations,
                )

        return KillSwitchResult(activated=False)

    def _generate_recommendations(
        self,
        domain_scores: List[DomainScore],
        all_violations: List[Violation],
        classification: ClassificationLevel,
    ) -> List[str]:
        """Generate actionable recommendations prioritized by severity."""
        recommendations: List[str] = []

        # Kill switch recommendations first
        critical_domains = [ds for ds in domain_scores if ds.score < 0.50]
        for ds in critical_domains:
            recommendations.append(
                f"🔴 CRITIQUE : Le domaine '{ds.domain_name}' nécessite une action immédiate (score {ds.score:.2f})."
            )

        # Critical violations
        for v in all_violations:
            if v.severity == "critical":
                recommendations.append(f"🔴 {v.recommendation}")

        # Major violations
        for v in all_violations:
            if v.severity == "major":
                recommendations.append(f"🟠 {v.recommendation}")

        # Minor violations
        for v in all_violations:
            if v.severity == "minor":
                recommendations.append(f"🟡 {v.recommendation}")

        # General classification-based recommendation
        if classification == ClassificationLevel.PLEINEMENT_CONFORME:
            recommendations.append("✅ Conformité atteinte. Maintenir les mesures en place et réaliser des audits périodiques.")
        elif classification == ClassificationLevel.LARGEMENT_CONFORME:
            recommendations.append("🟡 Largement conforme. Corriger les violations mineures pour atteindre le niveau Pleinement Conforme.")
        elif classification == ClassificationLevel.PARTIELLEMENT_CONFORME:
            recommendations.append("🟠 Partiellement conforme. Établir un plan d'action avec délais et responsables pour chaque violation majeure.")
        else:
            recommendations.append("🔴 Non conforme. Action immédiate requise. Prioriser les violations critiques et documenter un plan de mise en conformité.")

        # Deduplicate while preserving order
        seen = set()
        deduped: List[str] = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                deduped.append(rec)
        return deduped

    # =========================================================================
    # API compatible with old score.py (backward compatibility)
    # =========================================================================

    def generate_score_report(
        self,
        criteria_results: Dict,
        sector: str = "other",
    ) -> Dict:
        """
        Legacy API — generates a score report from old-style criteria_results.

        This method provides backward compatibility with the old score.py API.
        For new code, use run_audit() with AuditInput instead.

        Args:
            criteria_results: Old-style dict with domain keys and score/violation values
            sector: Industry sector

        Returns:
            Dict compatible with old score.py output format
        """
        # Convert old format to new AuditInput
        responses: Dict[str, ChecklistResponse] = {}
        for domain_key, domain_data in criteria_results.items():
            score = domain_data.get("score", 0.0)
            violations = domain_data.get("violations", [])
            # Create a synthetic response
            # Sanitize key to prevent ID injection
            safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', str(domain_key))
            responses[f"legacy.{safe_key}.q1"] = ChecklistResponse(
                item_id=f"legacy.{domain_key}.q1",
                score=score,
                evidence="legacy",
            )

        audit_input = AuditInput(
            client_id="legacy",
            sector=sector,
            jurisdiction="FR",
            responses=responses,
        )

        result = self.run_audit(audit_input)

        # Return old-compatible format
        return {
            "global_score": result.global_score,
            "classification": {
                "level": result.classification.value,
                "color": result.color.value,
                "action_required": result.classification != ClassificationLevel.PLEINEMENT_CONFORME,
                "attestation_eligible": result.attestation_eligible,
            },
            "criteria_details": [ds.to_dict() for ds in result.domain_scores],
            "recommendations": result.recommendations,
            "critical_violations": [
                {"criteria": v.criterion_id, "violation": v.description, "severity": v.severity, "reference": v.regulation}
                for v in result.all_violations if v.severity == "critical"
            ],
            "attestation_eligible": result.attestation_eligible,
            "regulation_weights": result.regulation_weights,
            "kill_switch": {
                "activated": result.kill_switch.activated,
                "reason": result.kill_switch.reason,
            },
        }

    def get_all_checklist_items(self) -> List[Dict]:
        """
        Get all checklist items across all domains.

        Returns:
            List of dicts with id, question, domain, regulation, article, is_mandatory, severity
        """
        items = []
        for domain in self.domains:
            for criterion in domain.criteria:
                for item in criterion.checklist:
                    items.append({
                        "id": item.id,
                        "question": item.question,
                        "domain_id": domain.id,
                        "domain_name": domain.name,
                        "regulation": domain.regulation,
                        "article_id": criterion.article_id,
                        "article_title": criterion.title,
                        "is_mandatory": item.is_mandatory,
                        "severity": item.severity,
                    })
        return items

    def get_domains_summary(self) -> Dict:
        """Get summary of all domains and their criteria counts."""
        return {
            "total_domains": len(self.domains),
            "total_criteria": sum(d.total_criteria for d in self.domains),
            "total_checklist_items": sum(d.total_checklist_items for d in self.domains),
            "domains": [
                {
                    "id": d.id,
                    "name": d.name,
                    "regulation": d.regulation,
                    "chapter": d.chapter,
                    "criteria_count": d.total_criteria,
                    "checklist_items": d.total_checklist_items,
                }
                for d in self.domains
            ],
        }
