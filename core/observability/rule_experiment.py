"""
Cortex Leman v5 — RuleExperiment: Framework d'expériences sur les règles JsonLogic

Inspiré de: Laurie Voss, "Ship Real Agents" (Arize)
> "Controlled comparison: same inputs, same evaluators, only the prompt changed."
> "Any difference in scores is attributable to your change."
> "You should be treating your evals like code — version them."

Leçon clé pour Cortex:
Le Médiateur utilise des règles JsonLogic, pas des prompts LLM.
Mais le principe d'expérience contrôlée s'applique:
- Mêmes inputs (cas de test du GoldenDataset)
- Mêmes evaluateurs (rubrics de l'EvalRouter)
- Seule la règle change → différence de score = impact de la règle

Architecture:
1. Snapshot de la règle actuelle (baseline)
2. Appliquer la règle candidate (modified)
3. Comparer les résultats sur les mêmes cas de test
4. Mesurer: pass_rate delta, new_failures, new_passes, regressions
5. Proposer via le système d'extension → arbitrage humain
"""
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum
from copy import deepcopy

logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ChangeType(str, Enum):
    """Type de changement sur une règle"""
    ADD_RULE = "add_rule"             # Ajouter une nouvelle règle
    REMOVE_RULE = "remove_rule"       # Supprimer une règle
    MODIFY_CONDITION = "modify_condition"  # Modifier la condition JsonLogic
    MODIFY_THRESHOLD = "modify_threshold"  # Modifier un seuil
    MODIFY_ACTION = "modify_action"   # Changer l'action (warn → freeze, etc.)
    MODIFY_SEVERITY = "modify_severity"  # Changer la sévérité


@dataclass
class RuleChange:
    """
    Un changement proposé sur une règle.

    Version le changement pour comparaison:
    - before: snapshot de la règle actuelle
    - after: snapshot de la règle proposée
    """
    change_id: str = ""
    change_type: ChangeType = ChangeType.MODIFY_CONDITION
    vertical: str = ""
    rule_id: str = ""
    before: dict = field(default_factory=dict)  # Snapshot règle actuelle
    after: dict = field(default_factory=dict)    # Snapshot règle proposée
    rationale: str = ""   # Pourquoi ce changement
    source: str = ""      # Qui a proposé (meta_evaluator, human, etc.)

    def to_dict(self) -> dict:
        return {
            "change_id": self.change_id,
            "change_type": self.change_type.value,
            "vertical": self.vertical,
            "rule_id": self.rule_id,
            "before": self.before,
            "after": self.after,
            "rationale": self.rationale,
            "source": self.source,
        }


@dataclass
class ExperimentResult:
    """Résultat d'une expérience sur un seul cas"""
    case_id: str = ""
    vertical: str = ""
    input_text: str = ""

    # Résultats baseline vs candidate
    baseline_action: str = ""      # Action de la règle actuelle
    candidate_action: str = ""     # Action de la règle candidate
    baseline_triggered: bool = False
    candidate_triggered: bool = False

    # Évaluation
    is_regression: bool = False    # Le changement a introduit une régression
    is_improvement: bool = False   # Le changement a amélioré le résultat
    is_neutral: bool = True        # Pas de changement notable

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "vertical": self.vertical,
            "baseline_action": self.baseline_action,
            "candidate_action": self.candidate_action,
            "baseline_triggered": self.baseline_triggered,
            "candidate_triggered": self.candidate_triggered,
            "is_regression": self.is_regression,
            "is_improvement": self.is_improvement,
            "is_neutral": self.is_neutral,
        }


@dataclass
class ExperimentReport:
    """Rapport complet d'une expérience"""
    experiment_id: str = ""
    status: ExperimentStatus = ExperimentStatus.DRAFT
    created_at: str = ""
    completed_at: str = ""

    # Changement testé
    change: Optional[RuleChange] = None

    # Résultats agrégés
    total_cases: int = 0
    baseline_pass_rate: float = 0.0
    candidate_pass_rate: float = 0.0
    delta_pass_rate: float = 0.0

    improvements: int = 0
    regressions: int = 0
    neutral: int = 0

    # Détails
    case_results: list[ExperimentResult] = field(default_factory=list)

    # Recommendation
    recommendation: str = ""       # "adopt", "reject", "needs_review"
    recommendation_reason: str = ""

    @property
    def should_adopt(self) -> bool:
        """L'expérience améliore-t-elle le système ?"""
        return (
            self.delta_pass_rate > 0
            and self.regressions == 0
            and self.status == ExperimentStatus.COMPLETED
        )

    @property
    def has_regressions(self) -> bool:
        return self.regressions > 0

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "change": self.change.to_dict() if self.change else None,
            "summary": {
                "total_cases": self.total_cases,
                "baseline_pass_rate": round(self.baseline_pass_rate, 4),
                "candidate_pass_rate": round(self.candidate_pass_rate, 4),
                "delta_pass_rate": round(self.delta_pass_rate, 4),
                "improvements": self.improvements,
                "regressions": self.regressions,
                "neutral": self.neutral,
            },
            "recommendation": self.recommendation,
            "recommendation_reason": self.recommendation_reason,
            "case_results": [r.to_dict() for r in self.case_results],
        }


class RuleExperiment:
    """
    Framework d'expériences sur les règles JsonLogic du Médiateur.

    Processus:
    1. Définir un changement de règle (RuleChange)
    2. Charger les cas de test (GoldenDataset)
    3. Exécuter la règle baseline vs candidate sur chaque cas
    4. Comparer les résultats
    5. Mesurer les régressions et améliorations
    6. Proposer l'adoption via le système d'extension

    Usage:
        exp = RuleExperiment()
        change = RuleChange(
            vertical="comptable",
            rule_id="comptable-001",
            change_type=ChangeType.MODIFY_THRESHOLD,
            before={"condition": {"and": [...]}},
            after={"condition": {"and": [...nouveau...]}},
        )
        report = exp.run_experiment(
            change=change,
            test_cases=golden_dataset.get_split(DataSplit.TEST),
        )
    """

    # Seuils
    MIN_TEST_CASES = 5            # Minimum pour une expérience valide
    REGRESSION_TOLERANCE = 0      # Tolérance zéro pour les régressions
    IMPROVEMENT_THRESHOLD = 0.05  # 5% minimum d'amélioration pour recommander

    def __init__(self):
        self._experiments: dict[str, ExperimentReport] = {}

    def run_experiment(
        self,
        change: RuleChange,
        test_cases: list,
        rule_evaluator_fn=None,
    ) -> ExperimentReport:
        """
        Exécuter une expérience contrôlée.

        Args:
            change: Le changement de règle à tester
            test_cases: Les cas de test (GoldenCase objects)
            rule_evaluator_fn: Fonction (rule, case) → triggered, action
                               Si None, utilise l'évaluation basique par mots-clés

        Returns:
            Rapport d'expérience
        """
        report = ExperimentReport(
            experiment_id=uuid.uuid4().hex[:12],
            status=ExperimentStatus.RUNNING,
            created_at=datetime.now(timezone.utc).isoformat(),
            change=change,
        )

        if len(test_cases) < self.MIN_TEST_CASES:
            report.status = ExperimentStatus.FAILED
            report.recommendation_reason = (
                f"Pas assez de cas de test ({len(test_cases)} < {self.MIN_TEST_CASES})"
            )
            self._experiments[report.experiment_id] = report
            return report

        # Filtrer les cas du vertical concerné
        vertical_cases = [c for c in test_cases if c.vertical == change.vertical]
        if not vertical_cases:
            # Si pas de cas spécifique au vertical, utiliser tous les cas
            vertical_cases = test_cases

        report.total_cases = len(vertical_cases)

        baseline_passes = 0
        candidate_passes = 0

        for case in vertical_cases:
            result = ExperimentResult(
                case_id=case.case_id,
                vertical=case.vertical,
                input_text=case.input_text[:200],
            )

            if rule_evaluator_fn:
                # Utiliser la fonction d'évaluation fournie
                result.baseline_triggered, result.baseline_action = rule_evaluator_fn(
                    change.before, case
                )
                result.candidate_triggered, result.candidate_action = rule_evaluator_fn(
                    change.after, case
                )
            else:
                # Évaluation basique: simuler un trigger par mots-clés
                result.baseline_triggered, result.baseline_action = self._basic_rule_eval(
                    change.before, case
                )
                result.candidate_triggered, result.candidate_action = self._basic_rule_eval(
                    change.after, case
                )

            # Déterminer si c'est une régression, amélioration ou neutre
            # Régression: baseline ne bloquait pas, candidate ne bloque pas non plus
            # mais le cas est un FAIL → on s'attendrait à ce que ça bloque
            if case.expected_label.value == "fail":
                if not result.baseline_triggered and result.candidate_triggered:
                    result.is_improvement = True
                    result.is_neutral = False
                elif result.baseline_triggered and not result.candidate_triggered:
                    result.is_regression = True
                    result.is_neutral = False
            elif case.expected_label.value == "pass":
                if result.baseline_triggered and not result.candidate_triggered:
                    result.is_improvement = True
                    result.is_neutral = False
                elif not result.baseline_triggered and result.candidate_triggered:
                    result.is_regression = True
                    result.is_neutral = False

            # Compter les passes
            if not result.baseline_triggered or result.baseline_action in ("warn",):
                baseline_passes += 1
            if not result.candidate_triggered or result.candidate_action in ("warn",):
                candidate_passes += 1

            report.case_results.append(result)

        # Agréger
        report.baseline_pass_rate = baseline_passes / report.total_cases if report.total_cases else 0
        report.candidate_pass_rate = candidate_passes / report.total_cases if report.total_cases else 0
        report.delta_pass_rate = report.candidate_pass_rate - report.baseline_pass_rate

        report.improvements = sum(1 for r in report.case_results if r.is_improvement)
        report.regressions = sum(1 for r in report.case_results if r.is_regression)
        report.neutral = sum(1 for r in report.case_results if r.is_neutral)

        # Recommandation
        if report.regressions > self.REGRESSION_TOLERANCE:
            report.recommendation = "reject"
            report.recommendation_reason = (
                f"Régressions détectées: {report.regressions} cas dégradés. "
                f"Ne pas adopter sans investigation."
            )
        elif report.delta_pass_rate >= self.IMPROVEMENT_THRESHOLD:
            report.recommendation = "adopt"
            report.recommendation_reason = (
                f"Amélioration nette: +{report.delta_pass_rate:.1%} pass rate, "
                f"{report.improvements} améliorations, {report.regressions} régressions."
            )
        elif report.delta_pass_rate > 0:
            report.recommendation = "needs_review"
            report.recommendation_reason = (
                f"Amélioration marginale: +{report.delta_pass_rate:.1%}. "
                f"Considérer l'adoption si le changement est peu risqué."
            )
        elif report.delta_pass_rate == 0:
            report.recommendation = "neutral"
            report.recommendation_reason = "Aucun changement détecté."
        else:
            report.recommendation = "reject"
            report.recommendation_reason = (
                f"Dégradation: {report.delta_pass_rate:.1%} pass rate."
            )

        report.status = ExperimentStatus.COMPLETED
        report.completed_at = datetime.now(timezone.utc).isoformat()

        self._experiments[report.experiment_id] = report
        return report

    def _basic_rule_eval(self, rule: dict, case) -> tuple[bool, str]:
        """
        Évaluation basique d'une règle contre un cas.

        Simule le comportement du Médiateur JsonLogic:
        - Vérifie si la condition matche les attributs du cas
        - Retourne (triggered, action)

        C'est une approximation — le vrai Médiateur utiliserait jsonLogic.evaluate()
        """
        if not rule:
            return False, ""

        condition = rule.get("condition", {})
        action = rule.get("action", "warn")

        # Évaluation simplifiée par mots-clés du condition JsonLogic
        # On extrait les valeurs de condition et on les compare au cas
        input_lower = case.input_text.lower()
        output_lower = (case.output_text or "").lower()

        # Si la condition contient des mots-clés présents dans l'input
        condition_str = json.dumps(condition).lower()

        # Simulation: si le condition mentionne un action.type et que l'input en parle
        triggered = False

        # Heuristique simple: vérifier des patterns communs
        if '"data_transfer"' in condition_str and ("transfert" in input_lower or "transfer" in input_lower):
            triggered = True
        elif '"llm_query"' in condition_str and ("llm" in input_lower or "modèle" in input_lower):
            triggered = True
        elif '"decision_fiscale"' in condition_str and ("impôt" in input_lower or "fiscal" in input_lower):
            triggered = True
        elif '"redaction_conclusions"' in condition_str and ("conclusion" in input_lower or "rédiger" in input_lower):
            triggered = True
        elif '"ecriture_comptable"' in condition_str and ("écriture" in input_lower or "comptab" in input_lower):
            triggered = True

        return triggered, action

    def run_ab_test(
        self,
        rule_a: dict,
        rule_b: dict,
        test_cases: list,
        vertical: str = "",
    ) -> ExperimentReport:
        """
        A/B test entre deux versions d'une règle.

        Convenience wrapper pour comparer deux règles.
        """
        change = RuleChange(
            change_id=uuid.uuid4().hex[:8],
            vertical=vertical,
            before=rule_a,
            after=rule_b,
            change_type=ChangeType.MODIFY_CONDITION,
            rationale="A/B test comparatif",
        )

        return self.run_experiment(change, test_cases)

    def get_experiment(self, experiment_id: str) -> Optional[ExperimentReport]:
        """Récupérer une expérience par ID"""
        return self._experiments.get(experiment_id)

    def get_all_experiments(self) -> list[dict]:
        """Lister toutes les expériences"""
        return [r.to_dict() for r in self._experiments.values()]

    def propose_adoption(self, report: ExperimentReport) -> dict:
        """
        Convertir une recommandation d'expérience en proposition d'extension.

        La proposition passe par le système d'extension pour arbitrage humain.
        """
        if not report.change:
            return {"error": "Aucun changement associé"}

        return {
            "type": "rule_experiment",
            "action": "adopt_rule_change" if report.recommendation == "adopt" else "review_rule_change",
            "experiment_id": report.experiment_id,
            "vertical": report.change.vertical,
            "rule_id": report.change.rule_id,
            "change_type": report.change.change_type.value,
            "before": report.change.before,
            "after": report.change.after,
            "evidence": {
                "delta_pass_rate": round(report.delta_pass_rate, 4),
                "improvements": report.improvements,
                "regressions": report.regressions,
                "total_cases": report.total_cases,
            },
            "recommendation": report.recommendation,
            "recommendation_reason": report.recommendation_reason,
            "auto_apply": False,  # Jamais automatique — arbitrage humain
            "requires_human_approval": True,
        }


# === Singleton ===

rule_experiment = RuleExperiment()
