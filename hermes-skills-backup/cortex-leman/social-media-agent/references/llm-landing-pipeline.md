# LLM-Driven Landing Page Pipeline

End-to-end workflow: GPT-5.6 writes copy → you build HTML → Gemini 2.5 Flash does visual QA.

## When to Use

- Client needs a landing page and copywriting quality matters
- You have positioning docs, patterns, pricing but need them turned into a full page
- The active model (GLM-5.2) lacks native vision and you need visual QA

## Pipeline

```
Positioning + Patterns + Pricing
        ↓
   GPT-5.6 (OpenRouter) → structured copy with [design: ...] annotations
        ↓
   Build HTML (single-file, Dark Premium or client brand)
        ↓
   Gemini 2.5 Flash QA (OpenRouter) → layout, spacing, contrast feedback
        ↓
   Fix → Ship
```

## Phase 1: Generate Copy

### Prompt Structure (one shot, everything in)

1. **Business context** — name, domain, audience, vertical
2. **Pricing** — exact tiers with inclusions
3. **Positioning rules** — anti-positioning guardrails (what NOT to say)
4. **Copywriting patterns** — stolen patterns with examples (see `pilote-ia-copywriting.md`)
5. **Section structure** — exact sections to produce (hero, problem, anti-promises, results, process, audience, pricing, FAQ, CTA)
6. **Constraints** — language, tone, banned words, design style suggestion
7. **Output format** — markdown by section with `[design: ...]` annotations

**Key:** The `[design: ...]` annotations bridge copy → HTML without a separate design spec.

### Model

`openai/gpt-5.6` via OpenRouter, temperature 0.7, max_tokens 8000.
Cost: ~$0.13/page. See `openrouter-llm-pattern.md` for calling code.

## Phase 2: Build HTML

Single-file `index.html`. Take GPT-5.6's design notes and build:

1. CSS variables for colors (background, cards, accent, text)
2. Inter font (300-700)
3. Section structure matching the copy
4. Mobile-first: `@media (max-width: 768px)` breakpoints
5. No external CSS/JS files — everything inline

### Dark Premium Design System (FR-CH B2B)

```css
--bg: #0d1117;        /* anthracite */
--bg-card: #161b22;   /* elevated surface */
--border: #30363d;
--text: #e6edf3;
--text-muted: #8b949e;
--accent: #d4af37;    /* discreet gold */
```

No robot/brain/futuristic images. Use whitespace + typography for premium feel.

## Phase 3: Visual QA

### Fallback chain

1. `browser_vision` — if it works, use it
2. If error `1210` (GLM-5.2 limitation) → Gemini 2.5 Flash via OpenRouter

### Gemini QA prompt

> "Analyze this landing page screenshot. Check: (1) Visual design quality (2) Premium feel?
> (3) Layout issues or broken elements? (4) Mobile responsiveness indicators. Be specific and critical."

### What Gemini evaluates

- Color palette consistency and contrast
- Typographic hierarchy
- White space adequacy (premium = breathing room)
- CTA visibility
- Card/list spacing for scanability
- Fluid layout indicators for mobile

## Phase 4: Cross-Validation (before shipping)

Feed the copy back to GPT-5.6 or Kimi K3 with critical framing:

> "Critique this positioning. What's too optimistic? What assumptions are fragile?"

**Example:** GPT-5.6 caught that "FR-CH + nLPD" is NOT a moat — it's a prerequisite.
This correction changed the entire copy approach (results over abstractions).

## Pitfalls

- **GPT-5.6 variant:** `openai/gpt-5.6` may resolve to `gpt-5.6-sol` (reasoning). Check `data["model"]`.
- **Temperature:** 0.7 for copy, 0.3 for factual sections (pricing, FAQ).
- **Gemini image size:** Screenshots >1MB may timeout. Compress before base64.
- **Single-file rule:** Keep everything in one `index.html`. Deployment becomes trivial.
- **Don't skip the `[design: ...]` notes:** They contain layout and spacing guidance that saves HTML build time.

## Example Output

**Pilote IA landing** (Aug 2026):
- GPT-5.6 generated 15K chars of structured copy in 91s ($0.13)
- 9 sections with design annotations
- HTML build: single-file, 32KB, Dark Premium
- Gemini QA: "premium and professional" ✓, minor spacing suggestions
- Copy saved to `landing-copy-gpt56.md` for audit trail

## Cross-References

- `pilote-ia-copywriting.md` — FR-CH copywriting patterns (Le Facteur, anti-hype, Ken Griffin)
- `steal-and-improve.md` Methodology C — competitor landing page analysis workflow
- `openrouter-llm-pattern.md` — OpenRouter calling pattern (core code)
