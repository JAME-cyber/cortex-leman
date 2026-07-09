"""
Cortex Leman v5 — Tests: Agent Évaluateur, Contract Negotiation, Handoff JSON

Valide les trois modules issus de l'analyse divergente Anthropic.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# ── Handoff JSON ──────────────────────────────────────────────

class TestHandoffJSON:
    """Tests du système de breadcrumbs structurés."""

    def setup_method(self):
        self.tmp_dir = Path("./data/test_handoffs")
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def test_create_handoff(self):
        from core.agents.handoff import HandoffStore, FeatureAttempt, Lesson

        store = HandoffStore(persist_dir=str(self.tmp_dir))
        handoff = store.create(
            intention_id="test-001",
            agent_name="reasoning",
            mission_summary="Analyse fiscale pour client Dupont",
            mission_outcome="success",
            vertical="comptable",
            features=[
                FeatureAttempt(feature="Recherche réglementaire", status="done", tests_pass=True),
                FeatureAttempt(feature="Calcul optimisation", status="done", tests_pass=True),
                FeatureAttempt(feature="Rapport PDF", status="failed", reason="Template manquant"),
            ],
            lessons=[
                Lesson(
                    category="pattern",
                    description="L'API fiscale V2 nécessite un timeout de 30s minimum",
                    applies_to="vertical:comptable",
                ),
            ],
            files_modified=["data/reports/dupont.json"],
            next_steps=["Générer le template PDF", "Envoyer au client"],
        )

        assert handoff.handoff_id
        assert handoff.features_done == 2
        assert handoff.features_failed == 1
        assert len(handoff.lessons_learned) == 1
        assert handoff.mission_outcome == "success"

    def test_get_latest(self):
        from core.agents.handoff import HandoffStore

        store = HandoffStore(persist_dir=str(self.tmp_dir))
        store.create(
            intention_id="test-002",
            agent_name="data",
            mission_summary="Première session",
        )
        store.create(
            intention_id="test-002",
            agent_name="reasoning",
            mission_summary="Deuxième session",
        )

        latest = store.get_latest("test-002")
        assert latest is not None
        assert latest.agent_name == "reasoning"
        assert latest.mission_summary == "Deuxième session"

    def test_list_for_intention(self):
        import shutil
        from core.agents.handoff import HandoffStore

        # Utiliser un dossier unique pour éviter la pollution
        unique_dir = self.tmp_dir / "unique_003"
        if unique_dir.exists():
            shutil.rmtree(unique_dir)

        store = HandoffStore(persist_dir=str(unique_dir))
        store.create(
            intention_id="test-003",
            agent_name="data",
            mission_summary="Session 1",
        )
        store.create(
            intention_id="test-003",
            agent_name="reasoning",
            mission_summary="Session 2",
        )
        store.create(
            intention_id="test-003",
            agent_name="action",
            mission_summary="Session 3",
        )

        handoffs = store.list_for_intention("test-003")
        assert len(handoffs) == 3
        assert handoffs[0].agent_name == "data"
        assert handoffs[2].agent_name == "action"

    def test_generate_handoff_prompt(self):
        from core.agents.handoff import HandoffStore, FeatureAttempt

        store = HandoffStore(persist_dir=str(self.tmp_dir))
        store.create(
            intention_id="test-004",
            agent_name="action",
            mission_summary="Exécution de l'intention fiscale",
            mission_outcome="partial",
            vertical="comptable",
            features=[
                FeatureAttempt(feature="Calcul", status="done", tests_pass=True),
                FeatureAttempt(feature="Rapport", status="failed", reason="PDF error"),
            ],
            next_steps=["Corriger le template PDF"],
            blockers=["Template PDF corrompu"],
        )

        prompt = store.generate_handoff_prompt("test-004")
        assert "CONTEXTE DE REPRISE" in prompt
        assert "action" in prompt
        assert "Template PDF corrompu" in prompt

    def test_persistence_survives_reload(self):
        import shutil
        from core.agents.handoff import HandoffStore

        unique_dir = self.tmp_dir / "unique_005"
        if unique_dir.exists():
            shutil.rmtree(unique_dir)

        store1 = HandoffStore(persist_dir=str(unique_dir))
        store1.create(
            intention_id="test-005",
            agent_name="reasoning",
            mission_summary="Test persistance",
        )

        store2 = HandoffStore(persist_dir=str(unique_dir))
        latest = store2.get_latest("test-005")
        assert latest is not None
        assert latest.mission_summary == "Test persistance"

    def test_empty_handoff(self):
        from core.agents.handoff import HandoffStore

        store = HandoffStore(persist_dir=str(self.tmp_dir))
        assert store.get_latest("nonexistent") is None
        assert store.list_for_intention("nonexistent") == []
        assert store.generate_handoff_prompt("nonexistent") == ""


# ── Contract Negotiation ──────────────────────────────────────

class TestContractNegotiation:
    """Tests du système de négociation de contrats."""

    def setup_method(self):
        self.tmp_dir = Path("./data/test_contracts")
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    @pytest.mark.asyncio
    async def test_basic_negotiation(self):
        from core.agents.contract_negotiator import ContractNegotiator

        negotiator = ContractNegotiator(persist_dir=str(self.tmp_dir))

        contract = await negotiator.negotiate(
            intention_id="contract-001",
            vertical="comptable",
            query="Calculer l'optimisation fiscale pour le client X",
            context={"client_id": "test"},
        )

        assert contract.status == "agreed"
        assert len(contract.criteria) > 0
        # Le Médiateur doit avoir imposé au moins les critères génériques
        mediator_criteria = [c for c in contract.criteria if c.source == "mediator"]
        assert len(mediator_criteria) >= 2  # Au moins les 2 génériques

    @pytest.mark.asyncio
    async def test_vertical_mandatory_criteria(self):
        from core.agents.contract_negotiator import ContractNegotiator

        negotiator = ContractNegotiator(persist_dir=str(self.tmp_dir))

        # Mock LLM to avoid hanging
        with patch.object(negotiator, '_generate_reasoning_proposal', new_callable=AsyncMock) as mock:
            from core.agents.contract_negotiator import ContractCriterion
            mock.return_value = [
                ContractCriterion(
                    description="L'analyse juridique est complète et conforme",
                    test_method="api_call",
                    expected_result="Résponse structurée avec références légales",
                    category="functional",
                    source="reasoning",
                ),
            ]

            contract = await negotiator.negotiate(
                intention_id="contract-002",
                vertical="avocat",
                query="Analyser ce contrat de travail",
                context={"client_id": "test"},
            )

        assert contract.status == "agreed"
        mediator_criteria = [c for c in contract.criteria if c.source == "mediator"]
        descriptions = " ".join(c.description for c in mediator_criteria)
        assert "321 CP" in descriptions or "secret" in descriptions.lower()

    @pytest.mark.asyncio
    async def test_banque_kyc_criterion(self):
        from core.agents.contract_negotiator import ContractNegotiator, ContractCriterion

        negotiator = ContractNegotiator(persist_dir=str(self.tmp_dir))

        with patch.object(negotiator, '_generate_reasoning_proposal', new_callable=AsyncMock) as mock:
            mock.return_value = [
                ContractCriterion(
                    description="Le virement est exécuté conformément aux règles KYC",
                    test_method="api_call",
                    expected_result="Transaction confirmée avec KYC validé",
                    category="functional",
                    source="reasoning",
                ),
            ]

            contract = await negotiator.negotiate(
                intention_id="contract-003",
                vertical="banque",
                query="Exécuter un virement de 20K CHF",
            )

        assert contract.status == "agreed"
        descriptions = " ".join(c.description for c in contract.criteria)
        assert "KYC" in descriptions or "15K" in descriptions

    @pytest.mark.asyncio
    async def test_contract_persistence(self):
        from core.agents.contract_negotiator import ContractNegotiator

        negotiator = ContractNegotiator(persist_dir=str(self.tmp_dir))

        with patch.object(negotiator, '_generate_reasoning_proposal', new_callable=AsyncMock) as mock:
            from core.agents.contract_negotiator import ContractCriterion
            mock.return_value = [
                ContractCriterion(
                    description="Les performances sont analysées objectivement",
                    test_method="api_call",
                    expected_result="Rapport de performance sans biais",
                    category="functional",
                    source="reasoning",
                ),
            ]

            contract = await negotiator.negotiate(
                intention_id="contract-004",
                vertical="rh",
                query="Analyser les performances des employés",
            )

        # Recharger depuis le disque
        loaded = negotiator.get_contract("contract-004")
        assert loaded is not None
        assert loaded.contract_id == contract.contract_id
        assert loaded.status == "agreed"

    def test_criteria_overlap_detection(self):
        from core.agents.contract_negotiator import ContractNegotiator, ContractCriterion

        a = ContractCriterion(
            description="Vérifier la conformité RGPD des données personnelles",
            test_method="journal_check",
            expected_result="Conformité RGPD vérifiée dans le journal",
            category="compliance",
        )
        b = ContractCriterion(
            description="Vérifier la conformité RGPD des données sensibles",
            test_method="journal_check",
            expected_result="Conformité RGPD vérifiée dans le journal",
            category="compliance",
        )
        c = ContractCriterion(
            description="L'API retourne un status 200",
            test_method="api_call",
            expected_result="HTTP 200 OK",
            category="functional",
        )

        assert ContractNegotiator._criteria_overlap(a, b) is True
        assert ContractNegotiator._criteria_overlap(a, c) is False

    @pytest.mark.asyncio
    async def test_vague_criteria_rejected(self):
        """Le Médiateur doit rejeter les critères trop vagues."""
        from core.agents.contract_negotiator import (
            ContractNegotiator, ContractCriterion
        )

        negotiator = ContractNegotiator(persist_dir=str(self.tmp_dir))

        # Proposer un critère trop vague
        vague = ContractCriterion(
            description="Ça marche",  # < 20 chars
            test_method="llm_eval",
            expected_result="OK",  # < 10 chars
            category="functional",
            source="reasoning",
        )

        evaluation = negotiator._mediator_evaluate([vague], "comptable")
        assert not evaluation["accepted"]
        assert len(evaluation["rejected"]) > 0

    @pytest.mark.asyncio
    async def test_all_llm_eval_rejected(self):
        """Le Médiateur doit exiger au moins un test_method déterministe."""
        from core.agents.contract_negotiator import (
            ContractNegotiator, ContractCriterion
        )

        negotiator = ContractNegotiator(persist_dir=str(self.tmp_dir))

        all_llm = [
            ContractCriterion(
                description="L'analyse est correcte selon les standards fiscaux suisses",
                test_method="llm_eval",
                expected_result="L'analyse respecte les normes en vigueur",
                category="functional",
                source="reasoning",
            ),
            ContractCriterion(
                description="La conformité réglementaire est vérifiée par le modèle",
                test_method="llm_eval",
                expected_result="Le modèle confirme la conformité",
                category="compliance",
                source="reasoning",
            ),
        ]

        evaluation = negotiator._mediator_evaluate(all_llm, "comptable")
        # Doit signaler que tout est llm_eval
        assert any("déterministe" in r for r in evaluation["reasons"])


# ── Agent Évaluateur ──────────────────────────────────────────

class TestEvaluatorAgent:
    """Tests de l'agent évaluateur."""

    def test_rubric_default(self):
        from core.agents.evaluator_agent import DEFAULT_RUBRIC

        assert len(DEFAULT_RUBRIC) >= 10
        categories = {c.category for c in DEFAULT_RUBRIC}
        assert "functional" in categories
        assert "security" in categories
        assert "compliance" in categories
        assert "ux" in categories

    def test_rubric_vertical_sante(self):
        from core.agents.evaluator_agent import VERTICAL_RUBRICS

        assert "sante" in VERTICAL_RUBRICS
        sante_criteria = VERTICAL_RUBRICS["sante"]
        descriptions = " ".join(c.description for c in sante_criteria)
        assert "HDS" in descriptions or "patient" in descriptions.lower()

    def test_rubric_vertical_avocat(self):
        from core.agents.evaluator_agent import VERTICAL_RUBRICS

        assert "avocat" in VERTICAL_RUBRICS
        avocat_criteria = VERTICAL_RUBRICS["avocat"]
        descriptions = " ".join(c.description for c in avocat_criteria)
        assert "321 CP" in descriptions or "secret" in descriptions.lower()

    def test_evaluation_report_scoring(self):
        from core.agents.evaluator_agent import (
            EvaluationReport, EvaluationResult, EvaluationCriterion,
        )

        results = [
            EvaluationResult(criterion_id="func-001", passed=True, score=0.9),
            EvaluationResult(criterion_id="sec-001", passed=True, score=1.0),
            EvaluationResult(criterion_id="comp-001", passed=False, score=0.3,
                             critique="Data residency non vérifié"),
        ]

        # Report with a blocking required criterion that failed
        from core.agents.evaluator_agent import EvaluatorAgent
        agent = EvaluatorAgent.__new__(EvaluatorAgent)

        from core.agents.evaluator_agent import DEFAULT_RUBRIC
        report = agent._build_report(
            intention_id="test",
            vertical="comptable",
            rubric=DEFAULT_RUBRIC,
            results=results,
        )

        # comp-001 is required and failed → verdict should be fail
        assert report.verdict == "fail"
        assert len(report.blocking_issues) > 0

    def test_harsh_system_prompt(self):
        from core.agents.evaluator_agent import EvaluatorAgent

        prompt = EvaluatorAgent.HARSH_SYSTEM_PROMPT
        assert "JAMAIS" in prompt
        assert "exigeant" in prompt.lower()
        assert "ADVERSARIAL" in prompt

    @pytest.mark.asyncio
    async def test_sensitive_data_detection(self):
        from core.agents.evaluator_agent import EvaluatorAgent

        agent = EvaluatorAgent.__new__(EvaluatorAgent)

        # Simuler un résultat avec données sensibles
        data_with_secret = {
            "result": {
                "status": "processed",
                "api_key": "sk-1234567890",
                "customer_password": "hunter2",
            }
        }

        results = await agent._test_api("test-intention", data_with_secret, [])
        leaked = [r for r in results if r.criterion_id == "sec-001" and not r.passed]
        assert len(leaked) > 0

    @pytest.mark.asyncio
    async def test_clean_data_passes(self):
        from core.agents.evaluator_agent import EvaluatorAgent

        agent = EvaluatorAgent.__new__(EvaluatorAgent)

        clean_data = {
            "result": {
                "status": "processed",
                "saga_status": {
                    "steps": [
                        {"name": "Notification", "result": {"status": "sent"}}
                    ]
                },
            }
        }

        results = await agent._test_api("test-intention", clean_data, [])
        # Pas de données sensibles → sec-001 doit passer
        sec_results = [r for r in results if r.criterion_id == "sec-001"]
        assert any(r.passed for r in sec_results)


# ── Intégration: Contract → Evaluator ─────────────────────────

class TestContractEvaluatorIntegration:
    """Test que le contrat négocié est utilisé par l'évaluateur."""

    @pytest.mark.asyncio
    async def test_evaluator_uses_contract_criteria(self):
        from core.agents.contract_negotiator import ContractNegotiator, ContractCriterion
        from core.agents.evaluator_agent import EvaluatorAgent

        tmp_dir = Path("./data/test_integration_contracts")
        tmp_dir.mkdir(parents=True, exist_ok=True)

        negotiator = ContractNegotiator(persist_dir=str(tmp_dir))

        with patch.object(negotiator, '_generate_reasoning_proposal', new_callable=AsyncMock) as mock:
            mock.return_value = [
                ContractCriterion(
                    description="Les conclusions sont rédigées conformément aux standards du barreau",
                    test_method="llm_eval",
                    expected_result="Conclusions structurées avec références jurisprudentielles",
                    category="functional",
                    source="reasoning",
                ),
            ]

            contract = await negotiator.negotiate(
                intention_id="integ-001",
                vertical="avocat",
                query="Rédiger des conclusions",
            )

        agent = EvaluatorAgent.__new__(EvaluatorAgent)

        # Charger la rubrique avec le contrat
        rubric = agent._get_rubric("avocat", contract.model_dump())

        # Vérifier que les critères du contrat sont inclus
        criterion_ids = {c.criterion_id for c in rubric}
        for cc in contract.criteria:
            assert cc.id in criterion_ids, f"Contract criterion {cc.id} missing from rubric"

        # Vérifier que les critères avocat sont présents
        descriptions = " ".join(c.description for c in rubric)
        assert "321 CP" in descriptions


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
