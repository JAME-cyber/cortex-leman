---
name: service-watchdog-cron
description: "Monitor external services (APIs, databases, providers) with silent cron jobs that alert only on state changes. Uses Hermes cronjob with no_agent=true scripts for zero-token monitoring."
version: 1.0.0
category: devops
---

# Service Watchdog Cron Pattern

Monitor an external service's health with a Hermes cron job that is **silent while the expected state persists** and **alerts only on state change** (recovery, new failure, unexpected status). Zero LLM tokens consumed.

## When to Use

- An external API/provider goes down and you want to know when it recovers without polling manually.
- A dependency (DB, vector store, embedding provider) is flaky and you need proactive alerting.
- Any periodic health check where the "all clear" state should produce no noise.

## Architecture

```
┌─────────────┐    every N min     ┌──────────────┐
│  Hermes     │───────────────────▶│  bash script │
│  scheduler  │                    │  (healthcheck)│
└─────────────┘                    └──────┬───────┘
       │                                   │
       │  stdout non-empty → deliver       │
       │  stdout empty → silent            │
       ◀───────────────────────────────────┘
```

**Key principle:** The script's stdout IS the message. Empty stdout = silence. Non-empty stdout = alert delivered to the user's chat.

## Step-by-Step Setup

### 1. Write the healthcheck script

Place it in the project's `bin/` directory. Structure:

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Load credentials (from .env, config, etc.)
KEY=$(grep API_KEY /path/to/.env | head -1 | cut -d= -f2)
if [ -z "$KEY" ]; then
  echo "⚠️ API_KEY not found in .env"
  exit 1
fi

# 2. Probe the service
HTTP_CODE=$(curl -s -o /tmp/.health-check.json -w "%{http_code}" \
  "https://api.example.com/v1/endpoint" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": ["healthcheck"], "model": "model-name"}' 2>/dev/null)

# 3. Decide output based on state
case "$HTTP_CODE" in
  200)
    # Service is UP — this is the alert the user wants
    echo "✅ Service X is back UP! (HTTP 200)"
    echo "You can resume normal operations."
    echo "Recovery command: cd /path/to/project && make restart"
    ;;
  500|429|503)
    # Known down state — stay SILENT (exit 0, no output)
    exit 0
    ;;
  *)
    # Unexpected state — alert
    echo "⚠️ Service X — unexpected status: HTTP ${HTTP_CODE}"
    echo "Response: $(cat /tmp/.health-check.json | head -c 200)"
    ;;
esac

rm -f /tmp/.health-check.json
```

### 2. Make it executable and test

```bash
chmod +x bin/check-service.sh
# Dry run — should be silent if service is still down
bash bin/check-service.sh
echo "EXIT: $?"  # should be 0 with no output
```

### 3. Create the cron job

Use the Hermes `cronjob` tool with these critical settings:

| Parameter | Value | Why |
|-----------|-------|-----|
| `no_agent` | `true` | Skip LLM entirely — script output is the message verbatim |
| `script` | `bin/check-service.sh` | The healthcheck script |
| `workdir` | `/path/to/project` | So the script path resolves |
| `schedule` | `every 2h` | Adjust based on urgency |
| `deliver` | `origin` | Deliver to the chat where the job was created |
| `repeat` | `60` | Auto-expire after N runs (don't run forever) |

```
cronjob(action='create', no_agent=true, script='bin/check-service.sh',
        workdir='/path/to/project', schedule='every 2h', repeat=60,
        deliver='origin', name='Watchdog: Service X')
```

### 4. Verify the cron was created

```
cronjob(action='list')
```

## Design Rules

1. **Silent on expected-down.** The script MUST produce zero stdout when the service is in the known-bad state. This is the watchdog pattern — no spam, only signal.
2. **Verbose on recovery.** When the service comes back, the message should include the recovery command so the user can act immediately.
3. **Alert on unexpected states.** A status code you didn't anticipate (not 200, not 500) should produce output — it might indicate a different problem.
4. **Auto-expire.** Set `repeat` to a reasonable bound (60 runs = 5 days at 2h interval). Don't create infinite watchdogs — they accumulate.
5. **No LLM cost.** `no_agent=true` means zero tokens. The script runs, stdout is delivered, done.

## Variants

### Variant A: Flapping detection (count before alerting)

If a service is intermittent, add a state file to count consecutive failures:

```bash
STATE_FILE="/tmp/.service-x-state"
FAIL_COUNT=$(cat "$STATE_FILE" 2>/dev/null || echo "0")

if [ "$HTTP_CODE" = "500" ]; then
  FAIL_COUNT=$((FAIL_COUNT + 1))
  echo "$FAIL_COUNT" > "$STATE_FILE"
  if [ "$FAIL_COUNT" -ge 3 ]; then
    echo "🚨 Service X down for $FAIL_COUNT consecutive checks"
  fi
  exit 0
fi

# Reset on recovery
echo "0" > "$STATE_FILE"
```

### Variant B: Multi-endpoint check

Check several endpoints in one script, report only the ones that changed:

```bash
declare -A ENDPOINTS=(
  ["api-prod"]="https://api.example.com/health"
  ["api-staging"]="https://staging.example.com/health"
  ["vector-db"]="http://localhost:8000/health"
)

ALERT=""
for name in "${!ENDPOINTS[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "${ENDPOINTS[$name]}" 2>/dev/null)
  if [ "$code" != "200" ]; then
    ALERT+="❌ $name: HTTP $code\n"
  fi
done

if [ -n "$ALERT" ]; then
  echo -e "Service issues detected:\n$ALERT"
fi
# Empty ALERT = silent
```

### Variant C: Docker container health monitoring

Monitor a Docker Compose stack instead of HTTP endpoints. Docker containers have richer state than HTTP probes: `running`, `exited`, `unhealthy` (with `FailingStreak` count). A single down dependency (e.g. postgres) cascades to all dependent services silently — Docker's healthcheck runs but nobody reads the result without a watchdog.

Key differences from HTTP watchdog:
- Uses `docker inspect --format` to check state, not `curl`
- Captures `docker logs --tail N` on failure for diagnosis (embeds the "why" in the alert)
- Tracks cascading failures (postgres down → api unhealthy → nginx unhealthy) in a single alert
- State transitions matter: `exited → running` (recovery) and `running → unhealthy` (degradation)

```bash
# Container state check
status=$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo "missing")
health=$(docker inspect "$name" --format '{{.State.Health.Status}}' 2>/dev/null || echo "none")
failing=$(docker inspect "$name" --format '{{.State.Health.FailingStreak}}' 2>/dev/null || echo "?")
logs=$(docker logs "$name" --tail 5 2>&1 | tail -5)
```

See `templates/docker-watchdog.sh` for a complete, production-ready script. The template handles:
- **Active vs stopped separation**: `ACTIVE_CONTAINERS` (must be running) vs `STOPPED_CONTAINERS` (intentionally offline, never alerts). This prevents the watchdog from alerting forever about containers you deliberately took offline — the most common operational reality for partial stacks.
- Multiple container states (missing, exited, running+unhealthy, running+healthy)
- State-change detection (only alerts on transitions, not every tick)
- Recovery messages with the compose restart command
- Log extraction for each failing container

**Common Docker failure pattern**: `depends_on` with `condition: service_healthy` means a down dependency prevents the service from starting at all. The service container shows as "running" but its healthcheck fails indefinitely (FailingStreak grows into thousands). The root cause is always upstream — check which containers are `exited` first.

**When to use active/stopped split**: When a stack is partially decommissioned — e.g. postgres+redis+api+nginx are dead but n8n+nats still serve traffic and use SQLite internally. Before setting up the watchdog, verify which containers are actually independent (check their env vars and volumes for DB dependencies). Move dead containers to `STOPPED_CONTAINERS` and stop them cleanly (`docker stop`) to free resources. The watchdog then only alerts if a container in `ACTIVE_CONTAINERS` goes down.

## Example: NVIDIA Embedding Provider Watchdog

Real-world example from this session. NVIDIA's `baai/bge-m3` embedding API went down (HTTP 500). The watchdog monitors for recovery so the RAG system can resume indexing.

- **Script:** `knowledge-rag/bin/check-nvidia-bge-m3.sh`
- **Schedule:** every 2h
- **Behavior:** Silent while HTTP 500 persists. On HTTP 200, delivers recovery message with the re-index command.
- **Backup plan documented in script comments:** If bge-m3 stays down >48h, switch to `nvidia/nv-embedqa-e5-v5` (same 1024 dimensions, different vector space — requires full reindex).

See `references/nvidia-embedding-failover.md` for the full provider comparison and failover decision tree for NVIDIA embedding models.

### Variant D: Web Search Radar (LLM-powered intelligence monitoring)

**Different from hash-diff watchdogs**: Instead of checking if a page changed, this variant runs **scheduled web searches** via an LLM-driven cron and compares results against a **baseline knowledge file**. Silent when nothing new exists, alerts with structured intelligence when a new release/competitor/regulation appears.

**When to use**: Technology radar (new AI models, framework releases), competitive intelligence (new competitors, pricing changes), regulatory monitoring (AI Act, RGPD updates), market signals for specific verticals.

**Two-layer monitoring pattern** (best results):

| Layer | Cron type | Frequency | Cost | Catches |
|-------|-----------|-----------|------|---------|
| **Hash-diff** | `no_agent=true` script | Every 4-6h | 0 tokens | Page HTML changed (new version, pricing, features) |
| **Search radar** | LLM-driven, web toolset | Daily | ~4-6 web_search calls | Announcements, blog posts, news, social mentions NOT on the monitored pages |

The hash-diff catches **silent updates** (price changes, feature toggles). The search radar catches **announcements elsewhere** (blog posts, tweets, press releases, HN/Reddit threads). Together they cover both vectors.

**Baseline file** (the knowledge the agent already has):

```markdown
# Intelligence Baseline — Last updated: YYYY-MM-DD

## Monitored tools
### Tool X
- Version: X.Y
- Pricing: $Z/s
- Features: A, B, C
- Detection keywords: "Tool X 2.0" OR new API announcement
```

The baseline file is the agent's memory of "what already exists." Only **new** information (version not in baseline, pricing not listed, tool not known) triggers an alert. Update the baseline when an alert is confirmed.

**Cron creation** (search radar layer):

```
cronjob(action='create',
  name='Domain Radar',
  enabled_toolsets=['web', 'file'],
  schedule='0 8 * * *',
  deliver='origin',
  prompt='Read baseline at /path/to/baseline.md. Run N targeted web searches. Compare. If nothing new: respond "RAS". If new: 3-5 lines with link + impact + recommended action.'
)
```

**Key principles**:
1. **Baseline is king** — without a known-state reference, the agent can't distinguish "new" from "already known." Update the baseline when an alert fires and is confirmed.
2. **"RAS" = acceptable daily signal** — a short "RAS" message confirms the system is alive without noise.
3. **Restrict toolsets** — `enabled_toolsets=['web', 'file']` prevents unnecessary work (terminal, browser). Keeps token cost low.
4. **Proactive, not reactive** — the agent should bring news to the user BEFORE the user discovers it themselves. This is a core operational principle: if the user has to tell you something new came out, the radar failed.
5. **One brief, not a feed** — combine all discoveries into a single daily brief, not multiple messages throughout the day.
6. **Hash-diff script template**: See `templates/multi-site-hash-watchdog.sh` for monitoring multiple URLs by storing SHA-256 hashes and alerting only on changes.

### Variant E: Cron self-monitoring (meta-watchdog)

Monitor the Hermes cron system itself — alert only when jobs are in error. Uses `hermes cron list` text output parsing (no `--json` flag exists). The script checks each job's `Last run` line: if it doesn't end with `ok`, the job is flagged.

**Key differences from service watchdog:**
- No HTTP probe — parses `hermes cron list` text output
- Checks ALL jobs in one run, reports only the failing ones
- Silent when everything is green (the normal state)
- `no_agent=true` — zero tokens, pure bash+python

```bash
#!/bin/bash
# Cron Health Watchdog — SILENT if all OK, ALERT if jobs in error
set -euo pipefail

OUTPUT=$(hermes cron list 2>&1)

ERRORS=$(echo "$OUTPUT" | python3 -c "
import sys, re
lines = sys.stdin.read().split('\n')
errors = []
current_name, current_id = '?', '?'
for line in lines:
    s = line.strip()
    m = re.match(r'^([0-9a-f]{12})\s+\[(\w+)\]', s)
    if m:
        current_id = m.group(1)
    elif 'Name:' in s:
        current_name = s.split('Name:', 1)[1].strip()
    elif 'Last run:' in s:
        if not s.rstrip().endswith('ok'):
            errors.append(f'  • {current_name} ({current_id[:12]}): {s}')
if errors:
    print(f'🚨 CRON HEALTH — {len(errors)} job(s) en erreur:')
    print('\n'.join(errors))
    print('\nVérifie: hermes cron list')
")

if [ -n "$ERRORS" ]; then
    echo "$ERRORS"
fi
```

Create with: `cronjob(action='create', no_agent=true, script='cron-health-watchdog.sh', schedule='0 14 * * *', deliver='telegram:<chat_id>', name='cron-health-watchdog')`

Schedule once daily, after most jobs have run. This is the "who watches the watchers" pattern — essential when you have 15+ cron jobs.

## Pitfalls

- **Don't set `repeat` too high.** A watchdog that runs forever will accumulate. 60 runs at 2h = 5 days is usually enough. If the service hasn't recovered, recreate the job.
- **Don't forget `no_agent=true`.** Without it, the cron runs the full agent loop for every tick — wasteful for a script that just checks an HTTP code.
- **Don't put secrets in the script.** Load from `.env` or environment. The script's stdout goes to the user's chat — never `echo` credentials.
- **Test the silent path.** Before creating the cron, run the script manually while the service is down. Confirm zero stdout. A verbose-when-down script will spam the user every tick.
- **Don't monitor intentionally-stopped containers.** If part of a stack is deliberately offline, move those containers to `STOPPED_CONTAINERS` (or remove them from the check list). A watchdog that alerts about a known-dead service every tick is worse than no watchdog — it trains the user to ignore all alerts. Always verify which containers are truly independent before deciding what stays in `ACTIVE_CONTAINERS`.
- **False silence when the check itself fails.** If `curl` can't connect (DNS failure, network down, timeout) it returns a non-200 code — but that's a **tool failure**, not a "service is down" finding. The script may fall through to the silent path and produce zero stdout, creating a false sense of "all clear." Always distinguish: (a) check ran, service responded with a status code → report based on that code; (b) check itself failed (curl exit code 6/7/28) → this MUST produce output: "⚠️ Cannot reach <service> — check failed: <reason>. Blind spot active." A silent watchdog that can't reach its target is worse than no watchdog.
- **SPA / client-rendered pages defeat `curl`+`grep`.** Most modern product/marketing sites (React, Next.js, Vue) render content client-side via JavaScript. `curl` fetches only the empty `<div id="root"></div>` shell — the actual text (feature names, pricing tables, changelog entries) is **never in the raw HTML**. A `grep -qi "target phrase"` on that shell will always return false, so the watchdog stays silent forever even after the feature ships. **Three workarounds:** (1) Target the site's **JSON API, RSS/Atom feed, or sitemap.xml** instead of the HTML page — these return raw data without JS rendering. (2) Use a headless browser (`browser_navigate` → `browser_snapshot` in an agent-driven cron, or a headless Chromium/puppeteer script) to get the rendered DOM, then grep that. (3) Watch an alternative signal: the provider's API docs changelog, their developer Discord/Slack via webhook, or their GitHub releases if open-source. **Never assume `curl`+`grep` works on a site you haven't verified** — test once by curling the page and checking if the target string appears in the raw output before committing the watchdog. If it doesn't appear, switch to a browser-based or API-based detection method immediately.
- **`last_status: ok` can be misleading.** The cron system marks a job `ok` whenever the agent loop completes — even if the agent's response is an error report about the task failing. The status reflects "agent ran," not "task succeeded." When debugging a cron that looks broken despite `ok`, read the latest output file (`~/.hermes/cron/output/<job_id>/<latest>.md`) and look for `## Response` — everything after is the agent's actual finding. For crons running numpy-heavy Python scripts (RAG indexing, embeddings), a broken numpy is the first thing to check. See `references/numpy-x86v2-compat.md` for the full crash diagnostic and fix.
