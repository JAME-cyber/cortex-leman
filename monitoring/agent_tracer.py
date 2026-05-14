"""
Cortex Leman v5 — Agent Tracer (Observabilité agent-level)

Tracing JSONL de chaque action agent avec timing, tokens, coûts.
Complémentaire au tracing OpenTelemetry (infrastructure) et Prometheus (métriques).
Celui-ci trace au niveau MÉTIER: quel agent a fait quoi, quand, combien de temps.

Inspiré du module Observability SocialPulse, adapté pour Cortex Leman:
- Intégration journal append-only
- Isolation par client (RGPD)
- Dashboard par agent/verticale/période

Configuration:
- TRACER_PATH=./data/traces
- TRACER_ENABLED=true
"""
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)


@dataclass
class AgentTrace:
    """Trace d'une action agent"""
    trace_id: str = ""
    agent_name: str = ""
    action: str = ""
    intention_id: str = ""
    client_id: str = ""
    vertical: str = ""
    status: str = "pending"  # pending | success | error | timeout
    started_at: str = ""
    finished_at: str = ""
    duration_ms: float = 0
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    error_type: str = ""
    error_message: str = ""
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AgentMetrics:
    """Métriques agrégées par agent"""
    agent_name: str = ""
    total_traces: int = 0
    success_count: int = 0
    error_count: int = 0
    timeout_count: int = 0
    success_rate: float = 0.0
    avg_duration_ms: float = 0.0
    p50_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    by_vertical: dict = field(default_factory=dict)
    by_action: dict = field(default_factory=dict)


class AgentTracer:
    """
    Tracer agent-level — JSONL quotidien.
    
    Structure:
    traces/
    ├── 2025-05-08.jsonl
    ├── 2025-05-07.jsonl
    └── ...
    """
    
    def __init__(self, base_path: str = None):
        self._path = Path(base_path or os.getenv("TRACER_PATH", "./data/traces"))
        self._path.mkdir(parents=True, exist_ok=True)
        self._enabled = os.getenv("TRACER_ENABLED", "true").lower() == "true"
        self._active_traces: dict[str, AgentTrace] = {}
    
    def start_trace(
        self,
        agent_name: str,
        action: str,
        intention_id: str = "",
        client_id: str = "",
        vertical: str = "",
        metadata: dict = None,
    ) -> AgentTrace:
        """Démarrer une trace"""
        if not self._enabled:
            return AgentTrace()
        
        now = datetime.now(timezone.utc)
        trace_id = f"tr-{now.strftime('%H%M%S')}-{agent_name}-{action}"
        
        trace = AgentTrace(
            trace_id=trace_id,
            agent_name=agent_name,
            action=action,
            intention_id=intention_id,
            client_id=client_id,
            vertical=vertical,
            started_at=now.isoformat(),
            metadata=metadata or {},
        )
        
        self._active_traces[trace_id] = trace
        return trace
    
    def finish_trace(
        self,
        trace: AgentTrace,
        status: str = "success",
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost_usd: float = 0.0,
        error_type: str = "",
        error_message: str = "",
    ) -> None:
        """Terminer une trace et la sauvegarder"""
        if not self._enabled:
            return
        
        now = datetime.now(timezone.utc)
        trace.finished_at = now.isoformat()
        trace.status = status
        trace.tokens_in = tokens_in
        trace.tokens_out = tokens_out
        trace.cost_usd = cost_usd
        trace.error_type = error_type
        trace.error_message = error_message
        
        # Calculer durée
        try:
            start = datetime.fromisoformat(trace.started_at)
            trace.duration_ms = (now - start).total_seconds() * 1000
        except (ValueError, TypeError):
            trace.duration_ms = 0
        
        # Sauvegarder
        self._save_trace(trace)
        
        # Retirer des actives
        self._active_traces.pop(trace.trace_id, None)
        
        logger.debug(f"Trace: {trace.agent_name}/{trace.action} → {status} ({trace.duration_ms:.0f}ms)")
    
    def get_metrics(self, period: str = "today", agent_name: str = "") -> AgentMetrics:
        """
        Calculer les métrages agrégées.
        
        Args:
            period: "today" | "7d" | "30d" | "all"
            agent_name: filtrer par agent (optionnel)
        """
        traces = self._load_traces(period)
        
        if agent_name:
            traces = [t for t in traces if t.get("agent_name") == agent_name]
        
        if not traces:
            return AgentMetrics(agent_name=agent_name or "all")
        
        metrics = AgentMetrics(agent_name=agent_name or "all")
        metrics.total_traces = len(traces)
        
        durations = []
        by_vertical = {}
        by_action = {}
        
        for t in traces:
            status = t.get("status", "unknown")
            if status == "success":
                metrics.success_count += 1
            elif status == "timeout":
                metrics.timeout_count += 1
            else:
                metrics.error_count += 1
            
            dur = t.get("duration_ms", 0)
            if dur > 0:
                durations.append(dur)
            
            metrics.total_tokens += t.get("tokens_in", 0) + t.get("tokens_out", 0)
            metrics.total_cost_usd += t.get("cost_usd", 0)
            
            # Par verticale
            vert = t.get("vertical", "unknown")
            if vert not in by_vertical:
                by_vertical[vert] = {"count": 0, "success": 0, "errors": 0}
            by_vertical[vert]["count"] += 1
            if status == "success":
                by_vertical[vert]["success"] += 1
            else:
                by_vertical[vert]["errors"] += 1
            
            # Par action
            act = t.get("action", "unknown")
            if act not in by_action:
                by_action[act] = {"count": 0, "avg_ms": 0, "total_ms": 0}
            by_action[act]["count"] += 1
            by_action[act]["total_ms"] += dur
        
        # Calculer moyennes par action
        for act_data in by_action.values():
            if act_data["count"] > 0:
                act_data["avg_ms"] = round(act_data["total_ms"] / act_data["count"], 1)
        
        metrics.success_rate = round(metrics.success_count / metrics.total_traces * 100, 1) if metrics.total_traces > 0 else 0
        
        if durations:
            durations.sort()
            metrics.avg_duration_ms = round(sum(durations) / len(durations), 1)
            metrics.p50_duration_ms = round(durations[len(durations) // 2], 1)
            metrics.p95_duration_ms = round(durations[int(len(durations) * 0.95)], 1)
        
        metrics.by_vertical = by_vertical
        metrics.by_action = by_action
        
        return metrics
    
    def print_dashboard(self, period: str = "today") -> str:
        """Générer un dashboard texte"""
        all_traces = self._load_traces(period)
        if not all_traces:
            return f"Aucune trace pour la période '{period}'"
        
        # Agents uniques
        agents = sorted(set(t.get("agent_name", "unknown") for t in all_traces))
        
        lines = []
        lines.append(f"{'═' * 70}")
        lines.append(f"  CORTEX LEMAN V5 — DASHBOARD AGENTS ({period})")
        lines.append(f"  {len(all_traces)} traces • {len(agents)} agents")
        lines.append(f"{'═' * 70}")
        
        for agent in agents:
            m = self.get_metrics(period, agent)
            lines.append(f"")
            lines.append(f"  🔹 {agent}")
            lines.append(f"     {m.total_traces} traces • {m.success_rate}% succès • {m.avg_duration_ms}ms avg")
            lines.append(f"     Tokens: {m.total_tokens} • Coût: ${m.total_cost_usd:.4f}")
            
            if m.by_vertical:
                for vert, data in m.by_vertical.items():
                    lines.append(f"     └ {vert}: {data['count']} ({data['success']}✓ {data['errors']}✗)")
        
        lines.append(f"{'═' * 70}")
        return "\n".join(lines)
    
    def _save_trace(self, trace: AgentTrace) -> None:
        """Sauvegarder une trace dans le fichier JSONL du jour"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        trace_file = self._path / f"{today}.jsonl"
        
        with open(trace_file, "a") as f:
            f.write(json.dumps(trace.to_dict(), ensure_ascii=False) + "\n")
    
    def _load_traces(self, period: str = "today") -> list[dict]:
        """Charger les traces pour une période"""
        traces = []
        
        if period == "today":
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            files = [self._path / f"{today}.jsonl"]
        elif period == "7d":
            files = []
            for i in range(7):
                d = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
                files.append(self._path / f"{d}.jsonl")
        elif period == "30d":
            files = []
            for i in range(30):
                d = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
                files.append(self._path / f"{d}.jsonl")
        elif period == "all":
            files = list(self._path.glob("*.jsonl"))
        else:
            files = []
        
        for f in files:
            if not f.exists():
                continue
            for line in f.read_text().strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    traces.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return traces


# Singleton
agent_tracer = AgentTracer()
