#!/usr/bin/env python3
# gather-daily-review.py — collecte le contexte du jour pour le rituel de planification 17h.
# stdout est injecté tel quel dans le prompt de l'agent (Hermes cron "daily-planning").
#
# Logique (déterministe, zéro hallucination) — pattern maison "script stdout injecté" :
# le script RASSEMBLE les faits bruts du jour, le LLM DÉCIDE des time blocks de demain.
#
# Sources collectées :
#   1. Sessions pi du jour   → intentions (messages user) + volume assistant
#   2. Runs cron Hermes       → ce que l'auto a fait today (+ échecs à investiguer)
#   3. Commits git du jour    → ce qui a réellement ship, par projet
#   4. Kanban ouvert          → backlog vivant (todo / blocked / scheduled)
#
# Tout est défensif : si une source manque, on l'omet proprement sans planter.
from __future__ import annotations
import ast
import json
import os
import sqlite3
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

HOME = Path.home()
PI_SESSIONS = HOME / ".pi" / "agent" / "sessions"
HERMES = HOME / ".hermes"
EXEC_DB = HERMES / "cron" / "executions.db"
JOBS_FILE = HERMES / "cron" / "jobs.json"
KANBAN_CUR = HERMES / "kanban" / "current"
TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)

# Bornes : on ne scanne que les sous-dossiers top-level de ~ (pas de récursion profonde).
GIT_SCAN_ROOTS = [HOME] + [HOME / "cortex-leman-v5", HOME / "worldmonitor"]

WEEKDAYS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


# ───────────────────────── helpers ─────────────────────────
def _safe_literal(s: str):
    try:
        return ast.literal_eval(s)
    except Exception:
        return None


def _is_today(iso_ts: str | None) -> bool:
    """Accepte timestamps ISO ou epoch secondes/int."""
    if not iso_ts:
        return False
    try:
        if isinstance(iso_ts, str):
            dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00")).astimezone()
        else:
            dt = datetime.fromtimestamp(int(iso_ts)).astimezone()
        return dt.date() == TODAY
    except Exception:
        return False


# ───────────────────────── 1. pi sessions ─────────────────────────
def collect_pi() -> dict:
    out = {"sessions": 0, "user_msgs": [], "assist_turns": 0, "cwds": set()}
    if not PI_SESSIONS.exists():
        return out
    files = list(PI_SESSIONS.rglob("*.jsonl"))
    for f in files:
        # Filtre : fichier modifié aujourd'hui (mtime).
        try:
            if datetime.fromtimestamp(f.stat().st_mtime).date() != TODAY:
                continue
        except Exception:
            continue
        out["sessions"] += 1
        try:
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("cwd"):
                    out["cwds"].add(d["cwd"])
                if d.get("type") != "message":
                    continue
                m = d.get("message")
                if isinstance(m, str):
                    m = _safe_literal(m)
                if not isinstance(m, dict):
                    continue
                role = m.get("role")
                content = m.get("content")
                if role == "user" and isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            txt = (c.get("text") or "").strip()
                            # On garde les vraies intentions, on jette le bruit system/tool.
                            if txt and not txt.startswith("<") and not txt.startswith("[Request"):
                                out["user_msgs"].append(txt[:200])
                elif role == "assistant":
                    out["assist_turns"] += 1
        except Exception:
            continue
    return out


# ───────────────────────── 2. cron runs ─────────────────────────
def collect_cron() -> dict:
    out = {"total": 0, "ok": 0, "failed": []}
    # Map job_id -> name
    names: dict[str, str] = {}
    try:
        jj = json.loads(JOBS_FILE.read_text())
        for j in jj.get("jobs", []):
            names[j.get("id", "")] = j.get("name", j.get("id", ""))
    except Exception:
        pass
    if not EXEC_DB.exists():
        return out
    try:
        db = sqlite3.connect(f"file:{EXEC_DB}?mode=ro", uri=True)
        rows = db.execute(
            "select job_id, status, error, started_at from executions "
            "where date(started_at)=date(?)",
            (TODAY.isoformat(),),
        ).fetchall()
        out["total"] = len(rows)
        for job_id, status, error, started in rows:
            if status in ("ok", "success", "completed"):
                out["ok"] += 1
            elif status in ("error", "failed"):
                out["failed"].append(
                    (names.get(job_id, job_id or "?"), (error or "")[:120])
                )
    except Exception:
        pass
    return out


# ───────────────────────── 3. git commits du jour ─────────────────────────
def collect_git() -> list[tuple[str, str, str]]:
    """Retourne [(repo, hash, sujet)]. Borné aux dossiers top-level de ~."""
    results: list[tuple[str, str, str]] = []
    seen: set[Path] = set()
    roots = set()
    for root in GIT_SCAN_ROOTS:
        if not root.exists():
            continue
        for child in root.iterdir():
            if (child / ".git").is_dir():
                roots.add(child)
        # on accepte aussi root lui-même si c'est un repo
    for repo in sorted(roots):
        if repo in seen:
            continue
        seen.add(repo)
        try:
            log = subprocess.run(
                ["git", "-C", str(repo), "log", "--since", f"{TODAY.isoformat()} 00:00",
                 "--pretty=format:%h|%s"],
                capture_output=True, text=True, timeout=8,
            ).stdout.strip()
        except Exception:
            continue
        if not log:
            continue
        for line in log.splitlines():
            h, _, subj = line.partition("|")
            results.append((repo.name, h, subj[:90]))
    return results


# ───────────────────────── 4. kanban ouvert ─────────────────────────
def collect_kanban() -> list[tuple[str, str, str]]:
    """Retourne [(status, id, title)] pour les tâches non terminées."""
    out: list[tuple[str, str, str]] = []
    board_slug = None
    try:
        board_slug = KANBAN_CUR.read_text().strip()
    except Exception:
        return out
    db_path = HERMES / "kanban" / "boards" / board_slug / "kanban.db"
    if not db_path.exists():
        return out
    try:
        db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        rows = db.execute(
            "select status, id, title from tasks "
            "where status not in ('done','completed','cancelled','archived') "
            "order by case status when 'blocked' then 0 when 'todo' then 1 "
            "when 'in_progress' then 2 else 3 end, id",
        ).fetchall()
        out = [(r[0], r[1], r[2]) for r in rows]
    except Exception:
        pass
    return out


# ───────────────────────── rendu ─────────────────────────
def main() -> int:
    pi = collect_pi()
    cron = collect_cron()
    git = collect_git()
    kanban = collect_kanban()

    print(f"===== REVUE QUOTIDIENNE — {TODAY.isoformat()} ({WEEKDAYS_FR[TODAY.weekday()]}) =====")
    print(f"À planifier : DEMAIN {TOMORROW.isoformat()} ({WEEKDAYS_FR[TOMORROW.weekday()]})")
    print()
    print("▌ ACTIVITÉ DU JOUR")
    print(f"  • pi : {pi['sessions']} session(s), {len(pi['user_msgs'])} message(s) user, "
          f"{pi['assist_turns']} tour(s) assistant")
    if pi["cwds"]:
        cwds = sorted(c.name for c in [Path(p) for p in pi["cwds"]])
        print(f"  • projets touchés (pi) : {', '.join(cwds[:8])}")
    print(f"  • cron Hermes : {cron['total']} run(s) aujourd'hui "
          f"({cron['ok']} ok, {len(cron['failed'])} échec(s))")
    print(f"  • git : {len(git)} commit(s) aujourd'hui")
    print()

    if pi["user_msgs"]:
        print("▌ INTENTIONS PI DU JOUR (messages user, dans l'ordre)")
        for t in pi["user_msgs"][:20]:
            print(f"  • {t}")
        print()

    if git:
        print("▌ COMMITS DU JOUR")
        by_repo: dict[str, list[tuple[str, str]]] = {}
        for repo, h, subj in git:
            by_repo.setdefault(repo, []).append((h, subj))
        for repo in sorted(by_repo):
            for h, subj in by_repo[repo]:
                print(f"  • [{repo}] {h} {subj}")
        print()

    if cron["failed"]:
        print("▌ ⚠️ CRON EN ÉCHEC AUJOURD'HUI (à investiguer / reprogrammer)")
        for name, err in cron["failed"][:10]:
            print(f"  • {name} : {err}")
        print()

    if kanban:
        print("▌ KANBAN OUVERT (backlog vivant)")
        # plafonné à 20 pour rester lisible
        for status, tid, title in kanban[:20]:
            tag = {"todo": "TODO", "blocked": "BLOCKED", "in_progress": "WIP",
                   "scheduled": "SCHED"}.get(status, status.upper())
            print(f"  [{tag:<7}] {title[:110]}")
        if len(kanban) > 20:
            print(f"  … +{len(kanban) - 20} autre(s) tâche(s) ouverte(s)")
        print()

    print("===== FIN CONTEXTE — analyse et propose les time blocks de demain =====")
    return 0


if __name__ == "__main__":
    sys.exit(main())
