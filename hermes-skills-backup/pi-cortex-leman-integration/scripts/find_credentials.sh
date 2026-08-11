#!/usr/bin/env bash
# find_credentials.sh — Locate a credential/API key across the Hermes+Pi dual-stack.
#
# Usage:
#   ./find_credentials.sh xai
#   ./find_credentials.sh openrouter
#   ./find_credentials.sh grok
#
# Exits 0 if found, 1 if not. Prints every hit with its source location.
# Designed to be re-run by the agent instead of hand-typing 10 greps.

set -u
QUERY="${1:-}"
if [ -z "$QUERY" ]; then
  echo "Usage: $0 <provider-or-keyword>" >&2
  exit 2
fi
Q="$(printf '%s' "$QUERY" | tr '[:lower:]' '[:upper:]')"
ql="$(printf '%s' "$QUERY" | tr '[:upper:]' '[:lower:]')"

found=0
hit() {
  echo "✓ $1"
  found=1
}

echo "=== Searching for '$QUERY' across Hermes + Pi dual-stack ==="
echo ""

# 1. Hermes .env (uppercase key names)
if [ -f "$HOME/.hermes/.env" ]; then
  if grep -qiE "^${Q}_API_KEY|^${Q}_TOKEN|${ql}" "$HOME/.hermes/.env" 2>/dev/null; then
    hit "Hermes .env ($HOME/.hermes/.env)"
  fi
fi

# 2. Hermes config.yaml — both key blocks and config-only references
if [ -f "$HOME/.hermes/config.yaml" ]; then
  matches=$(grep -niE "${ql}" "$HOME/.hermes/config.yaml" 2>/dev/null)
  if [ -n "$matches" ]; then
    hit "Hermes config.yaml ($HOME/.hermes/config.yaml)"
    echo "$matches" | sed 's/^/    /'
    echo "    NOTE: config.yaml may reference a provider in a config block WITHOUT storing the key."
    echo "    Verify an actual XAI_API_KEY (or similar) env var exists, not just a tts.xai: block."
  fi
fi

# 3. Hermes auth.json credential_pool (does NOT show secrets, only labels/sources)
if [ -f "$HOME/.hermes/auth.json" ]; then
  if grep -qiE "${ql}" "$HOME/.hermes/auth.json" 2>/dev/null; then
    hit "Hermes auth.json credential_pool ($HOME/.hermes/auth.json)"
    /usr/bin/python3 -c "
import json,sys
with open('$HOME/.hermes/auth.json') as f: d=json.load(f)
for prov,creds in d.get('credential_pool',{}).items():
    if '${ql}'.lower() in prov.lower(): continue
    for c in creds:
        lbl=(c.get('label','') or '').lower()
        src=(c.get('source','') or '').lower()
        if '${ql}'.lower() in lbl or '${ql}'.lower() in src:
            print(f'    {prov}: {c.get(\"label\")} (source: {c.get(\"source\")})')
" 2>/dev/null | grep -i "${ql}" | sed 's/^/    /' || true
  fi
fi

# 4. Runtime environment variables
env_matches=$(env | grep -iE "${ql}" 2>/dev/null)
if [ -n "$env_matches" ]; then
  hit "Runtime environment variables"
  printf '%s\n' "$env_matches" | sed 's/=.*/=<redacted>/' | sed 's/^/    /'
fi

# 5. Pi settings.json (stores keys in PLAINTEXT in modelRegistry)
if [ -f "$HOME/.pi/settings.json" ]; then
  if grep -qiE "${ql}" "$HOME/.pi/settings.json" 2>/dev/null; then
    hit "Pi settings.json ($HOME/.pi/settings.json) — keys may be in PLAINTEXT here"
  fi
fi

# 6. Pi agent/models.json, settings.json, auth.json
for f in "$HOME/.pi/agent/models.json" "$HOME/.pi/agent/settings.json" "$HOME/.pi/agent/auth.json"; do
  if [ -f "$f" ] && grep -qiE "${ql}" "$f" 2>/dev/null; then
    hit "Pi $f"
  fi
done

# 7. Shell init files
for f in "$HOME/.bashrc" "$HOME/.profile" "$HOME/.bash_aliases" "$HOME/.zshrc"; do
  if [ -f "$f" ] && grep -qiE "${ql}" "$f" 2>/dev/null; then
    hit "Shell init: $f"
  fi
done

echo ""
if [ "$found" -eq 1 ]; then
  echo "=== FOUND — review hits above ==="
  exit 0
else
  echo "=== NOT FOUND — '$QUERY' is not present in any known credential location ==="
  echo ""
  echo "If the user believes the credential exists, common confusion patterns:"
  echo "  • A config block references the provider but no key is stored (e.g. tts.xai: in config.yaml without XAI_API_KEY)."
  echo "  • A model name contains the provider word (e.g. 'grok-4' as x_search.model via OpenRouter — that is NOT a direct xAI key)."
  echo "  • Audio/video output was produced via a DIFFERENT provider (edge-tts, Kie.ai) but attributed to the named provider."
  exit 1
fi
