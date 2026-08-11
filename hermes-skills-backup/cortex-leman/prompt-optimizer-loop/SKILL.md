---
name: prompt-optimizer-loop
description: Optimize AI video prompts via generate-score-mutate loop.
---

# Prompt Optimizer Loop (autoresearch pattern)

Autoresearch-style optimization loop for AI video generation prompts. Inspired by `karpathy/autoresearch` (fact #43): **generate → measure score → keep or discard → mutate → repeat**.

## When to use

- Optimizing a video prompt before spending full credits on Seedance
- Finding the best prompt variant for a scene without manual trial-and-error
- Any scenario where a measurable quality score can guide prompt iteration

## How it works

```
Base prompt → Hailuo T2V Standard (30cr) → ffmpeg frame extract → OmniRoute vision QA (free)
    → score ≥7/10? KEEP  ──────────────────────────────→ record as winner
    → score <7?  DISCARD → apply fixes from QA → mutate prompt → repeat
```

## Script

**Location**: `/home/tars/scripts/prompt_optimizer.py`

### Usage

```bash
# Basic: 3 iterations, 90cr budget
python3 /home/tars/scripts/prompt_optimizer.py \
  --base-prompt "Your prompt here" \
  --budget 90 --threshold 7 --max-iters 3

# From file, 5 iterations
python3 /home/tars/scripts/prompt_optimizer.py \
  --base-prompt-file prompt.txt \
  --budget 150 --max-iters 5
```

### Parameters

| Param | Default | Description |
|-------|---------|-------------|
| `--base-prompt` | required | Initial prompt to optimize |
| `--budget` | 120 | Max credits to spend |
| `--threshold` | 7 | Score 1-10 to keep a clip |
| `--max-iters` | 6 | Maximum iterations |
| `--duration` | 6 | Video duration (6 or 10 seconds) |
| `--resolution` | 768P | Unused by Hailuo 02 T2V but kept for compat |

### Output

Each run creates `/tmp/prompt_optimizer_<timestamp>/`:
- `iter_01.mp4`, `iter_01_frame.jpg`, `iter_02.mp4`, ...
- `optimization_log.json` — full log with prompts, scores, fixes, progression

## Key design decisions

1. **Hailuo 02 T2V Standard** (`hailuo/02-text-to-video-standard`) — cheapest T2V at 30cr/clip. Uses `prompt_optimizer: true` built-in flag. Note: this model does NOT accept a `resolution` field (causes 422).
2. **OmniRoute vision** (`auto/pro-vision` at `localhost:20128`) — free local QA scoring. Returns structured JSON with score + specific fixes.
3. **OmniRoute streaming parse** — OmniRoute returns SSE even with `stream: false`. The script handles both formats.
4. **Prompt mutation** — applies vision-model-suggested fixes (ADD/REMOVE tokens). Falls back to auto-mutation with specificity tokens if no fixes suggested.

## Prerequisites

- `KIE_AI_API_KEY` env var
- OmniRoute running on `localhost:20128` (or change `OMNI_HOST`/`OMNI_PORT`)
- `ffmpeg` + `ffprobe` for frame extraction

## Pitfalls

1. **`hailuo/02-text-to-video-standard` rejects `resolution` field** — returns 422. Only `prompt`, `duration`, `prompt_optimizer`, `nsfw_checker` are accepted. The `--resolution` CLI arg is kept for compatibility but ignored by this model.
2. **`http.client` import** — must be imported at module level (`import http.client`), NOT via `__import__("http.client")` which returns the `http` package, not the `.client` submodule.
3. **OmniRoute `auto/best-vision` often returns empty** — prefer `auto/pro-vision` which is more reliable for structured JSON output.
4. **Generation takes ~90s** — Hailuo Standard clips take 60-120s. Budget wall-clock time accordingly (~2min per iteration).
5. **Score inflation** — OmniRoute vision models tend to score generously (8/10 for decent clips). Consider threshold 8 for stricter quality gates.
6. **Markdown code fences in JSON responses** — OmniRoute vision sometimes wraps JSON in `` ```json ... ``` `` fences. The parser now strips these before extraction. If not stripped, the brace-matching fails silently and score defaults to 5 (fallback), causing valid clips to be discarded. Fixed in v2.
