"""
Cortex Leman v5 — SessionMiner: Mining des traces pour améliorer les skills

Inspiré de: Brian Scanlan (Intercom), "How Building with AI Can Double
the Throughput of Your Engineering Team"

> "We pull in all session transcripts into S3 for data mining, writing
>  reports, guide like also looking to see our skills effective, that
>  kind of stuff."
> "We've got a feedback loop using the session data."

Leçon Intercom: Le WORM journal est une mine d'or. Intercom pompe les
session transcripts et les mine pour:
1. Mesurer l'efficacité des skills
2. Identifier les patterns de failure récurrents
3. Générer automatiquement des golden cases
4. Détecter les zones de friction

Dans Cortex, le SessionMiner lit le WORM journal et:
1. Analyse les patterns de success/failure par skill et vertical
2. Détecte les "dark corners" — zones sans traces (biais aveugle)
3. Génère automatiquement des golden cases depuis les traces
4. Mesure la corrélation entre confiance agent et résultat réel
5. Propose des améliorations de skills basées sur les données

Mode: LECTURE SEULE sur le WORM journal (jamais de modification)
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field
from collections import defaultdict


def _safe_payload(entry: dict) -> dict:
    """Extraire le payload d'une entrée, garantissant un dict."""
    p = entry.get('payload', {})
    return p if isinstance(p, dict) else {}

logger = logging.getLogger(__name__)


@dataclass
class SkillMetrics:
    """Métriques d'un skill depuis les traces"""
    skill_id: str = ""
    vertical: str = ""
    total_invocations: int = 0
    successful: int = 0           # Agent a réussi + pas de conflit
    failed: int = 0               # Agent a échoué OU conflit/gel
    blocked_by_mediator: int = 0  # Bloqué par le Médiateur
    avg_confidence: float = 0.0
    avg_resolution_time_ms: float = 0.0

    # Distribution par résultat
    pass_rate: float = 0.0
    conflict_rate: float = 0.0

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "vertical": self.vertical,
            "total_invocations": self.total_invocations,
            "successful": self.successful,
            "failed": self.failed,
            "blocked_by_mediator": self.blocked_by_mediator,
            "pass_rate": round(self.pass_rate, 4),
            "conflict_rate": round(self.conflict_rate, 4),
            "avg_confidence": round(self.avg_confidence, 4),
        }


@dataclass
class FailurePattern:
    """Pattern de failure récurrent détecté"""
    pattern_id: str = ""
    vertical: str = ""
    agent_source: str = ""
    failure_type: str = ""        # "low_confidence", "mediator_conflict", "timeout", "error"
    occurrence_count: int = 0
    first_seen: str = ""
    last_seen: str = ""
    sample_intentions: list[str] = field(default_factory=list)
    description: str = ""
    recommendation: str = ""

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "vertical": self.vertical,
            "agent_source": self.agent_source,
            "failure_type": self.failure_type,
            "occurrence_count": self.occurrence_count,
            "description": self.description,
            "recommendation": self.recommendation,
        }


@dataclass
class DarkCorner:
    """Zone aveugle — pas assez de traces pour un vertical/agent"""
    vertical: str = ""
    agent_source: str = ""
    total_traces: int = 0
    expected_minimum: int = 50
    description: str = ""
    risk: str = ""  # "high" si < 10 traces

    def to_dict(self) -> dict:
        return {
            "vertical": self.vertical,
            "agent_source": self.agent_source,
            "total_traces": self.total_traces,
            "expected_minimum": self.expected_minimum,
            "risk": self.risk,
            "description": self.description,
        }


@dataclass
class MiningReport:
    """Rapport complet du mining"""
    report_id: str = ""
    timestamp: str = ""
    total_entries_analyzed: int = 0
    period_days: int = 30

    # Métriques par skill
    skill_metrics: list[SkillMetrics] = field(default_factory=list)

    # Patterns de failure
    failure_patterns: list[FailurePattern] = field(default_factory=list)

    # Zones aveugles
    dark_corners: list[DarkCorner] = field(default_factory=list)

    # Golden cases candidats
    golden_case_candidates: list[dict] = field(default_factory=list)

    # Corrélations
    confidence_vs_success: dict = field(default_factory=dict)

    # Recommandations
    recommendations: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "total_entries_analyzed": self.total_entries_analyzed,
            "period_days": self.period_days,
            "skill_metrics": [m.to_dict() for m in self.skill_metrics],
            "failure_patterns": [p.to_dict() for p in self.failure_patterns],
            "dark_corners": [d.to_dict() for d in self.dark_corners],
            "golden_case_candidates": self.golden_case_candidates,
            "confidence_vs_success": self.confidence_vs_success,
            "recommendations": self.recommendations,
        }


class SessionMiner:
    """
    Mineur de traces depuis le WORM journal.

    Analyse les traces pour:
    1. Mesurer l'efficacité des skills par vertical
    2. Détecter les patterns de failure récurrents
    3. Identifier les zones aveugles (pas assez de données)
    4. Générer des golden cases candidats
    5. Mesurer la corrélation confidence → succès

    Usage:
        miner = SessionMiner()
        report = miner.mine(journal_entries)
        # report contient les insights
    """

    MIN_TRACES_FOR_CONFIDENCE = 20
    HIGH_FAILURE_RATE = 0.3
    LOW_TRACE_THRESHOLD = 10

    def mine(
        self,
        journal_entries: list[dict],
        period_days: int = 30,
    ) -> MiningReport:
        """
        Miner les entrées du journal WORM.

        Args:
            journal_entries: Entrées du journal WORM
            period_days: Période d'analyse

        Returns:
            MiningReport avec les insights
        """
        report = MiningReport(
            report_id=uuid.uuid4().hex[:12],
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_entries_analyzed=len(journal_entries),
            period_days=period_days,
        )

        if not journal_entries:
            return report

        # === Phase 1: Agréger par vertical × agent ===
        by_vertical_agent: dict[tuple, list] = defaultdict(list)
        by_event_type: dict[str, list] = defaultdict(list)
        by_intention: dict[str, list] = defaultdict(list)

        for entry in journal_entries:
            v = entry.get("vertical", "unknown")
            a = entry.get("agent_source", "unknown")
            et = entry.get("event_type", "unknown")
            iid = entry.get("intention_id", "")

            by_vertical_agent[(v, a)].append(entry)
            by_event_type[et].append(entry)
            if iid:
                by_intention[iid].append(entry)

        # === Phase 2: Métriques par skill/vertical ===
        report.skill_metrics = self._compute_skill_metrics(
            by_vertical_agent, by_event_type
        )

        # === Phase 3: Patterns de failure ===
        report.failure_patterns = self._detect_failure_patterns(
            by_vertical_agent, by_intention
        )

        # === Phase 4: Zones aveugles ===
        report.dark_corners = self._detect_dark_corners(
            by_vertical_agent
        )

        # === Phase 5: Golden cases candidats ===
        report.golden_case_candidates = self._generate_golden_candidates(
            by_intention
        )

        # === Phase 6: Corrélation confidence → succès ===
        report.confidence_vs_success = self._compute_confidence_correlation(
            journal_entries, by_intention
        )

        # === Phase 7: Recommandations ===
        report.recommendations = self._generate_recommendations(report)

        return report

    def _compute_skill_metrics(
        self,
        by_vertical_agent: dict,
        by_event_type: dict,
    ) -> list[SkillMetrics]:
        """Calculer les métriques par vertical/agent"""
        metrics = []

        for (vertical, agent), entries in by_vertical_agent.items():
            total = len(entries)

            # Compter les succès et failures
            conflicts = len([
                e for e in entries
                if e.get("event_type") in ("mediator_conflict", "mediator.conflict", "mediator.freeze", "mediator_freeze")
            ])
            errors = len([
                e for e in entries
                if e.get("event_type") in ("agent_error", "agent.error")
            ])
            results = [
                e for e in entries
                if e.get("event_type") in ("agent_result", "agent.result")
            ]

            # Confidence moyenne
            confidences = [
                _safe_payload(e).get("confidence", 0.0)
                for e in results
                if isinstance(e.get("payload"), dict)
                and isinstance(_safe_payload(e).get("confidence"), (int, float))
            ]
            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

            successful = len(results) - conflicts
            failed = conflicts + errors

            m = SkillMetrics(
                skill_id=f"{vertical}:{agent}",
                vertical=vertical,
                total_invocations=total,
                successful=max(0, successful),
                failed=failed,
                blocked_by_mediator=conflicts,
                avg_confidence=avg_conf,
                pass_rate=successful / total if total else 0.0,
                conflict_rate=conflicts / total if total else 0.0,
            )
            metrics.append(m)

        return metrics

    def _detect_failure_patterns(
        self,
        by_vertical_agent: dict,
        by_intention: dict,
    ) -> list[FailurePattern]:
        """Détecter les patterns de failure récurrents"""
        patterns = []

        for (vertical, agent), entries in by_vertical_agent.items():
            # Pattern 1: Taux de conflit élevé
            conflicts = [
                e for e in entries
                if e.get("event_type") in ("mediator_conflict", "mediator.conflict")
            ]
            if len(conflicts) > self.HIGH_FAILURE_RATE * len(entries) and len(entries) >= 10:
                # Grouper par reason
                reasons: dict[str, list] = defaultdict(list)
                for c in conflicts:
                    reason = _safe_payload(c).get("reason", "unknown")[:100]
                    reasons[reason].append(c.get("intention_id", ""))

                for reason, intention_ids in sorted(reasons.items(), key=lambda x: -len(x[1])):
                    patterns.append(FailurePattern(
                        pattern_id=uuid.uuid4().hex[:8],
                        vertical=vertical,
                        agent_source=agent,
                        failure_type="mediator_conflict",
                        occurrence_count=len(intention_ids),
                        first_seen=entries[0].get("timestamp", ""),
                        last_seen=entries[-1].get("timestamp", ""),
                        sample_intentions=intention_ids[:5],
                        description=f"{vertical}/{agent}: {len(intention_ids)} conflits même cause",
                        recommendation=f"Investiguer le pattern: '{reason[:80]}'. "
                                       f"Ajuster les règles ou le prompt de l'agent.",
                    ))

            # Pattern 2: Basse confidence récurrente
            low_conf = [
                e for e in entries
                if isinstance(_safe_payload(e).get("confidence"), (int, float))
                and _safe_payload(e).get("confidence", 1.0) < 0.5
            ]
            if len(low_conf) > len(entries) * 0.3 and len(entries) >= 10:
                patterns.append(FailurePattern(
                    pattern_id=uuid.uuid4().hex[:8],
                    vertical=vertical,
                    agent_source=agent,
                    failure_type="low_confidence",
                    occurrence_count=len(low_conf),
                    description=f"{vertical}/{agent}: {len(low_conf)} résultats à confiance < 0.5",
                    recommendation=f"Vérifier les sources de données et le prompt de l'agent {agent} "
                                   f"pour la verticale {vertical}.",
                ))

            # Pattern 3: Erreurs récurrentes
            errors = [
                e for e in entries
                if e.get("event_type") in ("agent_error", "agent.error")
            ]
            if len(errors) > 3:
                patterns.append(FailurePattern(
                    pattern_id=uuid.uuid4().hex[:8],
                    vertical=vertical,
                    agent_source=agent,
                    failure_type="error",
                    occurrence_count=len(errors),
                    description=f"{vertical}/{agent}: {len(errors)} erreurs techniques",
                    recommendation=f"Investiguer les erreurs de l'agent {agent}. "
                                   f"Possible problème de connectivité ou de configuration.",
                ))

        return patterns

    def _detect_dark_corners(
        self,
        by_vertical_agent: dict,
    ) -> list[DarkCorner]:
        """Détecter les zones sans assez de traces"""
        corners = []

        # Vérifier les 6 verticals × agents principaux
        expected_verticals = {"comptable", "avocat", "banque", "sante", "rh", "startup"}
        expected_agents = {"data", "reasoning", "action"}

        for v in expected_verticals:
            for a in expected_agents:
                count = len(by_vertical_agent.get((v, a), []))

                if count < self.LOW_TRACE_THRESHOLD:
                    corners.append(DarkCorner(
                        vertical=v,
                        agent_source=a,
                        total_traces=count,
                        risk="high" if count < 5 else "medium",
                        description=f"{v}/{a}: seulement {count} traces. "
                                    f"Impossible de mesurer la qualité.",
                    ))

        return corners

    def _generate_golden_candidates(
        self,
        by_intention: dict,
    ) -> list[dict]:
        """
        Générer des candidats golden cases depuis les traces.

        Les bonnes intentions (haute confiance, pas de conflit) → PASS candidates
        Les intentions qui ont gelé → FAIL candidates
        """
        candidates = []

        for intention_id, entries in by_intention.items():
            if len(entries) < 2:
                continue

            has_conflict = any(
                e.get("event_type") in ("mediator_conflict", "mediator.conflict", "mediator_freeze", "mediator.freeze")
                for e in entries
            )
            has_result = any(
                e.get("event_type") in ("agent_result", "agent.result")
                for e in entries
            )

            if not has_result:
                continue

            # Trouver le résultat principal
            result_entries = [
                e for e in entries
                if e.get("event_type") in ("agent_result", "agent.result")
            ]

            if not result_entries:
                continue

            main_result = result_entries[-1]
            confidence = _safe_payload(main_result).get("confidence", 0.0)
            vertical = main_result.get("vertical", "unknown")

            # Trouver l'input (intention créée)
            input_entries = [
                e for e in entries
                if e.get("event_type") in ("intention_created", "intention.created")
            ]
            input_text = ""
            if input_entries:
                input_text = _safe_payload(input_entries[0]).get("original_query", "")

            # Trouver l'output
            output_text = _safe_payload(main_result).get("result", "")

            if has_conflict:
                # FAIL candidate — a été gelé
                candidates.append({
                    "vertical": vertical,
                    "input_text": input_text or f"intention {intention_id[:8]}",
                    "output_text": str(output_text)[:500],
                    "expected_label": "fail",
                    "origin": "session_mining",
                    "source_intention_id": intention_id,
                    "justification": f"Gel détecté — confiance={confidence:.2f}",
                })
            elif confidence >= 0.8 and input_text:
                # PASS candidate — haute confiance, pas de conflit
                candidates.append({
                    "vertical": vertical,
                    "input_text": input_text,
                    "output_text": str(output_text)[:500],
                    "expected_label": "pass",
                    "origin": "session_mining",
                    "source_intention_id": intention_id,
                    "justification": f"Réussite — confiance={confidence:.2f}",
                })

        return candidates

    def _compute_confidence_correlation(
        self,
        entries: list[dict],
        by_intention: dict,
    ) -> dict:
        """
        Mesurer la corrélation entre confidence de l'agent et résultat réel.

        Répond à la question: "Quand l'agent dit 0.9 de confiance,
        est-ce que c'est vraiment correct 90% du temps ?"
        """
        # Grouper par bucket de confidence
        buckets: dict[str, dict] = {
            "0.0-0.3": {"total": 0, "success": 0},
            "0.3-0.5": {"total": 0, "success": 0},
            "0.5-0.7": {"total": 0, "success": 0},
            "0.7-0.85": {"total": 0, "success": 0},
            "0.85-1.0": {"total": 0, "success": 0},
        }

        for intention_id, i_entries in by_intention.items():
            # Trouver la confidence
            conf = None
            for e in i_entries:
                c = _safe_payload(e).get("confidence")
                if isinstance(c, (int, float)):
                    conf = float(c)
                    break

            if conf is None:
                continue

            # Trouver le bucket
            if conf < 0.3:
                bucket = "0.0-0.3"
            elif conf < 0.5:
                bucket = "0.3-0.5"
            elif conf < 0.7:
                bucket = "0.5-0.7"
            elif conf < 0.85:
                bucket = "0.7-0.85"
            else:
                bucket = "0.85-1.0"

            # Déterminer le succès
            has_conflict = any(
                e.get("event_type") in ("mediator_conflict", "mediator.conflict")
                for e in i_entries
            )

            buckets[bucket]["total"] += 1
            if not has_conflict:
                buckets[bucket]["success"] += 1

        # Calculer les taux
        correlation = {}
        for bucket, data in buckets.items():
            if data["total"] > 0:
                correlation[bucket] = {
                    "total": data["total"],
                    "success_rate": round(data["success"] / data["total"], 4),
                    "calibrated": abs(
                        data["success"] / data["total"] -
                        float(bucket.split("-")[1])
                    ) < 0.15 if data["total"] > 5 else None,
                }

        return correlation

    def _generate_recommendations(self, report: MiningReport) -> list[dict]:
        """Générer des recommandations depuis les insights"""
        recs = []

        # Rec 1: Skills défaillants
        failing_skills = [
            m for m in report.skill_metrics
            if m.pass_rate < 0.7 and m.total_invocations >= 10
        ]
        for skill in failing_skills:
            recs.append({
                "priority": "high",
                "category": "skill_improvement",
                "title": f"Skill {skill.skill_id}: pass rate {skill.pass_rate:.0%}",
                "action": f"Investiguer les failures dans {skill.vertical}/{skill.skill_id}. "
                          f"Le taux de conflit est de {skill.conflict_rate:.0%}.",
            })

        # Rec 2: Zones aveugles
        dark = [d for d in report.dark_corners if d.risk == "high"]
        if dark:
            recs.append({
                "priority": "high",
                "category": "data_gap",
                "title": f"{len(dark)} zones aveugles détectées",
                "action": "Générer des traces synthétiques ou augmenter le traffic "
                          "dans ces zones pour pouvoir mesurer la qualité.",
            })

        # Rec 3: Patterns de failure
        critical_patterns = [
            p for p in report.failure_patterns
            if p.occurrence_count >= 5
        ]
        if critical_patterns:
            recs.append({
                "priority": "medium",
                "category": "failure_pattern",
                "title": f"{len(critical_patterns)} patterns de failure récurrents",
                "action": "Examiner les patterns et ajuster les règles/prompts.",
                "details": [p.description for p in critical_patterns[:5]],
            })

        # Rec 4: Golden cases candidats
        fail_candidates = [
            c for c in report.golden_case_candidates
            if c.get("expected_label") == "fail"
        ]
        pass_candidates = [
            c for c in report.golden_case_candidates
            if c.get("expected_label") == "pass"
        ]
        recs.append({
            "priority": "low",
            "category": "golden_dataset",
            "title": f"{len(fail_candidates)} FAIL + {len(pass_candidates)} PASS candidats",
            "action": f"Review et annoter les {len(report.golden_case_candidates)} candidats "
                      f"avant ajout au golden dataset.",
        })

        # Rec 5: Calibration confidence
        cal = report.confidence_vs_success
        miscalibrated = [
            bucket for bucket, data in cal.items()
            if data.get("calibrated") is False
        ]
        if miscalibrated:
            recs.append({
                "priority": "medium",
                "category": "calibration",
                "title": f"Confidence mal calibrée: {miscalibrated}",
                "action": "La confiance agent ne correspond pas au taux de succès réel. "
                          "Ajuster les prompts ou les seuils de confiance.",
            })

        return recs


# === Singleton ===

session_miner = SessionMiner()
