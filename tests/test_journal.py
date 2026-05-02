"""
Cortex Leman v5 — Tests du Journal Append-Only
"""
import os
import json
import tempfile
import pytest

from core.journal.append_only_journal import AppendOnlyJournal
from core.journal.models import JournalEventType


@pytest.fixture
def journal(tmp_path):
    """Journal temporaire pour les tests"""
    return AppendOnlyJournal(
        journal_path=str(tmp_path / "journal"),
        signing_key="test-key-for-signing",
        hash_algo="sha256",
    )


class TestAppendOnlyJournal:
    """Tests du journal immuable"""

    def test_append_creates_entry(self, journal):
        entry = journal.append(
            event_type=JournalEventType.INTENTION_CREATED,
            client_id="client-001",
            vertical="comptable",
            agent_source="orchestrator",
            intention_id="intent-001",
            payload={"query": "test query"},
        )
        assert entry.sequence == 1
        assert entry.event_type == JournalEventType.INTENTION_CREATED
        assert entry.client_id == "client-001"
        assert entry.previous_hash == "GENESIS"
        assert entry.entry_hash != ""

    def test_hash_chaining(self, journal):
        e1 = journal.append(
            event_type=JournalEventType.INTENTION_CREATED,
            client_id="c1", vertical="comptable",
            agent_source="orchestrator", intention_id="i1",
        )
        e2 = journal.append(
            event_type=JournalEventType.AGENT_QUERY,
            client_id="c1", vertical="comptable",
            agent_source="data", intention_id="i1",
        )
        assert e2.previous_hash == e1.entry_hash
        assert e2.sequence == 2

    def test_immutability(self, journal):
        entry = journal.append(
            event_type=JournalEventType.INTENTION_CREATED,
            client_id="c1", vertical="comptable",
            agent_source="orchestrator", intention_id="i1",
        )
        with pytest.raises(Exception):
            entry.client_id = "modified"

    def test_verify_integrity_valid(self, journal):
        for i in range(5):
            journal.append(
                event_type=JournalEventType.AGENT_RESULT,
                client_id="c1", vertical="comptable",
                agent_source="data", intention_id=f"i{i}",
            )
        result = journal.verify_integrity()
        assert result["valid"] is True
        assert result["total_entries"] == 5
        assert len(result["errors"]) == 0

    def test_query_by_intention(self, journal):
        journal.append(
            event_type=JournalEventType.INTENTION_CREATED,
            client_id="c1", vertical="comptable",
            agent_source="orchestrator", intention_id="target-intent",
        )
        journal.append(
            event_type=JournalEventType.AGENT_RESULT,
            client_id="c2", vertical="avocat",
            agent_source="data", intention_id="other-intent",
        )
        journal.append(
            event_type=JournalEventType.AGENT_ERROR,
            client_id="c1", vertical="comptable",
            agent_source="data", intention_id="target-intent",
        )

        results = journal.query(intention_id="target-intent")
        assert len(results) == 2
        assert all(r["intention_id"] == "target-intent" for r in results)

    def test_query_by_client(self, journal):
        journal.append(
            event_type=JournalEventType.INTENTION_CREATED,
            client_id="client-a", vertical="comptable",
            agent_source="orchestrator", intention_id="i1",
        )
        journal.append(
            event_type=JournalEventType.INTENTION_CREATED,
            client_id="client-b", vertical="avocat",
            agent_source="orchestrator", intention_id="i2",
        )

        results = journal.query(client_id="client-a")
        assert len(results) == 1
        assert results[0]["client_id"] == "client-a"

    def test_signature_present(self, journal):
        entry = journal.append(
            event_type=JournalEventType.INTENTION_CREATED,
            client_id="c1", vertical="comptable",
            agent_source="orchestrator", intention_id="i1",
        )
        assert entry.signature is not None
        assert len(entry.signature) > 0

    def test_persistence(self, tmp_path):
        journal_path = str(tmp_path / "journal")
        j1 = AppendOnlyJournal(
            journal_path=journal_path,
            signing_key="test-key",
        )
        j1.append(
            event_type=JournalEventType.SYSTEM_START,
            client_id="system", vertical="system",
            agent_source="orchestrator", intention_id="system",
        )
        seq1 = j1.sequence

        # Recréer le journal — doit recharger l'état
        j2 = AppendOnlyJournal(
            journal_path=journal_path,
            signing_key="test-key",
        )
        assert j2.sequence == seq1
        assert j2.last_hash == j1.last_hash
