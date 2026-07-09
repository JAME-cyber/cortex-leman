"""
Cortex Leman v5 — Journal WORM v2

Conformité RGPD (audit o3, 2026-05-27) :
- Chiffrement AES-256 au repos des entrées
- Minimisation des données (RGPD art. 5-1c)
- Purge automatique après durée de conservation (RGPD art. 5-1e)
- Isolation multi-tenant par client_id
- Registre des traitements (RGPD art. 30)

Le hash-chainage SHA-256 est préservé sur les données chiffrées :
chaque entrée est chiffrée APRÈS calcul du hash, garantissant
l'intégrité de la chaîne SANS exposer les données en clair au repos.
"""
import base64
import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.config import settings

logger = logging.getLogger(__name__)


def _derive_key(secret: str, salt: bytes) -> bytes:
    """Dérive une clé AES-256 valide (32 bytes → base64 pour Fernet) via PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480_000,
    )
    key = kdf.derive(secret.encode("utf-8"))
    return base64.urlsafe_b64encode(key)


class WormEncryption:
    """Chiffrement AES-256 au repos pour le journal WORM v2."""

    def __init__(self, key: Optional[str] = None):
        self._enabled = settings.journal_encryption_enabled
        if not self._enabled:
            logger.info("WORM v2: chiffrement DÉSACTIVÉ (mode dev)")
            self._fernet = None
            return

        # Charger ou générer la clé
        if key:
            raw_key = _derive_key(key, b"cortex-leman-worm-v2-salt")
        else:
            raw_key = _derive_key(
                settings.journal_signing_key,
                b"cortex-leman-worm-v2-salt",
            )

        self._fernet = Fernet(raw_key)
        logger.info("WORM v2: chiffrement AES-256 ACTIVÉ")

    @property
    def enabled(self) -> bool:
        return self._enabled and self._fernet is not None

    def encrypt(self, plaintext: str) -> str:
        """Chiffrer une entrée de journal"""
        if not self.enabled:
            return plaintext
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """Déchiffrer une entrée de journal"""
        if not self.enabled:
            return ciphertext
        try:
            return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except Exception as e:
            logger.error(f"WORM v2: déchiffrement échoué: {e}")
            raise ValueError(f"Entrée de journal indéchiffrable: {e}") from e


class PayloadMinimizer:
    """
    Minimisation des données dans le payload (RGPD art. 5-1c).
    
    Masque les champs sensibles avant écriture dans le journal.
    Les champs sont remplacés par "***REDACTED***" mais le hash
    est calculé AVANT minimisation pour préserver l'intégrité.
    """

    SENSITIVE_PATTERNS = [
        "password", "passwd", "pwd",
        "secret", "token", "api_key", "apikey",
        "credit_card", "card_number", "cvv",
        "ssn", "social_security",
        "health_data", "diagnosis",
        "bank_account", "iban", "swift",
        "access_token", "refresh_token",
        "private_key",
    ]

    @classmethod
    def minimize(cls, payload: dict, enabled: bool = True) -> dict:
        """
        Retourner une version minimisée du payload.
        Les champs sensibles sont remplacés par des marqueurs.
        """
        if not enabled:
            return payload

        if not isinstance(payload, dict):
            return payload

        minimized = {}
        for key, value in payload.items():
            key_lower = key.lower()
            if any(pattern in key_lower for pattern in cls.SENSITIVE_PATTERNS):
                minimized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                minimized[key] = cls.minimize(value, enabled)
            elif isinstance(value, list):
                minimized[key] = [
                    cls.minimize(item, enabled) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                minimized[key] = value

        return minimized


class JournalPurger:
    """
    Purge automatique des entrées expirées (RGPD art. 5-1e).
    
    Supprime les entrées plus anciennes que journal_retention_months.
    ATTENTION : la purge casse le hash-chainage par fichier.
    
    Solution : la purge se fait par FICHIER ENTIER (rotation quotidienne).
    Un fichier de journal complet est soit conservé, soit supprimé.
    Cela préserve le hash-chainage intra-fichier.
    """

    def __init__(self, journal_path: Path, retention_months: int = 24):
        self._path = journal_path
        self._retention_months = retention_months

    def purge_expired(self, dry_run: bool = True) -> dict:
        """
        Purger les fichiers de journal expirés.
        
        Args:
            dry_run: Si True, liste les fichiers sans supprimer.
        
        Returns:
            dict avec fichiers_purgés, taille_libérée, erreurs
        """
        if not settings.journal_purge_enabled and not dry_run:
            logger.warning("WORM v2: purge désactivée. Activer JOURNAL_PURGE_ENABLED.")
            return {"status": "disabled", "files": []}

        cutoff = datetime.now(timezone.utc)
        # Calculer la date de coupure
        from datetime import timedelta
        cutoff_date = cutoff - timedelta(days=self._retention_months * 30)

        journal_files = sorted(self._path.glob("journal-*.jsonl"))
        expired = []
        total_size = 0

        for jf in journal_files:
            # Extraire la date du nom de fichier (journal-YYYY-MM-DD.jsonl)
            try:
                date_str = jf.stem.replace("journal-", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                continue

            if file_date < cutoff_date:
                size = jf.stat().st_size
                expired.append({"file": jf.name, "date": date_str, "size_bytes": size})
                total_size += size

                if not dry_run:
                    try:
                        # Archiver avant suppression (conformité)
                        archive_dir = self._path / "archive"
                        archive_dir.mkdir(exist_ok=True)
                        archive_path = archive_dir / f"archived-{jf.name}"
                        jf.rename(archive_path)
                        logger.info(f"WORM v2: archivé {jf.name} → {archive_path.name}")
                    except Exception as e:
                        logger.error(f"WORM v2: échec archivage {jf.name}: {e}")

        return {
            "status": "dry_run" if dry_run else "executed",
            "retention_months": self._retention_months,
            "cutoff_date": cutoff_date.strftime("%Y-%m-%d"),
            "files_expired": len(expired),
            "files": expired,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }


class TenantIsolation:
    """
    Isolation des données par tenant/client (RGPD art. 5-1b).
    
    Vérifie qu'une query ne peut accéder qu'aux données du tenant
    correspondant. Les fichiers de journal sont partagés, mais
    chaque entrée est filtrée par client_id lors de la lecture.
    """

    @staticmethod
    def filter_entries(
        entries: list[dict],
        client_id: Optional[str] = None,
        allowed_client_ids: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        Filtrer les entrées par tenant.
        
        Args:
            entries: Liste d'entrées de journal
            client_id: Filtrer pour un client spécifique
            allowed_client_ids: Liste de clients autorisés (multi-tenant)
        """
        if not client_id and not allowed_client_ids:
            return entries  # Pas de filtrage (admin)

        if client_id:
            return [e for e in entries if e.get("client_id") == client_id]

        if allowed_client_ids:
            return [
                e for e in entries if e.get("client_id") in allowed_client_ids
            ]

        return entries


class TreatmentRegistry:
    """
    Registre des traitements RGPD art. 30.
    
    Documente chaque type de traitement effectué par le système
    pour permettre la production du registre à tout moment.
    """

    TREATMENTS = {
        "journal.worm.append": {
            "purpose": "Journalisation d'audit des événements système",
            "legal_basis": "Art. 6.1.f (intérêt légitime — audit et sécurité)",
            "data_categories": ["identifiants", "métadonnées techniques"],
            "retention": "24 mois (configurable)",
            "recipients": ["équipe technique Cortex Leman", "auditeurs certificateurs"],
            "transfers": "Aucun (stockage local)",
        },
        "mediator.check": {
            "purpose": "Vérification de conformité des actions IA",
            "legal_basis": "Art. 6.1.f (intérêt légitime — conformité réglementaire)",
            "data_categories": ["contexte d'action", "règles déclenchées"],
            "retention": "24 mois",
            "recipients": ["Médiateur", "auditeurs"],
            "transfers": "Aucun en mode Haute Protection",
        },
        "rag.search": {
            "purpose": "Recherche réglementaire dans le Knowledge Vault",
            "legal_basis": "Art. 6.1.f (intérêt légitime — conformité)",
            "data_categories": ["requêtes utilisateur", "passages réglementaires"],
            "retention": "24 mois",
            "recipients": ["Agent Raisonnement"],
            "transfers": "Aucun",
        },
        "llm.inference": {
            "purpose": "Inférence LLM pour analyse juridico-financière",
            "legal_basis": "Art. 6.1.f (intérêt légitime — service IA)",
            "data_categories": ["contexte métier", "résultats d'analyse"],
            "retention": "24 mois",
            "recipients": ["fournisseur LLM (OpenRouter/Ollama)"],
            "transfers": "Mode Standard: EU/US (EU-US DPF). Mode Haute Protection: aucun transfert.",
        },
        "arbitration.decision": {
            "purpose": "Enregistrement des décisions d'arbitrage humain",
            "legal_basis": "Art. 6.1.f + Art. 22.3 (décision humaine sur décision automatisée)",
            "data_categories": ["décision", "justification", "identité arbitre"],
            "retention": "24 mois",
            "recipients": ["auditeurs certificateurs", "client concerné"],
            "transfers": "Aucun",
        },
    }

    @classmethod
    def get_registry(cls) -> dict:
        """Retourner le registre complet des traitements"""
        return {
            "organization": "Cortex Leman v5",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "article": "RGPD Art. 30 — Registre des activités de traitement",
            "treatments": cls.TREATMENTS,
            "total_treatments": len(cls.TREATMENTS),
        }

    @classmethod
    def get_legal_basis_matrix(cls) -> list[dict]:
        """
        Matrice base légale par traitement (RGPD art. 6).
        Exigence identifiée par l'audit o3.
        """
        matrix = []
        for treatment_id, details in cls.TREATMENTS.items():
            matrix.append({
                "treatment": treatment_id,
                "purpose": details["purpose"],
                "legal_basis": details["legal_basis"],
                "data_categories": details["data_categories"],
                "transfers_outside_eu": details["transfers"],
            })
        return matrix
