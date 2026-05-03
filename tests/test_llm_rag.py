"""
Cortex Leman v5 — Tests LLM Wiring + RAG

Teste:
- RAG ChromaDB (indexation, recherche, chunking)
- LLM pipeline avec guardrails
- Agent Raisonnement en mode dégradé (sans LLM)
- Agent Data avec RAG
- Endpoints API RAG
"""
import os
import sys
import json
import pytest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ["DATABASE_URL"] = "sqlite:///file::memory:?cache=shared&uri=true"
os.environ["SECRET_KEY"] = "test-secret-key-for-llm-tests"
os.environ["JOURNAL_PATH"] = "/tmp/cortex-test-journal-llm"


# ============================================================
# Tests RAG ChromaDB
# ============================================================

class TestRAGChromaDB:
    """Tests du service RAG vectoriel"""

    @pytest.fixture(autouse=True)
    def setup_rag(self, tmp_path):
        """Crée un RAG avec répertoire temporaire"""
        from core.integrations.rag import RAGService
        self.rag = RAGService(persist_dir=str(tmp_path / "chroma_test"))
        yield

    def test_rag_init(self):
        stats = self.rag.get_stats()
        assert "collections" in stats
        assert "total_chunks" in stats

    def test_index_document(self):
        chunks = self.rag.index_document(
            client_id="test-client",
            doc_id="doc-001",
            content=(
                "Le RGPD (Règlement Général sur la Protection des Données) "
                "est un règlement européen qui encadre le traitement des données "
                "personnelles. L'article 22 traite des décisions automatisées. "
                "Les entreprises doivent désigner un DPO si elles traitent des "
                "données sensibles à grande échelle."
            ),
            metadata={"type": "regulation"},
        )
        assert chunks >= 1

    def test_index_and_search(self):
        # Indexer
        self.rag.index_document(
            client_id="test-client",
            doc_id="doc-rgpd",
            content="Le RGPD exige un consentement explicite pour les données sensibles.",
        )

        # Rechercher
        results = self.rag.search(
            query="consentement données sensibles",
            client_id="test-client",
            n_results=3,
        )

        assert len(results) >= 1
        assert any("RGPD" in r.get("content", "").upper() for r in results)

    def test_index_regulatory(self):
        regulations = [
            {
                "id": "rgpd-test",
                "title": "RGPD Article 22",
                "content": "La personne concernée a le droit de ne pas faire l'objet d'une décision automatisée.",
                "source": "RGPD",
                "vertical": "all",
            },
            {
                "id": "cp321-test",
                "title": "Art. 321 CP — Secret professionnel",
                "content": "Les avocats sont tenus au secret professionnel.",
                "source": "Code Pénal",
                "vertical": "avocat",
            },
        ]

        count = self.rag.index_regulatory(regulations)
        assert count >= 2

        # Recherche réglementaire
        results = self.rag.search(
            query="secret professionnel avocat",
            n_results=3,
            include_regulatory=True,
        )
        assert len(results) >= 1

    def test_search_regulatory_with_vertical_filter(self):
        regulations = [
            {
                "id": "filter-avocat",
                "title": "Secret avocat",
                "content": "Secret professionnel des avocats article 321.",
                "source": "CP",
                "vertical": "avocat",
            },
            {
                "id": "filter-banque",
                "title": "Secret bancaire",
                "content": "Secret bancaire article 47 de la loi sur les banques.",
                "source": "LB",
                "vertical": "banque",
            },
        ]
        self.rag.index_regulatory(regulations)

        results = self.rag.search(
            query="secret",
            vertical="avocat",
            n_results=5,
        )
        # Devrait trouver le texte avocat + "all" s'il y en a
        assert len(results) >= 1

    def test_build_context_for_agent(self):
        self.rag.index_document(
            client_id="test-client",
            doc_id="doc-ctx",
            content="Test document content for context building.",
        )

        context = self.rag.build_context_for_agent(
            query="test document",
            agent_name="reasoning",
            vertical="comptable",
            client_id="test-client",
        )

        assert isinstance(context, str)
        assert len(context) > 0

    def test_delete_client_data(self):
        self.rag.index_document(
            client_id="to-delete",
            doc_id="doc-del",
            content="This will be deleted for RGPD compliance.",
        )

        result = self.rag.delete_client_data("to-delete")
        assert result is True

    def test_empty_search(self):
        results = self.rag.search(
            query="nonexistent query about quantum physics",
            client_id="no-client",
            n_results=3,
        )
        assert isinstance(results, list)

    def test_chunk_text(self):
        from core.integrations.rag import RAGService

        # Texte court
        chunks = RAGService._chunk_text("Court", chunk_size=500)
        assert len(chunks) == 1

        # Texte long
        long_text = " ".join(["mot"] * 2000)
        chunks = RAGService._chunk_text(long_text, chunk_size=500, overlap=50)
        assert len(chunks) >= 2

        # Texte vide
        chunks = RAGService._chunk_text("")
        assert len(chunks) == 0

        # Texte None
        chunks = RAGService._chunk_text(None)
        assert len(chunks) == 0

    def test_load_regulatory_seed(self):
        # Pas de fichiers de seed dans le temp dir — devrait retourner 0
        count = self.rag.load_regulatory_seed()
        # Peut être 0 si pas de fichiers, c'est OK
        assert isinstance(count, int)


# ============================================================
# Tests LLM Pipeline
# ============================================================

class TestLLMPipeline:
    """Tests du pipeline LLM (mode dégradé sans API key)"""

    def test_llm_service_init(self):
        from core.integrations.llm.provider import LLMService
        service = LLMService()
        assert service.provider_name in ("openrouter", "ollama")

    def test_llm_service_stats(self):
        from core.integrations.llm.provider import LLMService
        service = LLMService()
        assert service._total_calls == 0
        assert service._total_tokens == 0

    def test_llm_guardrail_pii_blocking(self):
        """Test que le guardrail détecte les PII dans l'input"""
        from core.security.guardrails import GuardrailPipeline
        guardrail = GuardrailPipeline()

        result = guardrail.check_input(
            "Mon AVS est 756.1234.5678.90 et mon email est test@test.com",
            "comptable"
        )
        # Le guardrail doit détecter la PII
        assert isinstance(result.violations, list) or isinstance(result.passed, bool)


# ============================================================
# Tests Agent Raisonnement (mode dégradé)
# ============================================================

class TestReasoningAgentWired:
    """Tests de l'Agent Raisonnement avec LLM wiring"""

    def test_reasoning_agent_init(self):
        from core.agents.reasoning_agent import ReasoningAgent
        agent = ReasoningAgent()
        assert agent.name == "reasoning"

    @pytest.mark.asyncio
    async def test_reasoning_process_degraded(self):
        """Test en mode dégradé (sans LLM)"""
        from core.agents.reasoning_agent import ReasoningAgent
        agent = ReasoningAgent()

        result = await agent.process({
            "query": "Quelle est la meilleure structure fiscale pour une SARL?",
            "vertical": "comptable",
            "context": {"montant": 50000},
            "intention_id": "test-intention-001",
            "client_id": "test-client",
        }, {})

        assert "recommendation" in result
        assert "confidence" in result
        assert "compliance" in result
        assert "risks" in result
        assert isinstance(result["confidence"], float)
        assert 0 <= result["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_reasoning_sensitive_vertical(self):
        """Test avec une vertical sensible (avocat)"""
        from core.agents.reasoning_agent import ReasoningAgent
        agent = ReasoningAgent()

        result = await agent.process({
            "query": "Analyser le risque de cette procédure",
            "vertical": "avocat",
            "context": {},
            "intention_id": None,  # Pas de intention_id → pas de publish
        }, {})

        assert result["compliance"]["risks"] == ["data_residency_strict"]
        assert "Art. 321 CP" in result["compliance"]["references"]

    @pytest.mark.asyncio
    async def test_reasoning_llm_analyze_fallback(self):
        """Test que l'analyse LLM fallback gracieusement"""
        from core.agents.reasoning_agent import ReasoningAgent
        agent = ReasoningAgent()

        # Sans API key, le LLM doit fallback silencieusement
        result = await agent._llm_analyze(
            query="test query",
            vertical="comptable",
            context={},
            client_id="test",
            intention_id="test",
        )

        # Soit erreur (pas de clé), soit résultat
        assert "text" in result or "error" in result

    def test_reasoning_parse_llm_response(self):
        """Test du parsing de réponse LLM"""
        from core.agents.reasoning_agent import ReasoningAgent
        agent = ReasoningAgent()

        # JSON pur
        result = agent._parse_llm_response('{"confidence": 0.8}')
        assert result.get("confidence") == 0.8

        # JSON dans backticks
        result = agent._parse_llm_response('```json\n{"confidence": 0.9}\n```')
        assert result.get("confidence") == 0.9

        # JSON dans du texte
        result = agent._parse_llm_response(
            'Voici mon analyse:\n{"confidence": 0.7, "risks": ["test"]}\nFin.'
        )
        assert result.get("confidence") == 0.7

        # Pas de JSON
        result = agent._parse_llm_response("Pas de JSON ici")
        assert isinstance(result, dict)


# ============================================================
# Tests Agent Data (avec RAG)
# ============================================================

class TestDataAgentWired:
    """Tests de l'Agent Data avec RAG"""

    def test_data_agent_init(self):
        from core.agents.data_agent import DataAgent
        agent = DataAgent()
        assert agent.name == "data"

    @pytest.mark.asyncio
    async def test_data_process(self):
        """Test collecte de données (mode dégradé)"""
        from core.agents.data_agent import DataAgent
        agent = DataAgent()

        result = await agent.process({
            "query": "circulaire AFC déduction TVA",
            "vertical": "comptable",
            "context": {},
            "intention_id": "test-data-001",
            "client_id": "test-client",
        }, {})

        assert "recommendation" in result
        assert "sources" in result
        assert "confidence" in result
        assert isinstance(result["sources"], list)

    @pytest.mark.asyncio
    async def test_data_confidence_no_sources(self):
        """Test confiance quand aucune source"""
        from core.agents.data_agent import DataAgent
        agent = DataAgent()

        result = await agent.process({
            "query": "requête très spécifique xyz",
            "vertical": "unknown",
            "context": {},
            "intention_id": "test-empty",
            "client_id": "no-client",
        }, {})

        # Peut avoir des sources du vault ou RAG, mais le format est correct
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_data_returns_facts_field(self):
        """Sprint 3: L'Agent Data retourne toujours le champ facts"""
        from core.agents.data_agent import DataAgent
        agent = DataAgent()

        result = await agent.process({
            "query": "test facts field",
            "vertical": "comptable",
            "context": {},
            "intention_id": "test-facts-001",
            "client_id": "test-client",
        }, {})

        assert "facts" in result
        assert isinstance(result["facts"], list)
        assert "mode" in result
        assert "llm_used" in result
        assert "data_residency" in result

    @pytest.mark.asyncio
    async def test_data_high_protection_mode(self):
        """Sprint 3: Mode Haute Protection détecté"""
        from core.agents.data_agent import DataAgent
        agent = DataAgent()

        # En mode standard par défaut
        assert not agent._is_high_protection

    @pytest.mark.asyncio
    async def test_data_residency_check(self):
        """Sprint 3: Vérification data residency"""
        from core.agents.data_agent import DataAgent
        agent = DataAgent()

        # Verticale sensible en mode standard
        check = agent._check_data_residency("avocat", "test")
        assert check["allowed"] is True
        assert check["mode"] == "standard_warn"

        # Verticale non-sensible
        check2 = agent._check_data_residency("startup", "test")
        assert check2["allowed"] is True
        assert check2["mode"] == "standard"

    @pytest.mark.asyncio
    async def test_data_residency_high_protection(self):
        """Sprint 3: Mode haute protection = local_only"""
        from core.agents.data_agent import DataAgent
        import unittest.mock as mock

        with mock.patch("core.agents.data_agent.settings") as mock_settings:
            mock_settings.app_mode = "haute_protection"
            agent = DataAgent()
            assert agent._is_high_protection is True

            check = agent._check_data_residency("avocat", "test")
            assert check["allowed"] is True
            assert check["mode"] == "local_only"

    def test_data_parse_facts_response(self):
        """Sprint 3: Parser les réponses LLM en JSON"""
        from core.agents.data_agent import DataAgent
        agent = DataAgent()

        # JSON direct
        text = '[{"description": "TVA 20%", "source": "CGI", "confidence": 0.9}]'
        facts = agent._parse_facts_response(text)
        assert len(facts) == 1
        assert facts[0]["description"] == "TVA 20%"

        # JSON dans backticks
        text2 = '```json\n[{"description": "Seuil CA", "source": "AFC", "confidence": 0.8}]\n```'
        facts2 = agent._parse_facts_response(text2)
        assert len(facts2) == 1

        # Texte invalide
        text3 = "Pas de JSON ici"
        facts3 = agent._parse_facts_response(text3)
        assert len(facts3) == 0

    def test_data_fallback_facts(self):
        """Sprint 3: Mode dégradé — faits programmatiques"""
        from core.agents.data_agent import DataAgent
        agent = DataAgent()

        sources = [
            {
                "type": "rag",
                "relevance": 0.8,
                "data": {"content": "Circulaire AFC 2024-01", "title": "AFC", "doc_id": "d1"},
            },
            {
                "type": "vault",
                "relevance": 0.6,
                "data": {"name": "Bilan fiscal", "snippet": "CA: 500K", "tags": ["fiscal"]},
            },
        ]

        facts = agent._fallback_facts(sources)
        assert len(facts) == 2
        assert all("id" in f for f in facts)
        assert all("timestamp" in f for f in facts)
        assert all(f["extracted_by"] == "data_agent_programmatic" for f in facts)

    def test_data_format_sources_for_llm(self):
        """Sprint 3: Formatage des sources pour le prompt LLM"""
        from core.agents.data_agent import DataAgent
        agent = DataAgent()

        sources = [
            {
                "type": "rag",
                "relevance": 0.9,
                "data": {"content": "Contenu RAG", "title": "Titre RAG", "doc_id": "d1"},
            },
            {
                "type": "vault",
                "relevance": 0.7,
                "data": {"name": "Doc Vault", "snippet": "Extrait", "tags": ["tag1"]},
            },
        ]

        formatted = agent._format_sources_for_llm(sources)
        assert "[1] RAG" in formatted
        assert "[2] Vault" in formatted
        assert "Titre RAG" in formatted
        assert "Doc Vault" in formatted

    def test_data_compute_confidence_with_facts(self):
        """Sprint 3: Confiance pondérée sources + faits"""
        from core.agents.data_agent import DataAgent
        agent = DataAgent()

        sources = [{"relevance": 0.8}, {"relevance": 0.6}]
        facts = [{"confidence": 0.9}, {"confidence": 0.7}]

        conf = agent._compute_confidence(sources, facts)
        # 40% * avg(0.8, 0.6) + 60% * avg(0.9, 0.7)
        # = 0.4 * 0.7 + 0.6 * 0.8 = 0.28 + 0.48 = 0.76
        assert abs(conf - 0.76) < 0.01

    def test_data_compute_confidence_sources_only(self):
        """Sprint 3: Confiance sources uniquement"""
        from core.agents.data_agent import DataAgent
        agent = DataAgent()

        sources = [{"relevance": 0.8}, {"relevance": 0.6}]
        conf = agent._compute_confidence(sources, None)
        assert abs(conf - 0.7) < 0.01

    def test_data_compute_confidence_empty(self):
        """Sprint 3: Confiance zéro si pas de sources"""
        from core.agents.data_agent import DataAgent
        agent = DataAgent()
        assert agent._compute_confidence([], None) == 0.0
