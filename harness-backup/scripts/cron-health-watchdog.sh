#!/bin/bash
# Cron Health Watchdog — SILENT si tout va bien, ALERTE si jobs en erreur
set -euo pipefail

OUTPUT=$(hermes cron list 2>&1)

# Parse: chercher lignes "Last run:" qui ne finissent pas par "ok"
ERRORS=$(echo "$OUTPUT" | python3 -c "
import sys, re

lines = sys.stdin.read().split('\n')
errors = []
current_name = '?'
current_id = '?'

for line in lines:
    s = line.strip()
    m = re.match(r'^([0-9a-f]{12})\s+\[(\w+)\]', s)
    if m:
        current_id = m.group(1)
        current_name = '?'
    elif 'Name:' in s:
        current_name = s.split('Name:', 1)[1].strip()
    elif 'Last run:' in s:
        # Check if it doesn't end with 'ok'
        if not s.rstrip().endswith('ok'):
            errors.append(f'  • {current_name} ({current_id[:12]}): {s}')

if errors:
    print(f'🚨 CRON HEALTH — {len(errors)} job(s) en erreur:')
    print('\n'.join(errors))
    print()
    print('Vérifie: hermes cron list')
")

if [ -n "$ERRORS" ]; then
    echo "$ERRORS"
fi
