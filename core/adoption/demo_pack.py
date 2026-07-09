"""
Générateur de démos Cortex Leman v5.

Une démo doit montrer le moat : agents pair-à-pair, Médiateur déterministe,
gel, arbitrage humain, dégel et résultat journalisé WORM. Les cas sont anonymisés
et watermarqués DEMO.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


LEGAL_DISCLAIMERS: tuple[str, ...] = (
    "Dossier de démonstration anonymisé, watermark DEMO.",
    "Ne pas utiliser comme conseil professionnel ni comme décision finale.",
    "Secret professionnel art. 321 CP, RGPD et LPD : importer des données réelles uniquement dans un environnement validé.",
    "La démo illustre le Médiateur et le journal WORM ; elle ne les contourne pas.",
)


class DemoStep(BaseModel):
    """Étape auditable du parcours de démonstration."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    order: int = Field(..., ge=1)
    actor: str
    event_type: str
    description: str
    input_ref: str | None = None
    output_ref: str | None = None
    trust_control: str
    mediator_rule_id: str | None = None
    worm_hash: str
    requires_human: bool = False


class DemoPack(BaseModel):
    """Dossier démo complet pour vente, pitch ou onboarding."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(default_factory=lambda: f"demo-{uuid4().hex[:12]}")
    vertical: str
    title: str
    anonymized_case: dict[str, Any]
    initial_intention: dict[str, Any]
    journey: list[DemoStep]
    arbitration_result: dict[str, Any]
    final_result: dict[str, Any]
    moat_points: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    watermark: str = Field(default="DEMO")
    disclaimers: list[str] = Field(default_factory=lambda: list(LEGAL_DISCLAIMERS))


def generate_demo(vertical: str) -> DemoPack:
    """
    Produit un dossier démo convaincant pour un vertical.

    La chaîne illustrée est toujours :
    intention → agents → Médiateur → gel → arbitrage humain → dégel → résultat.
    """
    normalized = vertical.strip().lower()
    case = _case_for_vertical(normalized)
    events = _events_for_case(normalized, case)
    hashes = _hash_chain(events)

    journey = [
        DemoStep(
            order=index + 1,
            actor=event["actor"],
            event_type=event["event_type"],
            description=event["description"],
            input_ref=event.get("input_ref"),
            output_ref=event.get("output_ref"),
            trust_control=event["trust_control"],
            mediator_rule_id=event.get("mediator_rule_id"),
            worm_hash=hashes[index],
            requires_human=event.get("requires_human", False),
        )
        for index, event in enumerate(events)
    ]

    return DemoPack(
        vertical=normalized,
        title=case["title"],
        anonymized_case=case["anonymized_case"],
        initial_intention=case["initial_intention"],
        journey=journey,
        arbitration_result=case["arbitration_result"],
        final_result=case["final_result"],
        moat_points=[
            "Back-end souverain, déterministe, on-prem compatible professions régulées.",
            "Agents pair-à-pair : aucune boîte noire centrale ne décide seule.",
            "Médiateur JsonLogic : gels explicables et reproductibles.",
            "Journal WORM hash-chaîné : auditabilité de bout en bout.",
            "Arbitrage humain : l'expert régulé conserve la décision.",
            "UX rapide côté adoption sans affaiblir la confiance.",
        ],
    )


def _case_for_vertical(vertical: str) -> dict[str, Any]:
    """Retourne un cas anonymisé par vertical."""
    if vertical == "avocat":
        return {
            "title": "Démo avocat — revue NDA fournisseur SaaS",
            "anonymized_case": {
                "client": "PME romande anonymisée",
                "counterparty": "Fournisseur SaaS international anonymisé",
                "matter": "NDA + conditions d'évaluation logiciel",
                "pain": "Revue facturable répétable, délai attendu < 24h, secret professionnel strict.",
            },
            "initial_intention": {
                "type": "contract_review",
                "template_id": "avocat-contract-review-v1",
                "documents": ["nda_anonymise_demo.txt"],
                "watermark": "DEMO",
                "no_final_decision": True,
            },
            "arbitration_result": {
                "freeze_reason": "Non-concurrence 36 mois et droit de New York détectés.",
                "mediator_rule_id": "contract-review-001",
                "human_arbitrator": "avocat responsable",
                "decision": "Réduire non-concurrence à 12 mois, limiter territoire CH/UE, demander droit suisse ou français.",
            },
            "final_result": {
                "status": "unfrozen_after_human_validation",
                "deliverable": "rapport de revue non décisionnel validé par avocat",
                "client_value": "risques prioritaires identifiés en minutes, arbitrage expert conservé",
            },
        }
    if vertical == "comptable":
        return {
            "title": "Démo comptable — rapprochement et alerte TVA",
            "anonymized_case": {
                "client": "Société de services anonymisée",
                "matter": "Rapprochement mensuel + seuil TVA",
                "pain": "Écarts récurrents, risque fiscal, besoin d'audit trail.",
            },
            "initial_intention": {
                "type": "accounting_reconciliation",
                "template_id": "comptable-reconciliation-v1",
                "documents": ["grand_livre_demo.csv", "releves_demo.csv"],
                "watermark": "DEMO",
                "no_final_decision": True,
            },
            "arbitration_result": {
                "freeze_reason": "Seuil TVA proche et qualification fiscale non validée.",
                "mediator_rule_id": "comptable-001",
                "human_arbitrator": "expert-comptable",
                "decision": "Valider les pièces, documenter l'analyse et planifier déclaration si seuil confirmé.",
            },
            "final_result": {
                "status": "unfrozen_after_human_validation",
                "deliverable": "liste d'écarts et alerte TVA à valider",
                "client_value": "moins de tri manuel, aucune décision fiscale automatique",
            },
        }
    if vertical == "banque":
        return {
            "title": "Démo banque — KYC et conformité transaction",
            "anonymized_case": {
                "client": "Client corporate anonymisé",
                "matter": "Entrée en relation + transaction atypique",
                "pain": "Pression commerciale, exigence AML, audit interne.",
            },
            "initial_intention": {
                "type": "kyc_review",
                "template_id": "banque-kyc-v1",
                "documents": ["kyc_demo.zip"],
                "watermark": "DEMO",
                "no_final_decision": True,
            },
            "arbitration_result": {
                "freeze_reason": "Divergence UBO et justificatif source des fonds incomplet.",
                "mediator_rule_id": "banque-kyc-001",
                "human_arbitrator": "compliance officer",
                "decision": "Demander justificatif complémentaire et maintenir gel jusqu'à réception.",
            },
            "final_result": {
                "status": "human_review_required",
                "deliverable": "dossier KYC structuré avec points bloquants",
                "client_value": "explicabilité conformité sans acceptation automatique",
            },
        }
    raise ValueError(f"Vertical non supporté pour démo: {vertical}")


def _events_for_case(vertical: str, case: dict[str, Any]) -> list[dict[str, Any]]:
    """Crée le parcours graphe de confiance pour un cas."""
    rule_id = case["arbitration_result"]["mediator_rule_id"]
    return [
        {
            "actor": "user",
            "event_type": "intention.created",
            "description": "L'utilisateur démarre depuis un template métier pré-rempli.",
            "input_ref": "template",
            "output_ref": "intention",
            "trust_control": "watermark DEMO, minimisation données, secret professionnel",
        },
        {
            "actor": "agent.intake",
            "event_type": "agent.completed",
            "description": "Agent intake normalise les documents et prépare le contexte.",
            "input_ref": "intention",
            "output_ref": "normalized_case",
            "trust_control": "journal WORM avant/après traitement",
        },
        {
            "actor": "agent.analysis",
            "event_type": "agent.completed",
            "description": "Agent métier extrait risques, anomalies ou points de contrôle.",
            "input_ref": "normalized_case",
            "output_ref": "analysis_findings",
            "trust_control": "LLM derrière interface abstraite, aucune décision finale",
        },
        {
            "actor": "agent.contradiction",
            "event_type": "agent.completed",
            "description": "Agent contradicteur cherche incohérences et incertitudes.",
            "input_ref": "analysis_findings",
            "output_ref": "contradictions",
            "trust_control": "pair-à-pair, séparation des rôles",
        },
        {
            "actor": "mediator",
            "event_type": "mediator.freeze",
            "description": "Médiateur JsonLogic déclenche un gel déterministe.",
            "input_ref": "analysis_findings",
            "output_ref": "freeze_case",
            "trust_control": "règle déterministe reproductible",
            "mediator_rule_id": rule_id,
            "requires_human": True,
        },
        {
            "actor": "human.arbitrator",
            "event_type": "human.arbitrated",
            "description": "L'expert régulé arbitre le point gelé et documente sa décision.",
            "input_ref": "freeze_case",
            "output_ref": "human_decision",
            "trust_control": "responsabilité professionnelle conservée",
            "mediator_rule_id": rule_id,
            "requires_human": True,
        },
        {
            "actor": "mediator",
            "event_type": "mediator.unfreeze",
            "description": "Le Médiateur autorise le dégel après validation humaine.",
            "input_ref": "human_decision",
            "output_ref": "unfrozen_case",
            "trust_control": "dégel conditionné à l'arbitrage humain journalisé",
            "mediator_rule_id": rule_id,
        },
        {
            "actor": "agent.synthesis",
            "event_type": "result.completed",
            "description": "Synthèse finale assistée, marquée non décisionnelle et prête pour revue expert.",
            "input_ref": "unfrozen_case",
            "output_ref": "final_deliverable",
            "trust_control": "rapport WORM, disclaimers, décision finale humaine",
        },
    ]


def _hash_chain(events: list[dict[str, Any]]) -> list[str]:
    """Hash-chain déterministe de démonstration."""
    previous = "0" * 64
    hashes: list[str] = []
    for event in events:
        payload = json.dumps(event, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        digest = sha256(f"{previous}|{payload}".encode("utf-8")).hexdigest()
        hashes.append(digest)
        previous = digest
    return hashes
