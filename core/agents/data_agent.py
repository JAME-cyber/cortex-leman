"""
Cortex Leman v5 — Agent Data (LLM-wired)

Responsable de la recherche et collecte de données.
- Scan sources internes (RAG vectoriel)
- Recherche réglementaire via ChromaDB
- LLM pour reformulation de requêtes
- Documents (OCR)

Pipeline:
1. Recevoir requête sur cleman.data.query
2. Reformuler via LLM (optionnel)
3. RAG vectoriel → ChromaDB
4. Knowledge Vault (stockage)
5. Compiler résultats structurés
"""
import json
import logging

from core.agents.base_agent import BaseAgent
from core.bus.subjects import subjects

logger = logging.getLogger(__name__)


class DataAgent(BaseAgent):
    """
    Agent Data — Recherche et collecte avec RAG vectoriel.
    
    Sources:
    - ChromaDB (recherche sémantique)
    - Knowledge Vault (documents stockés)
    - LLM pour reformulation de requêtes
    """

    def __init__(self):
        super().__init__(
            name="data",
            subscribe_subjects=[subjects.DATA_QUERY],
        )
        self._complement_pending = False

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
        logger.info("Agent Data: écoute DATA_QUERY + demandes complément")

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
            f"{intention_id[:8] if intention_id else 'N/A'}..."
        )

        # Phase 1: Reformuler la requête via LLM (optionnel)
        enhanced_query = await self._enhance_query(query, vertical)

        # Phase 2: RAG vectoriel (ChromaDB)
        rag_results = await self._rag_search(
            enhanced_query or query, vertical, client_id
        )

        # Phase 3: Knowledge Vault (plein texte)
        vault_results = self._vault_search(client_id, query)

        # Phase 4: Compiler
        all_sources = rag_results + vault_results

        return {
            "recommendation": "data_collected" if all_sources else "data_not_found",
            "confidence": self._compute_confidence(all_sources),
            "sources": all_sources,
            "risks": self._identify_data_risks(all_sources, vertical),
            "summary": f"{len(all_sources)} sources trouvées pour '{query[:50]}...'",
            "enhanced_query": enhanced_query if enhanced_query != query else None,
            "rag_used": len(rag_results) > 0,
        }

    async def _enhance_query(self, query: str, vertical: str) -> str:
        """
        Reformuler la requête via LLM pour une meilleure recherche.
        Retourne la requête originale si LLM indisponible.
        """
        try:
            from core.integrations.llm import llm_service

            result = await llm_service.generate(
                system_prompt=(
                    f"Tu es un expert en recherche documentaire pour la verticale '{vertical}'. "
                    f"Reformule la requête utilisateur en termes de recherche optimaux. "
                    f"Réponds UNIQUEMENT avec la requête reformulée, rien d'autre."
                ),
                user_prompt=query,
                max_tokens=200,
                temperature=0.3,
            )

            enhanced = result.get("text", "").strip()
            if enhanced and len(enhanced) > 5:
                return enhanced

        except Exception as e:
            logger.debug(f"Reformulation LLM échouée: {e}")

        return query

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
                        "relevance": r.get("score", 0.5) / 10,  # normaliser
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

    def _compute_confidence(self, sources: list[dict]) -> float:
        """Calculer le score de confiance des résultats"""
        if not sources:
            return 0.0
        return min(1.0, sum(s.get("relevance", 0.5) for s in sources) / len(sources))

    def _identify_data_risks(self, sources: list[dict], vertical: str) -> list[str]:
        """Identifier les risques liés aux données collectées"""
        risks = []
        for source in sources:
            if source.get("type") == "external" and vertical in ("avocat", "banque"):
                risks.append("external_data_access_restricted")
        if not sources:
            risks.append("data_incomplete")
        return risks
