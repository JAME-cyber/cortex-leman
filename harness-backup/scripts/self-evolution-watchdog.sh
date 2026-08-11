#!/bin/bash
# Self-Evolution watchdog cron
# Runs every 2h. Silent unless patches are accepted by the judge.
# Output (stdout) is delivered verbatim to the user.

cd ~/.hermes/self-evolution

# Run dry-run scan (last 2 days to catch corrections from recent sessions)
OUTPUT=$(python3 self_evolve.py --days 2 2>&1)

# Check if any patches were accepted
ACCEPTED=$(echo "$OUTPUT" | grep -oP '\d+(?= accepted)' | tail -1)

if [ "$ACCEPTED" = "0" ] || [ -z "$ACCEPTED" ]; then
    # No accepted patches — stay silent (watchdog pattern)
    exit 0
fi

# Patches accepted — notify user
SCANNED=$(echo "$OUTPUT" | grep -oP '\d+(?= scanned)' | tail -1)
PROPOSED=$(echo "$OUTPUT" | grep -oP '\d+(?= proposed)' | tail -1)

# Extract accepted patch details
PATCHES=$(echo "$OUTPUT" | awk '
    /JUDGE.*verdict=accept/ { found=1 }
    found && /Correction:/ { gsub(/.*Correction: "/, ""); gsub(/".*/, ""); print "  • " substr($0, 1, 120) }
')

cat << EOF
🧬 Self-Evolution: ${ACCEPTED} patch(es) ready for review

${PATCHES}

📊 ${SCANNED} scanned | ${PROPOSED} proposed | ${ACCEPTED} accepted

Apply: python3 ~/.hermes/self-evolution/self_evolve.py --days 2 --apply
EOF
