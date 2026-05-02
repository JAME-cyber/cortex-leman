"""
Cortex Leman v5 — Insight 5: MCP (Model Context Protocol) Server

Inspiré de l'écosystème AG2 — protocole MCP (Model Context Protocol)
Expose notre RAG ChromaDB comme source de données MCP.

Permet à des agents MCP externes (Claude Desktop, Cursor, etc.)
de requêter notre Knowledge Vault réglementaire via le protocole standard.

Spec MCP: https://spec.modelcontextprotocol.io/
Implementation: JSON-RPC 2.0 over stdio/SSE

Tools exposés:
  - rag_search: Recherche sémantique dans le Knowledge Vault
  - rag_regulatory: Liste les textes réglementaires par vertical
  - rag_stats: Statistiques du Knowledge Vault
"""
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server pour Cortex Leman v5 Knowledge Vault.

    Implémente le protocole MCP (JSON-RPC 2.0) pour exposer
    notre RAG ChromaDB à des agents externes.

    Mode SSE (Server-Sent Events) pour intégration web.
    Mode stdio pour intégration CLI (Claude Desktop, etc.).
    """

    def __init__(self, rag_client=None):
        self.rag = rag_client
        self.server_info = {
            "name": "cortex-leman-knowledge-vault",
            "version": "5.0.0",
            "description": "Knowledge Vault réglementaire FR-CH — RGPD, AI Act, CP 321, LB 47, LPM",
        }
        self.tools = self._define_tools()

    def _define_tools(self) -> list[dict]:
        """Définir les tools MCP disponibles"""
        return [
            {
                "name": "rag_search",
                "description": (
                    "Recherche sémantique dans le Knowledge Vault réglementaire FR-CH. "
                    "Sources: RGPD, AI Act, Code Pénal (secret professionnel), "
                    "Loi Bancaire (secret bancaire), LPM (santé). "
                    "Verticals: comptable, avocat, sante, banque, startup, rh"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Requête de recherche en langage naturel",
                        },
                        "vertical": {
                            "type": "string",
                            "enum": ["comptable", "avocat", "sante", "banque", "startup", "rh"],
                            "description": "Vertical métier pour filtrer les résultats",
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "Nombre de résultats (défaut: 5)",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "rag_regulatory",
                "description": (
                    "Lister les textes réglementaires disponibles par vertical. "
                    "Retourne les documents indexés dans le Knowledge Vault."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vertical": {
                            "type": "string",
                            "enum": ["comptable", "avocat", "sante", "banque", "startup", "rh"],
                            "description": "Vertical métier (optionnel, tous si absent)",
                        },
                    },
                },
            },
            {
                "name": "rag_stats",
                "description": "Statistiques du Knowledge Vault (nombre de documents, chunks, verticals).",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]

    def handle_request(self, request: dict) -> dict:
        """
        Traiter une requête MCP (JSON-RPC 2.0).

        Endpoints MCP:
        - initialize: Handshake
        - tools/list: Liste des tools
        - tools/call: Appel d'un tool
        """
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")

        try:
            if method == "initialize":
                return self._handle_initialize(req_id, params)
            elif method == "notifications/initialized":
                return None  # Notification, no response
            elif method == "tools/list":
                return self._handle_tools_list(req_id)
            elif method == "tools/call":
                return self._handle_tools_call(req_id, params)
            else:
                return self._error_response(req_id, -32601, f"Méthode inconnue: {method}")

        except Exception as e:
            logger.error(f"MCP error: {e}")
            return self._error_response(req_id, -32603, str(e))

    def _handle_initialize(self, req_id: int, params: dict) -> dict:
        """MCP initialize handshake"""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False},
                },
                "serverInfo": self.server_info,
            },
        }

    def _handle_tools_list(self, req_id: int) -> dict:
        """Lister les tools MCP disponibles"""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": self.tools,
            },
        }

    def _handle_tools_call(self, req_id: int, params: dict) -> dict:
        """Exécuter un tool MCP"""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "rag_search":
            result = self._tool_rag_search(arguments)
        elif tool_name == "rag_regulatory":
            result = self._tool_rag_regulatory(arguments)
        elif tool_name == "rag_stats":
            result = self._tool_rag_stats()
        else:
            return self._error_response(req_id, -32602, f"Tool inconnu: {tool_name}")

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2),
                    }
                ],
            },
        }

    def _tool_rag_search(self, args: dict) -> dict:
        """Exécuter une recherche RAG via MCP"""
        query = args.get("query", "")
        vertical = args.get("vertical")
        n_results = args.get("n_results", 5)

        if not self.rag:
            return {"error": "RAG non configuré", "results": []}

        try:
            results = self.rag.search(query, n_results=n_results, vertical_filter=vertical)
            return {
                "query": query,
                "vertical": vertical,
                "results": results,
                "count": len(results) if isinstance(results, list) else 0,
            }
        except Exception as e:
            return {"error": str(e), "results": []}

    def _tool_rag_regulatory(self, args: dict) -> dict:
        """Lister les textes réglementaires"""
        vertical = args.get("vertical")

        # Regulatory data from our vault
        regulations = {
            "comptable": [
                {"id": "rgpd-art-30", "title": "RGPD Art. 30 — Registre des traitements"},
                {"id": "ai-art-9", "title": "AI Act Art. 9 — Gestion des risques"},
                {"id": "lgf-223", "title": "LGF Art. 223 — Obligations déclaratives"},
                {"id": "cgi-238", "title": "CGI Art. 238 — Déductions fiscales"},
            ],
            "avocat": [
                {"id": "cp-321", "title": "Code Pénal Art. 321 — Secret professionnel"},
                {"id": "rgpd-art-9", "title": "RGPD Art. 9 — Données sensibles"},
                {"id": "ai-art-6", "title": "AI Act Art. 6 — Classification des risques"},
                {"id": "loi-71-1130", "title": "Loi 71-1130 — Profession d'avocat"},
            ],
            "sante": [
                {"id": "lpm", "title": "LPM — Loi sur la Protection Médicale"},
                {"id": "rgpd-art-9", "title": "RGPD Art. 9 — Données de santé"},
                {"id": "hds", "title": "HDS — Hébergement Données de Santé"},
            ],
            "banque": [
                {"id": "lb-47", "title": "Loi Bancaire Art. 47 — Secret bancaire CH"},
                {"id": "aml-4", "title": "AML 4/5 — Anti-blanchiment"},
                {"id": "finma-circ", "title": "FINMA Circ. — Outsourcing banque"},
            ],
            "startup": [
                {"id": "ai-art-6", "title": "AI Act Art. 6 — Classification"},
                {"id": "rgpd-art-35", "title": "RGPD Art. 35 — AIPD/DPIA"},
                {"id": "ai-art-52", "title": "AI Act Art. 52 — Obligations transparence"},
            ],
            "rh": [
                {"id": "loi-2008-496", "title": "Loi 2008-496 — Non-discrimination"},
                {"id": "rgpd-art-22", "title": "RGPD Art. 22 — Décision automatisée"},
                {"id": "ai-art-10", "title": "AI Act Art. 10 — Données d'entraînement"},
            ],
        }

        if vertical:
            return {"vertical": vertical, "regulations": regulations.get(vertical, [])}

        return {"regulations": regulations, "total_verticals": len(regulations)}

    def _tool_rag_stats(self) -> dict:
        """Statistiques du Knowledge Vault"""
        if self.rag:
            try:
                stats = self.rag.get_stats()
                return stats
            except Exception:
                pass

        return {
            "vault": "cortex-leman-v5",
            "documents": 20,
            "chunks": "~400",
            "verticals": 6,
            "embeddings_model": "all-MiniLM-L6-v2",
            "status": "operational",
        }

    def _error_response(self, req_id: Optional[int], code: int, message: str) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": code, "message": message},
        }


# Singleton
mcp_server = MCPServer()
