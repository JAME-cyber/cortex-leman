"""
Cortex Leman Compliance Scoring Engine v5
Covers: RGPD (99 articles), AI Act (18 articles), LPD/CH (10 articles)
Deterministic scoring — no LLM involvement in score calculation.
"""

from .engine import ComplianceEngine
from .models import (
    Citation,
    Criterion,
    CriteriaDomain,
    AuditInput,
    AuditResult,
    DomainScore,
    ClassificationLevel,
    ColorCode,
)

__version__ = "5.0.0"
__all__ = [
    "ComplianceEngine",
    "Citation",
    "Criterion",
    "CriteriaDomain",
    "AuditInput",
    "AuditResult",
    "DomainScore",
    "ClassificationLevel",
    "ColorCode",
]
