"""
Sandbox freemium Cortex Leman v5.

La sandbox favorise l'acquisition par contenu et l'essai autonome, mais conserve
les garde-fous : quotas, mode Haute Protection local only, rétention maximale de
7 jours, watermark DEMO, Médiateur et journal WORM obligatoires.
"""

from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from typing import Any, Callable, Mapping
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


LEGAL_DISCLAIMERS: tuple[str, ...] = (
    "Sandbox gratuite : usage démonstration uniquement, watermark DEMO.",
    "Mode Haute Protection local only : ne pas envoyer de données réelles sans validation contractuelle et technique.",
    "Rétention maximale 7 jours ; aucune persistance durable par cette classe.",
    "Secret professionnel art. 321 CP, RGPD et LPD à respecter.",
    "Cortex Leman assiste l'expert régulé et ne rend aucune décision finale automatique.",
    "Le Médiateur et le journal WORM restent requis pour tout parcours de confiance.",
)


class QuotaExceededError(RuntimeError):
    """Erreur levée lorsqu'un quota freemium est dépassé."""


class QuotaPolicy(BaseModel):
    """Politique de quotas freemium."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    intentions_per_month: int = Field(default=10, ge=1, le=100)
    arbitrations_per_month: int = Field(default=2, ge=0, le=20)
    retention_days: int = Field(default=7, ge=1, le=7)
    high_protection_local_only: bool = Field(default=True)
    durable_persistence_allowed: bool = Field(default=False)
    watermark: str = Field(default="DEMO")

    @model_validator(mode="after")
    def enforce_safety(self) -> QuotaPolicy:
        """Verrouille les invariants de sécurité freemium."""
        if not self.high_protection_local_only:
            raise ValueError("Le freemium doit rester en mode Haute Protection local only")
        if self.durable_persistence_allowed:
            raise ValueError("La persistance durable est interdite en sandbox freemium")
        if self.retention_days > 7:
            raise ValueError("La rétention freemium ne peut pas dépasser 7 jours")
        return self


class QuotaUsage(BaseModel):
    """Consommation mensuelle des quotas."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    month: str
    intentions_used: int = Field(default=0, ge=0)
    arbitrations_used: int = Field(default=0, ge=0)
    resets_at: datetime


class SandboxRecord(BaseModel):
    """Enregistrement volatile watermarqué en sandbox."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(default_factory=lambda: f"sandbox-record-{uuid4().hex[:16]}")
    account_id: str
    kind: str
    payload: dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime
    watermark: str = Field(default="DEMO")
    mode: str = Field(default="HAUTE_PROTECTION_LOCAL_ONLY")
    mediator_required: bool = Field(default=True)
    worm_journal_required: bool = Field(default=True)
    human_arbitration_enabled: bool = Field(default=True)
    durable_persistence: bool = Field(default=False)
    disclaimers: list[str] = Field(default_factory=lambda: list(LEGAL_DISCLAIMERS))

    @model_validator(mode="after")
    def enforce_trust_controls(self) -> SandboxRecord:
        """Empêche la création d'un record qui affaiblit la chaîne de confiance."""
        if not self.mediator_required or not self.worm_journal_required:
            raise ValueError("SandboxRecord doit exiger Médiateur et journal WORM")
        if self.durable_persistence:
            raise ValueError("SandboxRecord ne peut pas être durablement persisté")
        if self.watermark != "DEMO":
            raise ValueError("SandboxRecord freemium doit porter le watermark DEMO")
        return self


class FreemiumSandbox:
    """Sandbox gratuite à quotas, volatile et compatible Haute Protection."""

    def __init__(
        self,
        *,
        account_id: str | None = None,
        quota_policy: QuotaPolicy | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialise une sandbox en mémoire, sans persistance durable."""
        self.account_id = account_id or f"freemium-{uuid4().hex[:12]}"
        self.policy = quota_policy or QuotaPolicy()
        self._now_fn = now_fn or (lambda: datetime.now(UTC))
        self._records: dict[str, SandboxRecord] = {}
        self._usage = self._new_usage(self._now_fn())
        self._lock = asyncio.Lock()

    @property
    def usage(self) -> QuotaUsage:
        """Retourne l'usage courant."""
        self._ensure_current_month()
        return self._usage.model_copy(deep=True)

    async def submit_intention(self, intention: Mapping[str, Any]) -> SandboxRecord:
        """
        Soumet une intention sandbox.

        L'intention est watermarquée, bornée par quota et marquée comme devant
        passer par le Médiateur et le journal WORM. Aucun routage réel n'est
        contourné ou simulé comme décision finale.
        """
        async with self._lock:
            self._purge_expired_locked()
            self._ensure_current_month()
            if self._usage.intentions_used >= self.policy.intentions_per_month:
                raise QuotaExceededError("Quota mensuel d'intentions freemium dépassé")

            payload = self._watermark_payload(dict(intention))
            payload["trust"] = self._trust_payload(payload.get("trust"))

            record = SandboxRecord(
                account_id=self.account_id,
                kind="intention",
                payload=payload,
                expires_at=self._now_fn() + timedelta(days=self.policy.retention_days),
                watermark=self.policy.watermark,
            )
            self._records[record.id] = record
            self._usage.intentions_used += 1
            return record.model_copy(deep=True)

    async def request_arbitration(self, arbitration_case: Mapping[str, Any]) -> SandboxRecord:
        """
        Crée un dossier d'arbitrage humain sandbox.

        Même en freemium, le gel/dégel reste conditionné à un humain ; cette méthode
        ne produit pas de décision automatique.
        """
        async with self._lock:
            self._purge_expired_locked()
            self._ensure_current_month()
            if self._usage.arbitrations_used >= self.policy.arbitrations_per_month:
                raise QuotaExceededError("Quota mensuel d'arbitrages freemium dépassé")

            payload = self._watermark_payload(dict(arbitration_case))
            payload["trust"] = self._trust_payload(payload.get("trust"))
            payload["arbitration"] = {
                **dict(payload.get("arbitration", {})),
                "human_required": True,
                "automatic_final_decision": False,
            }

            record = SandboxRecord(
                account_id=self.account_id,
                kind="arbitration",
                payload=payload,
                expires_at=self._now_fn() + timedelta(days=self.policy.retention_days),
                watermark=self.policy.watermark,
            )
            self._records[record.id] = record
            self._usage.arbitrations_used += 1
            return record.model_copy(deep=True)

    def remaining_quotas(self) -> dict[str, int]:
        """Retourne les quotas restants pour le mois courant."""
        self._ensure_current_month()
        return {
            "intentions": max(0, self.policy.intentions_per_month - self._usage.intentions_used),
            "arbitrations": max(0, self.policy.arbitrations_per_month - self._usage.arbitrations_used),
        }

    def records(self) -> tuple[SandboxRecord, ...]:
        """Retourne les records non expirés, en copie défensive."""
        self._purge_expired_locked()
        return tuple(record.model_copy(deep=True) for record in self._records.values())

    def purge_expired(self) -> int:
        """Supprime les records expirés et retourne le nombre supprimé."""
        before = len(self._records)
        self._purge_expired_locked()
        return before - len(self._records)

    def export_watermarked(self) -> dict[str, Any]:
        """Exporte l'état sandbox watermarqué pour affichage UX ou contenu acquisition."""
        self._purge_expired_locked()
        return {
            "account_id": self.account_id,
            "mode": "HAUTE_PROTECTION_LOCAL_ONLY",
            "watermark": self.policy.watermark,
            "quota_policy": self.policy.model_dump(mode="json"),
            "usage": self.usage.model_dump(mode="json"),
            "remaining": self.remaining_quotas(),
            "records": [record.model_dump(mode="json") for record in self.records()],
            "disclaimers": list(LEGAL_DISCLAIMERS),
        }

    def _trust_payload(self, existing: Any) -> dict[str, Any]:
        """Construit le bloc de confiance obligatoire."""
        base = dict(existing) if isinstance(existing, Mapping) else {}
        base.update(
            {
                "mediator_required": True,
                "worm_journal_required": True,
                "human_arbitration_enabled": True,
                "high_protection_local_only": True,
                "durable_persistence": False,
                "retention_days": self.policy.retention_days,
                "watermark": self.policy.watermark,
                "automatic_final_decision": False,
            }
        )
        return base

    def _watermark_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Applique le watermark DEMO à un payload."""
        copy = deepcopy(payload)
        copy["watermark"] = self.policy.watermark
        copy["demo"] = True
        copy["legal_disclaimers"] = list(LEGAL_DISCLAIMERS)
        return copy

    def _new_usage(self, now: datetime) -> QuotaUsage:
        """Crée un compteur mensuel."""
        next_month = (now.replace(day=28) + timedelta(days=4)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return QuotaUsage(
            month=now.strftime("%Y-%m"),
            intentions_used=0,
            arbitrations_used=0,
            resets_at=next_month,
        )

    def _ensure_current_month(self) -> None:
        """Réinitialise les quotas au changement de mois."""
        now = self._now_fn()
        if self._usage.month != now.strftime("%Y-%m"):
            self._usage = self._new_usage(now)

    def _purge_expired_locked(self) -> None:
        """Purge les données expirées ; aucune persistance durable n'est réalisée."""
        now = self._now_fn()
        expired = [record_id for record_id, record in self._records.items() if record.expires_at <= now]
        for record_id in expired:
            del self._records[record_id]
