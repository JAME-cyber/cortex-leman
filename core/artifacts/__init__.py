"""
Cortex Leman v5 — Artifacts Engine

Génère et structure des artefacts riches à partir des réponses LLM:
- Tableaux de données (CSV/Markdown → HTML)
- Graphiques de confiance (score timeline)
- Documents réglementaires (templates pré-remplis)
- Fiches de conformité
- Résumés exécutifs structurés

Les artefacts sont détectés automatiquement dans les réponses des agents
ou générés explicitement via l'API.
"""
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class ArtifactType(str, Enum):
    TABLE = "table"
    CHART = "chart"
    DOCUMENT = "document"
    COMPLIANCE_CARD = "compliance_card"
    TIMELINE = "timeline"
    SUMMARY = "summary"
    CODE = "code"
    METRICS = "metrics"


@dataclass
class Artifact:
    """Un artefact structuré affichable dans le frontend."""
    id: str
    type: ArtifactType
    title: str
    data: dict
    vertical: str = ""
    created_at: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "data": self.data,
            "vertical": self.vertical,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


def _generate_id() -> str:
    import uuid
    return f"art_{uuid.uuid4().hex[:8]}_{int(datetime.now(timezone.utc).timestamp())}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════
# DETECTION — Détecte les artefacts dans une réponse LLM
# ═══════════════════════════════════════════════════════════════

def detect_artifacts(text: str, vertical: str = "") -> list[Artifact]:
    """
    Analyser un texte de réponse LLM et détecter les artefacts structurés.
    
    Patterns détectés:
    - Tableaux Markdown (| ... | ... |)
    - Blocs de code (```...```)
    - Listes structurées avec métriques
    - Sections avec titres ### et données numériques
    """
    artifacts = []

    # 1. Tableaux Markdown
    artifacts.extend(_detect_tables(text, vertical))

    # 2. Blocs de code
    artifacts.extend(_detect_code_blocks(text, vertical))

    # 3. Métriques numériques (montant, TVA, scores)
    artifacts.extend(_detect_metrics(text, vertical))

    return artifacts


def _detect_tables(text: str, vertical: str) -> list[Artifact]:
    """Détecter les tableaux Markdown dans le texte."""
    artifacts = []

    # Pattern: lignes commençant par | avec séparateur |---|---|
    table_pattern = re.compile(
        r'((?:^\|.+\|$\n?)+)', re.MULTILINE
    )
    matches = table_pattern.findall(text)

    for match in matches:
        lines = [l.strip() for l in match.strip().split('\n') if l.strip()]
        if len(lines) < 2:
            continue

        # Parser les headers
        headers = [h.strip() for h in lines[0].split('|') if h.strip()]

        # Parser les rows (skip separator line)
        rows = []
        for line in lines[2:]:  # Skip header + separator
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells:
                rows.append(cells)

        if headers and rows:
            artifacts.append(Artifact(
                id=_generate_id(),
                type=ArtifactType.TABLE,
                title=f"Tableau ({len(rows)} lignes)",
                data={"headers": headers, "rows": rows},
                vertical=vertical,
                created_at=_now_iso(),
            ))

    return artifacts


def _detect_code_blocks(text: str, vertical: str) -> list[Artifact]:
    """Détecter les blocs de code."""
    artifacts = []
    code_pattern = re.compile(r'```(\w*)\n([\s\S]*?)```', re.MULTILINE)
    matches = code_pattern.findall(text)

    for lang, code in matches:
        artifacts.append(Artifact(
            id=_generate_id(),
            type=ArtifactType.CODE,
            title=f"Code {lang or 'plaintext'}",
            data={"language": lang or "plaintext", "code": code.strip()},
            vertical=vertical,
            created_at=_now_iso(),
        ))

    return artifacts


def _detect_metrics(text: str, vertical: str) -> list[Artifact]:
    """Détecter les métriques et montants dans le texte."""
    metrics = {}

    # Montants CHF
    chf_pattern = re.compile(r'CHF\s*([\d\s\',]+\.?\d*)', re.IGNORECASE)
    for m in chf_pattern.finditer(text):
        val = m.group(1).replace("'", "").replace(" ", "").replace(",", "")
        try:
            metrics[f"montant_{len(metrics)}"] = {"value": float(val), "currency": "CHF"}
        except ValueError:
            pass

    # TVA
    tva_pattern = re.compile(r'TVA[:\s]+([\d.]+)\s*%?', re.IGNORECASE)
    for m in tva_pattern.finditer(text):
        metrics["tva_rate"] = {"value": float(m.group(1)), "unit": "%"}

    # Scores de confiance
    conf_pattern = re.compile(r'confiance[:\s]+([\d.]+)\s*/?\s*100?', re.IGNORECASE)
    for m in conf_pattern.finditer(text):
        metrics["confidence"] = {"value": float(m.group(1)), "unit": "score"}

    # Pourcentages
    pct_pattern = re.compile(r'([\d.]+)\s*%', re.IGNORECASE)
    for m in pct_pattern.finditer(text):
        val = float(m.group(1))
        if val not in [8.1, 2.6, 3.8, 100]:  # Skip TVA rates and 100%
            metrics[f"percentage_{len(metrics)}"] = {"value": val, "unit": "%"}

    if metrics:
        return [Artifact(
            id=_generate_id(),
            type=ArtifactType.METRICS,
            title="Métriques détectées",
            data=metrics,
            vertical=vertical,
            created_at=_now_iso(),
        )]
    return []


# ═══════════════════════════════════════════════════════════════
# GENERATION — Génère des artefacts à partir de données
# ═══════════════════════════════════════════════════════════════

def generate_compliance_card(
    vertical: str,
    validation_result: dict,
    review_result: dict = None,
) -> Artifact:
    """Générer une fiche de conformité structurée."""
    checks = validation_result.get("checks", [])
    warnings = validation_result.get("warnings", [])
    blocks = validation_result.get("blocks", [])
    score = validation_result.get("compliance_score", 1.0)

    # Score color
    if score >= 0.8:
        status = "conforme"
        color = "#34d399"
    elif score >= 0.5:
        status = "attention"
        color = "#fbbf24"
    else:
        status = "non_conforme"
        color = "#fb7185"

    return Artifact(
        id=_generate_id(),
        type=ArtifactType.COMPLIANCE_CARD,
        title=f"Fiche Conformité — {vertical}",
        data={
            "vertical": vertical,
            "status": status,
            "score": score,
            "color": color,
            "checks_total": len(checks),
            "checks_ok": sum(1 for c in checks if c.get("status") == "ok"),
            "warnings": warnings,
            "blocks": blocks,
            "review_verdict": review_result.get("verdict") if review_result else None,
            "review_iterations": review_result.get("total_iterations") if review_result else 0,
        },
        vertical=vertical,
        created_at=_now_iso(),
        metadata={"type": "compliance_card"},
    )


def generate_trust_timeline(
    events: list[dict],
    vertical: str = "",
) -> Artifact:
    """Générer une timeline de confiance à partir d'événements WORM."""
    timeline_points = []
    for evt in events:
        timeline_points.append({
            "timestamp": evt.get("timestamp", ""),
            "event": evt.get("event_type", ""),
            "agent": evt.get("agent_source", ""),
            "vertical": evt.get("vertical", ""),
        })

    return Artifact(
        id=_generate_id(),
        type=ArtifactType.TIMELINE,
        title="Timeline de confiance",
        data={"events": timeline_points[:50]},
        vertical=vertical,
        created_at=_now_iso(),
    )


def generate_document_preview(
    template_id: str,
    template_data: dict,
    filled_fields: dict = None,
) -> Artifact:
    """Générer un aperçu de document pré-rempli."""
    fields = template_data.get("fields", [])
    filled = filled_fields or {}

    return Artifact(
        id=_generate_id(),
        type=ArtifactType.DOCUMENT,
        title=template_data.get("title", "Document"),
        data={
            "template_id": template_id,
            "category": template_data.get("category"),
            "description": template_data.get("description"),
            "regulation_ref": template_data.get("regulation_ref"),
            "fields": [
                {"name": f, "value": filled.get(f, ""), "filled": f in filled}
                for f in fields
            ],
        },
        vertical=template_data.get("vertical", ""),
        created_at=_now_iso(),
    )


def generate_summary(
    title: str,
    items: list[dict],
    vertical: str = "",
) -> Artifact:
    """Générer un résumé structuré."""
    return Artifact(
        id=_generate_id(),
        type=ArtifactType.SUMMARY,
        title=title,
        data={"items": items, "count": len(items)},
        vertical=vertical,
        created_at=_now_iso(),
    )
