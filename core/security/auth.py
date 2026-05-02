"""
Cortex Leman v5 — Authentification JWT + RBAC

JWT (access + refresh tokens) avec:
- Rôles: admin, expert, operator, viewer
- Permissions par vertical
- Rotation de tokens
- Audit de chaque action
"""
import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import settings

logger = logging.getLogger(__name__)

# === Config JWT ===

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
API_KEY_PREFIX = "cl_"

# === Password hashing ===

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# === Pydantic schemas ===

class TokenPayload(BaseModel):
    """Payload JWT"""
    sub: str  # user_id
    email: str
    role: str = "unknown"
    tenant_id: Optional[str] = None
    verticals: list[str] = []
    exp: datetime
    iat: datetime
    type: str = "access"  # access | refresh


class TokenResponse(BaseModel):
    """Réponse après login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # secondes
    user: "UserInfo"


class UserInfo(BaseModel):
    """Info utilisateur dans le token"""
    id: str
    email: str
    full_name: str
    role: str
    primary_vertical: Optional[str] = None
    allowed_verticals: list[str] = []
    tenant_id: Optional[str] = None
    organization: Optional[str] = None


class LoginRequest(BaseModel):
    """Requête de connexion"""
    email: str
    password: str


class ApiKeyCreate(BaseModel):
    """Création de clé API"""
    name: str
    scopes: list[str] = ["read"]
    allowed_verticals: list[str] = []
    expires_days: Optional[int] = 365


class ApiKeyResponse(BaseModel):
    """Réponse création clé API"""
    id: str
    key: str  # Affiché UNE SEULE FOIS
    key_prefix: str
    name: str
    expires_at: Optional[str] = None


class UserCreate(BaseModel):
    """Création d'utilisateur (admin)"""
    email: str
    password: str
    full_name: str
    role: str = "viewer"
    organization: Optional[str] = None
    primary_vertical: Optional[str] = None
    allowed_verticals: list[str] = []


# === JWT Token management ===

def hash_token(token: str) -> str:
    """Hash un refresh token pour stockage en DB (SHA-256)."""
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user_info: UserInfo) -> str:
    """Crée un access token JWT"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_info.id),
        "email": user_info.email,
        "role": user_info.role,
        "tenant_id": user_info.tenant_id,
        "verticals": user_info.allowed_verticals,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(user_info: UserInfo) -> str:
    """Crée un refresh token JWT"""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_info.id),
        "email": user_info.email,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> TokenPayload:
    """Vérifie et décode un JWT"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise ValueError(f"Token type invalide: attendu {token_type}")
        return TokenPayload(**payload)
    except JWTError as e:
        raise ValueError(f"Token invalide: {e}")


def hash_password(password: str) -> str:
    """Hash un mot de passe (bcrypt)"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Vérifie un mot de passe"""
    return pwd_context.verify(plain, hashed)


# === API Key management ===

def generate_api_key() -> tuple[str, str]:
    """Génère une clé API. Retourne (raw_key, key_hash)."""
    raw_key = f"{API_KEY_PREFIX}{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash


def verify_api_key(raw_key: str) -> str:
    """Hash une clé API pour comparaison"""
    return hashlib.sha256(raw_key.encode()).hexdigest()


# === RBAC Permissions ===

# Matrice de permissions par rôle
PERMISSIONS = {
    "admin": {
        "users": ["create", "read", "update", "delete"],
        "intentions": ["create", "read", "update", "delete", "freeze", "unfreeze"],
        "arbitrations": ["read", "decide", "delegate"],
        "journal": ["read", "export"],
        "compliance": ["read", "generate", "export"],
        "api_keys": ["create", "read", "revoke"],
        "settings": ["read", "update"],
        "mediator": ["read", "update_rules"],
    },
    "expert": {
        "users": ["read"],
        "intentions": ["create", "read", "update"],
        "arbitrations": ["read", "decide"],
        "journal": ["read", "export"],
        "compliance": ["read", "generate"],
        "api_keys": ["create", "read", "revoke"],  # ses propres clés
        "settings": ["read"],
        "mediator": ["read"],
    },
    "operator": {
        "users": [],
        "intentions": ["create", "read"],
        "arbitrations": ["read"],
        "journal": ["read"],
        "compliance": ["read"],
        "api_keys": ["create", "read"],  # ses propres clés
        "settings": [],
        "mediator": [],
    },
    "viewer": {
        "users": [],
        "intentions": ["read"],
        "arbitrations": ["read"],
        "journal": ["read"],
        "compliance": ["read"],
        "api_keys": [],
        "settings": [],
        "mediator": [],
    },
}


def has_permission(role: str, resource: str, action: str) -> bool:
    """Vérifie si un rôle a une permission"""
    role_perms = PERMISSIONS.get(role, {})
    resource_perms = role_perms.get(resource, [])
    return action in resource_perms


def require_permission(role: str, resource: str, action: str):
    """Lève une exception si pas de permission"""
    if not has_permission(role, resource, action):
        raise PermissionError(
            f"Rôle '{role}' non autorisé: {action} sur {resource}"
        )


# === User CRUD ===

def get_user_by_email(db: Session, email: str):
    """Récupère un utilisateur par email"""
    from core.db.models import UserModel
    stmt = select(UserModel).where(UserModel.email == email)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: str):
    """Récupère un utilisateur par ID"""
    from core.db.models import UserModel
    stmt = select(UserModel).where(UserModel.id == uuid.UUID(user_id))
    return db.execute(stmt).scalar_one_or_none()


def create_user(db: Session, user_data: UserCreate) -> "UserModel":
    """Crée un nouvel utilisateur"""
    from core.db.models import UserModel, UserRole, UserStatus

    # Vérifier unicité email
    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise ValueError(f"Email déjà utilisé: {user_data.email}")

    user = UserModel(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=UserRole(user_data.role),
        status=UserStatus.ACTIVE,
        organization=user_data.organization,
        primary_vertical=user_data.primary_vertical,
        allowed_verticals=user_data.allowed_verticals or (
            [user_data.primary_vertical] if user_data.primary_vertical else []
        ),
        consent_given=True,
        consent_date=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Utilisateur créé: {user.email} ({user.role.value})")
    return user


def authenticate_user(db: Session, email: str, password: str):
    """Authentifie un utilisateur. Retourne UserModel ou None."""
    from core.db.models import UserStatus

    user = get_user_by_email(db, email)
    if not user:
        return None
    if user.status != UserStatus.ACTIVE:
        return None
    if not verify_password(password, user.password_hash):
        return None

    # Mise à jour last_login
    user.last_login = datetime.now(timezone.utc)
    user.login_count = (user.login_count or 0) + 1
    db.commit()

    return user


def user_to_info(user) -> UserInfo:
    """Convertit UserModel → UserInfo"""
    return UserInfo(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role.value if hasattr(user.role, "value") else user.role,
        primary_vertical=user.primary_vertical.value if user.primary_vertical and hasattr(user.primary_vertical, "value") else user.primary_vertical,
        allowed_verticals=user.allowed_verticals or [],
        tenant_id=user.tenant_id,
        organization=user.organization,
    )


# === Seed data ===

SEED_USERS = [
    {
        "email": "admin@cortex-leman.com",
        "password": "C0rt3xL3m4n!",  # Obligatoirement changer via env SEED_ADMIN_PASSWORD en prod
        "full_name": "Administrateur Cortex Leman",
        "role": "admin",
        "organization": "Cortex Leman SA",
        "primary_vertical": None,
        "allowed_verticals": ["comptable", "avocat", "sante", "banque", "startup", "rh"],
    },
    {
        "email": "expert@dupont-comptable.fr",
        "password": "comptable",
        "full_name": "Marie Dupont",
        "role": "expert",
        "organization": "Dupont & Associés",
        "primary_vertical": "comptable",
        "allowed_verticals": ["comptable"],
    },
    {
        "email": "avocat@martin-avocat.ch",
        "password": "avocat",
        "full_name": "Pierre Martin",
        "role": "expert",
        "organization": "Martin & Partners",
        "primary_vertical": "avocat",
        "allowed_verticals": ["avocat"],
    },
    {
        "email": "medecin@hopital-geneve.ch",
        "password": "sante",
        "full_name": "Dr. Sophie Laurent",
        "role": "expert",
        "organization": "Hôpital de Genève",
        "primary_vertical": "sante",
        "allowed_verticals": ["sante"],
    },
    {
        "email": "analyste@ubank.ch",
        "password": "banque",
        "full_name": "Thomas Müller",
        "role": "operator",
        "organization": "UBank SA",
        "primary_vertical": "banque",
        "allowed_verticals": ["banque"],
    },
    {
        "email": "cto@startup-paris.fr",
        "password": "startup",
        "full_name": "Léa Dubois",
        "role": "operator",
        "organization": "StartupParis",
        "primary_vertical": "startup",
        "allowed_verticals": ["startup"],
    },
    {
        "email": "drh@groupe-rh.fr",
        "password": "rh",
        "full_name": "Jean Moreau",
        "role": "expert",
        "organization": "Groupe RH",
        "primary_vertical": "rh",
        "allowed_verticals": ["rh"],
    },
]


def seed_users(db: Session):
    """Insère les utilisateurs de démo si la table est vide.
    
    En production, le mot de passe admin doit être fourni via
    la variable d'environnement SEED_ADMIN_PASSWORD.
    """
    import os
    from core.db.models import UserModel
    count = db.query(UserModel).count()
    if count > 0:
        logger.info(f"Users déjà existants ({count}), skip seed")
        return

    # Override du mot de passe admin via env var (obligatoire en prod)
    admin_password = os.getenv("SEED_ADMIN_PASSWORD")
    if admin_password:
        SEED_USERS[0]["password"] = admin_password
        logger.info("Mot de passe admin chargé depuis SEED_ADMIN_PASSWORD")
    elif os.getenv("APP_ENV") == "production":
        raise RuntimeError(
            "SEED_ADMIN_PASSWORD obligatoire en production! "
            "Définissez cette variable d'environnement."
        )

    for seed in SEED_USERS:
        try:
            create_user(db, UserCreate(**seed))
        except ValueError as e:
            logger.warning(f"Seed skip: {e}")

    logger.info(f"Seed terminé: {len(SEED_USERS)} utilisateurs créés")
