# Counter-Analysis for Financial Projections & Bootstrapper Business Plans

## When to use

Counter-analysis is critical for **financial projections** — where single-model optimism hides fatal flaws in unit economics, fiscal transitions, and capacity assumptions. Use when:
- You've projected multi-year CA for a bootstrapped business (cash engine → scalable asset pipeline)
- The plan involves a fiscal transition (auto-entrepreneur → société) at a known revenue threshold
- A service business is expected to fund a product business in parallel
- The plan makes counter-cyclical claims ("this business thrives in recession")

## Prompt template (financial counter-analysis)

The prompt must force the counter-model to attack numbers, not just narrative.

```
Tu es un analyste financier senior et consultant en stratégie d'entreprise.
On te demande de faire une CONTRE-ANALYSE critique et honnête d'un plan
financier entrepreneurial.

Voici l'analyse à évaluer:

<analyse>
[Full analysis: CA projections, cost structure, margins, investment budget,
reinvestment timeline, macro assumptions]
</analyse>

Ta mission:
1. Identifier les failles, biais et angles morts. Sois impitoyable mais constructif.
2. Vérifier la cohérence des chiffres — ratios, pourcentages, hypothèses de croissance.
3. Évaluer le scénario macro — est-ce réaliste? Quel impact réel?
4. Critiquer le timing et l'allocation — les risques non couverts.
5. Proposer des corrections chiffrées si certains nombres sont optimistes/pessimistes.
6. Donner un verdict global: le plan est-il viable? Qu'est-ce qui le fera échouer?

Format: structuré en sections, tableaux si pertinent, ton direct et factuel.
Pas de flatterie. Identifie les 3 risques mortels et les 3 opportunités
sous-estimées.
```

## Single-call pattern with Opus 4.7

Claude Opus 4.7 handles full multi-section counter-analyses (8K+ output tokens) in a **single API call** — no two-call split needed. This simplifies the workflow vs GPT-5.5 which often needs continuation calls.

```python
payload = {
    "model": "anthropic/claude-opus-4.7",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 8000,
    "temperature": 0.3  # Low for rigorous financial analysis
}
```

## The "3 risks + 3 opportunities" format

The most actionable counter-analysis output structure for financial plans:

### 3 risques mortels (mortal risks)
Each risk must include:
- The mechanism (how it breaks the plan)
- The timing (when it hits)
- The magnitude (how much it costs or delays)
- The mitigation (if any exists)

### 3 opportunités sous-estimées
Each opportunity must include:
- Why the primary analysis missed it
- The estimated upside (€ or % uplift)
- How to capture it

## Case study: Darkom × Figue de Barbarie (July 2026)

**Plan analyzed**: Darkom Débarras (service business, Haute-Savoie) as cash engine to fund Figue de Barbarie (cosmétique import, Algérie → EU) via 50% reinvestment of Y1 net profits. GLM-5.2 projected CA growing 25k€ (2026) → 250-320k€ (2030).

**Claude Opus 4.7 counter-analysis findings**:

| Finding | Category | Impact |
|---------|----------|--------|
| AE→société fiscal cliff at 77.7k€ HT | 🔴 Mortal risk 1 | Cotisations 12.3% → 25-35% in 2028, margin halved |
| D2C cosmetic CAC ignored (40-80€/flacon) | 🔴 Mortal risk 2 | Product sells at loss for 12-18 months, needs 15-25k€ marketing budget |
| Solo founder carrying two unrelated businesses | 🔴 Mortal risk 3 | Burn-out/injury = both businesses collapse |
| TAM overestimated 2× (3-5% → real 1-2%) | Blind spot | Projections 30-40% too high |
| Revalorisation (resale of cleared items) | 🟢 Opportunity 1 | +20-40% CA at 70%+ margin |
| B2B contracts (notaires, EHPAD, syndics) | 🟢 Opportunity 2 | Near-zero CAC, recurring 20-40 chantiers/year |
| Swiss market at 2-3× FR prices | 🟢 Opportunity 3 | 1 CH job = 3-5 FR jobs equivalent |

**Key correction — sequencing over parallelism**: Opus recommended 100% Darkom in 2026-2027, launch FB only in 2028 when Darkom stabilizes at 80-100k€ with 25k€ net recurring. The "50% reinvestment Y1" rule was rejected as too aggressive — Y1 should rebuild the cash reserve, not fund a second business.

**Result**: Plan score 5.5/10 from Opus. Primary model (GLM-5.2) accepted all major correctifs. Tracker updated to include fiscal transition modeling.

## API execution pattern (payload escaping fix)

When the analysis text contains French apostrophes, accents, and special characters, inline shell heredocs break. Use the **write_file → python → curl** three-step pattern:

```bash
# Step 1: Write the Python script that builds the JSON payload
# Use write_file tool to create /tmp/build_prompt.py

# Step 2: Run it to produce the payload file
python3 /tmp/build_prompt.py
# → writes /tmp/opus_payload.json

# Step 3: Call the API with the payload file
export OPENROUTER_API_KEY=$(grep "^OPENROUTER_API_KEY=" ~/.hermes/.env | cut -d= -f2)
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/opus_payload.json \
  --max-time 180 > /tmp/response.json
```

## Synthesis checklist for financial counter-analysis

After receiving the counter-analysis:

- [ ] Accept or reject each point with explicit reasoning
- [ ] Update cost structure if cotisations/tax rates were wrong
- [ ] Recalculate break-even if CAC was missing
- [ ] Revise CA projections if TAM was overestimated
- [ ] Add the fiscal transition (AE → société) to the timeline if missing
- [ ] Evaluate sequencing (parallel vs sequential business launch)
- [ ] Update the financial tracker/tool with corrected assumptions
