"""
Cortex Leman v5 — Observabilité

Modules:
1. tracing.py — OpenTelemetry tracing sur le bus NATS
2. observe_skill.py — Dashboard + drift detection depuis le WORM
3. eval_router.py — Routeur d'évaluations par vertical (inspiration Laurie Voss / Arize)
4. golden_dataset.py — Dataset dynamique de cas de test
5. rule_experiment.py — Framework d'expériences sur les règles JsonLogic
6. judge_adversarial.py — Red teaming des rubrics d'évaluation
"""

from core.observability.tracing import (
    CortexTracer,
    CortexSpan,
    SpanKind,
    SpanStatus,
    ConsoleExporter,
    WORMExporter,
    OTLPExporter,
    TraceAnalytics,
    tracer,
)

from core.observability.observe_skill import (
    ObserveSkill,
    ObserveDashboard,
    DriftSignal,
    observe_skill,
)

from core.observability.eval_router import (
    EvalRouter,
    EvalRubric,
    EvalResult,
    EvalKind,
    EvalSeverity,
    eval_router,
)

from core.observability.golden_dataset import (
    GoldenDataset,
    GoldenCase,
    DatasetStats,
    CaseOrigin,
    CaseLabel,
    DataSplit,
    golden_dataset,
    seed_default_dataset,
)

from core.observability.rule_experiment import (
    RuleExperiment,
    RuleChange,
    ExperimentReport,
    ExperimentResult,
    ExperimentStatus,
    ChangeType,
    rule_experiment,
)

from core.observability.judge_adversarial import (
    JudgeAdversarialTest,
    JudgeAttack,
    JudgeTestResult,
    JudgeAdversarialReport,
    JudgeAttackType,
    JudgeVulnerability,
    judge_adversarial,
)

from core.observability.compliance_skill import (
    ComplianceSkill,
    SkillRegistry,
    SkillDomain,
    SkillConfidence,
    SkillGuide,
    skill_registry,
    seed_skills,
)

from core.observability.auto_approver import (
    AutoApprover,
    ApprovalRequest,
    ApprovalResult,
    ApprovalDecision,
    ApprovalRisk,
    BacktestResult,
    auto_approver,
)

from core.observability.session_miner import (
    SessionMiner,
    MiningReport,
    SkillMetrics,
    FailurePattern,
    DarkCorner,
    session_miner,
)

__all__ = [
    # Tracing
    "CortexTracer", "CortexSpan", "SpanKind", "SpanStatus",
    "ConsoleExporter", "WORMExporter", "OTLPExporter", "TraceAnalytics", "tracer",
    # Observe
    "ObserveSkill", "ObserveDashboard", "DriftSignal", "observe_skill",
    # Eval Router
    "EvalRouter", "EvalRubric", "EvalResult", "EvalKind", "EvalSeverity", "eval_router",
    # Golden Dataset
    "GoldenDataset", "GoldenCase", "DatasetStats", "CaseOrigin", "CaseLabel",
    "DataSplit", "golden_dataset", "seed_default_dataset",
    # Rule Experiment
    "RuleExperiment", "RuleChange", "ExperimentReport", "ExperimentResult",
    "ExperimentStatus", "ChangeType", "rule_experiment",
    # Judge Adversarial
    "JudgeAdversarialTest", "JudgeAttack", "JudgeTestResult",
    "JudgeAdversarialReport", "JudgeAttackType", "JudgeVulnerability", "judge_adversarial",
    # Compliance Skill (Intercom inspiration)
    "ComplianceSkill", "SkillRegistry", "SkillDomain", "SkillConfidence",
    "SkillGuide", "skill_registry", "seed_skills",
    # Auto Approver (Intercom inspiration)
    "AutoApprover", "ApprovalRequest", "ApprovalResult",
    "ApprovalDecision", "ApprovalRisk", "BacktestResult", "auto_approver",
    # Session Miner (Intercom inspiration)
    "SessionMiner", "MiningReport", "SkillMetrics",
    "FailurePattern", "DarkCorner", "session_miner",
]
