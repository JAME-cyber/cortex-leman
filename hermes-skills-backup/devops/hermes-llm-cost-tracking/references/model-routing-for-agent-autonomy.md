# Model Routing for Agent Autonomy

## The L1-L6 Autonomy Scale

Real-world assessment (Aug 2026, GLM-5.2 orchestrator + Claude Sonnet 4 subagents via OpenRouter):

| Level | Description | Reliable? | Example |
|-------|-------------|-----------|---------|
| L1 | Single task, 1 tool | ✅ Yes | "Analyse ce tweet" |
| L2 | Multi-step task, 1 session | ✅ Yes | Full landed-cost dossier |
| L3 | Task + self-validation + correction | ✅ Yes | self-verify-loop, TDD |
| L4 | Multiple parallel agents | ✅ Yes (validated 8 Aug 2026) | delegate_task batch with Claude Sonnet 4 |
| L5 | Overnight unsupervised | 🟡 Partial (code only) | no-mistakes gate: worktree→test→lint→review→PR |
| L6 | Self-improvement loop | 🔴 Experimental | self-evolution-engine |

**L4 is now reliable.** Validated 8 Aug 2026: Claude Sonnet 4 subagents via OpenRouter provide reliable tool calling, 200K context (no premature compaction), and native vision. The delegate_task routing was tested with a math problem and confirmed working in-session without `/reset`.

**L5 is partially achieved for code workflows only** via Pi Agent + no-mistakes: push→worktree jetable→review→test→lint→docs→push→PR→CI. This provides auto-detection of failures (tests fail → blocked) and auto-recovery (worktree retente). The git repo is the persistent state. However, this does NOT generalize to research/content/data tasks.

**Full agent stack on Tars (Aug 2026):**

| Agent | Role | Model | Provider |
|-------|------|-------|----------|
| Hermes (orchestrator) | Telegram interface, cron, webhook, delegate_task | GLM-5.2 | zai |
| Hermes subagents | Parallel workers (delegate_task) | Claude Sonnet 4 | OpenRouter |
| Pi Agent (no-mistakes) | Git gate proxy: worktree→test→lint→review→PR | GPT-5.6 | — |
| CodeBuddy (cnb.cool) | Agent in repo (personal only, NEVER client) | DeepSeek V4 Flash | cnb.cool |

### @antpalkin loop coverage (Find→Code→Test→Deploy→Autopsy→Learn)

| Step | Status | How |
|------|--------|-----|
| Find | ✅ | Crons, webhooks, lec-scout |
| Code | ✅ | delegate_task, Claude Sonnet 4 |
| Test | ✅ | no-mistakes gate, TDD skill |
| Deploy | ✅ | git push→PR→CI |
| Autopsy | 🟡 | Logs exist but not structured |
| Learn | ❌ | No reusable failure database. Pattern to build: @antpalkin Failure Ledger (domain, context, approach, result, reason, lesson, tags) consulted before each action |

### L5 Generalization Roadmap

To move from L5-code-only to L5-generalized:
1. **Crons with persistent state** — each job writes `progress.json`, each run reads and resumes
2. **Watchdog cron** — verifies jobs are advancing, alerts if blocked
3. **Failure Ledger** — queryable base of negative results consulted before each action
4. **Extend worktree pattern** — apply no-mistakes recovery to non-code tasks (research, content, data)
5. **Resistant compaction** — either reduce frequency or externalize state to files

## Model Selection by Role

The orchestrator and subagents should use DIFFERENT models. Cheap/fast for orchestration, capable/reliable for delegated work.

| Role | Recommended Model | Provider | Why |
|------|-------------------|----------|-----|
| Orchestrator (main session) | GLM-5.2 | zai | Cheap, fast, good enough for routing/synthesis |
| Subagent worker (delegate_task) | Claude Sonnet 4 | openrouter | Best tool-calling, 200K context, native vision, thinking mode |
| Cross-validator | Kimi K3 (kimi-k3) | openrouter | Finds blind spots GPT-5.6 misses. Slow but deep |
| Strategic deep-think | GPT-5.6 | openrouter | Best reasoning, expensive, use sparingly |
| Protos/experiments (personal only) | DeepSeek V4 | CodeBuddy | Free, sandbox. NEVER for client data (Chinese servers) |

## Hermes Config (config.yaml)

```yaml
delegation:
  model: anthropic/claude-sonnet-4    # subagents use Sonnet
  provider: openrouter                 # via OpenRouter
  reasoning_effort: medium             # thinking activated
  max_concurrent_children: 3           # parallel subagents
  child_timeout_seconds: 600           # 10 min per child
  max_iterations: 50                   # tool calls max per child
```

Set with:
```bash
hermes config set delegation.model "anthropic/claude-sonnet-4"
hermes config set delegation.provider "openrouter"
hermes config set delegation.reasoning_effort "medium"
```

Takes effect immediately — confirmed by live test (8 Aug 2026): dispatched a `delegate_task` in the same session that changed the config, and the delegation header reported `Model: anthropic/claude-sonnet-4`. No `/reset` needed.

### Validation test recipe

To confirm subagent routing after a config change:
1. Dispatch a simple `delegate_task` with a math problem (e.g. "poules et lapins, 35 têtes 94 pattes")
2. Ask the subagent to identify its model name
3. Check the delegation batch result header for `Model: anthropic/claude-sonnet-4`
4. Expected: ~6s latency, 1 API call, correct reasoning with step-by-step

## Why Claude Sonnet 4 for Subagents

| Requirement | Why Sonnet 4 |
|-------------|-------------|
| Tool calling reliability | Industry-best function calling accuracy |
| Stamina (30+ tool calls) | 200K context = no premature compaction |
| Self-evaluation | thinking mode recognizes failures and corrects |
| Vision | Native multimodal (no fallback needed) |
| Cost | ~3x cheaper than GPT-5.6, sufficient for L4 |

## Why NOT Other Models for L4 Subagents

- **Kimi K3**: Excellent reasoning but slow, timeout-prone (max 8K tokens output, timeout 300s), no vision, weak stamina. Good for validation, bad for worker loops.
- **DeepSeek V4**: Good and free via CodeBuddy, but CodeBuddy is a separate sandbox — can't use as Hermes backend. API version is paid. Chinese servers = privacy risk for client data.
- **GPT-5.6**: Excellent but expensive for subagent loops where Sonnet suffices.
- **GLM-5.2**: Current orchestrator model. Good for routing but not the best for deep multi-step worker loops.

## Blocking Factors for L5 Generalized (Overnight Autonomy)

L5 is **partially achieved for code** via Pi Agent + no-mistakes (worktree→test→lint→review→PR). For full L5 across all task types:

1. Context compaction — Hermes sessions compact after ~15-20 tool calls, losing detail. Pi Agent's git repo is immune (state is in the repo, not the context window)
2. No robust error recovery (non-code) — for code, no-mistakes worktree jetable handles this. For research/content/data tasks, no equivalent exists
3. No persistent inter-session state — memory exists but isn't full execution state
4. No Failure Ledger — no queryable base of negative results consulted before actions (see @antpalkin loop above)
5. Model stamina — even Sonnet drifts after extended unsupervised loops

## Market Reality Check (Aug 2026)

"Agentic OS" type demos (Julian Goldie etc.) sell L3 with a pretty UI dashboard. We already do L3 without UI and touch L4. The gap to L5 is NOT a model problem — it's a reliability/recovery architecture problem. Building a pretty dashboard over Hermes + Gemini CLI doesn't add autonomy levels.

## Kimi K3 Known Quirks for Cross-Validation

- Via OpenRouter: `moonshotai/kimi-k3`
- Slow: timeout 300s, max_tokens 8000+
- Good at finding 5+ blind spots that GPT-5.6 missed on FR-CH playbook analysis
- Use for: one-shot deep validation, NOT for agent loops
- Prompt pattern: contrarian + adversarial questions + FR-CH context

## Claude Fable 5 Bug (OpenRouter)

Claude Fable 5 via OpenRouter NEVER triggers reasoning (0 reasoning_tokens regardless of parameter). Silently dropped. Use `anthropic/claude-sonnet-4` with `{"thinking":{"type":"enabled","budget_tokens":N}}` instead. Ref: Hermes issue #43432.
