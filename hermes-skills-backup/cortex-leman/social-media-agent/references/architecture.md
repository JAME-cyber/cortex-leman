# Architecture — Social Media Agent

Detailed component breakdown and data flow for the reference implementation.

## Component Map

```
┌─────────────────────────────────────────────────────┐
│                   ORCHESTRATOR                        │
│            (orchestrator.py — CLI entry)              │
│                                                       │
│  plan ──┐   post ──┐   engage ──┐   status ──┐       │
│         │          │            │            │       │
└─────────┼──────────┼────────────┼────────────┼───────┘
          ▼          ▼            ▼            ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐
    │  BRAIN   │ │ PLATFORMS│ │ENGAGEMENT│ │ LOGS   │
    │ (GPT-5.6)│ │(xurl/LI) │ │  AGENT   │ │(JSONL) │
    └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┘
         │            │            │
    ┌────┴────┐  ┌────┴────┐  ┌───┴─────┐
    │Calendar │  │DryRun   │  │Mentions │
    │JSON     │  │XTwitter │  │Seen set │
    │data/    │  │LinkedIn │  │data/    │
    └─────────┘  └─────────┘  └─────────┘
```

## Data Flow

### Content Generation (plan)
1. Orchestrator calls `brain.generate_content_plan(account_id, days)`
2. Brain loads config from `accounts.yaml`
3. Brain constructs LLM prompt with: persona, pillars, platform specs, **today's date** (critical — see pitfalls)
4. GPT-5.6 returns JSON calendar
5. Calendar saved to `data/calendar_{account}_{YYYYMMDD}.json`

### Publishing (post)
1. Orchestrator calls `get_next_post_from_calendar(account_id)`
2. Finds today's unposted item by matching date+time
3. Checks `data/posted_{account}.json` for dedup
4. Adapts content via `brain.adapt_post_for_platform()`
5. Gets platform connector via `get_platform(account_id, platform_name)`
6. DryRun → logs only | X → xurl post | LinkedIn → API v2
7. On success, marks post_key in posted log

### Engagement (engage)
1. Engagement agent loads seen mentions from `data/seen_mentions_{account}.json`
2. For each enabled platform, calls `platform.read_mentions(limit=20)`
3. For each unseen mention:
   - Brain classifies: type, sentiment, should_reply, escalation
   - If escalation → log + notify (silent unless critical)
   - If should_reply → post reply via connector
   - If troll/spam → skip
4. Updated seen set saved (keep last 500)

### Analytics (weekly)
1. Load 7 days of JSONL logs from `logs/`
2. Brain analyzes: best pillar, best format, optimal times, top/bottom posts
3. Report saved to `data/engagement_report_{account}_{date}.json`

## Cron Job Architecture

```
┌─────────────────────────────────────────────────┐
│                  HERMES CRON                      │
│                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────┐│
│  │ social-post │  │social-engage │  │social-   ││
│  │ 3x/day      │  │ every 30min  │  │plan      ││
│  │ deliver:    │  │ deliver:     │  │weekly    ││
│  │ local       │  │ local        │  │deliver:  ││
│  │ (silent)    │  │ (watchdog)   │  │origin    ││
│  └──────┬──────┘  └──────┬───────┘  └────┬─────┘│
│         │                │               │      │
│         ▼                ▼               ▼      │
│  scripts/          scripts/          scripts/    │
│  scheduler_        scheduler_        scheduler_  │
│  post.sh           engage.sh         plan.sh     │
└───────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Platform Abstraction
`BasePlatform` defines the interface. Each concrete platform implements it. `get_platform()` factory returns the right one based on config. DryRun is the safe default.

### 2. LLM as Strategy Engine, Rules as Guardrail
The LLM (GPT-5.6) generates content and classifies comments. Hard rules enforce safety:
- `blocked_topics` list checked before posting
- Troll detection always skips
- Escalation flags route to human
- Dry-run mode prevents accidental publishing

### 3. Retry with Exponential Backoff
The orchestrator retries failed posts up to 3 times with exponential backoff (1s, 2s, 4s). Only marks a post as "posted" after `post_result.get("success")` is True. Without this, a transient API error permanently loses the post.

### 4. Rate Limiting
`BasePlatform._rate_limit()` enforces a minimum 3-second interval between API calls per platform connector instance. Prevents hitting X/Twitter rate limits during engagement sweeps (30 mentions × read + reply could otherwise burst).

### 5. Calendar Pre-Generation
Content is not generated on-the-fly at posting time. It's pre-generated into a reviewable JSON calendar. This allows human review before going live and decouples content quality from scheduling reliability.

### 6. Silent Watchdog Engagement
The engagement cron runs every 30min but only produces output when there's something to report (mentions found, replies needed). This respects the "cron should be silent unless signal" preference.

## File Inventory

| Path | Purpose |
|---|---|
| `config/accounts.yaml` | Multi-account personas, tones, pillars, platform config |
| `src/brain/brain.py` | LLM brain: all GPT-5.6 calls (strategy, adaptation, engagement, analytics) |
| `src/platforms/connectors.py` | Platform abstraction layer (X, LinkedIn, DryRun) |
| `src/engagement/agent.py` | Engagement loop: mentions → classify → reply/escalate |
| `orchestrator.py` | CLI entry point: plan, post, engage, status, run |
| `scripts/scheduler_*.sh` | Cron entry points (bash wrappers) |
| `data/calendar_*.json` | Generated content calendars |
| `data/posted_*.json` | Dedup log of posted items |
| `data/seen_mentions_*.json` | Dedup set for engagement |
| `logs/{account}_{YYYYMMDD}.jsonl` | Audit trail (one JSON per line per action) |
