#!/usr/bin/env python3
# gather-one-on-one.py — collecte le contexte du/des 1:1 manager DUS aujourd'hui.
# stdout est injecté tel quel dans le prompt de l'agent (Hermes cron).
#
# Logique (déterministe, zéro hallucination) :
#   - Chaque fiche ~/.hermes/one-on-one-sources/directs/<slug>.md a un frontmatter
#     avec `next_1on1: YYYY-MM-DD` (la date du prochain point).
#   - Le script ne remonte QUE les directs dont le prochain 1:1 est <= aujourd'hui.
#   - Si `next_1on1` est absent, il fallback sur la cadence (weekly = dû si le
#     dernier 1:1 noté dans le corps date de >= 7 jours).
#
# C'est exactement le pattern Hermes "script stdout injecté" : le déterministe
# décide QUI est dû, le LLM décide COMMENT préparer le point.
from __future__ import annotations
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
SRC = HERMES_HOME / "one-on-one-sources"
DIRECTS = SRC / "directs"
TODAY = date.today()


def parse_frontmatter(text: str) -> tuple[dict, str]:
    fm: dict[str, str] = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return fm, text
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm, text[m.end():]


def parse_date(s: str):
    s = s.strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def is_due(fm: dict, body: str) -> tuple[bool, str]:
    """Retourne (dû, raison)."""
    cadence = fm.get("cadence", "weekly").strip().lower()
    next_dt = parse_date(fm.get("next_1on1", ""))
    if next_dt:
        if next_dt <= TODAY:
            delta = (TODAY - next_dt).days
            return True, f"1:1 prévu le {next_dt.isoformat()} ({'aujourd’hui' if delta == 0 else f'il y a {delta}j'})"
        return False, f"prochain 1:1 le {next_dt.isoformat()}"
    # Pas de next_1on1 → fallback cadence
    dates_in_body = re.findall(r"\d{4}-\d{2}-\d{2}", body)
    last_dt = parse_date(dates_in_body[-1]) if dates_in_body else None
    if last_dt is None:
        return True, "aucun 1:1 enregistré → à initier"
    if cadence == "weekly":
        delta = (TODAY - last_dt).days
        if delta >= 7:
            return True, f"dernier 1:1 le {last_dt.isoformat()} (il y a {delta}j, cadence weekly)"
        return False, f"dernier 1:1 le {last_dt.isoformat()} (il y a {delta}j, pas encore dû)"
    if cadence == "biweekly":
        delta = (TODAY - last_dt).days
        if delta >= 14:
            return True, f"dernier 1:1 le {last_dt.isoformat()} (il y a {delta}j, cadence biweekly)"
        return False, f"dernier 1:1 le {last_dt.isoformat()} (il y a {delta}j, pas encore dû)"
    # cadence inconnue → on ne force pas
    return False, f"cadence « {cadence} » non reconnue, next_1on1 manquant"


def main() -> int:
    if not DIRECTS.is_dir():
        print(f"(dossier directs manquant : {DIRECTS})")
        print("Crée des fiches dans one-on-one-sources/directs/<slug>.md (voir README).")
        return 0

    due: list[tuple[str, dict, str, str]] = []
    not_due: list[tuple[str, str]] = []
    for f in sorted(DIRECTS.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        name = fm.get("name", f.stem)
        ok, reason = is_due(fm, body)
        if ok:
            due.append((name, fm, body, reason))
        else:
            not_due.append((name, reason))

    print(f"===== CONTEXTE 1:1 MANAGER — {TODAY.isoformat()} =====")
    print(f"{len(due)} 1:1 dû(s) aujourd’hui, {len(not_due)} non dû(s).\n")

    if not due:
        print("(Aucun 1:1 dû aujourd’hui.)")
        if not_due:
            print("\nRappel des prochaines échéances :")
            for name, reason in not_due:
                print(f"  • {name} — {reason}")
        print("\n===== FIN CONTEXTE =====")
        return 0

    for name, fm, body, reason in due:
        role = fm.get("role", "")
        goals = fm.get("quarterly_goal", "")
        header = f"----- {name}"
        if role:
            header += f"  ({role})"
        print(header + " -----")
        print(f"RAISON : {reason}")
        if goals:
            print(f"OBJECTIF TRIMESTRIEL : {goals}")
        print()
        print(body.strip())
        print()
    print("===== FIN CONTEXTE =====")
    return 0


if __name__ == "__main__":
    sys.exit(main())
