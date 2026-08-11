#!/usr/bin/env python3
"""gather-rebooking.py — moteur de calcul des relances rebooking (revue 09h00).

Wrapper mince autour de lib_rebooking. Produit :
  1. stdout (human-readable) → injecté dans le prompt de l'agent Hermes.
     Format identique à la version d'origine (le prompt de l'agent en dépend).
  2. ~/.hermes/rebooking-sources/outbox.json → source de vérité machine pour
     l'envoi Tier 2 (send-outbox.py à 10h00).

Aucune hallucination : tout est dérivé des données. Stdlib only.
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib_rebooking import (
    compute_reminders, load_config, load_clients, write_outbox,
    build_outbox, parse_templates,
)

TODAY = date.today()


def main():
    clients = load_clients()
    reminders = compute_reminders(TODAY)

    # ---- stdout : rendu human-readable (préserve le format d'origine) ----
    print(f"===== RELANCES REBOOKING — {TODAY.isoformat()} =====")
    print(f"Total clients scannés : {len(clients)}")
    print(f"Relances aujourd'hui  : {len(reminders)}")
    print()
    if not reminders:
        print("AUCUNE relance aujourd'hui. Reviendra demain.")
        print("===== FIN =====")
        _write_outbox_safe(reminders)
        return

    by_type = {}
    for rem in reminders:
        by_type.setdefault(rem["type"], []).append(rem)

    for t in ("REBOOKING", "ANNIVERSAIRE", "VACCINATION", "SAISON"):
        items = by_type.get(t, [])
        if not items:
            continue
        print(f"----- {t} ({len(items)}) -----")
        for i, r in enumerate(items, 1):
            print(f"{i}. {r['pet']} — {r['owner']} ({r['phone']})")
            print(f"   {r['breed']} / poil {r['coat']} | dernière venue {r['last']} ({r['days_since']}j)")
            if r["age"] is not None:
                print(f"   âge : {r['age']} ans")
            if r["notes"]:
                print(f"   ⚠ {r['notes']}")
            print(f"   → {r['why']}")
        print()

    print("===== FIN (l'agent personnalise les messages via templates.md) =====")

    _write_outbox_safe(reminders)


def _write_outbox_safe(reminders):
    """Écrit l'outbox machine pour l'envoi Tier 2. Ne lève jamais (le stdout agent
    prime). Log discret sur stderr pour le debug ops."""
    try:
        config = load_config()
        templates = parse_templates()
        outbox = build_outbox(reminders, templates, config, TODAY)
        payload = write_outbox(outbox, TODAY)
        sys.stderr.write(f"[outbox] {payload['count']} message(s) prêt(s) → outbox.json\n")
    except Exception as e:
        sys.stderr.write(f"[outbox] écriture ignorée : {e}\n")


if __name__ == "__main__":
    main()
