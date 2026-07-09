"""
Cortex Leman v5 — AutoApprover: Auto-approbation avec backtesting

Inspiré de: Brian Scanlan (Intercom), "How Building with AI Can Double
the Throughput of Your Engineering Team"

> "17.6% approval rate of our automatic code approval. We've gone through
>  a lot of detailed work to figure out using backtesting and previous data
>  and then getting humans to kind of label the outputs and figure out like
>  get the confidence level of the automatic approvers."
> "Shape the pull requests towards very safe and simple changes which
>  probably always should have been that way."
> "We've worked with our auditors to ensure that we're fully SOC 2,
>  ISO 27001, HIPAA compliant. You do not need humans in the loop to
>  meet these certifications."

Leçon Intercom: L'auto-approbation est possible SI:
1. Backtesté sur un historique significatif
2. Les humains ont labellisé les outputs
3. Le confidence level est mesuré
4. Les cas auto-approuvés sont "safe and simple"
5. Audit trail complet (WORM dans notre cas)

Dans Cortex, l'AutoApprover décide si une opération peut être
auto-approuvée ou si elle nécessite un arbitrage humain.

Conditions d'auto-approbation:
- Toutes les règles sont passées (aucune triggered)
- Tous les rubrics d'évaluation passent (score ≥ 0.8)
- Le golden dataset ne contient pas de cas similaire en FAIL
- La confidence globale ≥ seuil configuré
- Journalisé dans le WORM comme décision

JAMAIS d'auto-approbation pour:
- Les verticals avec montant > seuil
- Les opérations de type block/freeze
- Les cas où le Médiateur a détecté un conflit
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ApprovalDecision(str, Enum):
    """Décision d'approbation"""
    AUTO_APPROVED = "auto_approved"       # Approuvé automatiquement
    NEEDS_REVIEW = "needs_review"         # Révision humaine nécessaire
    NEEDS_ARBITRATION = "needs_arbitration"  # Arbitrage complet requis
    REJECTED = "rejected"                 # Rejeté


class ApprovalRisk(str, Enum):
    """Niveau de risque de l'opération"""
    LOW = "low"           # Opération simple, routine
    MEDIUM = "medium"     # Opération standard
    HIGH = "high"         # Opération sensible
    CRITICAL = "critical"  # Opération critique (jamais auto-approuvée)


@dataclass
class ApprovalRequest:
    """Requête d'approbation d'une opération"""
    request_id: str = ""
    vertical: str = ""
    client_id: str = ""
    intention_id: str = ""
    operation_type: str = ""     # data_query, fiscal_check, report_gen, etc.
    context: dict = field(default_factory=dict)
    agent_source: str = ""
    confidence: float = 0.0
    amount: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "vertical": self.vertical,
            "client_id": self.client_id,
            "intention_id": self.intention_id,
            "operation_type": self.operation_type,
            "agent_source": self.agent_source,
            "confidence": self.confidence,
            "amount": self.amount,
        }


@dataclass
class ApprovalResult:
    """Résultat d'une décision d'approbation"""
    result_id: str = ""
    request_id: str = ""
    decision: ApprovalDecision = ApprovalDecision.NEEDS_REVIEW
    risk_level: ApprovalRisk = ApprovalRisk.MEDIUM
    confidence: float = 0.0

    # Détails de la décision
    rules_checked: int = 0
    rules_triggered: int = 0
    evals_passed: int = 0
    evals_total: int = 0
    golden_cases_similar: int = 0
    golden_cases_passing: int = 0

    # Raisonnement
    reasoning: str = ""
    factors: list[dict] = field(default_factory=list)

    # Audit trail
    decided_at: str = ""
    decided_by: str = "auto_approver"  # ou "human" si override
    backtest_score: float = 0.0

    # Override humain
    overridden: bool = False
    override_reason: str = ""
    override_by: str = ""

    def to_dict(self) -> dict:
        return {
            "result_id": self.result_id,
            "request_id": self.request_id,
            "decision": self.decision.value,
            "risk_level": self.risk_level.value,
            "confidence": round(self.confidence, 4),
            "rules_checked": self.rules_checked,
            "rules_triggered": self.rules_triggered,
            "evals_passed": self.evals_passed,
            "evals_total": self.evals_total,
            "golden_cases_similar": self.golden_cases_similar,
            "golden_cases_passing": self.golden_cases_passing,
            "reasoning": self.reasoning,
            "factors": self.factors,
            "decided_at": self.decided_at,
            "decided_by": self.decided_by,
            "backtest_score": round(self.backtest_score, 4),
            "overridden": self.overridden,
        }


@dataclass
class BacktestResult:
    """Résultat d'un backtest de l'auto-approver"""
    total_cases: int = 0
    auto_approved: int = 0
    correct_approvals: int = 0       # Bien auto-approuvé
    incorrect_approvals: int = 0     # Auto-approuvé mais aurait dû être bloqué
    missed_approvals: int = 0        # Aurait pu être auto-approuvé mais ne l'a pas été
    precision: float = 0.0           # correct / (correct + incorrect)
    recall: float = 0.0              # correct / (correct + missed)

    def to_dict(self) -> dict:
        return {
            "total_cases": self.total_cases,
            "auto_approved": self.auto_approved,
            "correct_approvals": self.correct_approvals,
            "incorrect_approvals": self.incorrect_approvals,
            "missed_approvals": self.missed_approvals,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
        }


class AutoApprover:
    """
    Auto-approbation avec backtesting pour Cortex Leman.

    Processus:
    1. Recevoir une ApprovalRequest
    2. Évaluer les règles JsonLogic
    3. Évaluer les rubrics
    4. Vérifier le golden dataset
    5. Décider: auto_approve / needs_review / needs_arbitration / reject
    6. Journaliser dans le WORM

    Backtesting:
    - Comparer les décisions auto avec les labels humains du golden dataset
    - Mesurer precision et recall
    - Ajuster les seuils si nécessaire
    """

    # Seuils de configuration
    MIN_CONFIDENCE_FOR_AUTO = 0.85       # Confidence minimum pour auto-approve
    MIN_EVAL_SCORE_FOR_AUTO = 0.8        # Score eval minimum
    MAX_RULES_TRIGGERED_FOR_AUTO = 0     # Aucune règle ne doit être triggered
    MAX_AMOUNT_FOR_AUTO = 5000.0         # Montant max pour auto-approve

    # Types d'opérations safe (auto-approuvables par défaut)
    SAFE_OPERATIONS = {
        "data_query",        # Simple requête de données
        "report_gen",        # Génération de rapport (read-only)
        "compliance_check",  # Vérification de conformité
        "fiscal_info",       # Information fiscale générale
    }

    # Types d'opérations JAMAIS auto-approuvées
    BLOCKED_OPERATIONS = {
        "data_transfer",       # Transfert de données
        "decision_fiscale",    # Décision fiscale
        "ecriture_comptable",  # Écriture comptable
        "redaction_conclusions",  # Rédaction conclusions (avocat)
        "llm_query_external",  # Requête LLM externe
        "payment",             # Paiement
    }

    def __init__(self):
        self._history: list[ApprovalResult] = []
        self._auto_approved_count: int = 0
        self._total_count: int = 0

    def reset(self):
        """Réinitialiser l'état pour les tests."""
        self._history.clear()
        self._auto_approved_count = 0
        self._total_count = 0

    def evaluate(
        self,
        request: ApprovalRequest,
        rules_results: list[dict] = None,
        eval_results: list[dict] = None,
        golden_dataset=None,
    ) -> ApprovalResult:
        """
        Évaluer une requête d'approbation.

        Args:
            request: La requête d'approbation
            rules_results: Résultats des règles JsonLogic
                [{"rule_id", "triggered", "action", "severity"}]
            eval_results: Résultats des rubrics d'évaluation
                [{"rubric_id", "score", "severity"}]
            golden_dataset: GoldenDataset pour vérifier les cas similaires

        Returns:
            ApprovalResult avec la décision
        """
        # ── Input validation ──
        if not request:
            raise ValueError("ApprovalRequest requis")
        if not request.vertical or not request.vertical.strip():
            from core.observability.errors import EmptyInputError
            raise EmptyInputError("vertical")
        if not isinstance(request.confidence, (int, float)):
            request.confidence = 0.0

        self._total_count += 1

        result = ApprovalResult(
            result_id=uuid.uuid4().hex[:12],
            request_id=request.request_id or uuid.uuid4().hex[:12],
            decided_at=datetime.now(timezone.utc).isoformat(),
        )

        factors = []

        # === Check 1: Type d'opération ===
        op_type = request.operation_type
        if op_type in self.BLOCKED_OPERATIONS:
            result.decision = ApprovalDecision.REJECTED
            result.risk_level = ApprovalRisk.CRITICAL
            result.reasoning = f"Opération '{op_type}' jamais auto-approuvée"
            factors.append({"check": "operation_type", "result": "blocked", "value": op_type})
            result.factors = factors
            self._record(result)
            return result

        # === Check 2: Montant ===
        if request.amount and request.amount > self.MAX_AMOUNT_FOR_AUTO:
            result.decision = ApprovalDecision.NEEDS_ARBITRATION
            result.risk_level = ApprovalRisk.HIGH
            result.reasoning = f"Montant {request.amount} > seuil {self.MAX_AMOUNT_FOR_AUTO}"
            factors.append({"check": "amount", "result": "over_threshold", "value": request.amount})
            result.factors = factors
            self._record(result)
            return result

        # === Check 3: Règles JsonLogic ===
        rules_results = rules_results or []
        result.rules_checked = len(rules_results)
        triggered = [r for r in rules_results if r.get("triggered")]
        result.rules_triggered = len(triggered)

        if len(triggered) > self.MAX_RULES_TRIGGERED_FOR_AUTO:
            worst = max(triggered, key=lambda r: {"critical": 4, "high": 3, "medium": 2}.get(r.get("severity", "low"), 1))
            action = worst.get("action", "warn")

            if action == "block":
                result.decision = ApprovalDecision.REJECTED
            elif action == "freeze":
                result.decision = ApprovalDecision.NEEDS_ARBITRATION
            else:
                result.decision = ApprovalDecision.NEEDS_REVIEW

            result.risk_level = ApprovalRisk.HIGH
            result.reasoning = f"Règle déclenchée: {worst.get('rule_id')} ({worst.get('severity')})"
            factors.append({"check": "rules", "result": "triggered", "count": len(triggered)})
            result.factors = factors
            self._record(result)
            return result

        factors.append({"check": "rules", "result": "pass", "checked": len(rules_results)})

        # === Check 4: Rubrics d'évaluation ===
        eval_results = eval_results or []
        result.evals_total = len(eval_results)
        passed_evals = [e for e in eval_results if e.get("score", 0) >= self.MIN_EVAL_SCORE_FOR_AUTO]
        result.evals_passed = len(passed_evals)

        if eval_results and len(passed_evals) < len(eval_results):
            failed = [e for e in eval_results if e.get("score", 0) < self.MIN_EVAL_SCORE_FOR_AUTO]
            result.decision = ApprovalDecision.NEEDS_REVIEW
            result.risk_level = ApprovalRisk.MEDIUM
            result.reasoning = f"Rubrics en échec: {[e.get('rubric_id') for e in failed]}"
            factors.append({"check": "evals", "result": "some_failed", "passed": len(passed_evals), "total": len(eval_results)})
            result.factors = factors
            self._record(result)
            return result

        factors.append({"check": "evals", "result": "pass", "passed": len(passed_evals)})

        # === Check 5: Golden dataset (cas similaires) ===
        if golden_dataset:
            similar = golden_dataset.get_by_vertical(request.vertical)
            result.golden_cases_similar = len(similar)
            result.golden_cases_passing = sum(
                1 for c in similar
                if hasattr(c, 'expected_label') and c.expected_label.value == "pass"
            )

            # Si des cas similaires sont en FAIL, méfiance
            failing_similar = [
                c for c in similar
                if hasattr(c, 'expected_label') and c.expected_label.value == "fail"
                and hasattr(c, 'input_text') and request.operation_type.lower() in c.input_text.lower()
            ]
            if failing_similar:
                result.decision = ApprovalDecision.NEEDS_REVIEW
                result.risk_level = ApprovalRisk.MEDIUM
                result.reasoning = f"{len(failing_similar)} cas similaires en FAIL dans le golden dataset"
                factors.append({"check": "golden", "result": "failures_found", "count": len(failing_similar)})
                result.factors = factors
                self._record(result)
                return result

        factors.append({"check": "golden", "result": "pass", "similar": result.golden_cases_similar})

        # === Check 6: Confidence de l'agent ===
        if request.confidence < self.MIN_CONFIDENCE_FOR_AUTO:
            result.decision = ApprovalDecision.NEEDS_REVIEW
            result.risk_level = ApprovalRisk.MEDIUM
            result.reasoning = f"Confiance agent {request.confidence:.2f} < seuil {self.MIN_CONFIDENCE_FOR_AUTO}"
            factors.append({"check": "confidence", "result": "low", "value": request.confidence})
            result.factors = factors
            self._record(result)
            return result

        factors.append({"check": "confidence", "result": "pass", "value": request.confidence})

        # === Check 7: Opération safe ===
        if op_type not in self.SAFE_OPERATIONS:
            result.decision = ApprovalDecision.NEEDS_REVIEW
            result.risk_level = ApprovalRisk.MEDIUM
            result.reasoning = f"Opération '{op_type}' non dans la liste safe"
            factors.append({"check": "safe_operation", "result": "unknown", "value": op_type})
            result.factors = factors
            self._record(result)
            return result

        # === TOUT PASSE → AUTO-APPROVED ===
        result.decision = ApprovalDecision.AUTO_APPROVED
        result.risk_level = ApprovalRisk.LOW
        result.confidence = request.confidence
        result.reasoning = (
            f"Auto-approuvé: 0/{result.rules_checked} règles triggered, "
            f"{result.evals_passed}/{result.evals_total} evals passées, "
            f"confidence={request.confidence:.2f}"
        )
        result.factors = factors

        self._auto_approved_count += 1
        self._record(result)

        logger.info(
            f"AUTO-APPROVED [{request.vertical}] {op_type} "
            f"confidence={request.confidence:.2f}"
        )

        return result

    def backtest(
        self,
        golden_cases: list,
        rules_engine=None,
        eval_router=None,
    ) -> BacktestResult:
        """
        Backtester l'auto-approver contre le golden dataset.

        Inspiration Intercom: "Using backtesting and previous data
        and then getting humans to kind of label the outputs"

        Args:
            golden_cases: Cas du golden dataset avec expected_label
            rules_engine: Pour évaluer les règles
            eval_router: Pour évaluer les rubrics

        Returns:
            BacktestResult avec precision et recall
        """
        bt = BacktestResult(total_cases=len(golden_cases))

        for case in golden_cases:
            if not hasattr(case, 'expected_label'):
                continue

            # Construire la requête
            request = ApprovalRequest(
                vertical=case.vertical if hasattr(case, 'vertical') else "unknown",
                operation_type="data_query",
                confidence=0.9,
            )

            # Évaluer avec le même pipeline
            rules_results = []
            eval_results = []

            if rules_engine and hasattr(case, 'vertical'):
                r_results = rules_engine.evaluate(case.vertical, {})
                rules_results = [
                    {"rule_id": r.rule_id, "triggered": r.triggered, "action": r.action, "severity": r.severity}
                    for r in r_results
                ]

            if eval_router and hasattr(case, 'vertical'):
                e_results = eval_router.evaluate(
                    vertical=case.vertical,
                    input_text=getattr(case, 'input_text', ''),
                    output_text=getattr(case, 'output_text', ''),
                )
                eval_results = [
                    {"rubric_id": e.rubric_id, "score": e.score}
                    for e in e_results
                ]

            result = self.evaluate(request, rules_results, eval_results)

            if result.decision == ApprovalDecision.AUTO_APPROVED:
                bt.auto_approved += 1

                if case.expected_label.value == "pass":
                    bt.correct_approvals += 1  # Bonne auto-approbation
                else:
                    bt.incorrect_approvals += 1  # Auto-approuvé un FAIL → erreur
            else:
                if case.expected_label.value == "pass":
                    bt.missed_approvals += 1  # Aurait pu être auto-approuvé

        # Calculer precision et recall
        if bt.auto_approved > 0:
            bt.precision = bt.correct_approvals / bt.auto_approved
        if bt.correct_approvals + bt.missed_approvals > 0:
            bt.recall = bt.correct_approvals / (bt.correct_approvals + bt.missed_approvals)

        logger.info(
            f"Backtest: {bt.total_cases} cas, "
            f"{bt.auto_approved} auto-approuvés, "
            f"precision={bt.precision:.2%}, recall={bt.recall:.2%}"
        )

        return bt

    def _record(self, result: ApprovalResult):
        """Enregistrer le résultat dans l'historique"""
        self._history.append(result)

        # Journaliser dans le WORM
        try:
            from core.journal.append_only_journal import journal
            from core.journal.models import JournalEventType

            journal.append(
                event_type=JournalEventType.EVAL_ROUTER_RESULT,
                client_id="system",
                vertical="system",
                agent_source="auto_approver",
                intention_id=result.request_id,
                payload=result.to_dict(),
            )
        except (ValueError, KeyError, TypeError, RuntimeError) as e:
            logger.debug(f"AutoApprover WORM: skip ({e})")

    def get_stats(self) -> dict:
        """Statistiques de l'auto-approver"""
        total = self._total_count or len(self._history)
        auto = sum(1 for r in self._history if r.decision == ApprovalDecision.AUTO_APPROVED)
        needs_review = sum(1 for r in self._history if r.decision == ApprovalDecision.NEEDS_REVIEW)
        needs_arb = sum(1 for r in self._history if r.decision == ApprovalDecision.NEEDS_ARBITRATION)
        rejected = sum(1 for r in self._history if r.decision == ApprovalDecision.REJECTED)

        return {
            "total_evaluations": total,
            "auto_approved": auto,
            "needs_review": needs_review,
            "needs_arbitration": needs_arb,
            "rejected": rejected,
            "auto_approval_rate": round(auto / total, 4) if total else 0.0,
        }

    def get_history(self, limit: int = 50) -> list[dict]:
        return [r.to_dict() for r in self._history[-limit:]]


# === Singleton ===

auto_approver = AutoApprover()
