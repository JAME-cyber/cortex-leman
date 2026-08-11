"""Scoring subpackage — evaluation logic."""
from .evaluator import evaluate_domain, evaluate_all_domains
from .weights import get_regulation_weights, normalize_weights
from .thresholds import classify, classify_domain, COLOR_MAP, CLASSIFICATION_THRESHOLDS

__all__ = [
    "evaluate_domain",
    "evaluate_all_domains",
    "get_regulation_weights",
    "normalize_weights",
    "classify",
    "classify_domain",
    "COLOR_MAP",
    "CLASSIFICATION_THRESHOLDS",
]
