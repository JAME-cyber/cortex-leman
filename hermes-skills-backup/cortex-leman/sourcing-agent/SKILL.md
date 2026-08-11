---
name: sourcing-agent
description: "Use when sourcing products from China for import-export."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sourcing, import-export, china, alibaba, procurement, b2b]
    related_skills: [grounded-citations, a2a-webhook-pipeline]
---

# Sourcing Agent — Import-Export China

Automated product sourcing pipeline. Input: product description. Output: structured brief with top suppliers, pricing, MOQ, lead times, quality signals, and risk assessment.

## Trigger

Webhook route `sourcing-request` OR direct delegation from another agent.

## Workflow

### Step 1 — Product Analysis
Parse the request. Identify:
- Product category and sub-category
- Target market (EU/CH/Global)
- Key specifications (material, size, certifications needed)
- Price target (if specified)
- Volume estimate (MOQ tolerance)

### Step 2 — Supplier Discovery
Search these sources in parallel (delegate_task batch):
1. **Alibaba.com** — `web_search "{product} site:alibaba.com"` + extract top listings
2. **1688.com** (domestic prices) — `web_search "{product} 1688 批发"` 
3. **Made-in-China.com** — `web_search "{product} site:made-in-china.com"`
4. **Global Sources** — `web_search "{product} site:globalsources.com"`
5. **Recent market intel** — `web_search "{product} wholesale price 2026"`

### Step 3 — Supplier Evaluation (5-axis scoring)

Score each supplier 0-10 on:

| Axis | Signal |
|---|---|
| **Price competitiveness** | Unit price vs market average |
| **MOQ flexibility** | Minimum order quantity vs buyer tolerance |
| **Verified status** | Gold Supplier, Trade Assurance, verified manufacturer |
| **Response & lead time** | Response rate, production capacity, shipping estimates |
| **Quality signals** | Ratings, reviews, years on platform, certifications (CE, RoHS, ISO) |

### Step 4 — Risk Assessment
Flag red flags:
- Unusually low price (< 60% market avg = scam risk)
- New supplier (< 1 year on platform)
- No Trade Assurance / no verified status
- Shipping to EU requires CE marking / REACH compliance
- Customs codes (HS code) and import duty estimate

### Step 5 — Brief Generation

Output format (delivered to Telegram + outbound webhook):

```
📋 SOURCING BRIEF: {product}
━━━━━━━━━━━━━━━━━━━━━━━━

🎯 TOP 5 SUPPLIERS

1. {Supplier Name} — Score: X/10
   🏭 {Verified status} | {Years on platform}y
   💰 ${price}/unit (MOQ: {qty})
   ⏱️ Lead time: {days}d | Response: {rate}%
   📊 Rating: {stars} ({review_count} reviews)
   🔗 {URL}
   ✅ Pros: ...
   ⚠️ Cons: ...

[repeat for 5 suppliers]

📦 LOGISTICS
   HS Code: {code}
   Import duty (EU): {rate}%
   Import duty (CH): {rate}%
   Shipping: Sea {days}d / Air {days}d
   Estimated landed cost: ${price}/unit

🚨 RISK FLAGS
   - {any red flags}

💡 RECOMMENDATION
   {Best pick + rationale}

━━━━━━━━━━━━━━━━━━━━━━━━
Sources: {citations}
```

## Prompt Template (for webhook)

```
Sourcing request received: {payload.product}

Execute the full sourcing-agent skill workflow:
1. Analyze product requirements
2. Search Alibaba, 1688, Made-in-China, Global Sources in parallel
3. Score top 5 suppliers on 5 axes
4. Assess risks (scam, compliance, customs)
5. Generate structured brief

Use grounded-citations for all claims. Deliver brief.
```

## Pitfalls

1. **Alibaba anti-bot** — pages may block extraction. Use web_search first to find listing URLs, then web_extract on the specific product pages. If blocked, use browser_navigate as fallback.
2. **Price volatility** — always note search date. Prices change weekly on B2B platforms.
3. **1688 is Chinese-only** — use web_search with Chinese keywords for domestic prices (30-50% cheaper than Alibaba export prices).
4. **CE compliance** — EU imports require CE marking for electronics, toys, medical devices. Flag this proactively.
5. **HS codes** — approximate codes from product description. Always recommend confirming with a customs broker.

## EU/CH Compliance Quick Reference

| Category | EU Requirement | CH Requirement |
|---|---|---|
| Electronics | CE, RoHS, REACH | Same as EU (MRA) |
| Toys | EN 71 | SN EN 71 (same) |
| Textiles | REACH, fiber labels | same |
| Cosmetics | CPNP notification | Swissmedic/FCPS |
| Food contact | LFGB/DGCCRF | FOPH |
