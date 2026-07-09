"""
Cortex Leman v5 — Erreurs structurées pour l'observabilité

Hiérarchie d'exceptions spécifiques — pas de bare except.
Chaque module lève son type propre, testable individuellement.
"""
from typing import Optional


class CortexObservabilityError(Exception):
    """Base — toutes les erreurs observabilité héritent d'ici."""
    def __init__(self, message: str, *, module: str = "", details: Optional[dict] = None):
        super().__init__(message)
        self.module = module
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "error_type": type(self).__name__,
            "module": self.module,
            "message": str(self),
            "details": self.details,
        }


# ── Validation ──

class ValidationError(CortexObservabilityError):
    """Input invalide (vertical inconnu, montant négatif, etc.)."""


class InvalidVerticalError(ValidationError):
    """Vertical n'est pas dans les 6 FR-CH autorisés."""
    def __init__(self, vertical: str):
        super().__init__(
            f"Vertical '{vertical}' non reconnu. Attendu: comptable, avocat, banque, sante, rh, startup.",
            module="observability",
            details={"vertical": vertical, "allowed": ["comptable", "avocat", "banque", "sante", "rh", "startup"]},
        )
        self.vertical = vertical


class EmptyInputError(ValidationError):
    """Champ texte vide alors qu'il est requis."""
    def __init__(self, field_name: str):
        super().__init__(
            f"Le champ '{field_name}' ne peut pas être vide.",
            module="observability",
            details={"field": field_name},
        )


class InvalidScoreError(ValidationError):
    """Score hors de [0.0, 1.0]."""
    def __init__(self, score: float):
        super().__init__(
            f"Score {score} hors plage [0.0, 1.0].",
            module="observability",
            details={"score": score},
        )


# ── Skill ──

class SkillError(CortexObservabilityError):
    """Erreur liée aux ComplianceSkills."""


class SkillNotFoundError(SkillError):
    """Skill ID demandé n'existe pas."""
    def __init__(self, skill_id: str):
        super().__init__(
            f"Skill '{skill_id}' introuvable dans le registre.",
            module="compliance_skill",
            details={"skill_id": skill_id},
        )


class SkillInvocationError(SkillError):
    """Échec d'invocation d'un skill."""
    def __init__(self, skill_id: str, reason: str):
        super().__init__(
            f"Skill '{skill_id}' invocation échouée: {reason}",
            module="compliance_skill",
            details={"skill_id": skill_id, "reason": reason},
        )


# ── Eval ──

class EvalError(CortexObservabilityError):
    """Erreur liée aux évaluations."""


class RubricNotFoundError(EvalError):
    """Rubric ID demandé n'existe pas."""
    def __init__(self, rubric_id: str, vertical: str):
        super().__init__(
            f"Rubric '{rubric_id}' introuvable pour vertical '{vertical}'.",
            module="eval_router",
            details={"rubric_id": rubric_id, "vertical": vertical},
        )


class EvalExecutionError(EvalError):
    """Le juge LLM a levé une exception."""
    def __init__(self, rubric_id: str, original_error: str):
        super().__init__(
            f"Évaluation rubric '{rubric_id}' échouée: {original_error}",
            module="eval_router",
            details={"rubric_id": rubric_id, "original_error": original_error},
        )


# ── Golden Dataset ──

class GoldenDatasetError(CortexObservabilityError):
    """Erreur liée au golden dataset."""


class CaseNotFoundError(GoldenDatasetError):
    """Case ID demandé n'existe pas."""
    def __init__(self, case_id: str):
        super().__init__(
            f"Golden case '{case_id}' introuvable.",
            module="golden_dataset",
            details={"case_id": case_id},
        )


class DuplicateCaseError(GoldenDatasetError):
    """Case avec même input_hash déjà présent."""
    def __init__(self, input_hash: str, existing_id: str):
        super().__init__(
            f"Case avec input_hash '{input_hash}' déjà existant (id={existing_id}).",
            module="golden_dataset",
            details={"input_hash": input_hash, "existing_id": existing_id},
        )


# ── Auto Approver ──

class AutoApprovalError(CortexObservabilityError):
    """Erreur liée à l'auto-approbation."""


class BacktestInsufficientDataError(AutoApprovalError):
    """Pas assez de données pour un backtest fiable."""
    def __init__(self, total: int, minimum: int):
        super().__init__(
            f"Backtest: {total} cas insuffisants (minimum {minimum}).",
            module="auto_approver",
            details={"total": total, "minimum": minimum},
        )


# ── Session Miner ──

class MiningError(CortexObservabilityError):
    """Erreur liée au mining de traces."""


# ── Journal WORM ──

class WormWriteError(CortexObservabilityError):
    """Écriture WORM échouée — critique pour l'audit."""


# ── Constantes partagées ──

ALLOWED_VERTICALS = frozenset({"comptable", "avocat", "banque", "sante", "rh", "startup"})
