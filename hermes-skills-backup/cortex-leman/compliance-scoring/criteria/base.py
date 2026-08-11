"""
Base factory functions for CriteriaDomain and Criterion construction.

These are the single point of truth for building criteria objects.
All criteria files (rgpd.py, ai_act.py, lpd_ch.py) must use these builders.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from ..models import (
    ChecklistItem,
    Citation,
    Criterion,
    CriteriaDomain,
)


def build_citation(
    source: str,
    article_id: str,
    article_title: str,
    excerpt: str,
    url: str = "",
    relevance: float = 1.0,
) -> Citation:
    """Build a Citation with validation."""
    if not source:
        raise ValueError("Citation source is required")
    if not article_id:
        raise ValueError("Citation article_id is required")
    if not excerpt:
        raise ValueError("Citation excerpt is required")
    if not 0.0 <= relevance <= 1.0:
        raise ValueError("Citation relevance must be between 0.0 and 1.0")
    return Citation(
        source=source,
        article_id=article_id,
        article_title=article_title,
        excerpt=excerpt,
        url=url,
        relevance=relevance,
    )


def build_checklist_item(
    criterion_id: str,
    index: int,
    question: str,
    is_mandatory: bool = True,
    severity: str = "major",
) -> ChecklistItem:
    """Build a ChecklistItem with auto-generated id."""
    item_id = f"{criterion_id}.q{index}"
    if not question:
        raise ValueError(f"Checklist question cannot be empty for {item_id}")
    return ChecklistItem(
        id=item_id,
        question=question,
        is_mandatory=is_mandatory,
        severity=severity,
    )


def build_criterion(
    article_id: str,
    title: str,
    text: str,
    threshold: float = 0.6,
    weight: float = 1.0,
    checklist_questions: Optional[List[Dict]] = None,
    evidence_types: Optional[List[str]] = None,
    citations: Optional[List[Citation]] = None,
) -> Criterion:
    """
    Build a Criterion with auto-generated checklist items.

    Args:
        article_id: Unique id, e.g. "RGPD.5.1"
        title: Short title of the article
        text: Abridged original legal text
        threshold: Minimum score for compliance (default 0.6)
        weight: Weight within domain (will be normalized later)
        checklist_questions: List of dicts with keys:
            - question (str, required)
            - is_mandatory (bool, default True)
            - severity (str, default "major")
        evidence_types: List of accepted evidence types
        citations: List of Citation objects

    Returns:
        Frozen Criterion dataclass
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"Threshold must be 0.0-1.0 for {article_id}")

    checklist: List[ChecklistItem] = []
    if checklist_questions:
        for i, q_data in enumerate(checklist_questions, 1):
            item = build_checklist_item(
                criterion_id=article_id,
                index=i,
                question=q_data.get("question", ""),
                is_mandatory=q_data.get("is_mandatory", True),
                severity=q_data.get("severity", "major"),
            )
            checklist.append(item)

    return Criterion(
        article_id=article_id,
        title=title,
        text=text,
        threshold=threshold,
        weight=weight,
        checklist=checklist,
        evidence_types=evidence_types or [],
        citations=citations or [],
    )


def build_domain(
    domain_id: str,
    name: str,
    regulation: str,
    chapter: str,
    default_weight: float,
    criteria: List[Criterion],
) -> CriteriaDomain:
    """Build a CriteriaDomain with weight normalization."""
    if not criteria:
        raise ValueError(f"Domain {domain_id} must have at least one criterion")
    if default_weight <= 0:
        raise ValueError(f"Domain {domain_id} weight must be positive")

    return CriteriaDomain(
        id=domain_id,
        name=name,
        regulation=regulation,
        chapter=chapter,
        default_weight=default_weight,
        criteria=criteria,
    )
