"""
Vertical Cortex Leman v5 — revue assistée de contrats.

Ce module fournit un wedge métier ultra-précis pour avocats : la revue de contrats.
Il assiste l'expert, déclenche les gels nécessaires via règles déterministes et
prépare les points d'arbitrage humain. Il ne rend jamais de décision juridique finale.
"""

from .models import (
    ContractDocument,
    ContractIssue,
    ContractLanguage,
    ContractParty,
    ContractSection,
    ContractType,
    IssueCategory,
    IssueLocation,
    IssueSeverity,
    ReviewResult,
    RiskLevel,
)
from .reviewer import ContractReviewer, review_contract

__all__ = [
    "ContractDocument",
    "ContractIssue",
    "ContractLanguage",
    "ContractParty",
    "ContractReviewer",
    "ContractSection",
    "ContractType",
    "IssueCategory",
    "IssueLocation",
    "IssueSeverity",
    "ReviewResult",
    "RiskLevel",
    "review_contract",
]
