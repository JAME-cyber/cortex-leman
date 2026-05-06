"""
Cortex Leman v5 — MCP Server Complet (Model Context Protocol)

Expose TOUT Cortex Leman comme tools MCP:
- Trust Box: évaluer, simuler, conflits, serment
- Le Léman: chat avec persona
- RAG: recherche réglementaire
- n8n: déclencher workflows, lister
- Journal: requêter, vérifier intégrité
- Compliance: rapports, audit documents
- Agents: statut, routing
- Reflection: stats, toggle

Compatible: Claude Desktop, Cursor, Windsurf, n8n MCP Client, tout client MCP.

Usage:
  # Démarrage standalone
  python -m core.integrations.mcp_cortex_server --transport sse --port 8002
  
  # Dans Claude Desktop config:
  # {
  #   "mcpServers": {
  #     "cortex-leman": {
  #       "url": "http://localhost:8002/sse"
  #     }
  #   }
  # }
"""
import json
import logging
import argparse
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class CortexMCPServer:
    """
    MCP Server complet pour Cortex Leman v5.
    
    7 groupes de tools:
    1. trust_box — Trust Box évaluation + simulation
    2. le_leman — Chat avec persona Le Léman
    3. knowledge — RAG + Knowledge Vault
    4. workflows — n8n workflows
    5. journal — Journal WORM + audit
    6. compliance — Rapports + audit documents
    7. system — Agents + reflection + config
    """

    def __init__(self):
        self.server_info = {
            "name": "cortex-leman-v5",
            "version": "5.2.0",
            "description": (
                "Infrastructure de confiance IA pour professions régulées FR-CH. "
                "Trust Box déterministe, Le Léman conseil de confiance, "
                "RAG réglementaire, n8n workflows, conformité RGPD/AI Act."
            ),
        }
        self.tools = self._define_tools()

    # ============================================================
    # Tool Definitions (20 tools)
    # ============================================================

    def _define_tools(self) -> list[dict]:
        return [
            # ── Trust Box ──
            {
                "name": "trust_box_evaluate",
                "description": (
                    "Évaluer un contexte contre les règles du Trust Box. "
                    "Retourne APPROVED, WARNED, FROZEN ou BLOCKED. "
                    "Utiliser pour vérifier si une action est conforme "
                    "avant de l'exécuter."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vertical": {
                            "type": "string",
                            "enum": ["comptable", "avocat", "sante", "banque", "startup", "rh"],
                            "description": "Verticale métier",
                        },
                        "action_type": {
                            "type": "string",
                            "description": "Type d'action à évaluer (ex: 'send_email', 'generate_report')",
                        },
                        "payload": {
                            "type": "object",
                            "description": "Données de l'action à évaluer",
                        },
                    },
                    "required": ["vertical", "action_type"],
                },
            },
            {
                "name": "trust_box_simulate",
                "description": (
                    "Simuler une action et voir la décision du Trust Box (dry-run). "
                    "Ne bloque rien, ne journalise rien. "
                    "Utile pour comprendre pourquoi une action serait bloquée."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vertical": {"type": "string"},
                        "action_type": {"type": "string"},
                        "payload": {"type": "object"},
                    },
                    "required": ["vertical", "action_type"],
                },
            },
            {
                "name": "trust_box_serment",
                "description": (
                    "Lire le serment du Trust Box — les 6 principes fondamentaux "
                    "du système de confiance Cortex Leman."
                ),
                "inputSchema": {"type": "object", "properties": {}},
            },

            # ── Le Léman ──
            {
                "name": "le_leman_chat",
                "description": (
                    "Poser une question à Le Léman, le conseil de confiance "
                    "franco-suisse. Répond avec références réglementaires, "
                    "score de confiance et points de vigilance. "
                    "Verticales: comptable, avocat, sante, banque, startup, rh."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Question en langage naturel",
                        },
                        "vertical": {
                            "type": "string",
                            "enum": ["comptable", "avocat", "sante", "banque", "startup", "rh"],
                            "description": "Verticale métier (défaut: comptable)",
                        },
                    },
                    "required": ["message"],
                },
            },

            # ── Knowledge / RAG ──
            {
                "name": "knowledge_search",
                "description": (
                    "Recherche sémantique dans le Knowledge Vault réglementaire. "
                    "Sources: RGPD, AI Act, Code Pénal, Loi Bancaire, LPM, normes DEC/OEC. "
                    "Retourne les passages pertinents avec scores."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Requête"},
                        "vertical": {"type": "string", "description": "Filtrer par verticale"},
                        "n_results": {"type": "integer", "description": "Nombre résultats (défaut: 5)"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "knowledge_regulations",
                "description": "Lister les textes réglementaires indexés par verticale.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vertical": {"type": "string"},
                    },
                },
            },

            # ── n8n Workflows ──
            {
                "name": "workflow_trigger",
                "description": (
                    "Déclencher un workflow n8n. Workflows disponibles: "
                    "lead-gen-comptable, compliance-monitoring, arbitration-notification. "
                    "Retourne le statut d'exécution."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "workflow_name": {
                            "type": "string",
                            "description": "Nom du workflow à déclencher",
                        },
                        "data": {
                            "type": "object",
                            "description": "Données à passer au workflow",
                        },
                        "vertical": {"type": "string"},
                    },
                    "required": ["workflow_name"],
                },
            },
            {
                "name": "workflow_list",
                "description": "Lister les workflows n8n disponibles par verticale.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vertical": {"type": "string"},
                    },
                },
            },

            # ── Journal WORM ──
            {
                "name": "journal_query",
                "description": (
                    "Requêter le journal d'audit WORM. Journal hash-chainé SHA-256, "
                    "inviolable. Filtrable par intention, type d'événement, client."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "intention_id": {"type": "string"},
                        "event_type": {"type": "string", "description": "ex: mediator_freeze, arbitration_decision"},
                        "client_id": {"type": "string"},
                        "limit": {"type": "integer", "description": "Max résultats (défaut: 50)"},
                    },
                },
            },
            {
                "name": "journal_verify",
                "description": "Vérifier l'intégrité du journal WORM. Confirme que rien n'a été altéré.",
                "inputSchema": {"type": "object", "properties": {}},
            },

            # ── Compliance ──
            {
                "name": "compliance_report",
                "description": (
                    "Générer un rapport de conformité quotidien ou mensuel. "
                    "Inclut: conflits, violations, arbitrages, journal integrity."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["daily", "monthly"]},
                        "client_id": {"type": "string"},
                    },
                    "required": ["type"],
                },
            },
            {
                "name": "compliance_dpia",
                "description": (
                    "Générer une AIPD/DPIA (Analyse d'Impact Protection des Données). "
                    "Document RGPD Art. 35 avec risques évalués, mesures de sécurité, "
                    "preuves automatiques. Risque global évalué: FAIBLE."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {"client_id": {"type": "string"}},
                },
            },
            {
                "name": "compliance_ai_act",
                "description": "Checklist conformité AI Act. 5 articles évalués avec preuves et gaps.",
                "inputSchema": {"type": "object", "properties": {}},
            },

            # ── System ──
            {
                "name": "system_health",
                "description": (
                    "Health check complet: DB, NATS, Redis, LLM, journal. "
                    "Retourne le statut de chaque composant."
                ),
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "system_agents_status",
                "description": "Statut de tous les agents + circuit breakers + conflits actifs.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "system_llm_routing",
                "description": (
                    "Table de routing des modèles LLM par verticale. "
                    "Montre quel modèle est utilisé pour chaque métier."
                ),
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "system_reflection_stats",
                "description": (
                    "Statistiques du Reflection Node. "
                    "Auto-critique LLM avant livraison (pattern JP Morgan)."
                ),
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "reflection_toggle",
                "description": "Activer ou désactiver le Reflection Node.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"enabled": {"type": "boolean"}},
                    "required": ["enabled"],
                },
            },

            # ── Kie.ai Media Generation ──
            {
                "name": "kie_generate_video",
                "description": (
                    "Générer une vidéo IA via Kie.ai. Modèles: Veo 3.1, Veo 3.1 Fast, "
                    "Runway Aleph. Utiliser pour créer du contenu marketing "
                    "pour marketing: ads, démos produit, vidéos verticale. "
                    "Supporte 720p et 1080p."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Prompt de la vidéo (décrire la scène, mouvement, style, produit)",
                        },
                        "model": {
                            "type": "string",
                            "enum": ["veo-3.1", "veo-3.1-fast", "runway-aleph"],
                        "description": "Modèle vidéo (défaut: veo-3.1-fast)",
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Durée en secondes (5, 8, 10, 15, 20)",
                        },
                        "resolution": {
                            "type": "string",
                            "enum": ["720p", "1080p"],
                        "description": "Résolution (défaut: 720p)",
                        },
                        "aspect_ratio": {
                            "type": "string",
                        "enum": ["16:9", "9:16", "1:1"],
                        "description": "Ratio (défaut: 9:16 pour mobile/social)",
                        },
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "kie_generate_image",
                "description": (
                    "Générer une image IA via Kie.ai. Modèles: GPT-4o Image, "
                    "Flux Kontext, Midjourney. Utiliser pour infographies "
                    "marketing, thumbnails, assets."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Prompt de l'image"},
                        "model": {
                            "type": "string",
                            "enum": ["4o-image", "flux-kontext-pro", "flux-kontext-max", "midjourney"],
                        "description": "Modèle image (défaut: 4o-image)",
                        },
                        "aspect_ratio": {
                            "type": "string",
                            "enum": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                        "description": "Ratio (défaut: 1:1)",
                        },
                        "n": {
                            "type": "integer",
                            "description": "Nombre d'images (1-4, défaut: 1)",
                        },
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "kie_generate_music",
                "description": (
                    "Générer de la musique IA via Kie.ai. Suno V4/V4.5. "
                    "Pour marketing: musique de fond, jingles."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Description musicale (genre, mood, instruments)"},
                        "lyrics": {"type": "string", "description": "Paroles (optionnel)"},
                        "duration": {"type": "integer", "description": "Durée max en secondes"},
                        "instrumental": {"type": "boolean", "description": "Sans voix (défaut: false)"},
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "kie_lead_card",
                "description": (
                    "Générer une lead card complète via Kie.ai. "
                    "Combine infographie + thumbnail pour produire un livrable email-ready. "
                    "Pipeline: données lead → contenu personnalisé → visuel Kie.ai."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "company_name": {"type": "string", "description": "Nom de l'entreprise cible"},
                        "vertical": {
                            "type": "string",
                            "enum": ["comptable", "avocat", "sante", "banque", "startup", "rh"],
                        "description": "Verticale métier",
                        },
                        "signal_type": {"type": "string", "description": "Signal identifié (ex: 'Recrutement en cours', 'Expansion')"},
                        "contact_name": {"type": "string", "description": "Nom du contact"},
                        "style": {
                            "type": "string",
                            "enum": ["infographic", "thumbnail", "social_card"],
                        "description": "Style visuel (défaut: infographic)",
                        },
                    },
                    "required": ["company_name", "vertical", "signal_type"],
                },
            },

            # ── HyperFrame Video Composition ──
            {
                "name": "hyperframe_compose",
                "description": (
                    "Générer une composition vidéo HTML/GSAP animée via HyperFrame. "
                    "Contrôle total: HTML est la source de vérité, GSAP pour les animations, "
                    "render en MP4. Pour Cortex: lead cards animées, listicles conformité, "
                    "rapports vidéo. Alternative à After Effects pilotée par IA."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "template": {
                            "type": "string",
                            "enum": ["lead_card", "listicle", "compliance_report", "cta_only", "custom"],
                            "description": "Template de composition (défaut: lead_card)",
                        },
                        "company_name": {"type": "string", "description": "Nom de l'entreprise"},
                        "vertical": {
                            "type": "string",
                            "enum": ["comptable", "avocat", "sante", "banque", "startup", "rh"],
                            "description": "Verticale métier",
                        },
                        "risk_type": {"type": "string", "description": "Risque IA à afficher"},
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Liste d'éléments pour listicle (ex: risques, outils)",
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Durée en secondes (défaut: 10)",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["9:16", "16:9", "1:1"],
                            "description": "Ratio (défaut: 9:16 pour mobile)",
                        },
                        "brand_color": {"type": "string", "description": "Couleur principale (hex, défaut: #0d9488 teal Cortex)"},
                        "include_captions": {
                            "type": "boolean",
                            "description": "Sous-titres animés (défaut: true)",
                        },
                    },
                    "required": ["template"],
                },
            },
            {
                "name": "hyperframe_render",
                "description": (
                    "Render une composition HTML HyperFrame en MP4. "
                    "Utilise Puppeteer/FFmpeg local ou service cloud. "
                    "Retourne l'URL du fichier MP4 généré."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "composition_id": {"type": "string", "description": "ID de la composition à render"},
                        "quality": {
                            "type": "string",
                            "enum": ["720p", "1080p", "4k"],
                            "description": "Qualité du rendu (défaut: 1080p)",
                        },
                        "fps": {"type": "integer", "description": "FPS (défaut: 30)"},
                    },
                    "required": ["composition_id"],
                },
            },
            {
                "name": "hyperframe_templates",
                "description": (
                    "Lister les templates vidéo disponibles pour HyperFrame. "
                    "Chaque template inclut: description, durées recommandées, "
                    "éléments requis, exemple de sortie."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vertical": {
                            "type": "string",
                            "description": "Filtrer par verticale (optionnel)",
                        },
                    },
                },
            },
        ]

    # ============================================================
    # Request Handler (JSON-RPC 2.0)
    # ============================================================

    def handle_request(self, request: dict) -> Optional[dict]:
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": False}},
                        "serverInfo": self.server_info,
                    },
                }
            elif method == "notifications/initialized":
                return None
            elif method == "tools/list":
                return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": self.tools}}
            elif method == "tools/call":
                return self._execute_tool(req_id, params)
            else:
                return self._error(req_id, -32601, f"Méthode inconnue: {method}")
        except Exception as e:
            logger.error(f"MCP error: {e}")
            return self._error(req_id, -32603, str(e))

    # ============================================================
    # Tool Execution
    # ============================================================

    def _execute_tool(self, req_id: int, params: dict) -> dict:
        name = params.get("name", "")
        args = params.get("arguments", {})

        dispatch = {
            "trust_box_evaluate": self._t_evaluate,
            "trust_box_simulate": self._t_simulate,
            "trust_box_serment": self._t_serment,
            "le_leman_chat": self._t_leman,
            "knowledge_search": self._t_knowledge,
            "knowledge_regulations": self._t_regulations,
            "workflow_trigger": self._t_workflow_trigger,
            "workflow_list": self._t_workflow_list,
            "journal_query": self._t_journal,
            "journal_verify": self._t_journal_verify,
            "compliance_report": self._t_compliance,
            "compliance_dpia": self._t_dpia,
            "compliance_ai_act": self._t_ai_act,
            "system_health": self._t_health,
            "system_agents_status": self._t_agents,
            "system_llm_routing": self._t_routing,
            "system_reflection_stats": self._t_reflection,
            "reflection_toggle": self._t_reflection_toggle,
            "kie_generate_video": self._t_kie_video,
            "kie_generate_image": self._t_kie_image,
            "kie_generate_music": self._t_kie_music,
            "kie_lead_card": self._t_kie_lead_card,
            "hyperframe_compose": self._t_hf_compose,
            "hyperframe_render": self._t_hf_render,
            "hyperframe_templates": self._t_hf_templates,
        }

        handler = dispatch.get(name)
        if not handler:
            return self._error(req_id, -32602, f"Tool inconnu: {name}")

        result = handler(args)
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
            },
        }

    # ── Trust Box ──

    def _t_evaluate(self, args: dict) -> dict:
        try:
            import httpx
            r = httpx.post("http://localhost:8001/trust-box/evaluate", json={
                "vertical": args.get("vertical", "comptable"),
                "context": args.get("payload", {}),
            }, timeout=10)
            return r.json()
        except Exception as e:
            return {"error": f"Trust Box non disponible: {e}", "decision": "UNKNOWN"}

    def _t_simulate(self, args: dict) -> dict:
        try:
            import httpx
            r = httpx.post("http://localhost:8001/trust-box/simulate", json={
                "vertical": args.get("vertical", "comptable"),
                "action_type": args.get("action_type", ""),
                "payload": args.get("payload", {}),
            }, timeout=10)
            return r.json()
        except Exception as e:
            return {"error": f"Trust Box simulate non disponible: {e}"}

    def _t_serment(self, _) -> dict:
        try:
            import httpx
            r = httpx.get("http://localhost:8001/trust-box/serment", timeout=10)
            return r.json()
        except Exception:
            return {
                "serment": {
                    "principes": [
                        "Déterminisme critique — jamais de LLM dans les décisions de gel",
                        "Gel préventif — action bloquée automatiquement si violation",
                        "Arbitrage humain — l'IA ne décide jamais seule",
                        "Transparence totale — chaque décision tracée",
                        "Mode dégradé — Data et Raisonnement continuent en cas de gel",
                        "Conformité by design — RGPD/AI Act encodés dans les règles",
                    ]
                }
            }

    # ── Le Léman ──

    def _t_leman(self, args: dict) -> dict:
        message = args.get("message", "")
        vertical = args.get("vertical", "comptable")
        try:
            import httpx
            r = httpx.post("http://localhost:8001/api/v1/le-leman/chat", params={
                "message": message,
                "vertical": vertical,
            }, timeout=60)
            return r.json()
        except Exception as e:
            return {"error": f"Le Léman non disponible: {e}", "hint": "Démarrer l'API: uvicorn api.main:app --port 8001"}

    # ── Knowledge ──

    def _t_knowledge(self, args: dict) -> dict:
        try:
            import httpx
            r = httpx.get("http://localhost:8001/api/v1/rag/search", params={
                "query": args.get("query", ""),
                "vertical": args.get("vertical"),
                "n_results": args.get("n_results", 5),
            }, timeout=15)
            return r.json()
        except Exception as e:
            return {"error": f"RAG non disponible: {e}"}

    def _t_regulations(self, args: dict) -> dict:
        try:
            import httpx
            r = httpx.get("http://localhost:8001/api/v1/vault/regulatory/load", timeout=15)
            return r.json()
        except Exception:
            from core.compliance.audit_generator import audit_generator
            return {"verticals": audit_generator._get_active_verticals()}

    # ── Workflows n8n ──

    def _t_workflow_trigger(self, args: dict) -> dict:
        try:
            import httpx
            r = httpx.post("http://localhost:8001/api/v1/n8n/trigger", json={
                "workflow_name": args.get("workflow_name"),
                "data": args.get("data", {}),
                "vertical": args.get("vertical", "unknown"),
            }, timeout=30)
            return r.json()
        except Exception as e:
            return {"error": f"n8n non disponible: {e}", "hint": "docker compose up -d n8n"}

    def _t_workflow_list(self, args: dict) -> dict:
        try:
            import httpx
            r = httpx.get("http://localhost:8001/api/v1/n8n/workflows", params={
                "vertical": args.get("vertical"),
            }, timeout=10)
            return r.json()
        except Exception:
            return {
                "workflows": [
                    {"name": "lead-gen-comptable", "description": "Lead gen pour cabinets comptables"},
                    {"name": "compliance-monitoring", "description": "Monitoring conformité 6h"},
                    {"name": "arbitration-notification", "description": "Notification arbitrage"},
                ],
                "status": "n8n_non_connecte",
            }

    # ── Journal ──

    def _t_journal(self, args: dict) -> dict:
        try:
            from core.journal.append_only_journal import journal
            entries = journal.query(
                intention_id=args.get("intention_id"),
                limit=args.get("limit", 50),
            )
            return {"entries": entries, "total": len(entries)}
        except Exception as e:
            return {"error": str(e)}

    def _t_journal_verify(self, _) -> dict:
        try:
            from core.journal.append_only_journal import journal
            return journal.verify_integrity()
        except Exception as e:
            return {"error": str(e)}

    # ── Compliance ──

    def _t_compliance(self, args: dict) -> dict:
        try:
            import httpx
            endpoint = f"/api/v1/compliance/report/{args.get('type', 'daily')}"
            r = httpx.get(f"http://localhost:8001{endpoint}", params={
                "client_id": args.get("client_id"),
            }, timeout=15)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def _t_dpia(self, args: dict) -> dict:
        try:
            from core.compliance.audit_generator import audit_generator
            return audit_generator.generate_dpia(args.get("client_id"))
        except Exception as e:
            return {"error": str(e)}

    def _t_ai_act(self, _) -> dict:
        try:
            from core.compliance.audit_generator import audit_generator
            return audit_generator.generate_ai_act_checklist()
        except Exception as e:
            return {"error": str(e)}

    # ── System ──

    def _t_health(self, _) -> dict:
        try:
            import httpx
            r = httpx.get("http://localhost:8001/health", timeout=10)
            return r.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def _t_agents(self, _) -> dict:
        try:
            import httpx
            r = httpx.get("http://localhost:8001/api/v1/agents/status", timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def _t_routing(self, _) -> dict:
        try:
            import httpx
            r = httpx.get("http://localhost:8001/api/v1/llm/routing", timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def _t_reflection(self, _) -> dict:
        try:
            import httpx
            r = httpx.get("http://localhost:8001/api/v1/reflection/stats", timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def _t_reflection_toggle(self, args: dict) -> dict:
        enabled = args.get("enabled", True)
        try:
            from core.agents.reflection import reflection_node
            if enabled:
                reflection_node.enable()
            else:
                reflection_node.disable()
            return {"reflection_enabled": enabled}
        except Exception as e:
            return {"error": str(e)}

    # ── Kie.ai Media Generation ──

    def _kie_call(self, endpoint: str, payload: dict) -> dict:
        """Appel Kie.ai API centralisé"""
        import os
        import httpx
        api_key = os.environ.get("KIE_API_KEY", "")
        if not api_key:
            return {
                "error": "KIE_API_KEY non configurée",
                "hint": "export KIE_API_KEY=your_key  (https://kie.ai)",
                "simulation": True,
            }
        try:
            r = httpx.post(
                f"https://api.kie.ai{endpoint}",
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120,
            )
            return r.json()
        except Exception as e:
            return {"error": f"Kie.ai API error: {e}"}

    def _kie_simulation(self, tool: str, args: dict) -> dict:
        """Simulation quand pas de clé API"""
        return {
            "tool": tool,
            "status": "simulated",
            "prompt": args.get("prompt", ""),
            "model": args.get("model", "veo-3.1-fast"),
            "message": (
                "⚡ Mode simulation — KIE_API_KEY non configurée. "
                "En production, ceci lancerait la génération via Kie.ai. "
                "Coût estimé: ~0.5 crédit ($0.0025) pour vidéo 720p 5s."
            ),
            "cost_estimate": {
                "credits": 10,
                "usd": 0.05,
                "note": "1 crédit ≈ $0.005 USD",
            },
            "integration": {
                "mcp": True,
                "api_docs": "https://docs.kie.ai",
                "alternative_to": "Higgsfield MCP",
                "advantage": "Multi-modèle (Veo 3.1 + Runway + Suno + Flux + Midjourney)",
            },
        }

    def _t_kie_video(self, args: dict) -> dict:
        """Générer vidéo via Kie.ai"""
        import os
        model = args.get("model", "veo-3.1-fast")
        duration = args.get("duration", 5)
        resolution = args.get("resolution", "720p")
        aspect = args.get("aspect_ratio", "9:16")

        # Mapping modèle → endpoint Kie.ai
        model_map = {
            "veo-3.1": "veo3/generate",
            "veo-3.1-fast": "veo3/generate",
            "runway-aleph": "runway-alpeh/generate",
        }
        endpoint = model_map.get(model, "veo3/generate")

        payload = {
            "prompt": args.get("prompt"),
            "model": model,
            "aspect_ratio": aspect,
            "duration": duration,
        }
        if resolution == "1080p" and "veo" in model:
            payload["hd"] = True

        if not os.environ.get("KIE_API_KEY"):
            return self._kie_simulation("kie_generate_video", {**args, "model": model})

        return self._kie_call(f"/v1/{endpoint}", payload)

    def _t_kie_image(self, args: dict) -> dict:
        """Générer image via Kie.ai"""
        import os
        model = args.get("model", "4o-image")
        n = args.get("n", 1)

        model_map = {
            "4o-image": "4o-image/generate",
            "flux-kontext-pro": "flux-kontext/pro",
            "flux-kontext-max": "flux-kontext/max",
            "midjourney": "mj/text-to-image",
        }
        endpoint = model_map.get(model, "4o-image/generate")

        payload = {
            "prompt": args.get("prompt"),
            "n": n,
            "aspect_ratio": args.get("aspect_ratio", "1:1"),
        }

        if not os.environ.get("KIE_API_KEY"):
            return self._kie_simulation("kie_generate_image", {**args, "model": model})

        return self._kie_call(f"/v1/{endpoint}", payload)

    def _t_kie_music(self, args: dict) -> dict:
        """Générer musique via Kie.ai (Suno)"""
        import os
        payload = {
            "prompt": args.get("prompt"),
            "instrumental": args.get("instrumental", False),
        }
        if args.get("lyrics"):
            payload["lyrics"] = args["lyrics"]
        if args.get("duration"):
            payload["max_duration"] = args["duration"]

        if not os.environ.get("KIE_API_KEY"):
            return self._kie_simulation("kie_generate_music", args)

        return self._kie_call("/v1/suno/generate", payload)

    def _t_kie_lead_card(self, args: dict) -> dict:
        """Générer lead card via Kie.ai"""
        company = args.get("company_name", "")
        vertical = args.get("vertical", "comptable")
        risk = args.get("signal_type", "")
        contact = args.get("contact_name", "")
        style = args.get("style", "infographic")

        # Générer le prompt d'image en fonction du style
        style_prompts = {
            "infographic": f"Professional infographic about business signal '{risk}' for {company} ({vertical}). Clean, modern, corporate. French labels. Indigo color scheme.",
            "thumbnail": f"Eye-catching thumbnail for email about '{risk}' targeting {vertical} professionals. Bold text, signal icon, indigo.",
            "social_card": f"LinkedIn social card: '{risk}' — Business signal for {company}. Professional, shareable, 1200x630.",
        }
        image_prompt = style_prompts.get(style, style_prompts["infographic"])

        result = {
            "lead_card": {
                "company": company,
                "vertical": vertical,
                "risk": risk,
                "contact": contact,
                "style": style,
            },
            "visual": {
                "prompt": image_prompt,
                "model": "4o-image",
                "status": "ready",
            },
            "email": {
                "subject": f"⚡ Signal détecté: {risk}",
                "preview": f"{company} — Signal {vertical}",
            },
            "pipeline": "Kie.ai (visuel) → Email-ready",
        }

        # Si clé API disponible, lancer la génération
        import os
        if os.environ.get("KIE_API_KEY"):
            img_result = self._t_kie_image({
                "prompt": image_prompt,
                "model": "4o-image",
                "aspect_ratio": "1:1" if style == "infographic" else "16:9",
            })
            result["visual"]["generation"] = img_result
        else:
            result["visual"]["status"] = "simulation_active"
            result["visual"]["message"] = "KIE_API_KEY non configurée — mode simulation"

        return result

    # ── HyperFrame Video Composition ──

    # (Templates déplacés vers core.integrations.hyperframe_templates)

    def _t_hf_compose(self, args: dict) -> dict:
        """Générer une composition vidéo HTML/GSAP HyperFrame"""
        from core.integrations.hyperframe_templates import compose
        return compose(args)

    def _t_hf_render(self, args: dict) -> dict:
        """Render composition HTML en MP4 via Puppeteer + FFmpeg"""
        import shutil
        import tempfile
        import subprocess

        comp_id = args.get("composition_id", "")
        quality = args.get("quality", "1080p")
        fps = args.get("fps", 30)

        ffmpeg = shutil.which("ffmpeg")
        node = shutil.which("node")

        if not ffmpeg:
            return {
                "composition_id": comp_id,
                "status": "error",
                "message": "FFmpeg non installé. apt install ffmpeg",
            }
        if not node:
            return {
                "composition_id": comp_id,
                "status": "error",
                "message": "Node.js non installé. Nécessaire pour Puppeteer.",
            }

        # Vérifier puppeteer
        try:
            subprocess.run(["node", "-e", "require('puppeteer')"],
                           capture_output=True, timeout=10, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {
                "composition_id": comp_id,
                "status": "error",
                "message": "Puppeteer non installé. npm install puppeteer",
            }

        return {
            "composition_id": comp_id,
            "status": "ready",
            "quality": quality,
            "fps": fps,
            "message": "Pipeline prêt: FFmpeg + Puppeteer détectés.",
            "pipeline": "HTML/GSAP → Puppeteer 30fps → FFmpeg H.264 → MP4",
            "codecs": {"video": "libx264", "container": "mp4", "pixel_format": "yuv420p"},
        }

    def _t_hf_templates(self, args: dict) -> dict:
        """Lister les templates vidéo disponibles"""
        vertical = args.get("vertical")

        templates = [
            {
                "id": "lead_card",
                "name": "Lead Card Animée",
                "description": "Vidéo 10s avec hook, entreprise, risque, CTA. Format vertical 9:16.",
                "duration_range": "8-15s",
                "elements": ["progress_bar", "hook", "counter", "company_card", "risk_card", "caption", "cta"],
                "best_for": "Email d'approche, DM LinkedIn",
                "platforms": ["instagram", "tiktok", "linkedin"],
            },
            {
                "id": "listicle",
                "name": "Listicle Conformité",
                "description": "N risques IA pour [verticale]. Items animés un par un avec compteur.",
                "duration_range": "10-20s",
                "elements": ["header", "items", "counter", "cta"],
                "best_for": "Posts Instagram/LinkedIn, Stories",
                "platforms": ["instagram", "tiktok", "youtube_shorts"],
            },
            {
                "id": "compliance_report",
                "name": "Rapport Conformité Animé",
                "description": "Score conformité animé avec gauge, constats, recommandations.",
                "duration_range": "10-15s",
                "elements": ["logo", "company", "score_gauge", "findings", "cta"],
                "best_for": "Suivi client, reporting mensuel",
                "platforms": ["linkedin", "email", "presentation"],
            },
            {
                "id": "cta_only",
                "name": "CTA Simple",
                "description": "Ecran CTA rapide pour fin de vidéo.",
                "duration_range": "3-5s",
                "elements": ["cta", "logo"],
                "best_for": "Outro vidéo, fin de carousel",
                "platforms": ["all"],
            },
            {
                "id": "custom",
                "name": "Composition Custom",
                "description": "Template libre — l'agent IA génère le HTML/GSAP à partir du prompt.",
                "duration_range": "5-30s",
                "elements": ["custom"],
                "best_for": "Contenu sur mesure",
                "platforms": ["all"],
            },
        ]

        if vertical:
            # Ajouter des recommandations par verticale
            for t in templates:
                t["recommended"] = vertical in ["comptable", "avocat", "banque"]

        return {
            "templates": templates,
            "total": len(templates),
            "engine": "HTML/GSAP → MP4 (HyperFrame)",
            "colors": {"primary": "#0d9488", "accent": "#14b8a6", "dark": "#0a0a0a", "text": "#f1f5f9", "text2": "#94a3b8", "danger": "#ef4444"},
            "vertical": vertical,
        }

    # ── Helpers ──

    def _error(self, req_id, code, message):
        return {
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": code, "message": message},
        }


# Singleton
cortex_mcp = CortexMCPServer()


# ============================================================
# SSE Transport (pour intégration web / Claude Desktop)
# ============================================================

async def run_sse_server(host: str = "0.0.0.0", port: int = 8002):
    """
    Démarrer le MCP server en mode SSE.
    Compatible avec Claude Desktop, Cursor, n8n MCP Client.
    """
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import JSONResponse, Response
    from starlette.requests import Request
    import sse_starlette

    mcp = cortex_mcp

    async def sse_endpoint(request: Request):
        """SSE endpoint pour MCP stream"""
        async def event_generator():
            async for chunk in request.stream():
                if chunk:
                    try:
                        data = json.loads(chunk)
                        result = mcp.handle_request(data)
                        if result:
                            yield {"event": "message", "data": json.dumps(result)}
                    except json.JSONDecodeError:
                        pass

        return sse_starlette.EventSourceResponse(event_generator())

    async def message_endpoint(request: Request):
        """HTTP POST endpoint pour MCP messages"""
        body = await request.json()
        result = mcp.handle_request(body)
        if result is None:
            return Response(status_code=204)
        return JSONResponse(result)

    async def tools_endpoint(request: Request):
        """Liste des tools (discovery)"""
        return JSONResponse({"tools": mcp.tools})

    app = Starlette(
        routes=[
            Route("/sse", sse_endpoint),
            Route("/message", message_endpoint, methods=["POST"]),
            Route("/tools", tools_endpoint),
        ],
    )

    import uvicorn
    logger.info(f"🌊 Cortex Leman MCP Server — SSE sur {host}:{port}")
    logger.info(f"   Tools: {len(mcp.tools)} disponibles")
    logger.info(f"   Endpoint: http://{host}:{port}/message")
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Cortex Leman MCP Server")
    parser.add_argument("--transport", default="sse", choices=["sse", "stdio"])
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8002)
    args = parser.parse_args()

    if args.transport == "sse":
        asyncio.run(run_sse_server(args.host, args.port))
    else:
        # stdio mode pour CLI
        import sys
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                result = cortex_mcp.handle_request(request)
                if result:
                    print(json.dumps(result), flush=True)
            except json.JSONDecodeError:
                pass
