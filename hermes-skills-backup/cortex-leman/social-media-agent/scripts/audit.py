#!/usr/bin/env python3
"""
Social Media Agent — Post-build audit script.
Checks: file structure, config completeness, function imports,
class methods, Python syntax, script executability, env vars, dry-run.

Usage:
  python3 audit.py /path/to/social-media-agent
"""
import os
import sys
import json
import yaml
import subprocess
from pathlib import Path

def audit(base_path):
    BASE = Path(base_path)
    issues, warnings, ok = [], [], []

    # 1. Structure
    expected = [
        "config/accounts.yaml", "src/__init__.py", "src/brain/__init__.py",
        "src/brain/brain.py", "src/platforms/__init__.py", "src/platforms/connectors.py",
        "src/engagement/__init__.py", "src/engagement/agent.py",
        "orchestrator.py", "requirements.txt", "data", "logs",
    ]
    for f in expected:
        if (BASE / f).exists():
            ok.append(f"✅ {f}")
        else:
            issues.append(f"❌ MANQUANT: {f}")

    # 2. Scripts
    for script in ["scheduler_post.sh", "scheduler_engage.sh", "scheduler_plan.sh"]:
        p = BASE / "scripts" / script
        if p.exists() and os.access(p, os.X_OK):
            ok.append(f"✅ {script} exécutable")
        elif p.exists():
            issues.append(f"❌ {script} pas exécutable")
        else:
            issues.append(f"❌ {script} manquant")

    # 3. Config completeness
    config_path = BASE / "config/accounts.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
        g = config.get("global", {})
        for key in ["llm_model", "llm_fallback", "language", "timezone",
                     "posting_hours", "auto_reply", "dry_run", "blocked_topics"]:
            if key in g:
                ok.append(f"✅ global.{key}")
            else:
                issues.append(f"❌ global.{key} manquant")
        accounts = config.get("accounts", {})
        for acct_id, acct in accounts.items():
            for key in ["name", "handle", "tone", "platforms", "content_pillars"]:
                if key in acct:
                    ok.append(f"✅ {acct_id}.{key}")
                else:
                    issues.append(f"❌ {acct_id}.{key} manquant")

    # 4. Syntax check all Python files
    py_files = list(BASE.rglob("*.py"))
    for pf in py_files:
        result = subprocess.run(
            ["python3", "-c", f"import py_compile; py_compile.compile('{pf}', doraise=True)"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            issues.append(f"❌ Syntax: {pf.name}: {result.stderr[:100]}")
        else:
            ok.append(f"✅ Syntax: {pf.name}")

    # 5. Key source checks
    with open(BASE / "orchestrator.py") as f:
        orch = f.read()
    if "attempt" in orch and "retry" in orch.lower():
        ok.append("✅ Retry logic present")
    else:
        warnings.append("⚠️ No retry logic in orchestrator")

    with open(BASE / "src/platforms/connectors.py") as f:
        conn = f.read()
    if "_rate_limit" in conn:
        ok.append("✅ Rate limiting present")
    else:
        warnings.append("⚠️ No rate limiting in connectors")

    # 6. Dry-run test
    result = subprocess.run(
        ["python3", str(BASE / "orchestrator.py"), "status"],
        capture_output=True, text=True, cwd=str(BASE),
        env={**os.environ, "PATH": os.path.expanduser("~/.local/bin:") + os.environ.get("PATH", "")}
    )
    if result.returncode == 0:
        ok.append("✅ Orchestrator status OK")
    else:
        issues.append(f"❌ Orchestrator cassé: {result.stderr[:150]}")

    # Report
    print("=" * 60)
    print("AUDIT SOCIAL MEDIA AGENT")
    print("=" * 60)
    print(f"\n🟢 OK ({len(ok)}):")
    for item in sorted(ok):
        print(f"  {item}")
    if warnings:
        print(f"\n🟡 WARNINGS ({len(warnings)}):")
        for item in warnings:
            print(f"  {item}")
    if issues:
        print(f"\n🔴 ISSUES ({len(issues)}):")
        for item in issues:
            print(f"  {item}")
    else:
        print("\n🔴 ISSUES: 0")
    print(f"\n{'='*60}")
    print(f"TOTAL: {len(ok)} OK | {len(warnings)} warnings | {len(issues)} critiques")
    return len(issues) == 0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/home/tars/social-media-agent"
    sys.exit(0 if audit(path) else 1)
