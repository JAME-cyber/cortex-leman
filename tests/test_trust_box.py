"""
Tests pour le Trust Box API — Phase 1A
Couche exposition produit du Médiateur
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from api.main import app
    return TestClient(app)


@pytest.fixture(scope="module")
def auth_headers(client):
    """Obtenir un token JWT valide"""
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@cortex-leman.com",
        "password": "C0rt3xL3m4n!"
    })
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── /trust-box/status ──────────────────────────────────────

class TestTrustBoxStatus:
    def test_status_public(self, client):
        """Le statut du Trust Box est accessible sans auth"""
        resp = client.get("/trust-box/status")
        assert resp.status_code == 200
        data = resp.json()
        
        assert data["name"] == "Cortex Leman Trust Box"
        assert data["status"] == "active"
        assert data["philosophy"] == "Déterministe là où il faut. Intelligent là où on peut."
        assert data["architecture"]["decision_engine"] == "JsonLogic (0% LLM)"
        assert "block" in data["architecture"]["actions"]
        assert "freeze" in data["architecture"]["actions"]
        assert isinstance(data["metrics"]["total_rules"], int)
        assert isinstance(data["metrics"]["verticals"], int)
        assert isinstance(data["verticals"], list)

    def test_status_has_serment(self, client):
        """Le statut inclut le serment"""
        resp = client.get("/trust-box/status")
        data = resp.json()
        assert "serment" in data
        assert len(data["serment"]) > 0


# ── /trust-box/serment ─────────────────────────────────────

class TestTrustBoxSerment:
    def test_serment_public(self, client):
        """Le serment est accessible sans auth"""
        resp = client.get("/trust-box/serment")
        assert resp.status_code == 200
        data = resp.json()
        
        assert "serment" in data
        principes = data["serment"]["principes"]
        assert len(principes) == 6
        
        # Vérifier les 6 principes
        titres = [p["titre"] for p in principes]
        assert "Déterminisme critique" in titres
        assert "Gel préventif" in titres
        assert "Arbitrage humain" in titres
        assert "Transparence totale" in titres
        assert "Mode dégradé" in titres
        assert "Conformité by design" in titres
    
    def test_serment_has_implementation(self, client):
        """Chaque principe a une implémentation technique"""
        resp = client.get("/trust-box/serment")
        data = resp.json()
        
        for principe in data["serment"]["principes"]:
            assert "implementation" in principe
            assert len(principe["implementation"]) > 0


# ── /trust-box/rules ───────────────────────────────────────

class TestTrustBoxRules:
    def test_rules_all_verticals(self, client):
        """Lister toutes les verticales"""
        resp = client.get("/trust-box/rules")
        assert resp.status_code == 200
        data = resp.json()
        
        assert "verticals" in data
        assert data["total_rules"] > 0
        assert len(data["verticals"]) >= 5  # Au moins 5 verticales
    
    def test_rules_specific_vertical(self, client):
        """Lister les règles d'une verticale"""
        resp = client.get("/trust-box/rules?vertical=comptable")
        assert resp.status_code == 200
        data = resp.json()
        
        assert data["vertical"] == "comptable"
        assert data["total"] >= 7  # Au moins 7 règles comptable
        assert len(data["rules"]) == data["total"]
        
        # Chaque règle a les bons champs
        for rule in data["rules"]:
            assert "id" in rule
            assert "name" in rule
            assert "severity" in rule
            assert "action" in rule
            assert "message" in rule
            # La condition n'est PAS exposée (sécurité)
    
    def test_rules_no_condition_exposed(self, client):
        """Les conditions JsonLogic ne sont pas exposées (sécurité)"""
        resp = client.get("/trust-box/rules?vertical=comptable")
        data = resp.json()
        
        for rule in data["rules"]:
            assert "condition" not in rule
    
    def test_rules_unknown_vertical(self, client):
        """Verticale inconnue retourne vide"""
        resp = client.get("/trust-box/rules?vertical=inconnu")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0


# ── /trust-box/evaluate ────────────────────────────────────

class TestTrustBoxEvaluate:
    def test_evaluate_approved(self, client, auth_headers):
        """Contexte clean → APPROVED"""
        resp = client.post("/trust-box/evaluate", json={
            "vertical": "comptable",
            "context": {
                "action": {"type": "consultation"},
                "payload": {"montant": 100},
            }
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        
        assert data["vertical"] == "comptable"
        assert data["decision"] == "APPROVED"
        assert data["rules_triggered"] == 0
    
    def test_evaluate_blocked(self, client, auth_headers):
        """Décision fiscale sans validation humaine → au moins un trigger"""
        resp = client.post("/trust-box/evaluate", json={
            "vertical": "comptable",
            "context": {
                "action": {"type": "decision_fiscale"},
                "human_validated": False,
            }
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        
        # La règle comptable-001 doit se déclencher
        assert data["rules_triggered"] >= 1
        assert data["decision"] in ("FROZEN", "BLOCKED", "ARBITRATION")
    
    def test_evaluate_large_amount(self, client, auth_headers):
        """Montant > 10K → arbitrage"""
        resp = client.post("/trust-box/evaluate", json={
            "vertical": "comptable",
            "context": {
                "action": {"type": "virement"},
                "payload": {"montant": 15000},
            }
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        
        # comptable-003 ou comptable-006
        assert data["rules_triggered"] >= 1
    
    def test_evaluate_no_vertical(self, client, auth_headers):
        """Sans vertical → 400"""
        resp = client.post("/trust-box/evaluate", json={
            "context": {}
        }, headers=auth_headers)
        assert resp.status_code == 400
    
    def test_evaluate_requires_auth(self, client):
        """Sans auth → 401"""
        resp = client.post("/trust-box/evaluate", json={
            "vertical": "comptable",
            "context": {}
        })
        assert resp.status_code == 401


# ── /trust-box/simulate ────────────────────────────────────

class TestTrustBoxSimulate:
    def test_simulate_approved(self, client, auth_headers):
        """Simulation action clean → APPROVED"""
        resp = client.post("/trust-box/simulate", json={
            "vertical": "comptable",
            "action_type": "consultation",
            "payload": {"montant": 500}
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        
        assert data["simulation"] is True
        assert data["verdict"] == "APPROVED"
        assert data["explanation"]
    
    def test_simulate_frozen_decision(self, client, auth_headers):
        """Simulation décision fiscale → FROZEN"""
        resp = client.post("/trust-box/simulate", json={
            "vertical": "comptable",
            "action_type": "decision_fiscale",
            "payload": {"human_validated": False}
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        
        assert data["verdict"] == "FROZEN"
        assert "gel" in data["explanation"].lower() or "gèle" in data["explanation"].lower() or "freeze" in data["explanation"].lower()
    
    def test_simulate_block_data_transfer(self, client, auth_headers):
        """Simulation transfert CH → BLOCKED"""
        resp = client.post("/trust-box/simulate", json={
            "vertical": "comptable",
            "action_type": "data_transfer",
            "payload": {"data_residency": "CH"}
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        
        assert data["verdict"] == "BLOCKED"
    
    def test_simulate_no_params(self, client, auth_headers):
        """Params manquants → 400"""
        resp = client.post("/trust-box/simulate", json={
            "vertical": "comptable",
        }, headers=auth_headers)
        assert resp.status_code == 400


# ── /trust-box/conflicts ───────────────────────────────────

class TestTrustBoxConflicts:
    def test_conflicts_requires_auth(self, client):
        """Conflits nécessite auth"""
        resp = client.get("/trust-box/conflicts")
        assert resp.status_code == 401
    
    def test_conflicts_empty(self, client, auth_headers):
        """Pas de conflits en mode test"""
        resp = client.get("/trust-box/conflicts", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "active_conflicts" in data
        assert isinstance(data["conflicts"], list)


# ── /trust-box/audit-trail ─────────────────────────────────

class TestTrustBoxAuditTrail:
    def test_audit_trail_requires_auth(self, client):
        """Audit trail nécessite auth"""
        resp = client.get("/trust-box/audit-trail")
        assert resp.status_code == 401
    
    def test_audit_trail_returns_events(self, client, auth_headers):
        """Audit trail retourne des événements"""
        resp = client.get("/trust-box/audit-trail", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "events" in data
        assert "integrity" in data
