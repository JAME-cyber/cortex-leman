# OpenRouter LLM Calling Pattern

Reusable pattern for calling OpenRouter (GPT-5.6, Kimi, Gemini) from `execute_code`
using `urllib.request`. No SDK, no dependencies, works from any Hermes session.

## When to Use

- Cross-validation: feed your analysis to GPT-5.6 or Kimi for counter-analysis
- Content generation: batch-generate posts, landing page copy, scripts
- Vision QA fallback: when native vision (GLM-5.2) fails, use Gemini 2.5 Flash
- Any task requiring a different model than the active session model

## Core Pattern

```python
import os, json, urllib.request

# Load API key
# Key may be in ~/.hermes/.env OR in a profile-specific .env file
# Profile paths take precedence in multi-profile setups
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_KEY:
    # Try profile-specific .env files first (where keys actually live)
    for env_path in [
        os.path.expanduser("~/.hermes/profiles/orchestrator/.env"),
        os.path.expanduser("~/.hermes/.env"),
    ]:
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("OPENROUTER_API_KEY=") and not line.startswith("#"):
                        OPENROUTER_KEY = line.split("=", 1)[1]
                        break
            if OPENROUTER_KEY:
                break

payload = {
    "model": "openai/gpt-5.6",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 8000,
    "temperature": 0.7
}

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-domain.ch",
        "X-Title": "Project Name"
    }
)

resp = urllib.request.urlopen(req, timeout=180)
data = json.loads(resp.read())
content = data["choices"][0]["message"]["content"]
model_used = data.get("model", "?")
tokens = data.get("usage", {})
cost = tokens.get("cost", "?")
```

## Model IDs

| Model | OpenRouter ID | Use For | Notes |
|-------|--------------|---------|-------|
| GPT-5.6 | `openai/gpt-5.6` | Copywriting, structured output, cross-validation | May resolve to `-sol` (reasoning) variant |
| GPT-5.6 reasoning | `openai/gpt-5.6-sol` | Deep analysis, counter-arguments | Uses reasoning tokens |
| Kimi K2 | `moonshotai/kimi-k2` | Standard generation | Cheaper |
| Kimi K3 | `moonshotai/kimi-k3` | Deep reasoning | Set `max_tokens: 16000+` |
| Gemini 2.5 Flash | `google/gemini-2.5-flash` | Vision QA, fast analysis | Multimodal (images) |

## Cross-Validation Pattern

Feed your own analysis back to GPT-5.6 with a critical framing:

```
"Here is my analysis of [X]. Critique it. What's too optimistic?
What assumptions are fragile? What would a skeptical expert disagree with?
Where am I conflating correlation and causation?"
```

**Why it works:** The LLM that generated the analysis has optimism bias.
A fresh model with explicit "critique" framing catches blind spots.

### When to Cross-Validate

- Before finalizing business positioning or pricing
- Before shipping a landing page
- Before making go/no-go investment decisions
- When your analysis feels "too clean" or lacks pushback

### Parallel Cross-Validation

Run GPT-5.6 AND Kimi K3 in parallel (two `execute_code` calls or two `delegate_task` agents).
If both models agree on the critique, it's likely correct. If they disagree,
the truth is probably in between and needs human judgment.

## Vision QA Fallback Pattern

When `browser_vision` or `vision_analyze` fails (error `1210`: "messages.content.type is invalid"),
fall back to Gemini 2.5 Flash via OpenRouter:

```python
import base64

with open(screenshot_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {
    "model": "google/gemini-2.5-flash",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this screenshot. [your specific question]"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
        ]
    }],
    "max_tokens": 2000,
    "temperature": 0.3
}
# ... same urllib.request call as core pattern
```

**Known:** GLM-5.2 (active model on zai provider) does not support image input.
Gemini 2.5 Flash via OpenRouter is the reliable fallback for all vision tasks.

## Pitfalls

- **Model resolution:** `openai/gpt-5.6` may resolve to `openai/gpt-5.6-sol` on OpenRouter. Check `data["model"]` in the response to see which variant was actually used.
- **Timeout:** Complex prompts (8000+ tokens output) take 60-120s. Set `timeout=180` minimum.
- **Cost tracking:** `data["usage"]["cost"]` gives the actual cost. Useful for budget monitoring.
- **Temperature:** 0.7 for creative (copywriting), 0.3 for analytical (QA, validation).
- **API key location:** Key lives in `~/.hermes/.env` as `OPENROUTER_API_KEY=sk-or-v1-...`.
- **`HTTP-Referer` header:** OpenRouter uses this for attribution ranking. Set it even for non-existent domains.
