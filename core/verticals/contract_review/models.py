"""
Modèles Pydantic v2 pour la revue assistée de contrats.

Les modèles sont volontairement explicites pour faciliter l'audit, la sérialisation
dans le journal WORM hash-chaîné et le passage par le Médiateur déterministe.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from hashlib import sha256
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


LEGAL_DISCLAIMERS: tuple[str, ...] = (
    "Cortex Leman assiste l'avocat et ne remplace jamais son analyse professionnelle.",
    "Aucune conclusion de ce rapport ne constitue une décision juridique finale.",
    "Secret professionnel : traiter les données conformément à l'art. 321 CP suisse, au RGPD et à la LPD.",
    "Les points critiques doivent être validés par un avocat habilité avant toute communication au client.",
)


class ContractType(StrEnum):
    """Typologie opérationnelle du contrat analysé."""

    NDA = "nda"
    COMMERCIAL = "contrat_commercial"
    CGV = "cgv"
    EMPLOYMENT = "contrat_travail"
    SERVICE = "contrat_prestation"
    SAAS = "contrat_saas"
    DISTRIBUTION = "contrat_distribution"
    LICENSE = "contrat_licence"
    LEASE = "bail_commercial"
    MANDATE = "mandat"
    SHAREHOLDERS = "pacte_actionnaires"
    OTHER = "autre"


class ContractLanguage(StrEnum):
    """Langue principale du contrat."""

    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    ENGLISH = "en"
    OTHER = "autre"


class IssueSeverity(StrEnum):
    """Sévérité auditée d'un problème détecté."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(StrEnum):
    """Niveau de risque global agrégé."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class IssueCategory(StrEnum):
    """Catégorie métier d'un problème contractuel."""

    ABUSIVE_CLAUSE = "clause_abusive"
    IMBALANCE = "desequilibre_contractuel"
    MISSING_OBLIGATION = "obligation_manquante"
    GOVERNING_LAW_RISK = "droit_applicable_suspect"
    JURISDICTION_RISK = "jurisdiction_risk"
    PENALTY_RISK = "penalite_disproportionnee"
    NON_COMPETE_RISK = "non_concurrence_risquee"
    DATA_PROTECTION_RISK = "protection_donnees"
    LIABILITY_RISK = "responsabilite"
    IP_RISK = "propriete_intellectuelle"
    TERMINATION_RISK = "resiliation"
    OTHER = "autre"


class IssueSource(StrEnum):
    """Origine contrôlée d'une détection."""

    LLM = "llm"
    JSONLOGIC = "jsonlogic"
    HYBRID = "hybrid"
    HUMAN = "human"


class ContractParty(BaseModel):
    """Partie au contrat."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(..., min_length=1, description="Nom de la partie.")
    role: str | None = Field(default=None, description="Rôle contractuel : client, fournisseur, employeur, etc.")
    country: str | None = Field(default=None, description="Pays ou siège principal.")
    is_client: bool = Field(default=False, description="Indique si la partie est le client de l'avocat.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Métadonnées non décisionnelles.")


class ContractSection(BaseModel):
    """Section ou clause extraite du document."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(default_factory=lambda: f"section-{uuid4().hex[:12]}")
    title: str | None = Field(default=None)
    clause_ref: str | None = Field(default=None, description="Référence lisible : art. 7.2, clause 12, etc.")
    text: str = Field(..., min_length=1)
    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_pages(self) -> ContractSection:
        """Garantit une pagination cohérente lorsque présente."""
        if self.page_start is not None and self.page_end is not None and self.page_end < self.page_start:
            raise ValueError("page_end doit être supérieur ou égal à page_start")
        return self


class ContractDocument(BaseModel):
    """Document contractuel soumis à revue assistée."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(default_factory=lambda: f"contract-{uuid4().hex[:16]}")
    title: str = Field(default="Contrat sans titre", min_length=1)
    contract_type: ContractType = Field(default=ContractType.OTHER)
    parties: list[ContractParty] = Field(default_factory=list)
    jurisdiction: str | None = Field(default=None, description="Juridiction cible ou contexte métier attendu.")
    governing_law: str | None = Field(default=None, description="Droit applicable déclaré si déjà connu.")
    language: ContractLanguage = Field(default=ContractLanguage.FRENCH)
    text: str | None = Field(default=None, description="Texte intégral brut lorsque disponible.")
    sections: list[ContractSection] = Field(default_factory=list)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    contract_value: Decimal | None = Field(default=None, ge=Decimal("0"))
    source_path: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        """Normalise le code devise ISO en majuscules."""
        return value.upper() if value else value

    @model_validator(mode="after")
    def require_text_or_sections(self) -> ContractDocument:
        """Refuse un document sans contenu exploitable."""
        if not self.text and not self.sections:
            raise ValueError("ContractDocument nécessite au moins text ou sections")
        return self

    def full_text(self) -> str:
        """Retourne le texte consolidé du contrat."""
        if self.text:
            return self.text
        return "\n\n".join(section.text for section in self.sections)

    def stable_hash(self) -> str:
        """Calcule une empreinte stable utile au journal WORM."""
        payload = f"{self.id}|{self.title}|{self.contract_type}|{self.full_text()}".encode("utf-8")
        return sha256(payload).hexdigest()


class IssueLocation(BaseModel):
    """Localisation auditable d'un problème dans le contrat."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    section_id: str | None = None
    section_title: str | None = None
    clause_ref: str | None = None
    page: int | None = Field(default=None, ge=1)
    excerpt: str | None = Field(default=None, max_length=1200)


class ContractIssue(BaseModel):
    """Problème contractuel détecté par LLM, règle déterministe ou arbitrage humain."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(default_factory=lambda: f"issue-{uuid4().hex[:16]}")
    category: IssueCategory = Field(default=IssueCategory.OTHER)
    title: str = Field(..., min_length=1)
    severity: IssueSeverity = Field(default=IssueSeverity.MEDIUM)
    location: IssueLocation = Field(default_factory=IssueLocation)
    legal_basis: list[str] = Field(default_factory=list)
    recommendation: str = Field(..., min_length=1)
    rationale: str = Field(..., min_length=1)
    source: IssueSource = Field(default=IssueSource.LLM)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    requires_human_arbitration: bool = Field(
        default=True,
        description="Vrai si le point doit être validé ou arbitré par l'avocat.",
    )
    rule_id: str | None = Field(default=None, description="Identifiant JsonLogic si applicable.")
    action: str | None = Field(default=None, description="Action Médiateur attendue : flag, freeze, block.")

    @model_validator(mode="after")
    def force_arbitration_for_high_severity(self) -> ContractIssue:
        """Toute sévérité élevée impose une validation humaine."""
        if self.severity in {IssueSeverity.HIGH, IssueSeverity.CRITICAL}:
            self.requires_human_arbitration = True
        return self


class ReviewResult(BaseModel):
    """Résultat complet de revue assistée, prêt pour audit et arbitrage."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    review_id: str = Field(default_factory=lambda: f"review-{uuid4().hex[:16]}")
    contract_id: str
    contract_hash: str
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    issues: list[ContractIssue] = Field(default_factory=list)
    risk_score: int = Field(default=0, ge=0, le=100)
    risk_level: RiskLevel = Field(default=RiskLevel.LOW)
    summary: str = Field(..., min_length=1)
    human_validation_points: list[str] = Field(default_factory=list)
    deterministic_ruleset_version: str = Field(default="contract_review.rules.v1")
    llm_model: str | None = Field(default=None)
    mediator_required: bool = Field(
        default=True,
        description="La revue doit rester branchée au Médiateur déterministe.",
    )
    worm_journal_required: bool = Field(
        default=True,
        description="Les événements de revue doivent être inscrits dans le journal WORM.",
    )
    final_decision_rendered: bool = Field(
        default=False,
        description="Toujours faux : seul l'avocat peut décider.",
    )
    disclaimers: list[str] = Field(default_factory=lambda: list(LEGAL_DISCLAIMERS))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def ensure_no_final_decision(self) -> ReviewResult:
        """Empêche tout glissement vers une décision automatique."""
        if self.final_decision_rendered:
            raise ValueError("La revue de contrat ne peut jamais rendre une décision finale automatique")
        if not self.mediator_required or not self.worm_journal_required:
            raise ValueError("Le Médiateur et le journal WORM sont obligatoires")
        if "Validation finale par l'avocat obligatoire." not in self.human_validation_points:
            self.human_validation_points.append("Validation finale par l'avocat obligatoire.")
        return self
