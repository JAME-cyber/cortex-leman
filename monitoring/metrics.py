"""Cortex Leman v5 — Prometheus Metrics

Métriques exposées sur /metrics pour monitoring.
"""
import time
import logging
from typing import Optional

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

logger = logging.getLogger(__name__)

# Registry dédié (pas global pour éviter les collisions en test)
registry = CollectorRegistry()

# ── Compteurs ──────────────────────────────────────────────

http_requests_total = Counter(
    "cortex_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry,
)

auth_attempts_total = Counter(
    "cortex_auth_attempts_total",
    "Authentication attempts",
    ["method", "result"],  # method: jwt|api_key, result: success|failure
    registry=registry,
)

intentions_total = Counter(
    "cortex_intentions_total",
    "Intentions created",
    ["vertical", "status"],
    registry=registry,
)

llm_calls_total = Counter(
    "cortex_llm_calls_total",
    "LLM API calls",
    ["provider", "model", "result"],  # result: success|error|guardrail_blocked
    registry=registry,
)

arbitrations_total = Counter(
    "cortex_arbitrations_total",
    "Arbitration decisions",
    ["decision"],  # approve|reject|modify
    registry=registry,
)

mediator_freezes_total = Counter(
    "cortex_mediator_freezes_total",
    "Preventive freezes by mediator",
    ["vertical", "rule_id"],
    registry=registry,
)

guardrail_blocks_total = Counter(
    "cortex_guardrail_blocks_total",
    "Guardrail blocks",
    ["guard_type", "vertical"],  # pii|topic|output
    registry=registry,
)

# ── Histogrammes ───────────────────────────────────────────

llm_latency_seconds = Histogram(
    "cortex_llm_latency_seconds",
    "LLM response latency",
    ["provider"],
    buckets=(0.5, 1, 2, 5, 10, 30, 60, 120),
    registry=registry,
)

agent_processing_seconds = Histogram(
    "cortex_agent_processing_seconds",
    "Agent processing time",
    ["agent_name"],
    buckets=(0.1, 0.5, 1, 2, 5, 10),
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "cortex_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
    registry=registry,
)

# ── Jauges ─────────────────────────────────────────────────

active_intentions = Gauge(
    "cortex_active_intentions",
    "Currently active intentions",
    ["vertical"],
    registry=registry,
)

pending_arbitrations = Gauge(
    "cortex_pending_arbitrations",
    "Arbitrations awaiting human decision",
    registry=registry,
)

circuit_breaker_state = Gauge(
    "cortex_circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 0.5=half-open)",
    ["agent"],
    registry=registry,
)

rag_chunks_indexed = Gauge(
    "cortex_rag_chunks_indexed",
    "Total RAG chunks indexed",
    ["collection"],
    registry=registry,
)

# ── Info ───────────────────────────────────────────────────

app_info = Info(
    "cortex_app",
    "Application information",
    registry=registry,
)

# Initialize app info
app_info.info({
    "version": "5.0.0",
    "mode": "standard",
})


class MetricsMiddleware:
    """FastAPI middleware for automatic metrics collection"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET")
        path = scope.get("path", "/unknown")

        start_time = time.time()

        async def send_with_metrics(message):
            if message["type"] == "http.response.start":
                status = message.get("status", 200)
                http_requests_total.labels(
                    method=method, endpoint=path, status=status
                ).inc()
            await send(message)

        await self.app(scope, receive, send_with_metrics)

        duration = time.time() - start_time
        http_request_duration_seconds.labels(
            method=method, endpoint=path
        ).observe(duration)


def get_metrics() -> tuple[bytes, str]:
    """Génère les métriques Prometheus au format texte"""
    return generate_latest(registry), CONTENT_TYPE_LATEST


def record_llm_call(
    provider: str,
    model: str,
    result: str,
    latency: float,
    tokens: int = 0,
):
    """Enregistre un appel LLM"""
    llm_calls_total.labels(
        provider=provider, model=model, result=result
    ).inc()
    llm_latency_seconds.labels(provider=provider).observe(latency)


def record_agent_processing(agent_name: str, duration: float):
    """Enregistre le temps de traitement d'un agent"""
    agent_processing_seconds.labels(agent_name=agent_name).observe(duration)


def record_auth(method: str, result: str):
    """Enregistre une tentative d'auth"""
    auth_attempts_total.labels(method=method, result=result).inc()


def record_intention(vertical: str, status: str):
    """Enregistre une intention"""
    intentions_total.labels(vertical=vertical, status=status).inc()
