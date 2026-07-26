from __future__ import annotations

"""Defence-in-depth sanitisation for persistent agent memory.

This module treats memory as untrusted data. It does not attempt to determine
whether a document is factually correct; it only detects content that attempts
to alter agent behaviour or exfiltrate protected information.
"""

import base64
import binascii
import hashlib
import html
import logging
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

try:
    from core.journal.append_only_journal import journal
except Exception:  # pragma: no cover - allows isolated security testing
    journal = None


logger = logging.getLogger(__name__)
Action = Literal["allow", "quarantine", "block"]


@dataclass(frozen=True)
class Threat:
    category: str
    pattern: str
    evidence: str
    severity: float


@dataclass(frozen=True)
class SanitizeResult:
    clean_content: str
    is_safe: bool
    threats_found: list[Threat]
    risk_score: float
    action: Action


@dataclass
class AuditReport:
    files_scanned: int = 0
    files_with_threats: int = 0
    threats_found: list[Threat] = field(default_factory=list)
    findings: dict[str, list[Threat]] = field(default_factory=dict)


class MemorySanitizer:
    """Detect and neutralise instruction-bearing content in agent memory.

    The sanitizer is intentionally conservative. Content that looks suspicious
    is retained only inside explicit data markers; blocked content is removed
    from the prompt-facing representation entirely.
    """

    _PATTERNS: tuple[tuple[str, str, float], ...] = (
        ("instruction_override", r"\b(?:SYSTEM|DEVELOPER|ASSISTANT|USER)\s*:\s*", 0.72),
        ("instruction_override", r"\bIMPORTANT\s*:\s*", 0.52),
        ("instruction_override", r"\b(?:you\s+must|you\s+should|always\s+do|do\s+not)\b", 0.58),
        ("instruction_override", r"\b(?:à\s+partir\s+de\s+maintenant|nouvelles\s+instructions)\b", 0.68),
        ("persona_hijacking", r"\b(?:act\s+as|pretend\s+to\s+be|you\s+are\s+now)\b", 0.67),
        ("persona_hijacking", r"\b(?:tu\s+es\s+maintenant|tu\s+n['’]es\s+plus)\b", 0.67),
        ("rule_suppression", r"\b(?:ignore|disregard|forget)\s+(?:all\s+)?(?:your\s+)?(?:rules|instructions|safety|policies|previous)\b", 0.82),
        ("rule_suppression", r"\b(?:ignore\s+tes\s+consignes|oublie\s+les\s+règles|ignorez\s+vos\s+consignes)\b", 0.82),
        ("exfiltration", r"\b(?:output|print|reveal|show|give)\s+(?:the\s+)?(?:system\s+prompt|hidden\s+prompt|secrets?|credentials?|API\s*keys?|passwords?)\b", 0.88),
        ("exfiltration", r"\b(?:envoie\s+à|transmets|r[eé]vèle|affiche)\b.{0,100}\b(?:prompt|secret|mot\s+de\s+passe|identifiants?|cl[ée]s?)\b", 0.88),
        ("credential_leak", r"\b(?:API_?KEY|SECRET|TOKEN|PASSWORD)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{16,}", 0.90),
        ("credential_leak", r"\b(?:export\s+|set\s+)(?:API_?KEY|SECRET|TOKEN|PASSWORD)\b", 0.85),
        ("network_exfiltration", r"\b(?:curl|wget|fetch|http\.get)\s+https?://(?!localhost|127\.0\.0\.1)", 0.82),
    )

    _COMPILED = tuple(
        (category, re.compile(pattern, re.IGNORECASE | re.UNICODE), severity)
        for category, pattern, severity in _PATTERNS
    )
    _ZW_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060\u2061\u2066-\u2069\ufeff]")
    _HTML_COMMENT_RE = re.compile(r"<!--(.*?)-->", re.IGNORECASE | re.DOTALL)
    _BASE64_RE = re.compile(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{24,}={0,2}(?![A-Za-z0-9+/])")
    _CONFUSABLES = frozenset(
        "аɑссеԁԛһіјӏոоорѕԝухьΑΒΕΖΗΙΚΜΝΟΡΤΥΧΥа"
    )

    _QUARANTINE_START = "[QUARANTINED-CONTENT]"
    _QUARANTINE_END = "[/QUARANTINED-CONTENT]"

    def sanitize_for_storage(self, content: str, source: str = "") -> SanitizeResult:
        """Sanitise content before it is persisted in any memory store."""
        result = self._sanitize(content, context=f"storage:{source}")
        self._journal("memory_sanitized_for_storage", source, result)
        return result

    def sanitize_for_retrieval(self, content: str, context: str = "") -> SanitizeResult:
        """Sanitise content immediately before prompt construction."""
        result = self._sanitize(content, context=f"retrieval:{context}")
        self._journal("memory_sanitized_for_retrieval", context, result)
        return result

    def audit_memory_store(self, store_path: Path) -> AuditReport:
        """Scan existing regular files without modifying them."""
        report = AuditReport()
        path = Path(store_path)
        paths = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]
        for candidate in paths:
            try:
                content = candidate.read_text(encoding="utf-8", errors="replace")
                report.files_scanned += 1
                result = self._sanitize(content, context=f"audit:{candidate}", emit=False)
                if result.threats_found:
                    report.files_with_threats += 1
                    report.threats_found.extend(result.threats_found)
                    report.findings[str(candidate)] = result.threats_found
                    self._journal("memory_audit_finding", str(candidate), result)
            except (OSError, UnicodeError) as exc:
                logger.warning("Unable to audit memory file %s: %s", candidate, exc)
        return report

    def _sanitize(self, content: str, context: str, emit: bool = True) -> SanitizeResult:
        if not isinstance(content, str):
            raise TypeError("content must be a string")

        threats: list[Threat] = []
        seen: set[tuple[str, str]] = set()

        def add(category: str, pattern: str, evidence: str, severity: float) -> None:
            key = (category, evidence[:160])
            if key not in seen:
                seen.add(key)
                threats.append(Threat(category, pattern, evidence[:200], severity))

        for category, regex, severity in self._COMPILED:
            for match in regex.finditer(content):
                add(category, regex.pattern, match.group(0), severity)

        for match in self._ZW_RE.finditer(content):
            add("hidden_unicode", "zero-width/bidi control", repr(match.group(0)), 0.75)

        confusable_chars = sorted(set(content) & self._CONFUSABLES)
        if confusable_chars:
            add("homoglyph", "confusable Unicode characters", "".join(confusable_chars), 0.55)

        for match in self._HTML_COMMENT_RE.finditer(content):
            comment = html.unescape(match.group(1)).strip()
            if self._looks_instructional(comment):
                add("instruction_smuggling", "HTML comment containing instructions", comment, 0.82)

        for match in self._BASE64_RE.finditer(content):
            decoded = self._decode_base64(match.group(0))
            if decoded and self._looks_instructional(decoded):
                add("instruction_smuggling", "base64-encoded instruction", decoded, 0.86)

        risk = min(1.0, max((t.severity for t in threats), default=0.0) + max(0, len(threats) - 1) * 0.06)
        if not threats:
            action: Action = "allow"
            clean = content
        elif risk >= 0.86:
            action = "block"
            clean = "[BLOCKED-CONTENT: suspected prompt injection removed]"
        else:
            action = "quarantine"
            clean = f"{self._QUARANTINE_START}\n{content}\n{self._QUARANTINE_END}"
        result = SanitizeResult(clean, action == "allow", threats, round(risk, 4), action)
        if emit:
            logger.info("Memory sanitization: context=%s action=%s risk=%.3f", context, action, risk)
        return result

    @staticmethod
    def _looks_instructional(value: str) -> bool:
        lowered = value.casefold()
        terms = (
            "ignore", "system", "prompt", "instruction", "you must", "act as",
            "reveal", "output", "oublie", "consigne", "tu es", "envoie", "transmets",
        )
        return any(term in lowered for term in terms)

    @staticmethod
    def _decode_base64(value: str) -> str | None:
        try:
            decoded = base64.b64decode(value, validate=True)
            text = decoded.decode("utf-8")
            return text if len(text) <= 4096 else None
        except (binascii.Error, UnicodeDecodeError, ValueError):
            return None

    @staticmethod
    def _journal(event: str, source: str, result: SanitizeResult) -> None:
        payload = {
            "event": event,
            "source": source,
            "action": result.action,
            "risk_score": result.risk_score,
            "threat_categories": sorted({t.category for t in result.threats_found}),
            "content_sha256": hashlib.sha256(result.clean_content.encode("utf-8")).hexdigest(),
        }
        try:
            if journal is not None:
                from core.journal.models import JournalEventType
                journal.append(
                    event_type=JournalEventType.AGENT_RESULT,
                    client_id="system",
                    vertical="all",
                    agent_source="memory_sanitizer",
                    intention_id=event,
                    payload=payload,
                )
        except Exception:  # audit logging must never make sanitisation fail
            logger.exception("Unable to append memory sanitization event to journal")
