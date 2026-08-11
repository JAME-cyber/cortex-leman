# Counter-Analysis for Media Content (Podcasts, Videos, Articles)

## When to use

Counter-analysis is not just for business plans. When you analyze **media content** (podcasts, conference talks, video interviews) and produce strategic recommendations for the user, a counter-analysis via a different LLM catches:
- **Imitation bias** — "they seem successful, so we should copy their approach"
- **Confirmation bias** — cherry-picking quotes that support your thesis
- **Founder hype** — treating pitch-stage claims as proven business models
- **Missing context** — ignoring the user's actual constraints (bootstrap budget, FR-CH market, etc.)

## Workflow

### Step 1: Extract source material

For YouTube videos/podcasts, use the content-monitoring skill to get transcripts. Extract the key segments (by timestamp range) rather than the full 2h+ transcript — focus on the 3-5 segments most relevant to the user's projects.

### Step 2: Produce initial analysis

Your primary model (e.g. GLM-5.2) produces:
- Segment-by-segment breakdown
- Relevance to user's projects (with priority levels)
- Actionable recommendations ("copy X", "avoid Y", "watch Z")

### Step 3: Build counter-analysis prompt

Write the prompt to a temp file (avoids shell escaping issues with French text):

```bash
cat > /tmp/counter_prompt.txt << 'PROMPTEOF'
Tu es un analyste strategique independant. Voici l'analyse d'un autre analyste.

Ta mission: CONTRE-ANALYSE critique. Ou l'analyste se trompe-t-il ? Qu'a-t-il rate ?
Quelles sont ses hypotheses faibles ? Quelles opportunites a-t-il sous-estimees ou surevaluees ?

Sois direct, factuel, sans flatterie. Remets en question chaque conclusion.

=== CONTEXTE: Les projets de [USER] ===
[List all active projects with brief context]

=== ANALYSE A CONTREDIRE ===
[Paste your initial analysis]

=== POINTS CLES DU PODCAST ===
[Summarized key points from each segment — not full transcript, but enough substance]

Maintenant, ta contre-analyse en francais. Pour chaque point:
- ce qui est juste
- ce qui est faux/sous-evalue/surevalue
- ce qui a ete ignore
Conclusion sur la strategie globale.
PROMPTEOF
```

### Step 4: Dispatch via hermes -z (key resolution)

The OpenRouter key in `~/.hermes/.env` is masked — `grep`/`curl` from shell will 401. Use the Hermes CLI which resolves keys at runtime:

```bash
timeout 120 hermes -z "$(cat /tmp/counter_prompt.txt)" \
  -m openai/gpt-5.6-luna --provider openrouter --cli 2>&1
```

- `timeout 120` — GPT-5.6 can take 60-90s for complex prompts
- `--cli` — non-interactive mode, returns text to stdout
- The full counter-analysis output goes to stdout — capture and present to user

### Step 5: Synthesize for the user

Present a balanced synthesis:

1. **Where GPT was right and you were wrong** (be specific, honest)
2. **Where you maintain your position** (with reasoning)
3. **Net strategic correction** (what actually changes in the recommendations)

**Key principle**: Don't just relay GPT's analysis verbatim. Add your own meta-assessment of where GPT was too conservative (e.g. it may underestimate existing traction/assets the user already has).

## Case study: Silicon Carne podcast counter-analysis (July 2026)

**Source**: Silicon Carne podcast from Raise Summit Paris — 10 IA founders, 2h04min
**Primary model**: GLM-5.2 (Z.ai) — produced initial analysis of 4 segments (BlackFig, Lecat/Scality, H Company, d'Ornano)
**Counter-model**: GPT-5.6-luna via OpenRouter — `hermes -z` dispatch, ~$0.12 cost

**GPT-5.6 caught that GLM-5.2 missed:**

| Issue | GLM-5.2 said | GPT-5.6 counter |
|-------|-------------|-----------------|
| "Copy BlackFig's audit vocal" | 🔴 Good idea | ❌ Biais d'imitation. Voice is a module, not a product. RGPD risk ignored. Pricing uncalibrated. |
| "Cross-sell with SocialPulse/Menuo" | 🟠 Natural synergy | ❌ Forced synergy. Restaurants ≠ process accounting. Different buyer, budget, timing. |
| "Pitch harness > model" | 🟡 Technical angle | ⚠️ True in theory, not in sales. PME buys results, not architecture. |
| "Say 'réinventer' not 'productivité'" | 🟡 Messaging tip | ⚠️ "Réinventer" is anxiety-inducing. PME buys "fewer missed calls." |

**GPT-5.6's corrected strategy**: Don't launch 4 bets. Build one loop: sell workflow diagnostic → identify repetitive process → automate one bounded step → measure → productise only the repeated workflow.

**Where GLM-5.2 pushed back on GPT-5.6**: GPT-5.6 was too conservative about speed-to-test — Thierry already had active commercial channels (2382 SocialPulse leads, Menuo pilot), making the "3 paying diagnostics" test faster than GPT-5.6 assumed.

**Net result**: Counter-analysis materially improved the recommendations. The "copy BlackFig" recommendation was correctly downgraded to "test voice as a collection module within a narrower diagnostic offer."

## Prompt design principles for media counter-analysis

1. **Include the user's full project context** — counter-model needs to know what's relevant
2. **Include key podcast points, not just your analysis** — counter-model needs to form its own opinion from source material
3. **Ask specifically for**: what's right, what's wrong/overstated/understated, what was ignored
4. **Request per-point verdict** — forces systematic coverage rather than general impressions
5. **Ask for conclusion on global strategy** — prevents a laundry list without synthesis
