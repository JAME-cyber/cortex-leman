"""
conftest.py — Fixtures partagées pour les tests observabilité.

Isolation garantie: chaque test reçoit un contexte frais.
Pas de contamination entre tests.
"""
import pytest


@pytest.fixture
def ctx():
    """
    Contexte d'observabilité frais pour chaque test.
    Pas de contamination entre tests.
    """
    from core.observability.context import ObservabilityContext
    context = ObservabilityContext(seed=True)
    yield context
    context.reset_all()


@pytest.fixture
def eval_router(ctx):
    """EvalRouter isolé."""
    return ctx.eval_router


@pytest.fixture
def golden_dataset(ctx):
    """GoldenDataset isolé."""
    return ctx.golden_dataset


@pytest.fixture
def skill_registry(ctx):
    """SkillRegistry isolé avec skills par défaut."""
    return ctx.skill_registry


@pytest.fixture
def auto_approver(ctx):
    """AutoApprover isolé."""
    return ctx.auto_approver


@pytest.fixture
def session_miner(ctx):
    """SessionMiner isolé."""
    return ctx.session_miner
