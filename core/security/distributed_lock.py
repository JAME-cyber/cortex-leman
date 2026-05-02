"""Cortex Leman v5 — Verrous distribués

Verrouillage distribué sur les ressources partagées (dossier client).
Utilise Redis pour la coordination.
Fallback in-memory pour le développement.
"""
import time
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _try_get_redis():
    """Tenter de se connecter à Redis. Retourne None si indisponible."""
    try:
        import redis
        from core.config import settings
        client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password or None,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()  # Vérifier la connexion
        logger.info("DistributedLock: Redis connecté")
        return client
    except Exception as e:
        logger.info(f"DistributedLock: Redis non disponible, fallback in-memory ({e})")
        return None


class DistributedLock:
    """
    Verrou distribué basé sur Redis.
    En mode développement: fallback en mémoire.
    """

    def __init__(self, redis_client=None, timeout: int = 30):
        self._redis = redis_client  # None = auto-detect au premier appel
        self._timeout = timeout
        self._local_locks: dict[str, str] = {}  # Fallback in-memory
        self._initialized = False

    def _ensure_redis(self):
        """Lazy-init Redis connection."""
        if not self._initialized:
            self._redis = _try_get_redis()
            self._initialized = True

    async def acquire(self, resource: str, owner: Optional[str] = None) -> tuple[bool, str]:
        """
        Acquérir un verrou sur une ressource.
        
        Returns:
            (success, lock_id)
        """
        self._ensure_redis()
        lock_id = owner or str(uuid.uuid4())
        key = f"lock:{resource}"

        if self._redis:
            # Mode Redis
            acquired = self._redis.set(
                key, lock_id, nx=True, ex=self._timeout
            )
            if acquired:
                logger.debug(f"Verrou acquis: {resource} by {lock_id[:8]}...")
                return True, lock_id
            else:
                current = self._redis.get(key)
                logger.debug(f"Verrou refusé: {resource} (held by {current})")
                return False, ""
        else:
            # Fallback in-memory
            if resource not in self._local_locks:
                self._local_locks[resource] = lock_id
                logger.debug(f"Verrou local acquis: {resource}")
                return True, lock_id
            return False, ""

    async def release(self, resource: str, lock_id: str) -> bool:
        """Relâcher un verrou"""
        key = f"lock:{resource}"

        if self._redis:
            # Vérifier qu'on est bien le propriétaire
            current = self._redis.get(key)
            if current and current.decode() == lock_id:
                self._redis.delete(key)
                logger.debug(f"Verrou relâché: {resource}")
                return True
            return False
        else:
            if self._local_locks.get(resource) == lock_id:
                del self._local_locks[resource]
                return True
            return False

    async def is_locked(self, resource: str) -> bool:
        """Vérifier si une ressource est verrouillée"""
        key = f"lock:{resource}"
        if self._redis:
            return self._redis.exists(key)
        return resource in self._local_locks


# Singleton
dist_lock = DistributedLock()
