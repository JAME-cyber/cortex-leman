"""
Domain evaluation logic.

Evaluates checklist responses against criteria within a domain.
Produces a DomainScore with violations, citations, and a weighted score.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from ..models import (
    ChecklistResponse,
    Citation,
    CriteriaDomain,
    Criterion,
    DomainScore,
    Violation,
)
from .thresholds import classify_domain


def evaluate_domain(
    domain: CriteriaDomain,
    responses: Dict[str, ChecklistResponse],
) -> DomainScore:
    """
    Evaluate a single domain based on checklist responses.

    For each criterion in the domain:
    1. Collect matching responses by checklist item id
    2. Calculate criterion score as mean of response scores
    3. Check threshold compliance
    4. Generate violations for non-compliant items
    5. Collect citations

    The domain score is the weighted average of criterion scores,
    where weights are normalized within the domain.

    Args:
        domain: CriteriaDomain with criteria and their checklists
        responses: Dict of checklist item id -> ChecklistResponse

    Returns:
        DomainScore with score, violations, and citations
    """
    criterion_scores: List[float] = []
    criterion_weights: List[float] = []
    all_violations: List[Violation] = []
    all_citations: List[Citation] = []
    total_items = 0
    answered_items = 0

    for criterion in domain.criteria:
        # Gather responses for this criterion's checklist items
        item_ids = [item.id for item in criterion.checklist]
        matched_responses: List[ChecklistResponse] = []
        for iid in item_ids:
            if iid in responses:
                matched_responses.append(responses[iid])
                answered_items += 1
            total_items += 1

        # Calculate criterion score
        if matched_responses:
            criterion_score = sum(r.score for r in matched_responses) / len(matched_responses)
        else:
            # No responses = None (unanswered, excluded from scoring)
            criterion_score = None

        criterion_scores.append(criterion_score)
        criterion_weights.append(criterion.weight)

        # Generate violations only for criteria with responses
        # Unanswered criteria are already excluded from scoring (None)
        if matched_responses:
            violations = _generate_violations(criterion, matched_responses, item_ids)
            all_violations.extend(violations)

        # Collect citations from criterion
        all_citations.extend(criterion.citations)

    # Calculate weighted domain score
    domain_score = _weighted_average(criterion_scores, criterion_weights)
    answered_scores = [s for s in criterion_scores if s is not None]
    raw_score = sum(answered_scores) / len(answered_scores) if answered_scores else 0.0

    return DomainScore(
        domain_id=domain.id,
        domain_name=domain.name,
        regulation=domain.regulation,
        score=domain_score,
        raw_score=raw_score,
        total_items=total_items,
        answered_items=answered_items,
        violations=all_violations,
        citations=all_citations,
    )


def _weighted_average(values: List[float], weights: List[float]) -> float:
    """Calculate weighted average, handling None values and zero total weight.
    
    None values (unanswered criteria) are excluded from the calculation.
    If all values are None, returns 0.0.
    """
    filtered = [(v, w) for v, w in zip(values, weights) if v is not None]
    if not filtered:
        return 0.0
    total_weight = sum(w for _, w in filtered)
    if total_weight == 0:
        return sum(v for v, _ in filtered) / len(filtered)
    weighted_sum = sum(v * w for v, w in filtered)
    return weighted_sum / total_weight


def _generate_violations(
    criterion: Criterion,
    responses: List[ChecklistResponse],
    item_ids: List[str],
) -> List[Violation]:
    """Generate violations for non-compliant checklist items."""
    violations: List[Violation] = []

    for response in responses:
        item = next(
            (ci for ci in criterion.checklist if ci.id == response.item_id),
            None,
        )
        if item is None:
            continue

        severity = "minor"
        if response.score < 0.3:
            severity = "critical"
        elif response.score < 0.6:
            severity = "major"

        # Determine if this is a violation (score below threshold or critical)
        is_violation = response.score < criterion.threshold * 0.6 or severity == "critical"

        if is_violation:
            violations.append(Violation(
                criterion_id=criterion.article_id,
                article_id=criterion.article_id,
                regulation=criterion.citations[0].source if criterion.citations else "UNKNOWN",
                severity=severity,
                description=f"{item.question} — Score: {response.score:.2f} (seuil: {criterion.threshold:.2f})",
                recommendation=_recommendation_for(severity, item.question),
                citations=criterion.citations,
            ))

    # Also flag unanswered mandatory items
    responded_ids = {r.item_id for r in responses}
    for iid in item_ids:
        if iid not in responded_ids:
            item = next((ci for ci in criterion.checklist if ci.id == iid), None)
            if item and item.is_mandatory:
                violations.append(Violation(
                    criterion_id=criterion.article_id,
                    article_id=criterion.article_id,
                    regulation=criterion.citations[0].source if criterion.citations else "UNKNOWN",
                    severity="major",
                    description=f"Non répondu (obligatoire): {item.question}",
                    recommendation="Répondre à cette question pour compléter l'audit.",
                    citations=criterion.citations,
                ))

    return violations


def _recommendation_for(severity: str, question: str) -> str:
    """Generate a contextual recommendation based on severity."""
    if severity == "critical":
        return f"Action immédiate requise : {question}"
    elif severity == "major":
        return f"Plan de correction nécessaire : {question}"
    else:
        return f"Amélioration recommandée : {question}"


def evaluate_all_domains(
    domains: List[CriteriaDomain],
    responses: Dict[str, ChecklistResponse],
) -> List[DomainScore]:
    """
    Evaluate all domains.

    Args:
        domains: List of CriteriaDomain objects
        responses: Dict of checklist item id -> ChecklistResponse

    Returns:
        List of DomainScore objects
    """
    return [evaluate_domain(d, responses) for d in domains]
