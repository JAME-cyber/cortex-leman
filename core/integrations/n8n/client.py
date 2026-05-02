"""
Cortex Leman v5 — Intégration n8n

Client pour interagir avec les workflows n8n:
- Déclencher des workflows
- Surveiller les exécutions
- Webhook receiver pour callbacks
- Intégration avec l'Agent Action (Saga pattern)
"""
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

from core.config import settings
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)


class N8NConfig:
    """Configuration n8n"""
    base_url: str = "http://localhost:5678"
    api_key: str = ""
    webhook_base: str = "http://localhost:5678/webhook"

    @classmethod
    def from_env(cls):
        import os
        cls.base_url = os.getenv("N8N_BASE_URL", cls.base_url)
        cls.api_key = os.getenv("N8N_API_KEY", "")
        cls.webhook_base = os.getenv("N8N_WEBHOOK_BASE", cls.webhook_base)


# Workflows prédéfinis par verticale
VERTICAL_WORKFLOWS = {
    "comptable": {
        "cloture_annuelle": {
            "name": "Clôture annuelle comptable",
            "description": "Workflow de clôture avec validation expert",
            "steps": ["collect_documents", "reconcile", "generate_bilan", "expert_review", "archive"],
        },
        "tva_monthly": {
            "name": "Déclaration TVA mensuelle",
            "description": "Collecte et déclaration TVA",
            "steps": ["collect_invoices", "calculate_tva", "generate_declaration", "expert_validate"],
        },
    },
    "avocat": {
        "dossier_management": {
            "name": "Gestion dossier client",
            "description": "Workflow de gestion sécurisé (Art. 321 CP)",
            "steps": ["create_dossier", "assign_counsel", "track_deadlines", "generate_conclusions"],
        },
        "audience_preparation": {
            "name": "Préparation audience",
            "description": "Préparation documents et rappels",
            "steps": ["load_case", "prepare_documents", "set_reminders", "notify_counsel"],
        },
    },
    "rh": {
        "onboarding": {
            "name": "Onboarding employé",
            "description": "Processus d'intégration (RGPD compliant)",
            "steps": ["collect_data", "create_accounts", "assign_training", "gdpr_consent"],
        },
        "payroll": {
            "name": "Traitement paie",
            "description": "Workflow paie mensuel",
            "steps": ["collect_timesheets", "calculate_pay", "generate_payslips", "expert_validate"],
        },
    },
    "banque": {
        "kyc_compliance": {
            "name": "KYC Compliance",
            "description": "Vérification KYC client (Art. 47 LB)",
            "steps": ["collect_documents", "verify_identity", "risk_assessment", "compliance_review"],
        },
    },
    "sante": {
        "patient_intake": {
            "name": "Admission patient",
            "description": "Workflow admission (LPM/HDS)",
            "steps": ["collect_consent", "create_dossier", "assign_team", "schedule_care"],
        },
    },
    "startup": {
        "gdpr_audit": {
            "name": "Audit RGPD startup",
            "description": "Audit de conformité RGPD",
            "steps": ["scan_data", "map_processing", "assess_risks", "generate_report"],
        },
    },
}


class N8NClient:
    """
    Client n8n pour Cortex Leman v5.
    
    Utilise les webhooks n8n pour déclencher des workflows.
    L'API n8n est utilisée pour le monitoring.
    """

    def __init__(self):
        N8NConfig.from_env()
        self._base_url = N8NConfig.base_url
        self._api_key = N8NConfig.api_key
        self._webhook_base = N8NConfig.webhook_base

    async def trigger_workflow(
        self,
        workflow_name: str,
        data: dict,
        vertical: str = "unknown",
        client_id: str = "unknown",
        intention_id: str = "unknown",
        wait_for_result: bool = False,
        timeout: int = 300,
    ) -> dict:
        """
        Déclencher un workflow n8n via webhook.
        
        Args:
            workflow_name: Nom du workflow (ex: "cloture_annuelle")
            data: Données à passer au workflow
            vertical: Verticale métier
            client_id: ID client
            intention_id: ID intention
            wait_for_result: Attendre le résultat (synchrone)
            timeout: Timeout en secondes
        
        Returns:
            Résultat du workflow
        """
        webhook_url = f"{self._webhook_base}/{vertical}/{workflow_name}"

        payload = {
            "cortex_leman": {
                "version": "5.0.0",
                "intention_id": intention_id,
                "client_id": client_id,
                "vertical": vertical,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            **data,
        }

        # Journaliser le déclenchement
        journal.append(
            event_type=JournalEventType.ACTION_EXECUTED,
            client_id=client_id,
            vertical=vertical,
            agent_source="n8n",
            intention_id=intention_id,
            payload={
                "workflow": workflow_name,
                "action": "trigger",
                "webhook_url": webhook_url,
            },
        )

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if wait_for_result:
                    response = await client.post(webhook_url, json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Workflow {workflow_name} terminé avec succès")
                        return {"status": "completed", "result": result}
                    else:
                        return {"status": "error", "code": response.status_code}
                else:
                    response = await client.post(webhook_url, json=payload)
                    return {"status": "triggered", "webhook_url": webhook_url}

        except httpx.ConnectError:
            logger.warning(f"n8n non disponible — workflow {workflow_name} mis en file d'attente")
            return {"status": "queued", "reason": "n8n_unavailable"}
        except httpx.TimeoutException:
            logger.warning(f"n8n timeout — workflow {workflow_name}")
            return {"status": "timeout", "workflow": workflow_name}
        except Exception as e:
            logger.error(f"Erreur n8n: {e}")
            return {"status": "error", "error": str(e)}

    async def get_workflow_status(self, execution_id: str) -> dict:
        """Récupérer le statut d'une exécution"""
        headers = {}
        if self._api_key:
            headers["X-N8N-API-KEY"] = self._api_key

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self._base_url}/api/v1/executions/{execution_id}",
                    headers=headers,
                )
                if response.status_code == 200:
                    return response.json()
                return {"status": "unknown", "execution_id": execution_id}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

    def get_available_workflows(self, vertical: str = None) -> dict:
        """Lister les workflows disponibles par verticale"""
        if vertical:
            return {vertical: VERTICAL_WORKFLOWS.get(vertical, {})}
        return VERTICAL_WORKFLOWS

    async def health_check(self) -> dict:
        """Vérifier que n8n est disponible"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self._base_url}/healthz")
                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": self._base_url,
                }
        except Exception:
            return {"status": "unreachable", "url": self._base_url}


# Singleton
n8n_client = N8NClient()
