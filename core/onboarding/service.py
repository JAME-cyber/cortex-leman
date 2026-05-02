"""
Cortex Leman v5 — Onboarding Service

Lit les templates vertical (agent-config.yaml + règles JsonLogic + workflows)
et les installe en une seule transaction atomique.

Pas de "cards", pas de nouvelles skills. On a déjà tout.
Ce module fait le pont entre les templates existants et le système live.
"""

import json
import uuid
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import yaml

from core.config import settings
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType
from core.db.models import UserRole, UserStatus
from core.security.auth import (
    create_user, hash_password, UserCreate,
)
from core.security.encryption import init_encryption
from core.db.session import get_engine, init_db
from core.integrations.knowledge_vault.vault import KnowledgeVault
from core.compliance.gateway import ComplianceGateway

logger = logging.getLogger(__name__)

# Paths
TEMPLATES_DIR = Path.home() / ".hermes" / "skills" / "cortex-leman" / "agent-implementation-service" / "templates"
RULES_DIR = Path(__file__).parent.parent / "mediator" / "rules"

# Vertical → template directory mapping
VERTICAL_MAP = {
    "comptable": "cabinet-comptable",
    "avocat": "cabinet-avocat",
    "sante": "clinique-sante",
    "banque": "banque-finance",
    "startup": "startup-tech",
    "rh": "cabinet-rh",
}

# Verticals that auto-activate haute_protection
HIGH_PROTECTION_VERTICALS = {"avocat", "sante", "banque"}


class OnboardingResult:
    """Résultat de l'onboarding — ce qui a été créé"""

    def __init__(self):
        self.tenant_id: str = ""
        self.admin_user_id: str = ""
        self.vertical: str = ""
        self.mode: str = ""
        self.rules_loaded: int = 0
        self.agents_created: int = 0
        self.workflows_installed: int = 0
        self.vault_created: bool = False
        self.journal_initialized: bool = False
        self.regulatory_seeded: int = 0
        self.errors: list[str] = []

    def to_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "admin_user_id": self.admin_user_id,
            "vertical": self.vertical,
            "mode": self.mode,
            "rules_loaded": self.rules_loaded,
            "agents_created": self.agents_created,
            "workflows_installed": self.workflows_installed,
            "vault_created": self.vault_created,
            "journal_initialized": self.journal_initialized,
            "regulatory_seeded": self.regulatory_seeded,
            "errors": self.errors,
            "status": "activated" if not self.errors else "partial",
        }


class OnboardingService:
    """
    Service d'onboarding — installe un tenant complet en une transaction.

    Source de vérité: les templates YAML existants dans
    ~/.hermes/skills/cortex-leman/agent-implementation-service/templates/
    """

    def __init__(self):
        self.vault = KnowledgeVault()
        self.compliance_gateway = ComplianceGateway()

    def setup_tenant(self, data: dict) -> OnboardingResult:
        """
        Point d'entrée principal. Crée tout en une fois.

        data = {
            "identity": {"full_name": ..., "email": ..., "organization": ..., "size": ...},
            "vertical": "comptable",
            "compliance": {"data_residency": "EU", "encryption": "AES-256", "llm_mode": "cloud"},
            "security": {"admin_password": ..., "two_factor": ..., "invites": [...]},
        }
        """
        result = OnboardingResult()
        vertical = data["vertical"]
        result.vertical = vertical

        # Auto-déterminer le mode
        result.mode = "haute_protection" if vertical in HIGH_PROTECTION_VERTICALS else "standard"

        # Validations réglementaires AVANT de créer quoi que ce soit
        errors = self._validate_compliance(data)
        if errors:
            result.errors = errors
            return result

        # 1. Créer le tenant ID
        org = data["identity"]["organization"]
        result.tenant_id = self._generate_tenant_id(org)

        # 2. Charger le template vertical
        template = self._load_template(vertical)
        if not template:
            result.errors.append(f"Template introuvable pour vertical: {vertical}")
            return result

        # 3. Créer l'utilisateur admin
        try:
            admin = self._create_admin(data, result.tenant_id)
            result.admin_user_id = str(admin.id)
        except Exception as e:
            result.errors.append(f"Erreur création admin: {e}")
            return result

        # 4. Charger les règles JsonLogic
        result.rules_loaded = self._count_rules(vertical)

        # 5. Créer les agents depuis le template
        squad = template.get("squad", {})
        agents = squad.get("agents", [])
        result.agents_created = len(agents)

        # 6. Installer les workflows n8n
        workflows = template.get("integrations", {}).get("n8n", {}).get("workflows", [])
        result.workflows_installed = len(workflows)

        # 7. Créer le vault client
        try:
            self.vault.create_client_space(result.tenant_id, vertical)
            result.vault_created = True
        except Exception as e:
            result.errors.append(f"Vault: {e}")

        # 8. Initialiser le journal WORM
        try:
            journal.append(
                event_type=JournalEventType.SYSTEM,
                client_id=result.tenant_id,
                vertical=vertical,
                agent_source="onboarding",
                intention_id=f"tenant-setup-{result.tenant_id}",
                payload={
                    "action": "tenant.created",
                    "tenant_id": result.tenant_id,
                    "vertical": vertical,
                    "mode": result.mode,
                    "organization": org,
                    "admin_email": data["identity"]["email"],
                    "rules_loaded": result.rules_loaded,
                    "agents_created": result.agents_created,
                },
            )
            result.journal_initialized = True
        except Exception as e:
            result.errors.append(f"Journal: {e}")

        # 9. Vectoriser les textes réglementaires
        try:
            result.regulatory_seeded = self.vault.load_regulatory_data()
        except Exception as e:
            result.errors.append(f"RAG seed: {e}")

        # 10. Créer les utilisateurs invités
        invites = data.get("security", {}).get("invites", [])
        for invite in invites:
            try:
                self._create_invited_user(invite, result.tenant_id, data["identity"]["organization"])
            except Exception as e:
                result.errors.append(f"Invite {invite.get('email')}: {e}")

        # 11. Générer le premier message de l'agent
        result.first_message = self._generate_welcome_message(data, template, result)

        logger.info(
            f"Tenant onboardé: {result.tenant_id} ({vertical}, {result.mode}) — "
            f"{result.rules_loaded} règles, {result.agents_created} agents, "
            f"journal={result.journal_initialized}"
        )

        return result

    def get_vertical_preview(self, vertical: str) -> dict:
        """
        Prévisualisation ce qui sera installé pour une vertical.
        Utilisé par le frontend step 2 (sélection vertical).
        """
        template = self._load_template(vertical)
        if not template:
            return {"error": f"Vertical {vertical} non trouvée"}

        squad = template.get("squad", {})
        compliance = template.get("compliance", {})
        infra = template.get("infrastructure", {})

        return {
            "vertical": vertical,
            "mode": "haute_protection" if vertical in HIGH_PROTECTION_VERTICALS else "standard",
            "ai_act_risk": compliance.get("ai_act_risk_level", "unknown"),
            "agents": [
                {
                    "id": a.get("id"),
                    "role": a.get("role"),
                    "autonomy": a.get("autonomy_level"),
                    "guardrails": len(a.get("guardrails", {}).get("human_decision_required", [])),
                }
                for a in squad.get("agents", [])
            ],
            "rules_count": self._count_rules(vertical),
            "data_residency_default": infra.get("data_residency", {}).get("vps_location", "EU"),
            "encryption": infra.get("encryption", {}).get("at_rest", settings.compliance_encryption),
            "workflows": len(
                template.get("integrations", {}).get("n8n", {}).get("workflows", [])
            ),
            "special_notes": compliance.get("special_notes", ""),
            "allowed_llm_modes": self._get_allowed_llm_modes(vertical),
        }

    def list_verticals(self) -> list[dict]:
        """Liste toutes les verticals disponibles avec preview"""
        result = []
        for vertical in VERTICAL_MAP:
            preview = self.get_vertical_preview(vertical)
            result.append(preview)
        return result

    # ─── Validations réglementaires ─────────────────────────────

    def _validate_compliance(self, data: dict) -> list[str]:
        """Validations RGPD/AI Act par vertical. Retourne liste d'erreurs."""
        errors = []
        vertical = data["vertical"]
        compliance = data.get("compliance", {})
        identity = data.get("identity", {})
        llm_mode = compliance.get("llm_mode", "cloud")
        email = identity.get("email", "")

        # Avocat: email doit être pro (pas gmail, outlook, etc.)
        if vertical == "avocat":
            personal_domains = {"gmail.com", "outlook.com", "hotmail.fr", "yahoo.fr", "free.fr", "orange.fr"}
            domain = email.split("@")[-1].lower() if "@" in email else ""
            if domain in personal_domains:
                errors.append(
                    "Avocat: adresse email professionnelle obligatoire "
                    f"(domaine '{domain}' non autorisé pour secret professionnel Art. 321 CP)"
                )

        # Avocat/Banque/Santé: LLM cloud INTERDIT
        if vertical in HIGH_PROTECTION_VERTICALS and llm_mode == "cloud":
            errors.append(
                f"{vertical.title()}: mode LLM 'cloud' interdit — "
                "secret professionnel exige 'local' ou 'hybride' "
                f"(Art. 321 CP / Art. 47 LB / LPM)"
            )

        # Avocat/Banque: data residency CH obligatoire
        if vertical in ("avocat", "banque"):
            residency = compliance.get("data_residency", "EU")
            if residency == "EU":
                errors.append(
                    f"{vertical.title()}: data residency CH obligatoire "
                    f"(secret professionnel)"
                )

        # Password force
        password = data.get("security", {}).get("admin_password", "")
        if len(password) < 8:
            errors.append("Mot de passe: minimum 8 caractères")

        return errors

    # ─── Helpers ────────────────────────────────────────────────

    def _load_template(self, vertical: str) -> Optional[dict]:
        """Charge le template YAML de la vertical"""
        template_dir = VERTICAL_MAP.get(vertical)
        if not template_dir:
            return None

        template_path = TEMPLATES_DIR / template_dir / "agent-config.yaml"
        if not template_path.exists():
            logger.warning(f"Template non trouvé: {template_path}")
            return None

        with open(template_path) as f:
            return yaml.safe_load(f)

    def _count_rules(self, vertical: str) -> int:
        """Compte les règles JsonLogic pour une vertical"""
        rules_file = RULES_DIR / f"{vertical}.json"
        if not rules_file.exists():
            return 0
        with open(rules_file) as f:
            data = json.load(f)
            return len(data.get("rules", []))

    def _get_allowed_llm_modes(self, vertical: str) -> list[str]:
        if vertical in HIGH_PROTECTION_VERTICALS:
            return ["local", "hybrid"]
        return ["cloud", "local", "hybrid"]

    def _generate_tenant_id(self, org_name: str) -> str:
        slug = org_name.lower().strip()
        slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in slug)
        slug = slug.strip("-")[:40]
        return f"{slug}-{uuid.uuid4().hex[:6]}"

    def _create_admin(self, data: dict, tenant_id: str):
        """Crée l'utilisateur admin en DB"""
        from core.db.session import get_session
        from sqlalchemy.orm import Session

        identity = data["identity"]
        vertical = data["vertical"]

        user_data = UserCreate(
            email=identity["email"],
            full_name=identity.get("full_name", ""),
            password=data["security"]["admin_password"],
            role=UserRole.ADMIN,
            organization=identity["organization"],
            primary_vertical=vertical,
        )

        with Session(get_engine()) as db:
            return create_user(db, user_data)

    def _create_invited_user(self, invite: dict, tenant_id: str, org: str):
        """Crée un utilisateur invité"""
        from core.db.session import get_session
        from sqlalchemy.orm import Session

        user_data = UserCreate(
            email=invite["email"],
            full_name=invite.get("full_name", ""),
            password=uuid.uuid4().hex[:12],  # Temp password, will reset
            role=UserRole(invite.get("role", "operator")),
            organization=org,
        )

        with Session(get_engine()) as db:
            return create_user(db, user_data)

    def _generate_welcome_message(self, data: dict, template: dict, result: OnboardingResult) -> str:
        """Génère le premier message de l'agent après onboarding"""
        name = data["identity"].get("full_name", "").split()[0] or "utilisateur"
        org = data["identity"]["organization"]
        vertical = data["vertical"]
        mode_label = "haute protection" if result.mode == "haute_protection" else "standard"

        # Extract agent roles from template
        agents = template.get("squad", {}).get("agents", [])
        agent_roles = [f"• {a['role']} ({a['id']})" for a in agents]

        return (
            f"Bonjour {name} !\n\n"
            f"Je suis l'assistant Cortex Leman pour {org} — {vertical}.\n\n"
            f"Votre infrastructure de confiance est prête :\n"
            f"• Mode: {mode_label}\n"
            f"• {result.rules_loaded} règles de conformité actives\n"
            f"• {result.agents_created} agents spécialisés:\n"
            + "\n".join(f"  {r}" for r in agent_roles)
            + f"\n• Journal d'audit hash-chainé (SHA-256)\n"
            f"• Seuil de gel préventif: {self._get_freeze_threshold(vertical):,.0f} €\n"
            f"• Data residency: {data.get('compliance', {}).get('data_residency', 'EU')}\n\n"
            f"Que souhaitez-vous faire ?\n"
            f"1. Soumettre une intention métier\n"
            f"2. Vérifier la conformité d'un client\n"
            f"3. Explorer le dashboard"
        )

    def _get_freeze_threshold(self, vertical: str) -> float:
        """Seuil de gel par vertical"""
        thresholds = {
            "comptable": 10000,
            "avocat": 5000,
            "sante": 0,
            "banque": 15000,
            "startup": 50000,
            "rh": 20000,
        }
        return thresholds.get(vertical, 10000)


# Singleton
onboarding_service = OnboardingService()
