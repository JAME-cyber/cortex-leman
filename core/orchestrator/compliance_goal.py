"""
Cortex Leman v5 — Compliance Goal

Tâches de conformité longue durée, autonomes, auto-vérifiantes.
Inspiré du /slash goal de Codex (OpenAI) adapté à la conformité.

Le client donne un objectif de conformité:
  "Audit AI Act complet de notre startup d'ici vendredi"

Le système:
  1. Décompose en sous-tâches (Data, Raisonnement, Compliance)
  2. Exécute chaque sous-tâche via les agents existants
  3. Le Médiateur vérifie à chaque étape
  4. Le PrecedentStore enrichit les décisions
  5. Résultat: rapport complet avec preuve légale dans le journal WORM

États d'un goal:
  PENDING → RUNNING → [PAUSED → RUNNING] → COMPLETED | FAILED

Progression trackée dans le journal.
Vérifiable à tout moment via l'API.
"""
import uuid
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType
from core.config import settings

logger = logging.getLogger(__name__)


# ── Models ────────────────────────────────────────────────────

class GoalStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"       # Gel par le Médiateur → en attente d'arbitrage
    COMPLETED = "completed"
    FAILED = "failed"


class SubTaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    BLOCKED = "blocked"     # Médiateur a gelé cette sous-tâche
    DONE = "done"
    FAILED = "failed"


class SubTask(BaseModel):
    """Sous-tâche d'un compliance goal."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    agent: str  # data | reasoning | compliance | action
    status: SubTaskStatus = SubTaskStatus.PENDING
    result: Optional[dict] = None
    confidence: float = 0.0
    regulatory_refs: list[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class ComplianceGoal(BaseModel):
    """Un objectif de conformité longue durée."""
    goal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    vertical: str
    title: str
    description: str
    status: GoalStatus = GoalStatus.PENDING
    subtasks: list[SubTask] = Field(default_factory=list)
    result: Optional[dict] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    intention_id: Optional[str] = None  # Lié à une intention orchestrator
    deadline: Optional[datetime] = None
    progress: float = 0.0  # 0.0 → 1.0
    total_tokens_used: int = 0
    precedent_ids: list[str] = Field(default_factory=list)  # Précédents utilisés


# ── Goal Templates par verticale ──────────────────────────────

GOAL_TEMPLATES: dict[str, list[dict]] = {
    "comptable": [
        {
            "name": "Audit RGPD Annuel",
            "description": "Audit RGPD complet du cabinet: registre des traitements, AIPD, consentements, sous-traitants",
            "subtasks": [
                {"name": "Inventaire traitements", "description": "Recenser tous les traitements de données personnelles", "agent": "data"},
                {"name": "Vérification consentements", "description": "Vérifier la validité des consentements collectés", "agent": "reasoning"},
                {"name": "Audit sous-traitants", "description": "Vérifier les contrats sous-traitants (Art. 28 RGPD)", "agent": "reasoning"},
                {"name": "AIPD auto-évaluation", "description": "Générer l'Analyse d'Impact si traitements à risque", "agent": "compliance"},
                {"name": "Rapport final", "description": "Compiler le rapport d'audit avec recommandations", "agent": "reasoning"},
            ],
        },
        {
            "name": "Contrôle Conformité Fiscale",
            "description": "Vérifier la conformité des déclarations fiscales et des déductions",
            "subtasks": [
                {"name": "Analyse déductions", "description": "Vérifier les déductions fiscales déclarées", "agent": "data"},
                {"name": "Vérification seuils TVA", "description": "Contrôler les seuils de TVA applicables", "agent": "reasoning"},
                {"name": "Rapprochement comptable", "description": "Rapprocher les montants déclarés avec les justificatifs", "agent": "data"},
                {"name": "Rapport conformité", "description": "Générer le rapport de contrôle fiscal", "agent": "compliance"},
            ],
        },
    ],
    "avocat": [
        {
            "name": "Audit Secret Professionnel",
            "description": "Vérifier que le cabinet respecte Art. 321 CP / Art. 226-13 CP dans tous ses traitements IA",
            "subtasks": [
                {"name": "Cartographie données sensibles", "description": "Identifier toutes les données client traitées par IA", "agent": "data"},
                {"name": "Vérification confinement", "description": "Vérifier que les données sensibles ne sortent pas du périmètre", "agent": "reasoning"},
                {"name": "Audit Cloud Provider", "description": "Vérifier la localisation et le traitement par les fournisseurs cloud", "agent": "compliance"},
                {"name": "Test de fuite", "description": "Simuler une fuite de données et vérifier la réponse", "agent": "reasoning"},
                {"name": "Attestation secret", "description": "Générer l'attestation de conformité secret professionnel", "agent": "compliance"},
            ],
        },
    ],
    "banque": [
        {
            "name": "Audit KYC/AML",
            "description": "Vérification conformité KYC et anti-blanchiment (AML 4/5, FINMA)",
            "subtasks": [
                {"name": "Contrôle identité clients", "description": "Vérifier les procédures d'identification client", "agent": "data"},
                {"name": "Analyse transactions suspectes", "description": "Détecter les patterns de transactions anormales", "agent": "reasoning"},
                {"name": "Vérification PEP/sanctions", "description": "Screening Personnes Politiquement Exposées et listes de sanctions", "agent": "data"},
                {"name": "Rapport FINMA", "description": "Générer le rapport de conformité FINMA", "agent": "compliance"},
            ],
        },
    ],
    "sante": [
        {
            "name": "Audit HDS & Données Patient",
            "description": "Vérifier la conformité hébergement données de santé (HDS, LPM)",
            "subtasks": [
                {"name": "Inventaire données patient", "description": "Recenser toutes les données de santé traitées", "agent": "data"},
                {"name": "Vérification hébergeur certifié", "description": "Vérifier la certification HDS de l'hébergeur", "agent": "reasoning"},
                {"name": "Contrôle accès", "description": "Vérifier les contrôles d'accès aux données patient", "agent": "compliance"},
                {"name": "Rapport LPM", "description": "Générer le rapport de conformité LPM", "agent": "compliance"},
            ],
        },
    ],
    "startup": [
        {
            "name": "AI Act Compliance Check",
            "description": "Checklist complète AI Act pour startup (risque limité/transparent)",
            "subtasks": [
                {"name": "Classification IA", "description": "Classifier le système IA selon AI Act Art. 6", "agent": "reasoning"},
                {"name": "Vérification Art. 52", "description": "Vérifier les obligations de transparence", "agent": "reasoning"},
                {"name": "Documentation technique", "description": "Vérifier la documentation technique requise", "agent": "data"},
                {"name": "AIPD", "description": "Générer l'Analyse d'Impact (Art. 35 RGPD)", "agent": "compliance"},
                {"name": "Checklist finale", "description": "Compiler la checklist AI Act complète", "agent": "compliance"},
            ],
        },
    ],
    "rh": [
        {
            "name": "Audit Anti-Discrimination IA",
            "description": "Vérifier que les outils IA RH ne discriminent pas (RGPD Art. 22, Loi 2008-496)",
            "subtasks": [
                {"name": "Audit algorithmes sélection", "description": "Vérifier les biais dans les algorithmes de sélection", "agent": "reasoning"},
                {"name": "Vérification Art. 22", "description": "Vérifier le droit à intervention humaine (décision automatisée)", "agent": "compliance"},
                {"name": "Test biais", "description": "Tester les disparités d'impact sur groupes protégés", "agent": "data"},
                {"name": "Rapport anti-discrimination", "description": "Générer le rapport de conformité", "agent": "compliance"},
            ],
        },
    ],
}


# ── Goal Runner ───────────────────────────────────────────────

class ComplianceGoalRunner:
    """
    Orchestrateur de tâches de conformité longue durée.

    Utilise les agents existants (Data, Raisonnement, Compliance)
    et les passe par le Médiateur à chaque étape.
    """

    def __init__(self):
        self._goals: dict[str, ComplianceGoal] = {}

    def create_goal(
        self,
        client_id: str,
        vertical: str,
        title: str,
        description: str,
        template_name: Optional[str] = None,
        deadline: Optional[datetime] = None,
    ) -> ComplianceGoal:
        """
        Créer un nouveau compliance goal.

        Si un template_name est fourni, utilise les sous-tâches du template.
        Sinon, le titre et la description sont utilisés directement.
        """
        subtasks = []

        # Chercher un template correspondant
        if template_name:
            templates = GOAL_TEMPLATES.get(vertical, [])
            for tmpl in templates:
                if tmpl["name"].lower() == template_name.lower():
                    for st in tmpl["subtasks"]:
                        subtasks.append(SubTask(
                            name=st["name"],
                            description=st["description"],
                            agent=st["agent"],
                        ))
                    break
        elif title:
            # Recherche par titre dans les templates
            templates = GOAL_TEMPLATES.get(vertical, [])
            title_lower = title.lower()
            for tmpl in templates:
                if any(kw in title_lower for kw in tmpl["name"].lower().split()):
                    for st in tmpl["subtasks"]:
                        subtasks.append(SubTask(
                            name=st["name"],
                            description=st["description"],
                            agent=st["agent"],
                        ))
                    break

        if not subtasks:
            # Créer des sous-tâches génériques
            subtasks = [
                SubTask(name="Collecte données", description="Collecter les données nécessaires", agent="data"),
                SubTask(name="Analyse réglementaire", description="Analyser la conformité réglementaire", agent="reasoning"),
                SubTask(name="Vérification Médiateur", description="Passer par le Médiateur", agent="compliance"),
                SubTask(name="Rapport final", description="Générer le rapport", agent="reasoning"),
            ]

        goal = ComplianceGoal(
            client_id=client_id,
            vertical=vertical,
            title=title,
            description=description,
            subtasks=subtasks,
            deadline=deadline,
        )

        self._goals[goal.goal_id] = goal

        # Journaliser la création
        journal.append(
            event_type=JournalEventType.COMPLIANCE_CHECK,
            client_id=client_id,
            vertical=vertical,
            agent_source="compliance_goal",
            intention_id=goal.goal_id,
            payload={
                "event": "goal_created",
                "title": title,
                "subtask_count": len(subtasks),
                "deadline": deadline.isoformat() if deadline else None,
            },
        )

        logger.info(
            f"ComplianceGoal: créé {goal.goal_id[:8]}... "
            f"«{title}» ({len(subtasks)} sous-tâches)"
        )
        return goal

    def start_goal(self, goal_id: str) -> Optional[ComplianceGoal]:
        """Démarrer l'exécution d'un goal."""
        goal = self._goals.get(goal_id)
        if not goal or goal.status != GoalStatus.PENDING:
            return None

        goal.status = GoalStatus.RUNNING
        goal.started_at = datetime.now(timezone.utc)

        journal.append(
            event_type=JournalEventType.COMPLIANCE_CHECK,
            client_id=goal.client_id,
            vertical=goal.vertical,
            agent_source="compliance_goal",
            intention_id=goal_id,
            payload={"event": "goal_started"},
        )

        return goal

    def update_subtask(
        self,
        goal_id: str,
        task_id: str,
        status: Optional[SubTaskStatus] = None,
        result: Optional[dict] = None,
        confidence: Optional[float] = None,
        error: Optional[str] = None,
    ) -> Optional[ComplianceGoal]:
        """Mettre à jour une sous-tâche."""
        goal = self._goals.get(goal_id)
        if not goal:
            return None

        for st in goal.subtasks:
            if st.task_id == task_id:
                if status:
                    resolved = SubTaskStatus(status) if isinstance(status, str) else status
                    st.status = resolved
                    if resolved == SubTaskStatus.RUNNING:
                        st.started_at = datetime.now(timezone.utc)
                    elif resolved in (SubTaskStatus.DONE, SubTaskStatus.FAILED):
                        st.completed_at = datetime.now(timezone.utc)
                if result:
                    st.result = result
                if confidence is not None:
                    st.confidence = confidence
                if error:
                    st.error = error
                break

        # Recalculer la progression
        total = len(goal.subtasks)
        done = sum(1 for st in goal.subtasks if st.status == SubTaskStatus.DONE)
        goal.progress = done / total if total > 0 else 0.0

        # Vérifier si le goal est complété
        if all(
            (st.status == SubTaskStatus.DONE if isinstance(st.status, SubTaskStatus) else st.status == "done")
            for st in goal.subtasks
        ):
            goal.status = GoalStatus.COMPLETED
            goal.completed_at = datetime.now(timezone.utc)
            goal.result = self._compile_result(goal)

            journal.append(
                event_type=JournalEventType.COMPLIANCE_CHECK,
                client_id=goal.client_id,
                vertical=goal.vertical,
                agent_source="compliance_goal",
                intention_id=goal_id,
                payload={
                    "event": "goal_completed",
                    "progress": 1.0,
                    "subtask_count": total,
                },
            )
        elif any(
            (st.status == SubTaskStatus.FAILED if isinstance(st.status, SubTaskStatus) else st.status == "failed")
            for st in goal.subtasks
        ):
            # Ne pas marquer FAILED tant qu'il y a encore des tâches en cours
            def _is_pending_or_running(st):
                s = st.status
                if isinstance(s, str):
                    return s in ("pending", "running")
                return s in (SubTaskStatus.PENDING, SubTaskStatus.RUNNING)
            pending_or_running = any(_is_pending_or_running(st) for st in goal.subtasks)
            if not pending_or_running:
                goal.status = GoalStatus.FAILED
                goal.completed_at = datetime.now(timezone.utc)

        journal.append(
            event_type=JournalEventType.COMPLIANCE_CHECK,
            client_id=goal.client_id,
            vertical=goal.vertical,
            agent_source="compliance_goal",
            intention_id=goal_id,
            payload={
                "event": "subtask_updated",
                "task_id": task_id,
                "status": status.value if hasattr(status, 'value') else status,
                "progress": goal.progress,
            },
        )

        return goal

    def pause_goal(self, goal_id: str, reason: str = "") -> Optional[ComplianceGoal]:
        """Suspendre un goal (gel par le Médiateur)."""
        goal = self._goals.get(goal_id)
        if not goal or goal.status != GoalStatus.RUNNING:
            return None

        goal.status = GoalStatus.PAUSED

        # Bloquer les sous-tâches en cours
        for st in goal.subtasks:
            if st.status == SubTaskStatus.RUNNING:
                st.status = SubTaskStatus.BLOCKED

        journal.append(
            event_type=JournalEventType.COMPLIANCE_CHECK,
            client_id=goal.client_id,
            vertical=goal.vertical,
            agent_source="compliance_goal",
            intention_id=goal_id,
            payload={"event": "goal_paused", "reason": reason},
        )
        return goal

    def resume_goal(self, goal_id: str) -> Optional[ComplianceGoal]:
        """Reprendre un goal suspendu."""
        goal = self._goals.get(goal_id)
        if not goal or goal.status != GoalStatus.PAUSED:
            return None

        goal.status = GoalStatus.RUNNING

        for st in goal.subtasks:
            if st.status == SubTaskStatus.BLOCKED:
                st.status = SubTaskStatus.PENDING

        journal.append(
            event_type=JournalEventType.COMPLIANCE_CHECK,
            client_id=goal.client_id,
            vertical=goal.vertical,
            agent_source="compliance_goal",
            intention_id=goal_id,
            payload={"event": "goal_resumed"},
        )
        return goal

    def get_goal(self, goal_id: str) -> Optional[ComplianceGoal]:
        return self._goals.get(goal_id)

    def get_goals_for_client(self, client_id: str) -> list[ComplianceGoal]:
        return [g for g in self._goals.values() if g.client_id == client_id]

    def get_active_goals(self) -> list[ComplianceGoal]:
        return [
            g for g in self._goals.values()
            if g.status in (GoalStatus.PENDING, GoalStatus.RUNNING, GoalStatus.PAUSED)
        ]

    def get_templates(self, vertical: Optional[str] = None) -> dict:
        if vertical:
            return {vertical: GOAL_TEMPLATES.get(vertical, [])}
        return GOAL_TEMPLATES

    def _compile_result(self, goal: ComplianceGoal) -> dict:
        """Compiler le résultat final d'un goal complété."""
        return {
            "goal_id": goal.goal_id,
            "title": goal.title,
            "vertical": goal.vertical,
            "status": "completed",
            "progress": 1.0,
            "subtasks": [
                {
                    "name": st.name,
                    "status": st.status.value if hasattr(st.status, 'value') else str(st.status),
                    "confidence": st.confidence,
                    "result": st.result,
                    "regulatory_refs": st.regulatory_refs,
                }
                for st in goal.subtasks
            ],
            "started_at": goal.started_at.isoformat() if goal.started_at else None,
            "completed_at": goal.completed_at.isoformat() if goal.completed_at else None,
            "total_subtasks": len(goal.subtasks),
            "integrity": "WORM_journalized",
        }


# Singleton
compliance_goal_runner = ComplianceGoalRunner()
