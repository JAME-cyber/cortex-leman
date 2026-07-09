"""
Cortex Leman v5 — ObservabilityContext: DI container pour l'observabilité

Remplace les 9 singletons module-level par un contexte injectable.
- En production: `ObservabilityContext.default()` crée l'instance partagée
- En tests: `ObservabilityContext()` crée une instance fraîche isolée
- Chaque composant est accessible via le contexte, pas via import global
"""
import logging
from typing import Optional

from core.observability.errors import (
    CortexObservabilityError,
    ValidationError,
    InvalidVerticalError,
    EmptyInputError,
    ALLOWED_VERTICALS,
)

logger = logging.getLogger(__name__)


def validate_vertical(vertical: str) -> str:
    """Valider qu'un vertical est dans les 6 FR-CH autorisés. Lève InvalidVerticalError."""
    v = (vertical or "").strip().lower()
    if v not in ALLOWED_VERTICALS:
        raise InvalidVerticalError(vertical or "")
    return v


def validate_non_empty(text: str, field_name: str = "input_text") -> str:
    """Valider qu'un champ texte n'est pas vide. Lève EmptyInputError."""
    if not text or not text.strip():
        raise EmptyInputError(field_name)
    return text.strip()


def validate_score(score: float) -> float:
    """Valider qu'un score est dans [0.0, 1.0]. Lève InvalidScoreError."""
    from core.observability.errors import InvalidScoreError
    if not isinstance(score, (int, float)) or not (0.0 <= float(score) <= 1.0):
        raise InvalidScoreError(float(score) if isinstance(score, (int, float)) else -1)
    return float(score)


class ObservabilityContext:
    """
    Contexte d'observabilité injectable.

    Contient toutes les instances des modules observabilité.
    Pas de singletons globaux — tout passe par ce contexte.

    Usage production:
        ctx = ObservabilityContext.default()
        ctx.eval_router.evaluate(...)

    Usage tests:
        ctx = ObservabilityContext()  # Fraîchement créé, isolé
        ctx.skill_registry.register(...)
    """

    def __init__(self, seed: bool = False):
        # Lazy imports pour éviter les circular dependencies
        from core.observability.tracing import CortexTracer, ConsoleExporter, WORMExporter
        from core.observability.observe_skill import ObserveSkill
        from core.observability.eval_router import EvalRouter
        from core.observability.golden_dataset import GoldenDataset, seed_default_dataset
        from core.observability.rule_experiment import RuleExperiment
        from core.observability.judge_adversarial import JudgeAdversarialTest
        from core.observability.compliance_skill import SkillRegistry, seed_skills
        from core.observability.auto_approver import AutoApprover
        from core.observability.session_miner import SessionMiner

        # Tracing
        self.tracer = CortexTracer()
        self.tracer.add_exporter(ConsoleExporter())
        self.tracer.add_exporter(WORMExporter())

        # Observe
        self.observe_skill = ObserveSkill()

        # Eval pipeline
        self.eval_router = EvalRouter()
        self.golden_dataset = GoldenDataset()
        self.rule_experiment = RuleExperiment()
        self.judge_adversarial = JudgeAdversarialTest()

        # Intercom-inspired
        self.skill_registry = SkillRegistry()
        self.auto_approver = AutoApprover()
        self.session_miner = SessionMiner()

        # Meta-evaluator (separate module, keep reference)
        from core.mediator.meta_evaluator import MetaEvaluator
        self.meta_evaluator = MetaEvaluator()

        if seed:
            self.eval_router.load_rubrics()
            seed_default_dataset(self.golden_dataset)
            seed_skills(self.skill_registry)

    @classmethod
    def default(cls) -> "ObservabilityContext":
        """
        Créer le contexte de production avec données pré-chargées.
        """
        return cls(seed=True)

    def reset_all(self):
        """Réinitialiser tous les composants (pour les tests)."""
        self.eval_router.reset()
        self.golden_dataset.reset()
        self.skill_registry.reset()
        self.auto_approver.reset()

        # Les autres n'ont pas d'état mutable entre tests
        self.rule_experiment = type(self.rule_experiment)()
        self.judge_adversarial = type(self.judge_adversarial)()


# Instance globale pour la production — mais testable
_global_context: Optional[ObservabilityContext] = None


def get_context() -> ObservabilityContext:
    """
    Obtenir le contexte global (production).
    En tests, utiliser ObservabilityContext() directement.
    """
    global _global_context
    if _global_context is None:
        _global_context = ObservabilityContext.default()
    return _global_context
