"""
Cortex Leman v5 — Moteur de règles JsonLogic

Évalue les règles métier par verticale.
Actions possibles: block, freeze, arbitrate, warn, require_audit, pass.
"""
import json
import logging
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

from core.config import settings

logger = logging.getLogger(__name__)

try:
    from jsonlogic import jsonLogic as _jsonLogic

    def jsonLogic(test: dict, data: dict = None) -> Any:
        """Wrapper null-safe autour de jsonLogic.
        Toute comparaison numérique avec None retourne False au lieu de crasher.
        Irreprochable by design.
        """
        try:
            return _jsonLogic(test, data or {})
        except (TypeError, KeyError) as exc:
            # Comparaison None >= int, etc. → la règle ne se déclenche pas
            logger.debug(f"jsonLogic null-safe: {exc} — condition traitée comme False")
            return False

except ImportError:
    # Fallback null-safe — irreprochable by design
    _NUM_OPS = {">", ">=", "<", "<="}

    def jsonLogic(test: dict, data: dict = None) -> Any:
        """Minimal JsonLogic fallback — null-safe."""
        if data is None:
            data = {}
        if not isinstance(test, dict):
            return test
        op = list(test.keys())[0]
        args = test[op]

        if op == "var":
            keys = args.split(".") if isinstance(args, str) else args
            result = data
            for key in keys:
                if isinstance(result, dict):
                    result = result.get(key)
                else:
                    return None
            return result
        elif op == "==":
            return jsonLogic(args[0], data) == jsonLogic(args[1], data)
        elif op == "!=":
            return jsonLogic(args[0], data) != jsonLogic(args[1], data)
        elif op in _NUM_OPS:
            a = jsonLogic(args[0], data)
            b = jsonLogic(args[1], data)
            # Null-safe: None n'est jamais comparable numériquement
            if a is None or b is None:
                return False
            try:
                a_val, b_val = float(a), float(b)
            except (ValueError, TypeError):
                return False
            if op == ">":  return a_val > b_val
            if op == ">=": return a_val >= b_val
            if op == "<":  return a_val < b_val
            if op == "<=": return a_val <= b_val
        elif op == "!":
            return not jsonLogic(args[0], data)
        elif op == "and":
            return all(jsonLogic(a, data) for a in args)
        elif op == "or":
            return any(jsonLogic(a, data) for a in args)
        return False


@dataclass
class RuleResult:
    """Résultat de l'évaluation d'une règle"""
    rule_id: str
    rule_name: str
    severity: str
    action: str  # block | freeze | arbitrate | warn | require_audit | pass
    message: str
    triggered: bool = False
    data_used: dict = field(default_factory=dict)


class RulesEngine:
    """
    Moteur de règles JsonLogic par verticale.
    Charge et évalue les règles depuis les fichiers JSON.
    """

    def __init__(self, rules_dir: Optional[str] = None):
        self._rules_dir = Path(rules_dir or settings.mediator_rules_dir)
        self._rules_cache: dict[str, dict] = {}
        self._loaded = False

    def load_rules(self) -> None:
        """Charger toutes les règles depuis les fichiers JSON"""
        self._rules_cache.clear()

        if not self._rules_dir.exists():
            logger.warning(f"Répertoire règles non trouvé: {self._rules_dir}")
            return

        for rule_file in self._rules_dir.glob("*.json"):
            try:
                with open(rule_file) as f:
                    rule_set = json.load(f)
                    vertical = rule_set.get("vertical", rule_file.stem)
                    self._rules_cache[vertical] = rule_set
                    count = len(rule_set.get("rules", []))
                    logger.info(f"Règles chargées: {vertical} ({count} règles)")
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Erreur chargement {rule_file}: {e}")

        self._loaded = True
        logger.info(f"Total: {len(self._rules_cache)} verticales chargées")

    def evaluate(
        self,
        vertical: str,
        context: dict,
        action_context: Optional[dict] = None,
    ) -> list[RuleResult]:
        """
        Évaluer toutes les règles d'une verticale contre un contexte.
        
        Args:
            vertical: Verticale métier (comptable, avocat, etc.)
            context: Données contextuelles à évaluer
            action_context: Contexte additionnel de l'action en cours
        
        Returns:
            Liste des RuleResult (incluant les règles non déclenchées)
        """
        if not self._loaded:
            self.load_rules()

        rule_set = self._rules_cache.get(vertical)
        if not rule_set:
            logger.warning(f"Aucune règle pour verticale '{vertical}'")
            return []

        # Fusionner les contextes
        full_context = {**context, **(action_context or {})}

        results = []
        for rule in rule_set.get("rules", []):
            condition = rule.get("condition", {})
            try:
                triggered = bool(jsonLogic(condition, full_context))
            except Exception as e:
                logger.error(f"Erreur évaluation règle {rule.get('id')}: {e}")
                triggered = False

            results.append(RuleResult(
                rule_id=rule.get("id", "unknown"),
                rule_name=rule.get("name", ""),
                severity=rule.get("severity", "medium"),
                action=rule.get("action", "warn"),
                message=rule.get("message", ""),
                triggered=triggered,
                data_used=full_context,
            ))

        return results

    def evaluate_critical(
        self,
        vertical: str,
        context: dict,
    ) -> list[RuleResult]:
        """Retourner uniquement les règles critiques déclenchées"""
        all_results = self.evaluate(vertical, context)
        return [
            r for r in all_results
            if r.triggered and r.severity in ("critical", "high")
        ]

    def get_rules_for_vertical(self, vertical: str) -> list[dict]:
        """Lister les règles d'une verticale"""
        if not self._loaded:
            self.load_rules()
        rule_set = self._rules_cache.get(vertical, {})
        return rule_set.get("rules", [])

    def get_all_verticals(self) -> list[str]:
        """Lister les verticales disponibles"""
        if not self._loaded:
            self.load_rules()
        return list(self._rules_cache.keys())


# Singleton
rules_engine = RulesEngine()
