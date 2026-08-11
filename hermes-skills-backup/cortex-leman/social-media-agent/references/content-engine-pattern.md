# Content Engine Pattern — Autonomous Content Ideation via Hermes Kanban

> Reference architecture for a 5-profile pipeline that monitors 50+ sources,
> scores signals, verifies evidence, and produces content angles for human review.
> Inspired by [@VibeMarketer_'s Hermes tutorial](https://x.com/VibeMarketer_/status/2084632057733681197) (741 bookmarks, Aug 2026).
> Built and tested live on Tars' Hermes instance (content-engine board).

---

## When to Deploy

- A client needs a systematic content pipeline (not just a posting agent — an ideation engine)
- The social-media-agent already handles posting, but content ideas are ad-hoc
- The client wants "wake up to 3-4 researched content angles every morning"
- Selling point: "We monitor 50+ sources while you sleep and deliver angles that are researched, verified, and ready to draft"

## Architecture: 5-Profile Pipeline

```
┌─────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│ scout-x │──┐  │              │     │             │     │          │
│ 06:00   │  ├──▶ orchestrator ├──▶ │ researcher  ├──▶  │ ideator  │──▶ Telegram
│         │  │  │ 06:30        │     │ (parallel:  │     │          │    (human
├─────────┤  │  │ score 0-100  │     │  evidence + │     │ 3 angles │     approval)
│scout-web│──┘  │ route ≥70    │     │  coverage)  │     │          │
│ 06:00   │     └──────────────┘     └─────────────┘     └──────────┘
└─────────┘                                                       
                                                    ┌──────────┐
                                                    │  tuner   │  Vendredi 17h
                                                    │ (weekly) │  3 changes max
                                                    └──────────┘
```

## Profile Roster

| Profile | Role | Model Strategy | Output |
|---|---|---|---|
| `scout-x` | Scan X/Twitter for signals | Cheap/fast model | Kanban cards in triage |
| `scout-web` | Scan newsletters, Reddit, YouTube | Cheap/fast model | Kanban cards in triage |
| `orchestrator` | Group + score signals 0-100 | **Strongest model** (scoring errors cascade) | Scored cards + child tasks |
| `researcher` | Verify evidence + map coverage | Mid-range model | Evidence pack + coverage map |
| `ideator` | 3 content angles from verified research | Mid-range model | 3 angles, blocked for human review |

## Scoring Rubric (Orchestrator)

| Criterion | Weight | Question |
|-----------|--------|----------|
| Audience fit | 25 | Does this matter to Swiss SME owners and marketing teams? |
| Timeliness | 20 | Is this happening now or about to happen? |
| Evidence strength | 20 | Are there multiple independent sources? |
| Originality potential | 20 | Can we offer a unique angle? |
| Actionability | 15 | Can the reader do something with this today? |

**Routing:** ≥70 → promote + create researcher children, 50-69 → hold with note, <50 → archive with reason.

## Dependency Graph (parent-child tasks)

```
orchestrator promotes idea (≥70)
  ├──▶ T_research_evidence   (assignee: researcher, no parents)
  ├──▶ T_research_coverage   (assignee: researcher, no parents)
  └──▶ T_ideate_angles       (assignee: ideator, parents: [evidence, coverage])
```

The ideator task auto-promotes to `ready` only when BOTH research tasks complete. Use `kanban_create(parents=[...])`.

## Deployment Steps

### 1. Create profiles
```bash
for p in scout-x scout-web orchestrator researcher ideator; do
  hermes profile create "$p" --description "<one-line role>" --clone
done
```

### 2. Create board + switch
```bash
hermes kanban boards create content-engine
hermes kanban boards switch content-engine
```

### 3. Configure dispatcher
```bash
hermes config set kanban.dispatch_interval_seconds 60
hermes config set kanban.max_in_progress_per_profile 2
hermes config set kanban.failure_limit 2
hermes config set kanban.auto_subscribe_on_create true
hermes config set kanban.dispatch_in_gateway true
```

### 4. Write AGENTS.md for each profile
Place in `/home/tars/.hermes/profiles/<profile>/workspace/AGENTS.md`.
Each AGENTS.md defines: role, signal/card format, scoring rubric, routing rules.
See templates below.

### 5. Build watchlist
Create `data/watchlist.yaml` in scout workspaces with 20 sources to start.
Categories: x_accounts, newsletters, subreddits, youtube_channels.
Include `audience:` section for scoring context.

### 6. Schedule crons
```bash
# Scouts at 06:00 daily (silent, local)
# Orchestrator at 06:30 daily (silent, local)
# Tuner Friday 17:00 (deliver to user)
```

### 7. Test with manual signal injection
```bash
hermes kanban create "SIGNAL: [test signal]" \
  --assignee orchestrator \
  --body "SIGNAL: ... SOURCE: ... TOPIC: ... WHAT HAPPENED: ... WHY AUDIENCE MIGHT CARE: ... WHEN: ..."
```

## Key Learnings (from live deployment)

1. **Dispatcher auto-runs from gateway** — no need to manually dispatch if `dispatch_in_gateway: true`. Tasks created with `--assignee` auto-claim within 60s.

2. **CLI syntax gotchas:**
   - `boards create <slug>` (subcommand), NOT `boards --create` (flag)
   - Task title is positional: `create "TITLE"`, NOT `--title`
   - No `--board` flag on `create`/`list` — use `boards switch` to set context

3. **Orchestrator scoring quality matters most** — every scoring error wastes researcher/ideator budget. Use the strongest model for this profile.

4. **AGENTS.md must be explicit about output format** — without a rigid card template, scouts produce inconsistent signals that the orchestrator struggles to group.

5. **The "no double-pass" principle from film AI applies here** — separate jobs (scout → score → research → ideate) because a single agent "grades its own homework". Each handoff is an editorial check.

6. **Watchlist growth should be gradual** — start with 20 sources, review results daily, add 5/week toward 50. Adding too many sources at once drowns the orchestrator in noise.

7. **Tuner is critical for long-term quality** — the weekly learning loop analyzes which ideas were approved vs rejected and proposes prompt/source adjustments. Limit to 3 changes per cycle for measurability.

8. **Scratch workspaces are ephemeral** — the dispatcher warns about this. For the content engine, this is fine (output lives in kanban comments, not files).

## Selling Points (Pilote IA)

- **vs DIY (VibeMarketer tutorial):** The tutorial teaches HOW to build (30-day setup). We sell the running system + ongoing tuning + FR-CH compliance.
- **vs Hootsuite/Buffer:** Ideation engine upstream of posting. These tools schedule; we decide WHAT to create.
- **Cost:** API spend only. ~$0.50-1.00/day in LLM calls for the full pipeline.
- **Human approval gate:** Every idea passes through human editorial judgment before becoming content.

## Anti-Hype, Source Independence & Anti-Positioning (GPT-5.6 Contra-Analyse)

These three guardrail sets were added after a GPT-5.6 counter-analysis (Aug 2026)
caught critical blind spots in the initial content engine design. They are now
baked into the orchestrator, researcher, and ideator AGENTS.md files respectively.

### 1. Anti-Hype Scoring (Orchestrator)

Social signals (GitHub stars, X bookmarks, upvotes) are NOT evidence of market
demand, product retention, or willingness to pay. The orchestrator applies:

- **GitHub stars**: Penalize originality -5 if signal strength comes mainly from star count
- **X bookmark/like ratio >2.5**: "Save for later" reference, not viral adoption. Timeliness cap 65
- **Viral framing** ("game-changer", "pointless", "revolutionary"): Strip framing, evaluate underlying claim
- **"Free" claims**: Verify total cost of ownership (API, setup, maintenance) before scoring >70
- **Commoditization risk**: If an open-source tool commoditizes what we sell, +10 evidence but -10 originality

### 2. Source Independence Verification (Researcher)

**Counting URLs is NOT verifying independence.** Two articles can re-post the same
press release, the same study, or syndicated content.

Independence levels:
- **Independent**: Different authors, different data, different methodology → acceptable for high-risk claims
- **Corroborated**: Multiple sources but same underlying origin → acceptable for medium-risk only
- **Single-source**: One source → low-risk claims only, flag explicitly

For claims scored ≥80 (regulation, compliance, financial impact): require 2
INDEPENDENT sources, not 2 URLs. Document: "Source A [URL] — primary investigation.
Source B [URL] — independently confirmed via [different data/method]".

### 3. Anti-Positioning Guardrails (Ideator)

The ideator auto-rejects abstract framings and requires concrete outcomes.

**BANNED** (auto-reject the angle):
- "Second brain", "knowledge graph", "connected notes" — PMEs don't buy abstractions
- "Game-changer", "revolutionary", "pointless" — hype destroys credibility with FR-CH buyers
- "100% free" — nothing is free to operate
- "Conforme nLPD" as headline — compliance is a prerequisite, not a differentiator
- "Powered by AI" — every competitor says this

**REQUIRED** (at least one per angle):
- Concrete business outcome with metric: "Retrouver une procédure en 30s au lieu de 20min"
- Time/cost savings: "Économisez 6h/semaine sur la préparation des dossiers"
- Vertical specificity: "Conçu pour les fiduciaires romandes"
- Operational continuity: "Le savoir de votre équipe reste même quand quelqu'un part"

**Self-check**: "Would a 50-year-old fiduciaire owner in Lausanne read this hook
and think 'this solves my problem'?" If no → rewrite.

### Why These Matter

Without these guardrails, the content engine produces B2C-style hype content
("This free tool changes everything!") that fails with FR-CH SME buyers. The
GPT-5.6 contra-analyse proved that "FR-CH + nLPD" is NOT a moat by itself —
the real differentiator is concrete business outcomes, vertical specificity,
and operational governance.

## Competitor Integration Workflow

When a competitor signal enters the content engine (scout detects competitor tweet/product):

1. **Scout creates card** with `COMPETITOR:` prefix in title, assigns to orchestrator
2. **Orchestrator scores** with anti-hype rules active (stars/bookmarks ≠ market validation)
3. **Researcher verifies** using source independence rules — competitor's own claims need external corroboration
4. **Ideator generates angles** respecting anti-positioning guardrails — no "we do the same in French"
5. **Add competitor to watchlist** (`priority: high`) for ongoing monitoring
6. **Save reusable patterns** (copywriting, positioning, technical) to fact_store + `references/pilote-ia-copywriting.md`

See `references/steal-and-improve.md` Methodology C for the full competitor landing page analysis workflow.

## File Locations (Tars' instance)

- Profiles: `/home/tars/.hermes/profiles/{scout-x,scout-web,orchestrator,researcher,ideator}/`
- AGENTS.md: `<profile>/workspace/AGENTS.md`
- Watchlist: `<scout>/workspace/data/watchlist.yaml`
- Board DB: `/home/tars/.hermes/kanban/boards/content-engine/kanban.db`
- Cron jobs: `scout-x-daily`, `scout-web-daily`, `orchestrator-morning`, `content-tuner-weekly`
