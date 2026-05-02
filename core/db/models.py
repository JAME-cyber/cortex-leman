"""
Cortex Leman v5 — Modèles de base de données (SQLAlchemy)

Tables:
- users: utilisateurs avec RBAC
- api_keys: clés API par utilisateur
- audit_logs: journal d'audit DB (complément du fichier WORM)
- tenants: multi-tenancy (Sprint 2.2)
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    JSON,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base SQLAlchemy pour tous les modèles"""
    pass


# === Enums ===

class UserRole(str, enum.Enum):
    """Rôles RBAC — 4 niveaux"""
    ADMIN = "admin"
    EXPERT = "expert"
    OPERATOR = "operator"
    VIEWER = "viewer"


class UserStatus(str, enum.Enum):
    """Statut utilisateur"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"


class Vertical(str, enum.Enum):
    """6 verticales réglementées"""
    COMPTABLE = "comptable"
    AVOCAT = "avocat"
    SANTE = "sante"
    BANQUE = "banque"
    STARTUP = "startup"
    RH = "rh"


class ApiKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


# === Tables ===

class UserModel(Base):
    """Utilisateur Cortex Leman"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    # Mot de passe hashé (bcrypt)
    password_hash = Column(String(255), nullable=False)
    # Profil
    full_name = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.PENDING)
    # Vertical principale
    primary_vertical = Column(Enum(Vertical), nullable=True)
    # Verticals autorisées (JSON array)
    allowed_verticals = Column(JSON, default=list)
    # Tenant (multi-tenancy Sprint 2.2)
    tenant_id = Column(String(100), nullable=True, index=True)
    # Champs PII chiffrables
    phone = Column(String(500), nullable=True)  # potentiellement chiffré
    # Métadonnées
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    # Sécurité
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(500), nullable=True)  # chiffré
    must_change_password = Column(Boolean, default=False)
    # RGPD
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime, nullable=True)
    data_retention_days = Column(Integer, default=365)
    # Token de session
    refresh_token = Column(String(500), nullable=True)

    # Relations
    api_keys = relationship("ApiKeyModel", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"


class ApiKeyModel(Base):
    """Clé API — authentification programmatique"""
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # Clé hashée (seul le hash est stocké)
    key_hash = Column(String(255), nullable=False, unique=True)
    key_prefix = Column(String(12), nullable=False)  # "cl_xxxx..." pour identification
    name = Column(String(255), nullable=False)
    status = Column(Enum(ApiKeyStatus), nullable=False, default=ApiKeyStatus.ACTIVE)
    # Permissions
    scopes = Column(JSON, default=list)  # ["read", "write", "admin"]
    allowed_verticals = Column(JSON, default=list)
    rate_limit = Column(Integer, default=100)  # req/min
    # Cycle de vie
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)
    use_count = Column(Integer, default=0)

    # Relations
    user = relationship("UserModel", back_populates="api_keys")

    def __repr__(self):
        return f"<ApiKey {self.key_prefix} ({self.status.value})>"


class AuditLogModel(Base):
    """Journal d'audit en base — complément du journal WORM fichier.
    
    Le journal WORM fichier est la source de vérité légale.
    Cette table permet des requêtes rapides pour le dashboard.
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Qui
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    # Quoi
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(255), nullable=True)
    # Où
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    # Détails
    details = Column(JSON, nullable=True)
    # Résultat
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    # Contexte
    tenant_id = Column(String(100), nullable=True, index=True)
    vertical = Column(String(50), nullable=True)
    intention_id = Column(String(255), nullable=True, index=True)
    # Horodatage
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index("ix_audit_logs_action_date", "action", "created_at"),
        Index("ix_audit_logs_user_date", "user_id", "created_at"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_email}>"


class TenantModel(Base):
    """Tenant — isolation multi-organisation (Sprint 2.2)"""
    __tablename__ = "tenants"

    id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True, unique=True)
    # Plan
    plan = Column(String(50), default="free")  # free|pro|enterprise
    max_users = Column(Integer, default=5)
    max_intentions_per_day = Column(Integer, default=100)
    # Configuration
    active_verticals = Column(JSON, default=list)
    data_residency = Column(String(10), default="EU")
    custom_rules = Column(JSON, nullable=True)
    # Métadonnées
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    owner_email = Column(String(255), nullable=False)
    # RGPD
    dpo_email = Column(String(255), nullable=True)  # Délégué Protection Données
    retention_policy_days = Column(Integer, default=365)

    def __repr__(self):
        return f"<Tenant {self.id}: {self.name}>"
