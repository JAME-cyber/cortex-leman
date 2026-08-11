# Counter-Analysis for Business Plan Validation

## When to use

Counter-analysis is especially valuable for **business plan validation** — where a single model's optimism can hide fatal flaws. Use when:
- You've drafted a phased go-to-market plan and want to stress-test it
- You're about to invest time/money in a SaaS or service business
- The plan was produced by one model and you want a different model's perspective

## Two-call pattern

Complex counter-analyses (5+ output sections) often exceed 2000 tokens and get truncated. Split into two API calls:

### Call 1: Main analysis

```json
{
  "model": "openai/gpt-5.5",
  "messages": [
    {
      "role": "system",
      "content": "Tu es un consultant strategy & growth brutallement honnête. Tu analyses des business plans pour trouver les failles. Tu ne flatte pas. Tu identifies les risques cachés, les hypothèses non validées, et les angles morts. Réponds en français."
    },
    {
      "role": "user",
      "content": "Contre-analyse ce plan commercial. Trouve les failles, les risques cachés, les hypothèses dangereuses, et propose des correctifs.\n\n## Contexte\n[Full context: product, stack, pricing, existing assets, target market]\n\n## Plan à analyser\n[Full phased plan]\n\n## Ce que je veux\n1. Les 3 plus gros risques (classés par sévérité)\n2. Les hypothèses non validées qui pourraient tout faire crasher\n3. Ce qui manque (angles morts)\n4. Verdict : le plan tient la route ou pas\n5. Les correctifs prioritaires"
    }
  ],
  "max_tokens": 4000,
  "temperature": 0.7
}
```

### Call 2: Continuation (if truncated)

If `finish_reason` is `"length"`, send a follow-up:

```json
{
  "model": "openai/gpt-5.5",
  "messages": [
    {
      "role": "system",
      "content": "Tu es un consultant strategy & growth brutallement honnête. Réponds en français, format markdown concis."
    },
    {
      "role": "user",
      "content": "Suite de l'analyse. Tu étais en train d'analyser [recap what was being discussed]. Continue avec :\n3. Les angles morts du plan\n4. Verdict\n5. Les 5 correctifs prioritaires\n\nSois concis. Pas de blabla. Des bullets percutants."
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.6
}
```

## Synthesis step

After receiving the counter-analysis:

1. **List every point** the counter-model raised
2. **For each point, decide**: Accept (factually grounded) / Partial (right problem, wrong conclusion) / Reject (misunderstands your context)
3. **Apply accepted correctifs** to the plan
4. **Document the rejection reasoning** — so you don't later make the mistake the counter-model warned about

## Case study: Menuo (July 2026)

**Product**: SaaS QR code ordering for restaurants. 29-49€/mois. Firebase + Stripe + Vercel.
**Plan**: 3 phases — (1) validate pilot, (2) connect to SocialPulse pipeline, (3) scale to 10 clients.

**GPT-5.5 counter-analysis findings** (via OpenRouter, ~$0.12 total cost):

| Finding | Verdict | Action taken |
|---------|---------|-------------|
| Product "works technically" but fails in real service chaos | ✅ Accept | Added 14-day field observation criteria |
| Pricing too low for support burden | ✅ Accept | Added 149€ setup fee, split features across tiers |
| "Restaurants" niche too broad | ✅ Accept | Narrowed to kebabs/snacks/fast-casual |
| Payment integration premature for MVP | ✅ Accept | Removed Stripe from MVP, payment at register |
| SocialPulse leads ≠ proven channel | ⚠️ Partial | Right that leads≠sales, but underestimated 11 existing paying clients |
| Need 30 field interviews before building more | ❌ Reject | Too slow for bootstrapper; 10 manual sales sufficient |

**Result**: Plan materially improved. 4 of 6 correctifs applied directly.

## API details

### Calling OpenRouter (key is masked in .env — use hermes -z)

The OpenRouter key in `~/.hermes/.env` is a **masked placeholder** (`sk-or-...bb48`), not the real key. `grep`/`cut`/`cat` returns the masked value and direct `curl` gets 401.

**Recommended: use `hermes -z` CLI** (Hermes resolves keys at runtime):
```bash
# Write prompt to temp file (avoids shell escaping with French text)
cat > /tmp/counter_prompt.txt << 'PROMPTEOF'
[Your full counter-analysis prompt here]
PROMPTEOF

# Dispatch via hermes CLI
timeout 120 hermes -z "$(cat /tmp/counter_prompt.txt)" \
  -m openai/gpt-5.6-luna --provider openrouter --cli 2>&1
```

### GPT-5.x quirks

- `max_tokens` must be ≥ 16 (rejected otherwise with 400 error)
- Default to 4000+ for analysis tasks to avoid truncation
- `temperature: 0.6-0.7` works well for critical analysis (low enough for rigor, high enough for creative risk identification)
- Cost: ~$0.03-0.06 per call depending on input/output length
