#!/usr/bin/env python3
"""lib_rebooking.py — logique partagée du système de relance rebooking.

Centralise le calcul déterministe des relances + le rendu des messages depuis
les templates, pour que le chemin « revue » (gather-rebooking.py) et le chemin
« envoi » (send-outbox.py) ne dérivent JAMAIS l'un de l'autre.

Une seule source de vérité pour : qui relancer, pourquoi, et quel message envoyer.

Stdlib only. Aucune hallucination : tout est dérivé des données CSV + templates.
"""
import csv
import json
import os
import re
from datetime import date, datetime
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
SRC_DIR = HERMES_HOME / "rebooking-sources"
CLIENTS_CSV = SRC_DIR / "clients.csv"
TEMPLATES_MD = SRC_DIR / "templates.md"
CONFIG_JSON = SRC_DIR / "config.json"
OUTBOX_JSON = SRC_DIR / "outbox.json"
HOLD_FILE = SRC_DIR / "HOLD"
SEND_LOG = SRC_DIR / "send-log.jsonl"
SENT_ARCHIVE = SRC_DIR / "outbox-sent"

# Priorité quand un même client a plusieurs relances (on n'envoie qu'un message combiné).
PRIORITY = ["REBOOKING", "ANNIVERSAIRE", "VACCINATION", "SAISON"]


# ---------------------------------------------------------------- helpers dates
def parse_d(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def age_years(bday, today=None):
    today = today or date.today()
    if not bday:
        return None
    a = today.year - bday.year
    if (today.month, today.day) < (bday.month, bday.day):
        a -= 1
    return a


def days_to_birthday(bday, today=None):
    """Jours avant le prochain anniversaire (0 si aujourd'hui)."""
    today = today or date.today()
    if not bday:
        return None
    this_year = bday.replace(year=today.year)
    if this_year < today:
        this_year = this_year.replace(year=today.year + 1)
    return (this_year - today).days


# ---------------------------------------------------------------- chargement
def load_config():
    """Config du salon (nom, transport par défaut, etc.). Defaults sûrs."""
    defaults = {
        "salon_name": "Salon Toutou",
        "default_transport": "dry-run",
        "priority_order": PRIORITY,
        "whatsapp": {"api_version": "v20.0"},
    }
    if CONFIG_JSON.exists():
        try:
            cfg = json.loads(CONFIG_JSON.read_text(encoding="utf-8"))
            defaults.update(cfg)
        except Exception as e:
            print(f"⚠ config.json illisible ({e}), utilisation des défauts", flush=True)
    return defaults


def load_clients():
    rows = []
    if not CLIENTS_CSV.exists():
        return rows
    with CLIENTS_CSV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def parse_templates():
    """Découpe templates.md en {TYPE: template_text}.

    Attend des sections '## TYPE'. La première ligne non-vide après '##' est le template.
    """
    tpl = {}
    if not TEMPLATES_MD.exists():
        return tpl
    text = TEMPLATES_MD.read_text(encoding="utf-8")
    # split sur les titres ##
    parts = re.split(r"^##\s+(\w[^\n]*)", text, flags=re.MULTILINE)
    # parts = [pre, "REBOOKING (reponctuel)", body1, "ANNIVERSAIRE...", body2, ...]
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        type_key = header.split("(")[0].strip().upper()
        # première ligne non-vide du body = le template
        line = None
        for ln in body.splitlines():
            ln = ln.strip()
            if ln:
                line = ln
                break
        if line:
            tpl[type_key] = line
    return tpl


def normalize_phone(raw):
    """Retourne E.164 sans espaces : '+41 79 123 45 67' -> '+41791234567'."""
    if not raw:
        return None
    s = re.sub(r"[\s\-.()]", "", raw.strip())
    if not s:
        return None
    if not s.startswith("+"):
        # assume local CH -> +41
        if s.startswith("00"):
            s = "+" + s[2:]
        elif s.startswith("0"):
            s = "+41" + s[1:]
        else:
            s = "+" + s
    return s


# ---------------------------------------------------------------- calcul relances
def compute_reminders(today=None):
    """Retourne la liste des relances déterministes pour `today` (date).

    Chaque relance : dict(pet, owner, phone, breed, coat, service, last, days_since,
                          notes, age, bday, type, why).
    Réplique exactement la logique de gather-rebooking.py d'origine.
    """
    today = today or date.today()
    rows = load_clients()
    reminders = []
    for r in rows:
        pet = (r.get("pet_name") or "").strip()
        owner = (r.get("owner_name") or "").strip()
        if not pet or not owner:
            continue
        phone = (r.get("phone") or "").strip()
        breed = (r.get("breed") or "").strip()
        coat = (r.get("coat_type") or "").strip()
        service = (r.get("service") or "").strip()
        notes = (r.get("notes") or "").strip()
        last = parse_d(r.get("last_service"))
        try:
            interval_w = int(r.get("interval_weeks") or 0)
        except ValueError:
            interval_w = 0
        bday = parse_d(r.get("birthday"))

        days_since = (today - last).days if last else None
        client = {
            "pet": pet, "owner": owner, "phone": phone, "breed": breed, "coat": coat,
            "service": service, "last": str(last) if last else "?",
            "days_since": days_since, "notes": notes,
            "age": age_years(bday, today),
            "bday": bday.strftime("%d/%m") if bday else "?",
        }

        if days_since is not None and interval_w and days_since >= interval_w * 7:
            reminders.append({**client, "type": "REBOOKING",
                "why": f"{days_since}j depuis dernier toilettage (intervalle cible {interval_w} sem)"})

        if days_since is not None and days_since > 180:
            reminders.append({**client, "type": "VACCINATION",
                "why": f"{days_since // 30} mois sans venue — vérifier vaccins"})

        if bday:
            d = days_to_birthday(bday, today)
            if d is not None and 0 <= d <= 3:
                reminders.append({**client, "type": "ANNIVERSAIRE",
                    "why": f"Anniv. dans {d}j ({bday.strftime('%d/%m')}) — {age_years(bday, today)} ans"})

        if today.month in (6, 7, 8) and coat in ("long", "double") and (days_since is None or days_since < interval_w * 7 - 28):
            reminders.append({**client, "type": "SAISON",
                "why": f"été + poil {coat} ({breed}) — tonte légère"})
    return reminders


# ---------------------------------------------------------------- rendu messages
def _month_genitive(months):
    return f"{months} mois" if months else "plusieurs mois"


def render_message(template, reminder, config):
    """Substitue les placeholders du template avec les données du client.

    Placeholders supportés : {owner}, {pet}, {service}, {salon}, {age}, {months}.
    Les champs absents sont remplacés par une valeur vide (pas d'erreur).
    """
    salon = config.get("salon_name", "Salon Toutou")
    months = (reminder.get("days_since") or 0) // 30
    vals = {
        "owner": reminder.get("owner", ""),
        "pet": reminder.get("pet", ""),
        "service": reminder.get("service", ""),
        "salon": salon,
        "age": str(reminder.get("age") or ""),
        "months": str(months),
    }
    out = template
    for k, v in vals.items():
        out = out.replace("{" + k + "}", v)
    return out


def build_outbox(reminders, templates, config, today=None):
    """Groupe les relances par téléphone (1 message WhatsApp par client) et rend
    le message final. Retourne une liste d'items outbox prêts à l'envoi :

        {to, pet, owner, types: [...], message, created_at}

    Règle de combinaison : si un même téléphone a plusieurs relances, on prend le
    template du type de plus haute priorité, et on ajoute une ligne courte pour
    chaque raison secondaire.
    """
    today = today or date.today()
    by_phone = {}
    for r in reminders:
        by_phone.setdefault(r["phone"], []).append(r)

    priority = config.get("priority_order", PRIORITY)

    outbox = []
    for phone, items in by_phone.items():
        # type primaire = plus haute priorité parmi les items
        items_sorted = sorted(items, key=lambda x: priority.index(x["type"]) if x["type"] in priority else 99)
        primary = items_sorted[0]
        tpl = templates.get(primary["type"])
        if not tpl:
            continue  # type sans template -> skip (sécurité)
        msg = render_message(tpl, primary, config)

        # lignes secondaires si >1 relance pour ce téléphone
        if len(items_sorted) > 1:
            extras = []
            for it in items_sorted[1:]:
                extras.append(f"• {it['type'].lower()} : {it['why']}")
            msg = msg.rstrip() + "\n\nAussi : " + " / ".join(extras) + "."

        outbox.append({
            "to": normalize_phone(phone),
            "to_raw": phone,
            "pet": primary["pet"],
            "owner": primary["owner"],
            "types": [it["type"] for it in items_sorted],
            "message": msg,
            "created_at": today.isoformat(),
        })
    return outbox


def write_outbox(outbox, today=None):
    """Écrit outbox.json (source de vérité pour l'envoi). Écrase la veille."""
    today = today or date.today()
    payload = {
        "date": today.isoformat(),
        "count": len(outbox),
        "items": outbox,
    }
    OUTBOX_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload
