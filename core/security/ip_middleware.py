"""Middleware de capture et d'anonymisation des adresses IP pour Cortex Leman v5."""

from __future__ import annotations

import hashlib
import ipaddress
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

_ASGIApp = Callable[[Dict[str, Any], Callable[..., Awaitable[Any]], Callable[..., Awaitable[Any]]], Awaitable[None]]

# Le sel par défaut est volontairement différent à chaque démarrage du processus.
# En production, IP_HASH_SALT doit être défini avec une valeur persistante et secrète.
_STARTUP_SALT: str = secrets.token_hex(32)
_WARNED_ABOUT_EPHEMERAL_SALT: bool = False


def _get_configured_salt(settings: Optional[Any] = None) -> str:
    """Retourne le sel configuré via settings, variable d'environnement ou défaut mémoire."""
    global _WARNED_ABOUT_EPHEMERAL_SALT

    if settings is not None:
        try:
            configured_salt = getattr(settings, "IP_HASH_SALT", None)
            if configured_salt:
                return str(configured_salt)
        except Exception:
            logger.exception("Impossible de lire IP_HASH_SALT depuis les settings.")

    configured_salt = os.getenv("IP_HASH_SALT")
    if configured_salt:
        return configured_salt

    if not _WARNED_ABOUT_EPHEMERAL_SALT:
        logger.warning(
            "IP_HASH_SALT n'est pas configuré : un sel aléatoire temporaire est utilisé. "
            "Les hash IP changeront au prochain redémarrage."
        )
        _WARNED_ABOUT_EPHEMERAL_SALT = True

    return _STARTUP_SALT


def _parse_ip(value: Any) -> Optional[str]:
    """Valide une adresse IP et retourne sa représentation canonique."""
    if value is None:
        return None

    try:
        candidate = str(value).strip()
        if not candidate:
            return None

        parsed = ipaddress.ip_address(candidate)
        return str(parsed)
    except (TypeError, ValueError):
        return None


def hash_ip(ip_string: Optional[str], settings: Optional[Any] = None) -> Optional[str]:
    """
    Valide puis hache une adresse IPv4 ou IPv6 avec SHA-256.

    Le format du digest est hexadécimal, soit 64 caractères. La colonne SQL
    audit_logs.ip_address doit donc idéalement être migrée vers VARCHAR(64).
    """
    normalized_ip = _parse_ip(ip_string)
    if normalized_ip is None:
        if ip_string not in (None, ""):
            logger.warning("Adresse IP invalide ignorée lors du hash : %r", ip_string)
        return None

    try:
        salt = _get_configured_salt(settings)
        payload = f"{salt}{normalized_ip}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()
    except Exception:
        logger.exception("Erreur inattendue pendant le hash de l'adresse IP.")
        return None


def _headers_from_scope(scope: Dict[str, Any]) -> Dict[str, str]:
    """Convertit les headers ASGI en dictionnaire insensible à la casse."""
    headers: Dict[str, str] = {}

    for raw_name, raw_value in scope.get("headers", []):
        try:
            name = raw_name.decode("latin-1").lower() if isinstance(raw_name, bytes) else str(raw_name).lower()
            value = raw_value.decode("latin-1") if isinstance(raw_value, bytes) else str(raw_value)
            headers[name] = value
        except Exception:
            logger.warning("Header HTTP ignoré car il est malformé.")

    return headers


def _trusted_proxy_networks() -> List[Any]:
    """Charge les réseaux autorisés à transmettre des headers de proxy."""
    networks: List[Any] = []
    configured = os.getenv("TRUSTED_PROXY_NETWORKS", "")

    for item in configured.split(","):
        item = item.strip()
        if not item:
            continue

        try:
            networks.append(ipaddress.ip_network(item, strict=False))
        except ValueError:
            logger.error("Réseau de proxy de confiance invalide : %r", item)

    return networks


def _is_trusted_proxy(peer_ip: Optional[str]) -> bool:
    """
    Vérifie si le pair TCP immédiat est un proxy de confiance.

    Si TRUSTED_PROXY_NETWORKS n'est pas configuré, les headers de proxy sont
    acceptés pour conserver la compatibilité avec les déploiements existants.
    En production, cette variable doit être définie.
    """
    networks = _trusted_proxy_networks()
    if not networks:
        return True

    normalized_peer = _parse_ip(peer_ip)
    if normalized_peer is None:
        return False

    parsed_peer = ipaddress.ip_address(normalized_peer)
    return any(parsed_peer in network for network in networks)


def _extract_client_ip(scope: Dict[str, Any]) -> Optional[str]:
    """Extrait et valide l'adresse IP réelle du client depuis un scope ASGI."""
    headers = _headers_from_scope(scope)

    client = scope.get("client")
    peer_ip: Optional[str] = None
    if isinstance(client, (tuple, list)) and client:
        peer_ip = str(client[0])

    if _is_trusted_proxy(peer_ip):
        # X-Forwarded-For : la première adresse est le client d'origine.
        forwarded_for = headers.get("x-forwarded-for", "")
        if forwarded_for:
            for candidate in forwarded_for.split(","):
                normalized = _parse_ip(candidate)
                if normalized:
                    return normalized

        for header_name in ("cf-connecting-ip", "x-real-ip"):
            normalized = _parse_ip(headers.get(header_name))
            if normalized:
                return normalized

    return _parse_ip(peer_ip)


def get_client_ip_hash(request: Any) -> Optional[str]:
    """Retourne le hash IP placé par le middleware dans request.state.ip_hash."""
    try:
        state = getattr(request, "state", None)
        value = getattr(state, "ip_hash", None)
        return value if isinstance(value, str) and value else None
    except Exception:
        logger.exception("Impossible de récupérer request.state.ip_hash.")
        return None


class IPHashMiddleware:
    """Middleware ASGI compatible avec FastAPI et Starlette."""

    def __init__(self, app: _ASGIApp, settings: Optional[Any] = None) -> None:
        self.app = app
        self.settings = settings

    async def __call__(
        self,
        scope: Dict[str, Any],
        receive: Callable[..., Awaitable[Any]],
        send: Callable[..., Awaitable[Any]],
    ) -> None:
        """
        Calcule le hash IP et le rend disponible via request.state.ip_hash.

        Les erreurs sont absorbées afin qu'une anomalie de détection IP ne
        provoque jamais une indisponibilité de l'API.
        """
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        try:
            client_ip = _extract_client_ip(scope)
            ip_hash = hash_ip(client_ip, self.settings)

            state = scope.setdefault("state", {})
            if not isinstance(state, dict):
                logger.error("Le scope ASGI contient un état non modifiable.")
            else:
                state["ip_hash"] = ip_hash
                state["client_ip_hash"] = ip_hash
        except Exception:
            logger.exception("Erreur pendant le traitement de l'adresse IP cliente.")
            scope.setdefault("state", {})["ip_hash"] = None
            scope.setdefault("state", {})["client_ip_hash"] = None

        await self.app(scope, receive, send)


class IPAnonymizer:
    """Outil de rétention permettant d'anonymiser les anciennes traces d'audit."""

    @staticmethod
    def anonymize_old_logs(
        db_session: Any,
        days_threshold: int = 397,
        audit_model: Optional[Any] = None,
        delete: bool = False,
    ) -> int:
        """
        Anonymise ou supprime les adresses IP des logs plus anciens que le seuil.

        Args:
            db_session: Session SQLAlchemy active.
            days_threshold: Durée de conservation en jours, 397 par défaut.
            audit_model: Modèle SQLAlchemy AuditLog si disponible.
            delete: Supprime les lignes si True, sinon met ip_address à NULL.

        Returns:
            Nombre de lignes affectées.
        """
        if days_threshold < 1:
            raise ValueError("days_threshold doit être supérieur ou égal à 1.")

        cutoff = datetime.utcnow() - timedelta(days=days_threshold)

        try:
            if audit_model is not None:
                query = db_session.query(audit_model)
                query = query.filter(audit_model.created_at < cutoff)

                if delete:
                    affected = int(query.delete(synchronize_session=False))
                else:
                    affected = int(
                        query.update(
                            {audit_model.ip_address: None},
                            synchronize_session=False,
                        )
                    )
            else:
                # Fallback utile lorsque le modèle SQLAlchemy n'est pas importable
                # dans ce module. Le nom de table est fixe et non interpolé.
                if delete:
                    statement = (
                        "DELETE FROM audit_logs "
                        "WHERE created_at < :cutoff"
                    )
                else:
                    statement = (
                        "UPDATE audit_logs SET ip_address = NULL "
                        "WHERE created_at < :cutoff"
                    )

                result = db_session.execute(statement, {"cutoff": cutoff})
                affected = int(getattr(result, "rowcount", 0) or 0)

            db_session.commit()
            logger.info(
                "%d log(s) d'audit traité(s) par la rétention IP, seuil=%s jours, suppression=%s.",
                affected,
                days_threshold,
                delete,
            )
            return affected

        except Exception:
            logger.exception("Échec du job d'anonymisation des anciens logs d'audit.")
            try:
                db_session.rollback()
            except Exception:
                logger.exception("Échec du rollback après erreur de rétention.")
            return 0
