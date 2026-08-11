"""
Weight calculation for compliance scoring.

Regulation weights determine how much each framework (RGPD, AI Act, LPD/CH)
contributes to the global score. Weights are adjusted by sector and jurisdiction.

Default distribution:
  - RGPD: 50%
  - AI Act: 25%
  - LPD/CH: 25%

Sector adjustments:
  - health:  RGPD 55%, AI Act 20%, LPD/CH 25%
  - finance: RGPD 55%, AI Act 20%, LPD/CH 25%
  - retail:  RGPD 60%, AI Act 15%, LPD/CH 25%
  - public:  RGPD 50%, AI Act 25%, LPD/CH 25%
  - tech:    RGPD 30%, AI Act 50%, LPD/CH 20%
  - ai:      RGPD 25%, AI Act 55%, LPD/CH 20%

Jurisdiction adjustments:
  - FR (France only): LPD/CH weight → 0, redistributed to RGPD
  - CH (Switzerland only): RGPD reduced, LPD/CH increased
  - FR_CH (both): default weights
"""

from __future__ import annotations

from typing import Dict

# Default weights per regulation framework
DEFAULT_WEIGHTS: Dict[str, float] = {
    "RGPD": 0.50,
    "AI_ACT": 0.25,
    "LPD_CH": 0.25,
}

# Sector-specific weight overrides
SECTOR_WEIGHTS: Dict[str, Dict[str, float]] = {
    "health": {"RGPD": 0.55, "AI_ACT": 0.20, "LPD_CH": 0.25},
    "finance": {"RGPD": 0.55, "AI_ACT": 0.20, "LPD_CH": 0.25},
    "retail": {"RGPD": 0.60, "AI_ACT": 0.15, "LPD_CH": 0.25},
    "public": {"RGPD": 0.50, "AI_ACT": 0.25, "LPD_CH": 0.25},
    "tech": {"RGPD": 0.30, "AI_ACT": 0.50, "LPD_CH": 0.20},
    "ai": {"RGPD": 0.25, "AI_ACT": 0.55, "LPD_CH": 0.20},
    "other": {"RGPD": 0.50, "AI_ACT": 0.25, "LPD_CH": 0.25},
}


def get_regulation_weights(sector: str, jurisdiction: str) -> Dict[str, float]:
    """
    Get effective regulation weights for a given sector and jurisdiction.

    Args:
        sector: Industry sector (health, finance, retail, public, tech, ai, other)
        jurisdiction: "FR", "CH", or "FR_CH"

    Returns:
        Dict mapping regulation name to weight (sums to 1.0)
    """
    # Start with sector-specific weights
    sector_lower = sector.lower()
    if sector_lower in SECTOR_WEIGHTS:
        weights = SECTOR_WEIGHTS[sector_lower].copy()
    else:
        weights = DEFAULT_WEIGHTS.copy()

    # Jurisdiction adjustment
    if jurisdiction == "FR":
        # France-only: no LPD/CH, redistribute
        lpd_weight = weights.get("LPD_CH", 0.25)
        weights["LPD_CH"] = 0.0
        # Redistribute proportionally to RGPD and AI_ACT
        other_sum = weights["RGPD"] + weights["AI_ACT"]
        if other_sum > 0:
            weights["RGPD"] += lpd_weight * (weights["RGPD"] / other_sum)
            weights["AI_ACT"] += lpd_weight * (weights["AI_ACT"] / other_sum)

    elif jurisdiction == "CH":
        # Switzerland-only: LPD/CH is primary, RGPD is secondary
        weights["LPD_CH"] = 0.50
        weights["RGPD"] = 0.30
        weights["AI_ACT"] = 0.20

    # Normalize to ensure sum == 1.0
    return normalize_weights(weights)


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize weights to sum to 1.0.

    Args:
        weights: Dict of key -> float value

    Returns:
        Normalized dict with same keys, values summing to 1.0
    """
    total = sum(weights.values())
    if total == 0:
        return {k: 1.0 / len(weights) for k in weights}
    return {k: v / total for k, v in weights.items()}
