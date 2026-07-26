import json
from pathlib import Path

import pytest

from core.config import settings
from core.journal.append_only_journal import AppendOnlyJournal
from core.journal.models import JournalEventType


@pytest.fixture
def journal(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "journal_encryption_enabled", False)
    monkeypatch.setattr(settings, "journal_minimize_payload", True)
    monkeypatch.setattr(settings, "journal_signing_key", "test-signing-key")
    monkeypatch.setattr(settings, "journal_retention_months", 12)
    return AppendOnlyJournal(
        journal_path=str(tmp_path),
        signing_key="test-signing-key",
    )


def event_type():
    return next(iter(JournalEventType))


def append_entry(journal, index, payload=None):
    return journal.append(
        event_type=event_type(),
        client_id="client-1",
        vertical="test",
        agent_source="pytest",
        intention_id=f"intention-{index}",
        payload=payload or {"value": index},
    )


def test_append_and_verify(journal):
    for index in range(5):
        append_entry(journal, index)

    result = journal.verify_integrity()

    assert result["valid"] is True
    assert result["total_entries"] == 5
    assert result["errors"] == []


def test_minimized_payload_hash(journal):
    entry = append_entry(
        journal,
        0,
        {
            "username": "alice",
            "password": "plain-password",
            "access_token": "secret-token",
            "nested": {"api_key": "nested-secret", "visible": True},
        },
    )

    assert entry.payload["password"] == "***REDACTED***"
    assert entry.payload["access_token"] == "***REDACTED***"
    assert entry.payload["nested"]["api_key"] == "***REDACTED***"
    assert entry.payload["username"] == "alice"
    assert journal.verify_integrity()["valid"] is True

    stored = journal.query(limit=1)[0]
    assert stored["payload"] == entry.payload


def test_hash_chain_sequence(journal):
    entries = [append_entry(journal, index) for index in range(5)]

    assert entries[0].previous_hash == "GENESIS"
    for previous, current in zip(entries, entries[1:]):
        assert current.previous_hash == previous.entry_hash

    stored = journal.query(limit=10)
    assert [entry["sequence"] for entry in stored] == [1, 2, 3, 4, 5]
    assert stored[0]["previous_hash"] == "GENESIS"
    for previous, current in zip(stored, stored[1:]):
        assert current["previous_hash"] == previous["entry_hash"]


def test_repair_broken_entries(journal):
    for index in range(5):
        append_entry(journal, index, {"value": index})

    journal_file = next(Path(journal._path).glob("journal-*.jsonl"))
    with open(journal_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    entries = [json.loads(line) for line in lines if line.strip()]
    entries[1]["payload"]["value"] = "tampered"
    entries[3]["entry_hash"] = "broken-hash"

    with open(journal_file, "w", encoding="utf-8") as file:
        for entry in entries:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    assert journal.verify_integrity()["valid"] is False

    repair = journal.repair_integrity()

    assert repair["valid"] is True
    assert repair["repaired_entries"] >= 2
    assert journal.verify_integrity()["valid"] is True
    assert journal.verify_integrity()["total_entries"] == 5
