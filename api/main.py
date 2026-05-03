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
    for name, cls in [
        ("data", DataAgent),
        ("reasoning", ReasoningAgent),
        ("action", ActionAgent),
        ("supervisor", SupervisorAgent),
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
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
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
# COMPLIANCE (authentifié)
# ============================================================

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
    return await llm_service.health_check()


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
# AGENT CHAT (LLM direct pour le frontend)
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
    from core.integrations.mcp_server import mcp_server
    body = await request.json()
    result = mcp_server.handle_request(body)
    if result is None:
        return JSONResponse(content={}, status_code=204)
    return JSONResponse(content=result)


@app.get("/mcp/tools")
async def mcp_tools_list():
    """MCP: Liste des tools disponibles (public, pour discovery agents)"""
    from core.integrations.mcp_server import mcp_server
    response = mcp_server.handle_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
    })
    return response.get("result", {"tools": []})


@app.post("/mcp/tools/call")
async def mcp_tools_call(request: Request):
    """MCP: Appeler un tool (public pour agents externes)"""
    from core.integrations.mcp_server import mcp_server
    body = await request.json()
    response = mcp_server.handle_request({
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
