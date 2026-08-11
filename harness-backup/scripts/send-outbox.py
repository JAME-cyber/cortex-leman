#!/usr/bin/env python3
"""send-outbox.py — Tier 2 : envoi WhatsApp des relances validées.

Lit ~/.hermes/rebooking-sources/outbox.json (produit par gather-rebooking.py à 09h00)
et envoie chaque message. Conçu comme un cron `--no-agent` : son stdout est livré
tel quel (le reçu d'envoi arrive sur Telegram).

SÉCURITÉ :
  - DRY-RUN par défaut. N'envoie jamais réellement tant que --transport whatsapp
    (ou config default_transport=whatsapp) + creds env ne sont pas en place.
  - HOLD : si ~/.hermes/rebooking-sources/HOLD existe, l'envoi est suspendu
    (veto du toiletteur). Le reçu signale la suspension.
  - WHATSAPP_RECIPIENT_OVERRIDE : si défini, TOUT est redirigé vers ce numéro
    (indispensable en démo/test pour ne pas texter les numéros placeholders).

TRANSPORTS :
  - dry-run : imprime le reçu, n'appelle aucune API. (défaut)
  - whatsapp : WhatsApp Business Cloud API (Meta). Vars env :
      WHATSAPP_TOKEN          (access token, requis)
      WHATSAPP_PHONE_ID       (phone_number_id, requis)
      WHATSAPP_RECIPIENT_OVERRIDE  (optionnel, redirige tout vers 1 numéro)
      WHATSAPP_API_VERSION    (défaut v20.0)

CYCLE DE VIE OUTBOX :
  Lu -> envoyé -> archivé dans outbox-sent/<ts>.json -> outbox.json vidé.
  Idempotent : si outbox vide, stdout = "[SILENT]" (le cron ne livre rien).

USAGE :
  python3 send-outbox.py                     # dry-run (reçu sur Telegram)
  python3 send-outbox.py --transport whatsapp # envoi réel
  python3 send-outbox.py --limit 1           # tester sur 1 message
  python3 send-outbox.py --no-hold-check     # ignorer le veto HOLD (urgence)
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_rebooking import HOLD_FILE, OUTBOX_JSON, SEND_LOG, SENT_ARCHIVE, load_config


def log_send(entry):
    SEND_LOG.parent.mkdir(parents=True, exist_ok=True)
    with SEND_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def archive_outbox(payload):
    SENT_ARCHIVE.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    arc = SENT_ARCHIVE / f"{ts}.json"
    arc.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return arc


# ---------------------------------------------------------------- transports
def transport_dry_run(item):
    """Simule l'envoi. Retourne (status, detail). N'appelle rien."""
    preview = item["message"].replace("\n", " ⏎ ")
    return ("dry-run", f"SIMULÉ → {item['to']} ({item['pet']}/{item['owner']}) : {preview[:80]}…")


def transport_whatsapp(item):
    """Envoie via WhatsApp Business Cloud API (Meta). Retourne (status, detail)."""
    token = os.environ.get("WHATSAPP_TOKEN")
    phone_id = os.environ.get("WHATSAPP_PHONE_ID")
    if not token or not phone_id:
        return ("error", "WHATSAPP_TOKEN/WHATSAPP_PHONE_ID manquants — envoi impossible")
    api_ver = os.environ.get("WHATSAPP_API_VERSION", "v20.0")
    to = os.environ.get("WHATSAPP_RECIPIENT_OVERRIDE") or item["to"]
    if not to or not to.startswith("+"):
        return ("error", f"numéro invalide : {item.get('to_raw')}")

    url = f"https://graph.facebook.com/{api_ver}/{phone_id}/messages"
    body = json.dumps({
        "messaging_product": "whatsapp",
        "to": to[1:],  # E.164 sans le '+'
        "type": "text",
        "text": {"body": item["message"][:4096]},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        wamid = data.get("messages", [{}])[0].get("id", "?")
        redir = f" [redirigé vers {to}]" if os.environ.get("WHATSAPP_RECIPIENT_OVERRIDE") else ""
        return ("sent", f"✓ {item['to']} ({item['pet']}){redir} — {wamid}")
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:200]
        return ("error", f"HTTP {e.code} → {item['to']} : {err}")
    except Exception as e:
        return ("error", f"exception → {item['to']} : {e}")


TRANSPORTS = {"dry-run": transport_dry_run, "whatsapp": transport_whatsapp}


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Envoie l'outbox rebooking (Tier 2).")
    ap.add_argument("--transport", choices=list(TRANSPORTS),
                    help="Force le transport (défaut : config.default_transport ou dry-run).")
    ap.add_argument("--limit", type=int, help="Limiter à N messages (test).")
    ap.add_argument("--no-hold-check", action="store_true",
                    help="Ignorer le fichier HOLD (urgence).")
    args = ap.parse_args()

    config = load_config()
    transport = args.transport or config.get("default_transport", "dry-run")

    # outbox absent ou vide -> silencieux (ne spamme pas Telegram)
    if not OUTBOX_JSON.exists():
        print("[SILENT]")
        return
    try:
        payload = json.loads(OUTBOX_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"⚠ outbox.json illisible : {e}")
        return
    items = payload.get("items", [])
    if not items:
        print("[SILENT]")
        return

    # veto HOLD
    if HOLD_FILE.exists() and not args.no_hold_check:
        hold_reason = HOLD_FILE.read_text(encoding="utf-8").strip() or "(sans motif)"
        print(f"⏸ ENVOI SUSPENDU — fichier HOLD présent : {hold_reason}")
        print(f"  {len(items)} message(s) en attente. Retirer HOLD pour reprendre, "
              f"ou relancer avec --no-hold-check.")
        return

    if args.limit:
        items = items[: args.limit]

    now_iso = datetime.now().isoformat(timespec="seconds")
    date = payload.get("date", "?")
    print(f"📨 ENVOI REBOOKING — {date} ({now_iso})")
    print(f"Transport : {transport} · {len(items)} message(s)")
    print("─" * 50)

    results = {"sent": 0, "dry-run": 0, "error": 0}
    for item in items:
        status, detail = TRANSPORTS[transport](item)
        results[status] = results.get(status, 0) + 1
        marker = {"sent": "→", "dry-run": "○", "error": "✗"}.get(status, "?")
        print(f"{marker} {detail}")
        log_send({
            "ts": now_iso, "transport": transport, "status": status,
            "to": item.get("to"), "to_raw": item.get("to_raw"),
            "pet": item.get("pet"), "owner": item.get("owner"),
            "types": item.get("types"),
            "msg_preview": item["message"][:120],
        })

    # archivage + clear outbox SEULEMENT si pas d'erreur en envoi réel
    real = transport != "dry-run"
    archived = None
    if real and results.get("error", 0) == 0:
        archived = archive_outbox(payload)
        OUTBOX_JSON.write_text('{"date":"","count":0,"items":[]}', encoding="utf-8")

    print("─" * 50)
    recap = " · ".join(f"{k}: {v}" for k, v in results.items() if v)
    print(f"Récap : {recap}")
    if real and results.get("error", 0):
        print("⚠ erreurs — outbox CONSERVÉ (retry possible). Corriger puis relancer.")
    elif real:
        print(f"✓ Outbox archivé : {archived.name if archived else '—'}")
    else:
        print("(dry-run : outbox conservé pour un envoi réel ultérieur)")


if __name__ == "__main__":
    main()
