"""
Cortex Leman v5 — Insight 1: AutoDefense Multi-Agent

Inspiré du paper AG2 "AutoDefense: Multi-Agent LLM Defense against Jailbreak Attacks"
Utilise plusieurs agents légers en parallèle pour détecter les attaques
et renforcer la pipeline de guardrails existante.

Contrairement aux guardrails existants (règles regex mono-agent),
AutoDefense utilise 3 validateurs indépendants qui votent.

Pattern: 3 validateurs → vote majoritaire → block/pass
"""
import re
import logging
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class DefenseVote:
    """Vote d'un validateur individuel"""
    validator: str
    passed: bool
    confidence: float  # 0.0 → 1.0
    reason: str = ""


@dataclass
class AutoDefenseResult:
    """Résultat du vote multi-agent"""
    passed: bool
    blocked: bool
    votes: list[DefenseVote] = field(default_factory=list)
    consensus: float = 0.0  # % de validateurs d'accord
    category: str = ""
    reason: str = ""


class PromptInjectionValidator:
    """
    Validateur 1: Détection d'injection de prompt.
    Détecte les tentatives de manipulation du système prompt.
    """

    INJECTION_PATTERNS = [
        re.compile(r'ignore\s+(?:previous|all|above|your)\s+instructions?', re.IGNORECASE),
        re.compile(r'forget\s+(?:everything|all|your\s+instructions)', re.IGNORECASE),
        re.compile(r'(?:you\s+are|act\s+as|pretend\s+(?:to\s+be|you))\s+(?:now|a\s+)?(?:free|unrestricted|uncensored)', re.IGNORECASE),
        re.compile(r'system\s*:\s*(?:you|now|output)', re.IGNORECASE),
        re.compile(r'(?:jailbreak|DAN|evil|malicious)\s+mode', re.IGNORECASE),
        re.compile(r'(?:bypass|skip|disable|deactivate)\s+(?:the\s+)?(?:filter|guard|safety|security|moderation)', re.IGNORECASE),
        re.compile(r'output\s+(?:your|the)\s+(?:system|initial)\s+prompt', re.IGNORECASE),
        re.compile(r'(?:reveal|show|tell|print)\s+(?:me\s+)?(?:your|the)\s+(?:system|secret|hidden)\s+(?:prompt|instructions?)', re.IGNORECASE),
    ]

    def validate(self, content: str) -> DefenseVote:
        """Vérifier si le contenu contient une injection de prompt"""
        for pattern in self.INJECTION_PATTERNS:
            if pattern.search(content):
                return DefenseVote(
                    validator="prompt_injection",
                    passed=False,
                    confidence=0.95,
                    reason=f"Injection de prompt détectée: pattern '{pattern.pattern[:40]}...'",
                )

        # Heuristique secondaire: ratio de mots "d'instruction"
        instruction_words = ["ignore", "forget", "pretend", "bypass", "override", "system"]
        content_lower = content.lower()
        count = sum(1 for w in instruction_words if w in content_lower)
        if count >= 3:
            return DefenseVote(
                validator="prompt_injection",
                passed=False,
                confidence=0.7,
                reason=f"Heuristique: {count} mots d'instruction détectés",
            )

        return DefenseVote(
            validator="prompt_injection",
            passed=True,
            confidence=0.9,
            reason="Aucune injection détectée",
        )


class RegulatoryComplianceValidator:
    """
    Validateur 2: Conformité réglementaire du contenu.
    Vérifie que le contenu ne viole pas les obligations réglementaires FR-CH.
    """

    # Patterns qui indiquent une violation potentielle
    VIOLATION_PATTERNS = [
        (re.compile(r'(?:conseil\s+)?(?:d\'éviter|contourner|ne\s+pas\s+déclarer)\s+(?:(?:l\'|la\s+|le\s+)?)(?:impôt|réglementation|loi|règles?)', re.IGNORECASE),
         "Incitation à contourner la réglementation"),
        (re.compile(r'(?:sans\s+consentement|sans\s+autorisation)\s+(?:du\s+)?(?:patient|client)', re.IGNORECASE),
         "Violation du consentement (RGPD/LPM)"),
        (re.compile(r'(?:divulgu|partag|transmet)\s+(?:les?\s+)?(?:données|infos?|informations?)\s+(?:du\s+)?(?:patient|client|dossier)', re.IGNORECASE),
         "Divulgation potentielle de données protégées"),
        (re.compile(r'(?:pas\s+bésion|inutile\s+de)\s+(?:de\s+)?(?:déclarer|consent|autor|anonym)', re.IGNORECASE),
         "Dissuasion de conformité réglementaire"),
        (re.compile(r'(?:je\s+)?(?:peux|vais|vais\s+)\s+(?:vous\s+)?(?:donner|fournir|transmettre)\s+(?:les?\s+)?(?:données|dossier|infos?)\s+(?:de|du)', re.IGNORECASE),
         "Proposition de divulgation non contrôlée"),
    ]

    # Patterns de contextes autorisés qui neutralisent les alertes
    SAFE_CONTEXTS = [
        re.compile(r'(?:dans\s+le\s+cadre\s+du|conformément\s+au|selon\s+le)\s+(?:mandat|consentement|cadre\s+légal)', re.IGNORECASE),
        re.compile(r'(?:après\s+)?(?:obtention\s+du\s+)?consentement\s+(?:éclairé|exprès|du\s+client)', re.IGNORECASE),
        re.compile(r'(?:anonymisées?|pseudonymisées?|agrégées?)', re.IGNORECASE),
    ]

    def validate(self, content: str, vertical: str = "unknown") -> DefenseVote:
        """Vérifier la conformité réglementaire du contenu"""
        for pattern, reason in self.VIOLATION_PATTERNS:
            if pattern.search(content):
                # Vérifier s'il y a un contexte autorisé
                for safe in self.SAFE_CONTEXTS:
                    if safe.search(content):
                        return DefenseVote(
                            validator="regulatory_compliance",
                            passed=True,
                            confidence=0.8,
                            reason=f"Alerte neutralisée par contexte autorisé: {reason}",
                        )

                return DefenseVote(
                    validator="regulatory_compliance",
                    passed=False,
                    confidence=0.85,
                    reason=f"Violation potentielle: {reason}",
                )

        return DefenseVote(
            validator="regulatory_compliance",
            passed=True,
            confidence=0.95,
            reason="Conforme réglementairement",
        )


class SemanticAnomalyValidator:
    """
    Validateur 3: Détection d'anomalies sémantiques.
    Détecte les contenus inhabituels qui pourraient être des attaques
    non couvertes par les patterns (zero-day).
    """

    def validate(self, content: str) -> DefenseVote:
        """Vérifier les anomalies sémantiques"""
        anomalies = []
        content_lower = content.lower()

        # 1. Longueur suspecte (prompt très long = souvent une injection)
        if len(content) > 5000:
            anomalies.append("Contenu anormalement long")

        # 2. Répétition suspecte (attaque par épuisement)
        words = content_lower.split()
        if len(words) > 20:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                anomalies.append(f"Répétition suspecte (ratio unicité: {unique_ratio:.1%})")

        # 3. Multi-langue suspecte (technique d'evasion)
        lang_markers = {
            "en": len(re.findall(r'\b(the|is|are|can|will|should|must)\b', content_lower)),
            "fr": len(re.findall(r'\b(le|la|les|est|sont|peut|doit|faut)\b', content_lower)),
        }
        active_langs = sum(1 for c in lang_markers.values() if c > 3)
        if active_langs >= 2:
            anomalies.append("Multi-langue suspect (possible évasion)")

        # 4. Caractères spéciaux excessifs (technique d'obfuscation)
        special_chars = sum(1 for c in content if not c.isalnum() and not c.isspace())
        if len(content) > 0 and special_chars / len(content) > 0.3:
            anomalies.append(f"Excès de caractères spéciaux ({special_chars}/{len(content)})")

        # 5. Encodage suspect (base64, hex)
        if re.search(r'(?:[A-Za-z0-9+/]{40,}={0,2})', content):
            anomalies.append("Possible encodage base64 détecté")

        if anomalies:
            confidence = min(0.5 + len(anomalies) * 0.15, 0.9)
            return DefenseVote(
                validator="semantic_anomaly",
                passed=False,
                confidence=confidence,
                reason=f"Anomalies: {'; '.join(anomalies)}",
            )

        return DefenseVote(
            validator="semantic_anomaly",
            passed=True,
            confidence=0.85,
            reason="Aucune anomalie détectée",
        )


class AutoDefense:
    """
    AutoDefense: Multi-Agent Defense (inspiré AG2)

    3 validateurs indépendants votent en parallèle.
    Vote majoritaire (2/3 minimum) pour bloquer.
    En cas d'égalité, on bloque par sécurité (principe de précaution).
    """

    def __init__(self):
        self.validators = {
            "prompt_injection": PromptInjectionValidator(),
            "regulatory_compliance": RegulatoryComplianceValidator(),
            "semantic_anomaly": SemanticAnomalyValidator(),
        }

    def defend(
        self, content: str, vertical: str = "unknown"
    ) -> AutoDefenseResult:
        """
        Exécuter la defense multi-agent sur le contenu.

        Returns:
            AutoDefenseResult avec le consensus des validateurs
        """
        votes: list[DefenseVote] = []

        # Exécution parallèle des 3 validateurs
        votes.append(self.validators["prompt_injection"].validate(content))
        votes.append(self.validators["regulatory_compliance"].validate(content, vertical))
        votes.append(self.validators["semantic_anomaly"].validate(content))

        # Calcul du consensus
        pass_count = sum(1 for v in votes if v.passed)
        fail_count = len(votes) - pass_count

        # Vote majoritaire: 2+ échecs = blocage
        blocked = fail_count >= 2
        passed = pass_count >= 2

        # En cas d'égalité (1 vs 1 vs 1 ou 1 échec avec haute confiance)
        # Principe de précaution: vérifier confiance des échecs
        if not blocked and fail_count == 1:
            failing_vote = next(v for v in votes if not v.passed)
            if failing_vote.confidence >= 0.9:
                blocked = True
                passed = False
                logger.warning(
                    f"AutoDefense précaution: {failing_vote.validator} "
                    f"confiance {failing_vote.confidence:.0%}"
                )

        consensus = max(pass_count, fail_count) / len(votes)

        result = AutoDefenseResult(
            passed=passed and not blocked,
            blocked=blocked,
            votes=votes,
            consensus=consensus,
            category="autodefense",
            reason=self._build_reason(votes, blocked),
        )

        if blocked:
            logger.warning(f"AutoDefense BLOCAGE: {result.reason}")
        else:
            logger.debug(f"AutoDefense PASS: consensus {consensus:.0%}")

        return result

    def _build_reason(self, votes: list[DefenseVote], blocked: bool) -> str:
        """Construire un résumé lisible du résultat"""
        if not blocked:
            return "Consensus: contenu sûr"
        failures = [v for v in votes if not v.passed]
        return f"Bloqué par {len(failures)}/{len(votes)} validateurs: " + \
               "; ".join(f"{v.validator} ({v.reason})" for v in failures)


# Singleton
autodefense = AutoDefense()
