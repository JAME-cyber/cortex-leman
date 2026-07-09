"""
Cortex Leman v5 — Handoff JSON

Breadcrumbs structurés pour les sessions futures.
Inspiré de: Ash (Anthropic Applied AI) — "leave breadcrumbs for the next agent".

Principe: après chaque mission, l'agent écrit un handoff.json que le prochain
agent (ou un humain) peut lire pour reprendre le travail sans perte de contexte.

Pourquoi JSON et pas Markdown:
- Les modèles n'écrasent pas le JSON aussi facilement que le markdown (Andrew, Anthropic)
- Parsable programmatiquement
- Schema validation possible

Usage:
    from core.agents.handoff import handoff_store

    # Écrire un handoff après une mission
    handoff = handoff_store.create(
        intention_id="abc123",
        agent_name="reasoning",
        mission_summary="Analyse fiscale pour le client X",
        features=[...],
        lessons=["Ne pas utiliser l'API Y sans timeout"],
    )

    # Lire le dernier handoff pour une intention
    last = handoff_store.get_latest("abc123")

    # Lister tous les handoffs
    all_handoffs = handoff_store.list_for_intention("abc123")
"""
import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ── Modèles ───────────────────────────────────────────────────

class FeatureAttempt(BaseModel):
    """Une feature tentée pendant la mission"""
    feature: str
    status: str  # "done" | "failed" | "partial" | "skipped"
    tests_pass: bool = False
    reason: str = ""  # Pourquoi ça a échoué si status=failed


class Lesson(BaseModel):
    """Un apprentissage de la mission"""
    category: str  # "pattern" | "anti-pattern" | "api" | "config" | "edge_case"
    description: str
    applies_to: str = ""  # "all" | "vertical:avocat" | "agent:action"


class HandoffDocument(BaseModel):
    """
    Document de passation structuré entre sessions.

    Écrit par un agent à la fin de sa mission, lu par le prochain agent
    (ou un humain dans Claude Code / Pi) qui reprend le travail.
    """
    # Identité
    handoff_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    intention_id: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Source
    agent_name: str  # "reasoning" | "action" | "evaluator" | "data"
    session_duration_sec: float = 0.0
    vertical: str = ""

    # Résumé de la mission
    mission_summary: str
    mission_outcome: str  # "success" | "partial" | "failed" | "blocked"

    # Features
    features_attempted: list[FeatureAttempt] = Field(default_factory=list)
    features_done: int = 0
    features_failed: int = 0

    # Apprentissages
    lessons_learned: list[Lesson] = Field(default_factory=list)

    # Fichiers modifiés
    files_modified: list[str] = Field(default_factory=list)
    files_created: list[str] = Field(default_factory=list)

    # Prochaines étapes
    next_steps: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)

    # Contexte pour le prochain agent
    context_notes: str = ""
    api_calls_made: list[str] = Field(default_factory=list)
    models_used: list[str] = Field(default_factory=list)
    tokens_consumed: int = 0

    # État du pipeline
    mediator_checks: int = 0
    mediator_blocks: int = 0
    arbitration_triggered: bool = False

    model_config = {"arbitrary_types_allowed": True}


class HandoffStore:
    """
    Store pour les documents de handoff.

    Persistance: fichier JSON par intention dans data/handoffs/
    Format: un fichier par intention contenant une liste de handoffs.
    """

    def __init__(self, persist_dir: str = "./data/handoffs"):
        self._persist_dir = Path(persist_dir)
        self._persist_dir.mkdir(parents=True, exist_ok=True)

    def create(
        self,
        intention_id: str,
        agent_name: str,
        mission_summary: str,
        mission_outcome: str = "success",
        vertical: str = "",
        features: list[FeatureAttempt] = None,
        lessons: list[Lesson] = None,
        files_modified: list[str] = None,
        files_created: list[str] = None,
        next_steps: list[str] = None,
        blockers: list[str] = None,
        context_notes: str = "",
        session_duration_sec: float = 0.0,
        tokens_consumed: int = 0,
        models_used: list[str] = None,
        api_calls_made: list[str] = None,
        mediator_checks: int = 0,
        mediator_blocks: int = 0,
        arbitration_triggered: bool = False,
    ) -> HandoffDocument:
        """Créer et persister un handoff document."""

        features = features or []
        lessons = lessons or []
        files_modified = files_modified or []
        files_created = files_created or []
        next_steps = next_steps or []
        blockers = blockers or []
        models_used = models_used or []
        api_calls_made = api_calls_made or []

        handoff = HandoffDocument(
            intention_id=intention_id,
            agent_name=agent_name,
            mission_summary=mission_summary,
            mission_outcome=mission_outcome,
            vertical=vertical,
            features_attempted=features,
            features_done=sum(1 for f in features if f.status == "done"),
            features_failed=sum(1 for f in features if f.status == "failed"),
            lessons_learned=lessons,
            files_modified=files_modified,
            files_created=files_created,
            next_steps=next_steps,
            blockers=blockers,
            context_notes=context_notes,
            session_duration_sec=session_duration_sec,
            tokens_consumed=tokens_consumed,
            models_used=models_used,
            api_calls_made=api_calls_made,
            mediator_checks=mediator_checks,
            mediator_blocks=mediator_blocks,
            arbitration_triggered=arbitration_triggered,
        )

        self._persist(handoff)
        logger.info(
            f"Handoff créé: {handoff.handoff_id} "
            f"({agent_name}, intention={intention_id[:8]}..., "
            f"outcome={mission_outcome})"
        )
        return handoff

    def get_latest(self, intention_id: str) -> Optional[HandoffDocument]:
        """Récupérer le dernier handoff pour une intention."""
        handoffs = self._load(intention_id)
        return handoffs[-1] if handoffs else None

    def list_for_intention(self, intention_id: str) -> list[HandoffDocument]:
        """Lister tous les handoffs pour une intention (chronologique)."""
        return self._load(intention_id)

    def get_all_lessons(
        self,
        vertical: str = None,
        category: str = None,
    ) -> list[Lesson]:
        """Récupérer tous les apprentissages accumulés (toutes intentions)."""
        all_lessons = []
        for path in self._persist_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for entry in data:
                    for lesson in entry.get("lessons_learned", []):
                        if vertical and lesson.get("applies_to", "").endswith(vertical):
                            continue
                        if category and lesson.get("category") != category:
                            continue
                        all_lessons.append(Lesson(**lesson))
            except Exception:
                continue
        return all_lessons

    def get_timeline(self, intention_id: str) -> list[dict]:
        """Récupérer la timeline complète d'une intention."""
        handoffs = self._load(intention_id)
        return [
            {
                "handoff_id": h.handoff_id,
                "agent": h.agent_name,
                "timestamp": h.timestamp,
                "outcome": h.mission_outcome,
                "summary": h.mission_summary[:100],
                "features_done": h.features_done,
                "features_failed": h.features_failed,
                "blockers": h.blockers,
            }
            for h in handoffs
        ]

    def generate_handoff_prompt(self, intention_id: str) -> str:
        """
        Générer un prompt de reprise pour le prochain agent.
        C'est le texte à injecter dans le context du prochain agent.
        """
        latest = self.get_latest(intention_id)
        if not latest:
            return ""

        timeline = self.get_timeline(intention_id)

        features_status = "\n".join(
            f"  - {f.feature}: {f.status} {'(tests OK)' if f.tests_pass else ''} "
            f"{f.reason if f.status == 'failed' else ''}"
            for f in latest.features_attempted
        ) or "  (aucune feature enregistrée)"

        lessons_text = "\n".join(
            f"  - [{l.category}] {l.description}"
            for l in latest.lessons_learned
        ) or "  (aucun apprentissage enregistré)"

        next_steps_text = "\n".join(
            f"  {i+1}. {s}" for i, s in enumerate(latest.next_steps)
        ) or "  (aucune étape suivante)"

        return f"""══ CONTEXTE DE REPRISE ═════════════════════════════════
Intention: {intention_id[:8]}... | Verticale: {latest.vertical}
Dernier agent: {latest.agent_name} | Outcome: {latest.mission_outcome}
Durée session: {latest.session_duration_sec:.0f}s | Tokens: {latest.tokens_consumed}

Résumé: {latest.mission_summary}

Features tentées ({latest.features_done} OK / {latest.features_failed} FAIL):
{features_status}

Apprentissages:
{lessons_text}

Fichiers modifiés: {', '.join(latest.files_modified[-10:]) or 'aucun'}

Prochaines étapes:
{next_steps_text}

Blockers: {', '.join(latest.blockers) or 'aucun'}

Notes: {latest.context_notes or 'aucune'}

Timeline ({len(timeline)} sessions):
{chr(10).join(f'  {t["timestamp"][:19]} | {t["agent"]:12} | {t["outcome"]:8} | {t["summary"]}' for t in timeline[-5:])}
════════════════════════════════════════════════════════"""

    # ── Persistance ──────────────────────────────────────

    def _persist(self, handoff: HandoffDocument) -> None:
        """Persister un handoff (append-only)."""
        path = self._persist_dir / f"{handoff.intention_id}.json"
        existing = self._load_raw(handoff.intention_id)
        existing.append(handoff.model_dump(mode="json"))

        # Atomic write
        tmp = path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        tmp.replace(path)

    def _load(self, intention_id: str) -> list[HandoffDocument]:
        """Charger les handoffs pour une intention."""
        raw = self._load_raw(intention_id)
        return [HandoffDocument(**entry) for entry in raw]

    def _load_raw(self, intention_id: str) -> list[dict]:
        """Charger le JSON brut."""
        path = self._persist_dir / f"{intention_id}.json"
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Handoff load error for {intention_id[:8]}: {e}")
            return []


# Singleton
handoff_store = HandoffStore()
