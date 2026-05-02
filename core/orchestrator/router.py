"""
Cortex Leman v5 — Routeur dynamique d'agents

Détermine quels agents doivent traiter une intention
en fonction de la verticale, du contenu et des règles métier.
"""
import re
import logging
from typing import Optional

from core.journal.models import IntentionModel

logger = logging.getLogger(__name__)


# Patterns de routage par type de demande
ROUTING_PATTERNS = {
    "data": [
        r"(?:cherche|trouve|scan|analyse|récupère|données|data|document)",
        r"(?:quelle|quels|quelques|lister|recenser)",
        # Fiscalité / comptabilité : déduire implique chercher les données
        r"(?:dédui[rts]|déduction|fiscal|impôt|tva|charges?|provision)",
        # Recherche de sources / circulares / référentiels
        r"(?:circulaire|référentiel|disposition|législation|statut)",
    ],
    "reasoning": [
        r"(?:compare|analyser|évalue|recommande|conseil|avis)",
        r"(?:meilleur|pire|avantage|inconvénient|risque)",
        r"(?:conform|rgpd|ai.act|audit|légal|réglement)",
        # Optimisation / détermination / calculs
        r"(?:optimis|détermin|calcul|éligib|seuil|plafond)",
    ],
    "action": [
        r"(?:exécute|lance|déclenche|envoie|paie|facture)",
        r"(?:crée|génère|produis|workflow|automatise)",
        # Écritures comptables, provisions, paiements
        r"(?:écriture|provision|virement|saisir|enregistr)",
    ],
    "supervisor": [
        r"(?:valide|vérifie|confirme|approuve|signe)",
        r"(?:rapport|bilan|synthèse|résumé)",
    ],
}


class AgentTeam:
    """Équipe d'agents assemblée dynamiquement (inspiré CaptainAgent AG2)"""
    def __init__(self, team_id: str, agents: list[str], lead: str, reason: str):
        self.team_id = team_id
        self.agents = agents
        self.lead = lead        # Agent principal
        self.reason = reason    # Pourquoi cette équipe

    def to_dict(self) -> dict:
        return {
            "team_id": self.team_id,
            "agents": self.agents,
            "lead": self.lead,
            "reason": self.reason,
        }


class AgentRouter:
    """Routeur dynamique vers les agents spécialisés — avec CaptainAgent team assembly"""

    def __init__(self):
        self._vertical_overrides: dict[str, dict] = {}

    def route(self, intention: IntentionModel) -> dict[str, bool]:
        """
        Déterminer quels agents doivent être activés pour cette intention.
        
        Returns:
            dict mapping agent_name -> should_activate
        """
        query = (intention.refined_query or intention.original_query).lower()
        agents = {
            "data": False,
            "reasoning": False,
            "action": False,
            "supervisor": True,  # Toujours actif
            "mediator": True,    # Toujours actif (transverse)
        }

        for agent_name, patterns in ROUTING_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    agents[agent_name] = True
                    break

        # Si aucun agent spécifique activé, activer data + reasoning par défaut
        if not any(agents[k] for k in ["data", "reasoning", "action"]):
            agents["data"] = True
            agents["reasoning"] = True

        # Overrides par verticale
        vertical = intention.vertical
        if vertical in self._vertical_overrides:
            for agent, override in self._vertical_overrides[vertical].items():
                agents[agent] = override

        logger.info(
            f"Routage intention {intention.intention_id[:8]}... → "
            f"{[k for k, v in agents.items() if v]}"
        )
        return agents

    def add_vertical_override(self, vertical: str, agent: str, activate: bool) -> None:
        """Ajouter un override de routage pour une verticale"""
        if vertical not in self._vertical_overrides:
            self._vertical_overrides[vertical] = {}
        self._vertical_overrides[vertical][agent] = activate

    # ── Insight 3: CaptainAgent — Team Assembly ──────────────────────

    def assemble_team(self, intention: 'IntentionModel') -> AgentTeam:
        """
        Assembler dynamiquement une équipe d'agents (CaptainAgent pattern).

        Contrairement à route() qui active/désactive individuellement,
        assemble_team() crée une équipe cohérente avec un lead et un reason.

        Règles d'assemblage:
        - Médiateur TOUJOURS dans l'équipe (supervision)
        - Superviseur TOUJOURS dans l'équipe (monitoring)
        - 1-3 agents métier selon la complexité
        - 1 lead désigné selon le type de tâche
        """
        import uuid
        query = (intention.refined_query or intention.original_query).lower()
        vertical = intention.vertical

        # Agents de base (toujours présents)
        team_agents = ["mediator", "supervisor"]
        lead = "reasoning"  # par défaut
        reason_parts = []

        # Détecter la complexité de la requête
        activated = self.route(intention)

        if activated.get("data"):
            team_agents.append("data")
            reason_parts.append("recherche données")

        if activated.get("reasoning"):
            team_agents.append("reasoning")
            reason_parts.append("analyse/conformité")
            lead = "reasoning"

        if activated.get("action"):
            team_agents.append("action")
            reason_parts.append("exécution transactionnelle")
            lead = "action"  # Action prend le lead si présent

        # Règles par verticale
        vertical_teams = {
            "comptable": {
                "default_lead": "reasoning",
                "always": ["data"],  # Comptable a toujours besoin de données
                "high_value_keywords": ["bilan", "audit", "fiscal", "tva", "charges"],
            },
            "avocat": {
                "default_lead": "reasoning",
                "always": ["data"],
                "high_value_keywords": ["contrat", "litige", "conformité", "secret"],
            },
            "sante": {
                "default_lead": "reasoning",
                "always": ["data"],
                "high_value_keywords": ["patient", "consentement", "données médicales"],
            },
            "banque": {
                "default_lead": "reasoning",
                "always": ["data"],
                "high_value_keywords": ["kyc", "aml", "conformité", "crédit"],
            },
            "startup": {
                "default_lead": "reasoning",
                "always": [],
                "high_value_keywords": ["ia", "rgpd", "ai act", "dpia"],
            },
            "rh": {
                "default_lead": "reasoning",
                "always": ["data"],
                "high_value_keywords": ["recrutement", "discrimination", "paie"],
            },
        }

        vt = vertical_teams.get(vertical, {})

        # Ajouter les agents obligatoires par vertical
        for agent in vt.get("always", []):
            if agent not in team_agents:
                team_agents.append(agent)
                reason_parts.append(f"obligatoire vertical {vertical}")

        # Détecter haute complexité
        hv_keywords = vt.get("high_value_keywords", [])
        is_complex = any(kw in query for kw in hv_keywords)
        if is_complex:
            # Haute complexité: ajouter reasoning si pas déjà là
            if "reasoning" not in team_agents:
                team_agents.append("reasoning")
            reason_parts.append("complexité élevée détectée")

        lead = vt.get("default_lead", lead)
        # Action override si présent
        if "action" in team_agents:
            lead = "action"

        reason = "Équipe assemblée: " + ", ".join(reason_parts) if reason_parts else "Équipe standard"

        team = AgentTeam(
            team_id=str(uuid.uuid4())[:8],
            agents=team_agents,
            lead=lead,
            reason=reason,
        )

        logger.info(
            f"CaptainAgent team '{team.team_id}' assemblée: "
            f"agents={team.agents}, lead={team.lead} ({team.reason})"
        )

        return team


# Singleton
router = AgentRouter()
