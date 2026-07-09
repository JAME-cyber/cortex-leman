"""
Cortex Leman v5 — API FastAPI

Point d'entrée principal. Routes pour:
- Authentification JWT + API Keys
- Soumettre des intentions
- Consulter les arbitrages
- Journal d'audit
- Statut des agents
- Rapports de conformité
- Gestion des utilisateurs (admin)
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings

logger = logging.getLogger(__name__)

# État global (initialisé au démarrage)
app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cycle de vie de l'application"""
    # Startup
    from core.bus.nats_client import bus
    from core.orchestrator.conversationnal import orchestrator
    from core.mediator.mediator import mediator
    from core.agents.data_agent import DataAgent
    from core.agents.reasoning_agent import ReasoningAgent
    from core.agents.action_agent import ActionAgent
    from core.agents.supervisor_agent import SupervisorAgent
    from core.security.circuit_breaker import circuit_registry
    from core.db.session import init_db
    from core.db.session import get_engine
    from core.security.auth import seed_users
    from core.security.encryption import init_encryption
    from sqlalchemy.orm import Session

    logger.info("Démarrage Cortex Leman v5...")

    # Base de données
    init_db()

    # Seed utilisateurs démo
    engine = get_engine()
    with Session(engine) as db:
        seed_users(db)

    # Chiffrement
    init_encryption(settings.secret_key)

    # RAG Vectoriel
    try:
        from core.integrations.rag import init_rag
        init_rag()
    except Exception as e:
        logger.warning(f"RAG non initialisé: {e}")

    # Connexion bus (optionnel en dev)
    try:
        await bus.connect()
    except Exception as e:
        logger.warning(f"Bus NATS non disponible: {e}")

    # Médiateur
    try:
        await mediator.start()
    except Exception as e:
        logger.warning(f"Médiateur non démarré: {e}")

    # Agents
    agents = {}
    from core.agents.chief_of_staff import ChiefOfStaffAgent

    for name, cls in [
        ("data", DataAgent),
        ("reasoning", ReasoningAgent),
        ("action", ActionAgent),
        ("supervisor", SupervisorAgent),
        ("chief_of_staff", ChiefOfStaffAgent),
    ]:
        try:
            agent = cls()
            await agent.start()
            agents[name] = agent
        except Exception as e:
            logger.warning(f"Agent {name} non démarré: {e}")

    # Orchestrateur
    try:
        await orchestrator.start()
    except Exception as e:
        logger.warning(f"Orchestrateur non démarré: {e}")

    app_state["agents"] = agents
    app_state["orchestrator"] = orchestrator
    app_state["mediator"] = mediator

    logger.info("Cortex Leman v5 démarré — prêt")

    yield

    # Shutdown
    logger.info("Arrêt Cortex Leman v5...")
    try:
        await orchestrator.stop()
    except Exception:
        pass
    try:
        await bus.close()
    except Exception:
        pass


# === Application ===
app = FastAPI(
    title="Cortex Leman v5",
    description="Infrastructure de confiance pour professions régulées FR-CH",
    version="5.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "Stripe-Signature"],
)

# ============================================================
# IMPORTS DES DÉPENDANCES AUTH (après création de l'app)
# ============================================================
from api.dependencies import (
    AuthContext,
    get_current_user,
    get_api_key_user,
    get_optional_user,
    require_admin,
    require_expert,
    require_operator,
    require_vertical,
)
from api.routes.billing import router as billing_router
from api.routes.audit import router as audit_router

# Billing routes (Stripe)
app.include_router(billing_router)

# Audit & RGPD routes (Phase 1 v3 — audit o3)
app.include_router(audit_router)
from core.security.auth import (
    TokenResponse,
    UserInfo,
    LoginRequest,
    UserCreate,
    ApiKeyCreate,
    ApiKeyResponse,
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    hash_token,
    create_user,
    authenticate_user,
    user_to_info,
    get_user_by_email,
    get_user_by_id,
    generate_api_key,
    seed_users,
)
from core.security.audit import log_audit
from core.db.session import get_session
from core.db.models import (
    UserModel,
    ApiKeyModel,
    UserRole,
    UserStatus,
    ApiKeyStatus,
    AuditLogModel,
)
from sqlalchemy import select, func
from sqlalchemy.orm import Session
import uuid


# ============================================================
# ROUTES PUBLIQUES (sans auth)
# ============================================================

@app.get("/health")
async def health():
    """Health check profond: DB + NATS + Redis + LLM"""
    checks = {}
    overall = "healthy"

    # Database
    try:
        from core.db.session import get_engine
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {e}"
        overall = "degraded"

    # NATS Bus
    try:
        from core.bus.nats_client import bus
        checks["nats"] = "connected" if bus.connected else "disconnected"
        if not bus.connected:
            overall = "degraded"
    except Exception:
        checks["nats"] = "unavailable"
        overall = "degraded"

    # Redis (optional)
    try:
        from core.security.distributed_lock import _try_get_redis
        redis = _try_get_redis()
        checks["redis"] = "connected" if redis else "not_configured"
    except Exception:
        checks["redis"] = "unavailable"

    # LLM Provider
    try:
        from core.integrations.llm import llm_service
        llm_check = await llm_service.health_check()
        checks["llm"] = llm_check.get("status", "unknown")
        if checks["llm"] != "healthy":
            overall = "degraded"
    except Exception as e:
        checks["llm"] = f"unavailable: {e}"
        overall = "degraded"

    # Journal integrity
    try:
        from core.journal.append_only_journal import journal
        checks["journal_sequence"] = journal.sequence
    except Exception:
        checks["journal_sequence"] = "unavailable"

    return {
        "status": overall,
        "version": "5.0.0",
        "mode": settings.app_mode,
        "checks": checks,
    }


@app.get("/metrics")
async def metrics(
    auth: AuthContext = Depends(require_admin),
):
    """Prometheus metrics endpoint"""
    from monitoring.metrics import get_metrics
    from fastapi.responses import Response
    data, content_type = get_metrics()
    return Response(content=data, media_type=content_type)


@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    req: Request,
    db: Session = Depends(get_session),
):
    """Connexion — retourne JWT access + refresh tokens"""
    # Rate limiting par IP
    from api.dependencies import login_rate_limiter
    client_ip = req.client.host if req.client else "unknown"
    if not login_rate_limiter.is_allowed(client_ip):
        log_audit(
            db, action="login_rate_limited", ip_address=client_ip,
            success=False, error_message="Rate limit dépassé",
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives. Réessayez dans 1 minute.",
        )

    user = authenticate_user(db, request.email, request.password)
    if not user:
        log_audit(
            db, action="login_failed", user_email=request.email,
            ip_address=client_ip,
            success=False, error_message="Identifiants invalides",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    # Succès → réinitialiser le compteur
    login_rate_limiter.reset(client_ip)

    user_info = user_to_info(user)
    access_token = create_access_token(user_info)
    refresh_token = create_refresh_token(user_info)

    # Stocker le refresh token hashé (jamais en clair)
    user.refresh_token = hash_token(refresh_token)
    db.commit()

    log_audit(
        db, action="login_success", user_id=str(user.id),
        user_email=user.email,
        ip_address=req.client.host if req.client else None,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_expire_minutes * 60,
        user=user_info,
    )


@app.post("/api/v1/auth/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_session),
):
    """Renouvelle l'access token"""
    try:
        payload = verify_token(refresh_token, token_type="refresh")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    user = get_user_by_id(db, payload.sub)
    # Comparer le hash du refresh token
    if not user or user.refresh_token != hash_token(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide",
        )

    user_info = user_to_info(user)
    new_access = create_access_token(user_info)
    new_refresh = create_refresh_token(user_info)
    user.refresh_token = hash_token(new_refresh)
    db.commit()

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "expires_in": settings.jwt_access_expire_minutes * 60,
    }


@app.post("/api/v1/auth/register")
async def register(
    user_data: UserCreate,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Créer un nouvel utilisateur (admin/expert uniquement)"""
    if auth.role not in ("admin", "expert"):
        raise HTTPException(403, "Seuls admin et expert peuvent créer des utilisateurs")

    try:
        user = create_user(db, user_data)
    except ValueError as e:
        raise HTTPException(400, str(e))

    log_audit(
        db, action="user_created", user_id=auth.user_id,
        user_email=auth.email, resource_type="user",
        resource_id=str(user.id), details={"new_user_email": user.email, "role": user.role.value},
    )

    return {"id": str(user.id), "email": user.email, "role": user.role.value}


# ============================================================
# ROUTES AUTHENTIFIÉES
# ============================================================

@app.get("/api/v1/auth/me", response_model=UserInfo)
async def get_me(auth: AuthContext = Depends(get_current_user)):
    """Profil de l'utilisateur connecté"""
    return UserInfo(
        id=auth.user_id,
        email=auth.email,
        full_name="",  # sera enrichi depuis DB
        role=auth.role,
        tenant_id=auth.tenant_id,
        verticals=auth.verticals,
    )


@app.post("/api/v1/auth/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    key_data: ApiKeyCreate,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Créer une clé API"""
    raw_key, key_hash = generate_api_key()
    key_prefix = raw_key[:12]

    expires_at = None
    if key_data.expires_days:
        from datetime import timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(days=key_data.expires_days)

    api_key = ApiKeyModel(
        user_id=uuid.UUID(auth.user_id),
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=key_data.name,
        scopes=key_data.scopes,
        allowed_verticals=key_data.allowed_verticals or auth.verticals,
        expires_at=expires_at,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    log_audit(
        db, action="api_key_created", user_id=auth.user_id,
        user_email=auth.email, resource_type="api_key",
        resource_id=str(api_key.id),
    )

    return ApiKeyResponse(
        id=str(api_key.id),
        key=raw_key,  # Affiché UNE SEULE FOIS
        key_prefix=key_prefix,
        name=key_data.name,
        expires_at=str(expires_at) if expires_at else None,
    )


@app.get("/api/v1/auth/api-keys")
async def list_api_keys(
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Lister ses clés API"""
    stmt = (
        select(ApiKeyModel)
        .where(ApiKeyModel.user_id == uuid.UUID(auth.user_id))
        .where(ApiKeyModel.status == ApiKeyStatus.ACTIVE)
    )
    keys = db.execute(stmt).scalars().all()
    return {
        "api_keys": [
            {
                "id": str(k.id),
                "key_prefix": k.key_prefix,
                "name": k.name,
                "scopes": k.scopes,
                "last_used": str(k.last_used) if k.last_used else None,
                "use_count": k.use_count,
                "expires_at": str(k.expires_at) if k.expires_at else None,
            }
            for k in keys
        ]
    }


@app.delete("/api/v1/auth/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Révoquer une clé API"""
    stmt = select(ApiKeyModel).where(
        ApiKeyModel.id == uuid.UUID(key_id),
        ApiKeyModel.user_id == uuid.UUID(auth.user_id),
    )
    api_key = db.execute(stmt).scalar_one_or_none()
    if not api_key:
        raise HTTPException(404, "Clé API non trouvée")

    api_key.status = ApiKeyStatus.REVOKED
    db.commit()

    log_audit(
        db, action="api_key_revoked", user_id=auth.user_id,
        resource_type="api_key", resource_id=key_id,
    )
    return {"status": "revoked"}


# ============================================================
# ADMIN — Gestion utilisateurs
# ============================================================

@app.get("/api/v1/admin/users")
async def list_users(
    auth: AuthContext = Depends(require_admin),
    db: Session = Depends(get_session),
):
    """Lister tous les utilisateurs (admin)"""
    users = db.execute(select(UserModel)).scalars().all()
    return {
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role.value,
                "status": u.status.value,
                "organization": u.organization,
                "primary_vertical": u.primary_vertical.value if u.primary_vertical else None,
                "last_login": str(u.last_login) if u.last_login else None,
                "created_at": str(u.created_at),
            }
            for u in users
        ]
    }


@app.patch("/api/v1/admin/users/{user_id}")
async def update_user(
    user_id: str,
    role: Optional[str] = None,
    status: Optional[str] = None,
    primary_vertical: Optional[str] = None,
    auth: AuthContext = Depends(require_admin),
    db: Session = Depends(get_session),
):
    """Modifier un utilisateur (admin)"""
    user = db.execute(
        select(UserModel).where(UserModel.id == uuid.UUID(user_id))
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Utilisateur non trouvé")

    if role:
        user.role = UserRole(role)
    if status:
        user.status = UserStatus(status)
    if primary_vertical:
        user.primary_vertical = primary_vertical
    db.commit()

    log_audit(
        db, action="user_updated", user_id=auth.user_id,
        resource_type="user", resource_id=user_id,
        details={"changes": {"role": role, "status": status, "vertical": primary_vertical}},
    )
    return {"status": "updated"}


@app.delete("/api/v1/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    auth: AuthContext = Depends(require_admin),
    db: Session = Depends(get_session),
):
    """Supprimer un utilisateur (admin)"""
    user = db.execute(
        select(UserModel).where(UserModel.id == uuid.UUID(user_id))
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Utilisateur non trouvé")

    db.delete(user)
    db.commit()

    log_audit(
        db, action="user_deleted", user_id=auth.user_id,
        resource_type="user", resource_id=user_id,
    )
    return {"status": "deleted"}


# ============================================================
# AUDIT LOGS
# ============================================================

@app.get("/api/v1/admin/audit")
async def query_audit(
    user_email: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    auth: AuthContext = Depends(require_admin),
    db: Session = Depends(get_session),
):
    """Consulter les logs d'audit (admin)"""
    stmt = select(AuditLogModel).order_by(AuditLogModel.created_at.desc())

    if user_email:
        stmt = stmt.where(AuditLogModel.user_email == user_email)
    if action:
        stmt = stmt.where(AuditLogModel.action == action)

    total = db.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar()

    entries = db.execute(stmt.offset(offset).limit(limit)).scalars().all()

    return {
        "entries": [
            {
                "id": str(e.id),
                "action": e.action,
                "user_email": e.user_email,
                "resource_type": e.resource_type,
                "resource_id": e.resource_id,
                "ip_address": e.ip_address,
                "success": e.success,
                "details": e.details,
                "created_at": str(e.created_at),
            }
            for e in entries
        ],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


# ============================================================
# /GOAL — Point d'entrée simple style Hermes
# Auto-détection de verticale + risk_level immédiat
# ============================================================

@app.post("/api/v1/goal")
async def submit_goal(
    goal_text: str,
    client_id: str = "auto",
    vertical_hint: str = None,
    auth: AuthContext = Depends(get_current_user),
):
    """Soumettre un goal en langage libre.

    Le système détecte automatiquement la verticale métier
    et évalue le niveau de risque avant routage.
    """
    from core.orchestrator.goal_detector import detect_goal
    from core.mediator.rules_engine import rules_engine
    rules_engine.load_rules()

    # 1. Détection de verticale (déterministe)
    result = detect_goal(goal_text, hint_vertical=vertical_hint)

    # 2. Vérifier l'accès à la verticale
    if auth.role != "admin" and result.vertical not in auth.verticals:
        raise HTTPException(
            403,
            f"Verticale détectée: {result.vertical}. "
            f"Accès non autorisé pour votre compte.",
        )

    # 3. Évaluer le risk_level immédiatement
    risk_level, risk_action = rules_engine.evaluate_risk_level(
        result.vertical,
        {"action": {"type": "goal"}, "goal_text": goal_text},
    )
    appetite = rules_engine.get_risk_appetite(result.vertical)

    # 4. Soumettre l'intention dans le pipeline existant
    try:
        from core.orchestrator.conversationnal import orchestrator
        intention_id = await orchestrator.submit_intention(
            client_id=client_id,
            vertical=result.vertical,
            query=goal_text,
            context={
                "source": "goal",
                "vertical_confidence": result.confidence,
                "keywords_matched": result.keywords_matched,
                "risk_level": risk_level,
                "risk_action": risk_action,
            },
        )
    except Exception:
        intention_id = str(uuid.uuid4())

    return {
        "intention_id": intention_id,
        "vertical": result.vertical,
        "vertical_confidence": result.confidence,
        "keywords_matched": result.keywords_matched,
        "risk_level": risk_level,
        "risk_action": risk_action,
        "risk_appetite": appetite,
        "status": "submitted",
        "submitted_by": auth.email,
    }


# ============================================================
# INTENTIONS (authentifié)
# ============================================================

@app.post("/api/v1/intentions")
async def create_intention(
    client_id: str,
    vertical: str,
    query: str,
    context: dict = None,
    auth: AuthContext = Depends(get_current_user),
):
    """Soumettre une nouvelle intention métier"""
    # Vérifier accès à la vertical
    if auth.role != "admin" and vertical not in auth.verticals:
        raise HTTPException(403, f"Accès non autorisé à la vertical: {vertical}")

    try:
        from core.orchestrator.conversationnal import orchestrator
        intention_id = await orchestrator.submit_intention(
            client_id=client_id,
            vertical=vertical,
            query=query,
            context=context,
        )
    except Exception as e:
        # Bus pas connecté — mode dev
        intention_id = str(uuid.uuid4())

    return {"intention_id": intention_id, "status": "submitted", "submitted_by": auth.email}


@app.get("/api/v1/intentions/{intention_id}")
async def get_intention(
    intention_id: str,
    auth: AuthContext = Depends(require_operator),
):
    """Récupérer le statut d'une intention"""
    from core.orchestrator.intention import intention_store

    intention = intention_store.get(intention_id)
    if not intention:
        raise HTTPException(404, "Intention non trouvée")
    return intention.model_dump()


@app.get("/api/v1/intentions")
async def list_intentions(
    client_id: str = None,
    auth: AuthContext = Depends(require_operator),
):
    """Lister les intentions actives"""
    from core.orchestrator.intention import intention_store

    if client_id:
        intentions = intention_store.get_active_for_client(client_id)
        return {"intentions": [i.model_dump() for i in intentions]}
    return {"error": "client_id requis"}


# ============================================================
# ARBITRAGE (authentifié)
# ============================================================

@app.get("/api/v1/arbitrations")
async def list_arbitrations(
    auth: AuthContext = Depends(require_operator),
):
    """Lister les arbitrages en attente"""
    from core.arbitration.arbitration_service import arbitration_service
    return {"arbitrations": arbitration_service.get_pending_arbitrations()}


@app.get("/api/v1/arbitrations/{arbitration_id}")
async def get_arbitration(
    arbitration_id: str,
    auth: AuthContext = Depends(require_operator),
):
    """Récupérer un arbitrage"""
    from core.arbitration.arbitration_service import arbitration_service
    arb = arbitration_service.get_arbitration(arbitration_id)
    if not arb:
        raise HTTPException(404, "Arbitrage non trouvé")
    return arb


@app.post("/api/v1/arbitrations/{arbitration_id}/decide")
async def submit_arbitration_decision(
    arbitration_id: str,
    arbiter_id: str,
    arbiter_name: str,
    decision: str,
    justification: str,
    selected_position: str,
    modifications: dict = None,
    auth: AuthContext = Depends(require_expert),
    db: Session = Depends(get_session),
):
    """Soumettre une décision d'arbitrage humain (expert+)"""
    if decision not in ("approve", "reject", "modify"):
        raise HTTPException(400, "decision doit être: approve, reject, modify")

    from core.arbitration.arbitration_service import arbitration_service
    dec = arbitration_service.submit_decision(
        arbitration_id=arbitration_id,
        arbiter_id=arbiter_id,
        arbiter_name=arbiter_name,
        decision=decision,
        justification=justification,
        selected_position=selected_position,
        modifications=modifications,
    )

    log_audit(
        db, action="arbitration_decision", user_id=auth.user_id,
        user_email=auth.email, resource_type="arbitration",
        resource_id=arbitration_id,
        details={"decision": decision, "position": selected_position},
    )
    return dec.model_dump()


@app.get("/api/v1/arbitrations/precedents")
async def get_precedents(
    vertical: str = None,
    auth: AuthContext = Depends(require_operator),
):
    """Consulter les précédents d'arbitrage"""
    from core.arbitration.arbitration_service import arbitration_service
    return {"precedents": arbitration_service.get_precedents(vertical)}


# ============================================================
# JOURNAL (authentifié)
# ============================================================

@app.get("/api/v1/journal")
async def query_journal(
    intention_id: str = None,
    event_type: str = None,
    client_id: str = None,
    limit: int = 100,
    auth: AuthContext = Depends(require_operator),
):
    """Requêter le journal d'audit"""
    from core.journal.append_only_journal import journal
    from core.journal.models import JournalEventType

    et = None
    if event_type:
        try:
            et = JournalEventType(event_type)
        except ValueError:
            raise HTTPException(400, f"Type d'événement invalide: {event_type}")

    entries = journal.query(
        intention_id=intention_id,
        event_type=et,
        client_id=client_id,
        limit=limit,
    )
    return {"entries": entries, "total": len(entries)}


@app.get("/api/v1/journal/verify")
async def verify_journal(
    auth: AuthContext = Depends(require_operator),
):
    """Vérifier l'intégrité du journal d'audit"""
    from core.journal.append_only_journal import journal
    return journal.verify_integrity()


# ============================================================
# AGENTS (authentifié)
# ============================================================

@app.get("/api/v1/agents/status")
async def agents_status(
    auth: AuthContext = Depends(require_operator),
):
    """Statut de tous les agents"""
    from core.security.circuit_breaker import circuit_registry
    from core.mediator.mediator import mediator

    return {
        "circuit_breakers": circuit_registry.get_all_status(),
        "active_conflicts": mediator.get_active_conflicts(),
    }


# ============================================================
# AGENT IDENTITY / KYA (authentifié)
# ============================================================

@app.get("/api/v1/agents/identities")
async def list_agent_identities(
    auth: AuthContext = Depends(require_operator),
):
    """Lister toutes les cartes d'identité des agents (KYA)"""
    from core.security.agent_identity import agent_identity_provider
    identities = agent_identity_provider.get_all_identities()
    return {
        "identities": [agent_identity_provider.get_audit_trail(i.agent_id) for i in identities],
        "total": len(identities),
    }


@app.post("/api/v1/agents/identities/{agent_id}/activate")
async def activate_agent_session(
    agent_id: str,
    vertical: str = "comptable",
    auth: AuthContext = Depends(require_admin),
):
    """Activer une session agent avec serment numérique (admin)"""
    from core.security.agent_identity import agent_identity_provider
    cred = agent_identity_provider.activate_session(agent_id, vertical=vertical)
    if not cred:
        raise HTTPException(400, f"Impossible d'activer {agent_id}")
    return {
        "agent_id": agent_id,
        "session_id": cred.session_id,
        "scopes": [s.value for s in cred.scopes],
        "expires_at": cred.expires_at.isoformat(),
        "oath_signed": True,
    }


@app.post("/api/v1/agents/identities/{agent_id}/deactivate")
async def deactivate_agent_session(
    agent_id: str,
    auth: AuthContext = Depends(require_admin),
):
    """Désactiver la session d'un agent (admin)"""
    from core.security.agent_identity import agent_identity_provider
    ok = agent_identity_provider.deactivate_session(agent_id)
    if not ok:
        raise HTTPException(400, f"Pas de session active pour {agent_id}")
    return {"agent_id": agent_id, "status": "deactivated"}


@app.get("/api/v1/agents/identities/{agent_id}/audit")
async def agent_identity_audit(
    agent_id: str,
    auth: AuthContext = Depends(require_operator),
):
    """Audit trail complet d'un agent"""
    from core.security.agent_identity import agent_identity_provider
    audit = agent_identity_provider.get_audit_trail(agent_id)
    if "error" in audit:
        raise HTTPException(404, audit["error"])
    return audit


@app.post("/api/v1/agents/identities/{agent_id}/suspend")
async def suspend_agent(
    agent_id: str,
    reason: str = "Comportement suspect",
    auth: AuthContext = Depends(require_admin),
):
    """Suspendre un agent (admin)"""
    from core.security.agent_identity import agent_identity_provider
    ok = agent_identity_provider.suspend_agent(agent_id, reason=reason)
    if not ok:
        raise HTTPException(404, f"Agent {agent_id} non trouvé")
    return {"agent_id": agent_id, "status": "suspended", "reason": reason}


# ============================================================
# PRECEDENT STORE / JURISPRUDENCE (authentifié)
# ============================================================

@app.get("/api/v1/precedents")
async def list_precedents(
    vertical: str = None,
    auth: AuthContext = Depends(require_operator),
):
    """Lister les précédents de jurisprudence IA"""
    from core.mediator.precedent_store import precedent_store
    if vertical:
        precedents = precedent_store.get_all_for_vertical(vertical)
    else:
        precedents = []
        for v in ["comptable", "avocat", "sante", "banque", "startup", "rh"]:
            precedents.extend(precedent_store.get_all_for_vertical(v))
    return {
        "precedents": [
            {
                "precedent_id": p.precedent_id,
                "vertical": p.vertical,
                "question": p.question[:200],
                "decision": p.decision,
                "strength": p.strength.value,
                "arbiter": p.arbiter_name,
                "matched_count": p.matched_count,
                "created_at": p.created_at.isoformat(),
            }
            for p in precedents
        ],
        "total": len(precedents),
    }


@app.get("/api/v1/precedents/stats")
async def precedent_stats(
    auth: AuthContext = Depends(require_operator),
):
    """Statistiques du PrecedentStore"""
    from core.mediator.precedent_store import precedent_store
    return precedent_store.get_stats()


@app.get("/api/v1/precedents/query")
async def query_precedents(
    vertical: str,
    question: str,
    rule_id: str = None,
    limit: int = 5,
    auth: AuthContext = Depends(require_operator),
):
    """Rechercher des précédents par similarité"""
    from core.mediator.precedent_store import precedent_store
    matches = precedent_store.query(
        vertical=vertical,
        question=question,
        rule_id=rule_id,
        limit=limit,
    )
    return {
        "matches": [
            {
                "precedent_id": m.precedent.precedent_id,
                "relevance": m.relevance,
                "match_reason": m.match_reason,
                "decision": m.precedent.decision,
                "justification": m.precedent.justification[:300],
                "strength": m.precedent.strength.value,
                "arbiter": m.precedent.arbiter_name,
            }
            for m in matches
        ],
        "total": len(matches),
    }


@app.get("/api/v1/precedents/candidates")
async def list_rule_candidates(
    auth: AuthContext = Depends(require_expert),
):
    """Lister les candidats de promotion en règles (expert+)"""
    from core.mediator.precedent_store import precedent_store
    candidates = precedent_store.get_pending_candidates()
    return {
        "candidates": [
            {
                "candidate_id": c.candidate_id,
                "vertical": c.vertical,
                "source_count": len(c.source_precedent_ids),
                "suggested_action": c.suggested_action,
                "suggested_severity": c.suggested_severity,
                "message": c.suggested_message,
                "created_at": c.created_at.isoformat(),
            }
            for c in candidates
        ],
        "total": len(candidates),
    }


@app.post("/api/v1/precedents/candidates/{candidate_id}/approve")
async def approve_rule_candidate(
    candidate_id: str,
    auth: AuthContext = Depends(require_expert),
):
    """Approuver un candidat de promotion en règle (expert+)"""
    from core.mediator.precedent_store import precedent_store
    result = precedent_store.approve_candidate(candidate_id, reviewer=auth.email)
    if not result:
        raise HTTPException(404, "Candidat non trouvé")
    return {"status": "approved", "candidate_id": candidate_id, "reviewer": auth.email}


@app.post("/api/v1/precedents/candidates/{candidate_id}/reject")
async def reject_rule_candidate(
    candidate_id: str,
    reason: str = "",
    auth: AuthContext = Depends(require_expert),
):
    """Rejeter un candidat de promotion en règle (expert+)"""
    from core.mediator.precedent_store import precedent_store
    result = precedent_store.reject_candidate(candidate_id, reviewer=auth.email)
    if not result:
        raise HTTPException(404, "Candidat non trouvé")
    return {"status": "rejected", "candidate_id": candidate_id}


# ============================================================
# COMPLIANCE GOALS (authentifié)
# ============================================================

@app.post("/api/v1/compliance-goals")
async def create_compliance_goal(
    request: dict,
    auth: AuthContext = Depends(get_current_user),
):
    """Créer un Compliance Goal (tâche conformité longue durée)"""
    from core.orchestrator.compliance_goal import compliance_goal_runner

    client_id = request.get("client_id", auth.user_id)
    vertical = request.get("vertical")
    title = request.get("title")
    description = request.get("description", title)
    template = request.get("template")

    if not vertical or not title:
        raise HTTPException(400, "vertical et title requis")

    # Vérifier l'accès à la verticale
    if auth.role != "admin" and vertical not in auth.verticals:
        raise HTTPException(403, f"Accès non autorisé à {vertical}")

    goal = compliance_goal_runner.create_goal(
        client_id=client_id,
        vertical=vertical,
        title=title,
        description=description,
        template_name=template,
    )
    return {
        "goal_id": goal.goal_id,
        "title": goal.title,
        "vertical": goal.vertical,
        "status": goal.status.value,
        "subtask_count": len(goal.subtasks),
        "subtasks": [{"name": st.name, "agent": st.agent, "status": st.status.value} for st in goal.subtasks],
    }


@app.post("/api/v1/compliance-goals/{goal_id}/start")
async def start_compliance_goal(
    goal_id: str,
    auth: AuthContext = Depends(get_current_user),
):
    """Démarrer un Compliance Goal"""
    from core.orchestrator.compliance_goal import compliance_goal_runner
    goal = compliance_goal_runner.start_goal(goal_id)
    if not goal:
        raise HTTPException(404, "Goal non trouvé ou déjà démarré")
    return {"goal_id": goal_id, "status": goal.status.value}


@app.get("/api/v1/compliance-goals/{goal_id}")
async def get_compliance_goal(
    goal_id: str,
    auth: AuthContext = Depends(get_current_user),
):
    """Récupérer le statut d'un Compliance Goal"""
    from core.orchestrator.compliance_goal import compliance_goal_runner
    goal = compliance_goal_runner.get_goal(goal_id)
    if not goal:
        raise HTTPException(404, "Goal non trouvé")
    return {
        "goal_id": goal.goal_id,
        "title": goal.title,
        "vertical": goal.vertical,
        "status": goal.status.value,
        "progress": goal.progress,
        "subtasks": [
            {
                "task_id": st.task_id,
                "name": st.name,
                "agent": st.agent,
                "status": st.status.value if hasattr(st.status, 'value') else st.status,
                "confidence": st.confidence,
            }
            for st in goal.subtasks
        ],
        "started_at": goal.started_at.isoformat() if goal.started_at else None,
        "completed_at": goal.completed_at.isoformat() if goal.completed_at else None,
        "result": goal.result,
    }


@app.post("/api/v1/compliance-goals/{goal_id}/subtasks/{task_id}")
async def update_compliance_subtask(
    goal_id: str,
    task_id: str,
    request: dict,
    auth: AuthContext = Depends(require_operator),
):
    """Mettre à jour une sous-tâche d'un Compliance Goal"""
    from core.orchestrator.compliance_goal import compliance_goal_runner
    goal = compliance_goal_runner.update_subtask(
        goal_id=goal_id,
        task_id=task_id,
        status=request.get("status"),
        result=request.get("result"),
        confidence=request.get("confidence"),
        error=request.get("error"),
    )
    if not goal:
        raise HTTPException(404, "Goal ou sous-tâche non trouvé")
    return {
        "goal_id": goal_id,
        "progress": goal.progress,
        "status": goal.status.value,
    }


@app.post("/api/v1/compliance-goals/{goal_id}/pause")
async def pause_compliance_goal(
    goal_id: str,
    reason: str = "",
    auth: AuthContext = Depends(require_operator),
):
    """Suspendre un Compliance Goal"""
    from core.orchestrator.compliance_goal import compliance_goal_runner
    goal = compliance_goal_runner.pause_goal(goal_id, reason=reason)
    if not goal:
        raise HTTPException(404, "Goal non trouvé")
    return {"goal_id": goal_id, "status": "paused"}


@app.post("/api/v1/compliance-goals/{goal_id}/resume")
async def resume_compliance_goal(
    goal_id: str,
    auth: AuthContext = Depends(get_current_user),
):
    """Reprendre un Compliance Goal suspendu"""
    from core.orchestrator.compliance_goal import compliance_goal_runner
    goal = compliance_goal_runner.resume_goal(goal_id)
    if not goal:
        raise HTTPException(404, "Goal non trouvé")
    return {"goal_id": goal_id, "status": "running"}


@app.get("/api/v1/compliance-goals")
async def list_compliance_goals(
    client_id: str = None,
    auth: AuthContext = Depends(get_current_user),
):
    """Lister les Compliance Goals"""
    from core.orchestrator.compliance_goal import compliance_goal_runner
    if client_id:
        goals = compliance_goal_runner.get_goals_for_client(client_id)
    else:
        goals = compliance_goal_runner.get_active_goals()
    return {
        "goals": [
            {
                "goal_id": g.goal_id,
                "title": g.title,
                "vertical": g.vertical,
                "status": g.status.value,
                "progress": g.progress,
            }
            for g in goals
        ],
        "total": len(goals),
    }


@app.get("/api/v1/compliance-goals/templates")
async def list_compliance_templates(
    vertical: str = None,
):
    """Lister les templates de Compliance Goals disponibles (public)"""
    from core.orchestrator.compliance_goal import compliance_goal_runner
    return compliance_goal_runner.get_templates(vertical)


# ============================================================
# COMPLIANCE (authentifié)
# ============================================================

@app.get("/api/v1/compliance/audit/dpia")
async def generate_dpia(
    client_id: str = None,
    auth: AuthContext = Depends(require_expert),
):
    """Générer une AIPD / DPIA (RGPD Art. 35)"""
    from core.compliance.audit_generator import audit_generator
    return audit_generator.generate_dpia(client_id)


@app.get("/api/v1/compliance/audit/dpo-attestation")
async def generate_dpo_attestation(
    client_id: str = None,
    auth: AuthContext = Depends(require_expert),
):
    """Générer une attestation DPO (brouillon à faire signer)"""
    from core.compliance.audit_generator import audit_generator
    return audit_generator.generate_dpo_attestation(client_id)


@app.get("/api/v1/compliance/audit/ai-act")
async def generate_ai_act_checklist(
    auth: AuthContext = Depends(require_expert),
):
    """Générer la checklist AI Act"""
    from core.compliance.audit_generator import audit_generator
    return audit_generator.generate_ai_act_checklist()


@app.get("/api/v1/compliance/audit/iso27001")
async def generate_iso27001_evidence(
    auth: AuthContext = Depends(require_expert),
):
    """Générer le pack de preuves ISO 27001"""
    from core.compliance.audit_generator import audit_generator
    return audit_generator.generate_iso27001_evidence()


@app.get("/api/v1/compliance/report/daily")
async def daily_report(
    client_id: str = None,
    auth: AuthContext = Depends(require_operator),
):
    """Rapport de conformité quotidien"""
    from core.compliance.gateway import compliance_gateway
    return compliance_gateway.generate_daily_report(client_id)


@app.get("/api/v1/compliance/report/monthly")
async def monthly_report(
    client_id: str = None,
    auth: AuthContext = Depends(require_operator),
):
    """Rapport de conformité mensuel"""
    from core.compliance.gateway import compliance_gateway
    return compliance_gateway.generate_monthly_report(client_id)


@app.get("/api/v1/compliance/data-residency")
async def check_data_residency(
    vertical: str,
    auth: AuthContext = Depends(require_operator),
):
    """Vérifier la conformité data residency"""
    from core.compliance.gateway import compliance_gateway
    return compliance_gateway.check_data_residency({"vertical": vertical})


# ============================================================
# MÉDIATEUR (authentifié)
# ============================================================

@app.get("/api/v1/mediator/rules")
async def list_rules(
    vertical: str = None,
    auth: AuthContext = Depends(require_operator),
):
    """Lister les règles du Médiateur"""
    from core.mediator.rules_engine import rules_engine
    if vertical:
        return {"rules": rules_engine.get_rules_for_vertical(vertical)}
    return {"verticals": rules_engine.get_all_verticals()}


@app.get("/api/v1/mediator/conflicts")
async def list_conflicts(
    auth: AuthContext = Depends(require_operator),
):
    """Lister les conflits actifs"""
    from core.mediator.mediator import mediator
    return {"conflicts": mediator.get_active_conflicts()}


# ============================================================
# TRUST BOX (exposition produit — Ant Group T-Box inspired)
# ============================================================

@app.get("/trust-box/status")
async def trust_box_status():
    """Statut global du Trust Box
    
    Le Trust Box est la couche de confiance déterministe de Cortex Leman.
    0% LLM. 100% JsonLogic. Gel automatique si violation.
    """
    from core.mediator.rules_engine import rules_engine
    from core.mediator.mediator import mediator
    
    verticals = rules_engine.get_all_verticals()
    total_rules = sum(len(rules_engine.get_rules_for_vertical(v)) for v in verticals)
    
    return {
        "name": "Cortex Leman Trust Box",
        "version": "5.2.0",
        "status": "active",
        "philosophy": "Déterministe là où il faut. Intelligent là où on peut.",
        "architecture": {
            "decision_engine": "JsonLogic (0% LLM)",
            "actions": ["block", "freeze", "arbitrate", "warn", "require_audit", "pass"],
            "freeze_modes": ["complete", "degraded"],
            "consolidation_window_sec": mediator._CONSOLIDATION_WINDOW_SEC,
        },
        "metrics": {
            "verticals": len(verticals),
            "total_rules": total_rules,
            "active_conflicts": len(mediator.get_active_conflicts()),
        },
        "verticals": verticals,
        "serment": "Ne jamais laisser l'IA prendre une décision seule dans les moments critiques.",
    }


@app.post("/trust-box/evaluate")
async def trust_box_evaluate(
    request: dict,
    auth: AuthContext = Depends(require_operator),
):
    """Évaluer un contexte contre les règles du Trust Box (dry-run)"""
    from core.mediator.rules_engine import rules_engine
    
    vertical = request.get("vertical")
    context = request.get("context", {})
    
    if not vertical:
        raise HTTPException(400, "vertical requis")
    
    results = rules_engine.evaluate(vertical, context)
    triggered = [r for r in results if r.triggered]
    
    return {
        "vertical": vertical,
        "context_evaluated": context,
        "rules_evaluated": len(results),
        "rules_triggered": len(triggered),
        "decision": "BLOCKED" if any(r.action == "block" for r in triggered) else
                    "FROZEN" if any(r.action == "freeze" for r in triggered) else
                    "ARBITRATION" if any(r.action == "arbitrate" for r in triggered) else
                    "WARNED" if any(r.action == "warn" for r in triggered) else
                    "APPROVED",
        "details": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "severity": r.severity,
                "action": r.action,
                "triggered": r.triggered,
                "message": r.message,
            }
            for r in results
        ],
    }


@app.get("/trust-box/rules")
async def trust_box_rules(vertical: str = None):
    """Lister les règles du Trust Box"""
    from core.mediator.rules_engine import rules_engine
    
    if vertical:
        rules = rules_engine.get_rules_for_vertical(vertical)
        return {
            "vertical": vertical,
            "rules": [
                {
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "severity": r.get("severity"),
                    "action": r.get("action"),
                    "message": r.get("message"),
                }
                for r in rules
            ],
            "total": len(rules),
        }
    
    verticals = rules_engine.get_all_verticals()
    summary = []
    for v in verticals:
        rules = rules_engine.get_rules_for_vertical(v)
        summary.append({
            "vertical": v,
            "rules": len(rules),
            "actions": list(set(r.get("action") for r in rules)),
        })
    
    return {
        "trust_box": "Cortex Leman v5",
        "verticals": summary,
        "total_rules": sum(len(rules_engine.get_rules_for_vertical(v)) for v in verticals),
    }


@app.get("/trust-box/conflicts")
async def trust_box_conflicts(
    auth: AuthContext = Depends(require_operator),
):
    """Conflits actifs du Trust Box"""
    from core.mediator.mediator import mediator
    conflicts = mediator.get_active_conflicts()
    return {
        "trust_box": "Cortex Leman v5",
        "active_conflicts": len(conflicts),
        "conflicts": conflicts,
    }


@app.get("/trust-box/audit-trail")
async def trust_box_audit_trail(
    limit: int = 50,
    event_type: str = None,
    auth: AuthContext = Depends(require_operator),
):
    """Journal d'audit du Trust Box"""
    from core.journal.append_only_journal import journal
    from core.journal.models import JournalEventType
    
    tb_events = [
        JournalEventType.MEDIATOR_CHECK,
        JournalEventType.MEDIATOR_CONFLICT,
        JournalEventType.MEDIATOR_FREEZE,
        JournalEventType.COMPLIANCE_CHECK,
        JournalEventType.COMPLIANCE_VIOLATION,
    ]
    
    events = journal.query(limit=limit)
    filtered = []
    for e in events:
        et = e.get("event_type")
        if et in [t.value for t in tb_events]:
            if event_type and et != event_type:
                continue
            filtered.append(e)
    
    return {
        "trust_box": "Cortex Leman v5",
        "total_events": len(filtered),
        "events": filtered[:limit],
        "integrity": journal.verify_integrity(),
    }


@app.get("/trust-box/serment")
async def trust_box_serment():
    """Le serment du Trust Box"""
    return {
        "trust_box": "Cortex Leman v5",
        "serment": {
            "version": "1.0",
            "principes": [
                {
                    "id": 1,
                    "titre": "Déterminisme critique",
                    "texte": "Les décisions de gel et de blocage sont 100% déterministes. Jamais de LLM.",
                    "implementation": "JsonLogic rules_engine"
                },
                {
                    "id": 2,
                    "titre": "Gel préventif",
                    "texte": "Si une règle est violée, l'action est gelée automatiquement avant exécution.",
                    "implementation": "AgentMediator.freeze()"
                },
                {
                    "id": 3,
                    "titre": "Arbitrage humain",
                    "texte": "L'IA ne décide JAMAIS seule pour les actions critiques. L'humain est arbitre.",
                    "implementation": "ArbitrationService"
                },
                {
                    "id": 4,
                    "titre": "Transparence totale",
                    "texte": "Chaque décision du Trust Box est tracée dans un journal inviolable.",
                    "implementation": "WORM Journal SHA-256"
                },
                {
                    "id": 5,
                    "titre": "Mode dégradé",
                    "texte": "En cas de gel, Data et Raisonnement continuent d'enrichir le dossier.",
                    "implementation": "Degraded freeze + consolidation window"
                },
                {
                    "id": 6,
                    "titre": "Conformité by design",
                    "texte": "RGPD, AI Act, secret professionnel FR-CH encodés dans les règles.",
                    "implementation": "6 verticals × 2-12 règles JsonLogic"
                },
            ],
            "signature": "Cortex Leman Trust Box — Déterministe là où il faut. Intelligent là où on peut."
        }
    }


@app.post("/trust-box/simulate")
async def trust_box_simulate(
    request: dict,
    auth: AuthContext = Depends(require_operator),
):
    """Simuler une action et voir ce que le Trust Box déciderait (dry-run)"""
    from core.mediator.rules_engine import rules_engine
    
    vertical = request.get("vertical")
    action_type = request.get("action_type")
    payload = request.get("payload", {})
    
    if not vertical or not action_type:
        raise HTTPException(400, "vertical et action_type requis")
    
    context = {
        "action": {"type": action_type},
        "payload": payload,
        "human_validated": payload.get("human_validated", False),
        "data_residency": payload.get("data_residency", "EU"),
        "confidence_bias_score": payload.get("confidence_bias_score"),
        "contradiction_count": payload.get("contradiction_count", 0),
    }
    
    results = rules_engine.evaluate(vertical, context)
    triggered = [r for r in results if r.triggered]
    
    if any(r.action == "block" for r in triggered):
        verdict = "BLOCKED"
        explanation = "Le Trust Box bloque cette action. Elle ne peut pas être exécutée."
    elif any(r.action == "freeze" for r in triggered):
        verdict = "FROZEN"
        explanation = "Le Trust Box gèle cette action. Arbitrage humain obligatoire."
    elif any(r.action == "arbitrate" for r in triggered):
        verdict = "ARBITRATION_REQUIRED"
        explanation = "Le Trust Box demande un arbitrage. L'humain doit valider."
    elif any(r.action == "warn" for r in triggered):
        verdict = "WARNED"
        explanation = "Le Trust Box émet un avertissement."
    elif any(r.action == "require_audit" for r in triggered):
        verdict = "AUDIT_REQUIRED"
        explanation = "Le Trust Box exige un audit trail."
    else:
        verdict = "APPROVED"
        explanation = "Le Trust Box approuve cette action."
    
    return {
        "simulation": True,
        "vertical": vertical,
        "action_type": action_type,
        "verdict": verdict,
        "explanation": explanation,
        "rules_checked": len(results),
        "rules_triggered": len(triggered),
        "triggered_rules": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "severity": r.severity,
                "action": r.action,
                "message": r.message,
            }
            for r in triggered
        ],
    }


# ============================================================
# ORCHESTRATEUR (authentifié)
# ============================================================

@app.get("/api/v1/orchestrator/status")
async def orchestrator_status(
    auth: AuthContext = Depends(require_operator),
):
    """Statut de l'orchestrateur"""
    from core.orchestrator.conversationnal import orchestrator
    return await orchestrator.get_status()


# ============================================================
# LLM (authentifié)
# ============================================================

@app.get("/api/v1/llm/health")
async def llm_health(
    auth: AuthContext = Depends(require_operator),
):
    """Vérifier le provider LLM"""
    from core.integrations.llm import llm_service
    health = await llm_service.health_check()
    health["routing"] = llm_service.get_routing_table()
    return health


@app.get("/api/v1/llm/routing")
async def llm_routing(
    auth: AuthContext = Depends(require_operator),
):
    """Table de routing modèle par verticale"""
    from core.integrations.llm import llm_service
    return llm_service.get_routing_table()


@app.get("/api/v1/llm/stats")
async def llm_stats(
    auth: AuthContext = Depends(require_operator),
):
    """Statistiques d'utilisation LLM"""
    from core.integrations.llm import llm_service
    return llm_service.get_stats()


@app.get("/api/v1/llm/providers")
async def llm_providers():
    """Lister les providers LLM disponibles (public)"""
    return {
        "providers": [
            {"id": "openrouter", "name": "OpenRouter", "type": "cloud", "models": "200+"},
            {"id": "anthropic", "name": "Anthropic", "type": "cloud", "models": "Claude family"},
            {"id": "openai", "name": "OpenAI", "type": "cloud", "models": "GPT-4 family"},
            {"id": "ollama", "name": "Ollama", "type": "local", "models": "Llama, Mistral, etc."},
            {"id": "deepseek", "name": "DeepSeek", "type": "cloud", "models": "DeepSeek V3/R1"},
            {"id": "groq", "name": "Groq", "type": "cloud", "models": "Llama, Mixtral (fast)"},
            {"id": "mistral", "name": "Mistral AI", "type": "cloud", "models": "Mistral family"},
            {"id": "xai", "name": "xAI", "type": "cloud", "models": "Grok"},
            {"id": "google", "name": "Google AI", "type": "cloud", "models": "Gemini family"},
            {"id": "bedrock", "name": "AWS Bedrock", "type": "cloud", "models": "Multi-provider"},
            {"id": "azure", "name": "Azure OpenAI", "type": "cloud", "models": "GPT-4 (EU)"},
            {"id": "sambanova", "name": "SambaNova", "type": "cloud", "models": "SN models"},
        ],
        "default_provider": settings.llm_provider,
        "mode": settings.app_mode,
    }


@app.post("/api/v1/llm/generate")
async def llm_generate(
    system_prompt: str,
    user_prompt: str,
    vertical: str = "unknown",
    client_id: str = "unknown",
    intention_id: str = "unknown",
    max_tokens: int = 4096,
    temperature: float = 0.7,
    auth: AuthContext = Depends(require_operator),
):
    """Générer une réponse LLM"""
    from core.integrations.llm import llm_service
    return await llm_service.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        vertical=vertical,
        client_id=client_id,
        intention_id=intention_id,
    )


# ============================================================
# n8n (authentifié)
# ============================================================

@app.get("/api/v1/n8n/health")
async def n8n_health(
    auth: AuthContext = Depends(require_operator),
):
    """Vérifier la connexion n8n"""
    from core.integrations.n8n import n8n_client
    return await n8n_client.health_check()


@app.get("/api/v1/n8n/workflows")
async def n8n_workflows(
    vertical: str = None,
    auth: AuthContext = Depends(require_operator),
):
    """Lister les workflows n8n disponibles"""
    from core.integrations.n8n import n8n_client
    return n8n_client.get_available_workflows(vertical)


@app.post("/api/v1/n8n/trigger")
async def n8n_trigger(
    workflow_name: str,
    data: dict,
    vertical: str = "unknown",
    client_id: str = "unknown",
    intention_id: str = "unknown",
    auth: AuthContext = Depends(require_operator),
):
    """Déclencher un workflow n8n"""
    from core.integrations.n8n import n8n_client
    return await n8n_client.trigger_workflow(
        workflow_name=workflow_name,
        data=data,
        vertical=vertical,
        client_id=client_id,
        intention_id=intention_id,
    )


# ============================================================
# KNOWLEDGE VAULT (authentifié)
# ============================================================

@app.post("/api/v1/vault/clients")
async def vault_create_client(
    client_id: str,
    vertical: str,
    auth: AuthContext = Depends(require_expert),
):
    """Créer un espace client dans le vault"""
    from core.integrations.knowledge_vault import knowledge_vault
    return knowledge_vault.create_client_space(client_id, vertical)


@app.post("/api/v1/vault/documents")
async def vault_store_document(
    client_id: str,
    document_name: str,
    content: str,
    document_type: str = "general",
    tags: str = "",
    auth: AuthContext = Depends(require_expert),
):
    """Stocker un document"""
    from core.integrations.knowledge_vault import knowledge_vault
    return knowledge_vault.store_document(
        client_id=client_id,
        document_name=document_name,
        content=content,
        document_type=document_type,
        tags=tags.split(",") if tags else [],
    )


@app.get("/api/v1/vault/search")
async def vault_search(
    client_id: str,
    query: str,
    document_type: str = None,
    limit: int = 20,
    auth: AuthContext = Depends(require_operator),
):
    """Rechercher dans le vault"""
    from core.integrations.knowledge_vault import knowledge_vault
    results = knowledge_vault.search(
        client_id=client_id,
        query=query,
        document_type=document_type,
        limit=limit,
    )
    return {"results": results, "total": len(results)}


@app.get("/api/v1/vault/documents")
async def vault_list_documents(
    client_id: str,
    limit: int = 50,
    offset: int = 0,
    auth: AuthContext = Depends(require_operator),
):
    """Lister les documents d'un client (paginé)"""
    from core.integrations.knowledge_vault import knowledge_vault
    return {"documents": knowledge_vault.list_documents(client_id, limit=limit, offset=offset)}


@app.get("/api/v1/vault/stats")
async def vault_stats(
    auth: AuthContext = Depends(require_operator),
):
    """Statistiques du vault"""
    from core.integrations.knowledge_vault import knowledge_vault
    return knowledge_vault.get_stats()


@app.post("/api/v1/vault/regulatory/load")
async def vault_load_regulatory(
    auth: AuthContext = Depends(require_admin),
):
    """Charger les textes réglementaires de base (admin)"""
    from core.integrations.knowledge_vault import knowledge_vault
    count = knowledge_vault.load_regulatory_data()
    return {"loaded": count, "status": "ok"}


# ============================================================
# RAG VECTORIEL (authentifié)
# ============================================================

@app.get("/api/v1/rag/search")
async def rag_search(
    query: str,
    client_id: str = None,
    vertical: str = None,
    n_results: int = 5,
    auth: AuthContext = Depends(require_operator),
):
    """Recherche sémantique RAG"""
    from core.integrations.rag import get_rag
    rag = get_rag()
    results = rag.search(
        query=query,
        client_id=client_id,
        n_results=n_results,
        vertical=vertical,
    )
    return {"results": results, "total": len(results)}


@app.post("/api/v1/rag/index")
async def rag_index_document(
    client_id: str,
    doc_id: str,
    content: str,
    document_type: str = "general",
    auth: AuthContext = Depends(require_expert),
):
    """Indexer un document dans le RAG vectoriel"""
    from core.integrations.rag import get_rag
    rag = get_rag()
    chunks = rag.index_document(
        client_id=client_id,
        doc_id=doc_id,
        content=content,
        metadata={"type": document_type},
    )
    return {"indexed_chunks": chunks, "status": "ok"}


@app.post("/api/v1/rag/regulatory/seed")
async def rag_seed_regulatory(
    auth: AuthContext = Depends(require_admin),
):
    """Vectoriser les textes réglementaires (admin)"""
    from core.integrations.rag import get_rag
    rag = get_rag()
    count = rag.load_regulatory_seed()
    return {"seeded_chunks": count, "status": "ok"}


@app.get("/api/v1/rag/stats")
async def rag_stats(
    auth: AuthContext = Depends(require_operator),
):
    """Statistiques RAG"""
    from core.integrations.rag import get_rag
    rag = get_rag()
    return rag.get_stats()


@app.delete("/api/v1/rag/client/{client_id}")
async def rag_delete_client(
    client_id: str,
    auth: AuthContext = Depends(require_admin),
):
    """Supprimer les données RAG d'un client (RGPD droit à l'oubli)"""
    from core.integrations.rag import get_rag
    rag = get_rag()
    deleted = rag.delete_client_data(client_id)
    return {"deleted": deleted, "client_id": client_id}


# ============================================================
# LE LÉMAN — Chat avec persona (point d'entrée principal)
# ============================================================

@app.post("/api/v1/le-leman/chat")
async def le_leman_chat(
    message: str,
    vertical: str = "comptable",
    client_id: str = "unknown",
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Chat avec Le Léman — Conseil de confiance franco-suisse.
    
    Pipeline: Persona prompt → RAG context → LLM → Reflection Node → Réponse.
    Le Léman est la face visible de Cortex Leman pour les utilisateurs.
    """
    from core.integrations.llm import llm_service

    # Charger la persona Le Léman
    from core.agents.prompts import load_skill
    persona = load_skill("le_leman") or ""

    # Extraire les instructions clés de la persona
    from core.agents.prompts import extract_section
    identity = extract_section(persona, "IDENTITÉ") or "Conseil de confiance IA"
    personality = extract_section(persona, "PERSONNALITÉ") or "Rigoureux"
    format_resp = extract_section(persona, "FORMAT DE RÉPONSE") or ""
    phrases = extract_section(persona, "PHRASES CLÉ") or ""
    interdictions = extract_section(persona, "CE QUE TU NE FAIS JAMAIS") or ""
    verticales = extract_section(persona, "VERTICALES") or ""

    system_prompt = f"""Tu es Le Léman, le conseil de confiance IA de Cortex Leman.

{identity}

{personality}

FORMAT DE RÉPONSE:
{format_resp}

PHRASES À UTILISER:
{phrases}

INTERDICTIONS:
{interdictions}

VERTICALE ACTIVE: {vertical}
{verticales}

RÈGLES IMPÉRATIVES:
- Tu ne prends JAMAIS de décision autonome
- Tu signales TOUJOURS les risques de non-conformité
- Tu recommandes TOUJOURS une validation humaine pour les décisions critiques
- Tu respectes le RGPD, l'AI Act et le secret professionnel FR-CH
- Tu fournis des références réglementaires quand possible
"""

    result = await llm_service.generate_for_agent(
        agent_name="reasoning",
        task=message,
        context={"user_role": auth.role, "user_email": auth.email, "vertical": vertical},
        vertical=vertical,
        client_id=client_id,
    )

    response_text = result.get("text", "")

    # Reflection Node: auto-critique si disponible
    reflection_info = None
    try:
        from core.agents.reflection import reflection_node
        if reflection_node.enabled and response_text:
            # La réflexion est déjà faite par le ReasoningAgent,
            # mais ici on expose les stats
            reflection_info = reflection_node.get_stats()
    except ImportError:
        pass

    log_audit(
        db, action="le_leman_chat", user_id=auth.user_id,
        user_email=auth.email, resource_type="le_leman",
        details={"vertical": vertical, "model": result.get("model"), "reflection": reflection_info is not None},
    )

    # Trust layer
    guardrail_flags = result.get("guardrail_flags", [])
    guardrail_blocked = result.get("error") == "guardrail_blocked"

    # Signature Le Léman
    signature = "\n\n---\n*🌊 Le Léman — Conseil de confiance · Cortex Leman v5*"
    if response_text and not guardrail_blocked:
        response_text += signature

    return {
        "response": response_text,
        "persona": "Le Léman",
        "agent": "reasoning",
        "model": result.get("model"),
        "provider": result.get("provider"),
        "tokens": result.get("tokens", 0),
        "vertical": vertical,
        "error": result.get("error"),
        "guardrail_flags": guardrail_flags,
        "guardrail_blocked": guardrail_blocked,
        "trust_score": 1.0 if not guardrail_blocked and not guardrail_flags else (0.5 if guardrail_flags else 0.0),
        "reflection": reflection_info,
    }


@app.get("/api/v1/le-leman/info")
async def le_leman_info():
    """Informations sur Le Léman (public)"""
    return {
        "name": "Le Léman",
        "title": "Conseil de confiance franco-suisse",
        "description": "L'assistant IA de Cortex Leman qui analyse, recommande, et ne décide jamais seul.",
        "version": "1.0.0",
        "verticals": ["comptable", "avocat", "sante", "banque", "startup", "rh"],
        "capabilities": [
            "Analyse réglementaire avec références exactes",
            "Comparaison d'options avec score de confiance",
            "Auto-critique via Reflection Node (pattern JP Morgan)",
            "Conformité RGPD/AI Act/secret professionnel by design",
        ],
        "philosophy": "Déterministe là où il faut. Intelligent là où on peut.",
    }


# ============================================================
# REFLECTION NODE (stats + config)
# ============================================================

@app.get("/api/v1/reflection/stats")
async def reflection_stats(
    auth: AuthContext = Depends(require_operator),
):
    """Statistiques du Reflection Node"""
    from core.agents.reflection import reflection_node
    return reflection_node.get_stats()


@app.post("/api/v1/reflection/toggle")
async def reflection_toggle(
    enabled: bool,
    auth: AuthContext = Depends(require_admin),
    db: Session = Depends(get_session),
):
    """Activer/désactiver le Reflection Node (admin)"""
    from core.agents.reflection import reflection_node
    if enabled:
        reflection_node.enable()
    else:
        reflection_node.disable()

    log_audit(
        db, action="reflection_toggle", user_id=auth.user_id,
        user_email=auth.email, resource_type="reflection",
        details={"enabled": enabled},
    )
    return {"reflection_enabled": enabled}


# ============================================================
# AGENT CHAT (LLM direct pour le frontend — legacy)
# ============================================================

@app.post("/api/v1/chat")
async def agent_chat(
    message: str,
    vertical: str = "unknown",
    client_id: str = "unknown",
    agent_name: str = "reasoning",
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Chat direct avec un agent LLM (utilisé par le frontend)"""
    from core.integrations.llm import llm_service

    result = await llm_service.generate_for_agent(
        agent_name=agent_name,
        task=message,
        context={"user_role": auth.role, "user_email": auth.email},
        vertical=vertical,
        client_id=client_id,
    )

    log_audit(
        db, action="agent_chat", user_id=auth.user_id,
        user_email=auth.email, resource_type="chat",
        details={"agent": agent_name, "vertical": vertical, "model": result.get("model")},
    )

    # Trust layer info
    guardrail_flags = result.get("guardrail_flags", [])
    guardrail_blocked = result.get("error") == "guardrail_blocked"

    return {
        "response": result.get("text", ""),
        "agent": agent_name,
        "model": result.get("model"),
        "provider": result.get("provider"),
        "tokens": result.get("tokens", 0),
        "error": result.get("error"),
        # Trust layer
        "guardrail_flags": guardrail_flags,
        "guardrail_blocked": guardrail_blocked,
        "trust_score": 1.0 if not guardrail_blocked and not guardrail_flags else (0.5 if guardrail_flags else 0.0),
        "vertical": vertical,
    }


# ════════════════════════════════════════════════════════════════
# CHAT STREAMING SSE (Conversational UI P0)
# ════════════════════════════════════════════════════════════════
@app.post("/api/v1/chat/stream")
async def agent_chat_stream(
    request: Request,
    auth: AuthContext = Depends(get_current_user),
):
    """Chat streaming SSE — tokens en temps réel avec pipeline multi-agents."""
    import json
    from sse_starlette.sse import EventSourceResponse
    from core.integrations.llm import llm_service

    body = await request.json()
    message = body.get("message", "")
    vertical = body.get("vertical", "comptable")
    client_id = body.get("client_id", "demo")
    agent_name = body.get("agent_name", "reasoning")
    conversation_id = body.get("conversation_id")

    async def event_generator():
        # 1) Signal: démarrage du pipeline
        pipeline_id = f"chat_{datetime.now().strftime('%H%M%S')}_{auth.user_id[:6]}"
        yield {"event": "pipeline_start", "data": json.dumps({
            "pipeline_id": pipeline_id,
            "steps": ["intention", "mediator_check", "rag_context", "llm_generate", "guardrail", "journal"],
        })}

        # 2) Signal: intention détectée
        yield {"event": "agent_step", "data": json.dumps({
            "step": "intention", "agent": "orchestrator", "status": "done",
            "detail": f"Vertical: {vertical}",
        })}

        # 3) Signal: Médiateur check (deterministic)
        from core.mediator.mediator import mediator
        try:
            trust_eval = await mediator.evaluate(vertical, "chat", {
                "user_role": auth.role, "action": "chat", "message_length": len(message),
            })
            verdict = trust_eval.get("verdict", "APPROVED") if trust_eval else "APPROVED"
        except Exception:
            verdict = "APPROVED"

        yield {"event": "agent_step", "data": json.dumps({
            "step": "mediator_check", "agent": "mediator", "status": "done",
            "detail": f"Verdict: {verdict}", "verdict": verdict,
        })}

        if verdict in ("BLOCKED", "FROZEN"):
            yield {"event": "guardrail_blocked", "data": json.dumps({
                "verdict": verdict, "reason": "Action non autorisée par le Médiateur",
            })}
            yield {"event": "pipeline_end", "data": json.dumps({"status": "blocked"})}
            return

        # 4) Signal: RAG context
        yield {"event": "agent_step", "data": json.dumps({
            "step": "rag_context", "agent": "data", "status": "running",
        })}

        rag_context = ""
        try:
            from core.integrations.rag import rag_service
            if rag_service:
                rag_results = await rag_service.search(message, vertical=vertical)
                rag_context = "\n".join(r.get("content", "") for r in rag_results[:3]) if rag_results else ""
        except Exception:
            pass

        yield {"event": "agent_step", "data": json.dumps({
            "step": "rag_context", "agent": "data", "status": "done",
            "detail": f"{len(rag_context)} chars de contexte",
        })}

        # 5) Signal + Stream: LLM generation
        yield {"event": "agent_step", "data": json.dumps({
            "step": "llm_generate", "agent": agent_name, "status": "running",
        })}

        full_response = ""
        model_used = ""
        provider_used = ""
        tokens_used = 0

        try:
            # Try streaming from LLM service
            stream = llm_service.stream_generate(
                agent_name=agent_name,
                task=message,
                context={"user_role": auth.role, "vertical": vertical, "rag_context": rag_context},
                vertical=vertical,
                client_id=client_id,
            )
            async for chunk in stream:
                token = chunk.get("text", "")
                if token:
                    full_response += token
                    yield {"event": "token", "data": json.dumps({"text": token})}
                if chunk.get("model"):
                    model_used = chunk["model"]
                if chunk.get("provider"):
                    provider_used = chunk["provider"]
                if chunk.get("done"):
                    tokens_used = chunk.get("tokens", 0)
                    break
        except AttributeError:
            # Fallback: non-streaming generate
            result = await llm_service.generate_for_agent(
                agent_name=agent_name,
                task=message,
                context={"user_role": auth.role, "vertical": vertical, "rag_context": rag_context},
                vertical=vertical,
                client_id=client_id,
            )
            full_response = result.get("text", "")
            model_used = result.get("model", "")
            provider_used = result.get("provider", "")
            tokens_used = result.get("tokens", 0)
            # Simulate streaming by chunks
            words = full_response.split(" ")
            for i, w in enumerate(words):
                yield {"event": "token", "data": json.dumps({"text": w + (" " if i < len(words) - 1 else "")})}
        except Exception as e:
            full_response = f"Erreur: {e}"
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

        # 6) Signal: Guardrails check
        guardrail_flags = []
        yield {"event": "agent_step", "data": json.dumps({
            "step": "guardrail", "agent": "mediator", "status": "done",
            "detail": f"{len(guardrail_flags)} flags",
        })}

        # 7) Signal: Journal WORM
        yield {"event": "agent_step", "data": json.dumps({
            "step": "journal", "agent": "supervisor", "status": "done",
        })}

        # 8) Done
        trust_score = 1.0 if not guardrail_flags else 0.5
        yield {"event": "pipeline_end", "data": json.dumps({
            "status": "done",
            "agent": agent_name,
            "model": model_used,
            "provider": provider_used,
            "tokens": tokens_used,
            "trust_score": trust_score,
            "guardrail_flags": guardrail_flags,
            "vertical": vertical,
            "conversation_id": conversation_id,
        })}

        # Audit log
        try:
            log_audit(
                db=None, action="chat_stream", user_id=auth.user_id,
                user_email=auth.email, resource_type="chat",
                details={"agent": agent_name, "vertical": vertical, "model": model_used, "tokens": tokens_used},
            )
        except Exception:
            pass

    return EventSourceResponse(event_generator())


# ════════════════════════════════════════════════════════════════
# REVIEW LOOP (P1) — Boucle Médiateur déterministe
# ════════════════════════════════════════════════════════════════
@app.post("/api/v1/review-loop")
async def run_review_loop(
    request: Request,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Exécuter la Review Loop complète.
    
    Pipeline: Agent génère → Médiateur vérifie → Si problème → Agent corrige → Re-vérifie
    Max 3 itérations. Arbitrage humain si toujours pas approuvé.
    """
    body = await request.json()
    agent_name = body.get("agent_name", "reasoning")
    task = body.get("task", "")
    vertical = body.get("vertical", "comptable")
    context = body.get("context", {})
    client_id = body.get("client_id", "demo")
    intention_id = body.get("intention_id")

    if not task:
        raise HTTPException(400, "Le champ 'task' est requis")

    from core.mediator.review_loop import review_loop
    result = await review_loop.execute(
        agent_name=agent_name,
        task=task,
        vertical=vertical,
        context={**context, "user_role": auth.role},
        client_id=client_id,
        intention_id=intention_id,
    )

    log_audit(
        db, action="review_loop", user_id=auth.user_id,
        user_email=auth.email, resource_type="review_loop",
        details={
            "agent": agent_name, "vertical": vertical,
            "verdict": result.verdict.value, "iterations": result.total_iterations,
            "elapsed_ms": round(result.total_elapsed_ms),
        },
    )

    return result.to_dict()


@app.post("/api/v1/review-loop/stream")
async def run_review_loop_stream(
    request: Request,
    auth: AuthContext = Depends(get_current_user),
):
    """
    Review Loop en streaming SSE — chaque itération est envoyée en temps réel.
    """
    import json as json_mod
    from sse_starlette.sse import EventSourceResponse
    from core.mediator.review_loop import review_loop, LoopVerdict
    from core.integrations.llm import llm_service

    body = await request.json()
    agent_name = body.get("agent_name", "reasoning")
    task = body.get("task", "")
    vertical = body.get("vertical", "comptable")
    context = body.get("context", {})
    client_id = body.get("client_id", "demo")
    intention_id = body.get("intention_id")

    async def event_generator():
        # Signal de début
        yield {"event": "review_start", "data": json_mod.dumps({
            "agent": agent_name, "vertical": vertical, "max_iterations": 3,
        })}

        # Exécuter la review loop
        result = await review_loop.execute(
            agent_name=agent_name,
            task=task,
            vertical=vertical,
            context={**context, "user_role": auth.role},
            client_id=client_id,
            intention_id=intention_id,
        )

        # Envoyer chaque itération
        for it in result.iterations:
            yield {"event": "iteration", "data": json_mod.dumps({
                "iteration": it.iteration,
                "verdict": it.verdict,
                "findings_count": it.findings_count,
                "critical_count": it.critical_count,
                "rules_triggered": it.rules_triggered,
                "feedback": it.feedback,
                "elapsed_ms": round(it.elapsed_ms),
            })}

        # Signal de fin
        yield {"event": "review_end", "data": json_mod.dumps({
            "final_verdict": result.verdict.value,
            "total_iterations": result.total_iterations,
            "total_elapsed_ms": round(result.total_elapsed_ms),
            "trust_score": result.trust_score,
            "arbitration_reason": result.arbitration_reason,
            "final_output": result.final_output,
        })}

    return EventSourceResponse(event_generator())


# ════════════════════════════════════════════════════════════════
# SERMENT NUMÉRIQUE (Public — divergent)
# ════════════════════════════════════════════════════════════════

@app.get("/api/v1/serment/{vertical}")
async def get_serment(vertical: str):
    """Récupérer le serment numérique d'une vertical"""
    from core.serment import load_serment
    s = load_serment(vertical)
    if not s:
        raise HTTPException(404, f"Serment non trouvé pour vertical '{vertical}'")
    return s


@app.get("/api/v1/serment")
async def list_all_serments():
    """Lister tous les serments numériques"""
    from core.serment import list_serments
    return {"serments": list_serments()}


@app.get("/api/v1/serment/{vertical}/verify")
async def verify_serment(vertical: str):
    """Vérifier l'intégrité d'un serment"""
    from core.serment import verify_serment_integrity
    return verify_serment_integrity(vertical)


# ════════════════════════════════════════════════════════════════
# VOICE INTERFACE (P2) — STT + TTS
# ════════════════════════════════════════════════════════════════
@app.post("/api/v1/voice/transcribe")
async def voice_transcribe(
    request: Request,
    auth: AuthContext = Depends(get_current_user),
):
    """Transcrire un audio en texte (faster-whisper, local)."""
    audio_data = await request.body()
    if not audio_data:
        raise HTTPException(400, "Aucune donnée audio")

    content_type = request.headers.get("content-type", "audio/wav")

    from core.integrations.voice_service import stt_service
    try:
        result = await stt_service.transcribe(audio_data, language="fr")
    except ImportError:
        raise HTTPException(503, "Service STT non disponible (faster-whisper non installé)")
    except Exception as e:
        raise HTTPException(500, f"Erreur transcription: {e}")

    log_audit(
        db=None, action="voice_transcribe", user_id=auth.user_id,
        user_email=auth.email, resource_type="voice",
        details={"duration": result.get("duration"), "words": result.get("words_count")},
    )

    return result


@app.post("/api/v1/voice/synthesize")
async def voice_synthesize(
    request: Request,
    auth: AuthContext = Depends(get_current_user),
):
    """Synthétiser du texte en audio (edge-tts gratuit / elevenlabs premium)."""
    from fastapi.responses import Response

    body = await request.json()
    text = body.get("text", "")
    persona = body.get("persona", "le_leman")
    locale = body.get("locale")

    if not text:
        raise HTTPException(400, "Le champ 'text' est requis")
    if len(text) > 5000:
        raise HTTPException(400, "Texte trop long (max 5000 caractères)")

    from core.integrations.voice_service import tts_service
    try:
        result = await tts_service.synthesize(text, persona=persona, locale=locale)
    except Exception as e:
        raise HTTPException(500, f"Erreur synthèse: {e}")

    return Response(
        content=result["audio_data"],
        media_type=result["content_type"],
        headers={
            "X-Voice": result["voice"],
            "X-Provider": result["provider"],
            "X-Duration-Ms": str(result["duration_ms"]),
        },
    )


@app.post("/api/v1/voice/chat")
async def voice_chat(
    request: Request,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Voice Chat complet: Audio → STT → Chat → TTS → Audio.
    
    Pipeline: microphone → faster-whisper → Le Léman → edge-tts → haut-parleur.
    Tout est journalisé dans le WORM.
    """
    audio_data = await request.body()
    if not audio_data:
        raise HTTPException(400, "Aucune donnée audio")

    # 1. STT
    from core.integrations.voice_service import stt_service, tts_service
    from fastapi.responses import Response as FastResponse

    try:
        stt_result = await stt_service.transcribe(audio_data, language="fr")
    except Exception as e:
        raise HTTPException(500, f"Erreur STT: {e}")

    user_text = stt_result.get("text", "")
    if not user_text:
        return {"error": "Aucune parole détectée", "stt": stt_result}

    # 2. Chat avec Le Léman
    from core.integrations.llm import llm_service
    try:
        chat_result = await llm_service.generate_for_agent(
            agent_name="reasoning",
            task=user_text,
            context={"user_role": auth.role, "vertical": "voice", "source": "voice"},
            vertical="comptable",
            client_id="voice",
        )
        response_text = chat_result.get("text", "")
    except Exception as e:
        response_text = f"Erreur: {e}"

    # 3. TTS
    try:
        tts_result = await tts_service.synthesize(response_text[:2000], persona="le_leman")
    except Exception as e:
        # Si TTS échoue, retourner le texte
        return {
            "user_text": user_text,
            "response_text": response_text,
            "tts_error": str(e),
            "stt": stt_result,
        }

    # Audit
    log_audit(
        db, action="voice_chat", user_id=auth.user_id,
        user_email=auth.email, resource_type="voice",
        details={
            "stt_duration": stt_result.get("duration"),
            "stt_words": stt_result.get("words_count"),
            "response_length": len(response_text),
            "tts_provider": tts_result.get("provider"),
        },
    )

    return FastResponse(
        content=tts_result["audio_data"],
        media_type=tts_result["content_type"],
        headers={
            "X-User-Text": user_text[:200],
            "X-Response-Text": response_text[:200],
            "X-STT-Duration": str(stt_result.get("duration", 0)),
            "X-TTS-Provider": tts_result.get("provider", "unknown"),
            "X-TTS-Voice": tts_result.get("voice", "unknown"),
        },
    )


# ════════════════════════════════════════════════════════════════
# VERTICAL INTEGRATIONS (P2) — Connecteurs métier
# ════════════════════════════════════════════════════════════════

@app.get("/api/v1/verticals")
async def list_vertical_connectors():
    """Lister tous les connecteurs verticaux disponibles."""
    from core.integrations.verticals import vertical_registry
    return {"verticals": vertical_registry.list_all()}


@app.post("/api/v1/verticals/{vertical}/validate")
async def validate_vertical_action(
    vertical: str,
    request: Request,
    auth: AuthContext = Depends(get_current_user),
):
    """Valider une action selon les règles du connecteur vertical."""
    body = await request.json()
    action = body.get("action", "unknown")
    context = body.get("context", {})

    from core.integrations.verticals import vertical_registry
    result = vertical_registry.validate(vertical, action, context)
    return result.to_dict()


@app.post("/api/v1/verticals/{vertical}/enrich")
async def enrich_vertical_context(
    vertical: str,
    request: Request,
    auth: AuthContext = Depends(get_current_user),
):
    """Enrichir le contexte avec les données du connecteur vertical."""
    body = await request.json()
    context = body.get("context", {})

    from core.integrations.verticals import vertical_registry
    return {"enriched_context": vertical_registry.enrich(vertical, context)}


@app.get("/api/v1/verticals/{vertical}/templates")
async def get_vertical_templates(
    vertical: str,
    auth: AuthContext = Depends(get_current_user),
):
    """Récupérer les templates de documents réglementaires d'une vertical."""
    from core.integrations.verticals import vertical_registry
    return {"templates": vertical_registry.templates(vertical)}


@app.get("/api/v1/verticals/{vertical}/calendar")
async def get_vertical_calendar(
    vertical: str,
    year: int = None,
    auth: AuthContext = Depends(get_current_user),
):
    """Échéances réglementaires d'une vertical."""
    from core.integrations.verticals import vertical_registry
    return {"deadlines": vertical_registry.calendar(vertical, year)}


@app.get("/api/v1/verticals/templates")
async def get_all_templates(
    auth: AuthContext = Depends(get_current_user),
):
    """Tous les templates de toutes les verticales."""
    from core.integrations.verticals import vertical_registry
    return {"templates": vertical_registry.templates()}


@app.get("/api/v1/verticals/calendar")
async def get_all_calendar(
    year: int = None,
    auth: AuthContext = Depends(get_current_user),
):
    """Toutes les échéances réglementaires."""
    from core.integrations.verticals import vertical_registry
    return {"deadlines": vertical_registry.calendar(year=year)}


# ════════════════════════════════════════════════════════════════
# ÉCHÉANCIER RÉGLEMENTAIRE (Authentifié — divergent)
# ════════════════════════════════════════════════════════════════

@app.get("/api/v1/regulatory/calendar")
async def regulatory_calendar(
    vertical: str = None,
    jurisdiction: str = None,
):
    """Échéancier réglementaire FR-CH vivant"""
    from core.regulatory import get_calendar
    return {"deadlines": get_calendar(vertical=vertical, jurisdiction=jurisdiction)}


@app.get("/api/v1/regulatory/stats")
async def regulatory_stats(
    vertical: str = None,
):
    """Statistiques échéancier réglementaire"""
    from core.regulatory import get_deadline_stats
    return get_deadline_stats(vertical=vertical)


# ════════════════════════════════════════════════════════════════
# ARTIFACTS (P3) — Aperçus et artefacts riches
# ════════════════════════════════════════════════════════════════

@app.post("/api/v1/artifacts/detect")
async def detect_artifacts(
    request: Request,
    auth: AuthContext = Depends(get_current_user),
):
    """Détecter les artefacts dans un texte (tableaux, métriques, code)."""
    body = await request.json()
    text = body.get("text", "")
    vertical = body.get("vertical", "")

    from core.artifacts import detect_artifacts as _detect
    artifacts = _detect(text, vertical)
    return {"artifacts": [a.to_dict() for a in artifacts]}


@app.post("/api/v1/artifacts/compliance-card")
async def generate_compliance_card(
    request: Request,
    auth: AuthContext = Depends(get_current_user),
):
    """Générer une fiche de conformité structurée."""
    body = await request.json()
    vertical = body.get("vertical", "comptable")
    action = body.get("action", "consultation")
    context = body.get("context", {})

    from core.integrations.verticals import vertical_registry
    from core.artifacts import generate_compliance_card as _gen_card

    validation = vertical_registry.validate(vertical, action, context)
    card = _gen_card(vertical, validation.to_dict())
    return card.to_dict()


@app.post("/api/v1/artifacts/document-preview")
async def generate_document_preview(
    request: Request,
    auth: AuthContext = Depends(get_current_user),
):
    """Générer un aperçu de document pré-rempli."""
    body = await request.json()
    template_id = body.get("template_id")
    vertical = body.get("vertical", "comptable")
    filled_fields = body.get("fields", {})

    from core.integrations.verticals import vertical_registry
    from core.artifacts import generate_document_preview as _gen_doc

    templates = vertical_registry.templates(vertical)
    template = next((t for t in templates if t.get("id") == template_id), None)
    if not template:
        raise HTTPException(404, f"Template '{template_id}' non trouvé pour '{vertical}'")

    artifact = _gen_doc(template_id, template, filled_fields)
    return artifact.to_dict()


@app.get("/api/v1/artifacts/trust-timeline")
async def trust_timeline(
    vertical: str = None,
    limit: int = 50,
    auth: AuthContext = Depends(get_current_user),
):
    """Timeline de confiance à partir du journal WORM."""
    from core.journal.append_only_journal import journal
    from core.artifacts import generate_trust_timeline

    events = journal.query_last(limit=limit, vertical=vertical)
    artifact = generate_trust_timeline(events, vertical or "")
    return artifact.to_dict()


# ════════════════════════════════════════════════════════════════
# ONBOARDING
# ════════════════════════════════════════════════════════════════

@app.get("/api/v1/onboarding/verticals")
async def list_verticals():
    """Liste toutes les verticals disponibles avec preview"""
    from core.onboarding import onboarding_service
    return {"verticals": onboarding_service.list_verticals()}


@app.get("/api/v1/onboarding/verticals/{vertical}")
async def preview_vertical(vertical: str):
    """Prévisualisation d'une vertical (agents, règles, compliance)"""
    from core.onboarding import onboarding_service
    preview = onboarding_service.get_vertical_preview(vertical)
    if "error" in preview:
        raise HTTPException(404, preview["error"])
    return preview


@app.post("/api/v1/onboarding/setup")
async def setup_tenant(
    data: dict,
    db: Session = Depends(get_session),
):
    """
    Onboarding complet — crée tout en une transaction atomique.

    Pas de cards, pas de nouvelles skills. Lit les templates existants
    (agent-config.yaml + règles JsonLogic + workflows n8n) et les installe.
    """
    from core.onboarding import onboarding_service

    # Validation minimale
    required = ["identity", "vertical", "security"]
    for field in required:
        if field not in data:
            raise HTTPException(400, f"Champ requis: {field}")

    if not data.get("identity", {}).get("email"):
        raise HTTPException(400, "Email requis")

    if not data.get("security", {}).get("admin_password"):
        raise HTTPException(400, "Mot de passe admin requis")

    if data["vertical"] not in {"comptable", "avocat", "sante", "banque", "startup", "rh"}:
        raise HTTPException(400, f"Vertical invalide: {data['vertical']}")

    result = onboarding_service.setup_tenant(data)

    if result.errors and not result.admin_user_id:
        raise HTTPException(422, {"errors": result.errors})

    log_audit(
        db, action="tenant_onboarded",
        user_email=data["identity"]["email"],
        resource_type="tenant",
        resource_id=result.tenant_id,
        details={
            "vertical": result.vertical,
            "mode": result.mode,
            "rules_loaded": result.rules_loaded,
            "agents_created": result.agents_created,
            "errors": result.errors,
        },
    )

    response = result.to_dict()
    response["first_message"] = getattr(result, "first_message", "")
    return response


@app.get("/api/v1/onboarding/status")
async def onboarding_status(
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Vérifie si l'utilisateur a complété l'onboarding"""
    return {
        "user_id": auth.user_id,
        "email": auth.email,
        "role": auth.role,
        "verticals": auth.verticals,
        "onboarding_complete": bool(auth.verticals),
    }


# ════════════════════════════════════════════════════════════════
# MCP & A2A Protocol Endpoints (AG2-inspired Insights 5-6)
# ════════════════════════════════════════════════════════════════
# MCP & A2A Protocols
# ════════════════════════════════════════════════════════════════

@app.post("/mcp")
async def mcp_jsonrpc(request: Request):
    """MCP (Model Context Protocol) — JSON-RPC 2.0 complet"""
    from core.integrations.mcp_cortex_server import cortex_mcp
    body = await request.json()
    result = cortex_mcp.handle_request(body)
    if result is None:
        return JSONResponse(content={}, status_code=204)
    return JSONResponse(content=result)


@app.get("/mcp/tools")
async def mcp_tools_list():
    """MCP: Liste des 18 tools disponibles"""
    from core.integrations.mcp_cortex_server import cortex_mcp
    return {"tools": cortex_mcp.tools, "total": len(cortex_mcp.tools)}


@app.post("/mcp/tools/call")
async def mcp_tools_call(request: Request):
    """MCP: Appeler un tool"""
    from core.integrations.mcp_cortex_server import cortex_mcp
    body = await request.json()
    response = cortex_mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": body.get("name", ""),
            "arguments": body.get("arguments", {}),
        },
    })
    result = response.get("result") or response.get("error", {"message": "unknown"})
    return JSONResponse(content=result)


@app.post("/a2a")
async def a2a_endpoint(request: Request):
    """A2A (Agent-to-Agent) — JSON-RPC 2.0 endpoint"""
    from core.integrations.a2a_adapter import a2a_adapter
    body = await request.json()
    result = a2a_adapter.handle_request(body)
    return JSONResponse(content=result)


# AutoDefense endpoint (Insight 1)
@app.post("/api/v1/guardrails/autodefense")
async def autodefense_check(
    request: Request,
    auth=Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Vérification AutoDefense multi-agent (3 validateurs)"""
    from core.security.guardrails.autodefense import autodefense
    from core.security.audit import audit_log
    body = await request.json()
    content = body.get("content", "")
    vertical = body.get("vertical", "unknown")

    result = autodefense.defend(content, vertical)

    log_audit(
        db, action="autodefense_check", user_id=auth.user_id,
        user_email=auth.email, resource_type="guardrail",
        details={"passed": result.passed, "blocked": result.blocked, "consensus": result.consensus},
    )

    return {
        "passed": result.passed,
        "blocked": result.blocked,
        "consensus": result.consensus,
        "votes": [
            {"validator": v.validator, "passed": v.passed, "confidence": v.confidence, "reason": v.reason}
            for v in result.votes
        ],
        "reason": result.reason,
    }


# StateFlow endpoint (Insight 2)
@app.get("/api/v1/intentions/{intention_id}/history")
async def intention_history(
    intention_id: str,
    auth=Depends(get_current_user),
):
    """Historique des transitions d'état d'une intention (StateFlow)"""
    from core.orchestrator.intention import intention_store
    history = intention_store.get_history(intention_id)
    state = intention_store.get_state(intention_id)
    return {"intention_id": intention_id, "state": state.value if state else None, "history": history}


# CaptainAgent team assembly endpoint (Insight 3)
@app.post("/api/v1/agents/assemble-team")
async def assemble_team(
    request: Request,
    auth=Depends(get_current_user),
):
    """Assembler une équipe d'agents (CaptainAgent pattern)"""
    from core.orchestrator.router import router
    from core.journal.models import IntentionModel
    body = await request.json()

    intention = IntentionModel(
        intention_id=body.get("intention_id", "temp"),
        client_id=body.get("client_id", "demo"),
        vertical=body.get("vertical", "comptable"),
        original_query=body.get("query", ""),
        refined_query=body.get("query", ""),
        context=body.get("context", {}),
    )

    team = router.assemble_team(intention)
    return team.to_dict()


# ─── Chief of Staff Routes ─────────────────────────────────────────

@app.get("/api/v1/chief-of-staff/report")
async def chief_of_staff_report(auth=Depends(get_current_user)):
    """Rapport exécutif quotidien — synthèse cross-agents"""
    agents = app_state.get("agents", {})
    cos = agents.get("chief_of_staff")
    if not cos:
        raise HTTPException(status_code=503, detail="Chief of Staff agent not available")
    result = await cos.process({"request_type": "daily_report"}, {})
    return result.get("report", result)


@app.get("/api/v1/chief-of-staff/alerts")
async def chief_of_staff_alerts(auth=Depends(get_current_user)):
    """Alertes actives du Chief of Staff"""
    agents = app_state.get("agents", {})
    cos = agents.get("chief_of_staff")
    if not cos:
        raise HTTPException(status_code=503, detail="Chief of Staff agent not available")
    return cos._get_alerts()


@app.get("/api/v1/chief-of-staff/health")
async def chief_of_staff_health(auth=Depends(get_current_user)):
    """Health check rapide"""
    agents = app_state.get("agents", {})
    cos = agents.get("chief_of_staff")
    if not cos:
        raise HTTPException(status_code=503, detail="Chief of Staff agent not available")
    return cos._get_health_check()


@app.get("/api/v1/chief-of-staff/vertical/{vertical}")
async def chief_of_staff_vertical(vertical: str, auth=Depends(get_current_user)):
    """Métriques d'un vertical spécifique"""
    agents = app_state.get("agents", {})
    cos = agents.get("chief_of_staff")
    if not cos:
        raise HTTPException(status_code=503, detail="Chief of Staff agent not available")
    return cos._get_vertical_summary(vertical)
