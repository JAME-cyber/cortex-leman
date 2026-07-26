"""
Cortex Leman v5 — Journal Append-Only (WORM)

Journal immuable, hash-chainé, horodaté et minimisé avant hachage.
"""
import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.config import settings
from core.journal.models import JournalEntry, JournalEventType
from core.journal.worm_v2 import (
    JournalPurger,
    PayloadMinimizer,
    TenantIsolation,
    TreatmentRegistry,
    WormEncryption,
)

logger = logging.getLogger(__name__)


class AppendOnlyJournal:
    """Journal d'audit immuable avec stockage JSON-L et hash-chainage SHA-256."""

    def __init__(
        self,
        journal_path: Optional[str] = None,
        signing_key: Optional[str] = None,
        hash_algo: str = "sha256",
    ):
        self._path = Path(journal_path or settings.journal_path)
        self._signing_key = signing_key or settings.journal_signing_key
        self._hash_algo = hash_algo
        self._sequence = 0
        self._last_hash = "GENESIS"
        self._current_file = None

        self._encryption = WormEncryption()
        self._minimize = settings.journal_minimize_payload
        self._purger = JournalPurger(
            self._path,
            settings.journal_retention_months,
        )

        self._path.mkdir(parents=True, exist_ok=True)
        self._load_state()

    def _load_state(self) -> None:
        """Charger la séquence et le dernier hash depuis le journal existant."""
        journal_files = sorted(self._path.glob("journal-*.jsonl"))
        if not journal_files:
            logger.info("Journal vierge — démarrage depuis GENESIS")
            return

        last_entry = None
        with open(journal_files[-1], "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                raw_line = line
                if self._encryption.enabled:
                    try:
                        raw_line = self._encryption.decrypt(line)
                    except ValueError:
                        pass
                last_entry = json.loads(raw_line)

        if last_entry:
            self._sequence = last_entry.get("sequence", 0)
            self._last_hash = last_entry.get("entry_hash", "GENESIS")
            logger.info(
                "Journal chargé: seq=%s, last_hash=%s...",
                self._sequence,
                self._last_hash[:16],
            )

    def _get_current_file_path(self) -> Path:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._path / f"journal-{today}.jsonl"

    def _compute_hash(
        self,
        entry_data: dict,
        previous_hash: Optional[str] = None,
    ) -> str:
        """Calculer le hash d'une entrée et de son hash précédent."""
        previous = previous_hash if previous_hash is not None else self._last_hash
        content = json.dumps(entry_data, sort_keys=True, ensure_ascii=False)
        return hashlib.new(
            self._hash_algo,
            f"{content}|{previous}".encode("utf-8"),
        ).hexdigest()

    def _sign_entry(self, entry_data: dict) -> str:
        """Signer l'entrée avec la clé de signature HMAC-SHA256."""
        import hmac

        content = json.dumps(entry_data, sort_keys=True, ensure_ascii=False)
        return hmac.new(
            self._signing_key.encode(),
            content.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _decrypt_line(self, line: str) -> str:
        if not self._encryption.enabled:
            return line
        try:
            return self._encryption.decrypt(line)
        except ValueError:
            return line

    def append(
        self,
        event_type: JournalEventType,
        client_id: str,
        vertical: str,
        agent_source: str,
        intention_id: str,
        payload: dict = None,
    ) -> JournalEntry:
        """Ajouter une entrée, en minimisant le payload avant de le hacher."""
        self._sequence += 1
        previous_hash = self._last_hash

        # La minimisation doit précéder la création et le hachage de l'entrée.
        minimized_payload = payload or {}
        if self._minimize and minimized_payload:
            minimized_payload = PayloadMinimizer.minimize(minimized_payload)

        entry = JournalEntry(
            entry_id=str(uuid.uuid4()),
            sequence=self._sequence,
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            client_id=client_id,
            vertical=vertical,
            agent_source=agent_source,
            intention_id=intention_id,
            payload=minimized_payload,
            previous_hash=previous_hash,
        )

        entry_data = json.loads(entry.model_dump_json())
        entry_data.pop("entry_hash", None)
        entry_data.pop("signature", None)
        entry_hash = self._compute_hash(entry_data, previous_hash)
        signature = self._sign_entry({**entry_data, "entry_hash": entry_hash})
        entry = entry.model_copy(
            update={"entry_hash": entry_hash, "signature": signature}
        )

        line_data = entry.model_dump_json()
        if self._encryption.enabled:
            line_data = self._encryption.encrypt(line_data)
        line_data += "\n"

        try:
            with open(self._get_current_file_path(), "a", encoding="utf-8") as file:
                file.write(line_data)
        except IOError as error:
            self._sequence -= 1
            logger.critical("Écriture journal ÉCHOUÉE: %s", error)
            raise RuntimeError(f"Journal write failed: {error}") from error

        self._last_hash = entry_hash
        logger.debug(
            "Journal #%s: %s intent=%s",
            self._sequence,
            event_type.value,
            intention_id,
        )
        return entry

    def verify_integrity(self, file_path: Optional[Path] = None) -> dict:
        """Vérifier l'intégrité des entrées et de leur chaîne de hachage."""
        files_to_check = (
            [Path(file_path)]
            if file_path
            else sorted(self._path.glob("journal-*.jsonl"))
        )
        previous_hash = "GENESIS"
        total_entries = 0
        errors = []

        for journal_file in files_to_check:
            with open(journal_file, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(self._decrypt_line(line))
                        total_entries += 1

                        stored_previous = entry.get("previous_hash")
                        if stored_previous != previous_hash:
                            errors.append(
                                f"Chaîne brisée à {journal_file.name}:{line_number} "
                                f"(expected {previous_hash[:16]}... got "
                                f"{str(stored_previous or '')[:16]}...)"
                            )

                        verify_data = {
                            key: value
                            for key, value in entry.items()
                            if key not in ("entry_hash", "signature")
                        }
                        expected_hash = self._compute_hash(
                            verify_data,
                            stored_previous or "GENESIS",
                        )
                        if entry.get("entry_hash") != expected_hash:
                            errors.append(
                                f"Hash invalide à {journal_file.name}:{line_number}"
                            )

                        previous_hash = entry.get("entry_hash", previous_hash)
                    except (json.JSONDecodeError, KeyError, TypeError) as error:
                        errors.append(
                            f"Entrée corrompue {journal_file.name}:{line_number}: {error}"
                        )

        return {
            "valid": not errors,
            "total_entries": total_entries,
            "errors": errors,
            "last_hash": previous_hash,
        }

    def repair_integrity(self, file_path: Optional[Path] = None) -> dict:
        """Réparer les hashes invalides et propager la réparation dans la chaîne.

        Les fichiers sont réécrits uniquement lorsqu'une entrée doit être réparée.
        Les signatures sont recalculées pour les entrées modifiées.
        """
        files_to_repair = (
            [Path(file_path)]
            if file_path
            else sorted(self._path.glob("journal-*.jsonl"))
        )
        previous_hash = "GENESIS"
        repaired_entries = 0
        errors = []

        for journal_file in files_to_repair:
            entries = []
            changed = False
            try:
                with open(journal_file, "r", encoding="utf-8") as file:
                    for line_number, line in enumerate(file, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entries.append(json.loads(self._decrypt_line(line)))
                        except (json.JSONDecodeError, TypeError) as error:
                            errors.append(
                                f"Entrée corrompue {journal_file.name}:{line_number}: {error}"
                            )
            except OSError as error:
                errors.append(f"Lecture impossible {journal_file}: {error}")
                continue

            repaired_output = []
            for entry in entries:
                original = dict(entry)
                if entry.get("previous_hash") != previous_hash:
                    entry["previous_hash"] = previous_hash

                verify_data = {
                    key: value
                    for key, value in entry.items()
                    if key not in ("entry_hash", "signature")
                }
                expected_hash = self._compute_hash(verify_data, previous_hash)
                if entry.get("entry_hash") != expected_hash:
                    entry["entry_hash"] = expected_hash

                if entry != original:
                    repaired_entries += 1
                    changed = True
                    logger.warning(
                        "Réparation d'intégrité: %s sequence=%s",
                        journal_file.name,
                        entry.get("sequence"),
                    )

                # Toute modification de l'entrée signée impose une nouvelle signature.
                if entry != original or not entry.get("signature"):
                    sign_data = {
                        key: value
                        for key, value in entry.items()
                        if key != "signature"
                    }
                    entry["signature"] = self._sign_entry(sign_data)
                    changed = True

                previous_hash = entry.get("entry_hash", previous_hash)
                repaired_output.append(entry)

            if changed:
                temporary_path = journal_file.with_suffix(journal_file.suffix + ".repair")
                try:
                    with open(temporary_path, "w", encoding="utf-8") as file:
                        for entry in repaired_output:
                            serialized = json.dumps(
                                entry,
                                ensure_ascii=False,
                                separators=(",", ":"),
                            )
                            if self._encryption.enabled:
                                serialized = self._encryption.encrypt(serialized)
                            file.write(serialized + "\n")
                    temporary_path.replace(journal_file)
                except OSError as error:
                    errors.append(f"Écriture impossible {journal_file}: {error}")

        if files_to_repair and not errors:
            self._sequence = max(
                (entry.get("sequence", 0) for journal_file in files_to_repair
                 for entry in self._read_entries(journal_file)),
                default=self._sequence,
            )
            self._last_hash = previous_hash

        logger.info("Réparation d'intégrité terminée: %s entrée(s)", repaired_entries)
        return {
            "valid": not errors,
            "repaired_entries": repaired_entries,
            "errors": errors,
            "last_hash": previous_hash,
        }

    def _read_entries(self, journal_file: Path) -> list[dict]:
        entries = []
        if not journal_file.exists():
            return entries
        with open(journal_file, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    entries.append(json.loads(self._decrypt_line(line)))
        return entries

    def query(
        self,
        intention_id: Optional[str] = None,
        event_type: Optional[JournalEventType] = None,
        client_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Requêter le journal en lecture seule."""
        results = []
        for journal_file in sorted(self._path.glob("journal-*.jsonl")):
            for entry in self._read_entries(journal_file):
                if intention_id and entry.get("intention_id") != intention_id:
                    continue
                if event_type and entry.get("event_type") != event_type.value:
                    continue
                if client_id and entry.get("client_id") != client_id:
                    continue
                results.append(entry)
        return results[-limit:]

    def purge_expired(self, dry_run: bool = True) -> dict:
        return self._purger.purge_expired(dry_run=dry_run)

    def get_treatment_registry(self) -> dict:
        return TreatmentRegistry.get_registry()

    def get_legal_basis_matrix(self) -> list[dict]:
        return TreatmentRegistry.get_legal_basis_matrix()

    def query_tenant(
        self,
        client_id: str,
        intention_id: Optional[str] = None,
        event_type: Optional[JournalEventType] = None,
        limit: int = 100,
    ) -> list[dict]:
        entries = self.query(
            intention_id=intention_id,
            event_type=event_type,
            client_id=client_id,
            limit=limit,
        )
        return TenantIsolation.filter_entries(entries, client_id=client_id)

    @property
    def encryption_status(self) -> dict:
        return {
            "enabled": self._encryption.enabled,
            "algorithm": "AES-256 (Fernet)" if self._encryption.enabled else "none",
            "key_derivation": (
                "PBKDF2-SHA256 (480k iterations)"
                if self._encryption.enabled else "n/a"
            ),
        }

    @property
    def last_hash(self) -> str:
        return self._last_hash

    @property
    def sequence(self) -> int:
        return self._sequence


journal = AppendOnlyJournal()
