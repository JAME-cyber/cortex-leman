"""
Cortex Leman v5 — FastAPI Dependencies pour Auth

Dépendances injectables pour:
- Vérification JWT
- Vérification API Key
- Contrôle RBAC
- Audit logging
- Rate limiting
"""
import hashlib
import logging
import time
from typing import Optional
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Header, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.db.session import get_session
from core.security.auth import (
    verify_token,
    verify_api_key as hash_api_key,
    user_to_info,
    has_permission,
    TokenPayload,
    UserInfo,
)

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(auto_error=False)


# ── Rate Limiter (in-memory, par IP) ──────────────────────────

class RateLimiter:
    """
    Rate limiter simple par clé (IP ou email).
    Sliding window en mémoire.

    En production: utiliser Redis avec sliding window.
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self._max = max_requests
        self._window = window_seconds
        self._attempts: dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Vérifier si la requête est autorisée. Retourne False si limit dépassé."""
        now = time.monotonic()
        cutoff = now - self._window

        if key not in self._attempts:
            self._attempts[key] = []

        # Nettoyer les anciennes entrées
        self._attempts[key] = [t for t in self._attempts[key] if t > cutoff]

        if len(self._attempts[key]) >= self._max:
            return False

        self._attempts[key].append(now)
        return True

    def reset(self, key: str) -> None:
        """Réinitialiser le compteur pour une clé (après succès)."""
        self._attempts.pop(key, None)


# Rate limiters par usage
login_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)  # 5 req/min par IP
api_rate_limiter = RateLimiter(max_requests=100, window_seconds=60)   # 100 req/min par IP

class AuthContext:
    """Contexte d'authentification injecté dans les routes"""
    def __init__(
        self,
        user_id: str,
        email: str,
        role: str,
        tenant_id: Optional[str] = None,
        verticals: list[str] = None,
        auth_method: str = "jwt",
    ):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.tenant_id = tenant_id
        self.verticals = verticals or []
        self.auth_method = auth_method

    def has_permission(self, resource: str, action: str) -> bool:
        return has_permission(self.role, resource, action)

    def require_permission(self, resource: str, action: str):
        if not self.has_permission(resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé: {action} sur {resource} nécessite le rôle adéquat",
            )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_session),
) -> AuthContext:
    """Dépendance: authentifie via JWT Bearer token"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_token(credentials.credentials, token_type="access")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérifier que l'utilisateur existe toujours en base
    from core.security.auth import get_user_by_id
    user = get_user_by_id(db, payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur désactivé",
        )
    from core.db.models import UserStatus
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte suspendu",
        )

    return AuthContext(
        user_id=str(user.id),
        email=user.email,
        role=user.role.value if hasattr(user.role, "value") else user.role,
        tenant_id=user.tenant_id,
        verticals=user.allowed_verticals or [],
        auth_method="jwt",
    )


def get_api_key_user(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_session),
) -> AuthContext:
    """Dépendance: authentifie via clé API"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API requise (header X-API-Key)",
        )

    # Hash la clé fournie et chercher en base
    key_hash = hash_api_key(x_api_key)
    from core.db.models import ApiKeyModel, UserModel, ApiKeyStatus
    from sqlalchemy import select

    stmt = (
        select(ApiKeyModel)
        .where(ApiKeyModel.key_hash == key_hash)
        .where(ApiKeyModel.status == ApiKeyStatus.ACTIVE)
    )
    api_key = db.execute(stmt).scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou révoquée",
        )

    # Vérifier expiration
    if api_key.expires_at:
        from datetime import datetime, timezone
        if api_key.expires_at < datetime.now(timezone.utc):
            api_key.status = ApiKeyStatus.EXPIRED
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Clé API expirée",
            )

    # Incrémenter usage
    api_key.use_count = (api_key.use_count or 0) + 1
    api_key.last_used = datetime.now(timezone.utc)
    db.commit()

    # Charger l'utilisateur
    user = db.execute(
        select(UserModel).where(UserModel.id == api_key.user_id)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur associé introuvable",
        )

    return AuthContext(
        user_id=str(user.id),
        email=user.email,
        role=user.role.value if hasattr(user.role, "value") else user.role,
        tenant_id=user.tenant_id,
        verticals=api_key.allowed_verticals or user.allowed_verticals or [],
        auth_method="api_key",
    )


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_session),
) -> Optional[AuthContext]:
    """Dépendance: authentifie si possible, sinon None (routes publiques)"""
    if credentials:
        try:
            return get_current_user(credentials, db)
        except HTTPException:
            pass
    if x_api_key:
        try:
            return get_api_key_user(x_api_key, db)
        except HTTPException:
            pass
    return None


def require_role(*roles: str):
    """Factory: dépendance qui vérifie le rôle"""
    def checker(auth: AuthContext = Depends(get_current_user)) -> AuthContext:
        if auth.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôle requis: {', '.join(roles)}. Actuel: {auth.role}",
            )
        return auth
    return checker


def require_vertical(vertical: str):
    """Factory: dépendance qui vérifie l'accès à une vertical"""
    def checker(auth: AuthContext = Depends(get_current_user)) -> AuthContext:
        # Admin a accès à tout
        if auth.role == "admin":
            return auth
        if vertical not in auth.verticals:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès non autorisé à la vertical: {vertical}",
            )
        return auth
    return checker


# Alias pratiques
require_admin = require_role("admin")
require_expert = require_role("admin", "expert")
require_operator = require_role("admin", "expert", "operator")
