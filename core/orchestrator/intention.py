"""
Cortex Leman v5 — Intention Store Unifié

Combine l'IntentionStore (CRUD + persistance) et la StateFlow State Machine
en un seul store cohérent.

States: created → routed → processing → [frozen → arbitrating → unfrozen] → completed
Persistance fichier JSON (atomic write) pour survie au redémarrage.
"""
import json
import uuid
import logging
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from core.journal.models import IntentionModel

logger = logging.getLogger(__name__)


# ── State Machine ─────────────────────────────────────────────

class IntentionState(str, Enum):
    """États possibles d'une intention"""
    CREATED = "created"
    ROUTED = "routed"
    PROCESSING = "processing"
    FROZEN = "frozen"
    DEGRADED_FROZEN = "degraded_frozen"  # P0: Action gelée, Data+Raisonnement continuent
    ARBITRATING = "arbitrating"
    UNFROZEN = "unfrozen"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Transitions valides (from → [to, to, ...])
VALID_TRANSITIONS: dict[IntentionState, list[IntentionState]] = {
    IntentionState.CREATED:         [IntentionState.ROUTED, IntentionState.CANCELLED],
    IntentionState.ROUTED:          [IntentionState.PROCESSING, IntentionState.FROZEN, IntentionState.DEGRADED_FROZEN, IntentionState.CANCELLED],
    IntentionState.PROCESSING:      [IntentionState.FROZEN, IntentionState.DEGRADED_FROZEN, IntentionState.COMPLETED, IntentionState.FAILED],
    IntentionState.DEGRADED_FROZEN: [IntentionState.ARBITRATING, IntentionState.FROZEN, IntentionState.CANCELLED],
    IntentionState.FROZEN:          [IntentionState.ARBITRATING, IntentionState.CANCELLED],
    IntentionState.ARBITRATING:     [IntentionState.UNFROZEN, IntentionState.CANCELLED],
    IntentionState.UNFROZEN:        [IntentionState.PROCESSING, IntentionState.FROZEN],
    IntentionState.COMPLETED:       [],
    IntentionState.FAILED:          [],
    IntentionState.CANCELLED:       [],
}

# Alias de status string → IntentionState (rétrocompatibilité)
_STATUS_MAP = {
    "active":          IntentionState.CREATED,
    "routed":          IntentionState.ROUTED,
    "processing":      IntentionState.PROCESSING,
    "frozen":          IntentionState.FROZEN,
    "degraded_frozen": IntentionState.DEGRADED_FROZEN,
    "arbitrating":     IntentionState.ARBITRATING,
    "unfrozen":        IntentionState.UNFROZEN,
    "completed":       IntentionState.COMPLETED,
    "failed":          IntentionState.FAILED,
    "cancelled":       IntentionState.CANCELLED,
}


# ── Unified Store ─────────────────────────────────────────────

class IntentionStore:
    """
    Store unifié pour les intentions actives.

    - CRUD avec persistance fichier JSON (atomic write)
    - State machine intégrée (transitions validées)
    - En production: Redis ou NATS KV
    """

    def __init__(self, persist_path: Optional[str] = None):
        self._intentions: dict[str, IntentionModel] = {}
        self._states: dict[str, IntentionState] = {}
        self._history: dict[str, list[dict]] = {}
        self._persist_path = Path(persist_path or "./data/intentions.json")
        self._load()

    # ── Persistance ──────────────────────────────────────

    def _load(self) -> None:
        if not self._persist_path.exists():
            return
        try:
            data = json.loads(self._persist_path.read_text(encoding="utf-8"))
            for iid, idata in data.items():
                self._intentions[iid] = IntentionModel(**idata)
                status = idata.get("status", "active")
                self._states[iid] = _STATUS_MAP.get(status, IntentionState.CREATED)
            logger.info(f"IntentionStore: {len(self._intentions)} intentions chargées")
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"IntentionStore: échec chargement: {e}")

    def _save(self) -> None:
        try:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            data = {iid: i.model_dump(mode="json") for iid, i in self._intentions.items()}
            tmp = self._persist_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
            tmp.replace(self._persist_path)  # atomic
        except Exception as e:
            logger.error(f"IntentionStore: échec persistance: {e}")

    # ── State Machine ────────────────────────────────────

    def _transition(self, intention_id: str, target: IntentionState, trigger: str, reason: str = "") -> bool:
        """Tenter une transition d'état. Retourne True si OK."""
        current = self._states.get(intention_id, IntentionState.CREATED)
        allowed = VALID_TRANSITIONS.get(current, [])
        if target not in allowed:
            logger.warning(f"Transition invalide: {current.value} → {target.value} pour {intention_id[:8]}")
            return False

        self._history.setdefault(intention_id, []).append({
            "from": current.value,
            "to": target.value,
            "trigger": trigger,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self._states[intention_id] = target
        logger.info(f"Intention {intention_id[:8]}: {current.value} → {target.value} ({trigger})")
        return True

    def get_state(self, intention_id: str) -> Optional[IntentionState]:
        return self._states.get(intention_id)

    def get_history(self, intention_id: str) -> list[dict]:
        return self._history.get(intention_id, [])

    @property
    def defrozen(self) -> frozenset[IntentionState]:
        """États actifs (non terminaux)."""
        return frozenset({
            IntentionState.CREATED, IntentionState.ROUTED,
            IntentionState.PROCESSING, IntentionState.UNFROZEN,
        })

    # ── CRUD ─────────────────────────────────────────────

    def create(
        self,
        client_id: str,
        vertical: str,
        query: str,
        context: dict = None,
        parent_id: Optional[str] = None,
    ) -> IntentionModel:
        intention = IntentionModel(
            intention_id=str(uuid.uuid4()),
            client_id=client_id,
            vertical=vertical,
            original_query=query,
            refined_query=query,
            context=context or {},
            parent_intention_id=parent_id,
        )
        iid = intention.intention_id
        self._intentions[iid] = intention
        self._states[iid] = IntentionState.CREATED
        self._save()
        return intention

    def revise(
        self,
        intention_id: str,
        refined_query: Optional[str] = None,
        context_update: Optional[dict] = None,
        status: Optional[str] = None,
        assigned_agents: Optional[list[str]] = None,
    ) -> IntentionModel:
        current = self._intentions.get(intention_id)
        if not current:
            raise KeyError(f"Intention {intention_id} non trouvée")

        updated = current.model_copy(update={
            "version": current.version + 1,
            "refined_query": refined_query or current.refined_query,
            "context": {**current.context, **(context_update or {})},
            "status": status or current.status,
            "assigned_agents": assigned_agents or current.assigned_agents,
            "updated_at": datetime.now(timezone.utc),
        })
        self._intentions[intention_id] = updated

        # Mettre à jour la state machine si le status change
        if status and status != current.status:
            target = _STATUS_MAP.get(status)
            if target:
                self._transition(intention_id, target, "revise", f"status→{status}")

        self._save()
        return updated

    def route(self, intention_id: str, assigned_agents: list[str]) -> bool:
        """Transition: created → routed"""
        ok = self._transition(intention_id, IntentionState.ROUTED, "router", f"agents={assigned_agents}")
        if ok:
            self._update_model(intention_id, status="routed", assigned_agents=assigned_agents)
        return ok

    def start_processing(self, intention_id: str) -> bool:
        """Transition: routed → processing"""
        ok = self._transition(intention_id, IntentionState.PROCESSING, "orchestrator")
        if ok:
            self._update_model(intention_id, status="processing")
        return ok

    def freeze(self, intention_id: str, reason: str = "", degraded: bool = False) -> IntentionModel:
        """Geler une intention (Médiateur).
        
        Args:
            degraded: Si True, mode dégradé conforme — Action gelée mais
                      Data et Raisonnement continuent de travailler.
                      L'arbitre humain reçoit un dossier enrichi.
        """
        state = self._states.get(intention_id, IntentionState.CREATED)
        target = IntentionState.DEGRADED_FROZEN if degraded else IntentionState.FROZEN
        status = "degraded_frozen" if degraded else "frozen"

        if state in (IntentionState.PROCESSING, IntentionState.ROUTED, IntentionState.CREATED):
            self._transition(intention_id, target, "mediator", reason)
        return self.revise(intention_id, status=status)

    def is_fully_frozen(self, intention_id: str) -> bool:
        """True si l'intention est gelée complètement (pas dégradé)."""
        return self._states.get(intention_id) == IntentionState.FROZEN

    def is_degraded_frozen(self, intention_id: str) -> bool:
        """True si l'intention est en mode dégradé conforme."""
        return self._states.get(intention_id) == IntentionState.DEGRADED_FROZEN

    def is_action_blocked(self, intention_id: str) -> bool:
        """True si l'Agent Action doit être bloqué (gel complet ou dégradé)."""
        state = self._states.get(intention_id)
        return state in (IntentionState.FROZEN, IntentionState.DEGRADED_FROZEN)

    def start_arbitration(self, intention_id: str, reason: str = "") -> bool:
        """Transition: frozen → arbitrating"""
        ok = self._transition(intention_id, IntentionState.ARBITRATING, "human", reason)
        if ok:
            self._update_model(intention_id, status="arbitrating")
        return ok

    def unfreeze(self, intention_id: str, reason: str = "") -> IntentionModel:
        """Dégeler une intention (arbitrage résolu)."""
        state = self._states.get(intention_id)
        if state == IntentionState.FROZEN:
            self._transition(intention_id, IntentionState.ARBITRATING, "human", "arbitrage_start")
        self._transition(intention_id, IntentionState.UNFROZEN, "human", reason)
        return self.revise(intention_id, status="active")

    def complete(self, intention_id: str, reason: str = "") -> IntentionModel:
        """Marquer comme complétée."""
        self._transition(intention_id, IntentionState.COMPLETED, "agent", reason)
        return self.revise(intention_id, status="completed")

    def fail(self, intention_id: str, reason: str = "") -> bool:
        """Transition: processing → failed"""
        ok = self._transition(intention_id, IntentionState.FAILED, "system", reason)
        if ok:
            self._update_model(intention_id, status="failed")
        return ok

    def cancel(self, intention_id: str, reason: str = "") -> bool:
        state = self._states.get(intention_id)
        if not state:
            return False
        allowed = VALID_TRANSITIONS.get(state, [])
        if IntentionState.CANCELLED not in allowed:
            return False
        ok = self._transition(intention_id, IntentionState.CANCELLED, "user", reason)
        if ok:
            self._update_model(intention_id, status="cancelled")
        return ok

    def get(self, intention_id: str) -> Optional[IntentionModel]:
        return self._intentions.get(intention_id)

    def get_active_for_client(self, client_id: str) -> list[IntentionModel]:
        active_states = self.defrozen
        return [
            i for i in self._intentions.values()
            if i.client_id == client_id and self._states.get(i.intention_id) in active_states
        ]

    def _update_model(self, intention_id: str, **kwargs) -> None:
        intention = self._intentions.get(intention_id)
        if intention:
            updated = intention.model_copy(update={
                **kwargs,
                "updated_at": datetime.now(timezone.utc),
            })
            self._intentions[intention_id] = updated
            self._save()


# Singleton
intention_store = IntentionStore()
