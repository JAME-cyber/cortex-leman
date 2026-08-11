#!/usr/bin/env python3
"""
hermes_portfolio.py — Dossier de preuves: workflows autonomes exécutés et vérifiés.

Génère un portfolio Markdown qui documente des workflows réels avec leurs métriques
vérifiables (coût, durée, outils, tools, livrables). Au lieu de clamer "on peut
lancer 100 agents", on prouve avec des données réelles.

Usage:
    python3 hermes_portfolio.py --days 30
    python3 hermes_portfolio.py --days 7 --output portfolio.md
    python3 hermes_portfolio.py --session <id>
    python3 hermes_portfolio.py --days 30 --min-tools 20

Auteur: Hermes Agent (prototype, 2026-07-27)
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

_HERMES_ROOT = Path(os.path.expanduser("~/.hermes/hermes-agent"))
if _HERMES_ROOT.exists():
    sys.path.insert(0, str(_HERMES_ROOT))

try:
    from agent.usage_pricing import (
        CanonicalUsage,
        estimate_usage_cost,
    )
except ImportError:
    estimate_usage_cost = None

DB_PATH = os.path.expanduser("~/.hermes/state.db")


def _ts_to_iso(ts):
    if not ts:
        return ""
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ts_to_human(ts):
    if not ts:
        return ""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def _duration_str(start, end):
    if not start or not end:
        return "—"
    secs = end - start
    if secs < 60:
        return f"{secs:.0f}s"
    mins = secs / 60
    if mins < 60:
        return f"{mins:.0f}min"
    hours = mins / 60
    return f"{hours:.1f}h"


def _estimate_cost(row_dict):
    """Estimate cost from session/model usage row."""
    if estimate_usage_cost is None:
        return 0.0
    usage = CanonicalUsage(
        input_tokens=row_dict.get("input_tokens") or 0,
        output_tokens=row_dict.get("output_tokens") or 0,
        cache_read_tokens=row_dict.get("cache_read_tokens") or 0,
        cache_write_tokens=row_dict.get("cache_write_tokens") or 0,
    )
    result = estimate_usage_cost(
        row_dict.get("model") or "",
        usage,
        provider=row_dict.get("billing_provider"),
        base_url=row_dict.get("billing_base_url"),
    )
    return float(result.amount_usd or 0.0)


def _classify_workflow(title, tools_used, source):
    """Classify session into a workflow category."""
    title_lower = (title or "").lower()
    tools_str = " ".join(tools_used).lower()

    if "cron" in (source or "") or source == "cron":
        if "arxiv" in title_lower:
            return "ArXiv Daily Scan"
        elif "compliance" in title_lower or "cnil" in title_lower:
            return "Compliance Monitor";
        elif "weekly" in title_lower or "report" in title_lower:
            return "Weekly Report";
        else:
            return "Scheduled Pipeline"

    if any(w in title_lower for w in ["culture", "saveur", "év"]):
        return "Content Production";
    if any(w in title_lower for w in ["crypto", "bitcoin", "defi", "trading"]):
        return "Crypto Research";
    if any(w in title_lower for w in ["analyse", "vidéo", "sommet", "tweet"]):
        return "Media Analysis";
    if any(w in title_lower for w in ["migration", "setup", "implémentation", "installation"]):
        return "Infrastructure Setup";
    if any(w in title_lower for w in ["cortex", "pi framework"]):
        return "Cortex Leman Build";
    if any(w in title_lower for w in ["crm", "salesforce", "twenty"]):
        return "Business Tooling";
    if any(w in title_lower for w in ["compliance", "rgpd", "ai act"]):
        return "Compliance";

    # Fallback: classify by tool patterns
    if "vision_analyze" in tools_str or "browser_navigate" in tools_str:
        return "Web/Media Analysis";
    if "write_file" in tools_str or "patch" in tools_str:
        return "Development";
    if "web_search" in tools_str or "mcp" in tools_str:
        return "Research";

    return "General Task";


def _get_tool_categories(tool_names):
    """Map raw tool names to human-readable categories."""
    categories = Counter()
    for name, count in tool_names:
        name_lower = (name or "").lower()
        if name_lower.startswith("terminal"):
            categories["Terminal"] += count
        elif name_lower.startswith("browser"):
            categories["Browser"] += count
        elif name_lower.startswith("read_file") or name_lower.startswith("write_file"):
            categories["File I/O"] += count
        elif name_lower.startswith("patch") or name_lower.startswith("search_files"):
            categories["File Ops"] += count
        elif name_lower.startswith("web_search") or name_lower.startswith("web_extract"):
            categories["Web Research"] += count
        elif name_lower.startswith("vision"):
            categories["Vision"] += count
        elif name_lower.startswith("mcp"):
            categories["MCP Tools"] += count
        elif name_lower.startswith("delegate"):
            categories["Delegation"] += count
        elif name_lower.startswith("execute_code"):
            categories["Code Execution"] += count
        elif name_lower.startswith("memory") or name_lower.startswith("fact_store"):
            categories["Memory"] += count
        elif name_lower.startswith("skill"):
            categories["Skills"] += count
        elif name_lower.startswith("todo"):
            categories["Planning"] += count
        elif name_lower.startswith("process"):
            categories["Process Mgmt"] += count
        elif name_lower.startswith("clarify"):
            categories["User Interaction"] += count
        elif name_lower.startswith("session_search"):
            categories["Session History"] += count
        else:
            categories[name_lower.split("(")[0][:20]] += count
    return categories


def collect_workflows(conn, cutoff, min_tools=5, min_messages=3):
    """Collect all sessions that qualify as workflows."""
    rows = conn.execute(
        """
        SELECT id, title, source, model, started_at, ended_at,
               input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,
               api_call_count, tool_call_count, message_count,
               billing_provider, billing_base_url, cwd, git_repo_root,
               reasoning_tokens
        FROM sessions
        WHERE started_at >= ?
          AND tool_call_count >= ?
          AND message_count >= ?
        ORDER BY started_at DESC
        """,
        (cutoff, min_tools, min_messages),
    ).fetchall()

    workflows = []
    for row in rows:
        d = dict(row)
        d["estimated_cost_usd"] = _estimate_cost(d)
        d["tool_names"] = []
        d["tool_categories"] = Counter()

        # Get tool breakdown
        tool_rows = conn.execute(
            """
            SELECT tool_name, COUNT(*) as cnt
            FROM messages
            WHERE session_id = ? AND tool_name IS NOT NULL
            GROUP BY tool_name ORDER BY cnt DESC
            """,
            (d["id"],),
        ).fetchall()
        d["tool_names"] = [(r[0], r[1]) for r in tool_rows]
        d["tool_categories"] = _get_tool_categories(d["tool_names"])
        d["workflow_type"] = _classify_workflow(d["title"], [t[0] for t in d["tool_names"]], d["source"])
        workflows.append(d)

    return workflows


def get_session_detail(conn, session_id):
    """Get detailed breakdown for a single session."""
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["estimated_cost_usd"] = _estimate_cost(d)

    tool_rows = conn.execute(
        """
        SELECT tool_name, COUNT(*) as cnt
        FROM messages WHERE session_id = ? AND tool_name IS NOT NULL
        GROUP BY tool_name ORDER BY cnt DESC
        """,
        (session_id,),
    ).fetchall()
    d["tool_names"] = [(r[0], r[1]) for r in tool_rows]
    d["tool_categories"] = _get_tool_categories(d["tool_names"])
    d["workflow_type"] = _classify_workflow(d["title"], [t[0] for t in d["tool_names"]], d["source"])

    # Model usage breakdown
    model_rows = conn.execute(
        """
        SELECT model, task, input_tokens, output_tokens, api_call_count
        FROM session_model_usage WHERE session_id = ?
        ORDER BY input_tokens DESC
        """,
        (session_id,),
    ).fetchall()
    d["model_breakdown"] = [dict(r) for r in model_rows]

    return d


# ═══════════════════════════════════════════════════════════════════════
# MARKDOWN GENERATOR
# ═══════════════════════════════════════════════════════════════════════

def generate_portfolio(workflows, period_days, generated_at):
    """Generate full Markdown portfolio."""
    lines = []

    # ── Header ─────────────────────────────────────────────────────
    lines.append("# Dossier de Preuves — Workflows Autonomes")
    lines.append("")
    lines.append(f"> Généré le {generated_at} | Période: {period_days} jours")
    lines.append(f"> Données source: `~/.hermes/state.db` (SQLite, métriques vérifiables)")
    lines.append(f"> Scripts: `hermes_cost_audit.py` + `anti_sycophancy.py` + `hermes_portfolio.py`")
    lines.append("")

    # ── Executive Summary ──────────────────────────────────────────
    total_cost = sum(w["estimated_cost_usd"] for w in workflows)
    total_tools = sum(w["tool_call_count"] or 0 for w in workflows)
    total_api = sum(w["api_call_count"] or 0 for w in workflows)
    total_tokens_in = sum(w["input_tokens"] or 0 for w in workflows)
    total_tokens_out = sum(w["output_tokens"] or 0 for w in workflows)

    # Workflow types
    type_counts = Counter(w["workflow_type"] for w in workflows)

    # Autonomy metrics
    autonomous = [w for w in workflows if "cron" in (w.get("source") or "")]
    interactive = [w for w in workflows if "cron" not in (w.get("source") or "")]

    # Tool diversity (unique tools per session)
    tool_diversities = []
    for w in workflows:
        tool_diversities.append(len(w["tool_names"]))
    avg_diversity = sum(tool_diversities) / len(tool_diversities) if tool_diversities else 0

    lines.append("## Résumé Exécutif")
    lines.append("")
    lines.append("| Métrique | Valeur |")
    lines.append("|---|---|")
    lines.append(f"| Workflows documentés | **{len(workflows)}** |")
    lines.append(f"| Coût total estimé | **${total_cost:.2f}** |")
    lines.append(f"| Tool calls total | {total_tools:,} |")
    lines.append(f"| API calls total | {total_api:,} |")
    lines.append(f"| Tokens consommés | {total_tokens_in:,} in / {total_tokens_out:,} out |")
    lines.append(f"| Coût moyen/workflow | ${total_cost/len(workflows):.2f}" if workflows else "| Coût moyen | — |")
    lines.append(f"| Diversité outils (avg) | {avg_diversity:.1f} outils uniques/workflow |")
    lines.append("")

    # Autonomy split
    lines.append("### Autonomie")
    lines.append("")
    lines.append(f"- **{len(autonomous)} workflows autonomes** (cron, sans intervention humaine)")
    lines.append(f"- **{len(interactive)} workflows interactifs** (guidés par opérateur)")
    if autonomous:
        auto_cost = sum(w["estimated_cost_usd"] for w in autonomous)
        lines.append(f"- Coût des workflows autonomes: ${auto_cost:.2f} ({auto_cost/total_cost*100:.0f}% du total)" if total_cost else "")
        auto_tools = sum(w["tool_call_count"] or 0 for w in autonomous)
        lines.append(f"- Tool calls autonomes: {auto_tools:,}")
    lines.append("")

    # Workflow types breakdown
    lines.append("### Types de workflows")
    lines.append("")
    lines.append("| Type | Count |")
    lines.append("|---|---|")
    for wtype, count in type_counts.most_common():
        lines.append(f"| {wtype} | {count} |")
    lines.append("")

    # ── Detailed Workflow Cards ────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Workflows Détaillés")
    lines.append("")

    # Sort by tool call count (most complex first)
    sorted_workflows = sorted(workflows, key=lambda w: (w["tool_call_count"] or 0), reverse=True)

    for i, w in enumerate(sorted_workflows, 1):
        lines.append(f"### {i}. {(w['title'] or 'Sans titre')[:80]}")
        lines.append("")

        lines.append(f"**Session:** `{w['id']}`  ")
        lines.append(f"**Type:** {w['workflow_type']}  ")
        lines.append(f"**Date:** {_ts_to_human(w['started_at'])}  ")
        lines.append(f"**Durée:** {_duration_str(w['started_at'], w['ended_at'])}  ")
        lines.append(f"**Source:** {w['source'] or 'cli'}  ")
        lines.append(f"**Modèle:** {w['model'] or '?'}  ")
        lines.append("")

        # Metrics table
        lines.append("| Métrique | Valeur |")
        lines.append("|---|---|")
        lines.append(f"| Tool calls | {w['tool_call_count'] or 0} |")
        lines.append(f"| API calls | {w['api_call_count'] or 0} |")
        lines.append(f"| Messages | {w['message_count'] or 0} |")
        lines.append(f"| Tokens input | {w['input_tokens'] or 0:,} |")
        lines.append(f"| Tokens output | {w['output_tokens'] or 0:,} |")
        cost_str = f"${w['estimated_cost_usd']:.4f}" if w['estimated_cost_usd'] else "—"
        lines.append(f"| Coût estimé | {cost_str} |")
        lines.append("")

        # Tool categories used
        if w["tool_categories"]:
            lines.append("**Outils utilisés:**")
            lines.append("")
            for cat, count in w["tool_categories"].most_common():
                bar = "█" * min(20, count)
                lines.append(f"- `{cat}`: {count} {bar}")
            lines.append("")

        # Full tool list (collapsible)
        if w["tool_names"]:
            lines.append("<details>")
            lines.append(f"<summary>Détail tools ({len(w['tool_names'])} uniques)</summary>")
            lines.append("")
            lines.append("| Tool | Count |")
            lines.append("|---|---|")
            for name, count in w["tool_names"]:
                lines.append(f"| `{name}` | {count} |")
            lines.append("")
            lines.append("</details>")
            lines.append("")

        lines.append("---")
        lines.append("")

    # ── Methodology ────────────────────────────────────────────────
    lines.append("## Méthodologie")
    lines.append("")
    lines.append("**Source de données:** SQLite `state.db` (Hermes session store)")
    lines.append("")
    lines.append("**Critères d'inclusion:**")
    lines.append(f"- `tool_call_count >= {5}` (le workflow a utilisé des outils)")
    lines.append(f"- `message_count >= {3}` (interaction multi-tours)")
    lines.append(f"- `started_at` dans les {period_days} derniers jours")
    lines.append("")
    lines.append("**Coût estimé via:** `agent/usage_pricing.py` (pricing table officielle)")
    lines.append("")
    lines.append("**Limitations:**")
    lines.append("- Le coût est **estimé** à partir des tokens, pas facturé (sauf OpenRouter dynamique)")
    lines.append("- Les sessions sans `tool_name` dans les messages (anciennes) ne sont pas incluses")
    lines.append("- La qualité du livrable n'est pas mesurée automatiquement (requiert validation humaine)")
    lines.append("- Les workflows qui n'ont pas abouti sont inclus si ils ont consommé des ressources")
    lines.append("")

    return "\n".join(lines)


def generate_session_card(session):
    """Generate detailed card for a single session."""
    lines = []
    lines.append(f"# Workflow Detail — {(session['title'] or 'Sans titre')[:80]}")
    lines.append("")
    lines.append(f"**Session:** `{session['id']}`  ")
    lines.append(f"**Date:** {_ts_to_human(session['started_at'])}  ")
    lines.append(f"**Durée:** {_duration_str(session['started_at'], session['ended_at'])}  ")
    lines.append(f"**Coût:** ${session['estimated_cost_usd']:.4f}  ")
    lines.append("")

    # Model breakdown
    if session.get("model_breakdown"):
        lines.append("## Model Usage Breakdown")
        lines.append("")
        lines.append("| Model | Task | Input | Output | API Calls |")
        lines.append("|---|---|---|---|---|")
        for m in session["model_breakdown"]:
            lines.append(f"| {m['model'] or '?'} | {m['task'] or 'main'} | {m['input_tokens']:,} | {m['output_tokens']:,} | {m['api_call_count']} |")
        lines.append("")

    # Tools
    if session["tool_categories"]:
        lines.append("## Tools by Category")
        lines.append("")
        for cat, count in session["tool_categories"].most_common():
            lines.append(f"- `{cat}`: {count}")
        lines.append("")

    if session["tool_names"]:
        lines.append("## All Tool Calls")
        lines.append("")
        lines.append("| Tool | Count |")
        lines.append("|---|---|")
        for name, count in session["tool_names"]:
            lines.append(f"| `{name}` | {count} |")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Hermes Portfolio — dossier de preuves de workflows autonomes")
    parser.add_argument("--days", type=int, default=30, help="Lookback period (default: 30)")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output file (default: stdout)")
    parser.add_argument("--min-tools", type=int, default=5, help="Minimum tool calls to qualify (default: 5)")
    parser.add_argument("--session", type=str, default=None, help="Single session detail")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not os.path.exists(DB_PATH):
        print(f"ERROR: state.db not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    if args.session:
        session = get_session_detail(conn, args.session)
        conn.close()
        if not session:
            print(f"Session {args.session} not found", file=sys.stderr)
            sys.exit(1)
        if args.json:
            print(json.dumps(session, indent=2, default=str))
        else:
            print(generate_session_card(session))
        return

    cutoff = time.time() - (args.days * 86400)
    workflows = collect_workflows(conn, cutoff, min_tools=args.min_tools)
    conn.close()

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    if args.json:
        print(json.dumps(workflows, indent=2, default=str))
        return

    markdown = generate_portfolio(workflows, args.days, generated_at)

    if args.output:
        with open(args.output, "w") as f:
            f.write(markdown)
        print(f"Portfolio written to {args.output} ({len(workflows)} workflows)", file=sys.stderr)
    else:
        print(markdown)


if __name__ == "__main__":
    main()
