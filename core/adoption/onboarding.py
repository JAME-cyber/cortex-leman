"""
Onboarding rapide Cortex Leman v5.

Le quickstart génère un environnement sandbox démontrable en moins de deux minutes :
compte démo, intentions pré-remplies et dossier d'arbitrage exemplaire.

Important : cette couche accélère l'expérience utilisateur, mais ne contourne jamais
le Médiateur déterministe, le journal WORM ni l'arbitrage humain.
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from .demo_pack import generate_demo
from .templates import AppliedTemplate, TemplateRegistry


LEGAL_DISCLAIMERS: tuple[str, ...] = (
    "Sandbox d'adoption : données de démonstration uniquement, watermark DEMO.",
    "Secret professionnel art. 321 CP : ne pas importer de données client réelles sans environnement validé.",
    "RGPD/LPD : minimisation des données et rétention limitée.",
    "Cortex Leman assiste l'expert et ne le remplace jamais.",
    "Le Médiateur déterministe et le journal WORM restent obligatoires, y compris en onboarding.",
)


class SandboxAccount(BaseModel):
    """Compte sandbox créé pour une démonstration rapide."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(default_factory=lambda: f"sandbox-{uuid4().hex[:12]}")
    vertical: str
    user_role: str
    mode: str = Field(default="HAUTE_PROTECTION_LOCAL_ONLY")
    watermark: str = Field(default="DEMO")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(UTC) + timedelta(days=7))
    data_retention_days: int = Field(default=7, ge=1, le=7)
    mediator_required: bool = Field(default=True)
    worm_journal_required: bool = Field(default=True)
    human_arbitration_required: bool = Field(default=True)
    disclaimers: list[str] = Field(default_factory=lambda: list(LEGAL_DISCLAIMERS))


class DemoIntention(BaseModel):
    """Intention pré-remplie et routable par le bus d'agents."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(default_factory=lambda: f"intent-demo-{uuid4().hex[:12]}")
    vertical: str
    title: str
    template_id: str
    payload: dict[str, Any]
    requires_mediator: bool = Field(default=True)
    requires_worm_journal: bool = Field(default=True)
    human_arbitration_allowed: bool = Field(default=True)
    status: str = Field(default="prefilled")
    watermark: str = Field(default="DEMO")


class ArbitrationExample(BaseModel):
    """Dossier d'arbitrage humain exemplaire pour montrer la chaîne de confiance."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(default_factory=lambda: f"arb-demo-{uuid4().hex[:12]}")
    title: str
    reason_for_freeze: str
    mediator_rule_id: str
    human_decision: str
    status_sequence: list[str]
    worm_hash_chain_preview: list[str]
    disclaimers: list[str] = Field(default_factory=lambda: list(LEGAL_DISCLAIMERS))


class OnboardingEnvironment(BaseModel):
    """Environnement quickstart complet remis à l'utilisateur."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    account: SandboxAccount
    intentions: list[DemoIntention]
    arbitration_case: ArbitrationExample
    demo_pack_id: str
    created_in_seconds_budget: int = Field(default=120)
    next_actions: list[str]
    trust_guarantees: list[str]
    disclaimers: list[str] = Field(default_factory=lambda: list(LEGAL_DISCLAIMERS))


async def quickstart(vertical: str, user_role: str) -> OnboardingEnvironment:
    """
    Génère un environnement demo prêt à l'emploi.

    La fonction est async pour s'intégrer au bus NATS et aux orchestrateurs agents,
    mais ne réalise ici aucune persistance durable.
    """
    normalized_vertical = vertical.strip().lower()
    normalized_role = user_role.strip().lower()
    registry = TemplateRegistry()
    templates = registry.list(vertical=normalized_vertical, user_role=normalized_role)
    if len(templates) < 3:
        templates = registry.list(vertical=normalized_vertical)
    if not templates:
        raise ValueError(f"Vertical non supporté pour quickstart: {vertical}")

    account = SandboxAccount(vertical=normalized_vertical, user_role=normalized_role)
    selected = templates[:3]
    applied_templates: list[AppliedTemplate] = [
        registry.apply(template.id, overrides={"sandbox_account_id": account.id}, watermark="DEMO") for template in selected
    ]

    intentions = [
        DemoIntention(
            vertical=applied.vertical,
            title=applied.title,
            template_id=applied.template_id,
            payload=applied.payload,
        )
        for applied in applied_templates
    ]

    demo_pack = generate_demo(normalized_vertical)
    arbitration_case = _build_arbitration_example(normalized_vertical)

    await asyncio.sleep(0)

    return OnboardingEnvironment(
        account=account,
        intentions=intentions,
        arbitration_case=arbitration_case,
        demo_pack_id=demo_pack.id,
        next_actions=[
            "Ouvrir la première intention pré-remplie.",
            "Consulter le passage agents → Médiateur → gel.",
            "Lire le dossier d'arbitrage humain exemplaire.",
            "Déclencher un dégel simulé après validation humaine.",
            "Remplacer ensuite les données DEMO par un dossier client uniquement dans un environnement validé.",
        ],
        trust_guarantees=[
            "Aucun contournement du Médiateur déterministe.",
            "Chaque événement démontré possède une empreinte WORM simulée et hash-chaînée.",
            "Mode Haute Protection local only activé par défaut.",
            "Watermark DEMO appliqué à toutes les intentions.",
            "Rétention sandbox limitée à 7 jours.",
            "L'outil assiste l'expert régulé, sans décision finale automatique.",
        ],
    )


def quickstart_sync(vertical: str, user_role: str) -> OnboardingEnvironment:
    """Pont synchrone pour scripts de démonstration."""
    return asyncio.run(quickstart(vertical, user_role))


def _build_arbitration_example(vertical: str) -> ArbitrationExample:
    """Construit un dossier d'arbitrage représentatif par vertical."""
    if vertical == "avocat":
        title = "Gel revue NDA — droit applicable hors UE/CH et non-concurrence longue"
        reason = "Règle contract-review-001 déclenchée : non-concurrence supérieure à 24 mois."
        rule_id = "contract-review-001"
        decision = "L'avocat réduit la durée à 12 mois, limite le territoire et valide le dégel."
    elif vertical == "comptable":
        title = "Gel écriture TVA — seuil et décision fiscale"
        reason = "Règle comptable : aucune décision fiscale automatique sans validation humaine."
        rule_id = "comptable-001"
        decision = "L'expert-comptable valide le traitement après contrôle des pièces."
    elif vertical == "banque":
        title = "Gel KYC — divergence bénéficiaire effectif"
        reason = "Règle conformité : bénéficiaire effectif incohérent avec documents KYC."
        rule_id = "banque-kyc-001"
        decision = "Le compliance officer demande une pièce complémentaire puis dégèle."
    else:
        title = f"Gel démo {vertical} — validation humaine obligatoire"
        reason = "Règle Médiateur critique déclenchée."
        rule_id = f"{vertical}-demo-001"
        decision = "L'expert arbitre puis autorise le dégel."

    events = [
        {"event": "intention_created", "vertical": vertical, "watermark": "DEMO"},
        {"event": "agents_completed", "agents": 5},
        {"event": "mediator_freeze", "rule_id": rule_id},
        {"event": "human_arbitration", "decision": decision},
        {"event": "mediator_unfreeze", "rule_id": rule_id},
    ]

    return ArbitrationExample(
        title=title,
        reason_for_freeze=reason,
        mediator_rule_id=rule_id,
        human_decision=decision,
        status_sequence=["created", "agent_reviewed", "frozen", "human_arbitrated", "unfrozen", "completed"],
        worm_hash_chain_preview=_worm_hash_chain(events),
    )


def _worm_hash_chain(events: list[dict[str, Any]]) -> list[str]:
    """Produit une prévisualisation hash-chaînée sans persistance durable."""
    previous = "0" * 64
    chain: list[str] = []
    for event in events:
        payload = json.dumps(event, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        digest = sha256(f"{previous}|{payload}".encode("utf-8")).hexdigest()
        chain.append(digest)
        previous = digest
    return chain
