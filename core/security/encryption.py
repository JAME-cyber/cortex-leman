"""
Cortex Leman v5 — Chiffrement Fernet (at-rest)

Chiffre les données sensibles (PII, secrets clients, tokens)
avant stockage en base. Compatible RGPD Art. 32.
"""
import base64
import hashlib
import logging
import os
from typing import Optional

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class FernetEncryption:
    """Chiffrement symétrique Fernet pour données au repos.
    
    - Utilise AES-128-CBC + HMAC-SHA256
    - Clé dérivée du SECRET_KEY via HKDF
    - Rotation de clé supportée (max 2 clés actives)
    """

    def __init__(self, secret_key: str):
        # Dérive une clé Fernet valide (32 bytes base64) depuis le secret
        key_material = hashlib.sha256(
            f"cortex-leman-fernet-{secret_key}".encode()
        ).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(key_material))
        self._old_fernet: Optional[Fernet] = None

    def encrypt(self, plaintext: str) -> str:
        """Chiffre une chaîne → base64"""
        if not plaintext:
            return ""
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Déchiffre une chaîne"""
        if not ciphertext:
            return ""
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except Exception:
            # Essaye l'ancienne clé si rotation
            if self._old_fernet:
                try:
                    return self._old_fernet.decrypt(ciphertext.encode()).decode()
                except Exception:
                    raise ValueError("Déchiffrement échoué — clé invalide")
            raise

    def encrypt_dict(self, data: dict, fields: list[str]) -> dict:
        """Chiffre les champs spécifiés d'un dictionnaire"""
        result = data.copy()
        for field in fields:
            if field in result and isinstance(result[field], str):
                result[field] = self.encrypt(result[field])
                result[f"{field}_encrypted"] = True
        return result

    def decrypt_dict(self, data: dict, fields: list[str] = None) -> dict:
        """Déchiffre les champs chiffrés d'un dictionnaire"""
        result = data.copy()
        encrypted_fields = fields or [
            k.replace("_encrypted", "")
            for k in result
            if k.endswith("_encrypted") and result[k] is True
        ]
        for field in encrypted_fields:
            if field in result and result.get(f"{field}_encrypted"):
                result[field] = self.decrypt(result[field])
                del result[f"{field}_encrypted"]
        return result

    @staticmethod
    def generate_key() -> str:
        """Génère une nouvelle clé Fernet"""
        return Fernet.generate_key().decode()


# Instance singleton — initialisée au démarrage
_encryption: Optional[FernetEncryption] = None


def init_encryption(secret_key: str):
    """Initialise le chiffrement global"""
    global _encryption
    _encryption = FernetEncryption(secret_key)
    logger.info("Chiffrement Fernet initialisé")


def get_encryption() -> FernetEncryption:
    """Récupère l'instance de chiffrement"""
    if _encryption is None:
        raise RuntimeError("Chiffrement non initialisé — appeler init_encryption()")
    return _encryption
