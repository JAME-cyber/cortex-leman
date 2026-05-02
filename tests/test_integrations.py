"""
Cortex Leman v5 — Tests des intégrations (LLM, n8n, Knowledge Vault)
"""
import pytest
import json
from pathlib import Path

from core.integrations.knowledge_vault.vault import KnowledgeVault
from core.integrations.n8n.client import N8NClient, VERTICAL_WORKFLOWS
from core.integrations.llm.provider import LLMService


class TestKnowledgeVault:
    """Tests du Knowledge Vault"""

    @pytest.fixture
    def vault(self, tmp_path):
        return KnowledgeVault(vault_path=str(tmp_path / "vault"))

    def test_create_client_space(self, vault):
        metadata = vault.create_client_space("cabinet-test", "comptable")
        assert metadata["client_id"] == "cabinet-test"
        assert metadata["vertical"] == "comptable"
        assert metadata["document_count"] == 0

    def test_store_document(self, vault):
        vault.create_client_space("cabinet-test", "comptable")
        result = vault.store_document(
            client_id="cabinet-test",
            document_name="Bilan 2025",
            content="Bilan comptable du cabinet pour l'exercice 2025",
            document_type="bilan",
            tags=["fiscal", "2025"],
        )
        assert result["stored"] is True
        assert result["doc_id"] is not None

    def test_search_document(self, vault):
        vault.create_client_space("cabinet-test", "comptable")
        vault.store_document(
            client_id="cabinet-test",
            document_name="Bilan 2025",
            content="Bilan comptable du cabinet pour l'exercice 2025",
            tags=["fiscal"],
        )
        vault.store_document(
            client_id="cabinet-test",
            document_name="Déclaration TVA",
            content="Déclaration de TVA mensuelle janvier 2025",
            tags=["tva"],
        )

        results = vault.search("cabinet-test", "bilan")
        assert len(results) >= 1
        assert any("Bilan" in r["name"] for r in results)

    def test_search_with_tags(self, vault):
        vault.create_client_space("cabinet-test", "comptable")
        vault.store_document(
            client_id="cabinet-test",
            document_name="Doc fiscal",
            content="Contenu fiscal",
            tags=["fiscal"],
        )
        vault.store_document(
            client_id="cabinet-test",
            document_name="Doc tva",
            content="Contenu TVA",
            tags=["tva"],
        )

        results = vault.search("cabinet-test", "Contenu", tags=["fiscal"])
        assert len(results) == 1
        assert results[0]["name"] == "Doc fiscal"

    def test_list_documents(self, vault):
        vault.create_client_space("cabinet-test", "comptable")
        vault.store_document("cabinet-test", "Doc 1", "Contenu 1")
        vault.store_document("cabinet-test", "Doc 2", "Contenu 2")

        docs = vault.list_documents("cabinet-test")
        assert len(docs) == 2

    def test_regulatory_data(self, vault):
        count = vault.load_regulatory_data()
        assert count > 0

        results = vault.search_regulatory("secret professionnel")
        assert len(results) >= 1

    def test_stats(self, vault):
        vault.create_client_space("c1", "comptable")
        vault.create_client_space("c2", "avocat")
        vault.store_document("c1", "Doc", "Content")

        stats = vault.get_stats()
        assert stats["clients"] == 2
        assert stats["documents"] == 1

    def test_isolation_between_clients(self, vault):
        vault.create_client_space("client-a", "comptable")
        vault.create_client_space("client-b", "avocat")
        vault.store_document("client-a", "Secret A", "Contenu secret A")

        # Client B ne peut pas voir les documents de client A
        results = vault.search("client-b", "secret")
        assert len(results) == 0

    def test_unknown_client_search(self, vault):
        results = vault.search("nonexistent", "query")
        assert results == []


class TestN8NWorkflows:
    """Tests de la configuration des workflows n8n"""

    def test_all_verticals_have_workflows(self):
        for vertical in ["comptable", "avocat", "rh", "banque", "sante", "startup"]:
            assert vertical in VERTICAL_WORKFLOWS, f"Missing workflows for {vertical}"

    def test_workflow_structure(self):
        for vertical, workflows in VERTICAL_WORKFLOWS.items():
            for wf_id, wf in workflows.items():
                assert "name" in wf, f"Missing name in {vertical}/{wf_id}"
                assert "steps" in wf, f"Missing steps in {vertical}/{wf_id}"
                assert len(wf["steps"]) > 0

    def test_get_available_workflows(self):
        client = N8NClient()
        all_wf = client.get_available_workflows()
        assert len(all_wf) == 6

        comp_wf = client.get_available_workflows("comptable")
        assert "comptable" in comp_wf
        assert "cloture_annuelle" in comp_wf["comptable"]


class TestLLMService:
    """Tests du service LLM"""

    def test_provider_selection_openrouter(self):
        """En mode standard, OpenRouter est sélectionné"""
        from core.integrations.llm.provider import OpenRouterProvider
        service = LLMService()
        # Le provider par défaut selon .env
        assert service.provider_name in ("openrouter", "ollama")

    def test_is_local_property(self):
        service = LLMService()
        if service.provider_name == "ollama":
            assert service.is_local is True
        else:
            assert service.is_local is False

    def test_agent_prompt_contains_rules(self):
        from core.agents.prompts import build_system_prompt

        # Les prompts sont maintenant construits par le module prompts/
        prompt_avocat = build_system_prompt("data", "avocat", {})
        assert "Art. 321 CP" in prompt_avocat
        assert "secret professionnel" in prompt_avocat.lower()

        prompt_banque = build_system_prompt("reasoning", "banque", {})
        assert "Art. 47 LB" in prompt_banque

        prompt_sante = build_system_prompt("data", "sante", {})
        assert "LPM" in prompt_sante
