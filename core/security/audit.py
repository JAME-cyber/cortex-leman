"""
Cortex Leman v5 — Audit Logger

Enregistre chaque action en base pour traçabilité RGPD.
Complémentaire du journal WORM fichier.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def log_audit(
    db: Session,
    action: str,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[dict] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    tenant_id: Optional[str] = None,
    vertical: Optional[str] = None,
    intention_id: Optional[str] = None,
):
    """Enregistre un événement dans l'audit log"""
    try:
        from core.db.models import AuditLogModel

        entry = AuditLogModel(
            user_id=UUID(user_id) if user_id else None,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else None,
            details=details,
            success=success,
            error_message=error_message,
            tenant_id=tenant_id,
            vertical=vertical,
            intention_id=intention_id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        logger.error(f"Audit log échoué: {e}")
        # Ne jamais crasher l'application pour un audit log
