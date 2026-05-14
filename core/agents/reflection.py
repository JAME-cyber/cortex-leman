"""
Cortex Leman v5 — Nœud de Réflexion (Reflection Node)

Inspiré du pattern "LLM-as-judge" de JP Morgan "Ask David".
Le ReasoningAgent produit une analyse → le Reflection Node la critique →
le résultat final est soit confirmé, soit affiné.

Pipeline:
1. Recevoir l'analyse initiale du ReasoningAgent
2. Construire un prompt de critique (pas le même rôle que l'analyste)
3. Appeler le LLM en mode "réviseur"
4. Comparer la confiance originale vs. confiance révisée
5. Retourner le résultat enrichi

Configuration:
- REFLECTION_ENABLED=true  (activé par défaut)
- REFLECTION_MODE=standard (standard = 1 passe critique)
- Désactivé automatiquement en mode haute_protection si latence critique
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from core.config import settings

logger = logging.getLogger(__name__)


class ReflectionResult:
    """Résultat d'une réflexion (auto-critique)"""

    def __init__(
        self,
        original_confidence: float,
        revised_confidence: float,
        critique: str,
        issues_found: list[str],
        improvements: list[str],
        confirmed: bool,
        llm_used: bool = False,
    ):
        self.original_confidence = original_confidence
        self.revised_confidence = revised_confidence
        self.critique = critique
        self.issues_found = issues_found
        self.improvements = improvements
        self.confirmed = confirmed  # True si la réflexion confirme l'analyse
        self.llm_used = llm_used
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "original_confidence": self.original_confidence,
            "revised_confidence": self.revised_confidence,
            "confidence_delta": round(
                self.revised_confidence - self.original_confidence, 3
            ),
            "critique": self.critique,
            "issues_found": self.issues_found,
            "improvements": self.improvements,
            "confirmed": self.confirmed,
            "llm_used": self.llm_used,
            "timestamp": self.timestamp,
        }


class ReflectionNode:
    """
    Nœud de réflexion — auto-critique LLM avant livraison.

    Ce composant est l'équivalent du "reflection node" de JP Morgan Ask David.
    Il ne prend PAS de décision — il challenge l'analyse pour la renforcer.

    v5.3: Intégration FailureMemory + ProceduralMemory.
    - Les échecs passés sont injectés dans le prompt de critique.
    - Les insights de réflexion alimentent la mémoire procédurale.
    """

    def __init__(self):
        self._enabled = os.environ.get("REFLECTION_ENABLED", "true").lower() == "true"
        self._total_reflections = 0
        self._total_confirmed = 0
        self._total_revised = 0

        # v5.3: Mémoires intégrées
        from core.agents.memory import failure_memory, procedural_memory
        self._failure_memory = failure_memory
        self._procedural_memory = procedural_memory

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self) -> None:
        self._enabled = True
        logger.info("Reflection Node: activé")

    def disable(self) -> None:
        self._enabled = False
        logger.info("Reflection Node: désactivé")

    async def reflect(
        self,
        query: str,
        vertical: str,
        analysis: dict,
        compliance: dict,
        recommendations: dict,
        client_id: str = "unknown",
        intention_id: str = "unknown",
    ) -> Optional[ReflectionResult]:
        """
        Lancer une réflexion sur l'analyse produite par le ReasoningAgent.

        Args:
            query: La requête originale
            vertical: La verticale métier
            analysis: Résultat de l'analyse (dict avec confidence, factors, etc.)
            compliance: Résultat du check compliance
            recommendations: Les recommandations générées
            client_id: ID client
            intention_id: ID de l'intention

        Returns:
            ReflectionResult ou None si désactivé/LLM indisponible
        """
        if not self._enabled:
            return None

        original_confidence = analysis.get("confidence", 0.5)

        # 1. Construire le prompt de critique
        critique_prompt = self._build_critique_prompt(
            query, vertical, analysis, compliance, recommendations
        )

        # 2. Appeler le LLM en mode critique
        try:
            from core.integrations.llm import llm_service

            result = await llm_service.generate(
                system_prompt=self._get_critique_system_prompt(vertical),
                user_prompt=critique_prompt,
                max_tokens=2048,
                temperature=0.3,  # Basse température = critique plus cohérente
                vertical=vertical,
                client_id=client_id,
                intention_id=intention_id,
            )

            if not result.get("text"):
                logger.warning("Reflection Node: LLM indisponible — skip")
                return None

            # 3. Parser la critique
            critique_data = self._parse_critique(result["text"])

            # 4. Construire le résultat
            revised_confidence = critique_data.get("revised_confidence", original_confidence)

            # Si la confiance baisse de plus de 0.3, c'est une révision significative
            confirmed = abs(revised_confidence - original_confidence) < 0.3

            reflection = ReflectionResult(
                original_confidence=original_confidence,
                revised_confidence=revised_confidence,
                critique=critique_data.get("critique", ""),
                issues_found=critique_data.get("issues_found", []),
                improvements=critique_data.get("improvements", []),
                confirmed=confirmed,
                llm_used=True,
            )

            # Stats
            self._total_reflections += 1
            if confirmed:
                self._total_confirmed += 1
            else:
                self._total_revised += 1

            # v5.3: Alimenter la mémoire procédurale si des améliorations trouvées
            if critique_data.get("improvements") and vertical:
                improvements_text = "; ".join(critique_data["improvements"])
                self._procedural_memory.update_instructions(
                    agent_name="reasoning",
                    vertical=vertical,
                    instructions=f"Après réflexion: {improvements_text}",
                    insight_summary=critique_data.get("critique", "")[:200],
                )

            # v5.3: Enregistrer les problèmes comme échecs potentiels
            if not confirmed and critique_data.get("issues_found"):
                from core.agents.memory import FailureRecord
                for issue in critique_data["issues_found"][:3]:
                    record = FailureRecord(
                        agent_name="reasoning",
                        error_type="low_confidence_analysis",
                        error_message=issue,
                        vertical=vertical,
                        client_id=client_id,
                        intention_id=intention_id,
                    )
                    self._failure_memory.record_failure(record)

            logger.info(
                f"Reflection Node: confiance {original_confidence:.2f} → "
                f"{revised_confidence:.2f} "
                f"({'confirmé' if confirmed else 'révisé'})"
            )

            return reflection

        except Exception as e:
            logger.warning(f"Reflection Node: erreur LLM ({e}) — skip")
            return None

    def _get_critique_system_prompt(self, vertical: str) -> str:
        """System prompt pour le mode critique — un rôle différent de l'analyste"""
        return f"""Tu es un réviseur-expert du système Cortex Leman v5.
Ton rôle est de CRITIQUER l'analyse produite par l'Agent Raisonnement.

Verticale: {vertical}

Tu dois:
1. Identifier les faiblesses de l'analyse (arguments manquants, références imprécises)
2. Vérifier que les recommandations sont cohérentes avec les risques identifiés
3. Évaluer si le score de confiance est justifié
4. Proposer des améliorations concrètes

Tu ne dois PAS:
- Réécrire l'analyse complète
- Ajouter de nouvelles recommandations non liées à l'analyse
- Changer le score de confiance de plus de ±0.3 sans justification forte

FORMAT DE RÉPONSE (JSON):
{{
    "critique": "Résumé de ta critique en 2-3 phrases",
    "revised_confidence": 0.0-1.0,
    "issues_found": ["problème 1", "problème 2"],
    "improvements": ["amélioration 1", "amélioration 2"]
}}"""

    def _build_critique_prompt(
        self,
        query: str,
        vertical: str,
        analysis: dict,
        compliance: dict,
        recommendations: dict,
    ) -> str:
        """Construire le prompt de critique avec l'analyse à évaluer"""

        # v5.3: Injecter les échecs passés
        warnings = self._failure_memory.get_warnings("reasoning", vertical)
        failures_section = ""
        if warnings:
            failures_section = "\n\n⚠️ ÉCHECS PASSÉS À CONSIDÉRER:\n" + "\n".join(f"  - {w}" for w in warnings)

        # v5.3: Injecter les leçons apprises
        lessons = self._procedural_memory.get_instructions("reasoning", vertical)
        lessons_section = ""
        if lessons:
            lessons_section = f"\n\n📖 LEÇONS APPRISES (missions précédentes):\n{lessons}"

        return f"""CRITIQUE L'ANALYSE SUIVANTE:

REQUÊTE ORIGINALE: {query}
VERTICALE: {vertical}

ANALYSE PRODUITE:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

CHECK COMPLIANCE:
{json.dumps(compliance, ensure_ascii=False, indent=2)}

RECOMMANDATIONS:
{json.dumps(recommendations, ensure_ascii=False, indent=2)}{failures_section}{lessons_section}

Évalue cette analyse. Est-elle rigoureuse? Les références sont-elles pertinentes?
Le score de confiance est-il justifié? Y a-t-il des angles morts?"""

    def _parse_critique(self, text: str) -> dict:
        """Parser la réponse de critique (tolérant au formatage)"""
        result = {
            "critique": "",
            "revised_confidence": None,
            "issues_found": [],
            "improvements": [],
        }

        # Essayer JSON direct
        try:
            data = json.loads(text)
            result["critique"] = data.get("critique", "")
            result["revised_confidence"] = data.get("revised_confidence")
            result["issues_found"] = data.get("issues_found", [])
            result["improvements"] = data.get("improvements", [])
            return result
        except json.JSONDecodeError:
            pass

        # Chercher JSON dans backticks
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                result["critique"] = data.get("critique", "")
                result["revised_confidence"] = data.get("revised_confidence")
                result["issues_found"] = data.get("issues_found", [])
                result["improvements"] = data.get("improvements", [])
                return result
            except json.JSONDecodeError:
                pass

        # Chercher accolades
        brace_match = re.search(r'\{[\s\S]*\}', text)
        if brace_match:
            try:
                data = json.loads(brace_match.group(0))
                result["critique"] = data.get("critique", "")
                result["revised_confidence"] = data.get("revised_confidence")
                result["issues_found"] = data.get("issues_found", [])
                result["improvements"] = data.get("improvements", [])
                return result
            except json.JSONDecodeError:
                pass

        # Fallback: utiliser le texte brut comme critique
        result["critique"] = text[:500]
        return result

    def get_stats(self) -> dict:
        """Statistiques du nœud de réflexion"""
        return {
            "enabled": self._enabled,
            "total_reflections": self._total_reflections,
            "total_confirmed": self._total_confirmed,
            "total_revised": self._total_revised,
            "confirmation_rate": (
                round(self._total_confirmed / self._total_reflections, 3)
                if self._total_reflections > 0
                else None
            ),
            # v5.3: Stats mémoires
            "failure_patterns": self._failure_memory.get_error_patterns("reasoning"),
            "procedural_memories": self._procedural_memory.list_all(),
        }


# Singleton
reflection_node = ReflectionNode()
