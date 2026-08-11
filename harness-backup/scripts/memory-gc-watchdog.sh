#!/bin/bash
set -euo pipefail
MEMORY_FILE="/home/tars/.hermes/memories/MEMORY.md"
MAX_CHARS=2200
WARN_THRESHOLD=75
CRIT_THRESHOLD=90
if [ ! -f "$MEMORY_FILE" ]; then exit 0; fi
CURRENT=$(wc -c < "$MEMORY_FILE" | tr -d ' ')
PCT=$(( CURRENT * 100 / MAX_CHARS ))
if [ "$PCT" -lt "$WARN_THRESHOLD" ]; then exit 0; fi
ENTRIES=$(grep -c '§' "$MEMORY_FILE" 2>/dev/null || echo 0)
ENTRIES=$(( ENTRIES + 1 ))
LONG_ENTRIES=$(awk 'BEGIN{RS="§"} length($0) > 150 {count++} END{print count+0}' "$MEMORY_FILE")
SECRET_ENTRIES=$(grep -cE '(cfat_|ghp_|sk-|token|password|api_key)' "$MEMORY_FILE" 2>/dev/null || echo 0)
if [ "$PCT" -ge "$CRIT_THRESHOLD" ]; then LEVEL="🔴 CRITIQUE"; ACTION="Compression automatique requise"; else LEVEL="🟡 ATTENTION"; ACTION="Nettoyage recommandé"; fi
echo "🧹 Memory GC — $LEVEL"
echo ""
echo "Mémoire: ${CURRENT}/${MAX_CHARS} chars (${PCT}%)"
echo "Entrées: ${ENTRIES} | Longues (>150c): ${LONG_ENTRIES} | Avec secrets: ${SECRET_ENTRIES}"
echo ""
echo "$ACTION — lancer compression via agent."
