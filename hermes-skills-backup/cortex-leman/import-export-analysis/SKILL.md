---
name: import-export-analysis
description: "Use when calculating landed cost or Go/No-Go for imports."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [import-export, landed-cost, margin-analysis, go-no-go, switzerland, b2b-prospecting]
    category: cortex-leman
    related_skills: [sourcing-agent, sourcing-to-content]
---

# Import-Export Analysis

Landed cost calculation, margin analysis, Go/No-Go dossier generation, and B2B prospect identification for import-export projects. This is the **analysis and decision layer** that sits on top of `sourcing-agent` (supplier discovery).

## Trigger

- User asks "is this product worth importing?"
- User wants a Go/No-Go decision dossier for a product
- User needs to calculate real margin after logistics
- User wants B2B prospects for an import niche
- Any landed cost / margin question for physical goods crossing borders

## Workflow

### Step 1 — Gather Sourcing Data
Either from a `sourcing-agent` brief or manual research:
- FOB unit price + MOQ
- Product volume & weight per unit
- Supplier location (affects port of departure)

### Step 2 — Calculate Landed Cost
Full chain, always. See [references/landed-cost-formula.md](references/landed-cost-formula.md) for the complete formula.

```
Product FOB
+ Freight (maritime or air)
+ Origin charges (THC, doc fee, BL fee)
+ Insurance (0.3% × 110% CIF)
= CIF
+ Customs duty (tariff × CIF)
+ Import VAT (on CIF + duty)
+ Destination port charges
+ Customs broker / transit fee
+ Inland transport (port → final warehouse)
= LANDED COST TOTAL (TTC)
− VAT (recoverable if VAT-registered)
= LANDED COST NET (ex-VAT)
```

**Critical insight (GPT-5.6 validated):** Logistics cost (freight + duty + VAT + transit + storage) typically represents **60-80% of FOB cost**. "Marge 100%" YouTube claims become 4% net. Always calculate the full chain, not the facial ratio.

### Step 3 — Competitor Benchmark
Find at least 3 local competitors with real prices. Sources:
- B2B suppliers (Schäfer Shop CH, Manutan, LUSINI for hospitality)
- B2C retail (Galaxus, Digitec for consumer goods)
- Specialist wholesalers
- Use `web_search` + `browser_navigate` to get actual current prices

### Step 4 — 3-Scenario Margin Analysis (MANDATORY)

| Scenario | Pricing | Conditions | Purpose |
|---|---|---|---|
| **Premium** | +30-50% vs market | Sur-mesure, high-end client | Validate the opportunity exists |
| **Realistic** | Market mid-price | Direct sale, moderate volume | Operational reality |
| **Worst case** | Aggressive pricing | Unsold stock, extended storage | Kill bad opportunities |

**Rule:** If the realistic scenario gives <10% net margin, the deal only works in premium AND pre-sold. Volume at low price is a trap.

### Step 5 — Risk Assessment Matrix

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Quality insufficient | varies | High | Pre-shipment inspection (SGS/Tetra, ~$300) |
| Maritime delay >32d | Medium | Medium | Order 8 weeks before delivery |
| Client wants to see/touch | High | High | Free sample (DHL ~CHF 150) |
| Unsold inventory | High | CRITICAL | **PRE-SELL before ordering** |
| Missing origin certificate | Low | Medium | Require in purchase contract |

### Step 6 — Go/No-Go Dossier Generation

Produce a structured dossier that can be:
- Forwarded to a client or partner
- Used as a case study to sell audit services
- Stored as project documentation

**Structure:**
1. Executive summary — 3-scenario table with verdict (GO/Marginal/NO-GO)
2. Produit sourcé — supplier, FOB prices, MOQ, volume/weight
3. Landed cost breakdown — full chain with sources per line item
4. Prix marché concurrent — at least 3 competitors with real prices
5. Conformité & risques — applicable norms, risk matrix with mitigation
6. Conclusion — conditions impératives pour GO, investissement minimum viable

**PDF generation:** Use `fpdf2` with DejaVu Sans TTF fonts. Do NOT use Helvetica core font — it only supports latin-1 and crashes on em-dashes, accented characters, or any Unicode beyond ASCII. See pitfalls below.

Store output in `cases/{niche}-{market}/dossier-go-no-go.pdf`.

### Step 3a — Travel & Freight Intelligence (optional)

When estimating project costs or sourcing travel, use [fast-flights scraper](references/fast-flights-scraper.md) to:
- Estimate air freight for urgent samples (vs DHL ~CHF 150-300)
- Include sourcing travel costs (GVA→PVG/CAN/HKG) in project ROI
- Monitor flight price windows for optimal buying trips

```python
pip install fast-flights  # MIT, no API key, 3 deps
```

### Step 7 — B2B Prospect Identification (optional)

When the analysis is for a specific B2B niche (e.g., restaurant furniture):

1. **Find new market entrants** — Gault&Millau new entries, Lausanne Tourisme new spots, industry press
2. **Score prospects on fit:**
   - Volume potential (how many seats/units?)
   - Budget signal (chef-star, premium location, new build)
   - Product match (does their concept align with our sourcing?)
   - Timing (newly opened = already equipped but may need phase 2; renovating = active buyer)
3. **Rank and output top 3** with phone/address/concept/why-they-fit

## Switzerland Import Quick Reference

See [references/switzerland-import-rules.md](references/switzerland-import-rules.md) for full details.

| Rule | Summary |
|---|---|
| **ALE Suisse-Chine** | Duty-free (0%) with Form F origin certificate since 2014 |
| **TVA import** | 8.1% on (CIF + duty), recoverable |
| **Port of entry** | Basel (rhine port) for maritime containers |
| **Mobilier** | HS 9401/9403, EN 12521/12520 norms |
| **Electronics** | CE + RoHS + RED (complex, flag proactively) |

## Pitfalls

1. **fpdf2 Unicode crash** — The built-in `Helvetica` font only supports latin-1. Any em-dash (—), curly quote, or accented character causes `FPDFUnicodeEncodingException`. **Fix:** Add DejaVu Sans TTF fonts explicitly:
   ```python
   pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
   pdf.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
   pdf.add_font('DejaVu', 'I', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf')
   ```
   Then use `pdf.set_font('DejaVu', ...)` everywhere.

2. **pandoc PDF without LaTeX** — `pandoc -o output.pdf` requires a LaTeX engine (`xelatex`, `pdflatex`). If not installed, it fails silently. Check `which xelatex` first, or fall back to fpdf2.

3. **Confusing prix de vente with marge** — A product bought at 8 EUR and sold at 40 EUR does NOT have a 32 EUR margin. After freight, duty, VAT, storage, marketing, defects, and sales costs, the real margin might be 3 EUR. The 3-scenario analysis exists precisely to kill this illusion.

4. **TheFork / DataDome blocking** — TheFork.ch uses DataDome anti-bot. Use `web_search` to find restaurant info from indexed pages instead of navigating directly.

5. **SocialPulse data mismatch** — Existing SocialPulse CSV data (1500+ restaurants) covers **website presence** (for web services), not **furniture purchasing intent**. Don't reuse it for furniture B2B prospecting.

## Key Decisions Framework

**When to say NO-GO:**
- Realistic scenario <10% margin AND no premium positioning possible
- Product requires complex compliance (electronics with radio/lithium) without in-house expertise
- MOQ requires capital that can't be pre-sold to 2-3 clients

**When to say GO CONDITIONNEL:**
- Premium scenario shows 30%+ margin
- Realistic scenario is marginal (<10%) but product allows differentiation (sur-mesure, private label)
- Capital investment is bounded (<CHF 20K) and can be pre-sold

**Priority order (Luke Pierce playbook validated):**
1. Client before product
2. Pre-sell before order
3. Premium before volume
4. One niche before diversification
5. Manual pilot before automation
