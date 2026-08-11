---
name: social-media-agent
description: "Build autonomous social media agents for client deployments."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [social-media, automation, agents, openrouter, gpt-5.6, multi-account]
---

# Social Media Agent — Autonomous Multi-Platform Management

Build self-running social media agents that plan content, post on schedule, and engage with audiences — all powered by an LLM brain via OpenRouter. Designed for Pilote IA client deployments (FR-CH, nLPD-compliant, self-hosted).

## When to Use

- A client needs automated social media management (X/Twitter, LinkedIn, Instagram, TikTok)
- You need a "Manus AI" equivalent that runs on-premise (sovereignty selling point)
- Setting up a new account persona in the existing agent
- Adding a new platform connector
- Building an autonomous content ideation pipeline upstream of the posting agent (the "content engine" — see `references/content-engine-pattern.md`)

## Architecture Overview

```
social-media-agent/
├── config/accounts.yaml          ← Personas, tones, content pillars, platform settings
├── src/
│   ├── brain/brain.py            ← LLM brain: strategy, generation, adaptation, engagement, analytics
│   ├── platforms/connectors.py   ← Platform abstraction: X (xurl), LinkedIn, DryRun
│   └── engagement/agent.py       ← Mention monitoring, auto-reply, escalation
├── scripts/                      ← Cron entry points (silent watchdogs)
├── orchestrator.py               ← CLI: plan | post | engage | status | run
├── data/                         ← Calendars, posted log, seen mentions
└── logs/                         ← JSONL audit trail (per account, per day)
```

### Core Design Decisions

1. **Dry-run by default** — `dry_run: true` in config means nothing posts until explicitly switched. Safety first.
2. **One brain, many platforms** — GPT-5.6 generates content once, then `adapt_post_for_platform()` reformats per platform specs (char limits, style, hashtags).
3. **Calendar-driven** — Content is pre-generated into a JSON calendar. Posts fire on schedule from the calendar, not generated on-the-fly. This means content is reviewable before posting.
4. **Silent cron watchdogs** — Engagement checks every 30min but only notify if there's something to act on. No spam.
5. **Escalation built-in** — Trolls are ignored, complex questions are escalated to human, only safe replies are auto-posted.

## Build Steps (New Client Deployment)

### Step 1: Config
Copy `templates/accounts.yaml` and define the client's persona:
- `tone`: personality, voice, forbidden phrases, signature phrases
- `content_pillars`: themes with weights (must sum to ~100)
- `platforms`: enable X/LinkedIn, set posts_per_day
- Keep `dry_run: true` until tested

### Step 2: Brain
The brain (`src/brain/brain.py`) is reusable as-is. It provides:
- `generate_content_plan(account_id, days)` → JSON calendar saved to `data/`
- `adapt_post_for_platform(content, platform, account_id)` → platform-specific formatting
- `generate_reply(comment, original_post, account_id)` → classified reply decision
- `detect_trends(keywords, account_id)` → trend radar
- `analyze_performance(posts_data, account_id)` → weekly analytics

**LLM:** Uses `openai/gpt-5.6-terra` via OpenRouter with `gpt-5.6-luna` fallback. Key in `~/.hermes/.env`.

### Step 3: Platform Connectors
Each connector implements: `post()`, `read_mentions()`, `read_replies()`, `reply()`.

| Platform | Connector | Requirements |
|---|---|---|
| X/Twitter | `XTwitterPlatform` (xurl CLI) | `xurl` installed + OAuth2 |
| LinkedIn | `LinkedInPlatform` (API v2) | `LINKEDIN_ACCESS_TOKEN` env |
| DryRun | `DryRunPlatform` | None (default when `dry_run: true`) |

**To enable X/Twitter:** Install xurl, user completes OAuth2 manually (see `xurl` skill), then set `dry_run: false`.

### Step 4: Engagement Agent
Runs the loop: read mentions → classify via LLM → reply/ignore/escalate.
- Tracks seen mentions in `data/seen_mentions_{account}.json` (dedup)
- Max 5 auto-replies per post (configurable)
- 15min delay before replying (human-like)
- Blocked topics enforced (politics, religion, specific tax advice)

### Step 5: Cron Scheduling
Three silent cron jobs per account:

| Job | Schedule | Behavior |
|---|---|---|
| Post | 3x/day at posting_hours | Posts next calendar item |
| Engage | Every 30min | Silent watchdog — notifies only on interactions |
| Plan | Weekly Monday 6am | Regenerates 7-day calendar |

Create via Hermes cronjob with `deliver: local` for post/engage (silent) and `deliver: origin` for plan (weekly review).

### Step 6: Test & Go Live
```bash
# Test all commands
python3 orchestrator.py status <account_id>
python3 orchestrator.py plan <account_id> 2    # Generate 2-day test calendar
python3 orchestrator.py post <account_id>      # Test post (dry-run)
python3 orchestrator.py engage <account_id>    # Test engagement
python3 orchestrator.py run <account_id>       # Full cycle
```

Switch `dry_run: false` in config when ready to go live.

## Adding a New Account

1. Add a new entry under `accounts:` in `config/accounts.yaml`
2. Define tone, pillars, platforms
3. Run `python3 orchestrator.py plan <new_account_id> 7`
4. Test with `python3 orchestrator.py status <new_account_id>`

## Adding a New Platform

1. Create a class inheriting from `BasePlatform` in `connectors.py`
2. Implement `post()`, `read_mentions()`, `read_replies()`, `reply()`
3. Register in `get_platform()` factory
4. Add platform specs in `adapt_post_for_platform()` brain function

## Selling Points for Pilote IA

- **vs Manus AI:** Same capability (50+ accounts, 24/7) but self-hosted, nLPD-compliant, data stays in Switzerland
- **vs Hootsuite/Buffer:** Autonomous content generation + engagement, not just scheduling
- **Cost:** API costs only (GPT-5.6 ~$0.01-0.05/post), no SaaS subscription
- **Audit trail:** Every action logged in JSONL, reviewable for compliance

## Pitfalls

- **LLM date hallucination:** GPT-5.6 will invent calendar dates if you don't explicitly pass today's date in the prompt. Always inject `datetime.now().strftime('%Y-%m-%d')` into the generation prompt AND specify "Jour 1 = aujourd'hui, dates consécutives".
- **xurl auth:** User must complete OAuth2 manually outside the agent session. Never attempt to run `xurl auth` commands with inline secrets.
- **Platform rate limits:** X enforces per-endpoint limits. The 30min engagement interval is safe. Don't reduce below 15min. The `BasePlatform._rate_limit()` method enforces a 3s minimum between API calls.
- **Retry on API failure:** The orchestrator retries failed posts 3x with exponential backoff (1s, 2s, 4s). Without this, a transient API error permanently loses the post (it gets marked as posted even on failure). Always check `post_result.get("success")` before marking as posted.
- **JSON formatting in f-strings:** Python format codes like `{:<22d}` crash on string values. Use `{:>22s}` with `str()` conversion for safe status formatting.
- **Path imports:** When using `sys.path.insert` for local imports, calculate paths from `Path(__file__).parent` (not `.parent.parent`) when the orchestrator is at project root.
- **Missing `__init__.py`:** Python packages need `__init__.py` in every directory (`src/`, `src/brain/`, `src/platforms/`, `src/engagement/`). Without them, imports work in testing but break intermittently in production. Always create them during project scaffolding.
- **X Free tier is sufficient:** The X API Free tier (1500 posts/month) is enough for 3 posts/day per account. Don't recommend Basic ($200/mo) until managing 10+ client accounts.
- **GPT-5.6 `response_format: json_object` causes null content:** GPT-5.6-terra enters reasoning mode and returns `"content": null` when `response_format: {"type": "json_object"}` is set with complex prompts. **Fix:** drop the JSON format constraint, ask for plain text output prefixed with `POST 1:, POST 2:, ...`, and parse with simple string splitting. This is faster and more reliable than fighting the JSON mode. Use `gpt-5.6-luna` as fallback if terra fails entirely.
- **LLM content generation "Steal & Improve" workflow:** When a user drops a tweet/X link and says "on vole" (steal it), decompose the narrative structure (opening hook → cost anchor → process arrows → punchline), then regenerate adapted posts for the client niche. See `references/steal-and-improve.md` Methodology B for the full workflow.

## Verification After Build

Always run a comprehensive audit after building or modifying the agent. See `scripts/audit.py` for the reusable audit script that checks: file structure, config completeness, function imports, class methods, Python syntax, script executability, environment variables, and dry-run orchestration.

## Reference Implementation

A working implementation lives at `/home/tars/social-media-agent/`. Use it as:
- Template for new client deployments
- Reference for the brain/connector/engagement patterns
- Test bed for new platform connectors

## Tweet Extraction (No Auth)

When xurl is not authenticated, extract tweet content via read-only APIs. See `references/tweet-extraction-methods.md` for the full fallback chain (cdn.syndication.twimg.com → api.vxtwitter.com → fxtwitter HTML). Key: always `curl -o file` then parse — never `curl | python3` (security scanner blocks pipe-to-interpreter).

## LinkedIn Monitoring

For passive hand-raise detection (identifying warm prospects who like/comment on niche influencer posts) and LinkedIn scraping safety thresholds, see [references/linkedin-monitoring-safety.md](references/linkedin-monitoring-safety.md). Includes: 9 detection signals, safe daily limits, "Low & Slow" strategy, legal framework (hiQ vs LinkedIn, nLPD/CH), and Hermes browser implementation pattern.

## Support Files

- `references/architecture.md` — Detailed component breakdown and data flow
- `references/tweet-extraction-methods.md` — Read-only tweet extraction fallback chain (no xurl auth needed)
- `references/steal-and-improve.md` — Methodology for extracting content strategy from competitor analysis
- `references/content-engine-pattern.md` — 5-profile Hermes kanban pipeline for autonomous content ideation (scout → score → research → ideate → human approval). Full deployment guide, scoring rubric, and CLI quick reference.
- `references/pilote-ia-copywriting.md` — FR-CH PME copywriting patterns library (meta-rules from GPT-5.6 contra-analyse, "Le Facteur" pattern, anti-hype tone, Ken Griffin structure)
- `references/openrouter-llm-pattern.md` — Reusable OpenRouter calling pattern (urllib.request from execute_code, model selection, vision QA fallback via Gemini 2.5 Flash)
- `references/llm-landing-pipeline.md` — End-to-end LLM-driven landing page pipeline: GPT-5.6 copy → HTML build → Gemini visual QA. Includes prompt structure, model selection, cross-validation workflow.
- `templates/accounts.yaml` — Config template for multi-account setup
- `scripts/audit.py` — Reusable post-build audit script (structure, syntax, config, dry-run check)
