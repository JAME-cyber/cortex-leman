"""
Couche adoption Cortex Leman v5.

Objectif : accélérer l'onboarding, les démos et le démarrage par templates sans
affaiblir le moat de confiance : Médiateur déterministe, journal WORM hash-chaîné,
mode Haute Protection et arbitrage humain restent obligatoires.
"""

from .demo_pack import DemoPack, DemoStep, generate_demo
from .freemium import FreemiumSandbox, QuotaExceededError, QuotaPolicy, QuotaUsage, SandboxRecord
from .onboarding import ArbitrationExample, OnboardingEnvironment, SandboxAccount, quickstart, quickstart_sync
from .templates import AppliedTemplate, BusinessTemplate, TemplateRegistry

__all__ = [
    "AppliedTemplate",
    "ArbitrationExample",
    "BusinessTemplate",
    "DemoPack",
    "DemoStep",
    "FreemiumSandbox",
    "OnboardingEnvironment",
    "QuotaExceededError",
    "QuotaPolicy",
    "QuotaUsage",
    "SandboxAccount",
    "SandboxRecord",
    "TemplateRegistry",
    "generate_demo",
    "quickstart",
    "quickstart_sync",
]
