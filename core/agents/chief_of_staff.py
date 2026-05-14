"""
Cortex Leman v5 — Agent Chef de Cabinet (Chief of Staff)

Inspiré du "Sergio" de Cook AI (Serge Gatari).
Synthèse quotidienne cross-data, alertes proactives, rapport exécutif.

Rôle:
  - Agrège les résultats de TOUS les agents (Data, Raisonnement, Action)
  - Synthétise un rapport exécutif quotidien
  - Détecte les anomalies et alertes proactives
  - Suit les KPIs par vertical (comptable, avocat, santé, etc.)
  - Publie le rapport sur le bus + horodate dans le journal

Cycle:
  1. Écoute AGENT_RESULT en continu
  2. Accumule les données par vertical/client
  3. Sur trigger (cron ou request), génère le rapport
  4. Publie sur cleman.chief_of_staff.report
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from collections import defaultdict

from core.agents.base_agent import BaseAgent
from core.bus.subjects import subjects
from core.bus.nats_client import bus
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)


# ─── Data Models ────────────────────────────────────────────────────

class VerticalMetrics:
    """KPIs agrégés par vertical"""
    def __init__(self, vertical: str):
        self.vertical = vertical
        self.intentions_processed: int = 0
        self.intentions_completed: int = 0
        self.intentions_frozen: int = 0
        self.conflicts: int = 0
        self.compliance_violations: int = 0
        self.avg_confidence: float = 0.0
        self._confidences: list[float] = []
        self.last_activity: Optional[datetime] = None
        self.clients_active: set[str] = set()
        self.agent_calls: dict[str, int] = defaultdict(int)
        self.errors: int = 0

    def record_result(self, agent_name: str, confidence: float, client_id: str):
        self.intentions_processed += 1
        self.agent_calls[agent_name] += 1
        self._confidences.append(confidence)
        self.avg_confidence = sum(self._confidences) / len(self._confidences)
        self.last_activity = datetime.now(timezone.utc)
        if client_id:
            self.clients_active.add(client_id)

    def record_conflict(self):
        self.conflicts += 1

    def record_freeze(self):
        self.intentions_frozen += 1

    def record_error(self):
        self.errors += 1

    def record_violation(self):
        self.compliance_violations += 1

    def to_dict(self) -> dict:
        return {
            "vertical": self.vertical,
            "intentions_processed": self.intentions_processed,
            "intentions_completed": self.intentions_completed,
            "intentions_frozen": self.intentions_frozen,
            "conflicts": self.conflicts,
            "compliance_violations": self.compliance_violations,
            "avg_confidence": round(self.avg_confidence, 2),
            "clients_active": len(self.clients_active),
            "agent_calls": dict(self.agent_calls),
            "errors": self.errors,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
        }


class DailyReport:
    """Rapport exécutif quotidien"""
    def __init__(self):
        self.date: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.generated_at: datetime = datetime.now(timezone.utc)
        self.verticals: dict[str, VerticalMetrics] = {}
        self.alerts: list[dict] = []
        self.top_insights: list[str] = []
        self.total_intentions: int = 0
        self.total_conflicts: int = 0
        self.total_errors: int = 0
        self.health_score: float = 100.0  # Start at 100, decrease with issues

    def calculate_health(self):
        """Calculer le score de santé global (0-100)"""
        score = 100.0

        # Pénalités
        score -= min(30, self.total_errors * 2)       # -2 par erreur, max -30
        score -= min(20, self.total_conflicts * 3)     # -3 par conflit, max -20

        # Pénalité confiance basse
        for vm in self.verticals.values():
            if vm.avg_confidence < 0.5:
                score -= 5
            if vm.compliance_violations > 0:
                score -= vm.compliance_violations * 2

        self.health_score = max(0, round(score, 1))

    def to_dict(self) -> dict:
        self.calculate_health()
        return {
            "date": self.date,
            "generated_at": self.generated_at.isoformat(),
            "health_score": self.health_score,
            "total_intentions": self.total_intentions,
            "total_conflicts": self.total_conflicts,
            "total_errors": self.total_errors,
            "verticals": {k: v.to_dict() for k, v in self.verticals.items()},
            "alerts": self.alerts,
            "top_insights": self.top_insights,
        }


# ─── Chief of Staff Agent ───────────────────────────────────────────

class ChiefOfStaffAgent(BaseAgent):
    """
    Agent Chef de Cabinet — Le "Sergio" de Cortex Leman.

    Écoute tout, synthétise, alerte.
    Pas de traitement métier — uniquement observation et reporting.
    """

    def __init__(self):
        super().__init__(
            name="chief_of_staff",
            subscribe_subjects=["cleman.chief_of_staff.request"],
        )
        self._report = DailyReport()
        self._alerts: list[dict] = []
        self._history: list[dict] = []  # Derniers 30 rapports
        self._max_history = 30

    async def start(self) -> None:
        """Démarrage avec abonnements étendus"""
        await super().start()

        # Observer TOUT comme le superviseur
        await bus.subscribe(subjects.AGENT_RESULT, self._on_agent_result)
        await bus.subscribe(subjects.MEDIATOR_CONFLICT, self._on_conflict)
        await bus.subscribe(subjects.MEDIATOR_FREEZE, self._on_freeze)
        await bus.subscribe(subjects.SYSTEM_ERROR, self._on_system_error)
        await bus.subscribe(subjects.COMPLIANCE_VIOLATION, self._on_compliance_violation)

        logger.info("Chef de Cabinet: observateur démarré")

    # ─── Observateurs continus ─────────────────────────────────────

    async def _on_agent_result(self, data: dict, meta: dict) -> None:
        """Chaque résultat d'agent alimente les métriques"""
        vertical = data.get("vertical", "unknown")
        client_id = data.get("client_id", "unknown")
        agent_source = data.get("agent_source", "unknown")
        result = data.get("result", {})
        confidence = result.get("confidence", 0.5) if isinstance(result, dict) else 0.5

        # Accumuler par vertical
        if vertical not in self._report.verticals:
            self._report.verticals[vertical] = VerticalMetrics(vertical)

        self._report.verticals[vertical].record_result(
            agent_name=agent_source,
            confidence=confidence,
            client_id=client_id,
        )
        self._report.total_intentions += 1

        # Alerte si confiance très basse
        if confidence < 0.3:
            alert = {
                "type": "low_confidence",
                "severity": "warning",
                "agent": agent_source,
                "vertical": vertical,
                "client_id": client_id,
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Agent {agent_source} a produit un résultat à confiance {confidence:.0%} "
                           f"dans le vertical {vertical}",
            }
            self._alerts.append(alert)
            self._report.alerts.append(alert)

    async def _on_conflict(self, data: dict, meta: dict) -> None:
        """Conflit détecté → alerter"""
        vertical = data.get("vertical", "unknown")
        self._report.total_conflicts += 1

        if vertical in self._report.verticals:
            self._report.verticals[vertical].record_conflict()

        alert = {
            "type": "conflict",
            "severity": "high",
            "vertical": vertical,
            "intention_id": data.get("intention_id"),
            "reason": data.get("conflict_reason", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._alerts.append(alert)
        self._report.alerts.append(alert)

    async def _on_freeze(self, data: dict, meta: dict) -> None:
        """Gel → suivi"""
        vertical = data.get("vertical", "unknown")
        if vertical in self._report.verticals:
            self._report.verticals[vertical].record_freeze()

    async def _on_system_error(self, data: dict, meta: dict) -> None:
        """Erreur système → comptabiliser"""
        self._report.total_errors += 1
        vertical = data.get("vertical", "unknown")
        if vertical in self._report.verticals:
            self._report.verticals[vertical].record_error()

    async def _on_compliance_violation(self, data: dict, meta: dict) -> None:
        """Violation compliance → alerter immédiatement"""
        vertical = data.get("vertical", "unknown")
        if vertical in self._report.verticals:
            self._report.verticals[vertical].record_violation()

        alert = {
            "type": "compliance_violation",
            "severity": "critical",
            "vertical": vertical,
            "client_id": data.get("client_id"),
            "details": data.get("payload", {}),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._alerts.append(alert)
        self._report.alerts.append(alert)

    # ─── Génération de rapport ─────────────────────────────────────

    async def process(self, data: dict, meta: dict) -> dict:
        """Traiter une demande de rapport"""
        request_type = data.get("request_type", "daily_report")

        if request_type == "daily_report":
            return await self._generate_daily_report(data)
        elif request_type == "alerts":
            return self._get_alerts()
        elif request_type == "vertical_summary":
            return self._get_vertical_summary(data.get("vertical", "all"))
        elif request_type == "health_check":
            return self._get_health_check()
        else:
            return {"error": f"Unknown request_type: {request_type}"}

    async def _generate_daily_report(self, data: dict) -> dict:
        """Générer le rapport exécutif quotidien"""
        self._report.calculate_health()

        # Top insights automatiques
        insights = self._generate_insights()
        self._report.top_insights = insights

        report_dict = self._report.to_dict()

        # Journaliser le rapport
        journal.append(
            event_type=JournalEventType.SYSTEM,
            client_id="system",
            vertical="all",
            agent_source="chief_of_staff",
            intention_id=f"report-{self._report.date}",
            payload={"report": report_dict},
        )

        # Archiver
        self._history.append(report_dict)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # Reset pour le prochain cycle
        self._report = DailyReport()
        self._alerts.clear()

        # Publier sur le bus
        await bus.publish("cleman.chief_of_staff.report", report_dict)

        return {
            "report": report_dict,
            "confidence": 0.95,
        }

    def _generate_insights(self) -> list[str]:
        """Générer des insights automatiques depuis les métriques"""
        insights = []

        for vertical, metrics in self._report.verticals.items():
            # Confiance basse
            if metrics.avg_confidence < 0.5:
                insights.append(
                    f"⚠️ {vertical}: confiance moyenne {metrics.avg_confidence:.0%} — "
                    f"investiguer les résultats de {list(metrics.agent_calls.keys())}"
                )

            # Beaucoup de conflits
            if metrics.conflicts >= 3:
                insights.append(
                    f"🔴 {vertical}: {metrics.conflicts} conflits — "
                    f"le médiateur est très sollicité, vérifier la cohérence des agents"
                )

            # Violations compliance
            if metrics.compliance_violations > 0:
                insights.append(
                    f"🚨 {vertical}: {metrics.compliance_violations} violation(s) compliance — "
                    f"ACTION REQUISE"
                )

            # Vertical inactif avec clients
            if metrics.intentions_processed == 0 and metrics.clients_active:
                insights.append(
                    f"💤 {vertical}: {len(metrics.clients_active)} clients mais 0 intention traitée"
                )

            # Forte activité = positif
            if metrics.intentions_processed >= 10:
                insights.append(
                    f"✅ {vertical}: {metrics.intentions_processed} intentions traitées — "
                    f"vertical actif, {len(metrics.clients_active)} clients"
                )

            # Erreurs récurrentes
            if metrics.errors >= 3:
                insights.append(
                    f"❌ {vertical}: {metrics.errors} erreurs — "
                    f"circuit breaker probablement actif"
                )

        if not insights:
            insights.append("✅ RAS — Tous les verticals fonctionnent normalement")

        return insights

    def _get_alerts(self) -> dict:
        """Retourner les alertes actives"""
        return {
            "alerts": self._alerts[-50:],  # Dernières 50
            "total": len(self._alerts),
            "critical": len([a for a in self._alerts if a.get("severity") == "critical"]),
            "high": len([a for a in self._alerts if a.get("severity") == "high"]),
            "warning": len([a for a in self._alerts if a.get("severity") == "warning"]),
            "confidence": 0.95,
        }

    def _get_vertical_summary(self, vertical: str) -> dict:
        """Résumé d'un vertical spécifique"""
        if vertical == "all":
            return {
                "verticals": {k: v.to_dict() for k, v in self._report.verticals.items()},
                "confidence": 0.9,
            }

        vm = self._report.verticals.get(vertical)
        if not vm:
            return {
                "error": f"Vertical '{vertical}' pas encore observé",
                "confidence": 0.3,
            }

        return {
            "vertical": vm.to_dict(),
            "confidence": 0.9,
        }

    def _get_health_check(self) -> dict:
        """Quick health check du système"""
        self._report.calculate_health()
        return {
            "health_score": self._report.health_score,
            "total_intentions": self._report.total_intentions,
            "total_conflicts": self._report.total_conflicts,
            "total_errors": self._report.total_errors,
            "active_verticals": list(self._report.verticals.keys()),
            "active_alerts": len(self._alerts),
            "confidence": 0.95,
        }
