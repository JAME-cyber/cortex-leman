"""
Cortex Leman v5 — Agent Identity Cards (KYA Régulé)

Chaque agent Cortex Leman a une carte d'identité signée avec:
- Agent ID unique et immuable
- Permissions déléguées (scope par verticale)
- Serment numérique signé à chaque activation de session
- Audit trail de TOUTES ses actions

Inspiré de:
- «Know Your Agent» (discussion Romain Huet / La French)
- OAuth pour agents (Aaron Pariki, mainteneur OAuth)
- Notre concept de Serment Numérique (PENSEE-DIVERGENTE.md)

Cela positionne Cortex Leman comme le premier KYA pour professions régulées.
"""
import hashlib
import hmac
import uuid
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from core.config import settings
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)


# ── Permission Scopes ─────────────────────────────────────────

class AgentScope(str, Enum):
    """Permissions déléguées pour un agent."""
    # Lecture
    DATA_READ = "data.read"
    JOURNAL_READ = "journal.read"
    KNOWLEDGE_READ = "knowledge.read"
    REGULATIONS_READ = "regulations.read"

    # Écriture (contrôlée)
    DATA_WRITE = "data.write"
    REASONING_WRITE = "reasoning.write"
    COMPLIANCE_WRITE = "compliance.write"

    # Actions sensibles
    ACTION_EXECUTE = "action.execute"
    ACTION_COMPENSATE = "action.compensate"

    # Médiation
    MEDIATOR_EVALUATE = "mediator.evaluate"
    MEDIATOR_FREEZE = "mediator.freeze"
    MEDIATOR_UNFREEZE = "mediator.unfreeze"

    # Arbitrage
    ARBITRATION_REQUEST = "arbitration.request"
    ARBITRATION_DECIDE = "arbitration.decide"

    # Journal
    JOURNAL_APPEND = "journal.append"
    JOURNAL_VERIFY = "journal.verify"

    # Admin
    SYSTEM_HEALTH = "system.health"
    REFLECTION_TOGGLE = "reflection.toggle"


# Scopes par défaut par rôle d'agent
AGENT_DEFAULT_SCOPES: dict[str, list[AgentScope]] = {
    "data": [
        AgentScope.DATA_READ,
        AgentScope.DATA_WRITE,
        AgentScope.KNOWLEDGE_READ,
        AgentScope.REGULATIONS_READ,
        AgentScope.JOURNAL_APPEND,
    ],
    "reasoning": [
        AgentScope.DATA_READ,
        AgentScope.KNOWLEDGE_READ,
        AgentScope.REGULATIONS_READ,
        AgentScope.REASONING_WRITE,
        AgentScope.JOURNAL_APPEND,
    ],
    "action": [
        AgentScope.DATA_READ,
        AgentScope.ACTION_EXECUTE,
        AgentScope.ACTION_COMPENSATE,
        AgentScope.JOURNAL_APPEND,
    ],
    "supervisor": [
        AgentScope.DATA_READ,
        AgentScope.JOURNAL_READ,
        AgentScope.JOURNAL_VERIFY,
        AgentScope.SYSTEM_HEALTH,
    ],
    "mediator": [
        AgentScope.DATA_READ,
        AgentScope.MEDIATOR_EVALUATE,
        AgentScope.MEDIATOR_FREEZE,
        AgentScope.MEDIATOR_UNFREEZE,
        AgentScope.JOURNAL_APPEND,
        AgentScope.JOURNAL_READ,
    ],
    "orchestrator": [
        AgentScope.DATA_READ,
        AgentScope.DATA_WRITE,
        AgentScope.KNOWLEDGE_READ,
        AgentScope.REGULATIONS_READ,
        AgentScope.ARBITRATION_REQUEST,
        AgentScope.JOURNAL_APPEND,
        AgentScope.JOURNAL_READ,
        AgentScope.SYSTEM_HEALTH,
    ],
}


class IdentityStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"    # Suspecté de comportement anormal
    REVOKED = "revoked"        # Révoqué (ne peut plus agir)
    EXPIRED = "expired"


# ── Agent Identity Card ──────────────────────────────────────

class AgentIdentity(BaseModel):
    """
    Carte d'identité d'un agent Cortex Leman.

    Signée avec la clé du système. Immuable une fois créée.
    La session_id change à chaque activation.
    """
    agent_id: str = Field(..., description="ID unique et immuable de l'agent")
    agent_name: str
    agent_role: str  # data | reasoning | action | supervisor | mediator | orchestrator
    verticals: list[str]  # Verticales autorisées
    scopes: list[AgentScope]
    status: IdentityStatus = IdentityStatus.ACTIVE
    # Session courante
    session_id: Optional[str] = None
    session_started_at: Optional[datetime] = None
    # Serment
    oath_hash: Optional[str] = None  # Hash du serment signé pour cette session
    oath_signed_at: Optional[datetime] = None
    # Stats
    total_actions: int = 0
    total_freezes_caused: int = 0
    total_arbitrations_triggered: int = 0
    # Métadonnées
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_active_at: Optional[datetime] = None
    parent_agent_id: Optional[str] = None  # Pour les sous-agents
    delegated_from: Optional[str] = None   # Token parent (délégation de permissions)


class SessionCredential(BaseModel):
    """
    Credential temporaire pour une session d'agent.
    Signé avec HMAC-SHA256. Délégable.
    """
    credential_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    session_id: str
    scopes: list[AgentScope]
    verticals: list[str]
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    signature: str = ""
    parent_credential_id: Optional[str] = None  # Délégation


# ── Identity Provider ─────────────────────────────────────────

class AgentIdentityProvider:
    """
    Fournisseur d'identité pour les agents Cortex Leman.

    Responsable de:
    - Créer et gérer les cartes d'identité
    - Signer les sessions (serment numérique)
    - Vérifier les permissions avant chaque action
    - Journaliser les activations/désactivations
    - Gérer les délégations de permissions
    """

    # Durée de validité d'une session (secondes)
    SESSION_DURATION = 28800  # 8 heures

    def __init__(self, signing_key: Optional[str] = None):
        self._key = signing_key or settings.journal_signing_key
        self._identities: dict[str, AgentIdentity] = {}
        self._sessions: dict[str, SessionCredential] = {}  # session_id → credential
        self._init_default_agents()

    def _init_default_agents(self) -> None:
        """Initialiser les identités des agents par défaut."""
        default_agents = [
            ("agent-data", "Data Agent", "data", ["comptable", "avocat", "sante", "banque", "startup", "rh"]),
            ("agent-reasoning", "Raisonnement Agent", "reasoning", ["comptable", "avocat", "sante", "banque", "startup", "rh"]),
            ("agent-action", "Action Agent", "action", ["comptable", "avocat", "sante", "banque", "startup", "rh"]),
            ("agent-supervisor", "Superviseur V2", "supervisor", ["comptable", "avocat", "sante", "banque", "startup", "rh"]),
            ("mediator", "Médiateur", "mediator", ["comptable", "avocat", "sante", "banque", "startup", "rh"]),
            ("orchestrator", "Orchestrateur", "orchestrator", ["comptable", "avocat", "sante", "banque", "startup", "rh"]),
        ]

        for agent_id, name, role, verticals in default_agents:
            if agent_id not in self._identities:
                scopes = AGENT_DEFAULT_SCOPES.get(role, [])
                self._identities[agent_id] = AgentIdentity(
                    agent_id=agent_id,
                    agent_name=name,
                    agent_role=role,
                    verticals=verticals,
                    scopes=scopes,
                )

    # ── Session Management ───────────────────────────────

    def activate_session(
        self,
        agent_id: str,
        vertical: Optional[str] = None,
        delegated_scopes: Optional[list[AgentScope]] = None,
        parent_credential_id: Optional[str] = None,
    ) -> Optional[SessionCredential]:
        """
        Activer une session pour un agent (serment numérique).

        Signe la session avec HMAC. Le serment est inscrit dans le journal WORM.
        """
        identity = self._identities.get(agent_id)
        if not identity:
            logger.error(f"AgentIdentity: agent inconnu {agent_id}")
            return None

        if identity.status != IdentityStatus.ACTIVE:
            logger.warning(f"AgentIdentity: agent {agent_id} non actif ({identity.status.value})")
            return None

        # Vérifier la verticale
        if vertical and vertical not in identity.verticals:
            logger.warning(f"AgentIdentity: {agent_id} non autorisé pour {vertical}")
            return None

        # Déterminer les scopes pour cette session
        scopes = delegated_scopes or identity.scopes
        # Si délégation, vérifier que les scopes sont un sous-ensemble
        if parent_credential_id:
            parent_cred = self._sessions.get(parent_credential_id)
            if parent_cred:
                parent_scopes = set(parent_cred.scopes)
                requested_scopes = set(scopes)
                if not requested_scopes.issubset(parent_scopes):
                    logger.warning(
                        f"AgentIdentity: délégation refusée — "
                        f"{agent_id} demande {requested_scopes - parent_scopes} "
                        f"non inclus dans le credential parent"
                    )
                    return None

        # Créer la session
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        credential = SessionCredential(
            agent_id=agent_id,
            session_id=session_id,
            scopes=scopes,
            verticals=[vertical] if vertical else identity.verticals,
            issued_at=now,
            expires_at=datetime.fromtimestamp(now.timestamp() + self.SESSION_DURATION, tz=timezone.utc),
            parent_credential_id=parent_credential_id,
        )

        # Signer le credential
        credential.signature = self._sign_credential(credential)

        # Mettre à jour l'identité
        identity.session_id = session_id
        identity.session_started_at = now
        identity.last_active_at = now

        # Signer le serment numérique
        oath_text = self._generate_oath(identity, credential)
        identity.oath_hash = hashlib.sha256(oath_text.encode()).hexdigest()
        identity.oath_signed_at = now

        self._sessions[session_id] = credential

        # Journaliser l'activation du serment
        journal.append(
            event_type=JournalEventType.SYSTEM_START,
            client_id="system",
            vertical=vertical or "all",
            agent_source=agent_id,
            intention_id="system",
            payload={
                "event": "agent_session_activated",
                "session_id": session_id,
                "agent_role": identity.agent_role,
                "oath_hash": identity.oath_hash[:16] + "...",
                "scopes": [s.value for s in scopes],
                "verticals": credential.verticals,
                "delegated": parent_credential_id is not None,
            },
        )

        logger.info(
            f"AgentIdentity: session activée pour {agent_id} "
            f"(session={session_id[:8]}..., serment signé)"
        )
        return credential

    def deactivate_session(self, agent_id: str) -> bool:
        """Désactiver la session d'un agent."""
        identity = self._identities.get(agent_id)
        if not identity or not identity.session_id:
            return False

        session_id = identity.session_id

        journal.append(
            event_type=JournalEventType.SYSTEM,
            client_id="system",
            vertical="all",
            agent_source=agent_id,
            intention_id="system",
            payload={
                "event": "agent_session_deactivated",
                "session_id": session_id,
                "total_actions": identity.total_actions,
            },
        )

        # Nettoyer
        if session_id in self._sessions:
            del self._sessions[session_id]

        identity.session_id = None
        identity.session_started_at = None
        identity.oath_hash = None
        identity.oath_signed_at = None

        logger.info(f"AgentIdentity: session désactivée pour {agent_id}")
        return True

    # ── Permission Verification ──────────────────────────

    def verify_permission(
        self,
        agent_id: str,
        scope: AgentScope,
        vertical: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        Vérifier qu'un agent a la permission d'exécuter une action.

        Returns:
            (allowed, reason) — True si autorisé, False sinon avec la raison.
        """
        identity = self._identities.get(agent_id)
        if not identity:
            return False, f"Agent {agent_id} inconnu"

        # Vérifier le statut
        if identity.status != IdentityStatus.ACTIVE:
            return False, f"Agent {agent_id} non actif ({identity.status.value})"

        # Vérifier qu'une session est active
        if not identity.session_id:
            return False, f"Agent {agent_id} n'a pas de session active"

        # Vérifier le credential
        cred = self._sessions.get(identity.session_id)
        if not cred:
            return False, f"Pas de credential pour la session de {agent_id}"

        # Vérifier l'expiration
        if datetime.now(timezone.utc) > cred.expires_at:
            return False, f"Session expirée pour {agent_id}"

        # Vérifier le scope
        if scope not in cred.scopes:
            return False, f"Scope {scope.value} non accordé à {agent_id}"

        # Vérifier la verticale
        if vertical and vertical not in cred.verticals:
            return False, f"Verticale {vertical} non autorisée pour {agent_id}"

        # Vérifier la signature du credential
        expected_sig = self._sign_credential(cred)
        if cred.signature != expected_sig:
            return False, f"Signature credential invalide pour {agent_id}"

        # Mettre à jour l'activité
        identity.last_active_at = datetime.now(timezone.utc)
        identity.total_actions += 1

        return True, "OK"

    def verify_permission_or_raise(
        self,
        agent_id: str,
        scope: AgentScope,
        vertical: Optional[str] = None,
    ) -> None:
        """Vérifier la permission ou lever une exception."""
        allowed, reason = self.verify_permission(agent_id, scope, vertical)
        if not allowed:
            raise PermissionError(f"Agent {agent_id}: {reason}")

    # ── Delegation ───────────────────────────────────────

    def delegate_scopes(
        self,
        parent_agent_id: str,
        child_agent_id: str,
        scopes: list[AgentScope],
        vertical: str,
    ) -> Optional[SessionCredential]:
        """
        Déléguer des permissions d'un agent parent à un agent enfant.

        Le credential enfant est un sous-ensemble du credential parent.
        Comme OAuth: token parent → token enfant avec sous-permissions.
        """
        parent_identity = self._identities.get(parent_agent_id)
        if not parent_identity or not parent_identity.session_id:
            logger.error(f"Délégation: parent {parent_agent_id} non actif")
            return None

        parent_cred = self._sessions.get(parent_identity.session_id)
        if not parent_cred:
            return None

        # Vérifier que les scopes demandés sont un sous-ensemble
        parent_scopes = set(parent_cred.scopes)
        requested = set(scopes)
        if not requested.issubset(parent_scopes):
            logger.warning(
                f"Délégation refusée: {child_agent_id} demande "
                f"{requested - parent_scopes} hors scope parent"
            )
            return None

        # Créer la session enfant avec les scopes du parent pour la vérification
        child_identity = self._identities.get(child_agent_id)
        if not child_identity:
            logger.error(f"Délégation: agent enfant {child_agent_id} inconnu")
            return None

        # Temporairement mettre les scopes délégués sur l'identité enfant
        original_scopes = child_identity.scopes
        child_identity.scopes = list(requested)

        credential = self.activate_session(
            agent_id=child_agent_id,
            vertical=vertical,
            delegated_scopes=list(requested),
            parent_credential_id=parent_cred.credential_id,
        )

        # Restaurer les scopes originaux
        child_identity.scopes = original_scopes

        if credential:
            # Enregistrer la filiation
            child_identity = self._identities.get(child_agent_id)
            if child_identity:
                child_identity.parent_agent_id = parent_agent_id
                child_identity.delegated_from = parent_cred.credential_id

            journal.append(
                event_type=JournalEventType.SYSTEM,
                client_id="system",
                vertical=vertical,
                agent_source=parent_agent_id,
                intention_id="system",
                payload={
                    "event": "scope_delegation",
                    "parent_agent": parent_agent_id,
                    "child_agent": child_agent_id,
                    "delegated_scopes": [s.value for s in scopes],
                },
            )

            logger.info(
                f"AgentIdentity: délégation {parent_agent_id} → {child_agent_id} "
                f"({len(scopes)} scopes)"
            )

        return credential

    # ── Suspension / Revocation ──────────────────────────

    def suspend_agent(self, agent_id: str, reason: str) -> bool:
        """Suspendre un agent (comportement suspect détecté)."""
        identity = self._identities.get(agent_id)
        if not identity:
            return False

        identity.status = IdentityStatus.SUSPENDED
        self.deactivate_session(agent_id)

        journal.append(
            event_type=JournalEventType.SYSTEM_ERROR,
            client_id="system",
            vertical="all",
            agent_source="identity_provider",
            intention_id="system",
            payload={
                "event": "agent_suspended",
                "agent_id": agent_id,
                "reason": reason,
            },
        )

        logger.warning(f"AgentIdentity: agent {agent_id} SUSPENDU — {reason}")
        return True

    def revoke_agent(self, agent_id: str, reason: str) -> bool:
        """Révoquer définitivement un agent."""
        identity = self._identities.get(agent_id)
        if not identity:
            return False

        identity.status = IdentityStatus.REVOKED
        self.deactivate_session(agent_id)

        journal.append(
            event_type=JournalEventType.SYSTEM_ERROR,
            client_id="system",
            vertical="all",
            agent_source="identity_provider",
            intention_id="system",
            payload={
                "event": "agent_revoked",
                "agent_id": agent_id,
                "reason": reason,
            },
        )

        logger.critical(f"AgentIdentity: agent {agent_id} RÉVOQUÉ — {reason}")
        return True

    # ── Query ────────────────────────────────────────────

    def get_identity(self, agent_id: str) -> Optional[AgentIdentity]:
        return self._identities.get(agent_id)

    def get_all_identities(self) -> list[AgentIdentity]:
        return list(self._identities.values())

    def get_session(self, session_id: str) -> Optional[SessionCredential]:
        return self._sessions.get(session_id)

    def get_audit_trail(self, agent_id: str) -> dict:
        """Récupérer le résumé d'audit d'un agent."""
        identity = self._identities.get(agent_id)
        if not identity:
            return {"error": f"Agent {agent_id} inconnu"}

        return {
            "agent_id": agent_id,
            "agent_name": identity.agent_name,
            "agent_role": identity.agent_role,
            "status": identity.status.value,
            "scopes": [s.value for s in identity.scopes],
            "verticals": identity.verticals,
            "total_actions": identity.total_actions,
            "total_freezes_caused": identity.total_freezes_caused,
            "total_arbitrations_triggered": identity.total_arbitrations_triggered,
            "session_active": identity.session_id is not None,
            "session_id": identity.session_id[:8] + "..." if identity.session_id else None,
            "oath_signed": identity.oath_hash is not None,
            "oath_signed_at": identity.oath_signed_at.isoformat() if identity.oath_signed_at else None,
            "last_active_at": identity.last_active_at.isoformat() if identity.last_active_at else None,
            "created_at": identity.created_at.isoformat(),
        }

    # ── Internals ────────────────────────────────────────

    def _sign_credential(self, cred: SessionCredential) -> str:
        """Signer un credential avec HMAC-SHA256."""
        payload = f"{cred.credential_id}:{cred.agent_id}:{cred.session_id}"
        payload += ":" + ",".join(sorted(s.value for s in cred.scopes))
        payload += f":{cred.issued_at.isoformat()}"
        return hmac.new(
            self._key.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

    def _generate_oath(self, identity: AgentIdentity, cred: SessionCredential) -> str:
        """Générer le texte du serment numérique pour cette session."""
        role_oaths = {
            "data": "Je certifie accéder uniquement aux données autorisées et respecter la confidentialité.",
            "reasoning": "Je certifie analyser avec objectivité et signaler toute incohérence détectée.",
            "action": "Je certifie vérifier le gel avant chaque exécution et compenser en cas d'échec.",
            "supervisor": "Je certifie observer sans interférer et préparer des dossiers d'arbitrage complets.",
            "mediator": "Je certifie appliquer les règles de manière déterministe, sans LLM, et geler lorsque la prudence l'exige.",
            "orchestrator": "Je certifie router les intentions vers les agents appropriés et respecter le cycle de vie.",
        }
        oath = role_oaths.get(identity.agent_role, "Je certifie agir dans le cadre de mes permissions.")
        oath += f"\nAgent: {identity.agent_name} ({identity.agent_id})"
        oath += f"\nSession: {cred.session_id}"
        oath += f"\nScopes: {', '.join(s.value for s in cred.scopes)}"
        oath += f"\nVerticales: {', '.join(cred.verticals)}"
        oath += f"\nSigné: {datetime.now(timezone.utc).isoformat()}"
        return oath


# Singleton
agent_identity_provider = AgentIdentityProvider()
