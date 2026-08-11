---
name: critical-objective-analysis
category: research
description: Framework for critical objective analysis based on facts not opinions
---

# CRITICAL OBJECTIVE ANALYSIS

## ROLE

Framework for critical and objective analysis of:
- Projects, technologies, decisions evaluation
- Decisions based on facts, not opinions
- Identify fragile propositions (untested assumptions)
- Test falsifiable hypotheses
- Present probable scenarios with probabilities

## PRINCIPLE

**Pragmatism > Opinion**

- Prioritize verified facts
- Expose hypotheses as testable, not certainties
- Identify fragile propositions explicitly
- Propose probable scenarios with probabilities
- Self-criticize analysis to identify biases

## TEMPLATE STRUCTURE

### 1. ESTABLISHED FACTS (VERIFIED)

**Objective:** Document only what is verified, measurable, and irrefutable.

**Format:**
```
Fact [ID]: Description
- Source: URL / Reference / Document
- Date: YYYY-MM-DD
- Verification method: How it was verified
```

**Example:**
```
Fact 1: MiroFish repository has 49,283 stars
- Source: https://api.github.com/repos/666ghj/MiroFish
- Date: 2026-04-04
- Verification method: GitHub API call, stargazers_count field
```

**Quality criteria:**
- Precise source (not "from what I read")
- Explicit verification method
- Measurable data (numbers, dates, specific names)
- Avoid: "It seems that", "Probably", "We can assume"

---

### 2. TESTABLE HYPOTHESES (FALSIFIABLE)

**Objective:** Formulate hypotheses that can be proven false (falsifiability).

**Format:**
```
H[N]: Hypothesis description

**Test:**
1. Test method
2. Objective metrics
3. Success/fail criteria

**Validation criterion:** Condition to validate/reject hypothesis

**Fragile proposition:** What we assume but haven't tested
```

**Example:**
```
H1: MiroFish can predict real events with >50% accuracy

**Test:**
1. Select 10 past events (ex: elections, product launches)
2. Run MiroFish simulation with historical data (before event)
3. Compare predictions vs reality
4. Calculate accuracy: (correct predictions / total predictions)

**Validation criterion:** If accuracy > 50% (above chance), hypothesis supported. If accuracy <= 50%, hypothesis rejected.

**Fragile proposition:** No validation data available in README. Demos are qualitative (not quantitative).
```

**Quality criteria:**
- Falsifiable hypothesis (can be proven false)
- Test defined with clear steps
- Objective metrics (numbers, not "impression")
- Binary validation criterion (pass/fail)
- Avoid: "It's a good hypothesis", "It seems plausible"

---

### 3. RISKS AND LIMITS

**Objective:** Identify what can cause project/decision failure.

**Format:**
```
### 1. Risks [Category]

| Risk | Probability | Impact | Mitigation |
|--------|-------------|---------|------------|
| **Risk name** | High/Medium/Low | Critical/Medium/Low | Concrete action to reduce |

**Probability:** Probability risk occurs (based on facts, not intuition)
**Impact:** Consequence if risk occurs (quantifiable if possible)
**Mitigation:** Concrete action (not "we will pay attention")
```

**Example:**
```
### 1. Technical Risks

| Risk | Probability | Impact | Mitigation |
|--------|-------------|---------|------------|
| **CrewAI-OASIS incompatibility** | High | Critical | Technical POC 1 week to validate |
| **Simulation performance** | Medium | Medium | Benchmark scaling (100, 1000, 10000 agents) |
| **Unpredictable LLM costs** | Medium | High | Strict budget + usage monitoring |
```

**Quality criteria:**
- Specific risks (not "technical risks" global)
- Probability based on facts (ex: "3 similar projects failed")
- Quantifiable impact (ex: "5 weeks lost", "10K€ cost")
- Concrete mitigation (ex: "POC 1 week", not "monitor")
- Avoid: "Risk it doesn't work", "We'll see"

---

### 4. PROBABLE SCENARIOS

**Objective:** Present possible futures with probabilities (based on facts, not intuition).

**Format:**
```
### Scenario [N]: [Title] (Probability: X%)

**Description:**
- What happens
- Observable indicators
- Impact on project/decision

**Indicators:**
- Metric 1: Expected value
- Metric 2: Expected value

**Decision:** Action if this scenario occurs
```

**Example:**
```
### Scenario 1: Accurate but costly (Probability: 45%)

**Description:**
- MiroFish accuracy > 50% (above chance)
- Prohibitive LLM costs (10-50€/simulation)
- Impossible client pricing (negative ROI)

**Indicators:**
- Internal benchmarks: accuracy 55-65%
- Simulation cost: 20-50€ (1000 agents × 10 rounds)
- Client acceptance: "Too expensive"

**Decision:** Abandon MiroFish, pivot to cheaper solutions.
```

**Quality criteria:**
- Probabilities sum = 100% (exhaustive scenarios)
- Probabilities based on facts (ex: "3/10 similar cases")
- Observable indicators (not "we will feel")
- Clear decision (not "we will think about it")
- Avoid: "Probably it will work", "We hope"

---

### 5. FRAGILE PROPOSITIONS (UNTESTED ASSUMPTIONS)

**Objective:** Expose what we assume but haven't verified.

**Format:**
```
### [N]. **"[Explicit assumption]"**

**Fragile proposition:** Why it's fragile (lack of data, untested hypothesis)

**Required test:** How to test this proposition
```

**Example:**
```
### 1. **"MiroFish can predict the future"**

**Fragile proposition:** No validation data published. Demos are qualitative (not quantitative).

**Required test:** Empirical validation on past events with objective metrics.
```

**Quality criteria:**
- Explicit proposition (not "assumptions")
- Explanation why fragile (lack of data, untested hypothesis)
- Concrete test to validate
- Avoid: "It's probable", "We assume", "It seems"

---

### 6. SELF-CRITIQUE

**Objective:** Identify what could invalidate the complete analysis.

**Format:**
```
## SELF-CRITIQUE

### What could invalidate this analysis:

**1. Incomplete data**
- What I analyzed: [list]
- What I did NOT analyze: [list]

**Invalidates if:** [Condition that reveals data = incomplete]

---

**2. Selection bias**
- What I prioritized: [list]
- What I ignored: [list]

**Invalidates if:** [Condition that reveals a bias]

---

**3. Untested hypotheses**
- Listed hypotheses: [H1, H2, H3]
- Executed tests: [NONE / PARTIAL]

**Invalidates if:** Tests reveal results opposite to hypotheses

---

**4. Incomplete context**
- What I know: [list]
- What I do NOT know: [list]

**Invalidates if:** Context reveals ignored constraints

---

**5. Ignored alternatives**
- Compared: [Option A, Option B]
- Not compared: [Option C, Option D, ...]

**Invalidates if:** Alternative is superior to recommended option

---

**6. Over-analysis (overthinking)**
- Complexity: [Number of hypotheses/risks]
- Real necessity: [YES/NO]

**Invalidates if:** Problem is much simpler than analysis

---

## CONCLUSION

**Analysis summary:**
- Facts: [Number of established facts]
- Hypotheses: [Number of hypotheses, number tested]
- Risks: [Number of risks, global probability]
- Scenarios: [Most probable scenario]

**Decision:** [Recommended action]

**Next step:** [Immediate action to validate/invalidate]
```

**Example:**
```
## SELF-CRITIQUE

### What could invalidate this analysis:

**1. Incomplete data**
- I analyzed GitHub repo and API data
- But NOT:
  - Backend source code (did not access implementations)
  - Production logs (no real data)
  - Internal benchmarks (not published)

**Invalidates if:** Source code reveals architectural choices different from my assumptions (ex: OASIS not used).
```

**Quality criteria:**
- Each point has "Invalidates if" condition
- Testable conditions (not "if it doesn't work")
- Expose analysis weaknesses
- Avoid: "I did my best", "It's the best possible"

---

## RECOMMENDED USAGE

### When to use this skill:

1. **Technology evaluation** (ex: MiroFish, new frameworks)
2. **Strategic decisions** (ex: Integrate X into project)
3. **Risk analysis** (ex: Launch new product)
4. **Project validation** (ex: Is this project viable?)

### When NOT to use:

1. **Trivial decisions** (ex: Which text editor to use)
2. **Subjective opinions** (ex: Is this design beautiful?)
3. **Established facts** (ex: Earth is round - no analysis needed)

---

## QUALITY CHECKLIST

Before finalizing analysis:

- [ ] All facts have precise source
- [ ] All hypotheses are falsifiable
- [ ] All risks have concrete mitigation
- [ ] All scenarios have summed probability = 100%
- [ ] All fragile propositions have required test
- [ ] Self-critique exposes at least 3 weaknesses
- [ ] Conclusion recommends clear action
- [ ] No subjective terms ("seems", "probably", "we can assume")
- [ ] No certainties where there are hypotheses

---

## ANALYSIS EXAMPLES

### Example 1: Technology evaluation (MiroFish)

See complete analysis: MiroFish - Critical Analysis

### Example 2: Strategic decision (Integrate MiroFish in Cortex Leman)

Same structure with:
- Facts: Cortex Leman current architecture
- Hypotheses: MiroFish accuracy, costs, integration
- Risks: Incompatibility, costs, client adoption
- Scenarios: Success, failure, compromise
- Fragile propositions: "Clients will pay", "Integration feasible"
- Self-critique: Incomplete data (no benchmark)

### Example 3: Project validation (HELEN-Workflow-Manager)

**Real-world application of critical objective analysis to evaluate software project viability.**

**Analysis outcome:**

- **12 established facts** (workflow automation AI, Clean Architecture, FastAPI backend, React frontend, n8n integration, DashScope AI, backup/restore system, Docker/k8s deployment, pytest test suite, complete documentation, project audit clean-up, monitoring infrastructure)

- **6 testable hypotheses** (all untested):
  - H1: Production-ready (stable, scalable, maintainable)
  - H2: Clean Architecture improves maintainability
  - H3: n8n integration adds value vs local execution
  - H4: DashScope (Qwen) superior to OpenAI/Anthropic
  - H5: Backup/restore system functional
  - H6: Scaling capability (10→100→1000 users)

- **18 risks identified** (6 business + 6 technical + 6 compatibility):
  - Business: DashScope dependency (China API), n8n SaaS costs, 0 GitHub stars, unknown pricing, unclear target market
  - Technical: Clean Architecture overkill, SQLite bottleneck, n8n/DashScope single points of failure, k8s complexity, memory leaks
  - Compatibility: Python/Node conflicts, n8n version breaks, DashScope API changes

- **4 probable scenarios** (sum = 100%):
  - Scenario A: Production-ready MVP (30%) - Load tests pass, costs reasonable
  - Scenario B: Functional but not production-ready (40%) - Response time too slow, n8n costs high
  - Scenario C: Over-engineered (20%) - k8s/Clean Architecture unnecessary for target
  - Scenario D: Non-functional (10%) - System broken, not viable

- **6 fragile propositions exposed**:
  - Clean Architecture = better architecture
  - n8n = value add
  - DashScope = superior to alternatives
  - HELEN = production-ready
  - k8s = scaling solution
  - SQLite = database OK for production

**Conclusion:** HELEN is solid architecturally but NOT production-ready without validation.

**Next steps required:**
1. Load testing (100 concurrents, 1000 workflows)
2. LLM benchmark (DashScope vs OpenAI/Anthropic)
3. Market research (20+ beta users)
4. Technical validation (restore system, n8n integration, database locks)

This analysis demonstrates the framework's power: exposing that 0 tests were executed despite production-ready claims, identifying critical external dependencies (n8n, DashScope), and quantifying that the most probable outcome is "functional but not production-ready" (40%).

### Example 3: Project validation (Launch SaaS)

Same structure with:
- Facts: Market size, competition, resources
- Hypotheses: CAC < LTV, churn < 10%, growth > 50%/year
- Risks: Competition, market saturation, funding
- Scenarios: Success, failure, pivot, slow growth
- Fragile propositions: "Market need exists", "Differentiation works"
- Self-critique: Over-optimism assumptions

---

## MULTI-MODEL COUNTER-ANALYSIS

When doing critical analysis of content (videos, articles, claims), producing a **second-opinion counter-analysis via a different LLM** significantly improves robustness. This technique surfaces blind spots and biases that a single model might miss.

### Workflow

1. **Extract source material** — Get the full transcript/text of the content being analyzed
2. **Produce initial analysis** — Your primary model does the critical analysis using this framework
3. **Dispatch counter-analysis** — Send the same source material + a critical prompt to a different model via OpenRouter API
4. **Synthesize** — Compare both analyses, noting convergences (high confidence) and divergences (investigate further)

### OpenRouter API call pattern

**IMPORTANT**: The OpenRouter key in `~/.hermes/.env` is stored as a **masked placeholder** (e.g. `sk-or-...bb48`). Shell `grep`/`curl` approaches will get 401. Use one of these methods:

**Method A: `hermes -z` CLI (recommended)** — Hermes resolves keys at runtime:
```bash
timeout 120 hermes -z "$(cat /tmp/counter_prompt.txt)" \
  -m openai/gpt-5.6-luna --provider openrouter --cli 2>&1
```

**Method B: Python via execute_code** — same runtime key resolution:
```python
import json, urllib.request, os

api_key = os.environ.get('OPENROUTER_API_KEY', '')  # resolved by Hermes runtime
payload = json.dumps({
    "model": "openai/gpt-5.6-luna",
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.3,
    "max_tokens": 8000
}).encode()

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=payload,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hermes-agent.nousresearch.com",
        "X-Title": "Hermes Counter-Analysis"
    }
)
with urllib.request.urlopen(req, timeout=120) as resp:
    result = json.loads(resp.read())
print(result['choices'][0]['message']['content'])
```

### Available models for counter-analysis (OpenRouter, July 2026)

| Model | Context | Best for |
|---|---|---|
| `anthropic/claude-opus-4.7` | 1M | Deep multi-section analysis, financial plans, fiscal/regulatory detail |
| `anthropic/claude-sonnet-5` | 1M | Fast thorough analysis, different reasoning style |
| `openai/gpt-5.6-luna` | 1M | Deep analytical counter-opinion (current default for counter-analysis) |
| `openai/gpt-5.6-luna-pro` | 1M | Highest quality GPT, complex reasoning |
| `openai/gpt-5.5` / `gpt-5.5-pro` | 1M | Previous gen, still solid |

**Model selection rule:** Always use a **different model family** than the primary analysis. If you analyzed with a GLM model (Z.ai), counter with Claude or GPT. If you used GPT, counter with Claude. Echo-chamber confirmation happens within model families, not across them.

**Preferred counter-model for GLM-5.2 primary**: `openai/gpt-5.6-luna` — different family, strong French analytical reasoning, ~$0.10-0.15 per counter-analysis call.

### Counter-analysis prompt template

Structure the prompt to force the counter-model to:
- Identify **exaggerations and unproven claims** with specific citations
- Expose **conflicts of interest**
- Flag **survivorship bias** and missing alternatives
- Assess **applicability to user's specific context** (FR-CH for Cortex Leman)

### Pitfalls

- **API key access (CRITICAL — key is masked in .env)**: The OpenRouter key stored in `~/.hermes/.env` is a **redacted placeholder** (e.g. `sk-or-...bb48`), NOT the real key. Hermes masks secret values on write/display but resolves them internally at runtime. **`grep`/`cut`/`cat` the .env will return the masked value and API calls will 401.** Two working approaches:
  1. **Use `hermes -z` CLI** (recommended — Hermes resolves the key internally): `hermes -z "$(cat /tmp/counter_prompt.txt)" -m openai/gpt-5.6-luna --provider openrouter --cli`
  2. **Use `execute_code`** which has the same runtime key resolution as the agent process.
- **GPT-5.5/5.6 minimum max_tokens**: GPT-5.x via OpenRouter rejects `max_tokens < 16` with a 400 error. Always use `max_tokens >= 16` (recommend 4000+ for analysis tasks).
- **Output truncation**: Complex counter-analyses (risks + hypotheses + verdict + correctifs) often exceed 2000 tokens. Use `max_tokens: 4000-8000` for thorough analyses. If output is truncated (`finish_reason: "length"`), send a follow-up call with the partial result asking the model to "continue from where you stopped" with the remaining sections.
- **Two-call pattern for long analyses**: For structured counter-analyses with 5+ output sections, split into two calls: (1) main analysis (risks, hypotheses), (2) verdict + correctifs. This avoids truncation and keeps each response focused.
- **Token costs**: A 30K char transcript + 8K char prompt ≈ 8K input tokens. Counter-analysis output ≈ 5K tokens. Total cost: ~$0.10 with gpt-5.6.
- **Model selection**: Always use a **different model family** than the one that produced the initial analysis, otherwise you get echo-chamber confirmation. If primary was GLM/Z.ai, counter with Claude or GPT.
- **Payload escaping (Python heredoc pitfall)**: When building the API payload in shell, inline Python heredocs with `<< 'EOF'` break on apostrophes and triple-quotes in French text. **Use `write_file` to create a standalone Python script** at `/tmp/build_prompt.py`, then run `python3 /tmp/build_prompt.py` to write the JSON payload to `/tmp/payload.json`, then `curl -d @/tmp/payload.json`. This completely avoids shell escaping hell.
- **Anthropic models via OpenRouter**: Claude Opus 4.7 returns up to 10K+ char responses in a single call (no two-call split needed for most analyses). `temperature: 0.3` works well for rigorous financial counter-analysis.

### Application: Business Plan Counter-Analysis

Counter-analysis is especially powerful for **business plan validation** — not just content analysis. The workflow:

1. **Draft the plan** (your primary model produces a phased plan)
2. **Dispatch to counter-model** with the full plan + context (pricing, stack, market, existing assets)
3. **Ask specifically for**: top 3 risks by severity, unvalidated hypotheses, blind spots/angles morts, verdict (holds up or not), prioritized correctifs
4. **Synthesize**: accept correctifs that are factually grounded, push back on those that misunderstand your context (e.g., counter-model may underestimate existing assets you have)

**Proven result (July 2026)**: GPT-5.5 counter-analysis of a SaaS restaurant QR plan (Menuo) identified that (a) 29-49€/mois was too low for the support burden, (b) payment integration was premature for the MVP, (c) "restaurants" was too broad a niche. All three correctifs were applied and materially improved the plan. See `references/counter_analysis_business_plan.md` for the prompt template, two-call pattern, synthesis methodology, and full case study.

**Proven result 2 (July 2026)**: Claude Opus 4.7 counter-analysis of a Darkom × Figue de Barbarie financial projection (bootstrapper cash-engine → asset-scalable plan) caught three critical blind spots the primary GLM-5.2 analysis missed: (1) the AE→société fiscal cliff at 77.7k€ HT (cotisations jump 12.3%→25-35%), (2) ignored CAC for D2C cosmetics (40-80€/flacon, making the product sell at a loss for 12-18 months), (3) TAM was overestimated by ~2×. Opus also surfaced three underestimated opportunities (revalorisation/resale, B2B recurring contracts, Swiss market at 2-3× FR prices). See `references/counter_analysis_financial_projections.md` for the prompt template, single-call Opus pattern, and the "3 risques mortels / 3 opportunités sous-estimées" format.

**Proven result 3 (July 2026)**: GPT-5.6-luna counter-analysis of a Silicon Carne podcast analysis (10 IA founders, Raise Summit Paris). The primary GLM-5.2 analysis recommended "copy BlackFig's voice audit." GPT-5.6 caught: (1) imitation bias — treating a founder's pitch as a proven model, (2) forced cross-sell synergy between unrelated products, (3) "réinventer le métier" messaging is anxiety-inducing for PME buyers, (4) token optimization is not a commercial moat. The counter-analysis corrected the strategy from "launch 4 bets" to "test one narrow diagnostic offer with 3 paying clients first." Dispatched via `hermes -z` CLI (not `curl` — OpenRouter key is masked in `.env`). See `references/counter_analysis_media_content.md` for the media counter-analysis workflow, prompt template, and the `hermes -z` dispatch pattern.

---

## B2B NICHE EVALUATION: 3 PILLARS × 4 CRITERIA

When evaluating whether a B2B niche is viable (or diagnosing why prospecting fails), apply the **3 Pillars × 4 Criteria** framework before any other analysis. A single failed criterion kills a niche regardless of how well the others score.

See `references/b2b_niche_evaluation_framework.md` for the full framework, scoring rubric, application examples, and the restaurant vertical case study (Jul 2026).

**Quick test**: Score Cible (target) on 4 criteria — ROI, Marché, LTV, Régulation — each /10. Any score ≤2/10 = niche killed. Diagnose in order: Cible → Message → Infrastructure (never reverse).

---

## SKILL LIMITATIONS

### What this skill does NOT do:

- Make decisions FOR you (it structures information)
- Replace domain expertise (it formalizes thinking)
- Guide on "good decisions" (it exposes risks)
- Evaluate subjective opinions (beauty, taste, preferences)

### What this skill DOES:

- Structure information objectively
- Expose fragile propositions
- Identify possible scenarios
- Propose tests to validate/invalidate
- Self-criticize analysis

---

## INTEGRATION WITH OTHER SKILLS

### Cortex Leman Skills

- **l-architecte-lemanique (CSO):** Strategic decisions, project validation
- **le-gardien-des-normes (Compliance):** Regulatory risk evaluation
- **l-oeil-de-cortex (Data):** Data analysis for established facts
- **l-ingenieur-de-flux (Automation):** Technical feasibility evaluation

### Research Skills

- **arxiv:** Search established facts (papers, benchmarks)
- **plan:** Plan validation tests

---

## CONCLUSION

**Critical Objective Analysis = Framework for decisions based on facts, not opinions.**

**Key:** Pragmatism > Opinion. Expose fragile propositions. Self-criticize analysis.

---

*This skill helps make better decisions by structuring critical and objective thinking.*
