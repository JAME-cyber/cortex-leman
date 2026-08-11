# Hybrid Lead Scoring Methodology

Session-validated technique for filtering and prioritizing B2B leads from a raw
scraped dataset (SocialPulse 2,382 leads → 206 Segment A restaurant targets).

## When to Use

- You have a raw lead CSV with thousands of entries but no conversion labels
- You need to produce an actionable shortlist (top N) for outbound prospecting
- ML model exists but has zero real-world validation (synthetic-only training)

## The Problem with Pure ML Scoring

TabICLv2 trained on synthetic data (ROC-AUC 0.679) produces scores that cluster
too tightly — everything looks "above average." When applied naively, 1003/1509
restaurants scored as "Segment A," which is useless for prioritization.

**Rule: When ML has zero real-world labels, business rules beat ML. Use ML as a
secondary signal (5% weight max), not the primary ranking.**

## Hybrid Score Formula (100 pts)

| Component | Weight | Logic |
|-----------|--------|-------|
| No website | 25% | `website_status == 'none'` = 25, `facebook_only` = 18, `has_website` = 0 |
| Has phone | 15% | Actionable for cold call. Phone present = 15, absent = 5 |
| Core zone | 15% | Primary cities = 15, adjacent = 11-13, peripheral = 7 |
| Channel | 15% | Instagram = 15 (active, reachable), SMS = 12, email = 10, other = 5 |
| Business type | 10% | High-value types (pizza, kebab, grill, snack, burger, asian) = 10, other categorized = 7, generic = 3 |
| SocialPulse score | 10% | Normalized (min-max) raw score × 10 |
| ML score | 5% | Normalized TabICLv2 score × 5 — secondary only |
| Name specificity | 5% | Named business = 5, generic ("Restaurant") = 1 |

## Chain/Franchise Exclusion

Before scoring, exclude known chains that will never buy from a local agency:

```python
CHAINS = [
    'domino', 'mcdonald', 'buffalo grill', 'kfc', 'burger king',
    'subway', 'pizza hut', 'quick', 'la pataterie', 'courtepaille',
    'flunch', 'hippopotamus', '5 guys', 'poulet farm',
    'migros', 'carrefour', 'auchan', 'casino', 'intermarché',
    'totem', 'speed burger', 'izakaya', 'planet sushi'
]
```

This removed only 7 entries from 1509 restaurants but prevents wasted outreach.

## Segmentation Thresholds

| Segment | Score Range | Action | Count (from 1502) |
|---------|-------------|--------|-------------------|
| **A** (top priority) | ≥85 | Active prospecting, cold call, in-person visit | 206 |
| **B** (medium) | 70-84 | Email sequence, retarget later | 792 |
| **C** (low) | <70 | Park, revisit after Segment A/B exhausted | 504 |

## Key Insights from the Data

1. **96% of top 300 concentrated in 2 cities** (Annemasse + Gaillard) = walkable prospecting zone
2. **50% of top 300 have phone numbers** = directly callable
3. **All top 50 have `website_status == 'none'`** = the strongest single signal
4. **158/300 are "generic Restaurant" type** — name doesn't reveal cuisine, needs enrichment
5. High-value types (pizza, kebab, grill) cluster at the top — these benefit most from QR menus

## Enrichment Opportunities (Next Steps)

The base SocialPulse CSV lacks data that would sharpen scoring further:

| Missing Field | Source | Scoring Impact |
|---------------|--------|----------------|
| Google rating + review count | Google Places API | Low reviews = high opportunity |
| Uber Eats / Deliveroo presence | Platform search | Platform-only = high QR value |
| Instagram follower count | Instagram scrape | Low followers = opportunity |
| Menu digitization status | Manual / Google Images | Paper menu = direct pitch |

## Swap Path to Real Labels

After 90 days of prospecting, label each lead:
`contacted → responded → meeting → proposal → signed → active → retained → churned`

Then retrain TabICLv2 on real labels. Only valid with minimum:
- 50 responses, 20 meetings, 10 proposals, ideally 5-10 sales

Before that threshold: **business rules + rules-based scoring will outperform ML.**

## Working Implementation

- Script: produced inline in session (see `/tmp/score_restaurants_v2.py` pattern)
- Output: `~/socialpulse-mvp/annemasse-agency/ml/output/restaurant_priority_300.csv`
- Input: `~/socialpulse-mvp/annemasse-agency/ml/output/scored_leads.csv`

## GPT-5.6 Strategic Framework (Cross-Validated)

The scoring framework was cross-validated via OpenRouter GPT-5.6 (openai/gpt-5.6-luna).
GPT-5.6 proposed a similar weighting with emphasis on:
- Website absence as strongest signal (confirmed)
- Uber Eats dependency as conversion angle (added as enrichment target)
- Proximity for in-person sales (confirmed — walkable zone)

GPT-5.6's key addition: **vend un résultat, pas un outil** — the pitch should
promise "plus de commandes directes et d'avis" not "un site QR code."
