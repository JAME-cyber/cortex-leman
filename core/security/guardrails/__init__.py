"""
Cortex Leman v5 — Guardrails LLM

Couche de sécurité pour les entrées/sorties LLM.
Protège contre: PII leak, jailbreak, off-topic, contenu dangereux.

Contrairement au Médiateur (déterministe, JsonLogic),
les guardrails filtrent le CONTENU du LLM avant/après appel.

Ne remplace PAS le Médiateur — c'est une couche supplémentaire.
"""
import re
import logging
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class GuardrailResult:
    """Résultat d'une vérification guardrail"""
    passed: bool
    blocked: bool = False
    reason: str = ""
    category: str = ""
    cleaned_content: str = ""
    violations: list = field(default_factory=list)


class PIIGuard:
    """Détection et masquage de données personnelles (PII)"""

    # Patterns de détection PII
    PATTERNS = {
        "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        "phone_fr": re.compile(r'\b(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}\b'),
        "phone_ch": re.compile(r'\b(?:\+41|0)(?:[\s.-]?\d{2}){4}\d{2}\b'),
        "iban_fr": re.compile(r'\bFR\d{2}[A-Z0-9]{23}\b'),
        "iban_ch": re.compile(r'\bCH\d{2}[A-Z0-9]{17}\b'),
        "ssn_fr": re.compile(r'\b\d{1,2}\s\d{2}\s\d{2}\s\d{3}\s\d{3}\d{2}\b'),
        "avs_ch": re.compile(r'\b\d{3}\.\d{4}\.\d{4}\.\d{2}\b'),
        "credit_card": re.compile(r'\b(?:\d{4}[\s-]?){3}\d{4}\b'),
        "date_naissance": re.compile(r'\b\d{2}[/.-]\d{2}[/.-]\d{4}\b'),
        "nom_patient": re.compile(r'\b(?:patient|M\.|Mme\.|Dr\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'),
    }

    # Patterns spécifiques par verticale
    VERTICAL_EXTRA = {
        "sante": [
            ("diagnostic", re.compile(r'\b(?:diagnostic|pathologie|traitement|maladie)\s+(?:de|du|d\')?\s*[A-Z][a-z]+', re.IGNORECASE)),
        ],
        "banque": [
            ("compte_bancaire", re.compile(r'\bcompte\s*(?:n°|numéro|number)?\s*\d{5,}\b', re.IGNORECASE)),
        ],
    }

    def check(self, content: str, vertical: str = "unknown") -> GuardrailResult:
        """Vérifier et masquer les PII dans le contenu"""
        violations = []
        cleaned = content

        # Patterns généraux
        for pii_type, pattern in self.PATTERNS.items():
            matches = pattern.findall(content)
            if matches:
                violations.append(f"PII détecté: {pii_type} ({len(matches)} occurrence(s))")
                for match in matches:
                    cleaned = cleaned.replace(match, f"[{pii_type.upper()}_REDACTED]")

        # Patterns verticaux
        for pii_type, pattern in self.VERTICAL_EXTRA.get(vertical, []):
            matches = pattern.findall(content)
            if matches:
                violations.append(f"PII métier: {pii_type} ({len(matches)})")

        return GuardrailResult(
            passed=len(violations) == 0,
            blocked=False,  # On masque, on ne bloque pas
            reason="PII détecté et masqué" if violations else "",
            category="pii",
            cleaned_content=cleaned,
            violations=violations,
        )


class TopicGuard:
    """Contrôle que le LLM reste sur les sujets autorisés"""

    # Patterns interdits (quel que soit l'agent)
    FORBIDDEN_PATTERNS = [
        re.compile(r'contourner\s+(?:la\s+)?(?:r[eé]glementation|loi|r[eé]gle)', re.IGNORECASE),
        re.compile(r'[eé]chapper\s+[aà]\s+l[\'\']?imp[oô]t', re.IGNORECASE),
        re.compile(r'fraud(?:er|e)', re.IGNORECASE),
        re.compile(r'blanchir\s+(?:de\s+l[\'\']?)?argent', re.IGNORECASE),
        re.compile(r'(?:hack|exploit|vulnerability)', re.IGNORECASE),
        re.compile(r'instruction\s+ill[eé]gale', re.IGNORECASE),
    ]

    # Sujets autorisés par verticale
    ALLOWED_TOPICS = {
        "comptable": ["comptabilité", "fiscal", "tva", "bilan", "audit", "écriture", "déduction", "charges"],
        "avocat": ["juridique", "contrat", "litige", "conformité", "rgpd", "secret professionnel"],
        "sante": ["santé", "patient", "données médicales", "consentement", "hds", "lpm"],
        "banque": ["bancaire", "crédit", "kyc", "aml", "conformité", "finma"],
        "startup": ["ia", "rgpd", "ai act", "dpia", "données", "conformité"],
        "rh": ["recrutement", "discrimination", "rgpd", "ai act", "emploi", "paie"],
    }

    def check(self, content: str, vertical: str = "unknown") -> GuardrailResult:
        """Vérifier que le contenu reste dans les sujets autorisés"""
        content_lower = content.lower()
        violations = []

        # Vérifier sujets interdits
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern.search(content_lower):
                violations.append("Sujet interdit détecté")

        if violations:
            return GuardrailResult(
                passed=False,
                blocked=True,
                reason="Contenu bloque: sujet interdit détecté",
                category="topic_forbidden",
                violations=violations,
            )

        return GuardrailResult(
            passed=True,
            category="topic",
        )


class OutputSafetyGuard:
    """Vérification de sécurité sur les sorties LLM"""

    # Patterns dangereux dans les sorties
    DANGEROUS_PATTERNS = [
        re.compile(r'```(?:python|bash|sh|sql)\s*(?:DROP|DELETE|TRUNCATE|rm\s+-rf|os\.system|subprocess)', re.IGNORECASE),
        re.compile(r'(?:mot de passe|password|secret|clé\s+privée)\s*[:=]', re.IGNORECASE),
        re.compile(r'je\s+(?:peux|vais)\s+(?:vous\s+)?aidez?\s+(?:à|de)\s+(?:contourner|frauder|échapper)', re.IGNORECASE),
    ]

    def check(self, content: str) -> GuardrailResult:
        """Vérifier la sécurité du contenu de sortie"""
        violations = []

        for pattern in self.DANGEROUS_PATTERNS:
            matches = pattern.findall(content)
            if matches:
                violations.append(f"Pattern dangereux détecté")

        return GuardrailResult(
            passed=len(violations) == 0,
            blocked=len(violations) > 0,
            reason="Sortie bloquée: contenu potentiellement dangereux" if violations else "",
            category="output_safety",
            violations=violations,
        )


class GuardrailPipeline:
    """
    Pipeline complet de guardrails.
    
    Utilisé par LLMService.generate() pour filtrer
    les entrées ET les sorties de chaque appel LLM.
    """

    def __init__(self):
        self.pii = PIIGuard()
        self.topic = TopicGuard()
        self.safety = OutputSafetyGuard()

    def check_input(self, content: str, vertical: str = "unknown") -> GuardrailResult:
        """Vérifier l'entrée utilisateur avant envoi au LLM"""
        # 1. PII detection + masking
        pii_result = self.pii.check(content, vertical)
        cleaned = pii_result.cleaned_content if pii_result.violations else content

        # 2. Topic control
        topic_result = self.topic.check(cleaned, vertical)

        if topic_result.blocked:
            logger.warning(f"Guardrail INPUT bloqué: {topic_result.reason}")
            return GuardrailResult(
                passed=False,
                blocked=True,
                reason=topic_result.reason,
                category="input_blocked",
                cleaned_content="",
                violations=pii_result.violations + topic_result.violations,
            )

        return GuardrailResult(
            passed=True,
            blocked=False,
            reason=pii_result.reason,
            category="input_cleaned" if pii_result.violations else "input_ok",
            cleaned_content=cleaned,
            violations=pii_result.violations,
        )

    def check_output(self, content: str, vertical: str = "unknown") -> GuardrailResult:
        """Vérifier la sortie LLM avant restitution"""
        # 1. PII detection (le LLM peut avoir généré des PII)
        pii_result = self.pii.check(content, vertical)
        cleaned = pii_result.cleaned_content if pii_result.violations else content

        # 2. Output safety
        safety_result = self.safety.check(cleaned)

        if safety_result.blocked:
            logger.warning(f"Guardrail OUTPUT bloqué: {safety_result.reason}")
            return GuardrailResult(
                passed=False,
                blocked=True,
                reason=safety_result.reason,
                category="output_blocked",
                cleaned_content="[CONTENU_BLOQUE_PAR_GUARDRAIL]",
                violations=safety_result.violations,
            )

        return GuardrailResult(
            passed=True,
            blocked=False,
            reason=pii_result.reason,
            category="output_cleaned" if pii_result.violations else "output_ok",
            cleaned_content=cleaned,
            violations=pii_result.violations,
        )


# Singleton
guardrails = GuardrailPipeline()
