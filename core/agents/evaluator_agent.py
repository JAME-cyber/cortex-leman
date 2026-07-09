"""
Cortex Leman v5 — Agent Évaluateur (Pattern Generator-Evaluator Anthropic)

Agent séparé avec context window fraîche et system prompt dur.
Teste visuellement et fonctionnellement les features déployées par l'Agent Action.

Inspiré de: Ash & Andrew (Anthropic Applied AI, AI Engineer 2026)
Adapté pour: Cortex Leman avec Médiateur déterministe (pas besoin du full GAN pattern)

Différences vs Anthropic:
- Notre Évaluateur ne corrige JAMAIS — il critique et renvoie au cycle
- Le Médiateur JsonLogic reste le ground truth déterministe
- L'Évaluateur est un complément probabiliste, pas un remplacement
- Les rubriques sont codées en dur dans le skill, pas négociées dynamiquement
  (la negotiation se fait via le contract negotiation séparé)

Pipeline:
  Agent Action → déploiement → Agent Évaluateur → critique →
    si FAIL → renvoie au Reasoning (nouveau cycle)
    si PASS → Handoff JSON → complétion
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from core.agents.base_agent import BaseAgent
from core.bus.subjects import subjects
from core.bus.nats_client import bus
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)


# ── Modèles Pydantic ──────────────────────────────────────────

class EvaluationCriterion(BaseModel):
    """Un critère d'évaluation unique"""
    criterion_id: str
    category: str  # "functional" | "design" | "security" | "compliance" | "ux"
    description: str
    weight: float = 1.0  # 0.0-1.0
    required: bool = True  # Si True, un FAIL bloque la validation


class EvaluationResult(BaseModel):
    """Résultat d'un critère évalué"""
    criterion_id: str
    passed: bool
    score: float  # 0.0-1.0
    evidence: str = ""  # Ce que l'évaluateur a observé
    critique: str = ""  # Pourquoi ça échoue


class EvaluationReport(BaseModel):
    """Rapport complet d'évaluation"""
    report_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    intention_id: str
    vertical: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Scores
    overall_score: float = 0.0  # Moyenne pondérée
    functional_score: float = 0.0
    design_score: float = 0.0
    security_score: float = 0.0
    compliance_score: float = 0.0
    ux_score: float = 0.0

    # Résultats détaillés
    criteria_results: list[EvaluationResult] = Field(default_factory=list)

    # Verdict
    verdict: str = "pending"  # "pass" | "fail" | "partial"
    blocking_issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    # Méta
    evaluator_context_fresh: bool = True  # Toujours True — context window fraîche
    screenshots_taken: int = 0
    pages_tested: int = 0
    interactions_performed: int = 0

    model_config = {"arbitrary_types_allowed": True}


# ── Rubriques par verticale ───────────────────────────────────

DEFAULT_RUBRIC = [
    EvaluationCriterion(
        criterion_id="func-001",
        category="functional",
        description="La feature principale répond à l'intention utilisateur",
        weight=1.0,
        required=True,
    ),
    EvaluationCriterion(
        criterion_id="func-002",
        category="functional",
        description="Les endpoints API retournent des réponses valides (status 2xx)",
        weight=0.8,
        required=True,
    ),
    EvaluationCriterion(
        criterion_id="func-003",
        category="functional",
        description="Les données affichées correspondent aux données en base",
        weight=0.7,
        required=False,
    ),
    EvaluationCriterion(
        criterion_id="sec-001",
        category="security",
        description="Aucune donnée sensible exposée dans les réponses API",
        weight=1.0,
        required=True,
    ),
    EvaluationCriterion(
        criterion_id="sec-002",
        category="security",
        description="L'authentification est requise pour les endpoints protégés",
        weight=0.9,
        required=True,
    ),
    EvaluationCriterion(
        criterion_id="comp-001",
        category="compliance",
        description="Les données restent dans la juridiction requise (CH/EU)",
        weight=1.0,
        required=True,
    ),
    EvaluationCriterion(
        criterion_id="comp-002",
        category="compliance",
        description="Le journal WORM enregistre l'action",
        weight=0.8,
        required=False,
    ),
    EvaluationCriterion(
        criterion_id="ux-001",
        category="ux",
        description="L'interface est navigable sans erreur JavaScript bloquante",
        weight=0.7,
        required=False,
    ),
    EvaluationCriterion(
        criterion_id="ux-002",
        category="ux",
        description="Les messages d'erreur sont clairs et non techniques",
        weight=0.5,
        required=False,
    ),
    EvaluationCriterion(
        criterion_id="design-001",
        category="design",
        description="Pas de 'purple gradient AI slop' — design cohérent avec la verticale",
        weight=0.6,
        required=False,
    ),
]

# Critères supplémentaires par verticale sensible
VERTICAL_RUBRICS: dict[str, list[EvaluationCriterion]] = {
    "avocat": [
        EvaluationCriterion(
            criterion_id="avocat-001",
            category="compliance",
            description="Secret professionnel Art. 321 CP — aucune fuite de données client",
            weight=1.0,
            required=True,
        ),
        EvaluationCriterion(
            criterion_id="avocat-002",
            category="compliance",
            description="Aucune donnée n'est envoyée à un modèle externe sans anonymisation",
            weight=1.0,
            required=True,
        ),
    ],
    "sante": [
        EvaluationCriterion(
            criterion_id="sante-001",
            category="compliance",
            description="Données patient hébergées sur infrastructure certifiée HDS",
            weight=1.0,
            required=True,
        ),
        EvaluationCriterion(
            criterion_id="sante-002",
            category="compliance",
            description="Aucun diagnostic médical direct — toujours avec réserve",
            weight=1.0,
            required=True,
        ),
    ],
    "banque": [
        EvaluationCriterion(
            criterion_id="banque-001",
            category="compliance",
            description="Seuil KYC 15K CHF respecté — gel automatique au-dessus",
            weight=1.0,
            required=True,
        ),
        EvaluationCriterion(
            criterion_id="banque-002",
            category="security",
            description="Art. 47 LB — secret bancaire préservé dans tous les outputs",
            weight=1.0,
            required=True,
        ),
    ],
}


class EvaluatorAgent(BaseAgent):
    """
    Agent Évaluateur — Context window fraîche, system prompt dur.

    Rôle: tester ce que l'Agent Action a construit.
    Ne corrige JAMAIS — critique et renvoie.

    Modes:
    1. API test: vérifie les endpoints via HTTP
    2. Visual test: Playwright screenshots + navigation (si base_url fourni)
    3. LLM critique: évaluation subjective via LLM (design, UX)
    """

    # System prompt dur — l'évaluateur doit être exigeant
    HARSH_SYSTEM_PROMPT = """Tu es un évaluateur QA extrêmement exigeant.
Tu ne valides JAMAIS au premier passage.
Tu cherches activement les bugs, les failles de sécurité, et les violations de conformité.
Tu préfères signaler un faux positif plutôt que de laisser passer un vrai problème.

Règles absolues:
- Si un critère required échoue → verdict = FAIL, sans exception
- Si un endpoint retourne une erreur → FAIL
- Si des données sensibles sont exposées → FAIL immédiat
- Si le journal WORM n'a pas enregistré l'action → FAIL
- Tu ne donnes PAS de suggestions de correction — tu signales uniquement les problèmes
- Tu ne sommes PAS d'accord avec le générateur par défaut — tu es ADVERSARIAL
"""

    def __init__(self):
        super().__init__(
            name="evaluator",
            subscribe_subjects=[
                subjects.AGENT_RESULT,  # Intercepter les résultats de l'Action
                "cleman.evaluator.run",  # Demande explicite d'évaluation
            ],
        )

    async def process(self, data: dict, meta: dict) -> dict:
        intention_id = data.get("intention_id", "unknown")
        client_id = data.get("client_id", "unknown")
        vertical = data.get("vertical", "unknown")
        agent_source = data.get("agent_source")

        # On n'évalue que les résultats de l'Agent Action ou les demandes explicites
        if agent_source and agent_source != "action":
            return None

        logger.info(
            f"Agent Évaluateur: évaluation de {intention_id[:8]}... "
            f"(vertical={vertical})"
        )

        # Récupérer le contrat de validation (si contract negotiation a produit un)
        contract = await self._load_contract(intention_id)

        # Charger la rubrique
        rubric = self._get_rubric(vertical, contract)

        # Phase 1: Tests programmatiques (API endpoints)
        api_results = await self._test_api(intention_id, data, rubric)

        # Phase 2: Tests visuels (Playwright si base_url disponible)
        visual_results = await self._test_visual(intention_id, data, rubric)

        # Phase 3: Critique LLM (design, UX, edge cases)
        llm_results = await self._test_llm(intention_id, data, rubric)

        # Combiner tous les résultats
        all_results = api_results + visual_results + llm_results

        # Calculer les scores
        report = self._build_report(
            intention_id=intention_id,
            vertical=vertical,
            rubric=rubric,
            results=all_results,
            api_count=len(api_results),
            visual_count=len(visual_results),
        )

        # Journaliser
        journal.append(
            event_type=JournalEventType.COMPLIANCE_CHECK,
            client_id=client_id,
            vertical=vertical,
            agent_source="evaluator",
            intention_id=intention_id,
            payload={
                "report_id": report.report_id,
                "verdict": report.verdict,
                "overall_score": report.overall_score,
                "blocking_issues": report.blocking_issues,
                "criteria_evaluated": len(all_results),
                "criteria_passed": sum(1 for r in all_results if r.passed),
            },
        )

        # Si FAIL, renvoyer au cycle Reasoning (pas corriger directement)
        if report.verdict == "fail":
            await self._send_back_to_reasoning(intention_id, client_id, vertical, report)

        return {
            "recommendation": "evaluated",
            "confidence": report.overall_score,
            "evaluation_report": report.model_dump(),
            "verdict": report.verdict,
            "blocking_issues": report.blocking_issues,
        }

    def _get_rubric(
        self,
        vertical: str,
        contract: Optional[dict] = None,
    ) -> list[EvaluationCriterion]:
        """Construire la rubrique complète: défaut + verticale + contrat."""
        rubric = list(DEFAULT_RUBRIC)

        # Ajouter les critères spécifiques à la verticale
        if vertical in VERTICAL_RUBRICS:
            rubric.extend(VERTICAL_RUBRICS[vertical])

        # Ajouter les critères du contract negotiation (s'ils existent)
        if contract and contract.get("criteria"):
            for c in contract["criteria"]:
                rubric.append(EvaluationCriterion(
                    criterion_id=c.get("id", f"contract-{uuid.uuid4().hex[:6]}"),
                    category=c.get("category", "functional"),
                    description=c["description"],
                    weight=c.get("weight", 0.8),
                    required=c.get("required", True),
                ))

        return rubric

    async def _load_contract(self, intention_id: str) -> Optional[dict]:
        """Charger le contrat produit par le contract negotiation."""
        from pathlib import Path
        contract_path = Path(f"data/contracts/{intention_id}.json")
        if contract_path.exists():
            return json.loads(contract_path.read_text(encoding="utf-8"))
        return None

    async def _test_api(
        self,
        intention_id: str,
        data: dict,
        rubric: list[EvaluationCriterion],
    ) -> list[EvaluationResult]:
        """
        Tests programmatiques des endpoints API.
        Vérifie: status codes, structure des réponses, données sensibles.
        """
        results = []
        result = data.get("result", {})
        saga_status = result.get("saga_status", {})

        # Critère func-002: endpoints API valides
        steps = saga_status.get("steps", []) if isinstance(saga_status, dict) else []
        for step in steps:
            step_result = step.get("result", {}) if isinstance(step, dict) else {}
            status = step_result.get("status", "unknown") if isinstance(step_result, dict) else "unknown"

            if status == "error":
                results.append(EvaluationResult(
                    criterion_id="func-002",
                    passed=False,
                    score=0.0,
                    evidence=f"Step '{step.get('name', '?')}' returned error: {step_result}",
                    critique="Un step de la saga a échoué — l'action n'est pas complète",
                ))
            elif status in ("processed", "sent", "triggered", "recorded", "generated"):
                results.append(EvaluationResult(
                    criterion_id="func-002",
                    passed=True,
                    score=1.0,
                    evidence=f"Step '{step.get('name', '?')}' status: {status}",
                ))

        # Critère sec-001: pas de données sensibles dans le résultat
        result_str = json.dumps(result, ensure_ascii=False)
        sensitive_patterns = [
            "password", "secret", "token", "api_key",
            "credit_card", "iban", "ssn", "numéro_sécurité_sociale",
        ]
        leaked = [p for p in sensitive_patterns if p in result_str.lower()]
        if leaked:
            results.append(EvaluationResult(
                criterion_id="sec-001",
                passed=False,
                score=0.0,
                evidence=f"Patterns sensibles détectés: {leaked}",
                critique="Données potentiellement sensibles exposées dans la réponse API",
            ))
        else:
            results.append(EvaluationResult(
                criterion_id="sec-001",
                passed=True,
                score=1.0,
                evidence="Aucun pattern sensible détecté dans la réponse",
            ))

        # Critère comp-002: journal WORM
        from core.journal.append_only_journal import journal
        recent = journal.query(intention_id=intention_id, limit=5)
        if recent:
            results.append(EvaluationResult(
                criterion_id="comp-002",
                passed=True,
                score=1.0,
                evidence=f"Journal WORM: {len(recent)} entrées pour cette intention",
            ))
        else:
            results.append(EvaluationResult(
                criterion_id="comp-002",
                passed=False,
                score=0.3,
                evidence="Aucune entrée WORM trouvée pour cette intention",
                critique="L'action n'a pas été journalisée — traçabilité absente",
            ))

        return results

    async def _test_visual(
        self,
        intention_id: str,
        data: dict,
        rubric: list[EvaluationCriterion],
    ) -> list[EvaluationResult]:
        """
        Tests visuels via Playwright (si disponible).
        Prend des screenshots, navigue, vérifie l'UI.
        """
        results = []
        base_url = data.get("context", {}).get("base_url") or data.get("result", {}).get("url")

        if not base_url:
            # Pas d'URL → on ne peut pas tester visuellement
            # Ce n'est pas un FAIL — c'est un skip
            return results

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Naviguer vers l'app
                response = await page.goto(base_url, wait_until="networkidle", timeout=15000)

                if not response:
                    results.append(EvaluationResult(
                        criterion_id="func-001",
                        passed=False,
                        score=0.0,
                        evidence=f"Impossible de charger {base_url}",
                        critique="L'application ne répond pas",
                    ))
                    await browser.close()
                    return results

                # Critère ux-001: pas d'erreurs JS bloquantes
                js_errors = []
                page.on("pageerror", lambda err: js_errors.append(str(err)))
                await page.wait_for_timeout(2000)  # Attendre les erreurs

                if js_errors:
                    results.append(EvaluationResult(
                        criterion_id="ux-001",
                        passed=False,
                        score=0.3,
                        evidence=f"Erreurs JS: {js_errors[:3]}",
                        critique="Erreurs JavaScript détectées pendant le chargement",
                    ))
                else:
                    results.append(EvaluationResult(
                        criterion_id="ux-001",
                        passed=True,
                        score=1.0,
                        evidence="Aucune erreur JS détectée après 2s",
                    ))

                # Screenshot pour audit
                screenshot_path = f"data/screenshots/{intention_id[:8]}-eval.png"
                from pathlib import Path
                Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=screenshot_path, full_page=True)

                # Vérifier que la page n'est pas vide
                content = await page.content()
                if len(content) < 100:
                    results.append(EvaluationResult(
                        criterion_id="func-001",
                        passed=False,
                        score=0.1,
                        evidence=f"Page quasi-vide: {len(content)} chars",
                        critique="La page rendue est vide ou quasi-vide",
                    ))

                await browser.close()

        except ImportError:
            logger.debug("Playwright non installé — tests visuels ignorés")
        except Exception as e:
            logger.warning(f"Test visuel échoué: {e}")
            results.append(EvaluationResult(
                criterion_id="ux-001",
                passed=False,
                score=0.0,
                evidence=f"Erreur Playwright: {str(e)[:200]}",
                critique="Impossible de tester visuellement — vérifier manuellement",
            ))

        return results

    async def _test_llm(
        self,
        intention_id: str,
        data: dict,
        rubric: list[EvaluationCriterion],
    ) -> list[EvaluationResult]:
        """
        Critique LLM pour les critères subjectifs (design, UX).
        Utilise le HARSH_SYSTEM_PROMPT — le modèle est forcé d'être critique.
        """
        results = []
        result = data.get("result", {})
        vertical = data.get("vertical", "unknown")

        # Les critères subjectifs qui nécessitent un LLM
        subjective_criteria = [
            c for c in rubric
            if c.category in ("design", "ux") and c.criterion_id.startswith(("design-", "ux-"))
        ]

        if not subjective_criteria:
            return results

        try:
            from core.integrations.llm import llm_service

            # Construire le prompt de critique
            criteria_text = "\n".join(
                f"- [{c.criterion_id}] {c.description} (poids: {c.weight})"
                for c in subjective_criteria
            )

            task = f"""{self.HARSH_SYSTEM_PROMPT}

Évalue le résultat suivant contre ces critères subjectifs:

CRITÈRES:
{criteria_text}

RÉSULTAT À ÉVALUER (vertical: {vertical}):
{json.dumps(result, ensure_ascii=False, indent=2)[:3000]}

Pour chaque critère, donne:
- passed: true/false
- score: 0.0-1.0
- evidence: ce que tu as observé
- critique: pourquoi ça échoue (si applicable)

FORMAT JSON:
{{
    "evaluations": [
        {{
            "criterion_id": "...",
            "passed": true/false,
            "score": 0.0-1.0,
            "evidence": "...",
            "critique": "..."
        }}
    ]
}}"""

            llm_result = await llm_service.generate_for_agent(
                agent_name="evaluator",
                task=task,
                context=result,
                vertical=vertical,
                client_id="system",
                intention_id=intention_id,
                use_rag=False,
            )

            if llm_result.get("text"):
                parsed = self._parse_llm_eval(llm_result["text"])
                for ev in parsed.get("evaluations", []):
                    results.append(EvaluationResult(
                        criterion_id=ev.get("criterion_id", "unknown"),
                        passed=ev.get("passed", False),
                        score=ev.get("score", 0.0),
                        evidence=ev.get("evidence", ""),
                        critique=ev.get("critique", ""),
                    ))

        except Exception as e:
            logger.warning(f"Critique LLM échouée: {e} — mode dégradé")

        return results

    def _parse_llm_eval(self, text: str) -> dict:
        """Parser la réponse LLM en JSON."""
        import re
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            brace_match = re.search(r'\{[\s\S]*\}', text)
            if brace_match:
                try:
                    return json.loads(brace_match.group(0))
                except json.JSONDecodeError:
                    pass
            return {"evaluations": []}

    def _build_report(
        self,
        intention_id: str,
        vertical: str,
        rubric: list[EvaluationCriterion],
        results: list[EvaluationResult],
        api_count: int = 0,
        visual_count: int = 0,
    ) -> EvaluationReport:
        """Construire le rapport d'évaluation à partir des résultats."""

        # Map criterion_id → criterion pour les poids
        criterion_map = {c.criterion_id: c for c in rubric}

        # Calculer les scores par catégorie
        category_scores: dict[str, list[tuple[float, float]]] = {}
        blocking_issues: list[str] = []
        recommendations: list[str] = []

        for r in results:
            criterion = criterion_map.get(r.criterion_id)
            cat = criterion.category if criterion else "functional"
            weight = criterion.weight if criterion else 0.5
            required = criterion.required if criterion else True

            category_scores.setdefault(cat, []).append((r.score, weight))

            if not r.passed and required:
                blocking_issues.append(f"[{r.criterion_id}] {r.critique}")

            if not r.passed and r.critique:
                recommendations.append(r.critique)

        # Score global (moyenne pondérée)
        all_weighted = []
        for scores_weights in category_scores.values():
            for score, weight in scores_weights:
                all_weighted.append((score, weight))

        overall = (
            sum(s * w for s, w in all_weighted) / sum(w for _, w in all_weighted)
            if all_weighted else 0.0
        )

        # Scores par catégorie
        cat_scores = {}
        for cat, sw_list in category_scores.items():
            total_w = sum(w for _, w in sw_list)
            cat_scores[cat] = (
                sum(s * w for s, w in sw_list) / total_w if total_w > 0 else 0.0
            )

        # Verdict
        if blocking_issues:
            verdict = "fail"
        elif overall >= 0.7:
            verdict = "pass"
        else:
            verdict = "partial"

        return EvaluationReport(
            intention_id=intention_id,
            vertical=vertical,
            overall_score=round(overall, 3),
            functional_score=round(cat_scores.get("functional", 0.0), 3),
            design_score=round(cat_scores.get("design", 0.0), 3),
            security_score=round(cat_scores.get("security", 0.0), 3),
            compliance_score=round(cat_scores.get("compliance", 0.0), 3),
            ux_score=round(cat_scores.get("ux", 0.0), 3),
            criteria_results=results,
            verdict=verdict,
            blocking_issues=blocking_issues,
            recommendations=recommendations,
            screenshots_taken=visual_count,
            pages_tested=1 if visual_count > 0 else 0,
            interactions_performed=0,
        )

    async def _send_back_to_reasoning(
        self,
        intention_id: str,
        client_id: str,
        vertical: str,
        report: EvaluationReport,
    ) -> None:
        """
        Renvoyer le rapport d'évaluation au cycle Reasoning.
        L'Agent Action ne corrige pas — c'est un nouveau cycle.
        """
        await bus.publish(subjects.REASONING_ANALYZE, {
            "intention_id": intention_id,
            "client_id": client_id,
            "vertical": vertical,
            "query": f"Corriger les issues de l'évaluation: {report.blocking_issues}",
            "context": {
                "evaluation_report": report.model_dump(),
                "source": "evaluator",
                "verdict": report.verdict,
                "blocking_issues": report.blocking_issues,
                "recommendations": report.recommendations,
            },
        })

        logger.info(
            f"Évaluateur: rapport FAIL renvoyé au Reasoning pour "
            f"{intention_id[:8]}... ({len(report.blocking_issues)} issues)"
        )
