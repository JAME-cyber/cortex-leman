#!/usr/bin/env python3
"""
hermes_cost_audit.py — Journal de coût structuré par workflow.

Transforme les données session_model_usage en journal analysable:
  - Coût réel par session (workflow)
  - Répartition par modèle et par task
  - Identification des sessions coûteuses
  - Alertes budget

Usage:
    python3 hermes_cost_audit.py [--days 7] [--json] [--budget USD]
    python3 hermes_cost_audit.py --session <session_id>

Données lues directement depuis state.db — aucun interception runtime nécessaire.
Le journal est agrégé à partir des données que Hermes collecte déjà.

Auteur: Hermes Agent (prototype, 2026-07-27)
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ── Path setup: find the Hermes agent package ─────────────────────────
_HERMES_ROOT = Path(os.path.expanduser("~/.hermes/hermes-agent"))
if _HERMES_ROOT.exists():
    sys.path.insert(0, str(_HERMES_ROOT))

try:
    from agent.usage_pricing import (
        CanonicalUsage,
        estimate_usage_cost,
        has_known_pricing,
        resolve_billing_route,
    )
except ImportError:
    print("ERROR: Cannot import usage_pricing. Ensure Hermes agent source is at ~/.hermes/hermes-agent", file=sys.stderr)
    sys.exit(1)

DB_PATH = os.path.expanduser("~/.hermes/state.db")


def _ts_to_iso(ts: float) -> str:
    if not ts:
        return ""
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ts_to_human(ts: float) -> str:
    if not ts:
        return ""
    return datetime.fromtimestamp(ts).strftime("%m-%d %H:%M")


def _cost(usage_row: dict) -> tuple[float, str]:
    """Estimate cost from a session_model_usage row."""
    usage = CanonicalUsage(
        input_tokens=usage_row.get("input_tokens") or 0,
        output_tokens=usage_row.get("output_tokens") or 0,
        cache_read_tokens=usage_row.get("cache_read_tokens") or 0,
        cache_write_tokens=usage_row.get("cache_write_tokens") or 0,
    )
    result = estimate_usage_cost(
        usage_row.get("model") or "",
        usage,
        provider=usage_row.get("billing_provider"),
        base_url=usage_row.get("billing_base_url"),
    )
    return float(result.amount_usd or 0.0), result.status


def get_sessions_with_cost(conn: sqlite3.Connection, cutoff: float, source: str = None) -> list[dict]:
    """Fetch sessions within window with aggregated cost."""
    query = """
        SELECT
            s.id, s.source, s.model, s.started_at, s.ended_at,
            s.input_tokens, s.output_tokens,
            s.cache_read_tokens, s.cache_write_tokens,
            s.billing_provider, s.billing_base_url,
            s.api_call_count, s.tool_call_count, s.message_count,
            s.title
        FROM sessions s
        WHERE s.started_at >= ?
    """
    params: list = [cutoff]
    if source:
        query += " AND s.source = ?"
        params.append(source)
    query += " ORDER BY s.started_at DESC"

    rows = conn.execute(query, params).fetchall()
    sessions = []
    for row in rows:
        d = dict(row)
        cost, status = _cost(d)
        d["estimated_cost_usd"] = cost
        d["cost_status"] = status
        sessions.append(d)
    return sessions


def get_model_usage_breakdown(conn: sqlite3.Connection, cutoff: float) -> list[dict]:
    """Fetch per-model/task usage aggregated."""
    rows = conn.execute(
        """
        SELECT
            model,
            task,
            billing_provider,
            billing_base_url,
            SUM(input_tokens) as total_in,
            SUM(output_tokens) as total_out,
            SUM(cache_read_tokens) as total_cr,
            SUM(cache_write_tokens) as total_cw,
            SUM(api_call_count) as total_calls,
            COUNT(DISTINCT session_id) as session_count
        FROM session_model_usage
        WHERE last_seen >= ?
        GROUP BY model, task, billing_provider, billing_base_url
        ORDER BY total_in DESC
        """,
        (cutoff,),
    ).fetchall()
    results = []
    for row in rows:
        d = dict(row)
        usage = CanonicalUsage(
            input_tokens=d["total_in"] or 0,
            output_tokens=d["total_out"] or 0,
            cache_read_tokens=d["total_cr"] or 0,
            cache_write_tokens=d["total_cw"] or 0,
        )
        result = estimate_usage_cost(
            d["model"] or "",
            usage,
            provider=d.get("billing_provider"),
            base_url=d.get("billing_base_url"),
        )
        d["estimated_cost_usd"] = float(result.amount_usd or 0.0)
        d["cost_status"] = result.status
        d["has_pricing"] = has_known_pricing(
            d["model"] or "",
            d.get("billing_provider"),
            d.get("billing_base_url"),
        )
        results.append(d)
    return results


def get_session_detail(conn: sqlite3.Connection, session_id: str) -> dict:
    """Get detailed cost breakdown for a single session."""
    sess_row = conn.execute(
        """SELECT * FROM sessions WHERE id = ?""", (session_id,)
    ).fetchone()
    if not sess_row:
        return {"error": f"Session {session_id} not found"}

    sess = dict(sess_row)
    usage_rows = conn.execute(
        """SELECT * FROM session_model_usage WHERE session_id = ? ORDER BY last_seen""",
        (session_id,),
    ).fetchall()

    models_breakdown = []
    for row in usage_rows:
        d = dict(row)
        cost, status = _cost(d)
        d["estimated_cost_usd"] = cost
        d["cost_status"] = status
        models_breakdown.append(d)

    total_cost = sum(m["estimated_cost_usd"] for m in models_breakdown)

    tool_rows = conn.execute(
        """
        SELECT m.tool_name, COUNT(*) as count
        FROM messages m
        WHERE m.session_id = ? AND m.role = 'tool' AND m.tool_name IS NOT NULL
        GROUP BY m.tool_name ORDER BY count DESC
        """,
        (session_id,),
    ).fetchall()

    return {
        "session_id": session_id,
        "title": sess.get("title"),
        "model": sess.get("model"),
        "source": sess.get("source"),
        "started_at": _ts_to_iso(sess.get("started_at") or 0),
        "ended_at": _ts_to_iso(sess.get("ended_at") or 0),
        "duration_seconds": (sess["ended_at"] - sess["started_at"])
        if sess.get("started_at") and sess.get("ended_at")
        else None,
        "message_count": sess.get("message_count"),
        "tool_call_count": sess.get("tool_call_count"),
        "api_call_count": sess.get("api_call_count"),
        "total_cost_usd": round(total_cost, 6),
        "models_breakdown": models_breakdown,
        "tools_used": [dict(r) for r in tool_rows],
    }


def audit_report(days: int = 7, source: str = None, budget: float = None) -> dict:
    """Generate full cost audit report."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cutoff = time.time() - (days * 86400)

    sessions = get_sessions_with_cost(conn, cutoff, source)
    model_usage = get_model_usage_breakdown(conn, cutoff)

    total_cost = sum(s["estimated_cost_usd"] for s in sessions)
    total_input = sum(s["input_tokens"] or 0 for s in sessions)
    total_output = sum(s["output_tokens"] or 0 for s in sessions)
    total_api_calls = sum(s["api_call_count"] or 0 for s in sessions)
    total_tool_calls = sum(s["tool_call_count"] or 0 for s in sessions)

    unknown_sessions = [s for s in sessions if s["cost_status"] == "unknown"]
    unknown_tokens = sum(
        (s["input_tokens"] or 0) + (s["output_tokens"] or 0) for s in unknown_sessions
    )

    top_expensive = sorted(sessions, key=lambda x: x["estimated_cost_usd"], reverse=True)[:5]

    cost_by_model = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "calls": 0})
    for mu in model_usage:
        key = mu["model"] or "unknown"
        cost_by_model[key]["cost"] += mu["estimated_cost_usd"]
        cost_by_model[key]["tokens"] += (mu["total_in"] or 0) + (mu["total_out"] or 0)
        cost_by_model[key]["calls"] += mu["total_calls"] or 0

    cost_by_task = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "calls": 0})
    for mu in model_usage:
        key = mu["task"] or "main"
        cost_by_task[key]["cost"] += mu["estimated_cost_usd"]
        cost_by_task[key]["tokens"] += (mu["total_in"] or 0) + (mu["total_out"] or 0)
        cost_by_task[key]["calls"] += mu["total_calls"] or 0

    budget_alert = None
    if budget:
        pct = (total_cost / budget) * 100
        if pct >= 100:
            budget_alert = {"level": "EXCEEDED", "pct": pct, "budget": budget, "actual": total_cost}
        elif pct >= 75:
            budget_alert = {"level": "WARNING", "pct": pct, "budget": budget, "actual": total_cost}
        elif pct >= 50:
            budget_alert = {"level": "INFO", "pct": pct, "budget": budget, "actual": total_cost}

    conn.close()

    return {
        "generated_at": _ts_to_iso(time.time()),
        "period_days": days,
        "source_filter": source,
        "summary": {
            "total_sessions": len(sessions),
            "total_cost_usd": round(total_cost, 4),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_api_calls": total_api_calls,
            "total_tool_calls": total_tool_calls,
            "avg_cost_per_session": round(total_cost / len(sessions), 4) if sessions else 0,
        },
        "pricing_coverage": {
            "sessions_with_pricing": len(sessions) - len(unknown_sessions),
            "sessions_without_pricing": len(unknown_sessions),
            "unknown_cost_tokens": unknown_tokens,
            "pct_sessions_priced": round(
                (len(sessions) - len(unknown_sessions)) / len(sessions) * 100, 1
            ) if sessions else 0,
        },
        "cost_by_model": dict(cost_by_model),
        "cost_by_task": dict(cost_by_task),
        "top_5_expensive_sessions": [
            {
                "id": s["id"],
                "title": (s["title"] or "")[:60],
                "cost": round(s["estimated_cost_usd"], 4),
                "model": s["model"],
                "tokens_in": s["input_tokens"],
                "tokens_out": s["output_tokens"],
                "api_calls": s["api_call_count"],
                "date": _ts_to_human(s["started_at"]),
            }
            for s in top_expensive
        ],
        "budget_alert": budget_alert,
    }


def print_terminal(report: dict):
    s = report["summary"]
    pc = report["pricing_coverage"]

    print("=" * 70)
    print(f"  HERMES COST AUDIT — {report['period_days']} days")
    print(f"  Generated: {report['generated_at']}")
    print("=" * 70)

    print(f"\n📊 OVERVIEW")
    print(f"   Sessions:     {s['total_sessions']}")
    print(f"   Total cost:   ${s['total_cost_usd']:.4f}")
    print(f"   Avg/session:  ${s['avg_cost_per_session']:.4f}")
    print(f"   API calls:    {s['total_api_calls']:,}")
    print(f"   Tool calls:   {s['total_tool_calls']:,}")
    print(f"   Tokens in:    {s['total_input_tokens']:,}")
    print(f"   Tokens out:   {s['total_output_tokens']:,}")

    total = s["total_cost_usd"]
    print(f"\n💰 COST BY MODEL")
    for model, data in sorted(report["cost_by_model"].items(), key=lambda x: x[1]["cost"], reverse=True):
        calls = data["calls"]
        cost = data["cost"]
        pct = (cost / total * 100) if total else 0
        bar = "█" * int(pct / 5)
        print(f"   {model:<30} ${cost:>8.4f} ({pct:>5.1f}%) {bar} {calls:>5} calls")

    print(f"\n📋 COST BY TASK")
    for task, data in sorted(report["cost_by_task"].items(), key=lambda x: x[1]["cost"], reverse=True):
        cost = data["cost"]
        pct = (cost / total * 100) if total else 0
        print(f"   {task:<25} ${cost:>8.4f} ({pct:>5.1f}%) {data['calls']:>5} calls")

    print(f"\n🔓 PRICING COVERAGE")
    print(f"   Priced:     {pc['sessions_with_pricing']}/{s['total_sessions']} ({pc['pct_sessions_priced']}%)")
    print(f"   Unpriced:   {pc['sessions_without_pricing']} sessions ({pc['unknown_cost_tokens']:,} tokens)")

    print(f"\n🔝 TOP 5 EXPENSIVE SESSIONS")
    for i, sess in enumerate(report["top_5_expensive_sessions"], 1):
        print(f"   {i}. ${sess['cost']:.4f} | {sess['title']}")
        print(f"      {sess['model']} | {sess['tokens_in']:,}→{sess['tokens_out']:,} tok | {sess['api_calls']} APIs | {sess['date']}")

    if report.get("budget_alert"):
        alert = report["budget_alert"]
        emoji = "🚨" if alert["level"] == "EXCEEDED" else "⚠️" if alert["level"] == "WARNING" else "ℹ️"
        print(f"\n{emoji} BUDGET: {alert['level']} — ${alert['actual']:.2f} / ${alert['budget']:.2f} ({alert['pct']:.0f}%)")

    print()


def main():
    parser = argparse.ArgumentParser(description="Hermes Cost Audit — structured cost journal")
    parser.add_argument("--days", type=int, default=7, help="Lookback days (default: 7)")
    parser.add_argument("--source", type=str, default=None, help="Filter by source platform")
    parser.add_argument("--budget", type=float, default=None, help="Budget USD for alert thresholds")
    parser.add_argument("--session", type=str, default=None, help="Detailed breakdown for a single session")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not os.path.exists(DB_PATH):
        print(f"ERROR: state.db not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    if args.session:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        detail = get_session_detail(conn, args.session)
        conn.close()
        print(json.dumps(detail, indent=2, default=str))
        return

    report = audit_report(days=args.days, source=args.source, budget=args.budget)

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print_terminal(report)


if __name__ == "__main__":
    main()
