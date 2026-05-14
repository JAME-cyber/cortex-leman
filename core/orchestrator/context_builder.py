"""
Cortex Leman v5 — Context Builder (5 couches)

Construit un contexte riche pour chaque agent en combinant:
  Layer 1: System     → Rôle, capacités, limites de l'agent
  Layer 2: Vertical   → Connaissances métier (avocat, comptable, santé, immobilier, banque)
  Layer 3: Procedural → Leçons apprises par cet agent sur cette verticale
  Layer 4: Memory     → Échecs passés + vault client + RAG
  Layer 5: Task       → Contexte de la mission en cours

S'intègre avec: KnowledgeVault, RAG ChromaDB, ProceduralMemory, FailureMemory
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from core.agents.memory import procedural_memory, failure_memory

logger = logging.getLogger(__name__)


# ── VERTICAL KNOWLEDGE ────────────────────────────────────────

VERTICAL_KNOWLEDGE = {
    "avocat": {
        "name": "Avocat / Cabinet juridique",
        "key_regulations": ["Art. 321 CP (secret professionnel)", "RGPD Art. 22", "AI Act high-risk"],
        "constraints": [
            "Secret professionnel absolu (Art. 321 CP)",
            "Pas de décision automatisée sans supervision humaine",
            "Traçabilité obligatoire de toute recommandation IA",
            "Droit de contradiction par le client",
        ],
        "common_tasks": [
            "analyse_contrat", "recherche_jurisprudence", "rédaction_conclusions",
            "due_diligence", "conformité_rgpd", "audit_réglementaire",
        ],
        "risk_factors": [
            "Recommandation erronée → préjudice client",
            "Fuite de données confidentielles",
            "Absence de supervision humaine",
            "Non-respect du délai de conservation",
        ],
    },
    "comptable": {
        "name": "Expert-comptable / Cabinet comptable",
        "key_regulations": ["PCG", "IFRS", "RGPD", "Anti-blanchiment"],
        "constraints": [
            "Respect du Plan Comptable Général",
            "Obligation de déclaration de soupçon (Tracfin)",
            "Conservation des documents 10 ans",
            "Secret professionnel",
        ],
        "common_tasks": [
            "bilan_comptable", "déclaration_fiscale", "audit_comptable",
            "lettrage", "rapprochement_bancaire", "conformité_anti_blanchiment",
        ],
        "risk_factors": [
            "Erreur de calcul → redressement fiscal",
            "Non-déclaration de soupçon",
            "Perte de données comptables",
            "Non-conformité IFRS",
        ],
    },
    "immobilier": {
        "name": "Agent immobilier / Agence",
        "key_regulations": ["Loi Hoguet", "Loi ALUR", "RGPD", "SRU"],
        "constraints": [
            "Carte T obligatoire",
            "Mandat écrit obligatoire",
            "Affichage des honoraires",
            "Respect du droit à l'image des biens",
        ],
        "common_tasks": [
            "estimation_bien", "rédaction_mandat", "diffusion_annonce",
            "gestion_locative", "état_des_lieux", "diagnostics_amiante_plomb",
        ],
        "risk_factors": [
            "Estimation erronée → perte de mandat",
            "Non-respect de la Loi Hoguet",
            "Fuite de données clients",
            "Photos non conformes (droit à l'image)",
        ],
    },
    "sante": {
        "name": "Professionnel de santé",
        "key_regulations": ["Code de la Santé Publique", "RGPD Art. 9", "HDS", "Secret médical"],
        "constraints": [
            "Secret médical absolu",
            "Hébergement HDS obligatoire pour données de santé",
            "Consentement explicite pour tout traitement",
            "Pas de décision automatisée impactant le patient",
        ],
        "common_tasks": [
            "dossier_patient", "ordonnance", "compte_rendu",
            "plan_traitement", "suivi_pathologie", "téléconsultation",
        ],
        "risk_factors": [
            "Erreur de diagnostic assisté",
            "Fuite de données médicales",
            "Non-conformité HDS",
            "Absence de consentement",
        ],
    },
    "banque": {
        "name": "Établissement bancaire / FinTech",
        "key_regulations": ["Art. 47 LB", "MIFID II", "Bâle III", "Anti-blanchiment"],
        "constraints": [
            "Secret bancaire suisse (Art. 47 LB)",
            "Know Your Customer (KYC) obligatoire",
            "Déclaration de soupçon",
            "Conformité Bâle III",
        ],
        "common_tasks": [
            "kyc_onboarding", "analyse_risque", "déclaration_soupçon",
            "contrôle_conformité", "audit_interne", "reporting_régulateur",
        ],
        "risk_factors": [
            "Non-conformité KYC/AML",
            "Violation du secret bancaire",
            "Défaut de reporting régulateur",
            "Erreur d'évaluation des risques",
        ],
    },
}


# ── CONTEXT BUILDER ──────────────────────────────────────────

class ContextBuilder:
    """
    Constructeur de contexte en 5 couches.
    
    Usage:
        builder = ContextBuilder()
        context = builder.build(
            agent_name="reasoning",
            vertical="avocat",
            task="Analyser ce contrat de bail",
            client_id="client-123",
        )
        # context["system_prompt"] → prompt complet enrichi
        # context["layers"] → détail par couche
    """
    
    def build(
        self,
        agent_name: str,
        vertical: str = "",
        task: str = "",
        client_id: str = "",
        intention_id: str = "",
    ) -> dict:
        """
        Construire le contexte complet pour un agent.
        
        Returns:
            {
                "system_prompt": str,     → Prompt système complet
                "layers": {
                    "system": dict,       → Layer 1
                    "vertical": dict,     → Layer 2
                    "procedural": dict,   → Layer 3
                    "memory": dict,       → Layer 4
                    "task": dict,         → Layer 5
                },
                "warnings": list[str],    → Avertissements failure memory
                "meta": dict,             → Metadata
            }
        """
        layers = {
            "system": self._build_system_layer(agent_name),
            "vertical": self._build_vertical_layer(vertical),
            "procedural": self._build_procedural_layer(agent_name, vertical),
            "memory": self._build_memory_layer(agent_name, vertical, client_id),
            "task": self._build_task_layer(task, client_id, intention_id),
        }
        
        warnings = failure_memory.get_warnings(agent_name, vertical)
        
        system_prompt = self._compose_prompt(layers, warnings)
        
        return {
            "system_prompt": system_prompt,
            "layers": layers,
            "warnings": warnings,
            "meta": {
                "agent_name": agent_name,
                "vertical": vertical,
                "client_id": client_id,
                "built_at": datetime.now(timezone.utc).isoformat(),
                "has_procedural": bool(layers["procedural"].get("instructions")),
                "has_failures": len(warnings) > 0,
            },
        }
    
    def build_system_prompt(
        self,
        agent_name: str,
        vertical: str = "",
        task: str = "",
        client_id: str = "",
    ) -> str:
        """Raccourci: retourne juste le prompt système enrichi"""
        context = self.build(agent_name, vertical, task, client_id)
        return context["system_prompt"]
    
    # ── LAYER BUILDERS ─────────────────────────────────────
    
    def _build_system_layer(self, agent_name: str) -> dict:
        """Layer 1: Rôle et capacités de l'agent"""
        agent_roles = {
            "orchestrator": {
                "role": "Orchestrateur du système Cortex Leman",
                "capabilities": ["routage d'intention", "coordination multi-agent", "suivi de conversation"],
                "limits": ["ne produit pas d'analyse directement", "ne contredit pas le médiateur"],
            },
            "data": {
                "role": "Agent de collecte et validation des données",
                "capabilities": ["extraction de données", "validation RGPD", "enrichissement"],
                "limits": ["ne produit pas de recommandation", "ne juge pas la conformité"],
            },
            "reasoning": {
                "role": "Agent d'analyse et de raisonnement",
                "capabilities": ["analyse contextuelle", "évaluation de risques", "recommandations"],
                "limits": ["décision finale par l'expert humain", "ne peut pas garantir l'exhaustivité"],
            },
            "action": {
                "role": "Agent d'exécution et de déploiement",
                "capabilities": ["génération de documents", "déploiement de workflows", "notifications"],
                "limits": ["nécessite validation humaine pour les actions critiques"],
            },
            "supervisor": {
                "role": "Superviseur et gestionnaire de qualité",
                "capabilities": ["vérification qualité", "escalade", "coordination saga"],
                "limits": ["ne modifie pas les analyses", "ne prend pas de décision métier"],
            },
            "mediator": {
                "role": "Médiateur de confiance — garant de la conformité",
                "capabilities": ["vérification JsonLogic", "blocage non-conforme", "arbitrage humain"],
                "limits": ["ne peut pas être contourné", "décision finale = humain"],
            },
        }
        
        role = agent_roles.get(agent_name, {
            "role": f"Agent {agent_name}",
            "capabilities": ["traitement métier"],
            "limits": ["respecter les garde-fous"],
        })
        
        return role
    
    def _build_vertical_layer(self, vertical: str) -> dict:
        """Layer 2: Connaissances métier"""
        if not vertical or vertical not in VERTICAL_KNOWLEDGE:
            return {"name": vertical or "général", "note": "Pas de connaissances verticales spécifiques"}
        return VERTICAL_KNOWLEDGE[vertical]
    
    def _build_procedural_layer(self, agent_name: str, vertical: str) -> dict:
        """Layer 3: Leçons apprises"""
        instructions = procedural_memory.get_instructions(agent_name, vertical)
        if not instructions:
            return {"instructions": "", "note": "Aucune leçon encore enregistrée"}
        return {"instructions": instructions, "source": "procedural_memory"}
    
    def _build_memory_layer(self, agent_name: str, vertical: str, client_id: str) -> dict:
        """Layer 4: Échecs passés + vault"""
        failures = failure_memory.get_unresolved(agent_name, vertical)
        
        return {
            "unresolved_failures": len(failures),
            "failure_details": failures[:5],  # Top 5 les plus pertinents
            "client_id": client_id,
        }
    
    def _build_task_layer(self, task: str, client_id: str, intention_id: str) -> dict:
        """Layer 5: Contexte de la mission"""
        return {
            "task": task,
            "client_id": client_id,
            "intention_id": intention_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    # ── PROMPT COMPOSER ────────────────────────────────────
    
    def _compose_prompt(self, layers: dict, warnings: list[str]) -> str:
        """Composer le prompt système à partir des 5 couches"""
        parts = []
        
        # Layer 1: System
        system = layers["system"]
        parts.append(f"RÔLE: {system['role']}")
        parts.append(f"Capacités: {', '.join(system['capabilities'])}")
        parts.append(f"Limites: {', '.join(system['limits'])}")
        
        # Layer 2: Vertical
        vertical = layers["vertical"]
        if "constraints" in vertical:
            parts.append(f"\nVERTICALE: {vertical['name']}")
            parts.append(f"Contraintes: {'; '.join(vertical['constraints'])}")
            parts.append(f"Risques: {'; '.join(vertical.get('risk_factors', []))}")
        
        # Layer 3: Procedural
        proc = layers["procedural"]
        if proc.get("instructions"):
            parts.append(f"\nLEÇONS APPRISES:")
            parts.append(proc["instructions"])
        
        # Layer 4: Memory (warnings)
        mem = layers["memory"]
        if warnings:
            parts.append(f"\n⚠️ ATTENTION ({len(warnings)} avertissements):")
            for w in warnings:
                parts.append(f"  {w}")
        
        if mem.get("unresolved_failures", 0) > 0:
            parts.append(f"\nÉchecs non résolus: {mem['unresolved_failures']}")
        
        return "\n".join(parts)


# Singleton
context_builder = ContextBuilder()
