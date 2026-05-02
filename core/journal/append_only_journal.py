"""
Cortex Leman v5 — Journal Append-Only (WORM)

Journal immuable, hash-chainé, horodaté.
Source de vérité pour audit, reproductibilité et conformité AI Act.

Caractéristiques:
- Append-only: écriture seule, pas de modification ni suppression
- Hash-chainé: chaque entrée lie vers la précédente (chaîne de confiance)
- Horodatage UTC avec timezone
- Persistance fichier JSON-L avec rotation
- Vérification d'intégrité en continu
"""
import json
import hashlib
import os
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.journal.models import JournalEntry, JournalEventType
from core.config import settings

logger = logging.getLogger(__name__)


class AppendOnlyJournal:
    """
    Journal d'audit immuable Cortex Leman.
    Stockage JSON-L avec hash-chainage SHA-256.
    """

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

        # Créer le répertoire
        self._path.mkdir(parents=True, exist_ok=True)

        # Charger l'état depuis le dernier fichier
        self._load_state()

    def _load_state(self) -> None:
        """Charger la séquence et le dernier hash depuis le journal existant"""
        journal_files = sorted(self._path.glob("journal-*.jsonl"))
        if not journal_files:
            logger.info("Journal vierge — démarrage depuis GENESIS")
            return

        last_file = journal_files[-1]
        last_entry = None
        with open(last_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    last_entry = json.loads(line)

        if last_entry:
            self._sequence = last_entry.get("sequence", 0)
            self._last_hash = last_entry.get("entry_hash", "GENESIS")
            logger.info(f"Journal chargé: seq={self._sequence}, last_hash={self._last_hash[:16]}...")

    def _get_current_file_path(self) -> Path:
        """Fichier journal courant (un par jour)"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._path / f"journal-{today}.jsonl"

    def _compute_hash(self, entry_data: dict, previous_hash: str = None) -> str:
        """Calculer le hash d'une entrée (contenu + previous_hash)"""
        prev = previous_hash or self._last_hash
        content = json.dumps(entry_data, sort_keys=True, ensure_ascii=False)
        content_with_prev = f"{content}|{prev}"
        return hashlib.new(
            self._hash_algo,
            content_with_prev.encode("utf-8")
        ).hexdigest()

    def _sign_entry(self, entry_data: dict) -> str:
        """Signer l'entrée avec la clé de signature (HMAC-SHA256)"""
        import hmac
        content = json.dumps(entry_data, sort_keys=True, ensure_ascii=False)
        return hmac.new(
            self._signing_key.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()

    def append(
        self,
        event_type: JournalEventType,
        client_id: str,
        vertical: str,
        agent_source: str,
        intention_id: str,
        payload: dict = None,
    ) -> JournalEntry:
        """
        Ajouter une entrée au journal. Immuabilité garantie.
        
        Returns:
            JournalEntry: L'entrée créée (immuable)
        Raises:
            RuntimeError: Si l'écriture échoue (journal corrompu)
        """
        self._sequence += 1

        prev_hash = self._last_hash

        # Créer d'abord l'entrée sans hash
        entry = JournalEntry(
            entry_id=str(uuid.uuid4()),
            sequence=self._sequence,
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            client_id=client_id,
            vertical=vertical,
            agent_source=agent_source,
            intention_id=intention_id,
            payload=payload or {},
            previous_hash=prev_hash,
        )

        # Calculer le hash à partir de la sérialisation exacte de l'entrée
        entry_data = json.loads(entry.model_dump_json())
        # Retirer entry_hash et signature (pas encore calculés)
        entry_data.pop("entry_hash", None)
        entry_data.pop("signature", None)
        content = json.dumps(entry_data, sort_keys=True, ensure_ascii=False)
        entry_hash = hashlib.new(
            self._hash_algo,
            f"{content}|{prev_hash}".encode("utf-8")
        ).hexdigest()

        signature = self._sign_entry({**entry_data, "entry_hash": entry_hash})

        # Mettre à jour l'entrée avec le hash et la signature
        entry = entry.model_copy(update={
            "entry_hash": entry_hash,
            "signature": signature,
        })

        # Écriture append-only
        file_path = self._get_current_file_path()
        line = entry.model_dump_json() + "\n"

        try:
            with open(file_path, "a") as f:
                f.write(line)
        except IOError as e:
            self._sequence -= 1  # Rollback in-memory state
            logger.critical(f"Écriture journal ÉCHOUÉE: {e}")
            raise RuntimeError(f"Journal write failed: {e}") from e

        # Mettre à jour la chaîne
        self._last_hash = entry_hash
        logger.debug(f"Journal #{self._sequence}: {event_type.value} intent={intention_id}")

        return entry

    def verify_integrity(self, file_path: Optional[Path] = None) -> dict:
        """
        Vérifier l'intégrité de la chaîne de hachage.
        
        Returns:
            dict avec valid=True/False et détails
        """
        files_to_check = (
            [file_path] if file_path else sorted(self._path.glob("journal-*.jsonl"))
        )

        prev_hash = "GENESIS"
        total_entries = 0
        errors = []

        for jf in files_to_check:
            with open(jf, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        total_entries += 1

                        # Vérifier le chaînage
                        if entry.get("previous_hash") != prev_hash:
                            errors.append(
                                f"Chaîne brisée à {jf.name}:{line_num} "
                                f"(expected {prev_hash[:16]}... got {entry.get('previous_hash', '')[:16]}...)"
                            )

                        # Recalculer le hash
                        # Retirer entry_hash et signature pour le recalcul (même logique que append)
                        verify_data = {k: v for k, v in entry.items() if k not in ("entry_hash", "signature")}
                        expected_hash = hashlib.new(
                            self._hash_algo,
                            (json.dumps(verify_data, sort_keys=True, ensure_ascii=False) + "|" + entry.get("previous_hash", "GENESIS")).encode()
                        ).hexdigest()

                        if entry.get("entry_hash") != expected_hash:
                            errors.append(
                                f"Hash invalide à {jf.name}:{line_num}"
                            )

                        prev_hash = entry.get("entry_hash", prev_hash)

                    except (json.JSONDecodeError, KeyError) as e:
                        errors.append(f"Entrée corrompue {jf.name}:{line_num}: {e}")

        return {
            "valid": len(errors) == 0,
            "total_entries": total_entries,
            "errors": errors,
            "last_hash": prev_hash,
        }

    def query(
        self,
        intention_id: Optional[str] = None,
        event_type: Optional[JournalEventType] = None,
        client_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Requêter le journal (lecture seule)"""
        results = []

        for jf in sorted(self._path.glob("journal-*.jsonl")):
            with open(jf, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)

                    # Filtres
                    if intention_id and entry.get("intention_id") != intention_id:
                        continue
                    if event_type and entry.get("event_type") != event_type.value:
                        continue
                    if client_id and entry.get("client_id") != client_id:
                        continue

                    results.append(entry)

        return results[-limit:]

    @property
    def last_hash(self) -> str:
        return self._last_hash

    @property
    def sequence(self) -> int:
        return self._sequence


# Singleton
journal = AppendOnlyJournal()
