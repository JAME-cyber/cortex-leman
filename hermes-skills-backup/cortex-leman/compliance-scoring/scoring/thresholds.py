"""
Classification thresholds for compliance scoring.

4-tier classification system:
  VERT          >= 0.85  : Fully compliant, attestation eligible
  ORANGE_CLAIR  >= 0.70  : Largely compliant, minor actions needed
  ORANGE_FONCE  >= 0.50  : Partially compliant, action plan required
  ROUGE          < 0.50  : Non-compliant, immediate actions required
"""

from ..models import ClassificationLevel, ColorCode, DomainScore

# Thresholds for global classification
CLASSIFICATION_THRESHOLDS = [
    (0.85, ClassificationLevel.PLEINEMENT_CONFORME, ColorCode.VERT),
    (0.70, ClassificationLevel.LARGEMENT_CONFORME, ColorCode.ORANGE_CLAIR),
    (0.50, ClassificationLevel.PARTIELLEMENT_CONFORME, ColorCode.ORANGE_FONCE),
    (0.00, ClassificationLevel.NON_CONFORME, ColorCode.ROUGE),
]

# Domain-level thresholds (slightly more lenient to avoid over-penalization)
DOMAIN_CLASSIFICATION_THRESHOLDS = [
    (0.80, ClassificationLevel.PLEINEMENT_CONFORME, ColorCode.VERT),
    (0.65, ClassificationLevel.LARGEMENT_CONFORME, ColorCode.ORANGE_CLAIR),
    (0.40, ClassificationLevel.PARTIELLEMENT_CONFORME, ColorCode.ORANGE_FONCE),
    (0.00, ClassificationLevel.NON_CONFORME, ColorCode.ROUGE),
]

# Color code ordering for severity
COLOR_SEVERITY = {
    ColorCode.ROUGE: 4,
    ColorCode.ORANGE_FONCE: 3,
    ColorCode.ORANGE_CLAIR: 2,
    ColorCode.VERT: 1,
}

# Human-readable color map
COLOR_MAP = {
    ColorCode.VERT: "🟢 VERT",
    ColorCode.ORANGE_CLAIR: "🟡 ORANGE CLAIR",
    ColorCode.ORANGE_FONCE: "🟠 ORANGE FONCÉ",
    ColorCode.ROUGE: "🔴 ROUGE",
}


def classify(score: float) -> tuple[ClassificationLevel, ColorCode]:
    """
    Classify a global compliance score.

    Args:
        score: Compliance score between 0.0 and 1.0

    Returns:
        Tuple of (ClassificationLevel, ColorCode)
    """
    for threshold, level, color in CLASSIFICATION_THRESHOLDS:
        if score >= threshold:
            return level, color
    return ClassificationLevel.NON_CONFORME, ColorCode.ROUGE


def classify_domain(score: float) -> tuple[ClassificationLevel, ColorCode]:
    """
    Classify a domain-level compliance score (more lenient than global).

    Args:
        score: Domain score between 0.0 and 1.0

    Returns:
        Tuple of (ClassificationLevel, ColorCode)
    """
    for threshold, level, color in DOMAIN_CLASSIFICATION_THRESHOLDS:
        if score >= threshold:
            return level, color
    return ClassificationLevel.NON_CONFORME, ColorCode.ROUGE


def worst_domain_color(domains: list[DomainScore]) -> ColorCode:
    """
    Get the worst color across all domain scores.

    Args:
        domains: List of domain scores

    Returns:
        ColorCode with highest severity
    """
    worst = ColorCode.VERT
    for domain in domains:
        _, color = classify_domain(domain.score)
        if COLOR_SEVERITY.get(color, 0) > COLOR_SEVERITY.get(worst, 0):
            worst = color
    return worst
