#!/usr/bin/env bash
set -euo pipefail

# === Multi-Site Hash-Diff Watchdog ===
# Monitors multiple URLs by storing SHA-256 hashes.
# SILENT when nothing changed. ALERTS on any page modification.
#
# Usage: Place in ~/.hermes/scripts/ or <project>/bin/
#        Create cron: no_agent=true, script=multi-site-hash-watchdog.sh
#
# First run = baseline (stores hashes, stays silent).
# Subsequent runs = alert only if a hash changed.

STATE_DIR="/tmp/.veille-watchdog"
mkdir -p "$STATE_DIR"

# === CONFIG — Add your monitored URLs here ===
# Format: "url"
SITES=(
  "https://kie.ai/seedance-2-5"
  "https://kie.ai"
  "https://kinetix.tech"
  "https://wan.video"
  "https://kling.kuaishou.com"
)
# =============================================

CHANGES=""

for url in "${SITES[@]}"; do
  # Create a safe filename from URL
  safe_name=$(echo "$url" | md5sum | cut -d' ' -f1)
  hash_file="$STATE_DIR/${safe_name}"

  current_hash=$(curl -sL --max-time 15 "$url" 2>/dev/null | sha256sum | cut -d' ' -f1)

  if [ -z "$current_hash" ]; then
    # curl failed — don't false-positive, but note blind spot
    old_hash=$(cat "$hash_file" 2>/dev/null || echo "none")
    if [ "$old_hash" != "none" ]; then
      CHANGES+="⚠️ Cannot reach $url — check failed. Blind spot active.\n"
    fi
    continue
  fi

  old_hash=$(cat "$hash_file" 2>/dev/null || echo "none")

  if [ "$current_hash" != "$old_hash" ]; then
    if [ "$old_hash" != "none" ]; then
      CHANGES+="🔄 $url — page modified\n"
    fi
    echo "$current_hash" > "$hash_file"
  fi
done

if [ -n "$CHANGES" ]; then
  echo "📡 Watchdog — changes detected:"
  echo ""
  echo -e "$CHANGES"
  echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
fi
# Empty CHANGES = silent (exit 0, no output)
