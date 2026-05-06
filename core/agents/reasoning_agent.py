"""
Cortex Leman v5 — Agent Raisonnement (LLM-wired + Reflection Node)

Responsable de l'analyse, comparaison et recommandations.
- Compare specs/risques via LLM
- Intègre contexte RAG réglementaire
- Génère recommandations structurées
- Reflection Node: auto-critique LLM avant livraison (pattern JP Morgan)
- PEUT demander une révision d'intention si incohérence détectée

Couches:
- Skill prompt: core/agents/prompts/reasoning.md
- RAG: ChromaDB contexte réglementaire
- LLM: OpenRouter (standard) / Ollama (haute protection)
- Reflection: Nœud de réflexion (critique + confirmation)
- Guardrails: PII masking + topic control + output safety
"""
import json
import logging

from core.agents.base_agent import BaseAgent
from core.bus.subjects import subjects

logger = logging.getLogger(__name__)


class ReasoningAgent(BaseAgent):
    """
    Agent Raisonnement — Analyse et recommandations avec LLM + Reflection Node.
    
    Pipeline:
    1. Recevoir les données de l'Agent Data
    2. Construire le prompt avec skill + contexte RAG
    3. Appeler le LLM (via LLMService.generate_for_agent)
    4. Parser et structurer la réponse
    5. ★ Reflection Node: auto-critique de l'analyse (pattern JP Morgan)
    6. Vérifier les triggers de révision
    """

    def __init__(self):
        super().__init__(
            name="reasoning",
            subscribe_subjects=[subjects.REASONING_ANALYZE],
        )

    async def process(self, data: dict, meta: dict) -> dict:
        query = data.get("query", "")
        vertical = data.get("vertical", "unknown")
        context = data.get("context", {})
        client_id = data.get("client_id", "unknown")
        intention_id = data.get("intention_id")

        logger.info(
            f"Agent Raisonnement: analyse pour intention "
            f"{intention_id[:8] if intention_id else 'N/A'}..."
        )

        # === Phase 1: Analyse rapide (programmatique) ===
        analysis = self._analyze_context(context, query)
        compliance_check = self._check_compliance(analysis, vertical)

        # === Phase 2: Analyse LLM (si disponible) ===
        llm_result = await self._llm_analyze(query, vertical, context, client_id, intention_id)

        if llm_result.get("text"):
            # Le LLM a répondu — enrichir l'analyse
            llm_analysis = self._parse_llm_response(llm_result["text"])
            analysis["llm_enriched"] = True
            analysis["llm_confidence"] = llm_analysis.get("confidence")
            if llm_analysis.get("applicable_texts"):
                compliance_check["references"] = list(set(
                    compliance_check.get("references", []) +
                    llm_analysis["applicable_texts"]
                ))
            if llm_analysis.get("recommendations"):
                analysis["llm_recommendations"] = llm_analysis["recommendations"]

        # === Phase 3: Recommandations fusionnées ===
        recommendations = self._generate_recommendations(
            analysis, compliance_check, vertical
        )

        # === Phase 4: Reflection Node (auto-critique JP Morgan pattern) ===
        reflection_data = None
        try:
            from core.agents.reflection import reflection_node
            reflection = await reflection_node.reflect(
                query=query,
                vertical=vertical,
                analysis=analysis,
                compliance=compliance_check,
                recommendations=recommendations,
                client_id=client_id,
                intention_id=intention_id or "unknown",
            )
            if reflection:
                reflection_data = reflection.to_dict()
                # Ajuster la confiance finale si la réflexion est significative
                if not reflection.confirmed:
                    final_confidence = reflection.revised_confidence
                    logger.info(
                        f"Reflection Node: confiance ajustée "
                        f"{reflection.original_confidence:.2f} → "
                        f"{reflection.revised_confidence:.2f}"
                    )
                    # Si la réflexion a trouvé des problèmes, les ajouter aux risques
                    for issue in reflection.issues_found:
                        compliance_check.setdefault("risks", []).append(
                            f"reflection: {issue}"
                        )
        except ImportError:
            logger.debug("Reflection Node non disponible")
        except Exception as e:
            logger.warning(f"Reflection Node erreur: {e}")

        # === Phase 5: Vérification des triggers de révision ===
        if self._should_request_revision(analysis, compliance_check, context) and intention_id:
            from core.bus.nats_client import bus
            from core.bus.subjects import subjects
            await bus.publish(subjects.INTENTION_REVISE, {
                "intention_id": intention_id,
                "context_update": {
                    "reasoning_revision": {
                        "reason": "incoherence_detectee",
                        "risks": compliance_check.get("risks", []),
                        "original_confidence": analysis.get("confidence"),
                        "revised_confidence": max(0.1, analysis.get("confidence", 0.5) - 0.3),
                        "compliance_check": compliance_check,
                    }
                },
            })
            logger.info(f"Agent Raisonnement: demande de révision pour {intention_id[:8]}...")

        # Calculer la confiance finale
        final_confidence = analysis.get("confidence", 0.5)
        if llm_result.get("text") and analysis.get("llm_confidence"):
            # Moyenne pondérée: 40% programmatique + 60% LLM
            final_confidence = (
                0.4 * analysis.get("confidence", 0.5) +
                0.6 * analysis["llm_confidence"]
            )

        return {
            "recommendation": recommendations.get("primary", "analyze_complete"),
            "confidence": round(final_confidence, 3),
            "analysis": analysis,
            "compliance": compliance_check,
            "risks": compliance_check.get("risks", []),
            "recommendations": recommendations,
            "regulatory_refs": compliance_check.get("references", []),
            "llm_used": llm_result.get("text") is not None and llm_result.get("text") != "",
            "llm_model": llm_result.get("model"),
            "llm_provider": llm_result.get("provider"),
            "reflection": reflection_data,
        }

    async def _llm_analyze(
        self,
        query: str,
        vertical: str,
        context: dict,
        client_id: str,
        intention_id: str,
    ) -> dict:
        """
        Appel LLM pour analyse approfondie.
        Retourne {} si LLM indisponible (mode dégradé).
        """
        try:
            from core.integrations.llm import llm_service

            # Construire la tâche structurée
            task = self._build_analysis_task(query, vertical, context)

            result = await llm_service.generate_for_agent(
                agent_name="reasoning",
                task=task,
                context=context,
                vertical=vertical,
                client_id=client_id,
                intention_id=intention_id or "unknown",
                use_rag=True,
            )

            if result.get("error"):
                logger.warning(f"LLM indisponible: {result['error']} — mode dégradé")
                return {"text": "", "error": result["error"]}

            return result

        except Exception as e:
            logger.warning(f"LLM analyse échouée: {e} — mode dégradé")
            return {"text": "", "error": str(e)}

    def _build_analysis_task(self, query: str, vertical: str, context: dict) -> str:
        """Construire la tâche structurée pour le LLM"""
        context_str = json.dumps(context, ensure_ascii=False, indent=2) if context else "{}"

        return f"""Analyse la requête suivante pour la verticale '{vertical}'.

REQUÊTE: {query}

DONNÉES DISPONIBLES:
{context_str}

Produis une analyse structurée avec:
1. Les textes réglementaires applicables (avec articles exacts)
2. Score de confiance (0.0 à 1.0)
3. Risques identifiés
4. Recommandations (minimum 2 options si possible)
5. Si une vérification humaine est nécessaire

FORMAT JSON attendu:
{{
    "applicable_texts": ["Art. X Loi Y", ...],
    "confidence": 0.0-1.0,
    "risks": ["..."],
    "recommendations": [
        {{"option": "A", "description": "...", "risk_level": "low|medium|high"}}
    ],
    "requires_human": true/false
}}"""

    def _parse_llm_response(self, text: str) -> dict:
        """Extraire le JSON de la réponse LLM (tolérant au formatage)"""
        result = {}

        # Chercher du JSON dans la réponse
        try:
            # Essayer directement
            result = json.loads(text)
        except json.JSONDecodeError:
            # Chercher entre des backticks ou des balises
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            else:
                # Chercher des accolades
                brace_match = re.search(r'\{[\s\S]*\}', text)
                if brace_match:
                    try:
                        result = json.loads(brace_match.group(0))
                    except json.JSONDecodeError:
                        pass

        return result

    def _should_request_revision(self, analysis: dict, compliance: dict, context: dict) -> bool:
        """Déterminer si une révision d'intention est nécessaire"""
        revision_triggers = (
            "data_residency_strict",
            "threshold_exceeded",
            "conflicting_data",
            "compliance_violation",
            "regulatory_conflict",
            "montant_hors_seuil",
        )

        return (
            compliance.get("risks")
            and any(r for r in compliance.get("risks", []) if r in revision_triggers)
        ) or (
            analysis.get("confidence", 1.0) < 0.3
        ) or (
            context.get("contradictory_data") or context.get("threshold_exceeded")
        )

    # === Méthodes programmatiques (mode dégradé sans LLM) ===

    def _analyze_context(self, context: dict, query: str) -> dict:
        """Analyser le contexte et les données disponibles"""
        return {
            "confidence": 0.75,
            "factors": list(context.keys()),
            "query_type": self._classify_query(query),
        }

    def _classify_query(self, query: str) -> str:
        """Classifier le type de requête"""
        query_lower = query.lower()
        if any(w in query_lower for w in ["compare", "meilleur", "analyser"]):
            return "comparison"
        if any(w in query_lower for w in ["risque", "conform", "audit"]):
            return "risk_assessment"
        if any(w in query_lower for w in ["recommande", "conseil", "avis"]):
            return "recommendation"
        return "general"

    def _check_compliance(self, analysis: dict, vertical: str) -> dict:
        """Vérification réglementaire programmatique"""
        risks = []
        references = []

        if vertical in ("avocat", "banque", "sante"):
            risks.append("data_residency_strict")
            refs = {
                "avocat": "Art. 321 CP",
                "banque": "Art. 47 LB",
                "sante": "LPM + HDS",
            }
            references.append(refs.get(vertical, ""))

        return {
            "compliant": len(risks) == 0,
            "risks": risks,
            "references": references,
        }

    def _generate_recommendations(
        self, analysis: dict, compliance: dict, vertical: str
    ) -> dict:
        """Générer les recommandations"""
        recs = {
            "primary": "proceed",
            "actions": [],
        }

        if not compliance.get("compliant"):
            recs["primary"] = "requires_review"
            recs["actions"].append({
                "type": "compliance_review",
                "priority": "high",
                "message": "Points de conformité à vérifier avant poursuite",
            })

        # Enrichir avec les recommandations LLM si disponibles
        if analysis.get("llm_recommendations"):
            for rec in analysis["llm_recommendations"]:
                recs["actions"].append({
                    "type": "llm_recommendation",
                    "source": "reasoning_llm",
                    **rec,
                })

        return recs
