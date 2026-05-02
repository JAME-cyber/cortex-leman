"""
Cortex Leman v5 — Insight 4: OpenTelemetry Distributed Tracing

Inspiré du blog AG2 "Tracing in an Agentic World"
Ajoute distributed tracing aux flux multi-agents pour:
  - Visualiser le graphe d'exécution complet
  - Mesurer la latence par agent
  - Debug les problèmes de performance
  - Corréler les spans entre agents

Utilise OpenTelemetry SDK (opentelemetry-api, opentelemetry-sdk).
Si non installé, degrade gracieusement en no-op.
"""
import time
import logging
import functools
from typing import Optional, Callable
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Try to import OpenTelemetry, degrade gracefully
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
    from opentelemetry.sdk.resources import Resource

    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False

# Tracer global
_tracer: Optional[object] = None


def setup_tracing(service_name: str = "cortex-leman-v5") -> None:
    """
    Initialiser le tracing OpenTelemetry.
    En production: utiliser OTLP exporter vers Jaeger/Zipkin.
    En dev: ConsoleSpanExporter.
    """
    global _tracer

    if not _OTEL_AVAILABLE:
        logger.info("OpenTelemetry non disponible — tracing désactivé")
        return

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    # Console exporter pour dev
    console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(console_exporter))

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer("cortex-leman", "5.0.0")

    logger.info(f"OpenTelemetry tracing activé: {service_name}")


def get_tracer():
    """Récupérer le tracer global"""
    return _tracer


@contextmanager
def trace_span(name: str, attributes: dict = None):
    """
    Context manager pour créer un span de tracing.

    Usage:
        with trace_span("agent.reasoning.process") as span:
            # ... work ...
            if span:
                span.set_attribute("query.length", len(query))

    Si OpenTelemetry n'est pas disponible, c'est un no-op.
    """
    if _tracer and _OTEL_AVAILABLE:
        with _tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))
            yield span
    else:
        yield None


def trace_agent(agent_name: str):
    """
    Décorateur pour tracer un appel d'agent.

    Usage:
        @trace_agent("reasoning")
        def process(self, intention):
            ...

    Ajoute automatiquement:
      - Span avec nom de l'agent
      - Attributs: agent.name, agent.vertical
      - Métriques: durée, statut
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            span_name = f"agent.{agent_name}.{func.__name__}"

            # Extraire le vertical si possible (intention en argument)
            vertical = "unknown"
            if len(args) > 1 and hasattr(args[1], 'vertical'):
                vertical = args[1].vertical
            elif 'intention' in kwargs and hasattr(kwargs['intention'], 'vertical'):
                vertical = kwargs['intention'].vertical

            attrs = {
                "agent.name": agent_name,
                "agent.function": func.__name__,
                "agent.vertical": vertical,
            }

            start = time.monotonic()
            with trace_span(span_name, attrs) as span:
                try:
                    result = func(*args, **kwargs)
                    if span:
                        span.set_attribute("agent.status", "success")
                    return result
                except Exception as e:
                    if span:
                        span.set_attribute("agent.status", "error")
                        span.set_attribute("agent.error", str(e))
                    raise
                finally:
                    elapsed = time.monotonic() - start
                    if span:
                        span.set_attribute("agent.duration_ms", round(elapsed * 1000, 2))

        return wrapper
    return decorator


@contextmanager
def trace_guardrail(guardrail_name: str, direction: str = "input"):
    """
    Context manager pour tracer un guardrail.

    Usage:
        with trace_guardrail("pii", "input") as span:
            result = check_pii(content)
            if span:
                span.set_attribute("guard.violations", len(result.violations))
    """
    with trace_span(f"guardrail.{guardrail_name}.{direction}") as span:
        if span:
            span.set_attribute("guardrail.name", guardrail_name)
            span.set_attribute("guardrail.direction", direction)
        yield span


@contextmanager
def trace_intention_transition(intention_id: str, from_state: str, to_state: str):
    """
    Context manager pour tracer une transition d'état d'intention.
    """
    with trace_span("stateflow.transition") as span:
        if span:
            span.set_attribute("intention.id", intention_id[:8])
            span.set_attribute("state.from", from_state)
            span.set_attribute("state.to", to_state)
        yield span


def trace_mediator_decision(rule_id: str, decision: str, vertical: str):
    """
    Tracer une décision du médiateur (event, pas span).
    """
    with trace_span("mediator.decide") as span:
        if span:
            span.set_attribute("mediator.rule", rule_id)
            span.set_attribute("mediator.decision", decision)
            span.set_attribute("mediator.vertical", vertical)


# Auto-setup si possible (lazy)
def ensure_tracing():
    """S'assurer que le tracing est initialisé"""
    global _tracer
    if _tracer is None and _OTEL_AVAILABLE:
        setup_tracing()
