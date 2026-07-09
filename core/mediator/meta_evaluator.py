"""
Cortex Leman v5 — Méta-Évaluateur des Règles du Médiateur

Vérifie périodiquement que les règles JsonLogic sont encore pertinentes:
- Trop de déclenchements = faux positifs?
- Conflits non matchés = faux négatifs?
- La réglementation a-t-elle changé?

JAMAIS de modification automatique des règles.
Le méta-évaluateur propose, l'humain décide.

Inspiré de: "Mind the Gap" — concept de "ce qu'on ne sait pas qu'on ne sait pas"
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

RULES_DIR = Path(__file__).parent.parent / "mediator" / "rules"


@dataclass
class RuleHealth:
    """Santé d'une règle individuelle"""
    rule_id: str
    vertical: str
    name: str
    action: str
    severity: str
    trigger_count: int = 0
    false_positive_suspected: bool = False
    false_negative_suspected: bool = False
    last_triggered: Optional[str] = None
    recommendation: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "vertical": self.vertical,
            "name": self.name,
            "action": self.action,
            "severity": self.severity,
            "trigger_count": self.trigger_count,
            "false_positive_suspected": self.false_positive_suspected,
            "false_negative_suspected": self.false_negative_suspected,
            "last_triggered": self.last_triggered,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
        }


@dataclass
class MetaEvaluationReport:
    """Rapport de méta-évaluation complet"""
    report_id: str = ""
    timestamp: str = ""
    total_rules: int = 0
    rules_evaluated: int = 0
    healthy_rules: int = 0
    rules_to_review: list[RuleHealth] = field(default_factory=list)
    rules_to_add: list[dict] = field(default_factory=list)
    rules_to_remove: list[dict] = field(default_factory=list)
    uncovered_conflicts: list[dict] = field(default_factory=list)

    @property
    def health_rate(self) -> float:
        return self.healthy_rules / self.rules_evaluated if self.rules_evaluated > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "summary": {
                "total_rules": self.total_rules,
                "rules_evaluated": self.rules_evaluated,
                "healthy_rules": self.healthy_rules,
                "health_rate": round(self.health_rate, 4),
                "rules_to_review": len(self.rules_to_review),
                "rules_to_add": len(self.rules_to_add),
                "rules_to_remove": len(self.rules_to_remove),
                "uncovered_conflicts": len(self.uncovered_conflicts),
            },
            "rules_to_review": [r.to_dict() for r in self.rules_to_review],
            "rules_to_add": self.rules_to_add,
            "rules_to_remove": self.rules_to_remove,
            "uncovered_conflicts": self.uncovered_conflicts,
        }


class MetaEvaluator:
    """
    Méta-évaluateur des règles JsonLogic du Médiateur.

    Processus:
    1. Charger toutes les règles depuis core/mediator/rules/*.json
    2. Analyser les entrées du journal WORM (ou données mockées)
    3. Pour chaque règle, évaluer:
       - Taux de déclenchement (trop haut = faux positifs probables)
       - Conflits non couverts (aucune règle n'a matché = faux négatifs)
       - Pertinence réglementaire (comparaison avec la dernière version)
    4. Générer un rapport avec recommandations
    5. Proposer via le système d'extension (cleman.extension.propose)

    JAMAIS de modification automatique.
    """

    # Seuils de détection
    HIGH_TRIGGER_RATE = 0.3       # >30% de déclenchement = suspect
    ZERO_TRIGGER_THRESHOLD = 100  # Après 100 événements, 0 trigger = suspect
    MIN_SAMPLE_SIZE = 10          # Minimum d'événements pour évaluer

    def __init__(self, rules_dir: Path = RULES_DIR):
        self.rules_dir = rules_dir
        self._loaded_rules: dict[str, list[dict]] = {}

    def load_rules(self) -> dict[str, list[dict]]:
        """Charger toutes les règles depuis les fichiers JSON"""
        self._loaded_rules = {}

        if not self.rules_dir.exists():
            logger.warning(f"MetaEvaluator: répertoire règles introuvable: {self.rules_dir}")
            return self._loaded_rules

        for rule_file in self.rules_dir.glob("*.json"):
            try:
                data = json.loads(rule_file.read_text())
                vertical = rule_file.stem
                rules = data.get("rules", [])
                self._loaded_rules[vertical] = rules
                logger.debug(f"MetaEvaluator: {len(rules)} règles chargées pour {vertical}")
            except Exception as e:
                logger.warning(f"MetaEvaluator: erreur lecture {rule_file}: {e}")

        return self._loaded_rules

    def evaluate_rules(
        self,
        conflict_history: list[dict] = None,
        trigger_history: list[dict] = None,
    ) -> MetaEvaluationReport:
        """
        Évaluer la pertinence de toutes les règles.

        Args:
            conflict_history: Historique des conflits du Médiateur
                [{"intention_id", "reason", "vertical", "rule_id", "timestamp"}]
            trigger_history: Historique des déclenchements de règles
                [{"rule_id", "vertical", "action", "timestamp"}]

        Returns:
            Rapport de méta-évaluation
        """
        import uuid

        if not self._loaded_rules:
            self.load_rules()

        report = MetaEvaluationReport(
            report_id=uuid.uuid4().hex[:12],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        conflict_history = conflict_history or []
        trigger_history = trigger_history or []

        # Compter les déclenchements par règle
        trigger_counts: dict[str, int] = {}
        last_trigger: dict[str, str] = {}
        for event in trigger_history:
            rid = event.get("rule_id", "unknown")
            trigger_counts[rid] = trigger_counts.get(rid, 0) + 1
            last_trigger[rid] = event.get("timestamp", "")

        total_events = len(trigger_history)

        # Évaluer chaque règle de chaque verticale
        for vertical, rules in self._loaded_rules.items():
            report.total_rules += len(rules)

            for rule in rules:
                rule_id = rule.get("id", "unknown")
                report.rules_evaluated += 1

                health = RuleHealth(
                    rule_id=rule_id,
                    vertical=vertical,
                    name=rule.get("name", ""),
                    action=rule.get("action", ""),
                    severity=rule.get("severity", ""),
                    trigger_count=trigger_counts.get(rule_id, 0),
                    last_triggered=last_trigger.get(rule_id),
                )

                # === Vérification 1: Taux de déclenchement ===
                if total_events >= self.MIN_SAMPLE_SIZE:
                    trigger_rate = health.trigger_count / total_events

                    if trigger_rate > self.HIGH_TRIGGER_RATE:
                        health.false_positive_suspected = True
                        health.recommendation = (
                            f"Taux de déclenchement très élevé ({trigger_rate:.0%}). "
                            f"Vérifier si cette règle est trop large et génère des faux positifs."
                        )
                        health.confidence = min(0.5 + trigger_rate, 0.95)

                # === Vérification 2: Règle jamais déclenchée ===
                if health.trigger_count == 0 and total_events >= self.ZERO_TRIGGER_THRESHOLD:
                    health.false_negative_suspected = True
                    health.recommendation = (
                        f"Jamais déclenchée après {total_events} événements. "
                        f"Soit la règle est trop restrictive, soit le pattern ne se produit jamais."
                    )
                    health.confidence = 0.5

                # === Vérification 3: Action et sévérité cohérentes ===
                action = rule.get("action", "")
                severity = rule.get("severity", "")
                if action == "block" and severity not in ("high", "critical"):
                    health.recommendation += (
                        " ⚠️ Action 'block' avec sévérité basse — incohérent."
                    )

                # Si tout va bien
                if not health.false_positive_suspected and not health.false_negative_suspected:
                    report.healthy_rules += 1
                else:
                    report.rules_to_review.append(health)

        # === Vérification 4: Conflits non couverts ===
        # Conflits qui n'ont matché aucune règle
        rule_ids = set()
        for rules in self._loaded_rules.values():
            for r in rules:
                rule_ids.add(r.get("id"))

        for conflict in conflict_history:
            conflict_rule = conflict.get("rule_id")
            if not conflict_rule or conflict_rule not in rule_ids:
                report.uncovered_conflicts.append({
                    "conflict_reason": conflict.get("reason", ""),
                    "vertical": conflict.get("vertical", ""),
                    "timestamp": conflict.get("timestamp", ""),
                    "no_matching_rule": True,
                })

        # === Vérification 5: Règles manquantes par verticale ===
        for vertical, rules in self._loaded_rules.items():
            actions_present = {r.get("action") for r in rules}
            if "freeze" not in actions_present and "block" not in actions_present:
                report.rules_to_add.append({
                    "vertical": vertical,
                    "reason": f"Aucune règle de gel/blocage pour {vertical}",
                    "suggested_action": "freeze",
                    "priority": "high",
                })

        return report

    def propose_updates(self, report: MetaEvaluationReport) -> list[dict]:
        """
        Convertir les recommandations en propositions d'extension.
        Ces propositions passent par le système cleman.extension.propose.

        Returns:
            Liste de propositions prêtes à être publiées sur le bus NATS
        """
        proposals = []

        for rule_health in report.rules_to_review:
            action = "review_rule" if rule_health.false_positive_suspected else "check_rule_relevance"

            proposals.append({
                "type": "rule_update",
                "action": action,
                "rule_id": rule_health.rule_id,
                "vertical": rule_health.vertical,
                "reason": rule_health.recommendation,
                "confidence": rule_health.confidence,
                "auto_apply": False,  # Jamais automatique
                "requires_human_approval": True,
            })

        for new_rule in report.rules_to_add:
            proposals.append({
                "type": "rule_addition",
                "action": "add_rule",
                "vertical": new_rule["vertical"],
                "reason": new_rule["reason"],
                "suggested_action": new_rule["suggested_action"],
                "priority": new_rule["priority"],
                "auto_apply": False,
                "requires_human_approval": True,
            })

        for uncovered in report.uncovered_conflicts:
            proposals.append({
                "type": "uncovered_conflict",
                "action": "investigate",
                "vertical": uncovered["vertical"],
                "reason": f"Conflit non couvert: {uncovered['conflict_reason'][:100]}",
                "auto_apply": False,
                "requires_human_approval": True,
            })

        return proposals


# === Singleton ===

meta_evaluator = MetaEvaluator()
