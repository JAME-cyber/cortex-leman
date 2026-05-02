"""
Cortex Leman v5 — NATS JetStream Client

Bus de coordination pair-à-pair asynchrone.
Fournit: publish, subscribe, request-reply, stream management.
"""
import json
import logging
from typing import Any, Callable, Optional
from datetime import datetime

import nats
from nats.js.api import StreamConfig, RetentionPolicy, StorageType

from core.config import settings
from core.bus.subjects import subjects

logger = logging.getLogger(__name__)


class NatsBus:
    """
    Client NATS JetStream pour Cortex Leman v5.
    Wraps publish/subscribe avec sérialisation JSON automatique.
    """

    def __init__(self):
        self._nc: Optional[nats.NATS] = None
        self._js: Optional[nats.js.JetStreamContext] = None
        self._subscriptions = []
        self._connected = False

    async def connect(self) -> None:
        """Connexion au serveur NATS + création du stream JetStream"""
        try:
            self._nc = await nats.connect(
                servers=[settings.nats_url],
                name=settings.nats_client_id,
                connect_timeout=3,
                reconnect_time_wait=2,
                max_reconnect_attempts=1 if settings.app_env == "development" else 60,
                error_cb=self._error_handler,
                disconnected_cb=self._disconnected_handler,
                reconnected_cb=self._reconnected_handler,
            )
            self._js = self._nc.jetstream()

            # Créer le stream s'il n'existe pas
            await self._ensure_stream()

            self._connected = True
            logger.info(f"NATS connecté: {settings.nats_url}")
        except Exception as e:
            logger.error(f"Erreur connexion NATS: {e}")
            raise

    async def _ensure_stream(self) -> None:
        """Créer ou mettre à jour le stream JetStream"""
        try:
            await self._js.stream_info(settings.nats_stream_name)
            logger.info(f"Stream '{settings.nats_stream_name}' existant")
        except nats.js.errors.NotFoundError:
            config = StreamConfig(
                name=settings.nats_stream_name,
                subjects=[settings.nats_stream_subjects],
                retention=RetentionPolicy.LIMITS,
                max_age=settings.nats_max_age_days * 86400,
                max_msg_size=settings.nats_max_msg_size,
                storage=StorageType.FILE,
                num_replicas=settings.nats_replicas,
            )
            await self._js.add_stream(config)
            logger.info(f"Stream '{settings.nats_stream_name}' créé")

    async def publish(self, subject: str, data: dict, headers: Optional[dict] = None) -> None:
        """Publier un message sur le bus"""
        if not self._connected:
            raise RuntimeError("NATS non connecté")

        payload = json.dumps({
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "source": settings.nats_client_id,
        }).encode()

        msg_headers = {}
        if headers:
            msg_headers = {f"X-{k}": str(v) for k, v in headers.items()}

        await self._js.publish(
            subject,
            payload,
            headers=msg_headers if msg_headers else None,
        )
        logger.debug(f"Publié sur {subject}: {len(payload)} bytes")

    async def subscribe(
        self,
        subject: str,
        handler: Callable,
        queue: Optional[str] = None,
        durable: Optional[str] = None,
    ) -> None:
        """
        S'abonner à un sujet avec un handler asynchrone.
        handler(signature): async def handler(data: dict, meta: dict) -> None
        """
        if not self._connected:
            raise RuntimeError("NATS non connecté")

        async def _wrapped_handler(msg):
            try:
                payload = json.loads(msg.data.decode())
                meta = {
                    "subject": msg.subject,
                    "headers": dict(msg.headers) if msg.headers else {},
                    "sequence": msg.metadata.sequence if hasattr(msg, 'metadata') else None,
                }
                await handler(payload.get("data", payload), meta)
                await msg.ack()
            except Exception as e:
                logger.error(f"Handler error on {msg.subject}: {e}")
                await msg.nak()

        sub = await self._js.subscribe(
            subject,
            queue=queue,
            cb=_wrapped_handler,
            durable=durable,
            stream=settings.nats_stream_name,
            config=nats.js.api.ConsumerConfig(
                deliver_group=queue or settings.nats_client_id,
            ),
        )
        self._subscriptions.append(sub)
        logger.info(f"Abonné à {subject} (queue={queue}, durable={durable})")

    async def request(self, subject: str, data: dict, timeout: float = 10.0) -> dict:
        """Request-reply pattern pour communication synchrone entre agents"""
        if not self._connected:
            raise RuntimeError("NATS non connecté")

        payload = json.dumps({
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "source": settings.nats_client_id,
        }).encode()

        response = await self._nc.request(subject, payload, timeout=timeout)
        return json.loads(response.data.decode())

    async def close(self) -> None:
        """Fermeture propre"""
        for sub in self._subscriptions:
            await sub.unsubscribe()
        if self._nc:
            await self._nc.close()
        self._connected = False
        logger.info("NATS déconnecté")

    # === Event Handlers ===

    async def _error_handler(self, e):
        logger.error(f"NATS error: {e}")

    async def _disconnected_handler(self):
        self._connected = False
        logger.warning("NATS déconnecté")

    async def _reconnected_handler(self):
        self._connected = True
        logger.info("NATS reconnecté")

    @property
    def connected(self) -> bool:
        return self._connected


# Singleton
bus = NatsBus()
