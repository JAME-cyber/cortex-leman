"""
Cortex Leman v5 — Observe Skill: Diagnostic automatisé depuis le journal WORM

Agent d'analyse qui lit le journal WORM et diagnostique:
1. Détection de dérive (confiance, gels, conflits)
2. Analyse des échecs récurrents
3. Recommandations actionnables
4. Dashboard exposure via API

Mode: LECTURE SEULE sur le journal WORM
Jamais de modification du système en automatique.

Inspiré de: "Mind the Gap" — Nitya Narasimhan (Microsoft Foundry)
> "It's what we don't know that hurts us. It's not about I don't even know what I don't know."
> "What this does is exposes me to what I don't know."
"""
import json
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class DriftSignal:
    """Signal de dérive détecté dans le journal"""
    signal_id: str = ""
    signal_type: str = ""         # "confidence_drop", "freeze_spike", "agent_degradation"
    vertical: str = ""
    agent_source: str = ""
    severity: str = ""            # "info", "warning", "critical"
    metric_name: str = ""
    metric_value: float = 0.0
    baseline_value: float = 0.0
    deviation_pct: float = 0.0
    description: str = ""
    recommendation: str = ""
    detected_at: str = ""
    affected_intentions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
            "vertical": self.vertical,
            "agent_source": self.agent_source,
            "severity": self.severity,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "baseline_value": self.baseline_value,
            "deviation_pct": round(self.deviation_pct, 2),
            "description": self.description,
            "recommendation": self.recommendation,
            "detected_at": self.detected_at,
            "affected_intentions": self.affected_intentions[:10],
        }


@dataclass
class ObserveDashboard:
    """Dashboard d'observabilité Cortex Leman"""
    generated_at: str = ""
    period_days: int = 30
    total_intentions: int = 0
    total_conflicts: int = 0
    total_freezes: int = 0
    total_arbitrations: int = 0
    avg_confidence: float = 0.0
    avg_resolution_time_ms: float = 0.0

    # Par verticale
    vertical_metrics: dict = field(default_factory=dict)

    # Par agent
    agent_metrics: dict = field(default_factory=dict)

    # Signaux de dérive
    drift_signals: list[DriftSignal] = field(default_factory=list)

    # Top risques
    top_risks: list[dict] = field(default_factory=list)

    # Recommandations
    recommendations: list[dict] = field(default_factory=list)

    @property
    def health_score(self) -> float:
        """Score de santé global (0-100)"""
        if self.total_intentions == 0:
            return 100.0

        # Facteurs négatifs
        conflict_rate = self.total_conflicts / self.total_intentions
        freeze_rate = self.total_freezes / self.total_intentions
        critical_signals = sum(1 for s in self.drift_signals if s.severity == "critical")

        # Score de base
        score = 100.0

        # Pénalités
        score -= conflict_rate * 20       # Chaque conflit coûte
        score -= freeze_rate * 15         # Chaque gel coûte
        score -= critical_signals * 10    # Signaux critiques
        score -= max(0, (1 - self.avg_confidence) * 30)  # Confiance basse

        return max(0, min(100, round(score, 1)))

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "period_days": self.period_days,
            "health_score": self.health_score,
            "summary": {
                "total_intentions": self.total_intentions,
                "total_conflicts": self.total_conflicts,
                "total_freezes": self.total_freezes,
                "total_arbitrations": self.total_arbitrations,
                "avg_confidence": round(self.avg_confidence, 3),
                "avg_resolution_time_ms": round(self.avg_resolution_time_ms, 1),
            },
            "vertical_metrics": self.vertical_metrics,
            "agent_metrics": self.agent_metrics,
            "drift_signals": [s.to_dict() for s in self.drift_signals],
            "top_risks": self.top_risks[:10],
            "recommendations": self.recommendations,
        }


class ObserveSkill:
    """
    Observe Skill pour Cortex Leman v5.

    Analyse le journal WORM pour:
    - Détecter les dérives de confiance par verticale
    - Identifier les patterns d'échec récurrents
    - Mesurer les temps de résolution d'arbitrage
    - Proposer des améliorations concrètes

    Usage:
        skill = ObserveSkill()
        dashboard = skill.generate_dashboard(journal_entries, days=30)
        signals = skill.detect_drift(journal_entries)
    """

    # Seuils de détection de dérive
    CONFIDENCE_DROP_THRESHOLD = 0.15      # -15% de confiance = signal
    FREEZE_SPIKE_THRESHOLD = 3.0          # 3x la normale = signal
    STALE_AGENT_THRESHOLD_SEC = 300       # Agent inactif >5min
    HIGH_CONFLICT_RATE = 0.3              # >30% de taux de conflit

    def generate_dashboard(
        self,
        journal_entries: list[dict],
        days: int = 30,
    ) -> ObserveDashboard:
        """
        Générer le dashboard d'observabilité à partir des entrées du journal.

        Args:
            journal_entries: Entrées du journal WORM
                [{"event_type", "client_id", "vertical", "agent_source",
                  "intention_id", "timestamp", "payload"}]
            days: Période d'analyse en jours

        Returns:
            Dashboard complet
        """
        dashboard = ObserveDashboard(
            generated_at=datetime.now(timezone.utc).isoformat(),
            period_days=days,
        )

        if not journal_entries:
            return dashboard

        # === Agrégation par type d'événement ===
        by_type = defaultdict(list)
        by_vertical = defaultdict(list)
        by_agent = defaultdict(list)
        by_intention = defaultdict(list)

        for entry in journal_entries:
            event_type = entry.get("event_type", "unknown")
            vertical = entry.get("vertical", "unknown")
            agent = entry.get("agent_source", "unknown")
            intention_id = entry.get("intention_id", "")

            by_type[event_type].append(entry)
            by_vertical[vertical].append(entry)
            by_agent[agent].append(entry)
            if intention_id:
                by_intention[intention_id].append(entry)

        # === Métriques globales ===
        intentions = {e.get("intention_id") for e in journal_entries if e.get("intention_id")}
        dashboard.total_intentions = len(intentions)
        dashboard.total_conflicts = len([e for e in by_type.get("mediator_conflict", [])] + by_type.get("mediator.conflict", []))
        dashboard.total_freezes = len([e for e in by_type.get("mediator_freeze", [])] + by_type.get("mediator.freeze", []))
        dashboard.total_arbitrations = len([e for e in by_type.get("arbitration_decision", [])] + by_type.get("arbitration.decision", []))

        # Confiance moyenne
        all_confidences = [
            e.get("payload", {}).get("confidence", 0.0)
            for e in journal_entries
            if isinstance(e.get("payload", {}).get("confidence"), (int, float))
        ]
        dashboard.avg_confidence = (
            sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        )

        # === Métriques par verticale ===
        for vertical, entries in by_vertical.items():
            v_intentions = {e.get("intention_id") for e in entries if e.get("intention_id")}
            v_conflicts = len([e for e in entries if e.get("event_type") in ("mediator_conflict", "mediator.conflict")])
            v_freezes = len([e for e in entries if e.get("event_type") in ("mediator_freeze", "mediator.freeze")])
            v_confidences = [
                e.get("payload", {}).get("confidence", 0.0)
                for e in entries
                if isinstance(e.get("payload", {}).get("confidence"), (int, float))
            ]
            avg_conf = sum(v_confidences) / len(v_confidences) if v_confidences else 0.0

            dashboard.vertical_metrics[vertical] = {
                "intentions": len(v_intentions),
                "conflicts": v_conflicts,
                "freezes": v_freezes,
                "conflict_rate": round(v_conflicts / len(v_intentions), 3) if v_intentions else 0,
                "avg_confidence": round(avg_conf, 3),
            }

        # === Métriques par agent ===
        for agent, entries in by_agent.items():
            agent_confidences = [
                e.get("payload", {}).get("confidence", 0.0)
                for e in entries
                if isinstance(e.get("payload", {}).get("confidence"), (int, float))
            ]
            avg_conf = sum(agent_confidences) / len(agent_confidences) if agent_confidences else 0.0

            dashboard.agent_metrics[agent] = {
                "events": len(entries),
                "avg_confidence": round(avg_conf, 3),
                "low_confidence_count": sum(1 for c in agent_confidences if c < 0.5),
            }

        # === Détection de dérive ===
        dashboard.drift_signals = self.detect_drift(journal_entries, dashboard)

        # === Top risques ===
        dashboard.top_risks = self._compute_top_risks(journal_entries, by_vertical)

        # === Recommandations ===
        dashboard.recommendations = self._generate_recommendations(dashboard)

        return dashboard

    def detect_drift(
        self,
        journal_entries: list[dict],
        dashboard: ObserveDashboard = None,
    ) -> list[DriftSignal]:
        """
        Détecter les signaux de dérive dans le journal.

        Types de signaux:
        - confidence_drop: Confiance en baisse significative
        - freeze_spike: Pic de gels sur une verticale
        - agent_degradation: Agent avec confiance basse récurrente
        - unresolved_conflict: Conflits sans résolution
        """
        signals = []

        if not journal_entries:
            return signals

        # Grouper par verticale
        by_vertical = defaultdict(list)
        for entry in journal_entries:
            by_vertical[entry.get("vertical", "unknown")].append(entry)

        # === Signal 1: Taux de gel élevé par verticale ===
        if dashboard:
            for vertical, metrics in dashboard.vertical_metrics.items():
                conflict_rate = metrics.get("conflict_rate", 0)
                if conflict_rate > self.HIGH_CONFLICT_RATE:
                    signals.append(DriftSignal(
                        signal_id=uuid.uuid4().hex[:8],
                        signal_type="freeze_spike",
                        vertical=vertical,
                        severity="warning" if conflict_rate < 0.5 else "critical",
                        metric_name="conflict_rate",
                        metric_value=conflict_rate,
                        baseline_value=self.HIGH_CONFLICT_RATE,
                        deviation_pct=((conflict_rate - self.HIGH_CONFLICT_RATE) / self.HIGH_CONFLICT_RATE) * 100,
                        description=f"Verticale {vertical}: taux de conflit {conflict_rate:.0%} (seuil: {self.HIGH_CONFLICT_RATE:.0%})",
                        recommendation=f"Vérifier les règles du Médiateur pour {vertical}. "
                                       f"Ajuster les seuils si les conflits sont des faux positifs.",
                        detected_at=datetime.now(timezone.utc).isoformat(),
                    ))

        # === Signal 2: Agent avec confiance basse ===
        by_agent = defaultdict(list)
        for entry in journal_entries:
            if entry.get("agent_source"):
                by_agent[entry["agent_source"]].append(entry)

        for agent, entries in by_agent.items():
            low_conf = [
                e for e in entries
                if isinstance(e.get("payload", {}).get("confidence"), (int, float))
                and e.get("payload", {}).get("confidence", 1.0) < 0.5
            ]
            if len(low_conf) > len(entries) * 0.3:  # >30% de résultats à basse confiance
                signals.append(DriftSignal(
                    signal_id=uuid.uuid4().hex[:8],
                    signal_type="agent_degradation",
                    agent_source=agent,
                    severity="warning",
                    metric_name="low_confidence_rate",
                    metric_value=len(low_conf) / len(entries),
                    baseline_value=0.3,
                    deviation_pct=((len(low_conf) / len(entries)) - 0.3) / 0.3 * 100,
                    description=f"Agent {agent}: {len(low_conf)}/{len(entries)} résultats à confiance < 0.5",
                    recommendation=f"Investiguer les sources de données de l'agent {agent}. "
                                   f"Vérifier si les LLM prompts sont optimaux.",
                    detected_at=datetime.now(timezone.utc).isoformat(),
                ))

        # === Signal 3: Conflits sans arbitrage ===
        conflict_intentions = {
            e.get("intention_id") for e in journal_entries
            if e.get("event_type") in ("mediator_conflict", "mediator.conflict") and e.get("intention_id")
        }
        resolved_intentions = {
            e.get("intention_id") for e in journal_entries
            if e.get("event_type") in ("arbitration_decision", "arbitration.decision") and e.get("intention_id")
        }
        unresolved = conflict_intentions - resolved_intentions
        if unresolved:
            signals.append(DriftSignal(
                signal_id=uuid.uuid4().hex[:8],
                signal_type="unresolved_conflict",
                severity="critical",
                metric_name="unresolved_conflicts",
                metric_value=len(unresolved),
                baseline_value=0,
                deviation_pct=100,
                description=f"{len(unresolved)} conflits sans résolution d'arbitrage",
                recommendation="Vérifier le processus d'arbitrage. "
                               "Les intentions gelées doivent être résolues par un humain.",
                detected_at=datetime.now(timezone.utc).isoformat(),
                affected_intentions=list(unresolved)[:10],
            ))

        return signals

    def _compute_top_risks(
        self,
        journal_entries: list[dict],
        by_vertical: dict,
    ) -> list[dict]:
        """Calculer les top risques"""
        risks = []

        # Risk 1: Verticale avec le plus de conflits
        for vertical, entries in by_vertical.items():
            conflicts = len([e for e in entries if e.get("event_type") == "mediator_conflict"])
            if conflicts > 0:
                risks.append({
                    "type": "high_conflict_vertical",
                    "vertical": vertical,
                    "count": conflicts,
                    "severity": "high" if conflicts > 10 else "medium",
                })

        # Risk 2: Pattern d'attaque récurrent
        attack_events = [
            e for e in journal_entries
            if "injection" in json.dumps(e.get("payload", {})).lower()
            or "bypass" in json.dumps(e.get("payload", {})).lower()
        ]
        if attack_events:
            risks.append({
                "type": "recurring_attack_pattern",
                "count": len(attack_events),
                "severity": "critical",
                "description": "Patterns d'attaque récurrents détectés dans le journal",
            })

        # Trier par sévérité puis par count
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        risks.sort(key=lambda r: (severity_order.get(r.get("severity", "low"), 99), -r.get("count", 0)))

        return risks

    def _generate_recommendations(self, dashboard: ObserveDashboard) -> list[dict]:
        """Générer des recommandations actionnables"""
        recs = []

        # Rec 1: Health score bas
        if dashboard.health_score < 60:
            recs.append({
                "priority": "critical",
                "category": "overall_health",
                "title": f"Score de santé critique: {dashboard.health_score}/100",
                "action": "Examen immédiat requis. Plusieurs indicateurs sont dégradés.",
                "auto_fixable": False,
            })

        # Rec 2: Verticale problématique
        for vertical, metrics in dashboard.vertical_metrics.items():
            if metrics.get("conflict_rate", 0) > 0.5:
                recs.append({
                    "priority": "high",
                    "category": "vertical_conflict",
                    "title": f"Verticale {vertical}: {metrics['conflict_rate']:.0%} de taux de conflit",
                    "action": f"Revoir les règles JsonLogic pour {vertical}. "
                              f"Considérer un ajustement des seuils ou l'ajout de nouvelles règles.",
                    "auto_fixable": False,
                })

        # Rec 3: Agent dégradé
        for agent, metrics in dashboard.agent_metrics.items():
            low_conf = metrics.get("low_confidence_count", 0)
            total = metrics.get("events", 1)
            if low_conf / total > 0.3:
                recs.append({
                    "priority": "medium",
                    "category": "agent_degradation",
                    "title": f"Agent {agent}: {low_conf} résultats à basse confiance ({low_conf/total:.0%})",
                    "action": f"Vérifier les prompts LLM de l'agent {agent}. "
                              f"Les sources de données sont peut-être insuffisantes.",
                    "auto_fixable": False,
                })

        # Rec 4: Signaux de dérive critiques
        critical_signals = [s for s in dashboard.drift_signals if s.severity == "critical"]
        if critical_signals:
            recs.append({
                "priority": "critical",
                "category": "drift_detection",
                "title": f"{len(critical_signals)} signaux critiques de dérive détectés",
                "action": "Examiner chaque signal et prendre une action corrective.",
                "auto_fixable": False,
                "details": [s.description for s in critical_signals],
            })

        return recs


# === Singleton ===

observe_skill = ObserveSkill()
