"""
Cortex Leman v5 — Security Auditor (inspired by agent-skills security-auditor.md)

Agent spécialisé dans l'audit de sécurité pour les décisions Cortex.
Étend le Gardien des Normes avec un framework d'audit 5 axes.

Axes:
  1. Input Handling — Validation des données entrantes
  2. Auth & Access — Contrôle d'accès et identité
  3. Data Protection — Protection des données (RGPD/LPD)
  4. Infrastructure — Sécurité infra + dépendances
  5. Third-Party — Intégrations externes et webhooks

Sévérité (adaptée Cortex):
  CRITICAL → Gel immédiat (full freeze)
  HIGH     → Gel partiel (degraded freeze)
  MEDIUM   → Warning + log
  LOW      → Info + suivi
  INFO     → Bonne pratique

Usage:
    auditor = SecurityAuditor()
    report = auditor.audit_agent_output(agent_id, output_data)
    report = auditor.audit_integration(integration_config)
    report = auditor.audit_webhook(payload, signature)
"""
import hashlib
import hmac
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class AuditAxis(str, Enum):
    INPUT_HANDLING = "input_handling"
    AUTH_ACCESS = "auth_access"
    DATA_PROTECTION = "data_protection"
    INFRASTRUCTURE = "infrastructure"
    THIRD_PARTY = "third_party"


@dataclass
class Finding:
    """Un finding d'audit"""
    id: str
    severity: Severity
    axis: AuditAxis
    title: str
    description: str
    impact: str
    recommendation: str
    location: str = ""
    reference: str = ""  # RGPD Art., AI Act section, etc.
    cwe: str = ""  # CWE ID si applicable


@dataclass
class AuditReport:
    """Rapport d'audit complet"""
    target: str  # Ce qui a été audité
    timestamp: str
    findings: list[Finding] = field(default_factory=list)
    
    @property
    def summary(self) -> dict:
        counts = {s.value: 0 for s in Severity}
        for f in self.findings:
            counts[f.severity.value] += 1
        return counts
    
    @property
    def has_critical(self) -> bool:
        return any(f.severity == Severity.CRITICAL for f in self.findings)
    
    @property
    def has_high(self) -> bool:
        return any(f.severity == Severity.HIGH for f in self.findings)
    
    @property
    def freeze_recommended(self) -> str:
        """Recommandation de gel pour le Médiateur"""
        if self.has_critical:
            return "FULL_FREEZE"
        elif self.has_high:
            return "DEGRADED_FREEZE"
        return "NONE"
    
    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "timestamp": self.timestamp,
            "freeze_recommended": self.freeze_recommended,
            "summary": self.summary,
            "findings": [
                {
                    "id": f.id,
                    "severity": f.severity.value,
                    "axis": f.axis.value,
                    "title": f.title,
                    "description": f.description,
                    "impact": f.impact,
                    "recommendation": f.recommendation,
                    "location": f.location,
                    "reference": f.reference,
                }
                for f in self.findings
            ],
        }


class SecurityAuditor:
    """
    Auditeur de sécurité pour Cortex Leman v5.
    
    Inspiré du persona security-auditor.md (agent-skills)
    Adapté pour le contexte FR-CH RGPD/AI Act/secret professionnel.
    """
    
    # Patterns dangereux dans les inputs
    INJECTION_PATTERNS = [
        (r";\s*(DROP|DELETE|INSERT|UPDATE|ALTER)\s", "SQL injection pattern"),
        (r"\$\{.*\}", "Template injection (SSTI)"),
        (r"<script[^>]*>", "XSS script tag"),
        (r"javascript:", "JavaScript protocol injection"),
        (r"\.\./", "Path traversal"),
        (r"__import__|exec\(|eval\(|os\.system", "Code injection Python"),
        (r"rm\s+-rf|sudo\s+", "Command injection"),
    ]
    
    # Données sensibles RGPD (Art. 9)
    SENSITIVE_DATA_PATTERNS = [
        (r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", "Date de naissance possible"),
        (r"\b\d{5}\b", "Code postal (géolocalisation indirecte)"),
        (r"\b[A-Z]{2}\d{9}[A-Z]{2}\b", "Numéro de passeport"),
        (r"\b\d{13}\b", "Numéro de sécurité sociale FR"),
        (r"\b[\w.-]+@[\w.-]+\.\w+\b", "Adresse email"),
        (r"\b\d{10,}\b", "Numéro de téléphone possible"),
        (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "Numéro de carte"),
    ]
    
    def __init__(self):
        self._finding_counter = 0
    
    def _next_id(self) -> str:
        self._finding_counter += 1
        return f"SA-{self._finding_counter:04d}"
    
    def audit_agent_output(self, agent_id: str, output: dict) -> AuditReport:
        """
        Audit complet de la sortie d'un agent Cortex.
        Utilisé par le Médiateur avant de valider/rejeter.
        """
        report = AuditReport(
            target=f"agent:{agent_id}",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        
        # 1. Input Handling
        self._check_input_handling(output, report)
        
        # 2. Auth & Access
        self._check_auth_access(agent_id, output, report)
        
        # 3. Data Protection (RGPD)
        self._check_data_protection(output, report)
        
        # 4. Infrastructure
        self._check_infrastructure(output, report)
        
        # 5. Third-Party
        self._check_third_party(output, report)
        
        return report
    
    def audit_webhook(self, payload: bytes, signature: str, secret: str) -> AuditReport:
        """Audit d'un webhook entrant"""
        report = AuditReport(
            target="webhook",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        
        # Vérifier la signature
        if secret:
            expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, signature):
                report.findings.append(Finding(
                    id=self._next_id(),
                    severity=Severity.CRITICAL,
                    axis=AuditAxis.THIRD_PARTY,
                    title="Signature webhook invalide",
                    description="Le payload ne correspond pas à la signature HMAC",
                    impact="Possible tentative d'injection ou replay attack",
                    recommendation="Rejeter le webhook. Vérifier le secret partagé.",
                    reference="OWASP API Security #8",
                ))
        
        # Vérifier le contenu
        try:
            data = json.loads(payload)
            self._check_input_handling(data, report)
            self._check_data_protection(data, report)
        except json.JSONDecodeError:
            report.findings.append(Finding(
                id=self._next_id(),
                severity=Severity.HIGH,
                axis=AuditAxis.INPUT_HANDLING,
                title="Payload JSON invalide",
                description="Le webhook payload n'est pas du JSON valide",
                impact="Erreur de parsing, possible attaque",
                recommendation="Rejeter le webhook malformé",
            ))
        
        return report
    
    def audit_integration(self, config: dict) -> AuditReport:
        """Audit d'une configuration d'intégration tierce"""
        report = AuditReport(
            target=f"integration:{config.get('name', 'unknown')}",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        
        # Vérifier les secrets
        api_key = config.get("api_key", "")
        if api_key and not api_key.startswith("${"):
            report.findings.append(Finding(
                id=self._next_id(),
                severity=Severity.HIGH,
                axis=AuditAxis.DATA_PROTECTION,
                title="Secret en dur dans la config",
                description=f"La clé API pour '{config.get('name')}' est en dur, pas dans env vars",
                impact="Fuite de secret via versioning ou logs",
                recommendation="Utiliser une variable d'environnement ou un vault",
                reference="RGPD Art. 32 (sécurité du traitement)",
            ))
        
        # Vérifier HTTPS
        url = config.get("url", "")
        if url and url.startswith("http://"):
            report.findings.append(Finding(
                id=self._next_id(),
                severity=Severity.HIGH,
                axis=AuditAxis.INFRASTRUCTURE,
                title="Connexion non chiffrée (HTTP)",
                description=f"L'intégration '{config.get('name')}' utilise HTTP au lieu de HTTPS",
                impact="Données transmises en clair, interception possible",
                recommendation="Migrer vers HTTPS",
                reference="RGPD Art. 32",
            ))
        
        # Vérifier le rate limiting
        if not config.get("rate_limit"):
            report.findings.append(Finding(
                id=self._next_id(),
                severity=Severity.MEDIUM,
                axis=AuditAxis.INFRASTRUCTURE,
                title="Pas de rate limiting",
                description=f"Intégration '{config.get('name')}' sans rate limiting",
                impact="Abus possible de l'API tierce",
                recommendation="Ajouter un rate limiter (circuit breaker)",
            ))
        
        return report
    
    # ── Checks internes ─────────────────────────────────────
    
    def _check_input_handling(self, data: dict, report: AuditReport):
        """Vérifie les patterns d'injection dans les données"""
        raw = json.dumps(data)
        
        for pattern, name in self.INJECTION_PATTERNS:
            if re.search(pattern, raw, re.IGNORECASE):
                report.findings.append(Finding(
                    id=self._next_id(),
                    severity=Severity.CRITICAL,
                    axis=AuditAxis.INPUT_HANDLING,
                    title=f"Pattern d'injection détecté: {name}",
                    description=f"Pattern {name} trouvé dans les données de l'agent",
                    impact="Exécution de code arbitraire ou injection de données",
                    recommendation="Sanitiser l'input avant traitement",
                    reference="OWASP Top 10 A03:2021",
                    cwe="CWE-79" if "XSS" in name else "CWE-89",
                ))
    
    def _check_auth_access(self, agent_id: str, data: dict, report: AuditReport):
        """Vérifie les problèmes d'authentification/autorisation"""
        # Vérifier si l'agent accède à des données hors scope
        tenant = data.get("tenant_id")
        if not tenant and "user_data" in str(data):
            report.findings.append(Finding(
                id=self._next_id(),
                severity=Severity.HIGH,
                axis=AuditAxis.AUTH_ACCESS,
                title="Données utilisateur sans tenant_id",
                description=f"Agent {agent_id} manipule des données user sans contexte tenant",
                impact="Possible accès non autorisé à des données d'un autre client",
                recommendation="Toujours valider le tenant_id avant accès données",
                reference="RGPD Art. 25 (protection by design)",
            ))
        
        # IDOR check
        if "resource_id" in data and "requested_by" in data:
            report.findings.append(Finding(
                id=self._next_id(),
                severity=Severity.MEDIUM,
                axis=AuditAxis.AUTH_ACCESS,
                title="Vérification IDOR nécessaire",
                description="Accès à une ressource par ID — vérifier l'appartenance",
                impact="IDOR — accès à données d'un autre utilisateur",
                recommendation="Valider resource_id ∈ user scope avant retour",
                reference="OWASP API #1 (BOLA)",
            ))
    
    def _check_data_protection(self, data: dict, report: AuditReport):
        """Vérifie la présence de données sensibles RGPD"""
        raw = json.dumps(data) if isinstance(data, dict) else str(data)
        
        for pattern, name in self.SENSITIVE_DATA_PATTERNS:
            matches = re.findall(pattern, raw)
            if matches:
                severity = Severity.HIGH if "carte" in name.lower() else Severity.MEDIUM
                report.findings.append(Finding(
                    id=self._next_id(),
                    severity=severity,
                    axis=AuditAxis.DATA_PROTECTION,
                    title=f"Donnée sensible détectée: {name}",
                    description=f"{len(matches)} occurrence(s) de {name} dans la sortie agent",
                    impact="Violation RGPD Art. 9 si données sensibles non chiffrées",
                    recommendation="Masquer/pseudonymiser les données sensibles dans les logs",
                    reference="RGPD Art. 5(1)(f) — minimisation + Art. 9 — données sensibles",
                ))
        
        # Vérifier si des données sont loggées en clair
        if "password" in raw.lower() or "secret" in raw.lower():
            report.findings.append(Finding(
                id=self._next_id(),
                severity=Severity.HIGH,
                axis=AuditAxis.DATA_PROTECTION,
                title="Secret/mot de passe potentiel dans les données",
                description="Le champ 'password' ou 'secret' apparaît dans les données",
                impact="Fuite de credentials via logs ou sortie agent",
                recommendation="Exclure les champs sensibles avant logging",
                reference="RGPD Art. 32 + OWASP A07:2021",
            ))
    
    def _check_infrastructure(self, data: dict, report: AuditReport):
        """Vérifie la sécurité infrastructure"""
        raw = json.dumps(data)
        
        # Stack trace dans la sortie?
        if "Traceback" in raw or "Exception" in raw or "Error:" in raw:
            report.findings.append(Finding(
                id=self._next_id(),
                severity=Severity.MEDIUM,
                axis=AuditAxis.INFRASTRUCTURE,
                title="Stack trace dans la sortie agent",
                description="Des détails d'erreur internes sont exposés dans la sortie",
                impact="Information disclosure — structure interne révélée",
                recommendation="Logger l'erreur côté serveur, retourner un message générique",
            ))
        
        # URLs internes exposées?
        if re.search(r"(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)", raw):
            report.findings.append(Finding(
                id=self._next_id(),
                severity=Severity.LOW,
                axis=AuditAxis.INFRASTRUCTURE,
                title="URL interne exposée",
                description="Une URL d'infrastructure interne apparaît dans la sortie",
                impact="Reconnaissance — aide un attaquant à cartographier l'infra",
                recommendation="Filtrer les URLs internes avant d'envoyer au client",
            ))
    
    def _check_third_party(self, data: dict, report: AuditReport):
        """Vérifie les risques liés aux intégrations tierces"""
        raw = json.dumps(data)
        
        # CDN/scripts tiers
        if re.search(r"<script\s+src=", raw):
            report.findings.append(Finding(
                id=self._next_id(),
                severity=Severity.MEDIUM,
                axis=AuditAxis.THIRD_PARTY,
                title="Script tiers chargé sans SRI",
                description="Un script externe est chargé sans integrity hash (SRI)",
                impact="Si le CDN est compromis, le script injecté s'exécute",
                recommendation="Ajouter un attribut integrity + crossorigin",
                reference="OWASP A08:2021",
            ))
        
        # OAuth state check
        if "oauth" in raw.lower() and "state" not in raw.lower():
            report.findings.append(Finding(
                id=self._next_id(),
                severity=Severity.HIGH,
                axis=AuditAxis.THIRD_PARTY,
                title="Flux OAuth sans paramètre state",
                description="Le flux OAuth détecté ne semble pas utiliser de paramètre state",
                impact="Vulnérabilité CSRF sur le flux OAuth",
                recommendation="Toujours utiliser un paramètre state aléatoire dans les flux OAuth",
                reference="RFC 6749 Section 10.12",
            ))


# ── Instance singleton ────────────────────────────────────────

security_auditor = SecurityAuditor()
