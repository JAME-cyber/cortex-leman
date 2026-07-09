"""
Bibliothèque de templates métier prêts à l'emploi.

L'utilisateur démarre d'une intention pré-configurée plutôt que d'une page blanche.
Chaque template encode aussi les garde-fous : Médiateur, journal WORM, arbitrage
humain et disclaimers légaux.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Iterable
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


LEGAL_DISCLAIMERS: tuple[str, ...] = (
    "Template de démarrage : à adapter et valider par l'expert régulé.",
    "Secret professionnel art. 321 CP pour les avocats ; RGPD/LPD pour toutes données personnelles.",
    "Cortex Leman assiste l'expert et ne rend aucune décision finale automatique.",
    "Le Médiateur déterministe et le journal WORM ne doivent jamais être contournés.",
)


class BusinessTemplate(BaseModel):
    """Template métier réutilisable pour créer une intention Cortex."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str
    vertical: str
    name: str
    title: str
    description: str
    user_roles: list[str]
    intention_type: str
    default_payload: dict[str, Any]
    required_controls: list[str]
    mediator_subject: str
    worm_journal_stream: str
    agents: list[str]
    tags: list[str] = Field(default_factory=list)
    disclaimers: list[str] = Field(default_factory=lambda: list(LEGAL_DISCLAIMERS))


class AppliedTemplate(BaseModel):
    """Template appliqué sous forme d'intention prête à router."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    intention_id: str = Field(default_factory=lambda: f"intent-{uuid4().hex[:16]}")
    template_id: str
    vertical: str
    title: str
    intention_type: str
    payload: dict[str, Any]
    routing: dict[str, Any]
    controls: list[str]
    requires_mediator: bool = Field(default=True)
    requires_worm_journal: bool = Field(default=True)
    human_arbitration_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    watermark: str | None = None
    disclaimers: list[str] = Field(default_factory=lambda: list(LEGAL_DISCLAIMERS))


class TemplateRegistry:
    """Registre de templates métier versionnés en mémoire."""

    def __init__(self, templates: Iterable[BusinessTemplate] | None = None) -> None:
        """Initialise le registre avec les templates par défaut."""
        self._templates: dict[str, BusinessTemplate] = {}
        for template in templates or _default_templates():
            self.register(template)

    def register(self, template: BusinessTemplate) -> None:
        """Ajoute ou remplace un template."""
        self._templates[template.id] = template

    def list(self, *, vertical: str | None = None, user_role: str | None = None) -> list[BusinessTemplate]:
        """Liste les templates filtrés par vertical et rôle utilisateur."""
        vertical_norm = vertical.strip().lower() if vertical else None
        role_norm = user_role.strip().lower() if user_role else None
        templates = list(self._templates.values())
        if vertical_norm:
            templates = [template for template in templates if template.vertical == vertical_norm]
        if role_norm:
            templates = [
                template
                for template in templates
                if not template.user_roles or role_norm in {role.lower() for role in template.user_roles}
            ]
        return sorted(templates, key=lambda item: (item.vertical, item.name))

    def get(self, template_id: str) -> BusinessTemplate:
        """Charge un template par identifiant."""
        try:
            return self._templates[template_id]
        except KeyError as exc:
            raise KeyError(f"Template inconnu: {template_id}") from exc

    def load(self, template_id: str) -> BusinessTemplate:
        """Alias explicite pour `get`."""
        return self.get(template_id)

    def apply(
        self,
        template_id: str,
        *,
        overrides: dict[str, Any] | None = None,
        watermark: str | None = None,
    ) -> AppliedTemplate:
        """
        Applique un template pour produire une intention pré-configurée.

        Les garde-fous de confiance sont toujours conservés, même si des overrides
        UX sont fournis.
        """
        template = self.get(template_id)
        payload = deepcopy(template.default_payload)
        if overrides:
            payload = _deep_merge(payload, deepcopy(overrides))

        payload["trust"] = _deep_merge(
            payload.get("trust", {}),
            {
                "mediator_required": True,
                "worm_journal_required": True,
                "human_arbitration_enabled": True,
                "no_final_decision": True,
                "watermark": watermark,
            },
        )

        return AppliedTemplate(
            template_id=template.id,
            vertical=template.vertical,
            title=template.title,
            intention_type=template.intention_type,
            payload=payload,
            routing={
                "nats_subject": template.mediator_subject,
                "agents": template.agents,
                "mediator": "deterministic_jsonlogic",
                "worm_stream": template.worm_journal_stream,
            },
            controls=sorted(
                set(template.required_controls)
                | {
                    "mediator_required",
                    "worm_hash_chain_required",
                    "human_arbitration_for_freeze",
                    "no_automatic_final_decision",
                }
            ),
            watermark=watermark,
        )


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Fusion récursive déterministe de dictionnaires."""
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _default_templates() -> list[BusinessTemplate]:
    """Définit les templates métier de démarrage."""
    common_controls = [
        "secret_professionnel_or_confidentiality",
        "rgpd_lpd_minimisation",
        "mediator_jsonlogic",
        "worm_hash_chain",
        "human_arbitration",
    ]

    return [
        BusinessTemplate(
            id="avocat-contract-review-v1",
            vertical="avocat",
            name="Revue de contrat",
            title="Revue assistée d'un contrat client",
            description="Détecte clauses risquées, déséquilibres, droit applicable suspect et points à arbitrer.",
            user_roles=["avocat", "juriste", "partner", "collaborateur"],
            intention_type="contract_review",
            default_payload={
                "vertical": "avocat",
                "workflow": "contract_review",
                "document_slots": ["contrat", "annexes", "instructions_client"],
                "risk_focus": [
                    "non_concurrence",
                    "droit_applicable",
                    "juridiction",
                    "penalites",
                    "responsabilite",
                    "donnees_personnelles",
                ],
                "expected_output": "rapport_de_revue_non_decisionnel",
                "legal_disclaimer": "Assiste l'avocat ; secret professionnel art. 321 CP ; RGPD/LPD.",
            },
            required_controls=common_controls,
            mediator_subject="mediator.intentions.avocat.contract_review",
            worm_journal_stream="worm.avocat.contract_review",
            agents=["intake_agent", "legal_analysis_agent", "risk_agent", "contradiction_agent", "synthesis_agent"],
            tags=["wedge", "contrat", "roi_mesurable"],
        ),
        BusinessTemplate(
            id="avocat-jurisprudence-search-v1",
            vertical="avocat",
            name="Recherche jurisprudence",
            title="Recherche assistée de jurisprudence",
            description="Prépare une recherche jurisprudentielle sourcée, sans conclusion automatique.",
            user_roles=["avocat", "juriste", "collaborateur"],
            intention_type="jurisprudence_search",
            default_payload={
                "vertical": "avocat",
                "workflow": "jurisprudence_search",
                "query_slots": ["question_juridique", "juridiction", "periode", "mots_cles"],
                "source_policy": "sources_citees_obligatoires",
                "expected_output": "note_de_recherche_a_valider",
                "legal_disclaimer": "Sources et raisonnement à valider par avocat.",
            },
            required_controls=common_controls,
            mediator_subject="mediator.intentions.avocat.jurisprudence_search",
            worm_journal_stream="worm.avocat.jurisprudence",
            agents=["intake_agent", "retrieval_agent", "citation_agent", "contradiction_agent", "synthesis_agent"],
            tags=["jurisprudence", "recherche", "sources"],
        ),
        BusinessTemplate(
            id="avocat-pieces-summary-v1",
            vertical="avocat",
            name="Synthèse pièces",
            title="Synthèse assistée de pièces",
            description="Produit une chronologie et une synthèse de pièces avec incertitudes et conflits.",
            user_roles=["avocat", "juriste", "paralegal", "collaborateur"],
            intention_type="evidence_summary",
            default_payload={
                "vertical": "avocat",
                "workflow": "evidence_summary",
                "document_slots": ["pieces", "bordereau", "instructions"],
                "expected_output": "chronologie_et_synthese_non_conclusive",
                "conflict_policy": "contradictions_signalees",
                "legal_disclaimer": "Ne qualifie pas définitivement les faits ; validation avocat requise.",
            },
            required_controls=common_controls,
            mediator_subject="mediator.intentions.avocat.evidence_summary",
            worm_journal_stream="worm.avocat.pieces",
            agents=["intake_agent", "extraction_agent", "timeline_agent", "contradiction_agent", "synthesis_agent"],
            tags=["pieces", "chronologie", "contentieux"],
        ),
        BusinessTemplate(
            id="comptable-reconciliation-v1",
            vertical="comptable",
            name="Rapprochement",
            title="Rapprochement comptable assisté",
            description="Rapproche écritures, factures et relevés avec anomalies à valider.",
            user_roles=["comptable", "expert-comptable", "fiduciaire"],
            intention_type="accounting_reconciliation",
            default_payload={
                "vertical": "comptable",
                "workflow": "reconciliation",
                "document_slots": ["grand_livre", "factures", "releves_bancaires"],
                "expected_output": "liste_ecarts_a_valider",
                "decision_policy": "aucune_decision_fiscale_automatique",
            },
            required_controls=common_controls,
            mediator_subject="mediator.intentions.comptable.reconciliation",
            worm_journal_stream="worm.comptable.reconciliation",
            agents=["intake_agent", "extraction_agent", "matching_agent", "anomaly_agent", "synthesis_agent"],
            tags=["rapprochement", "fiduciaire"],
        ),
        BusinessTemplate(
            id="comptable-vat-threshold-alert-v1",
            vertical="comptable",
            name="Alerte seuil TVA",
            title="Alerte assistée de seuil TVA",
            description="Détecte les franchissements de seuils et prépare un dossier de validation.",
            user_roles=["comptable", "expert-comptable", "fiduciaire"],
            intention_type="vat_threshold_alert",
            default_payload={
                "vertical": "comptable",
                "workflow": "vat_threshold_alert",
                "data_slots": ["chiffre_affaires", "periode", "pays", "historique"],
                "expected_output": "alerte_non_decisionnelle",
                "decision_policy": "validation_expert_obligatoire",
            },
            required_controls=common_controls,
            mediator_subject="mediator.intentions.comptable.vat_threshold",
            worm_journal_stream="worm.comptable.tva",
            agents=["intake_agent", "calculation_agent", "threshold_agent", "compliance_agent", "synthesis_agent"],
            tags=["tva", "seuil", "fiscal"],
        ),
        BusinessTemplate(
            id="banque-kyc-v1",
            vertical="banque",
            name="KYC",
            title="Dossier KYC assisté",
            description="Prépare et contrôle un dossier KYC avec gels conformité.",
            user_roles=["compliance", "banquier", "risk-officer", "analyste"],
            intention_type="kyc_review",
            default_payload={
                "vertical": "banque",
                "workflow": "kyc_review",
                "document_slots": ["piece_identite", "justificatif_domicile", "ubo", "source_des_fonds"],
                "expected_output": "dossier_kyc_a_valider",
                "decision_policy": "aucune_acceptation_client_automatique",
            },
            required_controls=common_controls,
            mediator_subject="mediator.intentions.banque.kyc",
            worm_journal_stream="worm.banque.kyc",
            agents=["intake_agent", "identity_agent", "ubo_agent", "sanctions_agent", "synthesis_agent"],
            tags=["kyc", "compliance", "aml"],
        ),
        BusinessTemplate(
            id="banque-transaction-compliance-v1",
            vertical="banque",
            name="Conformité transaction",
            title="Contrôle assisté de transaction",
            description="Signale anomalies transactionnelles et prépare arbitrage compliance.",
            user_roles=["compliance", "banquier", "risk-officer", "analyste"],
            intention_type="transaction_compliance",
            default_payload={
                "vertical": "banque",
                "workflow": "transaction_compliance",
                "data_slots": ["transaction", "contrepartie", "historique", "justificatifs"],
                "expected_output": "rapport_anomalies_non_decisionnel",
                "decision_policy": "aucun_blocage_definitif_automatique",
            },
            required_controls=common_controls,
            mediator_subject="mediator.intentions.banque.transaction_compliance",
            worm_journal_stream="worm.banque.transactions",
            agents=["intake_agent", "transaction_agent", "sanctions_agent", "risk_agent", "synthesis_agent"],
            tags=["transaction", "aml", "conformite"],
        ),
    ]
