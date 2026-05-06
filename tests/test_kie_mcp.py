"""
Tests des tools Kie.ai dans le MCP Cortex Server.
Pattern: simulation quand KIE_API_KEY absente, intégration quand présente.
"""
import json
import pytest


@pytest.fixture
def mcp():
    from core.integrations.mcp_cortex_server import CortexMCPServer
    return CortexMCPServer()


# ── Tool Discovery ──

class TestKieToolDiscovery:
    """Les 4 tools Kie doivent être déclarés dans le MCP."""

    def test_kie_video_tool_registered(self, mcp):
        names = [t["name"] for t in mcp.tools]
        assert "kie_generate_video" in names

    def test_kie_image_tool_registered(self, mcp):
        names = [t["name"] for t in mcp.tools]
        assert "kie_generate_image" in names

    def test_kie_music_tool_registered(self, mcp):
        names = [t["name"] for t in mcp.tools]
        assert "kie_generate_music" in names

    def test_kie_lead_card_tool_registered(self, mcp):
        names = [t["name"] for t in mcp.tools]
        assert "kie_lead_card" in names

    def test_total_tool_count(self, mcp):
        """25 tools: 18 originaux + 4 Kie.ai + 3 HyperFrame"""
        assert len(mcp.tools) == 25

    def test_kie_video_schema_has_required_prompt(self, mcp):
        tool = next(t for t in mcp.tools if t["name"] == "kie_generate_video")
        assert "prompt" in tool["inputSchema"]["required"]

    def test_kie_video_has_model_choices(self, mcp):
        tool = next(t for t in mcp.tools if t["name"] == "kie_generate_video")
        model_enum = tool["inputSchema"]["properties"]["model"]["enum"]
        assert "veo-3.1" in model_enum
        assert "veo-3.1-fast" in model_enum
        assert "runway-aleph" in model_enum


# ── Simulation Mode (KIE_API_KEY absente) ──

class TestKieSimulation:
    """Sans clé API, les tools retournent des simulations."""

    def test_video_simulation(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "kie_generate_video", "arguments": {
                "prompt": "Drone shot of Geneva lake at sunset",
                "model": "veo-3.1-fast",
                "duration": 5,
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["tool"] == "kie_generate_video"
        assert result["status"] == "simulated"
        assert result["status"] == "simulated"
        assert "KIE_API_KEY" in result["message"]

    def test_image_simulation(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "kie_generate_image", "arguments": {
                "prompt": "Infographie conformité IA cabinet comptable",
                "model": "4o-image",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["tool"] == "kie_generate_image"
        assert result["status"] == "simulated"

    def test_music_simulation(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "kie_generate_music", "arguments": {
                "prompt": "Corporate background music, uplifting, 30 seconds",
                "instrumental": True,
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["tool"] == "kie_generate_music"
        assert result["status"] == "simulated"

    def test_lead_card_simulation(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "kie_lead_card", "arguments": {
                "company_name": "Cabinet Dupont",
                "vertical": "comptable",
                "signal_type": "Chatbot fiscal sans consentement",
                "contact_name": "Marie Dupont",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["lead_card"]["company"] == "Cabinet Dupont"
        assert result["lead_card"]["vertical"] == "comptable"
        assert result["lead_card"]["risk"] == "Chatbot fiscal sans consentement"
        assert "visual" in result
        assert "email" in result
        assert result["visual"]["status"] == "simulation_active"

    def test_simulation_cost_estimate(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 5, "method": "tools/call",
            "params": {"name": "kie_generate_video", "arguments": {
                "prompt": "Test prompt",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert "cost_estimate" in result
        assert "credits" in result["cost_estimate"]
        assert result["cost_estimate"]["usd"] > 0

    def test_simulation_shows_alternative(self, mcp):
        """Simulation doit mentionner Higgsfield comme alternative"""
        req = {
            "jsonrpc": "2.0", "id": 6, "method": "tools/call",
            "params": {"name": "kie_generate_video", "arguments": {
                "prompt": "Test",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["integration"]["alternative_to"] == "Higgsfield MCP"
        assert result["integration"]["mcp"] is True


# ── Lead Card Scenarios ──

class TestKieLeadCardScenarios:
    """Tests des différents scénarios de lead card."""

    @pytest.mark.parametrize("style", ["infographic", "thumbnail", "social_card"])
    def test_lead_card_styles(self, mcp, style):
        req = {
            "jsonrpc": "2.0", "id": 10, "method": "tools/call",
            "params": {"name": "kie_lead_card", "arguments": {
                "company_name": "Test Corp",
                "vertical": "startup",
                "signal_type": "Données IA non chiffrées",
                "style": style,
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["lead_card"]["style"] == style

    @pytest.mark.parametrize("vertical", [
        "comptable", "avocat", "sante", "banque", "startup", "rh"
    ])
    def test_lead_card_all_verticals(self, mcp, vertical):
        req = {
            "jsonrpc": "2.0", "id": 11, "method": "tools/call",
            "params": {"name": "kie_lead_card", "arguments": {
                "company_name": f"Cabinet {vertical}",
                "vertical": vertical,
                "signal_type": "Test risk",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert result["lead_card"]["vertical"] == vertical
        assert result["email"]["subject"]  # sujet non vide

    def test_lead_card_email_subject_contains_risk(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 12, "method": "tools/call",
            "params": {"name": "kie_lead_card", "arguments": {
                "company_name": "Banque Leman",
                "vertical": "banque",
                "signal_type": "Modèle scoring sans DPIA",
            }},
        }
        resp = mcp.handle_request(req)
        result = json.loads(resp["result"]["content"][0]["text"])
        assert "Modèle scoring sans DPIA" in result["email"]["subject"]


# ── JSON-RPC Compliance ──

class TestKieJsonRpc:
    """Les tools Kie respectent le protocole JSON-RPC 2.0."""

    def test_unknown_kie_tool_returns_error(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 20, "method": "tools/call",
            "params": {"name": "kie_nonexistent", "arguments": {}},
        }
        resp = mcp.handle_request(req)
        assert "error" in resp
        assert resp["error"]["code"] == -32602

    def test_video_response_format(self, mcp):
        req = {
            "jsonrpc": "2.0", "id": 21, "method": "tools/call",
            "params": {"name": "kie_generate_video", "arguments": {
                "prompt": "Test",
            }},
        }
        resp = mcp.handle_request(req)
        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 21
        assert "result" in resp
        assert "content" in resp["result"]
        assert resp["result"]["content"][0]["type"] == "text"
