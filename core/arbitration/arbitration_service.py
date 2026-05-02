"""
Cortex Leman v5 — Système d'Arbitrage Humain

Interface d'arbitrage structurée:
- Présente les positions contradictoires
- Permet à l'expert humain de trancher en motivant sa décision
- Enregistre la décision comme précédent
- Horodatage RFC 3161 et signature électronique

P0 — Escalade arbitrage:
- File d'escalade configurable (arbitre → suppléant → associé)
- Timeout par niveau (ex: 2h → 4h → 8h)
- Si aucun arbitre ne répond, escalade automatique
- Journalisation de chaque étape d'escalade
"""
import json
import uuid
import hmac
import hashlib
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType, ArbitrationDecision
from core.config import settings

logger = logging.getLogger(__name__)


class EscalationLevel:
    """Niveau d'escalade dans la file"""
    PRIMARY = "primary"      # Arbitre principal (1er niveau)
    SUBSTITUTE = "substitute"  # Arbitre suppléant (2ème niveau)
    PARTNER = "partner"       # Associé du cabinet (3ème niveau)
    ADMIN = "admin"           # Admin système (dernier recours)


class ArbitrationService:
    """
    Service d'arbitrage humain Cortex Leman v5.
    
    Flux:
    1. Un conflit est détecté → gel de l'intention
    2. Les positions contradictoires sont préparées en dashboard
    3. L'expert humain tranche avec justification
    4. La décision est enregistrée (signée + horodatée)
    5. Le précédent peut enrichir le Médiateur
    
    P0 — Escalade:
    - Si l'arbitre principal ne répond pas sous X heures → suppléant
    - Si le suppléant ne répond pas sous Y heures → associé
    - Si l'associé ne répond pas → admin système (blocage)
    """

    def __init__(self):
        self._precedent_file = Path(settings.arbitration_precedent_file)
        self._precedent_file.parent.mkdir(parents=True, exist_ok=True)
        self._pending_arbitrations: dict[str, dict] = {}
        self._completed_arbitrations: dict[str, ArbitrationDecision] = {}
        # P0: Configuration escalade
        self._escalation_timeout_hours = settings.arbitration_escalation_timeout_hours
        self._escalation_chain = settings.arbitration_escalation_chain
        # Timer d'escalade (task asyncio)
        self._escalation_tasks: dict[str, asyncio.Task] = {}
        # Robustesse: persistance des timers escalade
        self._timers_file = self._precedent_file.parent / "escalation_timers.json"
        self._load_pending_timers()

    def prepare_arbitration(
        self,
        intention_id: str,
        conflict_id: str,
        positions: dict[str, dict],
        reason: str,
        severity: str = "medium",
        client_id: str = "unknown",
        vertical: str = "unknown",
    ) -> dict:
        """
        Préparer un tableau de bord d'arbitrage.
        P0: Démarre automatiquement le timer d'escalade.
        
        Returns:
            Dashboard structuré pour l'interface utilisateur
        """
        arbitration_id = str(uuid.uuid4())

        # Structurer les positions pour affichage
        dashboard_positions = {}
        for agent_name, position in positions.items():
            dashboard_positions[agent_name] = {
                "agent": agent_name,
                "recommendation": position.get("recommendation", "N/A"),
                "confidence": position.get("confidence", 0),
                "sources": position.get("sources", []),
                "risks": position.get("risks", []),
                "regulatory_refs": position.get("regulatory_refs", []),
                "data": position,
            }

        # Déterminer l'arbitre initial selon la chaîne d'escalade
        primary_arbiter = self._escalation_chain[0] if self._escalation_chain else "admin"

        dashboard = {
            "arbitration_id": arbitration_id,
            "intention_id": intention_id,
            "conflict_id": conflict_id,
            "client_id": client_id,
            "vertical": vertical,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "severity": severity,
            "conflict_reason": reason,
            "positions": dashboard_positions,
            "status": "pending",
            # P0: Escalade
            "current_arbiter": {
                "level": EscalationLevel.PRIMARY,
                "name": primary_arbiter,
                "assigned_at": datetime.now(timezone.utc).isoformat(),
                "deadline": (datetime.now(timezone.utc) + timedelta(hours=self._escalation_timeout_hours[0])).isoformat(),
            },
            "escalation_history": [],
            # Simulations d'impact (placeholder)
            "impact_analysis": {
                agent: self._simulate_impact(pos, vertical)
                for agent, pos in positions.items()
            },
        }

        self._pending_arbitrations[arbitration_id] = dashboard

        # P0: Démarrer le timer d'escalade
        self._start_escalation_timer(arbitration_id)

        # Journaliser la demande
        journal.append(
            event_type=JournalEventType.ARBITRATION_REQUESTED,
            client_id=client_id,
            vertical=vertical,
            agent_source="arbitration",
            intention_id=intention_id,
            payload={
                "arbitration_id": arbitration_id,
                "conflict_id": conflict_id,
                "reason": reason,
                "severity": severity,
                "agents_involved": list(positions.keys()),
                "assigned_to": primary_arbiter,
                "escalation_level": EscalationLevel.PRIMARY,
            },
        )

        logger.info(
            f"Arbitrage préparé: {arbitration_id[:8]}... "
            f"assigné à {primary_arbiter} ({len(positions)} positions)"
        )
        return dashboard

    def submit_decision(
        self,
        arbitration_id: str,
        arbiter_id: str,
        arbiter_name: str,
        decision: str,
        justification: str,
        selected_position: str,
        modifications: dict = None,
    ) -> ArbitrationDecision:
        """
        Soumettre une décision d'arbitrage.
        P0: Annule le timer d'escalade.
        
        Args:
            arbitration_id: ID de l'arbitrage
            arbiter_id: Identité de l'humain
            arbiter_name: Nom de l'humain
            decision: approve | reject | modify
            justification: Motivation textuelle
            selected_position: Agent choisi
            modifications: Modifications apportées
        
        Returns:
            ArbitrationDecision signée
        """
        arb = self._pending_arbitrations.get(arbitration_id)
        if not arb:
            raise ValueError(f"Arbitrage {arbitration_id} non trouvé")

        # P0: Annuler le timer d'escalade
        self._cancel_escalation_timer(arbitration_id)

        # Créer la décision
        now = datetime.now(timezone.utc)
        timestamp_token = None
        if settings.arbitration_signature_enabled:
            timestamp_token = self._generate_timestamp_token(now)

        dec = ArbitrationDecision(
            arbitration_id=arbitration_id,
            conflict_id=arb["conflict_id"],
            intention_id=arb["intention_id"],
            arbiter_id=arbiter_id,
            arbiter_name=arbiter_name,
            decision=decision,
            justification=justification,
            selected_position=selected_position,
            modifications=modifications or {},
            signed_at=now,
            timestamp_token=timestamp_token,
            precedent_value="weak",  # Par défaut, devient "strong" après 3+ usages
        )

        # Journaliser la décision
        journal.append(
            event_type=JournalEventType.ARBITRATION_DECISION,
            client_id=arb["client_id"],
            vertical=arb["vertical"],
            agent_source="arbitration",
            intention_id=arb["intention_id"],
            payload={
                "arbitration_id": arbitration_id,
                "arbiter": arbiter_name,
                "decision": decision,
                "justification": justification,
                "selected_position": selected_position,
                "signed_at": now.isoformat(),
                "timestamp_token": timestamp_token is not None,
                "escalation_level": arb.get("current_arbiter", {}).get("level", "unknown"),
            },
        )

        # Enregistrer comme précédent
        self._save_precedent(dec, arb["vertical"])

        # Archiver
        self._completed_arbitrations[arbitration_id] = dec
        del self._pending_arbitrations[arbitration_id]

        logger.info(
            f"Arbitrage {arbitration_id[:8]}... décidé: {decision} "
            f"par {arbiter_name} (position: {selected_position})"
        )

        return dec

    def get_pending_arbitrations(self) -> list[dict]:
        """Lister les arbitrages en attente"""
        return list(self._pending_arbitrations.values())

    def get_arbitration(self, arbitration_id: str) -> Optional[dict]:
        """Récupérer un arbitrage spécifique"""
        if arbitration_id in self._pending_arbitrations:
            return self._pending_arbitrations[arbitration_id]
        if arbitration_id in self._completed_arbitrations:
            return self._completed_arbitrations[arbitration_id].model_dump()
        return None

    def get_precedents(self, vertical: str = None, limit: int = 50) -> list[dict]:
        """Récupérer les précédents d'arbitrage"""
        if not self._precedent_file.exists():
            return []

        with open(self._precedent_file, "r") as f:
            precedents = json.loads(f.read() or "[]")

        if vertical:
            precedents = [p for p in precedents if p.get("vertical") == vertical]

        return precedents[-limit:]

    # === Robustesse: Persistance timers escalade ===

    def _load_pending_timers(self) -> None:
        """Charger les timers d'escalade persistés au démarrage."""
        if not self._timers_file.exists():
            self._persisted_timers = {}
            return
        try:
            data = json.loads(self._timers_file.read_text(encoding="utf-8"))
            self._persisted_timers = data
            logger.info(f"Timers escalade chargés: {len(data)} en attente")
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Échec chargement timers escalade: {e}")
            self._persisted_timers = {}

    def _save_timer_state(self, arbitration_id: str, level_idx: int, deadline_iso: str) -> None:
        """Persister l'état d'un timer pour survie au redémarrage."""
        self._persisted_timers[arbitration_id] = {
            "level_idx": level_idx,
            "deadline": deadline_iso,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        self._flush_timers()

    def _remove_timer_state(self, arbitration_id: str) -> None:
        """Supprimer un timer persisté (décision soumise ou résolu)."""
        self._persisted_timers.pop(arbitration_id, None)
        self._flush_timers()

    def _flush_timers(self) -> None:
        """Écrire les timers sur disque (atomic write)."""
        try:
            tmp = self._timers_file.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(self._persisted_timers, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            tmp.replace(self._timers_file)
        except Exception as e:
            logger.error(f"Échec persistance timers escalade: {e}")

    def reschedule_pending_timers(self) -> None:
        """
        Re-programmer les timers d'escalade au redémarrage du service.
        
        Pour chaque timer persisté:
        1. Vérifier si la deadline est dépassée → escalade immédiate
        2. Sinon → calculer le temps restant et programmer
        
        Doit être appelé après le chargement des arbitrages pending.
        """
        now = datetime.now(timezone.utc)
        to_remove = []

        for arb_id, timer_data in self._persisted_timers.items():
            if arb_id not in self._pending_arbitrations:
                # Arbitrage déjà résolu entre-temps
                to_remove.append(arb_id)
                continue

            deadline = datetime.fromisoformat(timer_data["deadline"])
            remaining = (deadline - now).total_seconds()

            if remaining <= 0:
                # Deadline dépassée → escalade immédiate au niveau suivant
                level_idx = timer_data["level_idx"]
                logger.warning(
                    f"RESCHEULE: deadline dépassée pour {arb_id[:8]}... "
                    f"(niveau {level_idx}, dépassé de {-remaining:.0f}s)"
                )
                # L'escalade loop gérera le niveau suivant
                self._start_escalation_timer(arb_id, force_level=level_idx)
            else:
                # Reprogrammer avec le temps restant
                level_idx = timer_data["level_idx"]
                self._start_escalation_timer(arb_id, force_level=level_idx)
                logger.info(
                    f"RESCHEULE: timer reprogrammé pour {arb_id[:8]}... "
                    f"(niveau {level_idx}, reste {remaining:.0f}s)"
                )

        for arb_id in to_remove:
            self._remove_timer_state(arb_id)

    # === P0: Escalade automatique ===

    def _start_escalation_timer(self, arbitration_id: str, force_level: int = 0) -> None:
        """Démarrer le timer d'escalade pour un arbitrage en attente.
        
        Args:
            force_level: Si > 0, reprendre à ce niveau (reschedule).
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            task = loop.create_task(
                self._escalation_loop(arbitration_id, start_level=force_level)
            )
            self._escalation_tasks[arbitration_id] = task

            # Robustesse: persister le timer
            arb = self._pending_arbitrations.get(arbitration_id)
            if arb:
                level_idx = force_level
                deadline_iso = arb.get("current_arbiter", {}).get("deadline")
                if deadline_iso:
                    self._save_timer_state(arbitration_id, level_idx, deadline_iso)
        else:
            logger.debug(f"Escalade timer différé pour {arbitration_id[:8]}... (pas de loop)")

    def _cancel_escalation_timer(self, arbitration_id: str) -> None:
        """Annuler le timer d'escalade et nettoyer la persistance."""
        task = self._escalation_tasks.pop(arbitration_id, None)
        if task and not task.done():
            task.cancel()
            logger.debug(f"Timer d'escalade annulé pour {arbitration_id[:8]}...")
        # Robustesse: supprimer la persistance
        self._remove_timer_state(arbitration_id)

    async def _escalation_loop(self, arbitration_id: str, start_level: int = 0) -> None:
        """
        Boucle d'escalade automatique.
        
        Pour chaque niveau de la chaîne:
        1. Attendre le timeout configuré
        2. Si toujours pending → escalader au niveau suivant
        3. Si dernier niveau atteint → notifier l'admin
        
        Args:
            start_level: Niveau de départ (0=normal, >0=reschedule)
        """
        arb = self._pending_arbitrations.get(arbitration_id)
        if not arb:
            return

        for level_idx, timeout_hours in enumerate(self._escalation_timeout_hours):
            if level_idx < start_level:
                continue

            # Calculer le temps d'attente
            if start_level > 0 and level_idx == start_level:
                # Reschedule: calculer le temps restant depuis la persistance
                timer_data = self._persisted_timers.get(arbitration_id)
                if timer_data and "deadline" in timer_data:
                    deadline = datetime.fromisoformat(timer_data["deadline"])
                    remaining = (deadline - datetime.now(timezone.utc)).total_seconds()
                    wait_seconds = max(remaining, 0)
                else:
                    wait_seconds = timeout_hours * 3600
            else:
                wait_seconds = timeout_hours * 3600

            # Attendre le timeout
            await asyncio.sleep(wait_seconds)

            # Vérifier si l'arbitrage est toujours en attente
            arb = self._pending_arbitrations.get(arbitration_id)
            if not arb:
                return  # Déjà résolu

            # Escalader au niveau suivant
            next_level_idx = level_idx + 1

            if next_level_idx < len(self._escalation_chain):
                next_arbiter = self._escalation_chain[next_level_idx]
                level_name = [EscalationLevel.PRIMARY, EscalationLevel.SUBSTITUTE, EscalationLevel.PARTNER, EscalationLevel.ADMIN]
                next_level = level_name[min(next_level_idx, len(level_name) - 1)]

                # Journaliser l'escalade
                journal.append(
                    event_type=JournalEventType.ARBITRATION_REQUESTED,
                    client_id=arb.get("client_id", "unknown"),
                    vertical=arb.get("vertical", "unknown"),
                    agent_source="arbitration",
                    intention_id=arb.get("intention_id", "unknown"),
                    payload={
                        "arbitration_id": arbitration_id,
                        "event": "escalation",
                        "from_level": arb.get("current_arbiter", {}).get("level", "unknown"),
                        "to_level": next_level,
                        "from_arbiter": arb.get("current_arbiter", {}).get("name", "unknown"),
                        "to_arbiter": next_arbiter,
                        "timeout_hours": timeout_hours,
                    },
                )

                # Mettre à jour le dashboard
                arb["escalation_history"].append({
                    "from": arb["current_arbiter"]["name"],
                    "to": next_arbiter,
                    "level": next_level,
                    "reason": f"Timeout après {timeout_hours}h",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                arb["current_arbiter"] = {
                    "level": next_level,
                    "name": next_arbiter,
                    "assigned_at": datetime.now(timezone.utc).isoformat(),
                    "deadline": (datetime.now(timezone.utc) + timedelta(
                        hours=self._escalation_timeout_hours[next_level_idx]
                        if next_level_idx < len(self._escalation_timeout_hours) else 24
                    )).isoformat(),
                }

                logger.warning(
                    f"ESCALADE: arbitrage {arbitration_id[:8]}... "
                    f"{arb['escalation_history'][-1]['from']} → {next_arbiter} "
                    f"(timeout {timeout_hours}h)"
                )
            else:
                # Dernier niveau atteint — notifier admin système
                logger.critical(
                    f"ESCALADE MAX: arbitrage {arbitration_id[:8]}... "
                    f"aucun arbitre n'a répondu après {len(self._escalation_chain)} niveaux"
                )
                arb["status"] = "escalation_exhausted"
                arb["escalation_history"].append({
                    "level": "exhausted",
                    "reason": f"Tous les arbitres ont été contactés sans réponse",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                return

    # === Méthodes internes ===

    def _simulate_impact(self, position: dict, vertical: str) -> dict:
        """Simuler l'impact d'un choix (pour l'interface d'arbitrage)"""
        confidence = position.get("confidence", 0.5)
        return {
            "risk_level": "high" if confidence < 0.5 else "medium" if confidence < 0.7 else "low",
            "compliance_impact": "neutral",
            "data_exposure": "none" if vertical in ("avocat", "banque") else "minimal",
            "reversibility": "reversible" if position.get("recommendation") != "executed" else "partial",
        }

    def _generate_timestamp_token(self, dt: datetime) -> str:
        """Générer un token d'horodatage (RFC 3161 simplifié)"""
        content = dt.isoformat() + settings.journal_signing_key
        return hmac.new(
            settings.journal_signing_key.encode(),
            content.encode(),
            hashlib.sha256,
        ).hexdigest()

    def _save_precedent(self, decision: ArbitrationDecision, vertical: str) -> None:
        """Sauvegarder la décision comme précédent"""
        precedents = []
        if self._precedent_file.exists():
            with open(self._precedent_file, "r") as f:
                precedents = json.loads(f.read() or "[]")

        # Vérifier si ce précédent existe déjà (similarité)
        precedent_entry = {
            "arbitration_id": decision.arbitration_id,
            "vertical": vertical,
            "conflict_type": "agent_divergence",
            "decision": decision.decision,
            "selected_position": decision.selected_position,
            "justification_summary": decision.justification[:200],
            "signed_at": decision.signed_at.isoformat(),
            "arbiter": decision.arbiter_name,
        }

        # Mettre à jour la force du précédent
        similar = [
            p for p in precedents
            if p.get("selected_position") == decision.selected_position
            and p.get("vertical") == vertical
        ]
        precedent_entry["precedent_strength"] = (
            "strong" if len(similar) >= 2 else "moderate" if len(similar) >= 1 else "weak"
        )

        precedents.append(precedent_entry)

        with open(self._precedent_file, "w") as f:
            json.dump(precedents, f, ensure_ascii=False, indent=2)


# Singleton
arbitration_service = ArbitrationService()
