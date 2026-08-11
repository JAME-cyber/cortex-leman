#!/usr/bin/env bash
# A2A Pipeline Filter Script
# Receives webhook payload as JSON on stdin
# Returns: empty stdout = ignore, non-empty = process, [SILENT] = silent skip
#
# Logic: only trigger pipeline for signals tagged "research" or "deep-dive"
# Everything else gets passed through to the agent normally

set -euo pipefail

PAYLOAD=$(cat)

# Extract event type from payload
EVENT_TYPE=$(echo "$PAYLOAD" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Check for various signal formats
    event = data.get('event', data.get('type', data.get('signal_type', '')))
    tags = data.get('tags', [])
    if isinstance(tags, str):
        tags = [tags]
    if 'research' in str(event).lower() or 'deep-dive' in str(event).lower():
        print('research')
    elif any('research' in str(t).lower() or 'deep' in str(t).lower() for t in tags):
        print('research')
    elif data.get('url') or data.get('source'):
        print('content')
    else:
        print('pass')
except:
    print('pass')
" 2>/dev/null || echo "pass")

if [ "$EVENT_TYPE" = "research" ]; then
    # Pass through - agent will handle with A2A + grounded-citations
    echo "$PAYLOAD"
elif [ "$EVENT_TYPE" = "content" ]; then
    # Content signal - use grounded-citations skill
    echo "$PAYLOAD"
else
    # Not interesting - skip silently
    echo "[SILENT]"
fi
