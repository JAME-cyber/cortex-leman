"""
Cortex Leman v5 — Agent Data (LLM-wired — Sprint 3)

Responsable de la recherche et collecte de données.
- Scan sources internes (RAG vectoriel)
- Recherche réglementaire via ChromaDB
- LLM pour reformulation de requêtes ET extraction structurée
- Compliance Gateway (vérification data residency)
- Mode Haute Protection: sources locales uniquement

Pipeline:
1. Recevoir requête sur cleman.data.query
2. Vérifier mode déploiement (Standard vs Haute Protection)
3. Reformuler via LLM pour optimiser la recherche
4. RAG vectoriel → ChromaDB
5. Knowledge Vault (plein texte)
6. Extraction LLM structurée des faits
7. Compiler résultats + horodatage + score de confiance
"""
import json
import logging
import uuid
from datetime import datetime, timezone

from core.agents.base_agent import BaseAgent
from core.bus.subjects import subjects
from core.config import settings

logger = logging.getLogger(__name__)


class DataAgent(BaseAgent):
    """
    Agent Data — Recherche et collecte avec RAG vectoriel + LLM.
    
    Sources:
    - ChromaDB (recherche sémantique)
    - Knowledge Vault (documents stockés)
    - LLM pour reformulation + extraction structurée
    
    Modes:
    - Standard: sources internes + externes, LLM OpenRouter
    - Haute Protection: sources locales uniquement, LLM Ollama
    """

    def __init__(self):
        super().__init__(
            name="data",
            subscribe_subjects=[subjects.DATA_QUERY],
        )
        self._complement_pending = False
        self._is_high_protection = settings.app_mode == "haute_protection"

    async def start(self) -> None:
        """Démarrage avec abonnement complémentaire"""
        from core.bus.nats_client import bus
        from core.bus.subjects import subjects
        await super().start()
        await bus.subscribe(
            "cleman.data.complement",
            self._on_complement_request,
            queue="agent-data",
        )
        mode_label = "HAUTE PROTECTION" if self._is_high_protection else "Standard"
        logger.info(f"Agent Data: écoute DATA_QUERY + demandes complément ({mode_label})")

    async def _on_complement_request(self, data: dict, meta: dict) -> None:
        """Traiter une demande de complément d'information"""
        intention_id = data.get("intention_id")
        missing_info = data.get("missing_info", [])
        logger.info(
            f"Agent Data: demande complément pour "
            f"{intention_id[:8] if intention_id else 'N/A'}... "
            f"infos manquantes: {missing_info}"
        )
        result = await self.process({
            "query": " ".join(missing_info),
            "intention_id": intention_id,
            "vertical": data.get("vertical", "unknown"),
            "context": {"complement_request": True},
        }, {})

    async def process(self, data: dict, meta: dict) -> dict:
        query = data.get("query", "")
        vertical = data.get("vertical", "unknown")
        context = data.get("context", {})
        client_id = data.get("client_id", "unknown")
        intention_id = data.get("intention_id")

        logger.info(
            f"Agent Data: recherche pour intention "
            f"{intention_id[:8] if intention_id else 'N/A'}... "
            f"(mode={'haute protection' if self._is_high_protection else 'standard'})"
        )

        # === Phase 0: Vérifier data residency ===
        residency_check = self._check_data_residency(vertical, client_id)
        if not residency_check["allowed"]:
            return {
                "recommendation": "data_blocked",
                "confidence": 0.0,
                "sources": [],
                "facts": [],
                "risks": [residency_check["reason"]],
                "summary": f"Recherche bloquée: {residency_check['reason']}",
                "enhanced_query": None,
                "rag_used": False,
                "llm_used": False,
                "mode": "haute_protection" if self._is_high_protection else "standard",
            }

        # === Phase 1: Reformuler la requête via LLM ===
        enhanced_query = await self._enhance_query(query, vertical)

        # === Phase 2: RAG vectoriel (ChromaDB) ===
        rag_results = await self._rag_search(
            enhanced_query or query, vertical, client_id
        )

        # === Phase 3: Knowledge Vault (plein texte) ===
        vault_results = self._vault_search(client_id, query)

        # === Phase 4: Compiler les sources brutes ===
        all_sources = rag_results + vault_results

        # === Phase 5: Extraction structurée via LLM ===
        facts = await self._extract_facts(
            query, vertical, all_sources, client_id, intention_id
        )

        # === Phase 6: Résultat final ===
        confidence = self._compute_confidence(all_sources, facts)
        query_display = query[:50] + "..." if len(query) > 50 else query

        return {
            "recommendation": "data_collected" if all_sources else "data_not_found",
            "confidence": confidence,
            "sources": all_sources,
            "facts": facts,
            "risks": self._identify_data_risks(all_sources, vertical),
            "summary": (
                f"{len(all_sources)} sources, {len(facts)} faits extraits "
                f"pour '{query_display}'"
            ),
            "enhanced_query": enhanced_query if enhanced_query != query else None,
            "rag_used": len(rag_results) > 0,
            "llm_used": bool(facts),
            "mode": "haute_protection" if self._is_high_protection else "standard",
            "data_residency": residency_check.get("mode", "standard"),
        }

    # ──────────────────────────────────────────────────
    # Data Residency
    # ──────────────────────────────────────────────────

    def _check_data_residency(self, vertical: str, client_id: str) -> dict:
        """Vérifier la conformité data residency avant toute recherche"""
        if self._is_high_protection:
            return {
                "allowed": True,
                "mode": "local_only",
                "reason": None,
            }

        # Verticales sensibles: avertissement en mode Standard
        restricted = {
            "avocat": "Art. 321 CP — sources externes interdites",
            "sante": "LPM + HDS — données santé non hébergées en cloud",
            "banque": "Art. 47 LB — secret bancaire CH",
        }

        if vertical in restricted:
            return {
                "allowed": True,
                "mode": "standard_warn",
                "reason": (
                    f"ATTENTION: {restricted[vertical]} — "
                    f"mode Haute Protection recommandé"
                ),
            }

        return {"allowed": True, "mode": "standard", "reason": None}

    # ──────────────────────────────────────────────────
    # LLM: Reformulation de requête
    # ──────────────────────────────────────────────────

    async def _enhance_query(self, query: str, vertical: str) -> str:
        """
        Reformuler la requête via LLM pour une meilleure recherche.
        Utilise le skill prompt data.md via generate_for_agent.
        Retourne la requête originale si LLM indisponible.
        """
        try:
            from core.integrations.llm import llm_service

            result = await llm_service.generate_for_agent(
                agent_name="data",
                task=(
                    f"Reformule cette requête de recherche en termes optimaux "
                    f"pour la verticale '{vertical}'.\n\n"
                    f"Requête: {query}\n\n"
                    f"Réponds UNIQUEMENT avec la requête reformulée, rien d'autre. "
                    f"Pas d'explication, pas de contexte."
                ),
                context={"query": query, "vertical": vertical},
                vertical=vertical,
                use_rag=False,
            )

            enhanced = result.get("text", "").strip()
            enhanced = enhanced.strip('"').strip("'")
            if enhanced and 5 < len(enhanced) < 500:
                return enhanced

        except Exception as e:
            logger.debug(f"Reformulation LLM échouée: {e}")

        return query

    # ──────────────────────────────────────────────────
    # LLM: Extraction structurée de faits
    # ──────────────────────────────────────────────────

    async def _extract_facts(
        self,
        query: str,
        vertical: str,
        sources: list[dict],
        client_id: str,
        intention_id: str,
    ) -> list[dict]:
        """
        Extraction structurée de faits via LLM.
        Transforme les sources brutes en faits horodatés avec source.
        Retourne [] si LLM indisponible (mode dégradé programmatique).
        """
        if not sources:
            return []

        try:
            from core.integrations.llm import llm_service

            sources_text = self._format_sources_for_llm(sources)

            task = (
                f"EXTRAIS les faits pertinents des sources suivantes "
                f"pour répondre à la requête.\n\n"
                f"REQUÊTE: {query}\n"
                f"VERTICALE: {vertical}\n\n"
                f"SOURCES:\n{sources_text}\n\n"
                f"Pour chaque fait, fournis:\n"
                f"- description: résumé factuel (1 phrase)\n"
                f"- source: référence exacte\n"
                f"- confidence: 0.0 à 1.0\n\n"
                f"FORMAT JSON attendu — un tableau:\n"
                f'[{{"description": "...", "source": "...", "confidence": 0.0}}]\n\n'
                f"IMPORTANT: Seulement des FAITS vérifiables. "
                f"Pas d'opinions. Pas de données personnelles."
            )

            result = await llm_service.generate_for_agent(
                agent_name="data",
                task=task,
                context={
                    "query": query,
                    "vertical": vertical,
                    "source_count": len(sources),
                },
                vertical=vertical,
                client_id=client_id,
                intention_id=intention_id or "unknown",
                use_rag=False,
            )

            if not result.get("text"):
                return self._fallback_facts(sources)

            facts = self._parse_facts_response(result["text"])

            # Horodater chaque fait
            now = datetime.now(timezone.utc).isoformat()
            for fact in facts:
                fact["id"] = f"f-{uuid.uuid4().hex[:8]}"
                fact["timestamp"] = now
                fact["extracted_by"] = "data_agent_llm"

            return facts

        except Exception as e:
            logger.warning(f"Extraction LLM échouée: {e} — mode dégradé")
            return self._fallback_facts(sources)

    def _format_sources_for_llm(self, sources: list[dict]) -> str:
        """Formater les sources pour injection dans le prompt LLM"""
        parts = []
        for i, s in enumerate(sources[:10], 1):
            src_type = s.get("type", "unknown")
            relevance = s.get("relevance", 0)
            data = s.get("data", {})

            if src_type == "rag":
                parts.append(
                    f"[{i}] RAG (pertinence: {relevance:.0%})\n"
                    f"    Titre: {data.get('title', 'N/A')}\n"
                    f"    Contenu: {data.get('content', 'N/A')[:300]}"
                )
            elif src_type == "vault":
                parts.append(
                    f"[{i}] Vault — {data.get('name', 'N/A')}\n"
                    f"    Tags: {', '.join(data.get('tags', []))}\n"
                    f"    Extrait: {data.get('snippet', 'N/A')[:300]}"
                )
            else:
                parts.append(
                    f"[{i}] {src_type}: {json.dumps(data, ensure_ascii=False)[:300]}"
                )

        return "\n\n".join(parts)

    def _parse_facts_response(self, text: str) -> list[dict]:
        """Extraire les faits structurés de la réponse LLM"""
        import re

        # Essayer directement
        try:
            facts = json.loads(text)
            if isinstance(facts, list):
                return [f for f in facts if isinstance(f, dict) and "description" in f]
        except json.JSONDecodeError:
            pass

        # Backticks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if json_match:
            try:
                facts = json.loads(json_match.group(1))
                if isinstance(facts, list):
                    return [f for f in facts if isinstance(f, dict) and "description" in f]
            except json.JSONDecodeError:
                pass

        # Crochets
        bracket_match = re.search(r'\[[\s\S]*\]', text)
        if bracket_match:
            try:
                facts = json.loads(bracket_match.group(0))
                if isinstance(facts, list):
                    return [f for f in facts if isinstance(f, dict) and "description" in f]
            except json.JSONDecodeError:
                pass

        return []

    def _fallback_facts(self, sources: list[dict]) -> list[dict]:
        """
        Créer des faits basiques depuis les sources brutes.
        Mode dégradé quand le LLM n'est pas disponible.
        """
        now = datetime.now(timezone.utc).isoformat()
        facts = []
        for s in sources[:10]:
            data = s.get("data", {})
            content = (
                data.get("content", "")
                or data.get("snippet", "")
                or data.get("name", "")
            )
            if content:
                facts.append({
                    "id": f"f-{uuid.uuid4().hex[:8]}",
                    "description": content[:200],
                    "source": s.get("type", "unknown"),
                    "confidence": round(s.get("relevance", 0.5), 3),
                    "timestamp": now,
                    "extracted_by": "data_agent_programmatic",
                })
        return facts

    # ──────────────────────────────────────────────────
    # Sources: RAG + Vault
    # ──────────────────────────────────────────────────

    async def _rag_search(
        self, query: str, vertical: str, client_id: str
    ) -> list[dict]:
        """Recherche sémantique via ChromaDB"""
        results = []

        try:
            from core.integrations.rag import get_rag
            rag = get_rag()

            rag_results = rag.search(
                query=query,
                client_id=client_id if client_id != "unknown" else None,
                n_results=5,
                vertical=vertical,
            )

            for r in rag_results:
                results.append({
                    "type": "rag",
                    "source": r.get("source", "unknown"),
                    "relevance": r.get("relevance", 0.5),
                    "data": {
                        "content": r.get("content", "")[:500],
                        "title": r.get("title", ""),
                        "doc_id": r.get("doc_id", ""),
                    },
                })

        except Exception as e:
            logger.debug(f"RAG non disponible: {e}")

        return results

    def _vault_search(self, client_id: str, query: str) -> list[dict]:
        """Recherche plein texte dans le Knowledge Vault"""
        results = []

        try:
            from core.integrations.knowledge_vault import knowledge_vault

            if client_id and client_id != "unknown":
                vault_results = knowledge_vault.search(
                    client_id=client_id, query=query, limit=5
                )
                for r in vault_results:
                    results.append({
                        "type": "vault",
                        "source": "knowledge_vault",
                        "relevance": r.get("score", 0.5) / 10,
                        "data": {
                            "name": r.get("name", ""),
                            "doc_id": r.get("doc_id", ""),
                            "snippet": r.get("snippet", ""),
                            "tags": r.get("tags", []),
                        },
                    })

        except Exception as e:
            logger.debug(f"Vault non disponible: {e}")

        return results

    # ──────────────────────────────────────────────────
    # Confiance + Risques
    # ──────────────────────────────────────────────────

    def _compute_confidence(
        self, sources: list[dict], facts: list[dict] = None
    ) -> float:
        """Calculer le score de confiance des résultats"""
        if not sources:
            return 0.0

        source_conf = min(
            1.0, sum(s.get("relevance", 0.5) for s in sources) / len(sources)
        )

        if facts:
            fact_conf = sum(f.get("confidence", 0.5) for f in facts) / len(facts)
            return round(0.4 * source_conf + 0.6 * fact_conf, 3)

        return round(source_conf, 3)

    def _identify_data_risks(self, sources: list[dict], vertical: str) -> list[str]:
        """Identifier les risques liés aux données collectées"""
        risks = []
        for source in sources:
            if source.get("type") == "external" and vertical in ("avocat", "banque"):
                risks.append("external_data_access_restricted")
        if not sources:
            risks.append("data_incomplete")
        if self._is_high_protection and vertical in ("avocat", "sante", "banque"):
            risks.append("haute_protection_local_only")
        return risks
