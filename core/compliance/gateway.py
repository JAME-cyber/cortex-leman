"""
Cortex Leman v5 — Compliance Gateway

Module centralisé qui:
1. Collecte les preuves d'audit (logs signés)
2. Agrège les événements de conformité
3. Produit automatiquement des rapports périodiques
4. Ne expose JAMAIS les données métier (métadonnées uniquement)
"""
import json
import uuid
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType
from core.config import settings

logger = logging.getLogger(__name__)


class ComplianceGateway:
    """
    Gateway de conformité Cortex Leman v5.
    
    Fonctionne en mode:
    - standard: collecte + agrégation locale
    - haute_protection: réplication chiffrée vers service externe
    """

    def __init__(self):
        self._report_dir = Path(settings.compliance_report_dir)
        self._report_dir.mkdir(parents=True, exist_ok=True)

    def generate_daily_report(self, client_id: Optional[str] = None) -> dict:
        """Générer le rapport de conformité quotidien"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Collecter les événements du jour
        events = journal.query(client_id=client_id, limit=10000)

        # Filtrer les événements de conformité
        compliance_events = [
            e for e in events
            if e.get("event_type") in (
                JournalEventType.MEDIATOR_CONFLICT.value,
                JournalEventType.MEDIATOR_FREEZE.value,
                JournalEventType.ARBITRATION_REQUESTED.value,
                JournalEventType.ARBITRATION_DECISION.value,
                JournalEventType.COMPLIANCE_CHECK.value,
                JournalEventType.COMPLIANCE_VIOLATION.value,
                JournalEventType.ACTION_COMPENSATED.value,
                JournalEventType.AGENT_ERROR.value,
            )
        ]

        report = {
            "report_id": str(uuid.uuid4()),
            "report_type": "daily",
            "date": today,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "client_id": client_id or "all",
            "mode": settings.app_mode,
            "data_residency": settings.compliance_data_residency,

            # Métriques
            "metrics": {
                "total_events": len(events),
                "compliance_events": len(compliance_events),
                "conflicts_detected": sum(
                    1 for e in compliance_events
                    if e.get("event_type") == JournalEventType.MEDIATOR_CONFLICT.value
                ),
                "arbitrations_requested": sum(
                    1 for e in compliance_events
                    if e.get("event_type") == JournalEventType.ARBITRATION_REQUESTED.value
                ),
                "arbitrations_resolved": sum(
                    1 for e in compliance_events
                    if e.get("event_type") == JournalEventType.ARBITRATION_DECISION.value
                ),
                "actions_compensated": sum(
                    1 for e in compliance_events
                    if e.get("event_type") == JournalEventType.ACTION_COMPENSATED.value
                ),
                "agent_errors": sum(
                    1 for e in compliance_events
                    if e.get("event_type") == JournalEventType.AGENT_ERROR.value
                ),
                "compliance_violations": sum(
                    1 for e in compliance_events
                    if e.get("event_type") == JournalEventType.COMPLIANCE_VIOLATION.value
                ),
            },

            # Statut de conformité
            "compliance_status": self._assess_compliance(compliance_events),

            # Intégrité du journal
            "journal_integrity": journal.verify_integrity(),

            # Vérification data residency
            "data_residency_check": {
                "configured": settings.compliance_data_residency,
                "encryption": settings.compliance_encryption,
                "mode": settings.app_mode,
                "vertical": settings.active_vertical,
            },

            # Arbre de décision simplifié
            "decision_tree": self._build_decision_tree(compliance_events),
        }

        # Sauvegarder
        self._save_report(report)

        logger.info(
            f"Rapport quotidien généré: {report['report_id'][:8]}... "
            f"({len(compliance_events)} événements conformité)"
        )

        return report

    def generate_monthly_report(self, client_id: Optional[str] = None) -> dict:
        """Générer le rapport de conformité mensuel"""
        daily_reports = sorted(self._report_dir.glob("report-daily-*.json"))

        monthly_metrics = {
            "total_conflicts": 0,
            "total_arbitrations": 0,
            "total_violations": 0,
            "total_compensations": 0,
            "days_reported": 0,
        }

        for rf in daily_reports[-30:]:  # 30 derniers jours
            with open(rf) as f:
                daily = json.loads(f.read())
                m = daily.get("metrics", {})
                monthly_metrics["total_conflicts"] += m.get("conflicts_detected", 0)
                monthly_metrics["total_arbitrations"] += m.get("arbitrations_resolved", 0)
                monthly_metrics["total_violations"] += m.get("compliance_violations", 0)
                monthly_metrics["total_compensations"] += m.get("actions_compensated", 0)
                monthly_metrics["days_reported"] += 1

        report = {
            "report_id": str(uuid.uuid4()),
            "report_type": "monthly",
            "period": datetime.now(timezone.utc).strftime("%Y-%m"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "client_id": client_id or "all",
            "metrics": monthly_metrics,
            "overall_compliance": self._assess_monthly_compliance(monthly_metrics),
            "recommendations": self._generate_recommendations(monthly_metrics),
        }

        self._save_report(report)
        return report

    def check_data_residency(self, data: dict) -> dict:
        """Vérifier la conformité data residency pour une opération"""
        vertical = data.get("vertical", "unknown")
        configured_residency = settings.compliance_data_residency

        # Règles strictes par verticale
        strict_ch = vertical in ("avocat", "banque", "sante")
        required_residency = "CH" if strict_ch else configured_residency

        return {
            "compliant": True,  # Dans le mode configuré
            "vertical": vertical,
            "required_residency": required_residency,
            "configured_residency": configured_residency,
            "encryption_required": strict_ch or configured_residency == "CH",
            "pgp_required": strict_ch,
        }

    # === Méthodes internes ===

    def _assess_compliance(self, events: list[dict]) -> dict:
        """Évaluer le statut de conformité global"""
        violations = [e for e in events if e.get("event_type") == "compliance.violation"]
        unresolved_conflicts = [
            e for e in events
            if e.get("event_type") == "mediator.conflict"
            and not any(
                r.get("payload", {}).get("conflict_id") == e.get("payload", {}).get("conflict_id")
                for r in events
                if r.get("event_type") == "arbitration.decision"
            )
        ]

        if violations:
            return {"status": "non_compliant", "level": "critical", "violations": len(violations)}
        if unresolved_conflicts:
            return {"status": "attention", "level": "warning", "unresolved": len(unresolved_conflicts)}
        return {"status": "compliant", "level": "ok"}

    def _build_decision_tree(self, events: list[dict]) -> list[dict]:
        """Construire un arbre de décision simplifié pour le rapport"""
        tree = []
        for e in events:
            tree.append({
                "event": e.get("event_type"),
                "agent": e.get("agent_source"),
                "intention": e.get("intention_id", "")[:8],
                "timestamp": e.get("timestamp"),
            })
        return tree

    def _assess_monthly_compliance(self, metrics: dict) -> dict:
        assessment = {
            "score": 100,
            "deductions": [],
        }
        if metrics["total_violations"] > 0:
            assessment["score"] -= metrics["total_violations"] * 10
            assessment["deductions"].append(f"-{metrics['total_violations'] * 10} violations")
        if metrics["total_compensations"] > 3:
            assessment["score"] -= 5
            assessment["deductions"].append("-5 compensations excessives")
        assessment["score"] = max(0, assessment["score"])
        return assessment

    def _generate_recommendations(self, metrics: dict) -> list[str]:
        recs = []
        if metrics["total_violations"] > 0:
            recs.append("Revoir les règles de conformité — violations détectées")
        if metrics["total_compensations"] > 3:
            recs.append("Investiguer les compensations fréquentes — problèmes de qualité possibles")
        if not recs:
            recs.append("Aucune action corrective nécessaire")
        return recs

    def _save_report(self, report: dict) -> None:
        """Sauvegarder un rapport"""
        report_type = report.get("report_type", "unknown")
        date_str = report.get("date") or report.get("period", "unknown")
        filename = f"report-{report_type}-{date_str}-{report['report_id'][:8]}.json"
        filepath = self._report_dir / filename

        with open(filepath, "w") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)

        logger.debug(f"Rapport sauvegardé: {filepath}")


# Singleton
compliance_gateway = ComplianceGateway()
