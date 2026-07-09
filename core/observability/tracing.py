"""
Cortex Leman v5 — OpenTelemetry Tracing sur le bus NATS

Corrélation bout-en-bout des spans pour chaque intention.
L'Orchestrateur crée le trace root, chaque agent crée un span enfant.

Export: OTLP (Jaeger/Tempo) ou console en dev.

Inspiré de: "Mind the Gap" — Amy Boyd & Nitya Narasimhan (Microsoft Foundry)
Adapté pour: bus NATS pair-à-pair + journal WORM hash-chainé
"""
import uuid
import time
import logging
import json
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class SpanKind(str, Enum):
    INTERNAL = "INTERNAL"
    CLIENT = "CLIENT"       # Appel sortant (ex: API externe)
    SERVER = "SERVER"       # Réception d'une requête
    PRODUCER = "PRODUCER"   # Publication sur le bus
    CONSUMER = "CONSUMER"   # Consommation depuis le bus


class SpanStatus(str, Enum):
    OK = "OK"
    ERROR = "ERROR"
    UNSET = "UNSET"


@dataclass
class CortexSpan:
    """Span OpenTelemetry adapté pour Cortex Leman"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    kind: SpanKind = SpanKind.INTERNAL
    status: SpanStatus = SpanStatus.UNSET
    start_time: float = 0.0
    end_time: float = 0.0
    attributes: dict = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)

    # Cortex-specific
    agent_source: str = ""
    intention_id: str = ""
    vertical: str = ""
    client_id: str = ""

    @property
    def duration_ms(self) -> float:
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0

    def set_status(self, status: SpanStatus, description: str = ""):
        self.status = status
        if description:
            self.attributes["status_description"] = description

    def set_attribute(self, key: str, value):
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict = None):
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {},
        })

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "kind": self.kind.value,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": round(self.duration_ms, 2),
            "attributes": self.attributes,
            "events": self.events,
            "agent_source": self.agent_source,
            "intention_id": self.intention_id,
            "vertical": self.vertical,
            "client_id": self.client_id,
        }


class CortexTracer:
    """
    Tracer Cortex Leman — fabrique et exporte les spans.

    Intégration:
    - BaseAgent.process() → auto-wrap dans un span
    - Mediator → span de vérification
    - Journal WORM → trace_id dans chaque entrée
    """

    def __init__(self, service_name: str = "cortex-leman-v5"):
        self.service_name = service_name
        self._exporters: list = []
        self._active_spans: dict[str, CortexSpan] = {}  # span_id → span

    def generate_trace_id(self) -> str:
        return uuid.uuid4().hex[:32]

    def generate_span_id(self) -> str:
        return uuid.uuid4().hex[:16]

    def start_span(
        self,
        operation_name: str,
        trace_id: str = None,
        parent_span_id: str = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: dict = None,
        agent_source: str = "",
        intention_id: str = "",
        vertical: str = "",
        client_id: str = "",
    ) -> CortexSpan:
        """Créer et démarrer un nouveau span"""
        span = CortexSpan(
            trace_id=trace_id or self.generate_trace_id(),
            span_id=self.generate_span_id(),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            kind=kind,
            start_time=time.time(),
            attributes=attributes or {},
            agent_source=agent_source,
            intention_id=intention_id,
            vertical=vertical,
            client_id=client_id,
        )
        self._active_spans[span.span_id] = span
        return span

    def end_span(self, span: CortexSpan, status: SpanStatus = SpanStatus.OK):
        """Terminer un span et l'exporter"""
        span.end_time = time.time()
        span.set_status(status)
        self._export_span(span)

        if span.span_id in self._active_spans:
            del self._active_spans[span.span_id]

    def _export_span(self, span: CortexSpan):
        """Exporter le span vers tous les exporteurs configurés"""
        span_dict = span.to_dict()

        for exporter in self._exporters:
            try:
                exporter.export(span_dict)
            except Exception as e:
                logger.warning(f"Tracer: erreur export span {span.span_id}: {e}")

    def add_exporter(self, exporter):
        """Ajouter un exporteur (ConsoleExporter, OTLPExporter, etc.)"""
        self._exporters.append(exporter)

    @asynccontextmanager
    async def trace_operation(
        self,
        operation_name: str,
        trace_id: str = None,
        parent_span_id: str = None,
        agent_source: str = "",
        intention_id: str = "",
        vertical: str = "",
        client_id: str = "",
        **extra_attrs,
    ):
        """Context manager pour tracer une opération asynchrone"""
        span = self.start_span(
            operation_name=operation_name,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            agent_source=agent_source,
            intention_id=intention_id,
            vertical=vertical,
            client_id=client_id,
            attributes=extra_attrs,
        )
        try:
            yield span
            self.end_span(span, SpanStatus.OK)
        except Exception as e:
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e)[:500])
            span.add_event("exception", {"exception.message": str(e)[:500]})
            self.end_span(span, SpanStatus.ERROR)
            raise

    def get_trace_context(self, span: CortexSpan) -> dict:
        """Extraire le contexte de trace pour propagation via NATS"""
        return {
            "trace_id": span.trace_id,
            "span_id": span.span_id,
            "parent_span_id": span.parent_span_id,
        }

    def inject_trace_context(self, payload: dict, span: CortexSpan) -> dict:
        """Injecter le contexte de trace dans un payload NATS"""
        if "_trace" not in payload:
            payload["_trace"] = {}
        payload["_trace"].update(self.get_trace_context(span))
        return payload

    def extract_trace_context(self, payload: dict) -> dict:
        """Extraire le contexte de trace d'un payload NATS"""
        return payload.get("_trace", {})

    def get_active_traces(self) -> dict:
        """Retourner les spans actifs (pour debugging)"""
        return {
            span_id: span.to_dict()
            for span_id, span in self._active_spans.items()
        }

    def get_trace_tree(self, trace_id: str) -> list[dict]:
        """Reconstruire l'arbre d'un trace (depuis les spans exportés)"""
        # Cette méthode sera utilisée par l'Observe Skill
        # Pour l'instant, retourne les spans actifs pour ce trace_id
        return [
            span.to_dict()
            for span in self._active_spans.values()
            if span.trace_id == trace_id
        ]


# === Exporters ===

class ConsoleExporter:
    """Exporte les spans vers la console (dev mode)"""

    def export(self, span_dict: dict):
        duration = span_dict.get("duration_ms", 0)
        agent = span_dict.get("agent_source", "?")
        op = span_dict.get("operation_name", "?")
        status = span_dict.get("status", "?")
        trace = span_dict.get("trace_id", "?")[:8]
        span = span_dict.get("span_id", "?")[:8]
        parent = span_dict.get("parent_span_id", "")[:8]

        tree = f"└── {parent} → {span}" if parent else f"■ {span}"
        logger.info(
            f"TRACE [{trace}] {tree} {agent}.{op} "
            f"{duration:.1f}ms [{status}]"
        )


class WORMExporter:
    """Exporte les spans dans le journal WORM Cortex Leman"""

    def export(self, span_dict: dict):
        try:
            from core.journal.append_only_journal import journal
            from core.journal.models import JournalEventType

            journal.append(
                event_type=JournalEventType.TRACE_SPAN,
                client_id=span_dict.get("client_id", "system"),
                vertical=span_dict.get("vertical", "system"),
                agent_source=span_dict.get("agent_source", "tracer"),
                intention_id=span_dict.get("intention_id", ""),
                payload=span_dict,
            )
        except Exception as e:
            logger.debug(f"WORMExporter: skip ({e})")


class OTLPExporter:
    """Exporte les spans au format OTLP (vers Jaeger/Tempo/Grafana)"""

    def __init__(self, endpoint: str = "http://localhost:4318/v1/traces"):
        self.endpoint = endpoint
        self._buffer: list[dict] = []
        self._max_buffer = 50

    def export(self, span_dict: dict):
        self._buffer.append(span_dict)
        if len(self._buffer) >= self._max_buffer:
            self._flush()

    def _flush(self):
        """Envoyer le buffer vers le collector OTLP"""
        if not self._buffer:
            return

        try:
            import requests
            # Format OTLP/JSON simplifié
            otlp_payload = {
                "resourceSpans": [{
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": "cortex-leman-v5"}}
                        ]
                    },
                    "scopeSpans": [{
                        "spans": [self._to_otlp(s) for s in self._buffer]
                    }]
                }]
            }

            resp = requests.post(
                self.endpoint,
                json=otlp_payload,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
            if resp.status_code in (200, 202):
                logger.debug(f"OTLP: {len(self._buffer)} spans exportés")
            self._buffer.clear()

        except Exception as e:
            logger.debug(f"OTLP export failed: {e}")
            # Ne pas vider le buffer — retry au prochain flush
            if len(self._buffer) > 200:
                self._buffer = self._buffer[-100:]  # Garder les 100 plus récents

    @staticmethod
    def _to_otlp(span: dict) -> dict:
        """Convertir un CortexSpan en format OTLP"""
        return {
            "traceId": span.get("trace_id", ""),
            "spanId": span.get("span_id", ""),
            "parentSpanId": span.get("parent_span_id", ""),
            "name": span.get("operation_name", "unknown"),
            "kind": {
                "INTERNAL": 1, "CLIENT": 3, "SERVER": 2,
                "PRODUCER": 4, "CONSUMER": 5,
            }.get(span.get("kind", "INTERNAL"), 1),
            "startTimeUnixNano": str(int(span.get("start_time", 0) * 1e9)),
            "endTimeUnixNano": str(int(span.get("end_time", 0) * 1e9)),
            "status": {
                "code": {
                    "OK": 1, "ERROR": 2, "UNSET": 0,
                }.get(span.get("status", "UNSET"), 0)
            },
            "attributes": [
                {"key": k, "value": {"stringValue": str(v)}}
                for k, v in span.get("attributes", {}).items()
            ] + [
                {"key": "cortex.agent_source", "value": {"stringValue": span.get("agent_source", "")}},
                {"key": "cortex.intention_id", "value": {"stringValue": span.get("intention_id", "")}},
                {"key": "cortex.vertical", "value": {"stringValue": span.get("vertical", "")}},
            ],
        }


# === Trace Analytics — pour l'Observe Skill ===

class TraceAnalytics:
    """
    Analytique des traces pour le dashboard observabilité.
    Lit les spans du journal WORM et calcule des métriques.
    """

    @staticmethod
    def compute_intention_timeline(trace_id: str, spans: list[dict]) -> dict:
        """
        Reconstruire la timeline d'une intention à partir de ses spans.

        Returns:
            {
                "trace_id": "...",
                "total_duration_ms": 4500,
                "spans": [...],
                "critical_path": [...],
                "bottlenecks": [...]
            }
        """
        if not spans:
            return {"trace_id": trace_id, "spans": [], "total_duration_ms": 0}

        # Trier par start_time
        sorted_spans = sorted(spans, key=lambda s: s.get("start_time", 0))

        # Trouver le span root (pas de parent)
        root_spans = [s for s in sorted_spans if not s.get("parent_span_id")]
        if root_spans:
            total_start = root_spans[0].get("start_time", 0)
            total_end = max(s.get("end_time", 0) for s in sorted_spans)
            total_ms = (total_end - total_start) * 1000
        else:
            total_ms = max(s.get("duration_ms", 0) for s in sorted_spans)

        # Identifier les bottlenecks (spans > 2s)
        bottlenecks = [
            s for s in sorted_spans
            if s.get("duration_ms", 0) > 2000
        ]

        # Construire l'arbre parent/enfant
        span_map = {s["span_id"]: s for s in sorted_spans if "span_id" in s}
        children = {}
        for s in sorted_spans:
            pid = s.get("parent_span_id")
            if pid:
                children.setdefault(pid, []).append(s)

        # Critical path: chaîne la plus longue du root à une feuille
        critical_path = []
        if root_spans:
            def _walk(span_id, path):
                path.append(span_id)
                kids = children.get(span_id, [])
                if not kids:
                    return path
                # Prendre l'enfant le plus long
                longest = max(kids, key=lambda k: k.get("duration_ms", 0))
                return _walk(longest["span_id"], path)

            critical_path = _walk(root_spans[0].get("span_id"), [])

        return {
            "trace_id": trace_id,
            "total_duration_ms": round(total_ms, 2),
            "span_count": len(sorted_spans),
            "root_operation": root_spans[0].get("operation_name") if root_spans else None,
            "spans": sorted_spans,
            "bottlenecks": bottlenecks,
            "bottleneck_count": len(bottlenecks),
            "critical_path": critical_path,
            "error_spans": [s for s in sorted_spans if s.get("status") == "ERROR"],
            "agent_coverage": list(set(
                s.get("agent_source", "") for s in sorted_spans if s.get("agent_source")
            )),
        }

    @staticmethod
    def compute_agent_metrics(spans: list[dict]) -> dict:
        """
        Calculer les métriques par agent à partir d'une liste de spans.

        Returns:
            {
                "data": {"avg_ms": 120, "p99_ms": 450, "error_rate": 0.02, "call_count": 150},
                "reasoning": {...},
                "action": {...},
                "mediator": {...},
            }
        """
        from collections import defaultdict

        agent_spans = defaultdict(list)
        for s in spans:
            agent = s.get("agent_source", "unknown")
            agent_spans[agent].append(s)

        metrics = {}
        for agent, agent_span_list in agent_spans.items():
            durations = [s.get("duration_ms", 0) for s in agent_span_list if s.get("duration_ms")]
            errors = [s for s in agent_span_list if s.get("status") == "ERROR"]

            if durations:
                sorted_d = sorted(durations)
                p99_idx = min(int(len(sorted_d) * 0.99), len(sorted_d) - 1)
                metrics[agent] = {
                    "call_count": len(agent_span_list),
                    "avg_ms": round(sum(durations) / len(durations), 2),
                    "p50_ms": round(sorted_d[len(sorted_d) // 2], 2),
                    "p99_ms": round(sorted_d[p99_idx], 2),
                    "max_ms": round(max(durations), 2),
                    "error_count": len(errors),
                    "error_rate": round(len(errors) / len(agent_span_list), 4),
                }
            else:
                metrics[agent] = {
                    "call_count": len(agent_span_list),
                    "avg_ms": 0,
                    "error_count": len(errors),
                    "error_rate": round(len(errors) / len(agent_span_list), 4) if agent_span_list else 0,
                }

        return metrics


# === Singleton ===

tracer = CortexTracer()

# Configuration par défaut: console + WORM
tracer.add_exporter(ConsoleExporter())
tracer.add_exporter(WORMExporter())
