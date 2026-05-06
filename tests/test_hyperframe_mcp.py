"""
Tests des tools HyperFrame dans le MCP Cortex Server.
Templates HTML/GSAP, composition, render, catalogue.
"""
import json
import pytest


@pytest.fixture
def mcp():
    from core.integrations.mcp_cortex_server import CortexMCPServer
    return CortexMCPServer()


# ── Tool Discovery ──

class TestHyperFrameDiscovery:
    """Les 3 tools HyperFrame doivent être déclarés."""

    def test_hf_compose_registered(self, mcp):
        names = [t["name"] for t in mcp.tools]
        assert "hyperframe_compose" in names

    def test_hf_render_registered(self, mcp):
        names = [t["name"] for t in mcp.tools]
        assert "hyperframe_render" in names

    def test_hf_templates_registered(self, mcp):
        names = [t["name"] for t in mcp.tools]
        assert "hyperframe_templates" in names

    def test_total_tools_25(self, mcp):
        """22 tools existants + 4 Kie.ai + 3 HyperFrame = 25"""
        assert len(mcp.tools) == 25

    def test_compose_has_template_enum(self, mcp):
        tool = next(t for t in mcp.tools if t["name"] == "hyperframe_compose")
        enum = tool["inputSchema"]["properties"]["template"]["enum"]
        assert "lead_card" in enum
        assert "listicle" in enum
        assert "compliance_report" in enum

    def test_render_requires_composition_id(self, mcp):
        tool = next(t for t in mcp.tools if t["name"] == "hyperframe_render")
        assert "composition_id" in tool["inputSchema"]["required"]


# ── Lead Card Template ──

class TestHyperFrameLeadCard:
    """Tests du template lead card animée."""

    def test_lead_card_composition(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "lead_card",
                "company_name": "Cabinet Dupont",
                "vertical": "comptable",
                "risk_type": "Chatbot fiscal sans consentement",
                "duration": 10,
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["status"] == "composed"
        assert result["template"] == "lead_card"
        assert "composition_id" in result
        assert result["composition_id"].startswith("sp-")

    def test_lead_card_contains_company(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "lead_card",
                "company_name": "Maître Laurent",
                "vertical": "avocat",
                "risk_type": "IA dans les conclusions",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert "Maître Laurent" in result["html_full"]
        assert "IA dans les conclusions" in result["html_full"]

    def test_lead_card_has_gsap(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "lead_card",
                "company_name": "Test",
                "vertical": "sante",
                "risk_type": "Test risk",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert "gsap" in result["html_full"]
        assert "gsap.timeline" in result["html_full"]

    def test_lead_card_vertical_format(self, mcp):
        """Format 9:16 = 1080x1920"""
        req = {
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "lead_card",
                "company_name": "Test",
                "vertical": "banque",
                "risk_type": "Test",
                "format": "9:16",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert "1080px" in result["html_full"]
        assert "1920px" in result["html_full"]

    def test_lead_card_cortex_colors(self, mcp):
        """Les couleurs Cortex Leman sont utilisées"""
        req = {
            "jsonrpc": "2.0", "id": 5, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "lead_card",
                "company_name": "Test",
                "vertical": "startup",
                "risk_type": "Test",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert "#0d9488" in result["html_full"]  # teal primary

    def test_lead_card_progress_bar(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 6, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "lead_card",
                "company_name": "Test",
                "vertical": "rh",
                "risk_type": "Test",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert "progressFill" in result["html_full"] or "progress-fill" in result["html_full"]

    def test_lead_card_vertical_icon(self, mcp):
        """Chaque verticale a son icône"""
        req = {
            "jsonrpc": "2.0", "id": 7, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "lead_card",
                "company_name": "Test",
                "vertical": "avocat",
                "risk_type": "Test",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert "⚖️" in result["html_full"]


# ── Listicle Template ──

class TestHyperFrameListicle:
    """Tests du template listicle."""

    def test_listicle_composition(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 10, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "listicle",
                "vertical": "comptable",
                "items": [
                    "Chatbot fiscal sans consentement",
                    "Scoring client sans DPIA",
                    "Données transférées hors UE",
                ],
                "duration": 15,
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["template"] == "listicle"
        assert "Chatbot fiscal" in result["html_full"]
        assert "1 / 3" in result["html_full"] or "1/3" in result["html_full"]

    def test_listicle_max_5_items(self, mcp):
        """Le template limite à 5 items max"""
        req = {
            "jsonrpc": "2.0", "id": 11, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "listicle",
                "vertical": "sante",
                "items": ["A", "B", "C", "D", "E", "F", "G"],  # 7 items
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        # Devrait avoir max 5 items
        assert ("5 / 5" in result["html_full"] or "5/5" in result["html_full"])
        assert "6 / 5" not in result["html_full"]


# ── Compliance Report Template ──

class TestHyperFrameComplianceReport:
    """Tests du template rapport conformité."""

    def test_compliance_report_composition(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 20, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "compliance_report",
                "company_name": "Clinique du Léman",
                "vertical": "sante",
                "duration": 12,
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["template"] == "compliance_report"
        assert "Clinique du Léman" in result["html_full"]
        assert "score" in result["html_full"].lower()
        assert "CORTEX LEMAN" in result["html_full"]

    def test_compliance_report_score_animation(self, mcp):
        """Le score est animé avec un counter GSAP"""
        req = {
            "jsonrpc": "2.0", "id": 21, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "compliance_report",
                "company_name": "Test",
                "vertical": "banque",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert "innerText" in result["html_full"]  # counter animation


# ── Render ──

class TestHyperFrameRender:
    """Tests du rendu."""

    def test_render_without_ffmpeg(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 30, "method": "tools/call",
            "params": {"name": "hyperframe_render", "arguments": {
                "composition_id": "sp-test123",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        # Soit render ready, soit unavailable
        assert result["status"] in ["ready", "error", "render_unavailable"]
        assert result["composition_id"] == "sp-test123"


# ── Templates Catalog ──

class TestHyperFrameTemplates:
    """Tests du catalogue de templates."""

    def test_list_all_templates(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 40, "method": "tools/call",
            "params": {"name": "hyperframe_templates", "arguments": {}},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["total"] == 5
        template_ids = [t["id"] for t in result["templates"]]
        assert "lead_card" in template_ids
        assert "listicle" in template_ids
        assert "compliance_report" in template_ids
        assert "cta_only" in template_ids
        assert "custom" in template_ids

    def test_templates_with_vertical(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 41, "method": "tools/call",
            "params": {"name": "hyperframe_templates", "arguments": {
                "vertical": "avocat",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["vertical"] == "avocat"
        # Les templates pour avocat devraient être recommended
        for t in result["templates"]:
            assert "recommended" in t

    def test_templates_include_cortex_colors(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 42, "method": "tools/call",
            "params": {"name": "hyperframe_templates", "arguments": {}},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert "colors" in result
        assert result["colors"]["primary"] == "#0d9488"


# ── SocialPulse Integration ──

class TestHyperFrameSocialPulse:
    """Tests d'intégration SocialPulse."""

    def test_compose_sets_platform(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 50, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "lead_card",
                "company_name": "Test",
                "vertical": "comptable",
                "risk_type": "Test",
                "format": "9:16",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["socialpulse_use"]["platform"] == "instagram"
        assert result["socialpulse_use"]["vertical"] == "comptable"

    def test_compose_landscape_for_linkedin(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 51, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "lead_card",
                "company_name": "Test",
                "vertical": "banque",
                "risk_type": "Test",
                "format": "16:9",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["socialpulse_use"]["platform"] == "linkedin"
        assert "1920px" in result["html_full"]


# ── JSON-RPC Compliance ──

class TestHyperFrameJsonRpc:
    """Les tools HyperFrame respectent JSON-RPC 2.0."""

    def test_compose_response_format(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 60, "method": "tools/call",
            "params": {"name": "hyperframe_compose", "arguments": {
                "template": "lead_card",
                "company_name": "Test",
                "vertical": "comptable",
                "risk_type": "Test",
            }},
        }
        resp = mcp.handle_request(req)
        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 60
        assert "result" in resp
        assert "content" in resp["result"]
        assert resp["result"]["content"][0]["type"] == "text"

    def test_unknown_hf_tool(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 61, "method": "tools/call",
            "params": {"name": "hyperframe_nonexistent", "arguments": {}},
        }
        resp = mcp.handle_request(req)
        assert "error" in resp
