#!/usr/bin/env bash
# scout_trigger.sh — Déclenche le scout LEC via webhook (local)
# Usage:
#   ./scout_trigger.sh "https://exemple.com/article"           # URL à analyser
#   ./scout_trigger.sh "EU clears 659M EUR for chip plants"     # Texte libre
#   ./scout_trigger.sh "$(cat article.txt)"                     # Contenu d'un fichier
#
# Le secret et l'URL sont lus depuis ~/.hermes/webhook_subscriptions.json
# si possible, sinon fallback sur les valeurs hardcoded ci-dessous.

set -euo pipefail

WEBHOOK_URL="http://localhost:8644/webhooks/lec-scout"

# Lire le secret depuis le fichier de subscriptions
SECRET=$(python3 -c "
import json, sys
try:
    with open('$HOME/.hermes/webhook_subscriptions.json') as f:
        subs = json.load(f)
    for name, cfg in subs.items():
        if 'lec-scout' in name:
            print(cfg.get('secret', ''))
            sys.exit(0)
except Exception:
    pass
print('')  # fallback vide
" 2>/dev/null)

if [ -z "$SECRET" ]; then
  echo "❌ Secret introuvable. Vérifie ~/.hermes/webhook_subscriptions.json ou hardcodez-le."
  exit 1
fi

if [ $# -eq 0 ]; then
  echo "Usage: $0 <URL ou texte du signal>"
  echo "Exemples:"
  echo "  $0 \"https://www.digitimes.com/news/...\""
  echo "  $0 \"TSMC annonce 659M EUR subsidies\""
  exit 1
fi

SIGNAL="$1"

# Détecter si c'est une URL
if [[ "$SIGNAL" =~ ^https?:// ]]; then
  URL="$SIGNAL"
  SIGNAL_TEXT="(voir URL)"
else
  URL=""
  SIGNAL_TEXT="$SIGNAL"
fi

# Construire le payload JSON
BODY=$(python3 -c "
import json, sys
print(json.dumps({
    'event_type': 'signal',
    'signal': sys.argv[1],
    'url': sys.argv[2],
    'source': 'manual'
}))
" "$SIGNAL_TEXT" "$URL")

# Signer (V1 legacy: HMAC-SHA256 du body brut)
SIG=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $NF}')

# POST
echo "→ Envoi au scout..."
RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: $SIG" \
  -d "$BODY")

echo "← $RESPONSE"

# Vérifier acceptation
if echo "$RESPONSE" | grep -q "accepted"; then
  echo "✅ Scout déclenché — verdict arrive sur Telegram"
else
  echo "❌ Échec — vérifie le gateway (hermes gateway run) ou le format du payload"
  exit 1
fi
