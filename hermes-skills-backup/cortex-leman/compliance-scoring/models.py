"""
Data models for Cortex Leman Compliance Scoring v5.

All scoring inputs/outputs are defined here.
Each model is immutable (frozen dataclass) to prevent accidental mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class ClassificationLevel(Enum):
    """Compliance classification levels (4 tiers)."""
    NON_CONFORME = "NON_CONFORME"
    PARTIELLEMENT_CONFORME = "PARTIELLEMENT_CONFORME"
    LARGEMENT_CONFORME = "LARGEMENT_CONFORME"
    PLEINEMENT_CONFORME = "PLEINEMENT_CONFORME"


class ColorCode(Enum):
    """Traffic-light color code for classification."""
    VERT = "VERT"
    ORANGE_CLAIR = "ORANGE_CLAIR"
    ORANGE_FONCE = "ORANGE_FONCE"
    ROUGE = "ROUGE"


class RegulationSource(Enum):
    """Regulation framework identifier."""
    RGPD = "RGPD"
    AI_ACT = "AI_ACT"
    LPD_CH = "LPD_CH"


class EvidenceType(Enum):
    """Types of audit evidence accepted."""
    DOCUMENT = "document"
    POLICY = "policy"
    CONTRACT = "contract"
    LOG = "log"
    SCREENSHOT = "screenshot"
    DECLARATION = "declaration"
    DPA = "dpa"
    PIA = "pia"
    REGISTRE = "registre"


@dataclass(frozen=True)
class Citation:
    """Traceable legal citation — every score must reference its legal basis."""
    source: str          # "RGPD", "AI_ACT", "LPD_CH"
    article_id: str       # "RGPD.5.1.a", "AI_ACT.9.2", "LPD_CH.7.1"
    article_title: str    # "Principe de licéité, équité et transparence"
    excerpt: str          # Exact or abridged text from the regulation
    url: str              # Link to official text
    relevance: float      # 0.0-1.0 — how relevant this citation is to the finding

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "article_id": self.article_id,
            "article_title": self.article_title,
            "excerpt": self.excerpt,
            "url": self.url,
            "relevance": self.relevance,
        }


@dataclass(frozen=True)
class ChecklistItem:
    """A single audit question tied to a criterion."""
    id: str               # "RGPD.5.1.a.q1"
    question: str          # "Avez-vous documenté la base légale pour chaque traitement ?"
    is_mandatory: bool = True  # If false, non-answer is not a violation
    severity: str = "major"  # "critical", "major", "minor"


@dataclass(frozen=True)
class Criterion:
    """A single legal article with its audit checklist."""
    article_id: str        # "RGPD.5.1.a"
    title: str             # "Principe de licéité"
    text: str              # Abridged original text
    threshold: float        # Minimum score to be compliant (0.0-1.0)
    weight: float          # Weight within its domain (normalized to sum=1)
    checklist: List[ChecklistItem] = field(default_factory=list)
    evidence_types: List[str] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)


@dataclass(frozen=True)
class CriteriaDomain:
    """A domain groups related criteria (e.g., all RGPD Chapter II articles)."""
    id: str                # "rgpd_principes"
    name: str              # "Principes de traitement"
    regulation: str        # "RGPD"
    chapter: str           # "Chapitre II, Art. 5-11"
    default_weight: float # Default weight in global score (0.0-1.0)
    criteria: List[Criterion] = field(default_factory=list)

    @property
    def total_criteria(self) -> int:
        return len(self.criteria)

    @property
    def total_checklist_items(self) -> int:
        return sum(len(c.checklist) for c in self.criteria)


@dataclass(frozen=True)
class ChecklistResponse:
    """Response to a single checklist item."""
    item_id: str
    score: float           # 0.0=no, 0.5=partial, 1.0=yes
    evidence: Optional[str] = None  # Description or link to evidence
    notes: Optional[str] = None     # Auditor notes


@dataclass(frozen=True)
class Violation:
    """A specific compliance violation found during audit."""
    criterion_id: str
    article_id: str
    regulation: str
    severity: str          # "critical", "major", "minor"
    description: str
    recommendation: str
    citations: List[Citation] = field(default_factory=list)


@dataclass(frozen=True)
class DomainScore:
    """Score for a single domain."""
    domain_id: str
    domain_name: str
    regulation: str
    score: float           # 0.0-1.0 weighted domain score
    raw_score: float       # Unweighted average of checklist responses
    total_items: int
    answered_items: int
    violations: List[Violation] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "domain_id": self.domain_id,
            "domain_name": self.domain_name,
            "regulation": self.regulation,
            "score": self.score,
            "raw_score": self.raw_score,
            "total_items": self.total_items,
            "answered_items": self.answered_items,
            "violation_count": len(self.violations),
            "critical_violations": sum(1 for v in self.violations if v.severity == "critical"),
        }


@dataclass(frozen=True)
class KillSwitchResult:
    """Result of kill switch evaluation."""
    activated: bool
    reason: str = ""
    domain_id: str = ""
    violations: List[Violation] = field(default_factory=list)


@dataclass(frozen=True)
class AuditResult:
    """Complete audit result — the final output of the scoring engine."""
    audit_id: str
    timestamp: str
    global_score: float
    classification: ClassificationLevel
    color: ColorCode
    domain_scores: List[DomainScore]
    all_violations: List[Violation]
    kill_switch: KillSwitchResult
    recommendations: List[str]
    citations: List[Citation]
    attestation_eligible: bool
    regulation_weights: Dict[str, float]  # Actual weights used: {"RGPD": 0.60, "AI_ACT": 0.25, "LPD_CH": 0.15}
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "global_score": self.global_score,
            "classification": self.classification.value,
            "color": self.color.value,
            "attestation_eligible": self.attestation_eligible,
            "kill_switch": {
                "activated": self.kill_switch.activated,
                "reason": self.kill_switch.reason,
            },
            "regulation_weights": self.regulation_weights,
            "domain_scores": [ds.to_dict() for ds in self.domain_scores],
            "violation_count": len(self.all_violations),
            "critical_violations": sum(1 for v in self.all_violations if v.severity == "critical"),
            "recommendations": self.recommendations,
            "citation_count": len(self.citations),
        }


# --- Input models ---

@dataclass
class AuditInput:
    """Input for an audit evaluation."""
    client_id: str
    sector: str            # "health", "finance", "retail", "public", "tech", "ai", "other"
    jurisdiction: str      # "FR", "CH", "FR_CH"
    responses: Dict[str, ChecklistResponse]  # Keyed by checklist item id
    metadata: Dict = field(default_factory=dict)
