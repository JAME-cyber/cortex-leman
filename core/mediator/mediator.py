"""
Cortex Leman v5 — Agent Médiateur

Agent transverse qui:
1. Valide la cohérence factuelle et réglementaire en continu
2. Détecte les conflits entre agents
3. Gèle les branches d'exécution incriminées
4. Prépare des dossiers contradictoires pour l'arbitrage humain
"""
import uuid
import logging
from typing import Optional
from datetime import datetime, timezone

from core.bus.nats_client import bus
from core.bus.subjects import subjects
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType, ConflictRecord
from core.mediator.rules_engine import rules_engine, RuleResult
from core.config import settings

logger = logging.getLogger(__name__)


class AgentMediator:
    """
    Médiateur transverse Cortex Leman v5.
    
    Abonné au bus, il intercepte TOUS les résultats d'agents
    et applique les règles métier en temps réel.
    
    Modes de gel:
    - FULL FREEZE: tous les agents sont bloqués (conflit critique, règle block)
    - DEGRADED FREEZE (P0): seul l'Agent Action est bloqué.
      Data et Raisonnement continuent de travailler pour enrichir
      le dossier d'arbitrage. L'humain reçoit un dossier plus complet.
    """

    # Fenêtre de consolidation post-dégel (en secondes)
    # Pendant cette fenêtre, les résultats en vol sont capturés
    # et explicitement ajoutés au dossier d'arbitrage.
    _CONSOLIDATION_WINDOW_SEC = 5.0

    def __init__(self):
        self._active_conflicts: dict[str, ConflictRecord] = {}
        self._agent_positions: dict[str, dict] = {}  # intention_id -> {agent: result}
        self._max_positions = 10_000  # TTL: purge au-delà
        self._max_conflicts = 1_000
        # P1: Seuils de gel paramétrables par verticale
        self._freeze_thresholds: dict[str, float] = {
            "comptable": settings.mediator_default_freeze_threshold,
            "avocat": 0.0,       # Pas de seuil montant — gel par type d'action
            "banque": 15000.0,    # KYC renforcé ≥ 15K CHF
            "sante": 0.0,         # Pas de seuil montant — gel par type de données
            "startup": settings.mediator_default_freeze_threshold,
            "rh": settings.mediator_default_freeze_threshold,
        }
        # Robustesse: intentions récemment dégelées — fenêtre de consolidation
        # key = intention_id, value = datetime du dégel
        self._recently_unfrozen: dict[str, datetime] = {}

    async def start(self) -> None:
        """Démarrer le Médiateur et s'abonner au bus"""
        # Charger les règles
        rules_engine.load_rules()

        # S'abonner aux résultats de tous les agents
        await bus.subscribe(subjects.MEDIATOR_CHECK, self._on_check_request)
        await bus.subscribe(subjects.AGENT_RESULT, self._on_agent_result)
        await bus.subscribe(subjects.ARBITRATION_DECISION, self._on_arbitrage_done)

        logger.info(
            f"Médiateur démarré — "
            f"{len(rules_engine.get_all_verticals())} verticales chargées"
        )

    async def _on_check_request(self, data: dict, meta: dict) -> None:
        """Vérification explicite demandée par l'orchestrateur"""
        intention_id = data.get("intention_id")
        client_id = data.get("client_id", "unknown")
        vertical = data.get("vertical", "unknown")

        # Évaluer les règles de la verticale
        context = data.get("context", {})
        results = rules_engine.evaluate(vertical, context)

        triggered = [r for r in results if r.triggered]

        journal.append(
            event_type=JournalEventType.MEDIATOR_CHECK,
            client_id=client_id,
            vertical=vertical,
            agent_source="mediator",
            intention_id=intention_id,
            payload={
                "rules_evaluated": len(results),
                "rules_triggered": len(triggered),
                "actions": [r.action for r in triggered],
            },
        )

        if triggered:
            await self._handle_triggered_rules(
                intention_id, client_id, vertical, triggered, data
            )

    async def _on_agent_result(self, data: dict, meta: dict) -> None:
        """Intercepter les résultats d'agents pour détection de conflits"""
        intention_id = data.get("intention_id")
        agent_source = data.get("agent_source")

        if not intention_id or not agent_source:
            return

        # Vérifier si l'intention est gelée
        from core.orchestrator.intention import intention_store
        intention = intention_store.get(intention_id)

        # --- P0: MODE DÉGRADÉ CONFORME ---
        # Si gel complet (FROZEN): tous les agents sont bloqués
        if intention and intention_store.is_fully_frozen(intention_id):
            logger.info(f"Médiateur: intention {intention_id[:8]}... gelée, résultat de {agent_source} ignoré")
            return

        # Si gel dégradé (DEGRADED_FROZEN): seul l'Action est bloqué
        # Data et Raisonnement continuent d'enrichir le dossier d'arbitrage
        if intention and intention_store.is_degraded_frozen(intention_id):
            if agent_source == "action":
                logger.info(f"Médiateur: intention {intention_id[:8]}... dégradé, Action bloqué")
                return
            else:
                await self._capture_enrichment(intention_id, agent_source, data)
                return

        # --- Robustesse: FENÊTRE DE CONSOLIDATION POST-DÉGEL ---
        # Si l'intention vient d'être dégelée (< 5s), on capture quand même
        # les résultats en vol pour éviter de perdre des informations.
        if intention_id in self._recently_unfrozen:
            unfrozen_at = self._recently_unfrozen[intention_id]
            elapsed = (datetime.now(timezone.utc) - unfrozen_at).total_seconds()
            if elapsed < self._CONSOLIDATION_WINDOW_SEC:
                if agent_source in ("data", "reasoning"):
                    logger.info(
                        f"Médiateur: CONSOLIDATION post-dégel — "
                        f"résultat de {agent_source} capturé pour {intention_id[:8]}... "
                        f"({elapsed:.1f}s après dégel)"
                    )
                    await self._capture_enrichment(intention_id, agent_source, data)
                    # Ne pas supprimer encore — d'autres résultats peuvent arriver
                    return
                # Nettoyer si la fenêtre est dépassée pour ce résultat
            else:
                # Fenêtre expirée → nettoyer
                del self._recently_unfrozen[intention_id]

        # Stocker la position de l'agent
        if intention_id not in self._agent_positions:
            self._agent_positions[intention_id] = {}
        self._agent_positions[intention_id][agent_source] = data.get("result", {})

        # Nettoyage mémoire si trop de positions accumulées
        if len(self._agent_positions) > self._max_positions:
            oldest = list(self._agent_positions.keys())[:self._max_positions // 2]
            for k in oldest:
                del self._agent_positions[k]
            logger.info(f"Médiateur: purge {len(oldest)} anciennes positions")

        # ============================================================
        # GEL PAR DÉFAUT — Verticales sensibles avec montant élevé
        # P1: Seuil paramétrable par verticale (self._freeze_thresholds)
        # P0: Gel DÉGRADÉ par défaut (Data+Raisonnement continuent)
        # ============================================================
        vertical = data.get("vertical", "unknown")
        sensitive_verticals = {"comptable", "avocat", "banque", "sante"}
        result = data.get("result", {})

        # P1: Seuil paramétrable par verticale
        threshold = self._freeze_thresholds.get(vertical, settings.mediator_default_freeze_threshold)

        if vertical in sensitive_verticals and agent_source in ("data", "reasoning"):
            # Détecter un montant dans le résultat
            amount = self._extract_amount(result)
            if amount and amount >= threshold:
                # Vérifier si une règle a déjà été déclenchée
                rules_results = rules_engine.evaluate(vertical, result)
                critical_triggered = any(
                    r.triggered and r.action in ("freeze", "block")
                    for r in rules_results
                )
                if not critical_triggered:
                    logger.warning(
                        f"Médiateur: GEL DÉGRADÉ PAR DÉFAUT — {vertical}/{intention_id[:8]}... "
                        f"montant={amount} (seuil={threshold}), aucun gel explicite."
                    )
                    await self._create_conflict(
                        intention_id=intention_id,
                        agent_a=agent_source,
                        agent_b="default_freeze",
                        reason=f"Gel dégradé: {vertical}, montant {amount} (seuil {threshold}). Data+Raisonnement continuent.",
                        data=data,
                        severity="high",
                        rule_id="default-freeze",
                        degraded=True,  # P0: gel dégradé par défaut
                    )
                    return

        # Vérifier les conflits entre positions
        await self._detect_conflicts(intention_id, data)

    async def _detect_conflicts(self, intention_id: str, data: dict) -> None:
        """Détecter les conflits entre positions d'agents"""
        positions = self._agent_positions.get(intention_id, {})

        if len(positions) < 2:
            return  # Pas assez de positions pour un conflit

        # Logique de détection de conflits
        agents = list(positions.keys())
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                conflict = self._compare_positions(
                    agents[i], positions[agents[i]],
                    agents[j], positions[agents[j]],
                )
                if conflict:
                    await self._create_conflict(
                        intention_id=intention_id,
                        agent_a=agents[i],
                        agent_b=agents[j],
                        reason=conflict,
                        data=data,
                    )
                    return  # Un conflit suffit pour geler

    def _compare_positions(
        self,
        agent_a: str, pos_a: dict,
        agent_b: str, pos_b: dict,
    ) -> Optional[str]:
        """
        Comparer deux positions d'agents.
        Retourne la raison du conflit ou None.
        """
        # Conflit: un agent recommande d'exécuter, l'autre non
        rec_a = pos_a.get("recommendation")
        rec_b = pos_b.get("recommendation")

        if rec_a and rec_b:
            if rec_a != rec_b:
                return (
                    f"Divergence: {agent_a} recommande '{rec_a}' "
                    f"mais {agent_b} recommande '{rec_b}'"
                )

        # Conflit: score de confiance très différent
        conf_a = pos_a.get("confidence", 0.5)
        conf_b = pos_b.get("confidence", 0.5)
        if abs(conf_a - conf_b) > settings.mediator_conflict_threshold:
            return (
                f"Divergence confiance: {agent_a}={conf_a:.2f} "
                f"vs {agent_b}={conf_b:.2f}"
            )

        # Conflit: un agent signale un risque que l'autre ignore
        risks_a = set(pos_a.get("risks", []))
        risks_b = set(pos_b.get("risks", []))
        if risks_a and not risks_a.intersection(risks_b):
            return (
                f"Risques non partagés: {agent_a} identifie {risks_a} "
                f"mais {agent_b} ne les mentionne pas"
            )

        return None

    async def _handle_triggered_rules(
        self,
        intention_id: str,
        client_id: str,
        vertical: str,
        triggered_rules: list[RuleResult],
        original_data: dict,
    ) -> None:
        """Traiter les règles déclenchées"""
        for rule in triggered_rules:
            logger.warning(
                f"RÈGLE DÉCLENCHÉE [{rule.severity}] {rule.rule_id}: {rule.message}"
            )

            if rule.action == "block":
                # Blocage immédiat
                await bus.publish(subjects.MEDIATOR_FREEZE, {
                    "intention_id": intention_id,
                    "client_id": client_id,
                    "vertical": vertical,
                    "reason": rule.message,
                    "rule_id": rule.rule_id,
                    "action": "block",
                })
                return

            elif rule.action == "freeze":
                # Gel + arbitrage obligatoire
                await self._create_conflict(
                    intention_id=intention_id,
                    agent_a="mediator",
                    agent_b="rules",
                    reason=rule.message,
                    data=original_data,
                    severity=rule.severity,
                    rule_id=rule.rule_id,
                )
                return

            elif rule.action == "arbitrate":
                # Demande d'arbitrage (sans gel)
                await bus.publish(subjects.ARBITRATION_REQUEST, {
                    "intention_id": intention_id,
                    "client_id": client_id,
                    "vertical": vertical,
                    "reason": rule.message,
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "positions": self._agent_positions.get(intention_id, {}),
                })

            elif rule.action == "warn":
                logger.warning(f"MEDIATOR WARN: {rule.message}")

            elif rule.action == "require_audit":
                journal.append(
                    event_type=JournalEventType.COMPLIANCE_CHECK,
                    client_id=client_id,
                    vertical=vertical,
                    agent_source="mediator",
                    intention_id=intention_id,
                    payload={"rule": rule.rule_id, "action": "audit_required"},
                )

    async def _create_conflict(
        self,
        intention_id: str,
        agent_a: str,
        agent_b: str,
        reason: str,
        data: dict,
        severity: str = "high",
        rule_id: str = None,
        degraded: bool = False,  # P0: mode dégradé conforme
    ) -> None:
        """Créer un conflit et geler la branche.
        
        Args:
            degraded: Si True, gel dégradé — Action bloqué, Data+Raisonnement
                      continuent d'enrichir le dossier d'arbitrage.
        """
        conflict = ConflictRecord(
            conflict_id=str(uuid.uuid4()),
            intention_id=intention_id,
            agent_positions=self._agent_positions.get(intention_id, {}),
            conflict_reason=reason,
            severity=severity,
        )
        self._active_conflicts[conflict.conflict_id] = conflict

        # Journaliser le conflit
        journal.append(
            event_type=JournalEventType.MEDIATOR_CONFLICT,
            client_id=data.get("client_id", "unknown"),
            vertical=data.get("vertical", "unknown"),
            agent_source="mediator",
            intention_id=intention_id,
            payload={
                "conflict_id": conflict.conflict_id,
                "agents": [agent_a, agent_b],
                "reason": reason,
                "severity": severity,
                "rule_id": rule_id,
                "degraded": degraded,
            },
        )

        # Geler l'intention (mode dégradé ou complet)
        from core.orchestrator.intention import intention_store
        intention_store.freeze(intention_id, reason=reason, degraded=degraded)

        freeze_subject = subjects.MEDIATOR_DEGRADED_FREEZE if degraded else subjects.MEDIATOR_FREEZE
        await bus.publish(freeze_subject, {
            "intention_id": intention_id,
            "conflict_id": conflict.conflict_id,
            "client_id": data.get("client_id"),
            "vertical": data.get("vertical"),
            "reason": reason,
            "positions": conflict.agent_positions,
            "severity": severity,
            "degraded": degraded,
        })

        logger.warning(
            f"CONFLIT CRÉÉ {conflict.conflict_id[:8]}... "
            f"intention={intention_id[:8]}... severity={severity} "
            f"{'DÉGRADÉ' if degraded else 'COMPLET'}"
        )

    async def _on_arbitrage_done(self, data: dict, meta: dict) -> None:
        """Un arbitrage a été résolu → nettoyer"""
        conflict_id = data.get("conflict_id")
        if conflict_id in self._active_conflicts:
            conflict = self._active_conflicts[conflict_id]
            conflict.resolved = True
            conflict.arbitration_id = data.get("arbitration_id")

            intention_id = conflict.intention_id

            # Robustesse: enregistrer le moment du dégel pour la fenêtre
            # de consolidation (résultats Data/Raisonnement encore en vol)
            self._recently_unfrozen[intention_id] = datetime.now(timezone.utc)
            logger.info(
                f"Médiateur: dégel enregistré pour {intention_id[:8]}... "
                f"fenêtre de consolidation {self._CONSOLIDATION_WINDOW_SEC}s"
            )

            # Ne PAS supprimer agent_positions tout de suite —
            # la fenêtre de consolidation peut encore en avoir besoin.
            # La purge se fera par le nettoyage mémoire.

            logger.info(f"Conflit {conflict_id[:8]}... résolu par arbitrage")

        # Purger les conflits résolus si trop nombreux
        if len(self._active_conflicts) > self._max_conflicts:
            resolved = [cid for cid, c in self._active_conflicts.items() if c.resolved]
            for cid in resolved[:len(resolved) // 2]:
                del self._active_conflicts[cid]
            logger.info(f"Médiateur: purge {len(resolved)} conflits résolus")

    async def _capture_enrichment(
        self, intention_id: str, agent_source: str, data: dict
    ) -> None:
        """Capturer un résultat d'agent comme enrichissement du dossier d'arbitrage.
        
        Utilisé en mode dégradé ET pendant la fenêtre de consolidation post-dégel.
        Journalise chaque capture pour traçabilité complète.
        """
        result = data.get("result", {})
        if intention_id not in self._agent_positions:
            self._agent_positions[intention_id] = {}
        self._agent_positions[intention_id][agent_source] = result

        # Journaliser l'enrichissement dans le WORM
        journal.append(
            event_type=JournalEventType.AGENT_RESULT,
            client_id=data.get("client_id", "unknown"),
            vertical=data.get("vertical", "unknown"),
            agent_source="mediator",
            intention_id=intention_id,
            payload={
                "event": "degraded_enrichment",
                "enriched_by": agent_source,
                "confidence": result.get("confidence"),
                "positions_snapshot": dict(self._agent_positions.get(intention_id, {})),
            },
        )

        # Publier la mise à jour du dossier
        await bus.publish(subjects.MEDIATOR_DEGRADED_FREEZE, {
            "intention_id": intention_id,
            "agent_source": agent_source,
            "event": "enrichment",
            "message": f"Agent {agent_source} a enrichi le dossier pendant le gel dégradé",
            "positions": self._agent_positions.get(intention_id, {}),
        })

        logger.info(
            f"Médiateur: enrichissement {agent_source} → {intention_id[:8]}... "
            f"(positions: {list(self._agent_positions.get(intention_id, {}).keys())})"
        )

    @staticmethod
    def _extract_amount(result: dict) -> Optional[float]:
        """Extraire un montant d'un résultat d'agent (cherche dans payload, amount, montant, etc.)"""
        candidates = [
            result.get("amount"),
            result.get("montant"),
            result.get("payload", {}).get("amount"),
            result.get("payload", {}).get("montant"),
            result.get("analysis", {}).get("amount"),
            result.get("analysis", {}).get("montant"),
            result.get("impact_fiscal"),
            result.get("fiscal_impact"),
        ]
        for c in candidates:
            if isinstance(c, (int, float)) and c > 0:
                return float(c)
        return None

    def get_active_conflicts(self) -> list[dict]:
        """Lister les conflits actifs"""
        return [
            {
                "conflict_id": c.conflict_id,
                "intention_id": c.intention_id,
                "reason": c.conflict_reason,
                "severity": c.severity,
                "positions": c.agent_positions,
                "frozen_at": c.frozen_at.isoformat(),
            }
            for c in self._active_conflicts.values()
            if not c.resolved
        ]


# Singleton
mediator = AgentMediator()
