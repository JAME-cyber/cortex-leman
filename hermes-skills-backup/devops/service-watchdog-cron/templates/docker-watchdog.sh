#!/usr/bin/env bash
set -euo pipefail

# === Docker Compose Stack Watchdog ===
# Silent when all ACTIVE containers are healthy.
# Alerts with diagnosis (container states + last log lines) on state change.
# IGNORES containers in STOPPED_CONTAINERS (intentionally offline — won't alert).
# stdout = message delivered to chat. Empty = silence.
#
# Usage: Place in <project>/bin/docker-watchdog.sh
#        Create cron: no_agent=true, script=bin/docker-watchdog.sh, schedule=every 30m

# === CONFIG — Edit these ===
COMPOSE_DIR="/path/to/project"

# Containers that MUST be running and healthy
ACTIVE_CONTAINERS=(
  "project-n8n-1"
  "project-nats-1"
)

# Containers that are intentionally stopped (won't trigger alerts)
# Move a container here when it's deliberately taken offline
STOPPED_CONTAINERS=(
  "project-postgres-1"
  "project-redis-1"
  "project-api-1"
  "project-nginx-1"
)
# ===========================

STATE_FILE="/tmp/.${COMPOSE_DIR##*/}-watchdog-state"
PREV_STATE=$(cat "$STATE_FILE" 2>/dev/null || echo "")

ALL_HEALTHY=true
ALERT=""

for name in "${ACTIVE_CONTAINERS[@]}"; do
  status=$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo "missing")

  if [ "$status" = "missing" ]; then
    ALL_HEALTHY=false
    ALERT+="⚠️ $name: container not found\n"
    continue
  fi

  if [ "$status" != "running" ]; then
    ALL_HEALTHY=false
    ALERT+="🔴 $name: $status\n"
    continue
  fi

  health=$(docker inspect "$name" --format '{{.State.Health.Status}}' 2>/dev/null || echo "none")
  if [ "$health" = "unhealthy" ]; then
    ALL_HEALTHY=false
    failing=$(docker inspect "$name" --format '{{.State.Health.FailingStreak}}' 2>/dev/null || echo "?")
    ALERT+="🟡 $name: unhealthy (${failing} consecutive failures)\n"
  fi
done

# Healthy → silent (or recovery message on transition)
if [ "$ALL_HEALTHY" = true ]; then
  if [ -n "$PREV_STATE" ] && [ "$PREV_STATE" != "healthy" ]; then
    echo "✅ ${COMPOSE_DIR##*/}: all active containers healthy."
  fi
  echo "healthy" > "$STATE_FILE"
  exit 0
fi

# Unhealthy → gather logs + alert on state change
ALERT+="\n--- Last logs ---\n"
for name in "${ACTIVE_CONTAINERS[@]}"; do
  status=$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo "missing")
  health=$(docker inspect "$name" --format '{{.State.Health.Status}}' 2>/dev/null || echo "none")

  if [ "$status" != "running" ] || [ "$health" = "unhealthy" ]; then
    ALERT+="\n[$name]\n"
    logs=$(docker logs "$name" --tail 5 2>&1 | tail -5 || echo "(no logs)")
    ALERT+="${logs}\n"
  fi
done

CURRENT_STATE="unhealthy"
if [ "$PREV_STATE" != "$CURRENT_STATE" ]; then
  echo -e "🚨 ${COMPOSE_DIR##*/} — problem detected:\n"
  echo -e "$ALERT"
  echo "---"
  echo "Fix: cd $COMPOSE_DIR && docker compose up -d"
fi

echo "$CURRENT_STATE" > "$STATE_FILE"
