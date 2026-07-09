"""
Cortex Leman v5 — Review Loop

Boucle déterministe de re-vérification :
  Agent génère → Médiateur vérifie → Si problème → Agent corrige → Médiateur re-vérifie
  → Si toujours problème → Arbitrage humain

Max 3 itérations. Jamais plus.

Inspiré de:
  - Pluto/Greptile: LLM code review loop
  - Cortex diff: Le reviewer est DÉTERMINISTE (JsonLogic), pas LLM

Cycle:
  1. generate()  → LLM agent produit une sortie
  2. review()    → Médiateur évalue (rules_engine + code_reviewer)
  3. Si APPROVE  → terminé, journal WORM
  4. Si REQUEST_CHANGES → feedback injecté, agent re-génère (max 3x)
  5. Si NEEDS_ARBITRATION → gel + dossier envoyé à l'humain

Usage:
    from core.mediator.review_loop import review_loop

    result = await review_loop.execute(
        agent_name="reasoning",
        task="Analyser l'impact fiscal de cette opération",
        vertical="comptable",
        context={"montant": 50000},
    )
    # result.verdict = "approved" | "changes_requested" | "arbitration_required"
"""
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from core.mediator.rules_engine import rules_engine
from core.mediator.reviewer import code_reviewer, ReviewVerdict, FindingSeverity
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType
from core.bus.nats_client import bus

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 3


class LoopVerdict(str, Enum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    ARBITRATION_REQUIRED = "arbitration_required"
    ERROR = "error"


@dataclass
class LoopIteration:
    """Une itération de la boucle de review."""
    iteration: int
    verdict: str
    findings_count: int
    critical_count: int
    important_count: int
    rules_triggered: int
    feedback: str
    elapsed_ms: float


@dataclass
class LoopResult:
    """Résultat complet de la Review Loop."""
    verdict: LoopVerdict
    final_output: str
    iterations: list[LoopIteration] = field(default_factory=list)
    total_iterations: int = 0
    total_elapsed_ms: float = 0.0
    agent_name: str = ""
    model: str = ""
    vertical: str = ""
    trust_score: float = 1.0
    arbitration_reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "final_output": self.final_output,
            "total_iterations": self.total_iterations,
            "total_elapsed_ms": round(self.total_elapsed_ms, 0),
            "agent_name": self.agent_name,
            "model": self.model,
            "vertical": self.vertical,
            "trust_score": self.trust_score,
            "iterations": [
                {
                    "iteration": it.iteration,
                    "verdict": it.verdict,
                    "findings_count": it.findings_count,
                    "critical_count": it.critical_count,
                    "rules_triggered": it.rules_triggered,
                    "elapsed_ms": round(it.elapsed_ms, 0),
                }
                for it in self.iterations
            ],
            "arbitration_reason": self.arbitration_reason,
        }


def _build_correction_prompt(original_task: str, output: str, feedback_items: list[str], rules_feedback: list[str]) -> str:
    """Construire le prompt de correction pour l'agent LLM."""
    parts = [
        "⚠️ CORRECTION DEMANDÉE PAR LE MÉDIATEUR\n",
        "Votre réponse précédente a été jugée insatisfaisante par le Médiateur déterministe.\n",
        f"**Tâche originale:** {original_task}\n",
        "\n**Votre réponse précédente:**\n",
        output[:2000],
        "\n\n**Problèmes identifiés:**\n",
    ]

    for i, fb in enumerate(feedback_items, 1):
        parts.append(f"{i}. {fb}")

    if rules_feedback:
        parts.append("\n**Règles réglementaires violées:**\n")
        for rf in rules_feedback:
            parts.append(f"- {rf}")

    parts.append(
        "\n**Instructions:**\n"
        "Corrigez votre réponse en tenant compte de TOUS les points ci-dessus.\n"
        "Respectez scrupuleusement les règles RGPD, AI Act et le secret professionnel.\n"
        "Ne supprimez aucune information — ajoutez les mentions légales nécessaires.\n"
    )

    return "\n".join(parts)


class ReviewLoop:
    """
    Boucle de review déterministe Cortex.
    
    1. L'agent LLM génère une réponse
    2. Le Médiateur vérifie (rules_engine + code_reviewer)
    3. Si problème → feedback injecté → agent corrige
    4. Max 3 itérations puis arbitrage si toujours pas bon
    """

    def __init__(self):
        self._llm_service = None

    def _get_llm_service(self):
        """Lazy import du LLM service."""
        if self._llm_service is None:
            from core.integrations.llm import llm_service
            self._llm_service = llm_service
        return self._llm_service

    async def execute(
        self,
        agent_name: str,
        task: str,
        vertical: str,
        context: dict = None,
        client_id: str = "unknown",
        intention_id: str = None,
    ) -> LoopResult:
        """
        Exécuter la boucle de review complète.
        
        Args:
            agent_name: Nom de l'agent (reasoning, data, etc.)
            task: Tâche/texte de la requête
            vertical: Verticale métier
            context: Contexte additionnel
            client_id: ID client
            intention_id: ID de l'intention
        
        Returns:
            LoopResult avec verdict final
        """
        start_time = time.monotonic()
        context = context or {}
        result = LoopResult(
            verdict=LoopVerdict.ERROR,
            final_output="",
            agent_name=agent_name,
            vertical=vertical,
        )

        llm = self._get_llm_service()
        current_task = task

        for iteration in range(1, MAX_ITERATIONS + 1):
            iter_start = time.monotonic()

            # ── ÉTAPE 1: Génération LLM ──
            try:
                gen_result = await llm.generate_for_agent(
                    agent_name=agent_name,
                    task=current_task,
                    context={**context, "review_iteration": iteration},
                    vertical=vertical,
                    client_id=client_id,
                )
                output_text = gen_result.get("text", "")
                output_data = gen_result
                result.model = gen_result.get("model", result.model)
            except Exception as e:
                logger.error(f"Review Loop: erreur génération itération {iteration}: {e}")
                result.final_output = f"Erreur de génération: {e}"
                result.verdict = LoopVerdict.ERROR
                result.total_iterations = iteration
                result.total_elapsed_ms = (time.monotonic() - start_time) * 1000
                return result

            if not output_text:
                result.final_output = "Génération vide"
                result.verdict = LoopVerdict.ERROR
                result.total_iterations = iteration
                result.total_elapsed_ms = (time.monotonic() - start_time) * 1000
                return result

            # ── ÉTAPE 2: Review par le Médiateur ──
            # 2a: Rules Engine (100% déterministe, JsonLogic)
            rules_results = rules_engine.evaluate(vertical, {
                **context,
                "output_text": output_text,
                "action": "chat_response",
                "iteration": iteration,
            })
            rules_triggered = [r for r in rules_results if r.triggered]
            critical_rules = [r for r in rules_triggered if r.action in ("block", "freeze")]

            # 2b: Code Reviewer (structural checks)
            review_report = code_reviewer.review(
                agent_id=agent_name,
                output=output_data,
                context=context,
            )

            # ── ÉTAPE 3: Décision ──
            iter_elapsed = (time.monotonic() - iter_start) * 1000

            # Règles critiques = gel immédiat
            if critical_rules:
                iteration_record = LoopIteration(
                    iteration=iteration,
                    verdict="blocked_by_rules",
                    findings_count=review_report.findings_count if hasattr(review_report, 'findings_count') else len(review_report.findings),
                    critical_count=sum(1 for r in critical_rules),
                    important_count=0,
                    rules_triggered=len(rules_triggered),
                    feedback="; ".join(r.message for r in critical_rules),
                    elapsed_ms=iter_elapsed,
                )
                result.iterations.append(iteration_record)
                result.verdict = LoopVerdict.ARBITRATION_REQUIRED
                result.final_output = output_text
                result.arbitration_reason = (
                    f"Règle(s) critique(s) violée(s) après {iteration} itération(s): "
                    + "; ".join(r.rule_id for r in critical_rules)
                )
                result.total_iterations = iteration
                result.total_elapsed_ms = (time.monotonic() - start_time) * 1000
                result.trust_score = 0.0

                # Journaliser
                journal.append(
                    event_type=JournalEventType.MEDIATOR_CHECK,
                    client_id=client_id,
                    vertical=vertical,
                    agent_source="review_loop",
                    intention_id=intention_id,
                    payload={
                        "event": "review_loop_blocked",
                        "iteration": iteration,
                        "rules_blocked": [r.rule_id for r in critical_rules],
                        "verdict": "arbitration_required",
                    },
                )
                return result

            # Reviewer verdict
            if review_report.verdict == ReviewVerdict.APPROVE and not rules_triggered:
                # ✅ APPROUVÉ — aucune itération supplémentaire nécessaire
                iteration_record = LoopIteration(
                    iteration=iteration,
                    verdict="approved",
                    findings_count=len(review_report.findings),
                    critical_count=0,
                    important_count=sum(1 for f in review_report.findings if f.severity == FindingSeverity.IMPORTANT),
                    rules_triggered=0,
                    feedback="",
                    elapsed_ms=iter_elapsed,
                )
                result.iterations.append(iteration_record)
                result.verdict = LoopVerdict.APPROVED
                result.final_output = output_text
                result.total_iterations = iteration
                result.total_elapsed_ms = (time.monotonic() - start_time) * 1000
                result.trust_score = 1.0

                # Journaliser l'approbation
                journal.append(
                    event_type=JournalEventType.MEDIATOR_CHECK,
                    client_id=client_id,
                    vertical=vertical,
                    agent_source="review_loop",
                    intention_id=intention_id,
                    payload={
                        "event": "review_loop_approved",
                        "iteration": iteration,
                        "findings": len(review_report.findings),
                        "verdict": "approved",
                    },
                )
                return result

            elif review_report.verdict == ReviewVerdict.NEEDS_ARBITRATION:
                # ⚖️ ARBITRATION REQUISE — on n'essaie même pas de corriger
                iteration_record = LoopIteration(
                    iteration=iteration,
                    verdict="needs_arbitration",
                    findings_count=len(review_report.findings),
                    critical_count=sum(1 for f in review_report.findings if f.severity == FindingSeverity.CRITICAL),
                    important_count=sum(1 for f in review_report.findings if f.severity == FindingSeverity.IMPORTANT),
                    rules_triggered=len(rules_triggered),
                    feedback=review_report.summary,
                    elapsed_ms=iter_elapsed,
                )
                result.iterations.append(iteration_record)
                result.verdict = LoopVerdict.ARBITRATION_REQUIRED
                result.final_output = output_text
                result.arbitration_reason = review_report.summary
                result.total_iterations = iteration
                result.total_elapsed_ms = (time.monotonic() - start_time) * 1000
                result.trust_score = 0.0

                journal.append(
                    event_type=JournalEventType.MEDIATOR_CHECK,
                    client_id=client_id,
                    vertical=vertical,
                    agent_source="review_loop",
                    intention_id=intention_id,
                    payload={
                        "event": "review_loop_arbitration",
                        "iteration": iteration,
                        "critical_findings": sum(1 for f in review_report.findings if f.severity == FindingSeverity.CRITICAL),
                        "verdict": "arbitration_required",
                    },
                )
                return result

            else:
                # 🔄 CHANGEMENTS DEMANDÉS — on boucle
                feedback_items = [
                    f"[{f.severity.value}] {f.title}: {f.recommendation}"
                    for f in review_report.findings
                    if f.severity in (FindingSeverity.CRITICAL, FindingSeverity.IMPORTANT)
                ]
                rules_feedback = [
                    f"{r.rule_id}: {r.message} (action={r.action})"
                    for r in rules_triggered
                ]

                iteration_record = LoopIteration(
                    iteration=iteration,
                    verdict="changes_requested",
                    findings_count=len(review_report.findings),
                    critical_count=sum(1 for f in review_report.findings if f.severity == FindingSeverity.CRITICAL),
                    important_count=sum(1 for f in review_report.findings if f.severity == FindingSeverity.IMPORTANT),
                    rules_triggered=len(rules_triggered),
                    feedback="; ".join(feedback_items[:5]),
                    elapsed_ms=iter_elapsed,
                )
                result.iterations.append(iteration_record)

                logger.info(
                    f"Review Loop: itération {iteration} — {len(feedback_items)} problèmes, "
                    f"{len(rules_feedback)} règles → correction demandée"
                )

                # Préparer le prompt de correction pour la prochaine itération
                if iteration < MAX_ITERATIONS:
                    current_task = _build_correction_prompt(
                        original_task=task,
                        output=output_text,
                        feedback_items=feedback_items,
                        rules_feedback=rules_feedback,
                    )

        # ── Max iterations atteint → arbitrage ──
        result.verdict = LoopVerdict.ARBITRATION_REQUIRED
        result.final_output = output_text
        result.arbitration_reason = (
            f"Review Loop: {MAX_ITERATIONS} itérations atteintes sans approbation. "
            f"Dernier verdict: changes_requested. Arbitrage humain requis."
        )
        result.total_iterations = MAX_ITERATIONS
        result.total_elapsed_ms = (time.monotonic() - start_time) * 1000
        result.trust_score = 0.2

        journal.append(
            event_type=JournalEventType.MEDIATOR_CHECK,
            client_id=client_id,
            vertical=vertical,
            agent_source="review_loop",
            intention_id=intention_id,
            payload={
                "event": "review_loop_max_iterations",
                "iterations": MAX_ITERATIONS,
                "verdict": "arbitration_required",
            },
        )

        logger.warning(
            f"Review Loop: MAX ITERATIONS ({MAX_ITERATIONS}) atteintes "
            f"pour {vertical}/{agent_name} → arbitrage"
        )

        return result


# Singleton
review_loop = ReviewLoop()
