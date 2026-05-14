"""
Cortex Leman v5 — Code Reviewer (inspired by agent-skills code-reviewer.md)

Agent de review des décisions et outputs des 5 agents Cortex.
Utilisé par le Médiateur pour évaluer la qualité avant validation.

5 Dimensions (adaptées Cortex):
  1. Correctness — La sortie est-elle correcte factuellement?
  2. Readability — Le résultat est-il compréhensible par un humain?
  3. Architecture — Suit-il les patterns Cortex?
  4. Security — Conforme au security-auditor?
  5. Performance — Efficace et non-redondant?

Sévérité des findings:
  CRITICAL → Bloque la validation (dossier arbitration)
  IMPORTANT → Corriger avant validation
  SUGGESTION → Amélioration optionnelle

Usage:
    reviewer = CodeReviewer()
    report = reviewer.review(agent_id, agent_output, context)
    if report.verdict == ReviewVerdict.REQUEST_CHANGES:
        # Médiateur déclenche un gel
        pass
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ReviewVerdict(str, Enum):
    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    NEEDS_ARBITRATION = "NEEDS_ARBITRATION"


class FindingSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    IMPORTANT = "IMPORTANT"
    SUGGESTION = "SUGGESTION"


class ReviewDimension(str, Enum):
    CORRECTNESS = "correctness"
    READABILITY = "readability"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class ReviewFinding:
    dimension: ReviewDimension
    severity: FindingSeverity
    title: str
    description: str
    recommendation: str
    location: str = ""


@dataclass
class ReviewReport:
    agent_id: str
    timestamp: str
    verdict: ReviewVerdict
    findings: list[ReviewFinding] = field(default_factory=list)
    positives: list[str] = field(default_factory=list)
    summary: str = ""
    
    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "verdict": self.verdict.value,
            "summary": self.summary,
            "findings_count": len(self.findings),
            "critical": sum(1 for f in self.findings if f.severity == FindingSeverity.CRITICAL),
            "important": sum(1 for f in self.findings if f.severity == FindingSeverity.IMPORTANT),
            "suggestions": sum(1 for f in self.findings if f.severity == FindingSeverity.SUGGESTION),
            "positives": self.positives,
            "findings": [
                {
                    "dimension": f.dimension.value,
                    "severity": f.severity.value,
                    "title": f.title,
                    "description": f.description,
                    "recommendation": f.recommendation,
                }
                for f in self.findings
            ],
        }


class CodeReviewer:
    """
    Reviewer de qualité pour les outputs des agents Cortex.
    
    Adapté du persona code-reviewer.md (agent-skills).
    Évalue sur 5 dimensions avec verdict binaire.
    """
    
    def review(self, agent_id: str, output: dict, context: dict = None) -> ReviewReport:
        """
        Review complète d'un output agent.
        
        Args:
            agent_id: Identifiant de l'agent (data, reasoning, action, narrative, oeil)
            output: Sortie de l'agent à reviewer
            context: Contexte additionnel (intention, conversation, etc.)
        """
        report = ReviewReport(
            agent_id=agent_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            verdict=ReviewVerdict.APPROVE,
            findings=[],
            positives=[],
        )
        
        context = context or {}
        
        # 1. Correctness
        self._check_correctness(agent_id, output, context, report)
        
        # 2. Readability
        self._check_readability(output, report)
        
        # 3. Architecture
        self._check_architecture(agent_id, output, report)
        
        # 4. Security (delegate to security_auditor)
        self._check_security(output, report)
        
        # 5. Performance
        self._check_performance(agent_id, output, report)
        
        # Calcul du verdict
        critical = sum(1 for f in report.findings if f.severity == FindingSeverity.CRITICAL)
        important = sum(1 for f in report.findings if f.severity == FindingSeverity.IMPORTANT)
        
        if critical > 0:
            report.verdict = ReviewVerdict.NEEDS_ARBITRATION
            report.summary = f"{critical} problème(s) critique(s) — arbitration humaine requise"
        elif important > 2:
            report.verdict = ReviewVerdict.REQUEST_CHANGES
            report.summary = f"{important} problème(s) important(s) — corrections requises"
        elif important > 0:
            report.verdict = ReviewVerdict.APPROVE
            report.summary = f"Approuvé avec {important} suggestion(s) d'amélioration"
        else:
            report.summary = "Approuvé sans réserve"
        
        return report
    
    # ── Dimension 1: Correctness ───────────────────────────
    
    def _check_correctness(self, agent_id: str, output: dict, context: dict, report: ReviewReport):
        """Vérifie l'exactitude factuelle et logique"""
        
        # Données vides ou manquantes
        if not output:
            report.findings.append(ReviewFinding(
                dimension=ReviewDimension.CORRECTNESS,
                severity=FindingSeverity.CRITICAL,
                title="Output vide",
                description=f"Agent {agent_id} a retourné un output vide",
                recommendation="L'agent doit toujours produire un output structuré",
            ))
            return
        
        # Confidence score manquant
        if "confidence" not in output and "score" not in output:
            report.findings.append(ReviewFinding(
                dimension=ReviewDimension.CORRECTNESS,
                severity=FindingSeverity.IMPORTANT,
                title="Pas de score de confiance",
                description="L'output ne contient pas de confidence score",
                recommendation="Ajouter un champ confidence (0.0-1.0) à tout output",
            ))
        elif "confidence" in output:
            conf = output["confidence"]
            if isinstance(conf, (int, float)) and conf < 0.5:
                report.findings.append(ReviewFinding(
                    dimension=ReviewDimension.CORRECTNESS,
                    severity=FindingSeverity.IMPORTANT,
                    title="Confiance trop basse",
                    description=f"Score de confiance = {conf} (< 0.5 seuil)",
                    recommendation="Ne pas valider un output avec confiance < 0.5",
                ))
            report.positives.append("Score de confiance présent et valide")
        
        # Contradictions avec le contexte
        if context and "intention" in context:
            intention_type = context["intention"].get("type", "")
            output_type = output.get("type", "")
            if intention_type and output_type and intention_type != output_type:
                report.findings.append(ReviewFinding(
                    dimension=ReviewDimension.CORRECTNESS,
                    severity=FindingSeverity.IMPORTANT,
                    title="Type d'output ≠ intention",
                    description=f"Intention: {intention_type}, Output: {output_type}",
                    recommendation="L'output doit correspondre au type d'intention",
                ))
        
        # Sources/references check (pour agents research)
        if agent_id in ("data", "oeil") and "sources" not in output:
            report.findings.append(ReviewFinding(
                dimension=ReviewDimension.CORRECTNESS,
                severity=FindingSeverity.IMPORTANT,
                title="Pas de sources citées",
                description=f"Agent {agent_id} ne cite pas ses sources",
                recommendation="Toute donnée factuelle doit avoir une source vérifiable",
            ))
        elif "sources" in output and output["sources"]:
            report.positives.append(f"Sources citées: {len(output['sources'])} référence(s)")
    
    # ── Dimension 2: Readability ───────────────────────────
    
    def _check_readability(self, output: dict, report: ReviewReport):
        """Vérifie la lisibilité pour un humain"""
        
        # Texte trop long
        output_str = str(output)
        if len(output_str) > 10000:
            report.findings.append(ReviewFinding(
                dimension=ReviewDimension.READABILITY,
                severity=FindingSeverity.SUGGESTION,
                title="Output très long",
                description=f"{len(output_str)} caractères — risque de surcharge cognitive",
                recommendation="Structurer avec des sections, résumer si > 5000 chars",
            ))
        
        # Pas de résumé
        if "summary" not in output and "resume" not in output:
            report.findings.append(ReviewFinding(
                dimension=ReviewDimension.READABILITY,
                severity=FindingSeverity.SUGGESTION,
                title="Pas de résumé",
                description="L'output ne contient pas de résumé exécutif",
                recommendation="Ajouter un champ 'summary' en début d'output",
            ))
        else:
            report.positives.append("Résumé exécutif présent")
        
        # Jargon technique excessif
        if output_str.count("__") > 5 or output_str.count("::") > 3:
            report.positives.append("Output bien structuré")
        elif output_str.count("NaN") > 0 or output_str.count("None") > 3:
            report.findings.append(ReviewFinding(
                dimension=ReviewDimension.READABILITY,
                severity=FindingSeverity.SUGGESTION,
                title="Valeurs brutes non formatées",
                description="Présence de NaN/None dans l'output visible",
                recommendation="Formater les valeurs: None → 'N/A', NaN → '—'",
            ))
    
    # ── Dimension 3: Architecture ──────────────────────────
    
    def _check_architecture(self, agent_id: str, output: dict, report: ReviewReport):
        """Vérifie le respect des patterns Cortex"""
        
        # Metadata requises
        required_meta = ["timestamp", "agent_id"]
        for meta in required_meta:
            if meta not in output:
                report.findings.append(ReviewFinding(
                    dimension=ReviewDimension.ARCHITECTURE,
                    severity=FindingSeverity.IMPORTANT,
                    title=f"Métadonnée manquante: {meta}",
                    description=f"Le champ '{meta}' est requis dans tout output Cortex",
                    recommendation=f"Ajouter '{meta}' automatiquement à la sortie de l'agent",
                ))
        
        # Agent ID cohérent
        if "agent_id" in output and output["agent_id"] != agent_id:
            report.findings.append(ReviewFinding(
                dimension=ReviewDimension.ARCHITECTURE,
                severity=FindingSeverity.CRITICAL,
                title="Agent ID incohérent",
                description=f"Attendu: {agent_id}, Trouvé: {output['agent_id']}",
                recommendation="L'agent_id dans l'output doit correspondre à l'agent qui l'a produit",
            ))
        
        # Trace ID pour corrélation
        if "trace_id" in output or "correlation_id" in output:
            report.positives.append("Trace/correlation ID présent")
        else:
            report.findings.append(ReviewFinding(
                dimension=ReviewDimension.ARCHITECTURE,
                severity=FindingSeverity.SUGGESTION,
                title="Pas de trace ID",
                description="L'output n'a pas de trace_id pour corrélation cross-agent",
                recommendation="Propager le trace_id du bus NATS dans chaque output",
            ))
    
    # ── Dimension 4: Security ──────────────────────────────
    
    def _check_security(self, output: dict, report: ReviewReport):
        """Délègue les checks sécurité au SecurityAuditor"""
        from core.security.auditor import security_auditor, Severity
        
        audit = security_auditor.audit_agent_output("review_check", output)
        
        for finding in audit.findings:
            # Mapper sévérité auditor → sévérité reviewer
            if finding.severity in (Severity.CRITICAL, Severity.HIGH):
                severity = FindingSeverity.CRITICAL
            elif finding.severity == Severity.MEDIUM:
                severity = FindingSeverity.IMPORTANT
            else:
                severity = FindingSeverity.SUGGESTION
            
            report.findings.append(ReviewFinding(
                dimension=ReviewDimension.SECURITY,
                severity=severity,
                title=f"[{finding.axis.value}] {finding.title}",
                description=finding.description,
                recommendation=finding.recommendation,
            ))
    
    # ── Dimension 5: Performance ───────────────────────────
    
    def _check_performance(self, agent_id: str, output: dict, report: ReviewReport):
        """Vérifie l'efficacité de l'output"""
        
        # Données dupliquées
        output_str = str(output)
        if "data" in output and isinstance(output.get("data"), dict):
            data_keys = list(output["data"].keys())
            if len(data_keys) != len(set(data_keys)):
                report.findings.append(ReviewFinding(
                    dimension=ReviewDimension.PERFORMANCE,
                    severity=FindingSeverity.SUGGESTION,
                    title="Clés dupliquées dans data",
                    description="Le champ data contient des clés en double",
                    recommendation="Dédupliquer les clés de data",
                ))
        
        # Output trop lourd
        if len(output_str) > 50000:
            report.findings.append(ReviewFinding(
                dimension=ReviewDimension.PERFORMANCE,
                severity=FindingSeverity.IMPORTANT,
                title="Output trop volumineux",
                description=f"{len(output_str)//1024}KB — impact sur le bus et les performances",
                recommendation="Compresser ou paginer les données volumineuses",
            ))
        
        # Temps de traitement
        if "processing_time_ms" in output:
            proc_time = output["processing_time_ms"]
            if isinstance(proc_time, (int, float)) and proc_time > 5000:
                report.findings.append(ReviewFinding(
                    dimension=ReviewDimension.PERFORMANCE,
                    severity=FindingSeverity.SUGGESTION,
                    title="Traitement lent",
                    description=f"{proc_time}ms — seuil recommandé < 5000ms",
                    recommendation="Optimiser ou mettre en cache les résultats",
                ))
            elif isinstance(proc_time, (int, float)):
                report.positives.append(f"Temps de traitement: {proc_time}ms")


# ── Instance singleton ────────────────────────────────────────

code_reviewer = CodeReviewer()
