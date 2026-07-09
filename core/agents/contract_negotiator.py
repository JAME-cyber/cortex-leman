"""
Cortex Leman v5 — Contract Negotiation

Inspiré de: Ash (Anthropic Applied AI) — « The two agents negotiate what "done" means. »

Principe: avant que l'Agent Action exécute, le Raisonnement et le Médiateur
co-créent un contrat de critères d'acceptation. Ce contrat définit ce que
"fait" signifie pour cette intention spécifique.

Différences vs Anthropic:
- Anthropic: deux LLMs négocient → risque de convergence sur faux optimum
- Cortex Leman: Raisonnement (LLM) propose + Médiateur (JsonLogic déterministe) valide
- Le Médiateur ne PEUT PAS être convaincu par un bon argument LLM — il applique des règles
- C'est l'équilibre entre flexibilité (LLM) et rigueur (déterministe)

Pipeline:
  Intention → Reasoning propose contrat → Médiateur valide/rejette →
    si rejeté → Reasoning affine (max 3 rounds) →
    si validé → contrat persisté en JSON → Action exécute → Évaluateur vérifie

Contrat persisté dans: data/contracts/{intention_id}.json
"""
import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from core.mediator.rules_engine import rules_engine
from core.bus.nats_client import bus
from core.bus.subjects import subjects
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)


# ── Modèles ───────────────────────────────────────────────────

class ContractCriterion(BaseModel):
    """Un critère du contrat d'acceptation"""
    id: str = Field(default_factory=lambda: f"c-{uuid.uuid4().hex[:6]}")
    description: str
    test_method: str  # "api_call" | "unit_test" | "visual_check" | "journal_check" | "llm_eval"
    expected_result: str  # Description de ce qui constitue un PASS
    category: str = "functional"  # "functional" | "security" | "compliance" | "ux" | "design"
    weight: float = 0.8
    required: bool = True
    source: str = "reasoning"  # "reasoning" | "mediator"


class Contract(BaseModel):
    """
    Contrat d'acceptation co-créé entre le Raisonnement et le Médiateur.

    Ce contrat est ce que l'Agent Évaluateur vérifiera après l'exécution.
    Il est persisté en JSON et versionné.
    """
    contract_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    intention_id: str
    vertical: str
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    version: int = 1

    # Les critères négociés
    criteria: list[ContractCriterion] = Field(default_factory=list)

    # Métadonnées de la négociation
    negotiation_rounds: int = 0
    max_rounds: int = 3
    status: str = "draft"  # "draft" | "negotiating" | "agreed" | "rejected"

    # Qui a participé
    reasoning_proposed: int = 0
    mediator_rejected: int = 0
    mediator_added: int = 0

    # Raison du rejet (si applicable)
    rejection_reasons: list[str] = Field(default_factory=list)


class ContractNegotiator:
    """
    Négociateur de contrats entre le Raisonnement et le Médiateur.

    Processus:
    1. Reasoning propose des critères basés sur l'intention
    2. Médiateur valide chaque critère contre les règles JsonLogic
    3. Si un critère est trop faible ou manquant, Médiateur le rejette/ajoute
    4. Reasoning affine et repropose
    5. Quand les deux s'accordent → contrat persisté

    Le Médiateur ne négocie JAMAIS — il impose des contraintes déterministes.
    Seul le Raisonnement adapte sa proposition.
    """

    # Critères obligatoires par verticale (imposés par le Médiateur)
    MANDATORY_CRITERIA: dict[str, list[ContractCriterion]] = {
        "avocat": [
            ContractCriterion(
                id="mand-avocat-001",
                description="Aucune donnée client n'est envoyée à un modèle externe",
                test_method="journal_check",
                expected_result="Journal WORM montre que toutes les données restent en local",
                category="compliance",
                weight=1.0,
                required=True,
                source="mediator",
            ),
            ContractCriterion(
                id="mand-avocat-002",
                description="Secret professionnel Art. 321 CP préservé dans tous les outputs",
                test_method="llm_eval",
                expected_result="Aucune information permettant d'identifier un client dans les outputs",
                category="compliance",
                weight=1.0,
                required=True,
                source="mediator",
            ),
        ],
        "sante": [
            ContractCriterion(
                id="mand-sante-001",
                description="Données patient conformes LPM + HDS",
                test_method="journal_check",
                expected_result="Data residency vérifié dans le journal",
                category="compliance",
                weight=1.0,
                required=True,
                source="mediator",
            ),
            ContractCriterion(
                id="mand-sante-002",
                description="Aucun diagnostic médical direct — toujours avec réserve professionnelle",
                test_method="llm_eval",
                expected_result="Toute recommandation médicale contient une réserve",
                category="compliance",
                weight=1.0,
                required=True,
                source="mediator",
            ),
        ],
        "banque": [
            ContractCriterion(
                id="mand-banque-001",
                description="Secret bancaire Art. 47 LB préservé",
                test_method="journal_check",
                expected_result="Aucune donnée bancaire dans les logs non-chiffrés",
                category="compliance",
                weight=1.0,
                required=True,
                source="mediator",
            ),
            ContractCriterion(
                id="mand-banque-002",
                description="Seuil KYC 15K CHF respecté — gel automatique si dépassé",
                test_method="api_call",
                expected_result="Transaction > 15K CHF déclenche un gel médiateur",
                category="compliance",
                weight=1.0,
                required=True,
                source="mediator",
            ),
        ],
        "comptable": [
            ContractCriterion(
                id="mand-comptable-001",
                description="Conformité RGPD Art. 22 — pas de décision automatisée sans recours humain",
                test_method="journal_check",
                expected_result="Chaque décision automatisée a un arbitrage humain accessible",
                category="compliance",
                weight=1.0,
                required=True,
                source="mediator",
            ),
        ],
        "rh": [
            ContractCriterion(
                id="mand-rh-001",
                description="Anti-discrimination — pas de scoring biaisé",
                test_method="llm_eval",
                expected_result="Les critères de scoring ne contiennent pas de variables protégées",
                category="compliance",
                weight=1.0,
                required=True,
                source="mediator",
            ),
        ],
    }

    # Critères génériques que le Médiateur exige toujours
    GENERIC_MANDATORY = [
        ContractCriterion(
            id="mand-gen-001",
            description="L'action est enregistrée dans le journal WORM",
            test_method="journal_check",
            expected_result="Entrée WORM avec hash-chainage valide pour cette intention",
            category="compliance",
            weight=0.9,
            required=True,
            source="mediator",
        ),
        ContractCriterion(
            id="mand-gen-002",
            description="Aucune donnée sensible dans les logs non-chiffrés",
            test_method="api_call",
            expected_result="Les réponses API ne contiennent pas de PII en clair",
            category="security",
            weight=1.0,
            required=True,
            source="mediator",
        ),
    ]

    def __init__(self, persist_dir: str = "./data/contracts"):
        self._persist_dir = Path(persist_dir)
        self._persist_dir.mkdir(parents=True, exist_ok=True)

    async def negotiate(
        self,
        intention_id: str,
        vertical: str,
        query: str,
        context: dict = None,
        reasoning_proposal: list[ContractCriterion] = None,
    ) -> Contract:
        """
        Mener la négociation complète entre Reasoning et Médiateur.

        Args:
            intention_id: L'intention à contractualiser
            vertical: La verticale métier
            query: La requête originale
            context: Contexte additionnel
            reasoning_proposal: Critères proposés par le Reasoning (si déjà générés)

        Returns:
            Contract avec status "agreed" ou "rejected"
        """
        contract = Contract(
            intention_id=intention_id,
            vertical=vertical,
        )

        # Phase 1: Le Reasoning propose (ou on génère automatiquement)
        if reasoning_proposal:
            proposed = reasoning_proposal
        else:
            proposed = await self._generate_reasoning_proposal(
                intention_id, vertical, query, context or {}
            )

        contract.reasoning_proposed = len(proposed)

        # Phase 2: Négociation rounds
        for round_num in range(1, contract.max_rounds + 1):
            contract.negotiation_rounds = round_num
            contract.status = "negotiating"

            # Le Médiateur évalue la proposition
            evaluation = self._mediator_evaluate(proposed, vertical)

            if evaluation["accepted"]:
                # Tous les critères sont acceptés
                contract.criteria = proposed
                contract.status = "agreed"
                break

            # Le Médiateur a rejeté certains critères ou en exige des supplémentaires
            contract.mediator_rejected += len(evaluation["rejected"])
            contract.mediator_added += len(evaluation["added"])
            contract.rejection_reasons = evaluation["reasons"]

            if round_num == contract.max_rounds:
                # Dernier round — on force l'accord avec les critères du Médiateur
                contract.criteria = self._force_agreement(proposed, evaluation, vertical)
                contract.status = "agreed"
                logger.warning(
                    f"Contract {contract.contract_id}: accord forcé après "
                    f"{round_num} rounds — Médiateur a imposé {len(evaluation['added'])} critères"
                )
                break

            # Le Reasoning affine sa proposition
            proposed = self._reasoning_refine(proposed, evaluation, vertical)

        # Persister le contrat
        self._persist(contract)

        # Journaliser
        journal.append(
            event_type=JournalEventType.MEDIATOR_CHECK,
            client_id=context.get("client_id", "unknown") if context else "unknown",
            vertical=vertical,
            agent_source="contract_negotiator",
            intention_id=intention_id,
            payload={
                "contract_id": contract.contract_id,
                "status": contract.status,
                "rounds": contract.negotiation_rounds,
                "criteria_count": len(contract.criteria),
                "reasoning_proposed": contract.reasoning_proposed,
                "mediator_rejected": contract.mediator_rejected,
                "mediator_added": contract.mediator_added,
            },
        )

        logger.info(
            f"Contract {contract.contract_id}: {contract.status} "
            f"({len(contract.criteria)} critères, {contract.negotiation_rounds} rounds)"
        )

        return contract

    async def _generate_reasoning_proposal(
        self,
        intention_id: str,
        vertical: str,
        query: str,
        context: dict,
    ) -> list[ContractCriterion]:
        """
        Générer les critères proposés par le Reasoning via LLM.
        Si LLM indisponible, génère des critères par défaut.
        """
        default_criteria = [
            ContractCriterion(
                description=f"La requête '{query[:80]}' est traitée avec succès",
                test_method="api_call",
                expected_result="Response status 2xx avec données valides",
                category="functional",
                weight=0.9,
                required=True,
                source="reasoning",
            ),
            ContractCriterion(
                description="Les résultats sont conformes aux attentes de la verticale",
                test_method="llm_eval",
                expected_result=f"Réponse cohérente avec les règles {vertical}",
                category="compliance",
                weight=0.8,
                required=True,
                source="reasoning",
            ),
        ]

        # Essayer d'enrichir via LLM
        try:
            from core.integrations.llm import llm_service

            task = f"""Pour la verticale '{vertical}', propose 5 critères de validation 
pour cette intention: "{query}"

Contexte: {json.dumps(context, ensure_ascii=False)[:500]}

Pour chaque critère, donne:
- description: ce qu'il vérifie
- test_method: api_call | unit_test | visual_check | journal_check | llm_eval
- expected_result: ce qui constitue un PASS
- category: functional | security | compliance | ux
- required: true/false

FORMAT JSON:
{{"criteria": [{{"description": "...", "test_method": "...", "expected_result": "...", "category": "...", "required": true}}]}}"""

            result = await llm_service.generate_for_agent(
                agent_name="reasoning",
                task=task,
                context=context,
                vertical=vertical,
                client_id="system",
                intention_id=intention_id,
                use_rag=False,
            )

            if result.get("text"):
                import re
                text = result["text"]
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError:
                    match = re.search(r'\{[\s\S]*\}', text)
                    parsed = json.loads(match.group(0)) if match else {}

                llm_criteria = []
                for c in parsed.get("criteria", []):
                    llm_criteria.append(ContractCriterion(
                        description=c.get("description", ""),
                        test_method=c.get("test_method", "api_call"),
                        expected_result=c.get("expected_result", ""),
                        category=c.get("category", "functional"),
                        required=c.get("required", True),
                        source="reasoning",
                    ))

                if llm_criteria:
                    return default_criteria + llm_criteria

        except Exception as e:
            logger.debug(f"LLM proposal generation failed: {e}")

        return default_criteria

    def _mediator_evaluate(
        self,
        proposed: list[ContractCriterion],
        vertical: str,
    ) -> dict:
        """
        Le Médiateur évalue la proposition du Reasoning.
        Déterministe — basé sur les règles JsonLogic et les mandatory criteria.

        Returns:
            {
                "accepted": bool,
                "rejected": list[ContractCriterion],  # Critères rejetés
                "missing": list[str],  # Catégories manquantes
                "added": list[ContractCriterion],  # Critères imposés par le Médiateur
                "reasons": list[str],  # Pourquoi rejeté
            }
        """
        rejected = []
        missing_categories = []
        added = []
        reasons = []

        # 1. Vérifier que les catégories sensibles sont couvertes
        required_categories = {"functional", "security", "compliance"}
        covered_categories = {c.category for c in proposed}
        missing = required_categories - covered_categories

        if missing:
            missing_categories.extend(missing)
            reasons.append(
                f"Catégories manquantes: {missing}. "
                f"Un contrat doit couvrir: functional, security, compliance."
            )

        # 2. Vérifier que les critères ne sont pas trop vagues
        for criterion in proposed:
            if len(criterion.description) < 20:
                rejected.append(criterion)
                reasons.append(
                    f"Critère {criterion.id} trop vague: '{criterion.description}'. "
                    f"Minimum 20 caractères pour être actionnable."
                )
            if len(criterion.expected_result) < 10:
                rejected.append(criterion)
                reasons.append(
                    f"Résultat attendu de {criterion.id} trop vague: "
                    f"'{criterion.expected_result}'. Soyez spécifique."
                )

        # 3. Vérifier les test_methods — pas que du llm_eval
        test_methods = {c.test_method for c in proposed}
        if test_methods == {"llm_eval"}:
            reasons.append(
                "Tous les critères utilisent llm_eval — le contrat doit inclure "
                "au moins un test_method déterministe (api_call, unit_test, journal_check)."
            )

        # 4. Imposer les critères obligatoires de la verticale
        mandatory = list(self.GENERIC_MANDATORY)
        if vertical in self.MANDATORY_CRITERIA:
            mandatory.extend(self.MANDATORY_CRITERIA[vertical])

        for m in mandatory:
            # Vérifier si le critère est déjà couvert
            covered = any(
                self._criteria_overlap(m, p) for p in proposed
            )
            if not covered:
                added.append(m)
                reasons.append(
                    f"Le Médiateur impose: {m.description} ({m.id})"
                )

        # 5. Évaluer contre les règles JsonLogic de la verticale
        rules_results = rules_engine.evaluate(
            vertical,
            {"contract_criteria": [c.model_dump() for c in proposed]},
        )
        for rule in rules_results:
            if rule.triggered and rule.action in ("block", "freeze"):
                reasons.append(f"Règle JsonLogic {rule.rule_id}: {rule.message}")

        accepted = (
            len(rejected) == 0
            and len(missing_categories) == 0
            and len(reasons) == 0
        )

        return {
            "accepted": accepted,
            "rejected": rejected,
            "missing": missing_categories,
            "added": added,
            "reasons": reasons,
        }

    def _reasoning_refine(
        self,
        proposed: list[ContractCriterion],
        evaluation: dict,
        vertical: str,
    ) -> list[ContractCriterion]:
        """
        Le Reasoning affine sa proposition après un rejet du Médiateur.
        Supprime les critères rejetés, ajoute les critères imposés.
        """
        rejected_ids = {c.id for c in evaluation["rejected"]}

        # Garder les critères non rejetés
        refined = [
            c for c in proposed if c.id not in rejected_ids
        ]

        # Ajouter les critères imposés par le Médiateur
        refined.extend(evaluation["added"])

        # Combler les catégories manquantes avec des critères génériques
        for missing_cat in evaluation.get("missing", []):
            refined.append(ContractCriterion(
                description=f"Validation {missing_cat} pour la verticale {vertical}",
                test_method="api_call" if missing_cat == "security" else "journal_check",
                expected_result=f"Conforme aux exigences {missing_cat}",
                category=missing_cat,
                weight=0.7,
                required=True,
                source="reasoning",
            ))

        return refined

    def _force_agreement(
        self,
        proposed: list[ContractCriterion],
        evaluation: dict,
        vertical: str,
    ) -> list[ContractCriterion]:
        """Forcer l'accord en incluant tous les critères du Médiateur."""
        rejected_ids = {c.id for c in evaluation["rejected"]}
        criteria = [c for c in proposed if c.id not in rejected_ids]
        criteria.extend(evaluation["added"])
        return criteria

    @staticmethod
    def _criteria_overlap(a: ContractCriterion, b: ContractCriterion) -> bool:
        """Vérifier si deux critères couvrent le même terrain."""
        # Heuristique: même catégorie + mots-clés communs > 50%
        if a.category != b.category:
            return False
        words_a = set(a.description.lower().split())
        words_b = set(b.description.lower().split())
        if not words_a or not words_b:
            return False
        overlap = len(words_a & words_b) / min(len(words_a), len(words_b))
        return overlap > 0.5

    def get_contract(self, intention_id: str) -> Optional[Contract]:
        """Récupérer le contrat pour une intention."""
        path = self._persist_dir / f"{intention_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return Contract(**data)
        except Exception as e:
            logger.warning(f"Contract load error: {e}")
            return None

    def _persist(self, contract: Contract) -> None:
        """Persister le contrat en JSON."""
        path = self._persist_dir / f"{contract.intention_id}.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(contract.model_dump(mode="json"), ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        tmp.replace(path)


# Singleton
contract_negotiator = ContractNegotiator()
