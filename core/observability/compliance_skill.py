"""
Cortex Leman v5 — ComplianceSkill: Unité atomique de savoir métier

Inspiré de: Brian Scanlan (Intercom), "How Building with AI Can Double
the Throughput of Your Engineering Team"

> "We encapsulated knowledge and context in engineering captures, skills,
>  guidance, hooks to force these things. We spend a lot of time cajoling
>  Claude Code to work well."
> "Give agents problems, not tasks. Let the agent figure out what skills
>  to invoke."

Leçon Intercom: un "skill" = un package auto-contenu qui emballe:
- Les règles JsonLogic (quoi vérifier)
- Le rubric d'évaluation (comment juger)
- Les golden cases (comment tester)
- Le guide métier (comment raisonner)

Dans Cortex, un ComplianceSkill est l'unité invocable par l'agent.
Quand l'agent reçoit un problème (pas une tâche), il cherche le skill
pertinent et l'invoque. Le Médiateur valide la classification.

Architecture:
- ComplianceSkill = règles + rubric + golden cases + guide
- SkillRegistry = registre des skills par vertical
- L'agent décrit le problème → SkillRegistry.find_matching() → skill invoqué
"""
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

SKILLS_DIR = Path(__file__).parent.parent / "skills" / "compliance"


class SkillDomain(str, Enum):
    """Domaines de compétences réglementaires"""
    FISCAL = "fiscal"               # Droit fiscal FR-CH
    SOCIAL = "social"               # Droit du travail
    BANKING = "banking"             # Bancaire / LBA
    MEDICAL = "medical"             # Santé / Secret médical
    GDPR = "gdpr"                   # Protection des données
    AI_ACT = "ai_act"               # Règlement IA européen
    PROFESSIONAL_SECRET = "professional_secret"  # Secret professionnel (avocat)
    ANTI_MONEY_LAUNDERING = "aml"   # Anti-blanchiment
    CORPORATE = "corporate"         # Droit des sociétés
    EMPLOYMENT = "employment"       # Droit du travail (RH)
    DATA_RESIDENCY = "data_residency"  # Localisation des données


class SkillConfidence(str, Enum):
    """Niveau de confiance d'un skill"""
    HIGH = "high"           # Backtesté sur >100 cas, >95% pass rate
    MEDIUM = "medium"       # Backtesté sur >50 cas, >80% pass rate
    LOW = "low"             # Nouveau, peu testé
    EXPERIMENTAL = "experimental"  # En développement


@dataclass
class SkillGuide:
    """
    Guide métier encapsulé dans le skill.

    C'est le "savoir-faire" que l'agent doit appliquer.
    Inclut: steps, avertissements, références légales.
    """
    title: str = ""
    description: str = ""
    steps: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    legal_references: list[str] = field(default_factory=list)
    examples: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "steps": self.steps,
            "warnings": self.warnings,
            "legal_references": self.legal_references,
            "examples": self.examples,
        }


@dataclass
class ComplianceSkill:
    """
    Unité atomique de savoir métier Cortex Leman.

    Package auto-contenu:
    - Règles JsonLogic (quoi vérifier)
    - Rubric d'évaluation (comment juger)
    - Golden cases de test (comment tester)
    - Guide métier (comment raisonner)

    Invoqué par l'agent quand un problème correspond au domaine.
    """
    skill_id: str = ""
    name: str = ""
    vertical: str = ""
    domain: SkillDomain = SkillDomain.GDPR
    version: int = 1
    confidence: SkillConfidence = SkillConfidence.EXPERIMENTAL
    description: str = ""

    # Règles associées (IDs dans rules/)
    rule_ids: list[str] = field(default_factory=list)

    # Rubric d'évaluation (ID dans eval_router)
    rubric_id: str = ""

    # Golden cases (IDs dans golden_dataset)
    golden_case_ids: list[str] = field(default_factory=list)

    # Guide métier
    guide: Optional[SkillGuide] = None

    # Patterns de déclenchement (mots-clés qui matchent ce skill)
    trigger_patterns: list[str] = field(default_factory=list)

    # Méta
    created_at: str = ""
    updated_at: str = ""
    author: str = ""
    last_backtest_score: float = 0.0
    total_invocations: int = 0
    pass_rate: float = 0.0

    # Racines françaises pour le matching tolérant aux flexions
    # Mapping: forme fléchie → racine normalisée (sans accent, minuscule)
    _FR_NORMALIZE = str.maketrans(
        "àâäéèêëîïôöùûüç",
        "aaaeeeeiioouuuc",
    )

    @staticmethod
    def _normalize_fr(text: str) -> str:
        """Normaliser un texte français : minuscules, sans accents, sans pluriels courants."""
        t = text.lower().translate(ComplianceSkill._FR_NORMALIZE)
        # Pluriels courants
        import re
        t = re.sub(r'(?:eux|ales|ents|ifs|ives|iers|ieres|ees|ais|aises)$', '', t)
        return t

    @staticmethod
    def _stem_fr(word: str) -> str:
        """Racinisation française minimale (stemming)."""
        w = word.lower().translate(ComplianceSkill._FR_NORMALIZE)
        # Pluriels d'abord
        if w.endswith('aux') and len(w) > 4:
            w = w[:-2] + 'al'  # bancaux → banal
        if w.endswith('s') and not w.endswith('ous') and len(w) > 3:
            w = w[:-1]        # impots → impot
        # Suffixes français — seuil len > 3 pour garder les racines courtes
        for suffix in ('issement', 'ication', 'alement', 'ement',
                       'ation', 'sion', 'tion',
                       'iser', 'ifier', 'aliser',
                       'elle', 'ence', 'ance', 'ique',
                       'ment',
                       'ive', 'ale', 'el', 'al',
                       'ent', 'ant', 'if',
                       'ee', 'er', 'ir'):
            if len(w) > 3 + len(suffix) and w.endswith(suffix):
                w = w[:-len(suffix)]
                break
        return w

    def matches_problem(self, problem: str) -> float:
        """
        Évaluer si ce skill correspond au problème décrit.

        Tolérant aux variations françaises :
        - Accents : "impôt" = "impot"
        - Pluriels : "impôts" = "impot"
        - Flexions : "déduire" ≈ "déduction"
        - Casse : "IMPÔT" = "impot"

        Returns:
            Score de pertinence (0.0 → 1.0)
        """
        if not problem or not problem.strip():
            return 0.0

        problem_norm = self._normalize_fr(problem)
        total_patterns = len(self.trigger_patterns)

        if total_patterns == 0:
            return 0.0

        matches = 0
        for pattern in self.trigger_patterns:
            pattern_norm = self._normalize_fr(pattern)

            # 1. Pattern exact (normalisé)
            if pattern_norm in problem_norm:
                matches += 1.0
                continue

            # 2. Mots du pattern stemmés dans le problème
            pattern_stems = [self._stem_fr(w) for w in pattern_norm.split() if len(w) > 2]
            problem_stems = [self._stem_fr(w) for w in problem_norm.split() if len(w) > 2]

            if pattern_stems and problem_stems:
                stem_matches = sum(
                    1 for ps in pattern_stems
                    if any(ps in pts or pts in ps for pts in problem_stems)
                )
                ratio = stem_matches / len(pattern_stems)
                if ratio >= 0.5:
                    matches += ratio

        return min(1.0, matches / total_patterns)

    def invoke(
        self,
        problem: str,
        context: dict = None,
        rules_engine=None,
        eval_router=None,
    ) -> dict:
        """
        Invoquer le skill sur un problème.

        1. Évaluer les règles JsonLogic
        2. Évaluer la sortie avec le rubric
        3. Retourner le résultat structuré

        Raises:
            EmptyInputError: si problem est vide

        Returns:
            dict structuré avec recommendation
        """
        if not problem or not problem.strip():
            from core.observability.errors import EmptyInputError
            raise EmptyInputError("problem")
        self.total_invocations += 1
        result = {
            "skill_id": self.skill_id,
            "name": self.name,
            "vertical": self.vertical,
            "domain": self.domain.value,
            "problem": problem[:200],
            "invoked_at": datetime.now(timezone.utc).isoformat(),
            "rules_results": [],
            "eval_results": [],
            "guide": self.guide.to_dict() if self.guide else None,
            "recommendation": "safe",
            "confidence": 0.5,
            "reasoning": "",
        }

        # 1. Évaluer les règles JsonLogic
        if rules_engine and self.rule_ids:
            all_results = rules_engine.evaluate(self.vertical, context or {})
            relevant = [r for r in all_results if r.rule_id in self.rule_ids or not self.rule_ids]
            result["rules_results"] = [
                {
                    "rule_id": r.rule_id,
                    "triggered": r.triggered,
                    "action": r.action,
                    "severity": r.severity,
                    "message": r.message,
                }
                for r in relevant
            ]

            # Si une règle critique est déclenchée → block/arbitrate
            triggered_critical = [
                r for r in relevant
                if r.triggered and r.action in ("block", "freeze")
            ]
            if triggered_critical:
                worst = max(triggered_critical, key=lambda r: {"critical": 4, "high": 3, "medium": 2}.get(r.severity, 1))
                result["recommendation"] = worst.action
                result["confidence"] = 0.9
                result["reasoning"] = f"Règle {worst.rule_id} ({worst.severity}): {worst.message}"

        # 2. Évaluer avec le rubric (si pas déjà bloqué)
        if eval_router and result["recommendation"] == "safe":
            eval_results = eval_router.evaluate(
                vertical=self.vertical,
                input_text=problem,
                output_text=str(context or ""),
            )
            result["eval_results"] = [
                {
                    "rubric_id": e.rubric_id,
                    "score": e.score,
                    "severity": e.severity.value,
                    "explanation": e.explanation,
                }
                for e in eval_results
            ]

            # Si un rubric échoue → caution
            failed = [e for e in eval_results if e.score < 0.5]
            if failed:
                result["recommendation"] = "caution"
                result["confidence"] = 0.6
                result["reasoning"] = f"Rubric {failed[0].rubric_id} en échec: {failed[0].explanation}"

        # 3. Ajouter le guide si pertinent
        if self.guide:
            result["guide"] = self.guide.to_dict()

        return result

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "vertical": self.vertical,
            "domain": self.domain.value,
            "version": self.version,
            "confidence": self.confidence.value,
            "description": self.description,
            "rule_ids": self.rule_ids,
            "rubric_id": self.rubric_id,
            "golden_case_ids": self.golden_case_ids,
            "trigger_patterns": self.trigger_patterns,
            "total_invocations": self.total_invocations,
            "pass_rate": self.pass_rate,
            "last_backtest_score": self.last_backtest_score,
        }


class SkillRegistry:
    """
    Registre des ComplianceSkills par vertical.

    L'agent décrit un problème → find_matching() retourne
    les skills pertinents triés par score.

    Usage:
        registry = SkillRegistry()
        registry.load_defaults()
        matches = registry.find_matching("Peut-on déduire 80K CHF sans justificatif ?")
    """

    def __init__(self):
        self._skills: dict[str, ComplianceSkill] = {}  # skill_id → skill
        self._by_vertical: dict[str, list[str]] = {}    # vertical → [skill_ids]
        self._by_domain: dict[str, list[str]] = {}      # domain → [skill_ids]

    def reset(self):
        """Réinitialiser pour les tests."""
        self._skills.clear()
        self._by_vertical.clear()
        self._by_domain.clear()

    def register(self, skill: ComplianceSkill) -> str:
        """Enregistrer un skill dans le registre"""
        if not skill.skill_id:
            skill.skill_id = uuid.uuid4().hex[:12]

        self._skills[skill.skill_id] = skill
        self._by_vertical.setdefault(skill.vertical, []).append(skill.skill_id)
        self._by_domain.setdefault(skill.domain.value, []).append(skill.skill_id)

        return skill.skill_id

    def find_matching(
        self,
        problem: str,
        vertical: str = None,
        domain: str = None,
        min_score: float = 0.1,
        limit: int = 5,
    ) -> list[tuple[ComplianceSkill, float]]:
        """
        Trouver les skills qui matchent un problème.

        Args:
            problem: Description du problème
            vertical: Filtrer par vertical (optionnel)
            domain: Filtrer par domaine (optionnel)
            min_score: Score minimum de pertinence
            limit: Nombre max de résultats

        Returns:
            Liste de (skill, score) triée par score descendant
        """
        candidates = list(self._skills.values())

        if vertical:
            candidates = [s for s in candidates if s.vertical == vertical]
        if domain:
            candidates = [s for s in candidates if s.domain.value == domain]

        scored = []
        for skill in candidates:
            score = skill.matches_problem(problem)
            if score >= min_score:
                scored.append((skill, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]

    def get_skill(self, skill_id: str) -> Optional[ComplianceSkill]:
        return self._skills.get(skill_id)

    def get_skills_by_vertical(self, vertical: str) -> list[ComplianceSkill]:
        ids = self._by_vertical.get(vertical, [])
        return [self._skills[i] for i in ids if i in self._skills]

    def get_skills_by_domain(self, domain: str) -> list[ComplianceSkill]:
        ids = self._by_domain.get(domain, [])
        return [self._skills[i] for i in ids if i in self._skills]

    def get_all_skills(self) -> list[ComplianceSkill]:
        return list(self._skills.values())

    def get_stats(self) -> dict:
        return {
            "total_skills": len(self._skills),
            "by_vertical": {v: len(ids) for v, ids in self._by_vertical.items()},
            "by_domain": {d: len(ids) for d, ids in self._by_domain.items()},
            "by_confidence": {
                c.value: sum(1 for s in self._skills.values() if s.confidence == c)
                for c in SkillConfidence
            },
        }


# === Skills par défaut (seed data) ===

DEFAULT_SKILLS = [
    ComplianceSkill(
        skill_id="comptable-fiscal-deduction",
        name="Vérification déduction fiscale",
        vertical="comptable",
        domain=SkillDomain.FISCAL,
        confidence=SkillConfidence.MEDIUM,
        description="Vérifie la conformité des déductions fiscales FR-CH",
        rule_ids=["comptable-001", "comptable-003", "comptable-006"],
        rubric_id="comptable-compliance-001",
        trigger_patterns=[
            "déduction fiscale", "déduire", "charge déductible",
            "optimisation fiscale", "réduction d'impôt",
            "frais professionnels", "amortissement",
        ],
        guide=SkillGuide(
            title="Guide déduction fiscale",
            description="Procédure de vérification des déductions fiscales",
            steps=[
                "1. Identifier le type de déduction (charge, investissement, don)",
                "2. Vérifier le montant contre les seuils légaux",
                "3. Vérifier la justification requise",
                "4. Confirmer l'éligibilité selon la juridiction (FR/CH)",
                "5. Si montant ≥ 10K€ → validation humaine obligatoire",
                "6. Si montant ≥ 50K CHF → gel préventif + arbitrage",
            ],
            warnings=[
                "⚠️ Art. 22 RGPD: Pas de décision fiscale entièrement automatisée",
                "⚠️ Seuil anti-blanchiment: 10K€ pour les opérations en espèces",
                "⚠️ Les seuils FR et CH diffèrent — vérifier la juridiction applicable",
            ],
            legal_references=[
                "Art. 22 RGPD (décisions automatisées)",
                "Art. 238 CGI (charges déductibles)",
                "LIFD (Loi fédérale sur l'impôt fédéral direct)",
                "OAR-FINMA (ordonnance sur le blanchiment)",
            ],
        ),
    ),
    ComplianceSkill(
        skill_id="avocat-secret-pro",
        name="Protection secret professionnel",
        vertical="avocat",
        domain=SkillDomain.PROFESSIONAL_SECRET,
        confidence=SkillConfidence.HIGH,
        description="Vérifie qu'aucune information couverte par le secret professionnel n'est divulguée",
        rule_ids=["avocat-001", "avocat-002", "avocat-004"],
        rubric_id="avocat-compliance-001",
        trigger_patterns=[
            "dossier client", "secret professionnel", "Art. 321 CP",
            "confidentiel", "privilege", "avocat-client",
            "correspondance", "consultation juridique",
            "résumé de dossier", "details du cas",
        ],
        guide=SkillGuide(
            title="Guide secret professionnel",
            description="Protection absolue du secret professionnel avocat",
            steps=[
                "1. Identifier si la requête concerne un dossier client spécifique",
                "2. Si oui → BLOCAGE IMMÉDIAT, aucun détail du dossier",
                "3. Vérifier que le LLM utilisé est local (pas d'externe)",
                "4. Vérifier que l'infrastructure est en Suisse",
                "5. Pour la rédaction de conclusions → arbitrage obligatoire",
            ],
            warnings=[
                "🚨 Art. 321 CP: Secret professionnel ABSOLU",
                "🚨 LPM: Infrastructure doit être en Suisse",
                "🚨 Aucun LLM externe pour les dossiers clients",
            ],
            legal_references=[
                "Art. 321 Code pénal français",
                "Art. 321 StGB suisse",
                "Loi sur la protection des données (LPD)",
                "LPM (Loi sur le mariage par procuration)",
            ],
        ),
    ),
    ComplianceSkill(
        skill_id="banque-aml",
        name="Contrôle anti-blanchiment KYC",
        vertical="banque",
        domain=SkillDomain.ANTI_MONEY_LAUNDERING,
        confidence=SkillConfidence.MEDIUM,
        description="Vérifie la conformité aux obligations LBA/AMLC",
        rule_ids=["comptable-003"],
        trigger_patterns=[
            "KYC", "blanchiment", "anti-blanchiment", "LBA", "AMLC",
            "virement", "transfert", "espèces", "seuil de déclaration",
            "source de fonds", "provenance des fonds",
            "structuration", "smurfing", "contournement seuil",
        ],
        guide=SkillGuide(
            title="Guide anti-blanchiment",
            steps=[
                "1. Vérifier si la transaction approche un seuil déclaratif",
                "2. Identifier les patterns de structuration (fractionnement)",
                "3. Vérifier la source des fonds",
                "4. Signaler toute suspicion à l'officer de compliance",
                "5. Ne JAMAIS conseiller de contourner les seuils",
            ],
            warnings=[
                "🚨 LBA: Obligation de déclaration des soupçons",
                "🚨 AMLC: Seuil de 15K CHF pour les espèces",
                "🚨 Le fractionnement est un délit",
            ],
            legal_references=[
                "LBA (Loi sur le blanchiment d'argent)",
                "AMLC (Anti-Money Laundering Control)",
                "GAFI/FATF Recommendations",
            ],
        ),
    ),
    ComplianceSkill(
        skill_id="sante-secret-medical",
        name="Protection données de santé",
        vertical="sante",
        domain=SkillDomain.MEDICAL,
        confidence=SkillConfidence.MEDIUM,
        description="Vérifie le respect du secret médical et des données de santé",
        trigger_patterns=[
            "patient", "dossier médical", "données de santé", "DMP",
            "diagnostic", "traitement", "prescription", "secret médical",
            "consentement", "CNIL", "CPP",
        ],
        guide=SkillGuide(
            title="Guide données de santé",
            steps=[
                "1. Identifier si la requête concerne des données de santé",
                "2. Vérifier le consentement du patient",
                "3. Ne jamais poser de diagnostic définitif",
                "4. Ne jamais divulguer de données patient identifiantes",
                "5. Signaler les obligations DMP",
            ],
            warnings=[
                "🚨 Art. 226-13 CP: Secret médical",
                "🚨 RGPD Art. 9: Données sensibles",
                "🚨 Pas de diagnostic automatisé",
            ],
        ),
    ),
    ComplianceSkill(
        skill_id="rh-discrimination",
        name="Anti-discrimination RH",
        vertical="rh",
        domain=SkillDomain.EMPLOYMENT,
        confidence=SkillConfidence.MEDIUM,
        description="Détecte les discriminations à l'embauche et dans le travail",
        trigger_patterns=[
            "recrutement", "embauche", "candidature", "CV", "sélection",
            "licenciement", "congédier", "âge", "genre", "origine",
            "discrimination", "égalité", "diversité",
        ],
        guide=SkillGuide(
            title="Guide anti-discrimination RH",
            steps=[
                "1. Identifier les critères de sélection mentionnés",
                "2. Vérifier qu'aucun critère discriminatoire n'est utilisé",
                "3. Vérifier le respect des procédures de licenciement",
                "4. Protéger les données personnelles des employés",
            ],
            warnings=[
                "🚨 Code du travail: Interdiction de discriminer",
                "🚨 Critères protégés: âge, genre, origine, religion, handicap",
                "🚨 RGPD: Données personnelles des employés",
            ],
        ),
    ),
    ComplianceSkill(
        skill_id="startup-ai-act",
        name="Conformité AI Act",
        vertical="startup",
        domain=SkillDomain.AI_ACT,
        confidence=SkillConfidence.MEDIUM,
        description="Vérifie la conformité au règlement IA européen",
        trigger_patterns=[
            "AI Act", "règlement IA", "risque IA", "système d'IA",
            "transparence", "high risk", "chatbot", "scoring",
            "classification automatique", "biais algorithmique",
        ],
        guide=SkillGuide(
            title="Guide AI Act",
            steps=[
                "1. Classifier le système IA selon les catégories de risque",
                "2. Identifier les obligations applicables",
                "3. Vérifier la documentation technique requise",
                "4. Vérifier les obligations de transparence",
                "5. Vérifier la surveillance humaine requise",
            ],
            warnings=[
                "🚨 AI Act Art. 6: Systèmes high-risk (emploi, crédit, etc.)",
                "🚨 AI Act Art. 52: Obligations de transparence",
                "🚨 Ne pas minimiser les risques pour faciliter la classification",
            ],
        ),
    ),
]


# === Singleton ===

skill_registry = SkillRegistry()


def seed_skills(registry: SkillRegistry = skill_registry) -> int:
    """Seeder le registre avec les skills par défaut"""
    count = 0
    for skill in DEFAULT_SKILLS:
        registry.register(skill)
        count += 1
    return count
