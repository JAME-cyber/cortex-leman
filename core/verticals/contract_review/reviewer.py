"""
Moteur de revue assistée de contrats.

Chaîne de traitement :
1. extraction de structure et de clauses ;
2. détection assistée par LLM via l'interface abstraite du projet ;
3. croisement déterministe JsonLogic ;
4. scoring de risque ;
5. préparation des points d'arbitrage humain.

Le moteur ne rend jamais de décision juridique finale.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping

try:  # Référence obligatoire à l'interface abstraite du projet, sans provider concret.
    from core.integrations.llm.provider import LLMProvider  # type: ignore
except Exception:  # pragma: no cover - le projet cible fournit normalement ce module.
    LLMProvider = Any  # type: ignore

from .models import (
    ContractDocument,
    ContractIssue,
    ContractSection,
    IssueCategory,
    IssueLocation,
    IssueSeverity,
    IssueSource,
    ReviewResult,
    RiskLevel,
)


RULES_PATH = Path(__file__).with_name("rules.json")
PROMPTS_PATH = Path(__file__).with_name("prompts.yaml")
MAX_LLM_CHARS = 60_000

_EU_COUNTRY_CODES: frozenset[str] = frozenset(
    {
        "AT",
        "BE",
        "BG",
        "HR",
        "CY",
        "CZ",
        "DK",
        "EE",
        "FI",
        "FR",
        "DE",
        "GR",
        "HU",
        "IE",
        "IT",
        "LV",
        "LT",
        "LU",
        "MT",
        "NL",
        "PL",
        "PT",
        "RO",
        "SK",
        "SI",
        "ES",
        "SE",
    }
)

_COUNTRY_ALIASES: dict[str, str] = {
    "suisse": "CH",
    "switzerland": "CH",
    "schweiz": "CH",
    "ch": "CH",
    "france": "FR",
    "francais": "FR",
    "francaise": "FR",
    "french": "FR",
    "allemagne": "DE",
    "allemand": "DE",
    "germany": "DE",
    "italie": "IT",
    "italien": "IT",
    "italy": "IT",
    "espagne": "ES",
    "spain": "ES",
    "luxembourg": "LU",
    "belgique": "BE",
    "belgium": "BE",
    "pays-bas": "NL",
    "netherlands": "NL",
    "angleterre": "GB",
    "anglais": "GB",
    "royaume uni": "GB",
    "royaume-uni": "GB",
    "united kingdom": "GB",
    "uk": "GB",
    "new york": "US-NY",
    "delaware": "US-DE",
    "californie": "US-CA",
    "california": "US-CA",
    "etats-unis": "US",
    "etats unis": "US",
    "united states": "US",
    "usa": "US",
    "singapour": "SG",
    "singapore": "SG",
    "chine": "CN",
    "china": "CN",
    "hong kong": "HK",
    "dubai": "AE",
    "emirats": "AE",
}

_LEGAL_BASIS_BY_RULE: dict[str, list[str]] = {
    "contract-review-001": [
        "Principe de proportionnalité des restrictions post-contractuelles",
        "Validation obligatoire par avocat selon droit applicable",
    ],
    "contract-review-002": [
        "Exigence usuelle de limitation territoriale d'une non-concurrence",
        "Contrôle de proportionnalité contractuelle",
    ],
    "contract-review-003": [
        "Risque de droit applicable hors UE/CH",
        "Contrôle conflictuel international privé",
    ],
    "contract-review-004": [
        "Risque de compétence juridictionnelle exclusive défavorable",
        "Contrôle d'accès effectif au juge",
    ],
    "contract-review-005": [
        "Contrôle de proportionnalité des clauses pénales",
        "Pouvoir modérateur du juge selon droit applicable",
    ],
    "contract-review-006": [
        "Principe d'équilibre contractuel",
        "Contrôle des engagements essentiels et de la résiliation",
    ],
    "contract-review-007": [
        "Interdiction des modifications unilatérales déséquilibrées sans garde-fou",
        "Exigence de prévisibilité contractuelle",
    ],
    "contract-review-008": [
        "Contrôle des clauses limitatives ou extensives de responsabilité",
        "Équilibre et réciprocité des obligations",
    ],
    "contract-review-009": [
        "RGPD art. 28 et obligations de sous-traitance",
        "LPD suisse et gouvernance des données personnelles",
    ],
    "contract-review-010": [
        "Contrôle des renouvellements automatiques et préavis excessifs",
        "Exigence de lisibilité des engagements de durée",
    ],
    "contract-review-011": [
        "Contrôle de proportionnalité des obligations de confidentialité",
        "Secret d'affaires et durée raisonnable selon contexte",
    ],
    "contract-review-012": [
        "Contrôle des cessions de droits de propriété intellectuelle",
        "Nécessité d'une assiette, d'une durée, d'un territoire et d'une contrepartie déterminables",
    ],
}

_CATEGORY_BY_RULE: dict[str, IssueCategory] = {
    "contract-review-001": IssueCategory.NON_COMPETE_RISK,
    "contract-review-002": IssueCategory.NON_COMPETE_RISK,
    "contract-review-003": IssueCategory.GOVERNING_LAW_RISK,
    "contract-review-004": IssueCategory.JURISDICTION_RISK,
    "contract-review-005": IssueCategory.PENALTY_RISK,
    "contract-review-006": IssueCategory.TERMINATION_RISK,
    "contract-review-007": IssueCategory.IMBALANCE,
    "contract-review-008": IssueCategory.LIABILITY_RISK,
    "contract-review-009": IssueCategory.DATA_PROTECTION_RISK,
    "contract-review-010": IssueCategory.TERMINATION_RISK,
    "contract-review-011": IssueCategory.IMBALANCE,
    "contract-review-012": IssueCategory.IP_RISK,
}

_DEFAULT_PROMPTS: dict[str, Any] = {
    "system": {
        "content": (
            "Tu es Juriste-Analyste Contractuel Lémanique. Tu assistes un avocat dans une revue de contrat. "
            "Tu ne rends jamais de décision juridique finale. Tu identifies les risques, cites la localisation, "
            "explique le raisonnement et proposes des points à valider par l'avocat. "
            "Respect strict du secret professionnel art. 321 CP, RGPD et LPD."
        )
    }
}


@dataclass(frozen=True)
class ContractStructure:
    """Structure extraite d'un contrat pour revue et règles déterministes."""

    sections: tuple[ContractSection, ...]
    facts: dict[str, Any]


class JsonLogicEvaluator:
    """Évaluateur JsonLogic minimal, déterministe et auditable pour les règles du wedge."""

    def evaluate(self, expression: Any, data: Mapping[str, Any]) -> Any:
        """Évalue une expression JsonLogic sur un dictionnaire de données."""
        if isinstance(expression, list):
            return [self.evaluate(item, data) for item in expression]
        if not isinstance(expression, dict):
            return expression
        if len(expression) != 1:
            raise ValueError(f"Expression JsonLogic invalide: {expression!r}")

        operator, raw_args = next(iter(expression.items()))
        args = raw_args if isinstance(raw_args, list) else [raw_args]

        if operator == "var":
            return self._resolve_var(raw_args, data)
        if operator == "and":
            result: Any = None
            for arg in args:
                result = self.evaluate(arg, data)
                if not result:
                    return result
            return result
        if operator == "or":
            for arg in args:
                result = self.evaluate(arg, data)
                if result:
                    return result
            return False
        if operator == "!":
            return not bool(self.evaluate(args[0], data))
        if operator == "!!":
            return bool(self.evaluate(args[0], data))
        if operator == "missing":
            keys = args if isinstance(raw_args, list) else [raw_args]
            return [key for key in keys if self._resolve_var(key, data, missing_marker=None) is None]
        if operator in {"==", "===", "!=", "!==", ">", ">=", "<", "<="}:
            left = self.evaluate(args[0], data)
            right = self.evaluate(args[1], data)
            return self._compare(operator, left, right)
        if operator == "in":
            needle = self.evaluate(args[0], data)
            haystack = self.evaluate(args[1], data)
            if haystack is None:
                return False
            return needle in haystack
        if operator == "+":
            return sum(self._to_number(self.evaluate(arg, data)) for arg in args)
        if operator == "max":
            values = [self._to_number(self.evaluate(arg, data)) for arg in args]
            return max(values) if values else None
        if operator == "min":
            values = [self._to_number(self.evaluate(arg, data)) for arg in args]
            return min(values) if values else None

        raise ValueError(f"Opérateur JsonLogic non supporté: {operator}")

    def _resolve_var(self, raw: Any, data: Mapping[str, Any], missing_marker: Any = None) -> Any:
        """Résout une variable JsonLogic avec chemins pointés."""
        if isinstance(raw, list):
            path = raw[0] if raw else ""
            default = raw[1] if len(raw) > 1 else missing_marker
        else:
            path = raw
            default = missing_marker

        if path in ("", None):
            return data

        current: Any = data
        for part in str(path).split("."):
            if isinstance(current, Mapping) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
                current = current[int(part)]
            else:
                return default
        return current

    def _compare(self, operator: str, left: Any, right: Any) -> bool:
        """Compare deux valeurs en évitant les exceptions non déterministes."""
        if operator in {"==", "==="}:
            return left == right
        if operator in {"!=", "!=="}:
            return left != right
        if left is None or right is None:
            return False
        try:
            left_value = self._to_number(left)
            right_value = self._to_number(right)
        except (TypeError, ValueError):
            left_value = left
            right_value = right

        if operator == ">":
            return left_value > right_value
        if operator == ">=":
            return left_value >= right_value
        if operator == "<":
            return left_value < right_value
        if operator == "<=":
            return left_value <= right_value
        return False

    def _to_number(self, value: Any) -> float:
        """Convertit une valeur en nombre pour les comparaisons JsonLogic."""
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, int | float):
            return float(value)
        if isinstance(value, Decimal):
            return float(value)
        return float(str(value).replace(",", "."))


class ContractReviewer:
    """Moteur orchestrant LLM abstrait, règles déterministes et validation humaine."""

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,  # type: ignore[valid-type]
        *,
        rules_path: Path = RULES_PATH,
        prompts_path: Path = PROMPTS_PATH,
    ) -> None:
        """
        Initialise le reviewer.

        `llm_provider` doit être une instance conforme à `core.integrations.llm.provider.LLMProvider`.
        Aucun fournisseur concret ni appel externe n'est instancié ici.
        """
        self.llm_provider = llm_provider
        self.rules_path = rules_path
        self.prompts_path = prompts_path
        self.jsonlogic = JsonLogicEvaluator()
        self.ruleset = self._load_ruleset()
        self.prompts = self._load_prompts()

    async def review_contract(self, contract: ContractDocument) -> ReviewResult:
        """
        Exécute une revue assistée complète.

        La sortie est un rapport d'aide à la décision : l'avocat arbitre toujours.
        """
        structure = self._extract_structure(contract)
        validation_notes: list[str] = []
        llm_issues: list[ContractIssue] = []

        if self.llm_provider is None:
            validation_notes.append(
                "Analyse LLM non exécutée : aucun LLMProvider abstrait n'a été fourni. "
                "Les règles déterministes restent appliquées."
            )
        else:
            try:
                llm_issues = await self._detect_llm_issues(contract, structure)
            except Exception as exc:  # L'indisponibilité LLM ne doit pas empêcher les contrôles déterministes.
                validation_notes.append(
                    f"Analyse LLM indisponible ou illisible ({exc.__class__.__name__}) : "
                    "validation humaine renforcée requise."
                )

        rule_issues = self._detect_rule_issues(contract, structure)
        issues = self._merge_issues([*llm_issues, *rule_issues])
        risk_score, risk_level = self._score(issues)
        human_points = self._build_human_validation_points(issues, validation_notes)
        summary = self._build_summary(contract, issues, risk_score, risk_level, llm_executed=bool(llm_issues))

        return ReviewResult(
            contract_id=contract.id,
            contract_hash=contract.stable_hash(),
            issues=issues,
            risk_score=risk_score,
            risk_level=risk_level,
            summary=summary,
            human_validation_points=human_points,
            deterministic_ruleset_version=f"{self.ruleset.get('vertical', 'contract_review')}.rules.v1",
            llm_model=self._llm_model_name(),
            metadata={
                "review_chain": [
                    "structure_extraction",
                    "llm_assisted_detection",
                    "jsonlogic_deterministic_rules",
                    "risk_scoring",
                    "human_arbitration_preparation",
                ],
                "reviewed_at_utc": datetime.now(UTC).isoformat(),
                "mediator": "required",
                "worm_journal": "required",
                "final_decision": "human_only",
            },
        )

    def _load_ruleset(self) -> dict[str, Any]:
        """Charge le fichier de règles JsonLogic du vertical."""
        with self.rules_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        required = {"vertical", "description", "risk_appetite", "rules"}
        missing = required.difference(payload)
        if missing:
            raise ValueError(f"rules.json incomplet, champs manquants: {sorted(missing)}")
        return payload

    def _load_prompts(self) -> dict[str, Any]:
        """Charge les prompts YAML, avec repli déterministe si PyYAML est absent."""
        if not self.prompts_path.exists():
            return _DEFAULT_PROMPTS
        try:
            import yaml  # type: ignore

            with self.prompts_path.open("r", encoding="utf-8") as handle:
                loaded = yaml.safe_load(handle) or {}
            return loaded if isinstance(loaded, dict) else _DEFAULT_PROMPTS
        except Exception:
            return _DEFAULT_PROMPTS

    def _extract_structure(self, contract: ContractDocument) -> ContractStructure:
        """Extrait sections et faits structurés utiles aux règles."""
        sections = tuple(contract.sections or self._split_sections(contract.full_text()))
        facts = self._extract_facts(contract, sections)
        return ContractStructure(sections=sections, facts=facts)

    def _split_sections(self, text: str) -> list[ContractSection]:
        """Découpe heuristiquement un texte brut en sections contractuelles."""
        heading_re = re.compile(
            r"^\s*((?:article|clause|section)\s+\d+(?:\.\d+)*\s*[-–:.]?\s*.+|\d+(?:\.\d+)+\s+.+)$",
            re.IGNORECASE,
        )
        sections: list[ContractSection] = []
        current_title: str | None = None
        current_lines: list[str] = []
        index = 1

        for line in text.splitlines():
            if heading_re.match(line.strip()) and current_lines:
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append(
                        ContractSection(
                            id=f"section-{index:03d}",
                            title=current_title,
                            clause_ref=current_title,
                            text=body,
                        )
                    )
                    index += 1
                current_title = line.strip()
                current_lines = [line]
            else:
                if current_title is None and heading_re.match(line.strip()):
                    current_title = line.strip()
                current_lines.append(line)

        body = "\n".join(current_lines).strip()
        if body:
            sections.append(
                ContractSection(
                    id=f"section-{index:03d}",
                    title=current_title or "Texte intégral",
                    clause_ref=current_title,
                    text=body,
                )
            )

        return sections or [ContractSection(id="section-001", title="Texte intégral", text=text)]

    def _extract_facts(self, contract: ContractDocument, sections: tuple[ContractSection, ...]) -> dict[str, Any]:
        """Produit les variables consommées par JsonLogic."""
        text = "\n\n".join(section.text for section in sections)
        norm = self._normalize(text)

        governing_law_name = contract.governing_law or self._extract_law_name(norm)
        governing_law_region = self._region_for_name(governing_law_name)

        forum_exclusive = bool(
            re.search(r"\b(juridiction|competence|tribunaux|courts?)\b.{0,80}\b(exclusive|exclusive|exclusif|exclusive)\b", norm)
            or re.search(r"\b(exclusive|exclusif|exclusive)\b.{0,80}\b(juridiction|competence|tribunaux|courts?)\b", norm)
        )
        forum_window = self._window(norm, r"juridiction|competence|tribunaux|courts?")
        forum_name = self._extract_law_name(forum_window)
        forum_region = self._region_for_name(forum_name)

        non_compete_window = self._window(norm, r"non[-\s]?concurrence|non[-\s]?compete|non[-\s]?competition")
        non_compete_present = bool(non_compete_window)
        non_compete_duration = self._extract_duration_months(non_compete_window)
        non_compete_geo_unlimited = bool(
            non_compete_window
            and re.search(r"monde entier|worldwide|sans limite territoriale|aucune limite territoriale|territoire illimite", non_compete_window)
        )

        penalty_percent = self._extract_penalty_percent(norm)

        termination_present = bool(re.search(r"\bresiliation\b|\btermination\b|\bdenonciation\b|\bfin du contrat\b", norm))

        unilateral_window = self._window(norm, r"modifier unilateralement|unilaterally modify|modification unilaterale")
        unilateral_present = bool(unilateral_window)
        unilateral_notice = bool(re.search(r"preavis|notice|notification|delai", unilateral_window))

        liability_window = self._window(norm, r"responsabilite|liability")
        liability_unlimited = bool(re.search(r"responsabilite illimitee|unlimited liability|sans plafond", liability_window))
        liability_mutual = bool(re.search(r"reciproque|mutuel|mutuelle|each party|les parties", liability_window))

        personal_data_present = bool(re.search(r"donnees personnelles|personal data|rgpd|gdpr|lpd|data protection", norm))
        dpa_present = bool(
            re.search(
                r"accord de traitement|annexe de traitement|data processing agreement|\bdpa\b|sous-traitant au sens|processor agreement",
                norm,
            )
        )

        renewal_window = self._window(norm, r"tacite reconduction|renouvellement automatique|automatic renewal|automatically renew")
        renewal_present = bool(renewal_window)
        renewal_duration = self._extract_duration_months(renewal_window)
        renewal_notice_days = self._extract_notice_days(renewal_window)

        confidentiality_window = self._window(norm, r"confidentialite|confidentiality|secret")
        confidentiality_duration_months = self._extract_duration_months(confidentiality_window)
        confidentiality_years = (
            999
            if re.search(r"perpetuel|perpetuelle|perpetual|duree indeterminee", confidentiality_window)
            else (confidentiality_duration_months / 12 if confidentiality_duration_months is not None else None)
        )

        ip_window = self._window(norm, r"propriete intellectuelle|intellectual property|cession de droits|assignment of rights")
        ip_future_assignment = bool(re.search(r"droits futurs|future rights|tous droits presents et futurs|all present and future rights", ip_window))
        ip_compensation = bool(re.search(r"contrepartie|remuneration|compensation|prix|fee", ip_window))

        locations = {
            "governing_law": self._locate(sections, (r"droit applicable|loi applicable|governed by|laws of",)),
            "forum": self._locate(sections, (r"juridiction|competence|tribunaux|courts?",)),
            "non_compete": self._locate(sections, (r"non[-\s]?concurrence|non[-\s]?compete",)),
            "penalty": self._locate(sections, (r"penalite|clause penale|penalty|indemnite forfaitaire",)),
            "termination": self._locate(sections, (r"resiliation|termination|tacite reconduction|renouvellement automatique",)),
            "unilateral_modification": self._locate(sections, (r"modifier unilateralement|modification unilaterale|unilaterally modify",)),
            "liability": self._locate(sections, (r"responsabilite|liability",)),
            "data_protection": self._locate(sections, (r"donnees personnelles|personal data|rgpd|gdpr|lpd",)),
            "confidentiality": self._locate(sections, (r"confidentialite|confidentiality|secret",)),
            "ip": self._locate(sections, (r"propriete intellectuelle|intellectual property|cession de droits|assignment of rights",)),
        }

        return {
            "action": {"type": "contract_review"},
            "human_validated": False,
            "contract": {
                "id": contract.id,
                "type": contract.contract_type.value,
                "jurisdiction": contract.jurisdiction,
                "language": contract.language.value,
                "value": float(contract.contract_value) if contract.contract_value is not None else None,
                "currency": contract.currency,
                "governing_law": governing_law_name,
                "governing_law_region": governing_law_region,
            },
            "governing_law": {"name": governing_law_name, "region": governing_law_region},
            "forum": {"exclusive": forum_exclusive, "name": forum_name, "region": forum_region},
            "clauses": {
                "non_compete": {
                    "present": non_compete_present,
                    "duration_months": non_compete_duration,
                    "geographic_unlimited": non_compete_geo_unlimited,
                },
                "penalty": {"max_percent_of_contract": penalty_percent},
                "termination": {"present": termination_present},
                "unilateral_modification": {"present": unilateral_present, "notice_or_optout": unilateral_notice},
                "liability": {"unlimited": liability_unlimited, "mutual": liability_mutual},
                "data_processing": {"personal_data_present": personal_data_present, "dpa_present": dpa_present},
                "auto_renewal": {
                    "present": renewal_present,
                    "duration_months": renewal_duration,
                    "notice_days": renewal_notice_days,
                },
                "confidentiality": {"duration_years": confidentiality_years},
                "ip_assignment": {"future_rights": ip_future_assignment, "compensation": ip_compensation},
            },
            "_locations": locations,
        }

    async def _detect_llm_issues(self, contract: ContractDocument, structure: ContractStructure) -> list[ContractIssue]:
        """Demande au LLM abstrait une détection structurée de problèmes."""
        messages = self._build_llm_messages(contract, structure)
        response = await self._invoke_llm(messages)
        if response is None:
            return []
        return self._parse_llm_response(contract, response)

    def _build_llm_messages(self, contract: ContractDocument, structure: ContractStructure) -> list[dict[str, str]]:
        """Construit les messages sans coupler le moteur à un fournisseur LLM."""
        system_prompt = (
            self.prompts.get("system", {}).get("content")
            if isinstance(self.prompts.get("system"), Mapping)
            else None
        ) or _DEFAULT_PROMPTS["system"]["content"]

        facts_for_prompt = {k: v for k, v in structure.facts.items() if k != "_locations"}
        text = contract.full_text()
        if len(text) > MAX_LLM_CHARS:
            text = text[:MAX_LLM_CHARS] + "\n\n[TRONQUÉ POUR ANALYSE LLM — vérifier le document source complet]"

        user_prompt = (
            "Analyse le contrat ci-dessous pour assister un avocat. "
            "Retourne uniquement du JSON conforme au schéma demandé.\n\n"
            f"Métadonnées contrat:\n{json.dumps(facts_for_prompt, ensure_ascii=False, indent=2)}\n\n"
            "Schéma JSON attendu:\n"
            "{\n"
            '  "issues": [\n'
            "    {\n"
            '      "category": "clause_abusive|desequilibre_contractuel|obligation_manquante|droit_applicable_suspect|jurisdiction_risk|penalite_disproportionnee|non_concurrence_risquee|protection_donnees|responsabilite|propriete_intellectuelle|resiliation|autre",\n'
            '      "title": "titre court",\n'
            '      "severity": "info|low|medium|high|critical",\n'
            '      "location": {"section_title": "...", "clause_ref": "...", "excerpt": "..."},\n'
            '      "legal_basis": ["base juridique ou principe à vérifier"],\n'
            '      "recommendation": "action proposée à valider par avocat",\n'
            '      "rationale": "raisonnement synthétique",\n'
            '      "confidence": 0.0,\n'
            '      "requires_human_arbitration": true\n'
            "    }\n"
            "  ],\n"
            '  "human_validation_points": ["points non conclusifs à arbitrer"]\n'
            "}\n\n"
            "Rappels impératifs: ne pas décider, ne pas rédiger de conclusion finale, "
            "signaler les incertitudes, respecter art. 321 CP/RGPD/LPD.\n\n"
            f"Contrat:\n{text}"
        )
        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    async def _invoke_llm(self, messages: list[dict[str, str]]) -> Any:
        """Appelle un LLMProvider abstrait en supportant les signatures usuelles du projet."""
        provider = self.llm_provider
        if provider is None:
            return None

        prompt = "\n\n".join(f"{message['role'].upper()}:\n{message['content']}" for message in messages)
        method_names = ("acomplete", "complete", "agenerate", "generate", "achat", "chat")

        attempts: list[tuple[tuple[Any, ...], dict[str, Any]]] = [
            ((), {"messages": messages, "temperature": 0, "response_format": {"type": "json_object"}}),
            ((), {"messages": messages, "temperature": 0}),
            ((messages,), {}),
            ((), {"prompt": prompt, "temperature": 0}),
            ((prompt,), {}),
        ]

        for method_name in method_names:
            method = getattr(provider, method_name, None)
            if method is None:
                continue
            for args, kwargs in attempts:
                try:
                    result = method(*args, **kwargs)
                    if inspect.isawaitable(result):
                        result = await result
                    return result
                except TypeError:
                    continue

        if callable(provider):
            result = provider(prompt)
            if inspect.isawaitable(result):
                result = await result
            return result

        raise TypeError("LLMProvider incompatible: aucune méthode abstraite reconnue")

    def _parse_llm_response(self, contract: ContractDocument, response: Any) -> list[ContractIssue]:
        """Parse et valide une réponse LLM en objets ContractIssue."""
        payload = self._response_to_payload(response)
        raw_issues = payload.get("issues", []) if isinstance(payload, Mapping) else []
        if not isinstance(raw_issues, list):
            raise ValueError("Réponse LLM invalide: issues doit être une liste")

        issues: list[ContractIssue] = []
        for raw in raw_issues:
            if not isinstance(raw, Mapping):
                continue
            location_raw = raw.get("location") if isinstance(raw.get("location"), Mapping) else {}
            title = str(raw.get("title") or "Risque contractuel à vérifier")
            severity = self._parse_severity(raw.get("severity"), default=IssueSeverity.MEDIUM)
            category = self._parse_category(raw.get("category"))
            issue_id = self._stable_issue_id(contract.id, "llm", title, json.dumps(location_raw, ensure_ascii=False))

            issues.append(
                ContractIssue(
                    id=issue_id,
                    category=category,
                    title=title,
                    severity=severity,
                    location=IssueLocation(
                        section_id=location_raw.get("section_id"),
                        section_title=location_raw.get("section_title"),
                        clause_ref=location_raw.get("clause_ref"),
                        page=location_raw.get("page"),
                        excerpt=location_raw.get("excerpt"),
                    ),
                    legal_basis=[str(item) for item in raw.get("legal_basis", []) if item],
                    recommendation=str(raw.get("recommendation") or "Point à vérifier et arbitrer par l'avocat."),
                    rationale=str(raw.get("rationale") or "Détection assistée par LLM nécessitant validation humaine."),
                    source=IssueSource.LLM,
                    confidence=float(raw.get("confidence", 0.5)),
                    requires_human_arbitration=bool(raw.get("requires_human_arbitration", True)),
                )
            )
        return issues

    def _response_to_payload(self, response: Any) -> Mapping[str, Any]:
        """Convertit une réponse provider en dictionnaire JSON."""
        if isinstance(response, Mapping):
            if "choices" in response and isinstance(response["choices"], list) and response["choices"]:
                choice = response["choices"][0]
                if isinstance(choice, Mapping):
                    message = choice.get("message")
                    if isinstance(message, Mapping) and "content" in message:
                        return self._json_from_text(str(message["content"]))
            if "content" in response and isinstance(response["content"], str):
                return self._json_from_text(response["content"])
            if "issues" in response:
                return response
        for attr in ("content", "text", "output"):
            value = getattr(response, attr, None)
            if isinstance(value, str):
                return self._json_from_text(value)
            if isinstance(value, Mapping):
                return value
        if isinstance(response, str):
            return self._json_from_text(response)
        raise ValueError("Type de réponse LLM non supporté")

    def _json_from_text(self, text: str) -> Mapping[str, Any]:
        """Extrait un objet JSON depuis du texte, y compris blocs Markdown."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if not match:
                raise
            parsed = json.loads(match.group(0))
        if not isinstance(parsed, Mapping):
            raise ValueError("La réponse LLM doit être un objet JSON")
        return parsed

    def _detect_rule_issues(self, contract: ContractDocument, structure: ContractStructure) -> list[ContractIssue]:
        """Applique les règles JsonLogic déterministes."""
        issues: list[ContractIssue] = []
        for rule in self.ruleset.get("rules", []):
            condition = rule.get("condition")
            if not condition:
                continue
            if self.jsonlogic.evaluate(condition, structure.facts):
                rule_id = str(rule["id"])
                severity = self._parse_severity(rule.get("severity"), default=IssueSeverity.HIGH)
                action = str(rule.get("action", "flag"))
                title = str(rule.get("name", "Règle contractuelle déclenchée"))
                location = self._location_for_rule(rule_id, structure.facts)
                issues.append(
                    ContractIssue(
                        id=self._stable_issue_id(contract.id, "jsonlogic", rule_id, title),
                        category=_CATEGORY_BY_RULE.get(rule_id, IssueCategory.OTHER),
                        title=title,
                        severity=severity,
                        location=location,
                        legal_basis=_LEGAL_BASIS_BY_RULE.get(rule_id, ["Point juridique à valider par avocat."]),
                        recommendation=str(rule.get("message", "Validation par avocat requise.")),
                        rationale=(
                            f"Règle déterministe JsonLogic {rule_id} déclenchée. "
                            "Le Médiateur doit appliquer l'action prévue sans rendre de décision finale."
                        ),
                        source=IssueSource.JSONLOGIC,
                        confidence=1.0,
                        requires_human_arbitration=action in {"freeze", "block"} or severity in {IssueSeverity.HIGH, IssueSeverity.CRITICAL},
                        rule_id=rule_id,
                        action=action,
                    )
                )
        return issues

    def _location_for_rule(self, rule_id: str, facts: Mapping[str, Any]) -> IssueLocation:
        """Associe une règle à la meilleure localisation extraite."""
        key_by_rule = {
            "contract-review-001": "non_compete",
            "contract-review-002": "non_compete",
            "contract-review-003": "governing_law",
            "contract-review-004": "forum",
            "contract-review-005": "penalty",
            "contract-review-006": "termination",
            "contract-review-007": "unilateral_modification",
            "contract-review-008": "liability",
            "contract-review-009": "data_protection",
            "contract-review-010": "termination",
            "contract-review-011": "confidentiality",
            "contract-review-012": "ip",
        }
        locations = facts.get("_locations", {})
        location = locations.get(key_by_rule.get(rule_id, ""))
        return location if isinstance(location, IssueLocation) else IssueLocation()

    def _merge_issues(self, issues: Iterable[ContractIssue]) -> list[ContractIssue]:
        """Fusionne les doublons simples tout en conservant les sources déterministes."""
        by_key: dict[tuple[str, str], ContractIssue] = {}
        severity_rank = {
            IssueSeverity.INFO: 1,
            IssueSeverity.LOW: 2,
            IssueSeverity.MEDIUM: 3,
            IssueSeverity.HIGH: 4,
            IssueSeverity.CRITICAL: 5,
        }

        for issue in issues:
            key = (issue.category.value, self._normalize(issue.title)[:80])
            existing = by_key.get(key)
            if existing is None:
                by_key[key] = issue
                continue

            if severity_rank[issue.severity] > severity_rank[existing.severity]:
                existing.severity = issue.severity
            existing.requires_human_arbitration = existing.requires_human_arbitration or issue.requires_human_arbitration
            existing.legal_basis = sorted(set(existing.legal_basis).union(issue.legal_basis))
            if existing.source != issue.source:
                existing.source = IssueSource.HYBRID
            if not existing.rule_id and issue.rule_id:
                existing.rule_id = issue.rule_id
                existing.action = issue.action
        return sorted(
            by_key.values(),
            key=lambda item: (severity_rank[item.severity], item.requires_human_arbitration, item.title),
            reverse=True,
        )

    def _score(self, issues: list[ContractIssue]) -> tuple[int, RiskLevel]:
        """Calcule un score de risque explicable, non décisionnel."""
        weights = {
            IssueSeverity.INFO: 1,
            IssueSeverity.LOW: 4,
            IssueSeverity.MEDIUM: 9,
            IssueSeverity.HIGH: 18,
            IssueSeverity.CRITICAL: 30,
        }
        score = sum(weights[issue.severity] for issue in issues)
        score += 8 * sum(1 for issue in issues if issue.action == "freeze")
        score += 12 * sum(1 for issue in issues if issue.action == "block")
        score = min(100, score)

        if score >= 75 or any(issue.severity == IssueSeverity.CRITICAL for issue in issues):
            level = RiskLevel.CRITICAL
        elif score >= 50 or any(issue.severity == IssueSeverity.HIGH for issue in issues):
            level = RiskLevel.HIGH
        elif score >= 20:
            level = RiskLevel.MODERATE
        else:
            level = RiskLevel.LOW
        return score, level

    def _build_human_validation_points(self, issues: list[ContractIssue], notes: list[str]) -> list[str]:
        """Prépare les points pour arbitrage humain."""
        points = list(notes)
        for issue in issues:
            if issue.requires_human_arbitration:
                location = issue.location.clause_ref or issue.location.section_title or "localisation à confirmer"
                points.append(f"{issue.title} ({location}) — {issue.recommendation}")
        points.append("Vérifier la complétude du contrat source et des annexes avant toute conclusion.")
        points.append("Validation finale par l'avocat obligatoire.")
        return list(dict.fromkeys(points))

    def _build_summary(
        self,
        contract: ContractDocument,
        issues: list[ContractIssue],
        risk_score: int,
        risk_level: RiskLevel,
        *,
        llm_executed: bool,
    ) -> str:
        """Produit une synthèse non conclusive pour l'avocat."""
        if not issues:
            return (
                f"Revue assistée du contrat « {contract.title} » : aucun risque matériel n'a été détecté "
                "par les contrôles exécutés. Cette absence de détection ne vaut pas validation juridique ; "
                "l'avocat doit vérifier le document complet, ses annexes et le contexte client."
            )

        critical_count = sum(1 for issue in issues if issue.severity == IssueSeverity.CRITICAL)
        high_count = sum(1 for issue in issues if issue.severity == IssueSeverity.HIGH)
        freeze_count = sum(1 for issue in issues if issue.action == "freeze")
        llm_note = "avec assistance LLM" if llm_executed else "sur règles déterministes uniquement"

        return (
            f"Revue assistée {llm_note} du contrat « {contract.title} » : {len(issues)} point(s) à examiner, "
            f"dont {critical_count} critique(s), {high_count} élevé(s) et {freeze_count} gel(s) Médiateur attendu(s). "
            f"Score indicatif non décisionnel : {risk_score}/100 ({risk_level.value}). "
            "L'avocat arbitre les suites ; Cortex Leman ne rend aucune décision finale."
        )

    def _llm_model_name(self) -> str | None:
        """Retourne le nom de modèle si exposé par le provider abstrait."""
        provider = self.llm_provider
        if provider is None:
            return None
        for attr in ("model", "model_name", "deployment", "name"):
            value = getattr(provider, attr, None)
            if isinstance(value, str) and value:
                return value
        return provider.__class__.__name__

    def _parse_severity(self, value: Any, *, default: IssueSeverity) -> IssueSeverity:
        """Parse une sévérité en valeur contrôlée."""
        try:
            return IssueSeverity(str(value).lower())
        except Exception:
            return default

    def _parse_category(self, value: Any) -> IssueCategory:
        """Parse une catégorie LLM en valeur contrôlée."""
        try:
            return IssueCategory(str(value))
        except Exception:
            return IssueCategory.OTHER

    def _stable_issue_id(self, contract_id: str, source: str, *parts: str) -> str:
        """Construit un identifiant stable pour l'audit et la déduplication."""
        digest = sha256("|".join((contract_id, source, *parts)).encode("utf-8")).hexdigest()[:16]
        return f"issue-{digest}"

    def _normalize(self, text: str | None) -> str:
        """Normalise un texte pour extraction robuste."""
        if not text:
            return ""
        decomposed = unicodedata.normalize("NFKD", text)
        stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
        return re.sub(r"\s+", " ", stripped.lower()).strip()

    def _window(self, normalized_text: str, pattern: str, *, before: int = 260, after: int = 520) -> str:
        """Retourne une fenêtre de texte normalisé autour d'un motif."""
        match = re.search(pattern, normalized_text)
        if not match:
            return ""
        start = max(0, match.start() - before)
        end = min(len(normalized_text), match.end() + after)
        return normalized_text[start:end]

    def _extract_law_name(self, normalized_text: str | None) -> str | None:
        """Détecte un pays ou système juridique mentionné."""
        if not normalized_text:
            return None
        for alias in sorted(_COUNTRY_ALIASES, key=len, reverse=True):
            if re.search(rf"\b{re.escape(alias)}\b", normalized_text):
                return alias
        return None

    def _region_for_name(self, name: str | None) -> str | None:
        """Classe une loi ou juridiction en UE/CH, hors UE/CH ou inconnu."""
        if not name:
            return None
        code = _COUNTRY_ALIASES.get(self._normalize(name), None)
        if code == "CH" or code in _EU_COUNTRY_CODES:
            return "EU_CH"
        return "OUTSIDE_EU_CH"

    def _extract_duration_months(self, text: str) -> int | None:
        """Extrait une durée en mois depuis une fenêtre normalisée."""
        if not text:
            return None
        matches = re.findall(
            r"(\d{1,3})\s*(mois|month|months|an|ans|annee|annees|year|years)",
            text,
            flags=re.IGNORECASE,
        )
        if not matches:
            return None
        durations: list[int] = []
        for raw_value, unit in matches:
            value = int(raw_value)
            if unit.startswith(("an", "anne", "year")):
                value *= 12
            durations.append(value)
        return max(durations) if durations else None

    def _extract_notice_days(self, text: str) -> int | None:
        """Extrait un préavis en jours depuis une fenêtre normalisée."""
        if not text:
            return None
        match = re.search(r"preavis|notice", text)
        if not match:
            return None
        window = text[match.start() : match.start() + 160]
        duration = self._extract_duration_months(window)
        if duration is not None:
            return duration * 30
        day_match = re.search(r"(\d{1,3})\s*(jour|jours|day|days)", window)
        return int(day_match.group(1)) if day_match else None

    def _extract_penalty_percent(self, normalized_text: str) -> float | None:
        """Extrait le pourcentage maximal de pénalité contractuelle."""
        values: list[float] = []
        patterns = (
            r"(penalite|penalty|clause penale|indemnite forfaitaire).{0,220}?(\d{1,3}(?:[,.]\d+)?)\s*%",
            r"(\d{1,3}(?:[,.]\d+)?)\s*%.{0,220}?(penalite|penalty|clause penale|indemnite forfaitaire)",
        )
        for pattern in patterns:
            for match in re.finditer(pattern, normalized_text):
                raw = match.group(2) if match.group(2).replace(",", ".").replace(".", "", 1).isdigit() else match.group(1)
                try:
                    values.append(float(raw.replace(",", ".")))
                except ValueError:
                    continue
        return max(values) if values else None

    def _locate(self, sections: tuple[ContractSection, ...], patterns: tuple[str, ...]) -> IssueLocation:
        """Localise un motif dans les sections."""
        for section in sections:
            norm = self._normalize(section.text)
            for pattern in patterns:
                match = re.search(pattern, norm)
                if match:
                    excerpt = self._excerpt(section.text, max(0, match.start() - 160), 520)
                    return IssueLocation(
                        section_id=section.id,
                        section_title=section.title,
                        clause_ref=section.clause_ref,
                        page=section.page_start,
                        excerpt=excerpt,
                    )
        return IssueLocation()

    def _excerpt(self, text: str, start: int, length: int) -> str:
        """Produit un extrait borné pour le rapport."""
        normalized_start = max(0, min(start, len(text)))
        excerpt = text[normalized_start : normalized_start + length].strip()
        return re.sub(r"\s+", " ", excerpt)


async def review_contract(
    contract: ContractDocument,
    llm_provider: LLMProvider | None = None,  # type: ignore[valid-type]
) -> ReviewResult:
    """
    Fonction d'entrée asynchrone du wedge revue de contrats.

    Le LLM reste optionnel et toujours injecté via l'interface abstraite du projet.
    Sans provider, le moteur exécute les contrôles déterministes et signale la limite.
    """
    reviewer = ContractReviewer(llm_provider=llm_provider)
    return await reviewer.review_contract(contract)


def review_contract_sync(
    contract: ContractDocument,
    llm_provider: LLMProvider | None = None,  # type: ignore[valid-type]
) -> ReviewResult:
    """
    Pont synchrone pour intégrations CLI ou scripts internes.

    À éviter dans les agents async ; préférer `await review_contract(...)`.
    """
    return asyncio.run(review_contract(contract, llm_provider=llm_provider))
