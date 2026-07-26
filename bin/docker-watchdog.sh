#!/usr/bin/env bash
set -euo pipefail

# === Cortex Leman Docker Watchdog ===
# Silent when all containers are healthy.
# Alerts with diagnosis + last log lines when something is wrong.
# stdout = message delivered to chat. Empty = silence.

COMPOSE_DIR="/home/tars/cortex-leman-v5"

# Active = must be running. Stopped = intentionally offline (won't alert).
ACTIVE_CONTAINERS=(
  "cortex-leman-v5-n8n-1"
  "cortex-leman-v5-nats-1"
)
STOPPED_CONTAINERS=(
  "cortex-leman-v5-postgres-1"
  "cortex-leman-v5-redis-1"
  "cortex-leman-v5-api-1"
  "cortex-leman-v5-nginx-1"
)

# Check overall state
ALL_HEALTHY=true
ALERT=""
STATE_FILE="/tmp/.cortex-watchdog-state"
PREV_STATE=$(cat "$STATE_FILE" 2>/dev/null || echo "")

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
  
  # Check health if the container has a healthcheck
  health=$(docker inspect "$name" --format '{{.State.Health.Status}}' 2>/dev/null || echo "none")
  if [ "$health" = "unhealthy" ]; then
    ALL_HEALTHY=false
    failing=$(docker inspect "$name" --format '{{.State.Health.FailingStreak}}' 2>/dev/null || echo "?")
    ALERT+="🟡 $name: unhealthy (${failing} consecutive failures)\n"
  fi
done

# If everything is fine, stay silent
if [ "$ALL_HEALTHY" = true ]; then
  # Check if we were previously alerted — send recovery
  if [ -n "$PREV_STATE" ] && [ "$PREV_STATE" != "healthy" ]; then
    echo "✅ Cortex Leman: tous les containers sont healthy."
    echo "Reprise confirmée."
  fi
  echo "healthy" > "$STATE_FILE"
  exit 0
fi

# Something is wrong — grab logs for diagnosis
ALERT+="\n--- Logs (dernières lignes) ---\n"
for name in "${ACTIVE_CONTAINERS[@]}"; do
  status=$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo "missing")
  health=$(docker inspect "$name" --format '{{.State.Health.Status}}' 2>/dev/null || echo "none")
  
  if [ "$status" != "running" ] || [ "$health" = "unhealthy" ]; then
    ALERT+="\n[$name]\n"
    # Last 5 lines of logs
    logs=$(docker logs "$name" --tail 5 2>&1 | tail -5 || echo "(no logs)")
    ALERT+="${logs}\n"
  fi
done

# State change detection
CURRENT_STATE="unhealthy"
if [ "$PREV_STATE" != "$CURRENT_STATE" ]; then
  echo -e "🚨 Cortex Leman — problème détecté:\n"
  echo -e "$ALERT"
  echo "---"
  echo "Réparation: cd $COMPOSE_DIR && docker compose up -d"
fi

echo "$CURRENT_STATE" > "$STATE_FILE"
