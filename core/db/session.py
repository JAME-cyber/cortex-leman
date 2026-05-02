"""
Cortex Leman v5 — Session Base de Données

SQLAlchemy async avec PostgreSQL (prod) / SQLite (dev).
Supporte Alembic pour les migrations.
"""
import logging
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from core.config import settings

logger = logging.getLogger(__name__)

# === Engine & Session ===

_engine = None
_async_engine = None
_SessionLocal = None
_AsyncSessionLocal = None


def get_database_url() -> str:
    """URL de connexion base de données"""
    url = settings.database_url
    if url:
        return url
    # Fallback SQLite pour dev
    return f"sqlite:///{settings.journal_path}/../cortex-leman.db"


def get_async_database_url() -> str:
    """URL async (PostgreSQL → asyncpg, SQLite → aiosqlite)"""
    url = get_database_url()
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return url


def init_db():
    """Initialise la connexion DB (sync — pour Alembic & dev)"""
    global _engine, _SessionLocal

    url = get_database_url()
    logger.info(f"Initialisation DB: {_mask_url(url)}")

    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    _engine = create_engine(
        url,
        connect_args=connect_args,
        echo=settings.app_env == "development",
        pool_pre_ping=True,
        # SQLite: StaticPool pour dev single-thread
        poolclass=StaticPool if url.startswith("sqlite") else None,
    )

    _SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=_engine,
    )

    # Créer les tables si pas de migration (dev uniquement)
    if settings.app_env == "development":
        from core.db.models import Base
        Base.metadata.create_all(bind=_engine)
        logger.info("Tables créées (mode dev)")


def init_async_db():
    """Initialise la connexion DB async"""
    global _async_engine, _AsyncSessionLocal

    url = get_async_database_url()
    logger.info(f"Initialisation DB async: {_mask_url(url)}")

    connect_args = {}
    if "sqlite" in url:
        connect_args["check_same_thread"] = False

    _async_engine = create_async_engine(
        url,
        connect_args=connect_args,
        echo=settings.app_env == "development",
        pool_pre_ping=True,
    )

    _AsyncSessionLocal = sessionmaker(
        _async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def get_session() -> Session:
    """Dépendance FastAPI — session sync"""
    if _SessionLocal is None:
        init_db()
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dépendance FastAPI — session async"""
    if _AsyncSessionLocal is None:
        init_async_db()
    async with _AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_engine():
    """Récupère l'engine sync"""
    if _engine is None:
        init_db()
    return _engine


def _mask_url(url: str) -> str:
    """Masque le mot de passe dans l'URL"""
    if "@" in url:
        parts = url.split("://", 1)
        if len(parts) == 2:
            proto, rest = parts
            if "@" in rest:
                creds, after = rest.rsplit("@", 1)
                if ":" in creds:
                    user, _ = creds.split(":", 1)
                    return f"{proto}://{user}:***@{after}"
    return url
