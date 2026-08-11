"""Criteria subpackage — legal criteria definitions."""
from .base import build_criterion, build_domain
from .rgpd import RGPD_DOMAINS
from .ai_act import AI_ACT_DOMAINS
from .lpd_ch import LPD_CH_DOMAINS

ALL_DOMAINS = RGPD_DOMAINS + AI_ACT_DOMAINS + LPD_CH_DOMAINS

__all__ = [
    "build_criterion",
    "build_domain",
    "RGPD_DOMAINS",
    "AI_ACT_DOMAINS",
    "LPD_CH_DOMAINS",
    "ALL_DOMAINS",
]
