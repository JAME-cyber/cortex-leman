# External LLM Audit Pattern for Video Campaigns

## When to use
- Before finalizing a multi-video campaign for a client
- When the user validates deliverables via external LLM (Claude Sonnet 4 / OpenRouter)
- As a quality gate before delivery

## Workflow

### 1. Compile project context
Gather all VO scripts, visual identity, business context, and deliverable list into a single structured brief.

### 2. Call external LLM via OpenRouter
```bash
curl -s "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/audit_prompt.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data['choices'][0]['message']['content'])
"
```

### 3. Prompt structure
- **System**: Marketing consultant role, specific domain (e.g., "associations/ONG")
- **User**: Full project context (business, deliverables, scripts, visual identity)
- **Task**: 6-point analysis (narrative coherence, marketing clarity, strengths, weaknesses/risks, top 5 recommendations, missing elements)

### 4. Proven audit framework (6 axes)
1. **Cohérence narrative** — Do videos form a coherent set? Missing link?
2. **Message marketing** — Is the pitch clear for the target audience?
3. **Points forts** — What works well
4. **Points faibles/risques** — What could harm (confusion, legal, creepy)
5. **Recommandations** — Top 5 priority actions
6. **Manquants** — Critical absent elements (social proof, testimonials, security info)

## Jul 2026 Results (Culture en Saveur)

### Key findings
- **Missing "Programme" video** — no video explained what children actually DO during 5 days → Created Programme V0 (54s)
- **No adult visible** — major trust red flag for parents → Added Seedance clips with animatrice
- **Security info absent** — no certifications, insurance, allergy protocols → Added trust badges on cards
- **4 campaigns in 1** — T1 (cuisine), T2 (humanitaire), T3 (écologie), Catering → Recommendation to simplify focus
- **No social proof** — no testimonials, no photos of real activities → Flagged as critical gap

### Actions taken from audit
1. ✅ Created Programme V0 with day-by-day schedule + animatrice clips
2. ✅ Upgraded T1/T3 with higher-quality Seedance clips (animatrice visible)
3. ✅ Added trust badges (certified instructor, secure location, Swiss products)
4. ⬜ Separate catering campaign (pending)
5. ⬜ Add testimonials/social proof (pending — needs client material)
