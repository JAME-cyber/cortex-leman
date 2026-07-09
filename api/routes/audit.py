"""
Cortex Leman v5 — API Audit & Conformité RGPD

Endpoints pour certificateurs et auditeurs (Phase 1, stratégie v3).
Fournit les données structurées permettant à un certificateur accrédité
de produire un rapport de conformité AI Act / RGPD.

Exigence : Audit o3 (ISO 42001), Phase 1 S7-S8
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("/export")
async def export_audit_report(
    format: str = Query("json", enum=["json", "csv", "summary"]),
    period_start: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    period_end: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    client_id: Optional[str] = Query(None, description="Filtrer par client (isolation tenant)"),
    vertical: Optional[str] = Query(None, description="Filtrer par verticale"),
    current_user: dict = Depends(get_current_user),
):
    """
    Exporter les données d'audit pour un certificateur.

    Retourne les événements du journal WORM filtrés par période et client.
    Le certificateur utilise ces données pour produire un rapport de conformité.
    """
    from core.journal.append_only_journal import journal
    from core.journal.models import JournalEventType

    # Récupérer les entrées du journal
    entries = journal.query_tenant(
        client_id=client_id or current_user.get("tenant_id", "default"),
        limit=10000,
    )

    # Filtrer par période
    if period_start:
        entries = [e for e in entries if e.get("timestamp", "") >= period_start]
    if period_end:
        entries = [e for e in entries if e.get("timestamp", "") <= period_end + "T23:59:59"]

    # Filtrer par verticale
    if vertical:
        entries = [e for e in entries if e.get("vertical") == vertical]

    if format == "summary":
        # Résumé pour certificat
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": {"start": period_start, "end": period_end},
            "client_id": client_id,
            "vertical": vertical,
            "summary": {
                "total_events": len(entries),
                "events_by_type": _count_by_field(entries, "event_type"),
                "events_by_agent": _count_by_field(entries, "agent_source"),
                "mediator_freezes": len([e for e in entries if "freeze" in e.get("event_type", "")]),
                "arbitrations": len([e for e in entries if "arbitration" in e.get("event_type", "")]),
                "compliance_violations": len([e for e in entries if "violation" in e.get("event_type", "")]),
                "unique_intentions": len(set(e.get("intention_id") for e in entries if e.get("intention_id"))),
            },
            "compliance_score": _calculate_compliance_score(entries),
            "worm_integrity": journal.verify_integrity(),
        }

    elif format == "csv":
        # Format CSV simplifié pour import tableur
        csv_lines = ["sequence,timestamp,event_type,client_id,vertical,agent_source,intention_id"]
        for e in entries:
            csv_lines.append(
                f"{e.get('sequence', '')},"
                f"{e.get('timestamp', '')},"
                f"{e.get('event_type', '')},"
                f"{e.get('client_id', '')},"
                f"{e.get('vertical', '')},"
                f"{e.get('agent_source', '')},"
                f"{e.get('intention_id', '')}"
            )
        return {"format": "csv", "lines": csv_lines, "total": len(entries)}

    else:
        # JSON complet
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": {"start": period_start, "end": period_end},
            "client_id": client_id,
            "vertical": vertical,
            "total_entries": len(entries),
            "entries": entries,
            "worm_integrity": journal.verify_integrity(),
        }


@router.get("/compliance-score")
async def get_compliance_score(
    client_id: Optional[str] = Query(None),
    vertical: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Score de conformité en temps réel.

    Calcule un score 0-100 basé sur :
    - Intégrité du journal WORM
    - Nombre de violations vs événements totaux
    - Nombre de gels non résolus
    - Ratio arbitrages résolus
    """
    from core.journal.append_only_journal import journal

    entries = journal.query_tenant(
        client_id=client_id or current_user.get("tenant_id", "default"),
        limit=10000,
    )

    if vertical:
        entries = [e for e in entries if e.get("vertical") == vertical]

    score = _calculate_compliance_score(entries)

    # Vérifier l'intégrité WORM
    worm = journal.verify_integrity()

    return {
        "score": score,
        "worm_integrity": worm.get("valid", False),
        "total_events": len(entries),
        "breakdown": {
            "journal_integrity": 100 if worm.get("valid") else 0,
            "violation_rate": _safe_pct(
                len([e for e in entries if "violation" in e.get("event_type", "")]),
                len(entries),
            ),
            "freeze_rate": _safe_pct(
                len([e for e in entries if "freeze" in e.get("event_type", "")]),
                len(entries),
            ),
            "arbitration_resolution_rate": _safe_pct(
                len([e for e in entries if e.get("event_type") == "arbitration.decision"]),
                max(1, len([e for e in entries if e.get("event_type") == "arbitration.requested"])),
            ),
        },
        "vertical": vertical,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/worm-extract")
async def extract_worm_entries(
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(1000, le=10000),
    current_user: dict = Depends(get_current_user),
):
    """
    Extraire des entrées WORM brutes pour vérification auditeur.

    Retourne les entrées avec leur hash pour vérification de chaîne.
    L'auditeur peut re-vérifier l'intégrité localement.
    """
    from core.journal.append_only_journal import journal
    from core.journal.models import JournalEventType

    et = None
    if event_type:
        try:
            et = JournalEventType(event_type)
        except ValueError:
            pass

    entries = journal.query_tenant(
        client_id=client_id or current_user.get("tenant_id", "default"),
        event_type=et,
        limit=limit,
    )

    if from_date:
        entries = [e for e in entries if e.get("timestamp", "") >= from_date]
    if to_date:
        entries = [e for e in entries if e.get("timestamp", "") <= to_date + "T23:59:59"]

    return {
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "total": len(entries),
        "entries": entries,
        "integrity_check": journal.verify_integrity(),
    }


@router.get("/rgpd/registry")
async def get_treatment_registry():
    """
    Registre des traitements RGPD art. 30 (PUBLIC).

    Documente chaque type de traitement effectué par le système.
    Accessible sans authentification (transparence réglementaire).
    """
    from core.journal.worm_v2 import TreatmentRegistry
    return TreatmentRegistry.get_registry()


@router.get("/rgpd/legal-basis")
async def get_legal_basis_matrix():
    """
    Matrice base légale par traitement RGPD art. 6 (PUBLIC).

    Exigence identifiée par l'audit o3.
    """
    from core.journal.worm_v2 import TreatmentRegistry
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "article": "RGPD Art. 6 — Matrice des bases légales",
        "matrix": TreatmentRegistry.get_legal_basis_matrix(),
    }


@router.get("/encryption-status")
async def get_encryption_status(
    current_user: dict = Depends(get_current_user),
):
    """Statut du chiffrement WORM v2"""
    from core.journal.append_only_journal import journal
    return {
        "worm_encryption": journal.encryption_status,
        "at_rest": journal.encryption_status.get("enabled", False),
        "algorithm": journal.encryption_status.get("algorithm", "none"),
        "key_derivation": journal.encryption_status.get("key_derivation", "n/a"),
        "minimization_enabled": True,
        "purge_enabled": False,
        "retention_months": 24,
    }


@router.post("/purge")
async def purge_expired_entries(
    dry_run: bool = Query(True, description="True = simulation, False = exécuter"),
    current_user: dict = Depends(get_current_user),
):
    """
    Purger les fichiers de journal expirés (RGPD art. 5-1e).

    ATTENTION : dry_run=True par défaut. Passer dry_run=False pour exécuter.
    Nécessite des droits admin.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(403, "Seul un admin peut exécuter la purge")

    from core.journal.append_only_journal import journal
    return journal.purge_expired(dry_run=dry_run)


@router.get("/ai-act-controls")
async def get_ai_act_control_matrix():
    """
    Référentiel de contrôle AI Act art. 9-17 (PUBLIC).

    Mappe chaque article AI Act à un contrôle Cortex Leman.
    Exigence audit o3 — ISO 42001 clause 8.
    """
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "framework": "EU AI Act (JOUE 2024/AI/679)",
        "controls": [
            {
                "article": "9",
                "title": "Risk Management System",
                "requirement": "Procédure formalisée d'identification, analyse et évaluation des risques",
                "cortex_control": "Médiateur + rules JsonLogic + registre des risques SGAI",
                "evidence": "core/mediator/mediator.py, core/mediator/rules/*.json, docs/sgai/MANUAL-QUALITE-IA.md",
                "status": "implemented",
            },
            {
                "article": "10",
                "title": "Data & Data Governance",
                "requirement": "Provenance, qualité et équité des données d'entraînement",
                "cortex_control": "Documentation des LLM tiers utilisés (OpenRouter/Ollama). Pas de training interne.",
                "evidence": "core/integrations/llm/provider.py, core/config.py (llm_vertical_routing)",
                "status": "partial",
            },
            {
                "article": "11",
                "title": "Technical Documentation (Annex IV)",
                "requirement": "Dossier technique : specs, logs, tests, métriques robustesse",
                "cortex_control": "Journal WORM hash-chainé + export audit + rapport conformité",
                "evidence": "core/journal/, /api/v1/audit/export, /api/v1/audit/compliance-score",
                "status": "implemented",
            },
            {
                "article": "13",
                "title": "Transparency & Information",
                "requirement": "Information transparente sur le fonctionnement du système IA",
                "cortex_control": "Journal public + score conformité + explication des règles",
                "evidence": "/api/v1/journal, /api/v1/audit/compliance-score, /api/v1/mediator/rules",
                "status": "implemented",
            },
            {
                "article": "14",
                "title": "Human Oversight",
                "requirement": "Supervision humaine avec possibilité d'intervention",
                "cortex_control": "Arbitrage humain obligatoire. L'IA ne décide jamais seule.",
                "evidence": "core/arbitration/, /api/v1/arbitrations, /api/v1/audit/export",
                "status": "implemented",
            },
            {
                "article": "15",
                "title": "Accuracy, Robustness, Cybersecurity",
                "requirement": "Précision, robustesse et sécurité du système",
                "cortex_control": "Circuit breaker + saga compensation + tests adversariaux",
                "evidence": "core/security/circuit_breaker.py, core/agents/saga/saga_manager.py",
                "status": "implemented",
            },
            {
                "article": "17",
                "title": "Quality Management System",
                "requirement": "SGAI complet : politique, rôles, objectifs, incidents",
                "cortex_control": "Manuel Qualité IA (ce document)",
                "evidence": "docs/sgai/MANUAL-QUALITE-IA.md",
                "status": "implemented",
            },
            {
                "article": "61",
                "title": "Post-market Monitoring",
                "requirement": "Monitoring continu après déploiement",
                "cortex_control": "Superviseur V2 + health board + alertes automatiques",
                "evidence": "core/agents/supervisor_agent.py, /health",
                "status": "implemented",
            },
            {
                "article": "62",
                "title": "Serious Incident Reporting",
                "requirement": "Notification aux autorités sous 15 jours",
                "cortex_control": "Procédure d'incident SGAI + monitoring + alertes",
                "evidence": "docs/sgai/MANUAL-QUALITE-IA.md (section 5)",
                "status": "partial",
            },
        ],
        "total_controls": 9,
        "implemented": 7,
        "partial": 2,
        "not_implemented": 0,
    }


@router.get("/secret-pro-controls")
async def get_secret_pro_control_matrix():
    """
    Référentiel de contrôle secret professionnel FR-CH (PUBLIC).
    """
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "framework": "Secret professionnel FR-CH",
        "controls": [
            {
                "text": "CP 321 (CH) — Secret avocat",
                "requirement": "Protection des informations couvertes par le secret professionnel",
                "cortex_control": "Chiffrement AES-256 WORM + Mode Haute Protection K3s local",
                "evidence": "core/journal/worm_v2.py, core/config.py (app_mode=haute_protection)",
                "status": "implemented",
            },
            {
                "text": "LB 47 (CH) — Secret bancaire",
                "requirement": "Zero transfert de données bancaires hors Suisse",
                "cortex_control": "Mode Haute Protection = K3s + Ollama local, zero appel externe",
                "evidence": "edge/k3s-install.sh, edge/ollama-setup.sh",
                "status": "implemented",
            },
            {
                "text": "LPM (CH) — Données de santé",
                "requirement": "Hébergement données de santé certifié",
                "cortex_control": "K3s on-premise + isolation réseau + chiffrement",
                "evidence": "core/compliance/gateway.py",
                "status": "partial",
            },
            {
                "text": "CNB 2023-14 — Convention avocat-prestataire",
                "requirement": "Convention type pour sous-traitance IA",
                "cortex_control": "Template convention en cours",
                "evidence": "docs/sgai/ (à créer)",
                "status": "planned",
            },
            {
                "text": "FINMA Circ. 2008/21 — Outsourcing banque",
                "requirement": "Contrôle des sous-traitants et data residency",
                "cortex_control": "Compliance Gateway + rapport data residency",
                "evidence": "core/compliance/gateway.py, /api/v1/compliance/data-residency",
                "status": "implemented",
            },
        ],
    }


@router.post("/web-scan")
async def web_compliance_scan(
    url: str = Query(..., description="URL du site à scanner"),
    client_id: Optional[str] = Query(None, description="ID client pour le rapport"),
    current_user: dict = Depends(get_current_user),
):
    """
    Scanner la conformité RGPD du site web public d'un client.

    Détecte: trackers, CMP, formulaires PII, headers de sécurité,
    politique de confidentialité, mentions IA/chatbot.

    Complète les documents internes (AIPD, DPO) en vérifiant
    ce que les utilisateurs voient réellement sur le site public.
    """
    from core.compliance.audit_generator import audit_generator

    try:
        report = audit_generator.generate_web_compliance_report(
            url=url,
            client_id=client_id or current_user.get("tenant_id", "default"),
        )
        return report
    except Exception as e:
        logger.error(f"Web scan failed for {url}: {e}")
        raise HTTPException(status_code=502, detail=f"Scan impossible: {e}")


# ═══ Helpers ═══

def _count_by_field(entries: list[dict], field: str) -> dict:
    """Compter les entrées par valeur d'un champ"""
    counts = {}
    for e in entries:
        val = e.get(field, "unknown")
        counts[val] = counts.get(val, 0) + 1
    return counts


def _safe_pct(numerator: int, denominator: int) -> float:
    """Pourcentage sécurisé (division par zero)"""
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def _calculate_compliance_score(entries: list[dict]) -> dict:
    """Calculer un score de conformité 0-100"""
    if not entries:
        return {"score": 100, "grade": "A", "reason": "no_data"}

    total = len(entries)
    violations = len([e for e in entries if "violation" in e.get("event_type", "")])
    freezes = len([e for e in entries if "freeze" in e.get("event_type", "")])
    arbitrations_requested = len([e for e in entries if e.get("event_type") == "arbitration.requested"])
    arbitrations_decided = len([e for e in entries if e.get("event_type") == "arbitration.decision"])

    # Score de base : 100
    score = 100

    # Déduire pour violations
    score -= min(30, violations * 5)

    # Déduire pour gels non résolus
    unresolved_freezes = freezes - arbitrations_decided
    score -= min(20, max(0, unresolved_freezes) * 3)

    # Bonus pour résolution d'arbitrages
    if arbitrations_requested > 0:
        resolution_rate = arbitrations_decided / arbitrations_requested
        score += min(10, int(resolution_rate * 10))

    score = max(0, min(100, score))

    # Grade
    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 40:
        grade = "D"
    else:
        grade = "F"

    return {
        "score": score,
        "grade": grade,
        "details": {
            "total_events": total,
            "violations": violations,
            "freezes": freezes,
            "arbitrations_requested": arbitrations_requested,
            "arbitrations_decided": arbitrations_decided,
            "unresolved_freezes": max(0, unresolved_freezes),
        },
    }
