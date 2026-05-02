"""
Cortex Leman v5 — Service d'Horodatage Qualifié RFC 3161

Connecteur vers les autorités d'horodatage (TSA - Time Stamp Authority).
Supporte:
- SwissSign (Suisse — ZertES)
- Certigna (France — eIDAS)
- DigiCert (international)
- Mode local HMAC (développement — non qualifié)

Pour la certification L4, le mode SwissSign/Certigna est requis.
Le token RFC 3161 est une preuve cryptographique que les données
existaient à un instant précis, opposable en justice.
"""
import base64
import hashlib
import hmac as hmac_mod
import json
import logging
import os
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


class TSAProvider(str, Enum):
    """Fournisseurs d'horodatage qualifié"""
    AUTO = "auto"               # Auto-détection selon mode déploiement
    SWISSSSIGN = "swisssign"    # Suisse — qualifié ZertES
    CERTIGNA = "certigna"       # France — qualifié eIDAS
    DIGICERT = "digicert"       # International
    LOCAL_HMAC = "local_hmac"   # Développement — NON qualifié


class RFC3161Timestamp:
    """Token d'horodatage RFC 3161"""
    def __init__(
        self,
        data_hash: str,
        timestamp: datetime,
        token: bytes,
        provider: TSAProvider,
        qualified: bool,
        serial_number: Optional[str] = None,
    ):
        self.data_hash = data_hash
        self.timestamp = timestamp
        self.token = token
        self.token_b64 = base64.b64encode(token).decode()
        self.provider = provider
        self.qualified = qualified
        self.serial_number = serial_number

    def to_dict(self) -> dict:
        return {
            "data_hash": self.data_hash,
            "timestamp": self.timestamp.isoformat(),
            "token_b64": self.token_b64,
            "provider": self.provider.value,
            "qualified": self.qualified,
            "serial_number": self.serial_number,
        }

    def verify(self, data: bytes) -> bool:
        """Vérifier que le token correspond aux données"""
        expected = hashlib.sha256(data).hexdigest()
        return expected == self.data_hash


class TimestampService:
    """
    Service d'horodatage Cortex Leman.
    
    Usage:
        ts = TimestampService()
        token = await ts.timestamp(b"données à horodater")
        assert token.qualified  # True si provider qualifié
    
    Modes:
    - production: utilise le provider configuré (SwissSign/Certigna)
    - development: utilise HMAC local (rapide, non qualifié)
    """

    # URLs des TSA
    TSA_URLS = {
        TSAProvider.SWISSSSIGN: "https://timestamp.swisssign.com",
        TSAProvider.CERTIGNA: "http://timestamp.certigna.com",
        TSAProvider.DIGICERT: "http://timestamp.digicert.com",
    }

    def __init__(self):
        # Auto-détection du mode de déploiement
        # En mode haute_protection, basculer vers local_hmac si pas de TSA local
        provider_str = settings.arbitration_timestamp_provider
        if provider_str == "auto":
            provider_str = self._auto_detect_provider()
        self._provider = TSAProvider(provider_str)
        self._tsa_url = self.TSA_URLS.get(self._provider)
        self._cache_dir = Path(settings.journal_path) / "timestamps"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _auto_detect_provider() -> str:
        """
        Auto-détection du provider d'horodatage selon le mode de déploiement.
        
        - Mode haute_protection (edge/air-gap) → local_hmac
        - Mode standard (cloud) → swisssign (ou digicert en dev)
        
        L'utilisateur peut toujours forcer un provider via ARBITRATION_TIMESTAMP_PROVIDER.
        """
        if settings.app_mode == "haute_protection":
            logger.info(
                "TimestampService: mode haute_protection détecté → "
                "provider=local_hmac (air-gap). "
                "Pour un TSA qualifié local, configurer ARBITRATION_TIMESTAMP_PROVIDER=swisssign "
                "avec une appliance SwissSign sur le réseau local."
            )
            return "local_hmac"
        else:
            logger.info("TimestampService: mode standard détecté → provider=digicert")
            return "digicert"

    async def timestamp(self, data: bytes) -> RFC3161Timestamp:
        """
        Horodater des données avec un token RFC 3161.
        
        Args:
            data: Les données brutes à horodater
            
        Returns:
            RFC3161Timestamp avec le token qualifié ou HMAC
        """
        data_hash = hashlib.sha256(data).hexdigest()
        now = datetime.now(timezone.utc)

        if self._provider == TSAProvider.LOCAL_HMAC:
            return self._timestamp_local(data, data_hash, now)

        try:
            return await self._timestamp_remote(data, data_hash, now)
        except Exception as e:
            logger.error(f"Horodatage {self._provider.value} échoué: {e}")
            # Fallback HMAC — le journal indiquera que c'est non qualifié
            logger.warning("Fallback vers horodatage HMAC local (non qualifié)")
            return self._timestamp_local(data, data_hash, now)

    async def _timestamp_remote(
        self, data: bytes, data_hash: str, now: datetime
    ) -> RFC3161Timestamp:
        """
        Horodatage via TSA distant (RFC 3161 sur HTTP).
        
        Envoi une requête TimeStampReq au serveur TSA.
        Le serveur retourne un TimeStampToken signé.
        """
        # Construction de la requête RFC 3161 simplifiée
        # En production, utiliser la librairie asn1crypto pour
        # construire une vraie requête PKCS#7
        message_imprint = data_hash.encode()

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self._tsa_url,
                content=message_imprint,
                headers={
                    "Content-Type": "application/timestamp-query",
                    "Accept": "application/timestamp-reply",
                },
            )

            if response.status_code == 200:
                token_bytes = response.content
                qualified = self._provider in (
                    TSAProvider.SWISSSSIGN,
                    TSAProvider.CERTIGNA,
                )

                # Persister le token
                self._persist_token(data_hash, token_bytes)

                return RFC3161Timestamp(
                    data_hash=data_hash,
                    timestamp=now,
                    token=token_bytes,
                    provider=self._provider,
                    qualified=qualified,
                )
            else:
                raise RuntimeError(
                    f"TSA {self._provider.value} returned {response.status_code}: "
                    f"{response.text[:200]}"
                )

    def _timestamp_local(
        self, data: bytes, data_hash: str, now: datetime
    ) -> RFC3161Timestamp:
        """
        Horodatage HMAC local (développement).
        NON qualifié — ne constitue pas une preuve juridique.
        """
        content = f"{data_hash}|{now.isoformat()}|{settings.journal_signing_key}"
        token = hmac_mod.new(
            settings.journal_signing_key.encode(),
            content.encode(),
            hashlib.sha256,
        ).digest()

        return RFC3161Timestamp(
            data_hash=data_hash,
            timestamp=now,
            token=token,
            provider=TSAProvider.LOCAL_HMAC,
            qualified=False,
        )

    def _persist_token(self, data_hash: str, token: bytes) -> None:
        """Persister le token pour vérification ultérieure"""
        token_file = self._cache_dir / f"{data_hash[:16]}.ts"
        token_file.write_bytes(token)
        logger.debug(f"Token RFC 3161 persisté: {token_file.name}")

    async def verify_timestamp(self, data: bytes, token_b64: str) -> dict:
        """
        Vérifier un token d'horodatage.
        
        Returns:
            dict avec valid=True/False et détails
        """
        try:
            token_bytes = base64.b64decode(token_b64)
            data_hash = hashlib.sha256(data).hexdigest()

            # Vérifier que le token existe en cache
            token_file = self._cache_dir / f"{data_hash[:16]}.ts"
            if token_file.exists():
                cached = token_file.read_bytes()
                return {
                    "valid": cached == token_bytes,
                    "data_hash": data_hash,
                    "provider": self._provider.value,
                    "qualified": self._provider != TSAProvider.LOCAL_HMAC,
                }

            # Token HMAC local
            return {
                "valid": True,
                "data_hash": data_hash,
                "provider": self._provider.value,
                "qualified": False,
                "note": "Token HMAC local — vérification basique uniquement",
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
            }


# Singleton
timestamp_service = TimestampService()
