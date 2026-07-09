"""
Cortex Leman v5 — Tests: PrecedentStore + ComplianceGoal + AgentIdentity

3 features inspirées du podcast La French × Romain Huet (OpenAI):
1. PrecedentStore — Jurisprudence IA
2. ComplianceGoal — Tâches conformité longue durée
3. AgentIdentity — KYA régulé (Know Your Agent)
"""
import os
import json
import tempfile
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ================================================================
# Test PrecedentStore
# ================================================================

class TestPrecedentStore:
    """Tests du système de jurisprudence IA."""

    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.store_path = os.path.join(self.tmp, "precedents.json")

    def _make_store(self):
        from core.mediator.precedent_store import PrecedentStore
        return PrecedentStore(persist_path=self.store_path)

    def test_capture_precedent(self):
        store = self._make_store()
        p = store.capture(
            conflict_id="conflict-001",
            intention_id="intent-001",
            client_id="client-dupont",
            vertical="comptable",
            question="Puis-je déduire les frais de repas professionnels ?",
            conflict_reason="gel_montant: montant élevé détecté",
            agent_positions={"data": {"recommendation": "oui", "confidence": 0.8}, "reasoning": {"recommendation": "non", "confidence": 0.6}},
            arbiter_id="expert-dupont",
            arbiter_name="Jean Dupont",
            decision="approve",
            justification="Les frais de repas sont déductibles dans la limite de 25€ par repas (Art. 239 CGI).",
            selected_position="data",
            rule_id_source="comptable-006",
        )
        assert p.precedent_id
        assert p.vertical == "comptable"
        assert p.decision == "approve"
        assert p.strength.value == "weak"  # Premier précédent
        assert p.context_signature  # Signature calculée

    def test_capture_strengthen_precedent(self):
        """3+ précédents similaires → force STRONG + suggestion de règle."""
        store = self._make_store()

        # Capturer 3 précédents avec le même pattern
        for i in range(3):
            store.capture(
                conflict_id=f"conflict-{i}",
                intention_id=f"intent-{i}",
                client_id="client-test",
                vertical="comptable",
                question="Puis-je déduire les frais de repas professionnels ?",
                conflict_reason="gel_montant: montant élevé détecté",
                agent_positions={},
                arbiter_id="expert",
                arbiter_name="Expert",
                decision="approve",
                justification=f"Justification {i}",
                selected_position="data",
                rule_id_source="comptable-006",
            )

        # Le 3ème doit être STRONG
        all_precedents = store.get_all_for_vertical("comptable")
        assert len(all_precedents) == 3

        # Un candidat de règle doit avoir été créé
        candidates = store.get_pending_candidates()
        assert len(candidates) >= 1
        assert candidates[0].vertical == "comptable"
        assert candidates[0].status == "pending"

    def test_query_precedents(self):
        store = self._make_store()

        # Capturer quelques précédents
        store.capture(
            conflict_id="c1", intention_id="i1", client_id="cl1",
            vertical="avocat", question="Puis-je partager des données client ?",
            conflict_reason="gel_secret: données sensibles",
            agent_positions={}, arbiter_id="e1", arbiter_name="Maître Martin",
            decision="reject", justification="Secret professionnel Art. 321 CP",
            selected_position="reasoning", rule_id_source="avocat-003",
        )
        store.capture(
            conflict_id="c2", intention_id="i2", client_id="cl1",
            vertical="avocat", question="Puis-je transmettre des données au confrère ?",
            conflict_reason="gel_secret: transfert sensible",
            agent_positions={}, arbiter_id="e1", arbiter_name="Maître Martin",
            decision="reject", justification="Secret professionnel Art. 321 CP",
            selected_position="reasoning", rule_id_source="avocat-003",
        )

        # Requêter
        matches = store.query(
            vertical="avocat",
            question="Puis-je partager des données client ?",
            rule_id="avocat-003",
        )
        assert len(matches) >= 1
        assert matches[0].relevance > 0.1
        assert matches[0].precedent.vertical == "avocat"

    def test_persistence(self):
        store = self._make_store()
        store.capture(
            conflict_id="c1", intention_id="i1", client_id="cl1",
            vertical="banque", question="Seuil KYC ?",
            conflict_reason="gel_montant: montant > 15K",
            agent_positions={}, arbiter_id="e1", arbiter_name="Analyste",
            decision="approve", justification="KYC complet",
            selected_position="data",
        )

        # Recharger depuis le disque
        from core.mediator.precedent_store import PrecedentStore
        store2 = PrecedentStore(persist_path=self.store_path)
        assert len(store2.get_all_for_vertical("banque")) == 1

    def test_override_precedent(self):
        store = self._make_store()
        p = store.capture(
            conflict_id="c1", intention_id="i1", client_id="cl1",
            vertical="rh", question="Score candidat automatisé ?",
            conflict_reason="conflit_agents: divergence",
            agent_positions={}, arbiter_id="e1", arbiter_name="DRH",
            decision="approve", justification="OK",
            selected_position="data",
        )

        ok = store.override_precedent(p.precedent_id, reason="Nouvel arbitrage contradictoire")
        assert ok

        # Le précédent n'est plus actif
        active = store.get_all_for_vertical("rh")
        assert len(active) == 0

    def test_approve_candidate(self):
        store = self._make_store()

        # Créer 3+ précédents pour déclencher la suggestion
        for i in range(3):
            store.capture(
                conflict_id=f"c{i}", intention_id=f"i{i}", client_id="cl1",
                vertical="startup", question="AI Act checklist ?",
                conflict_reason="gel_conformite: vérification requise",
                agent_positions={}, arbiter_id="e1", arbiter_name="CTO",
                decision="approve", justification=f"OK {i}",
                selected_position="data",
            )

        candidates = store.get_pending_candidates()
        assert len(candidates) >= 1

        candidate = candidates[0]
        approved = store.approve_candidate(candidate.candidate_id, reviewer="Expert Senior")
        assert approved.status == "approved"
        assert approved.reviewed_by == "Expert Senior"

    def test_get_stats(self):
        store = self._make_store()
        store.capture(
            conflict_id="c1", intention_id="i1", client_id="cl1",
            vertical="sante", question="Données patient ?",
            conflict_reason="gel_donnees: données de santé",
            agent_positions={}, arbiter_id="e1", arbiter_name="Dr. Martin",
            decision="reject", justification="LPM",
            selected_position="reasoning",
        )

        stats = store.get_stats()
        assert stats["total_precedents"] == 1
        assert stats["active"] == 1
        assert "sante" in stats["by_vertical"]


# ================================================================
# Test ComplianceGoal
# ================================================================

class TestComplianceGoal:
    """Tests des tâches de conformité longue durée."""

    def setup_method(self):
        from core.orchestrator.compliance_goal import ComplianceGoalRunner
        self.runner = ComplianceGoalRunner()

    def test_create_goal_from_template(self):
        goal = self.runner.create_goal(
            client_id="client-startup-1",
            vertical="startup",
            title="AI Act Compliance Check",
            description="Checklist complète AI Act",
        )
        assert goal.goal_id
        assert goal.vertical == "startup"
        assert len(goal.subtasks) >= 4  # Template startup a 5 sous-tâches
        assert goal.status.value == "pending"

    def test_create_goal_no_template(self):
        goal = self.runner.create_goal(
            client_id="client-1",
            vertical="comptable",
            title="Audit personnalisé",
            description="Audit sur mesure",
        )
        assert len(goal.subtasks) >= 2  # Au minimum les tâches génériques

    def test_start_goal(self):
        goal = self.runner.create_goal(
            client_id="c1", vertical="avocat",
            title="Audit Secret Pro", description="Test",
        )
        started = self.runner.start_goal(goal.goal_id)
        assert started.status.value == "running"
        assert started.started_at is not None

    def test_update_subtask(self):
        goal = self.runner.create_goal(
            client_id="c1", vertical="banque",
            title="Audit KYC", description="Test",
        )
        self.runner.start_goal(goal.goal_id)

        # Première sous-tâche → en cours
        first_task = goal.subtasks[0]
        self.runner.update_subtask(
            goal.goal_id, first_task.task_id,
            status="running",
        )

        # → complétée avec résultat
        self.runner.update_subtask(
            goal.goal_id, first_task.task_id,
            status="done",
            result={"found": 42, "confidence": 0.95},
            confidence=0.95,
        )

        updated = self.runner.get_goal(goal.goal_id)
        assert updated.subtasks[0].status.value == "done"
        assert updated.subtasks[0].confidence == 0.95
        assert updated.progress > 0

    def test_complete_all_subtasks_completes_goal(self):
        goal = self.runner.create_goal(
            client_id="c1", vertical="rh",
            title="Audit Anti-Discrimination", description="Test",
        )
        self.runner.start_goal(goal.goal_id)

        for st in goal.subtasks:
            self.runner.update_subtask(
                goal.goal_id, st.task_id, status="done",
                result={"ok": True}, confidence=0.9,
            )

        completed = self.runner.get_goal(goal.goal_id)
        assert completed.status.value == "completed"
        assert completed.progress == 1.0
        assert completed.result is not None
        assert completed.result["integrity"] == "WORM_journalized"

    def test_pause_and_resume_goal(self):
        goal = self.runner.create_goal(
            client_id="c1", vertical="sante",
            title="Audit HDS", description="Test",
        )
        self.runner.start_goal(goal.goal_id)

        paused = self.runner.pause_goal(goal.goal_id, reason="Médiateur a gelé")
        assert paused.status.value == "paused"

        resumed = self.runner.resume_goal(goal.goal_id)
        assert resumed.status.value == "running"

    def test_get_templates(self):
        from core.orchestrator.compliance_goal import compliance_goal_runner
        templates = compliance_goal_runner.get_templates()
        assert "comptable" in templates
        assert "avocat" in templates
        assert "startup" in templates
        assert len(templates["startup"]) >= 1

    def test_get_active_goals(self):
        g1 = self.runner.create_goal(
            client_id="c1", vertical="comptable",
            title="Goal 1", description="Test",
        )
        g2 = self.runner.create_goal(
            client_id="c1", vertical="comptable",
            title="Goal 2", description="Test",
        )
        self.runner.start_goal(g1.goal_id)

        active = self.runner.get_active_goals()
        assert len(active) == 2  # pending + running

    def test_get_goals_for_client(self):
        self.runner.create_goal(
            client_id="client-A", vertical="comptable",
            title="Goal A", description="Test",
        )
        self.runner.create_goal(
            client_id="client-B", vertical="avocat",
            title="Goal B", description="Test",
        )

        goals_a = self.runner.get_goals_for_client("client-A")
        assert len(goals_a) == 1
        assert goals_a[0].vertical == "comptable"


# ================================================================
# Test AgentIdentity
# ================================================================

class TestAgentIdentity:
    """Tests du KYA régulé (Know Your Agent)."""

    def setup_method(self):
        from core.security.agent_identity import AgentIdentityProvider
        self.provider = AgentIdentityProvider(signing_key="test-key-for-unit-tests")

    def test_default_agents_initialized(self):
        """Les 6 agents par défaut sont créés."""
        identities = self.provider.get_all_identities()
        agent_ids = [i.agent_id for i in identities]
        assert "agent-data" in agent_ids
        assert "agent-reasoning" in agent_ids
        assert "agent-action" in agent_ids
        assert "agent-supervisor" in agent_ids
        assert "mediator" in agent_ids
        assert "orchestrator" in agent_ids

    def test_activate_session(self):
        cred = self.provider.activate_session("agent-data", vertical="comptable")
        assert cred is not None
        assert cred.session_id
        assert cred.agent_id == "agent-data"
        assert cred.signature  # Signé

        # L'identité doit avoir un serment signé
        identity = self.provider.get_identity("agent-data")
        assert identity.session_id == cred.session_id
        assert identity.oath_hash is not None

    def test_deactivate_session(self):
        self.provider.activate_session("agent-reasoning", vertical="avocat")
        ok = self.provider.deactivate_session("agent-reasoning")
        assert ok

        identity = self.provider.get_identity("agent-reasoning")
        assert identity.session_id is None
        assert identity.oath_hash is None

    def test_verify_permission_allowed(self):
        from core.security.agent_identity import AgentScope
        self.provider.activate_session("agent-data", vertical="comptable")

        allowed, reason = self.provider.verify_permission(
            "agent-data", AgentScope.DATA_READ, "comptable"
        )
        assert allowed
        assert reason == "OK"

    def test_verify_permission_denied_wrong_scope(self):
        from core.security.agent_identity import AgentScope
        self.provider.activate_session("agent-data", vertical="comptable")

        # Data agent ne peut pas exécuter d'actions
        allowed, reason = self.provider.verify_permission(
            "agent-data", AgentScope.ACTION_EXECUTE, "comptable"
        )
        assert not allowed
        assert "non accordé" in reason

    def test_verify_permission_denied_wrong_vertical(self):
        from core.security.agent_identity import AgentScope
        self.provider.activate_session("agent-data", vertical="comptable")

        # Session ouverte pour comptable, pas pour avocat
        allowed, reason = self.provider.verify_permission(
            "agent-data", AgentScope.DATA_READ, "avocat"
        )
        assert not allowed

    def test_verify_permission_denied_no_session(self):
        from core.security.agent_identity import AgentScope

        # Pas de session active
        allowed, reason = self.provider.verify_permission(
            "agent-data", AgentScope.DATA_READ, "comptable"
        )
        assert not allowed
        assert "pas de session" in reason

    def test_verify_permission_or_raise(self):
        from core.security.agent_identity import AgentScope
        self.provider.activate_session("mediator", vertical="banque")

        # Autorisé
        self.provider.verify_permission_or_raise(
            "mediator", AgentScope.MEDIATOR_FREEZE, "banque"
        )

        # Non autorisé
        with pytest.raises(PermissionError):
            self.provider.verify_permission_or_raise(
                "mediator", AgentScope.ACTION_EXECUTE, "banque"
            )

    def test_delegate_scopes(self):
        from core.security.agent_identity import AgentScope

        # Parent: orchestrator
        parent_cred = self.provider.activate_session("orchestrator", vertical="comptable")
        assert parent_cred is not None

        # Déléguer des scopes à l'agent data
        child_cred = self.provider.delegate_scopes(
            parent_agent_id="orchestrator",
            child_agent_id="agent-data",
            scopes=[AgentScope.DATA_READ, AgentScope.KNOWLEDGE_READ],
            vertical="comptable",
        )
        assert child_cred is not None
        assert child_cred.parent_credential_id == parent_cred.credential_id

    def test_delegate_scopes_subset_only(self):
        """On ne peut déléguer QUE ce qu'on a."""
        from core.security.agent_identity import AgentScope

        # Supervisor n'a pas ACTION_EXECUTE
        self.provider.activate_session("agent-supervisor", vertical="rh")

        child_cred = self.provider.delegate_scopes(
            parent_agent_id="agent-supervisor",
            child_agent_id="agent-data",
            scopes=[AgentScope.ACTION_EXECUTE],  # Supervisor n'a pas ça
            vertical="rh",
        )
        assert child_cred is None  # Refusé

    def test_suspend_agent(self):
        self.provider.activate_session("agent-reasoning", vertical="avocat")
        ok = self.provider.suspend_agent("agent-reasoning", reason="Comportement suspect")
        assert ok

        identity = self.provider.get_identity("agent-reasoning")
        assert identity.status.value == "suspended"
        assert identity.session_id is None  # Session fermée

        # Ne peut plus activer de session
        cred = self.provider.activate_session("agent-reasoning", vertical="avocat")
        assert cred is None

    def test_revoke_agent(self):
        ok = self.provider.revoke_agent("agent-action", reason="Compromis")
        assert ok

        identity = self.provider.get_identity("agent-action")
        assert identity.status.value == "revoked"

    def test_get_audit_trail(self):
        self.provider.activate_session("mediator", vertical="sante")

        audit = self.provider.get_audit_trail("mediator")
        assert audit["agent_id"] == "mediator"
        assert audit["session_active"] is True
        assert audit["oath_signed"] is True
        assert audit["agent_role"] == "mediator"
        assert len(audit["scopes"]) > 0

    def test_mediator_has_no_action_execute(self):
        """Le Médiateur ne doit JAMAIS avoir ACTION_EXECUTE."""
        from core.security.agent_identity import AgentScope

        cred = self.provider.activate_session("mediator", vertical="comptable")
        assert AgentScope.ACTION_EXECUTE not in cred.scopes
        assert AgentScope.MEDIATOR_FREEZE in cred.scopes

    def test_action_agent_has_no_freeze(self):
        """L'Agent Action ne doit PAS avoir MEDIATOR_FREEZE."""
        from core.security.agent_identity import AgentScope

        cred = self.provider.activate_session("agent-action", vertical="banque")
        assert AgentScope.MEDIATOR_FREEZE not in cred.scopes
        assert AgentScope.ACTION_EXECUTE in cred.scopes
