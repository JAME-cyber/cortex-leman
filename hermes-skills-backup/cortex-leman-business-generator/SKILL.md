---
name: cortex-leman-business-generator
category: cortex-leman
description: |
  Create business applications from Cortex Leman technical capabilities. Transform technical research into SaaS products for PME FR-CH. Dual-stack (Docker + Vercel), multi-agent (Narrateur, Gardien), API integration (OpenRouter, Kie.ai, xAI TTS). Compliance validation included.
  Reference docs in references/: kieai-api-reference, socialpulse-lead-gen, socialpulse-annemasse-v2-pipeline, socialpulse-pitcher-v2-conversational-agent, socialpulse-voice-agent-xai-tts, socialpulse-hybrid-lead-scoring, hybrid_marketing_packages, zenithia-competitive-analysis, haute-savoie-74-campaign-batch001, cortex-leman-pricing.
author: Cortex Leman Team
version: 1.0.0
tags: [business, saas, dual-stack, multi-agent, compliance, frontend, backend]
---

# Cortex Leman Business Generator

Transform technical capabilities into business applications for PME FR-CH.

## Overview

This skill enables rapid creation of SaaS applications from Cortex Leman's technical research capabilities. It follows a proven pattern:

- **Business First**: Start with business problem → Technical solution (not reverse)
- **Dual Stack**: Backend on existing Docker infrastructure + Frontend on Vercel
- **Multi-Agent**: Leverage existing Cortex Leman agents (Narrateur, Gardien, Oeil)
- **API Integration**: OpenRouter (text) + Kie.ai (image) with proper error handling
- **Validation Layer**: Compliance validation before delivery
- **Production Ready**: Docker, FastAPI, health checks, monitoring

## Use Cases

- **Compliance Generator**: Transform RGPD/IA obligations into social media posts
- **Trend Alert System**: Convert ArXiv research into business insights
- **Security Dashboard**: Transform OWASP standards into visual reports
- **Audit Reports**: Generate compliance reports from technical findings

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│              BUSINESS APPLICATION (SaaS)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              FRONTEND (Next.js + Vercel)          │  │
│  │              Input Form + Result Display            │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         ORCHESTRATOR (FastAPI)                      │  │
│  │         /api/generate endpoint                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│           ┌───────────────┼───────────────┐               │
│           ▼               ▼               ▼               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  NARRATEUR   │  │   GARDIEN    │  │  EXTERNAL    │  │
│  │  (Content)   │  │ (Validation) │  │     APIs     │  │
│  │              │  │              │  │              │  │
│  │ - Marketing  │  │ - RGPD       │  │ - OpenRouter │  │
│  │ - Copywriting│  │ - Legal      │  │ - Kie.ai     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Backend (Docker Stack)

### Step 1.1: API Client Libraries

Create modular clients for external APIs:

**openrouter_client.py** (Text generation):
```python
class OpenRouterClient:
    def generate_linkedin_post(self, brief: str, tone: str) -> str
    def generate_twitter_post(self, brief: str) -> str
    def generate_all_posts(self, brief: str, platforms: List[str]) -> Dict
```

**kieai_client.py** (Image generation):
```python
class KieAIClient:
    def generate_compliance_images(self, brief: str, image_count: int) -> List[Dict]
    def _poll_result(self, task_id: str) -> Optional[Dict]
```

### Step 1.2: Agent Integration

**gardien_validator.py** (Compliance validation):
```python
class GardienValidator:
    def validate_post(self, text: str, platform: str) -> ValidationResult
    def _check_terminology(self, text: str, platform: str) -> Dict
    def _check_legal_coherence(self, text: str, platform: str) -> Dict
```

Validation rules:
- Exact terminology (RGPD vs GDPR)
- No proprietary industry jargon
- Legal coherence
- No unrealistic claims (100% compliant)
- Adaptation for PME context

### Step 1.3: Orchestrator

**compliance_generator.py**:
```python
class ComplianceGenerator:
    def generate(self, request: GenerationRequest) -> GenerationResult
    
    # Phase 1: Generate posts (Narrateur)
    def _generate_posts(self, request: GenerationRequest) -> Dict[str, str]
    
    # Phase 2: Validate (Gardien)
    def _validate_posts(self, posts: Dict[str, str], platforms: List[str]) -> Dict[str, dict]
    
    # Phase 3: Generate images (Kie.ai)
    def _generate_images(self, request: GenerationRequest) -> List[Dict]
```

### Step 1.4: FastAPI Endpoint

**api/main.py**:
```python
@app.post("/api/generate")
async def generate(request: GenerateRequest) -> GenerateResponse:
    # Get generator
    generator = get_generator()
    
    # Execute generation
    result = generator.generate(gen_request)
    
    # Return response
    return GenerateResponse(
        success=result.success,
        posts=result.posts,
        images=result.images,
        validation=result.validation,
        metadata=result.metadata
    )
```

### Step 1.5: Docker Integration

**docker-compose.override.yml**:
```yaml
services:
  business-generator:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - KIEAI_API_KEY=${KIEAI_API_KEY}
    depends_on:
      - postgres
      - redis
    networks:
      - cortex-leman-network
```

## Phase 2: Frontend (Next.js + Vercel)

### Step 2.1: Project Setup

```bash
npx create-next-app@latest cortex-leman-generator
cd cortex-leman-generator
npm install axios react-hook-form zustand tailwindcss
```

### Step 2.2: Input Form Component

**components/InputForm.tsx**:
```tsx
export function InputForm() {
  const { brief, platforms, imageCount, tone } = useStore()
  
  return (
    <form onSubmit={handleSubmit}>
      <textarea 
        placeholder="Ex: Nouvelle obligation RGPD pour IA générative"
        value={brief}
        onChange={(e) => setBrief(e.target.value)}
      />
      
      <CheckboxGroup label="Plateformes">
        <Checkbox label="LinkedIn" value="linkedin" />
        <Checkbox label="Twitter" value="twitter" />
      </CheckboxGroup>
      
      <Select label="Ton" value={tone} onChange={setTone}>
        <option value="professional">Professionnel</option>
        <option value="accessible">Accessible</option>
        <option value="urgent">Urgent</option>
      </Select>
      
      <RangeInput 
        label="Nombre d'images" 
        min={1} max={4} 
        value={imageCount}
      />
      
      <Button type="submit">Générer</Button>
    </form>
  )
}
```

### Step 2.3: Result Display Component

**components/ResultDisplay.tsx**:
```tsx
export function ResultDisplay() {
  const { posts, images, validation } = useStore()
  
  return (
    <div className="space-y-6">
      {posts.linkedin && (
        <Card>
          <CardHeader>
            <h2>LinkedIn Post</h2>
            <CopyButton text={posts.linkedin} />
          </CardHeader>
          <CardContent>
            <p>{posts.linkedin}</p>
            <ValidationBadge result={validation.linkedin} />
          </CardContent>
        </Card>
      )}
      
      <div className="grid grid-cols-2 gap-4">
        {images.map((img) => (
          <ImageCard key={img.index} image={img} />
        ))}
      </div>
    </div>
  )
}
```

### Step 2.4: API Integration

**lib/api.ts**:
```typescript
export async function generateCompliancePost(request: GenerateRequest) {
  const response = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  return response.json()
}
```

### Step 2.5: Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## Phase 3: Testing & Deployment

### Backend Testing

```bash
# Test individual components
python scripts/openrouter_client.py
python scripts/kieai_client.py
python scripts/gardien_validator.py

# Test full generator
python scripts/compliance_generator.py

# Test API
curl http://localhost:8001/health
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"brief": "Nouvelle obligation RGPD", "platforms": ["linkedin"]}'
```

### Frontend Testing

```bash
npm run dev
# Open http://localhost:3000

npm run build
npm run start
```

### Full Stack Deployment

```bash
# Deploy backend (Docker)
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Deploy frontend (Vercel)
vercel --prod

# Configure Nginx reverse proxy
# Add route /compliance -> frontend Vercel
# Add route /api/compliance -> backend API
```

## API Keys & Configuration

### Environment Variables

Create `.env`:
```bash
# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxx
OPENROUTER_MODEL=deepseek/deepseek-chat-v3

# Kie.ai
KIEAI_API_KEY=[REDACTED-KIEAI-KEY]
KIEAI_MODEL=nano-banana

# API
API_HOST=0.0.0.0
API_PORT=8001
ENABLE_VALIDATION=true
```

### API Models

| API | Model | Use Case | Cost |
|-----|-------|----------|------|
| OpenRouter | DeepSeek v3.2 | Text generation | $0.000001/prompt |
| Kie.ai | NanoBanana | Image generation | Credits based |

## Validation Rules

### Terminology Accuracy
- Use RGPD (not GDPR) for FR-CH context
- Explain abbreviations (DPO = Délégué à la Protection des Données)
- Avoid proprietary jargon ("best practice" → "standards reconnus")

### Legal Coherence
- No unrealistic claims (100% compliant → "conforme aux exigences actuelles")
- No guaranteed timeframes (24h → "en quelques jours")
- Accurate GDPR terminology

### PME Adaptation
- Content explicitly for small/medium enterprises
- Practical, actionable advice
- No enterprise-only jargon

## Monitoring & Metrics

### Health Checks

```bash
# Backend health
curl http://localhost:8001/health

# Response:
{
  "status": "healthy",
  "api_key_openrouter": true,
  "api_key_kieai": true,
  "generator_ready": true,
  "timestamp": "2026-04-06T16:00:00.000Z"
}
```

### Metrics to Track

- API response time (should be < 60s)
- Image generation time (Kie.ai polling)
- Validation pass rate
- User satisfaction (feedback loop)
- Cost per generation

### Grafana Dashboards

Create dashboard with:
- Request rate (requests/min)
- Success rate (%)
- API response time (p50, p95, p99)
- Image generation time
- Cost tracking

## Cold-Start ML Pattern (B2B Lead Scoring)

When a lead pipeline has zero labeled conversions but thousands of leads, use the **synthetic
cold-start pattern**: generate training labels from industry-known conversion rates, train a
foundation model (TabICLv2) on the synthetic data, and score all real leads. Swap in real labels
when available — zero code changes.

- **Template script**: `templates/ml/b2b_coldstart_lead_scorer.py` — reusable for any B2B domain
- **Working implementation**: SocialPulse `annemasse-agency/ml/synthetic_data_generator.py` + `lead_scorer.py`
- **Key technique**: logistic model with known coefficients (sector base rates, website/channel
  multipliers) + bootstrap augmentation + noise injection for realistic separability
- **Swap path**: `python lead_scorer.py --real-data real_conversions.csv` replaces synthetic with real

## Cross-LLM Analysis Validation

When producing a strategic analysis (business model teardown, market analysis,
go/no-go decision), cross-validate with a second LLM via OpenRouter before
delivering. This catches blind spots and adds nuance.

**Workflow:**
1. Produce initial analysis (your own reasoning + tool output)
2. Send a self-contained summary to GPT-5.6 via `curl` to OpenRouter
   (`openai/gpt-5.6-luna` or similar) with explicit instructions to challenge
3. Synthesize convergences, divergences, and additions into the final deliverable

```bash
source ~/.hermes/.env
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/analysis_prompt.json | python3 -c "..."
```

**When to use:** high-stakes strategic decisions, business model evaluation,
market entry analysis. **Not** for routine coding or simple lookups.

**Model selection:** Use a model from a different provider family than the one
that produced the initial analysis (e.g., GLM-5.2 initial → GPT-5.6 cross-check).
This maximizes the chance of catching provider-specific blind spots.

**See also:** `references/socialpulse-hybrid-lead-scoring.md` includes the
GPT-5.6 cross-validation of the lead scoring framework (convergences + additions).
`references/smma-counter-analysis.md` has the full CoachDydy teardown + 90-day action plan.

## Hybrid Lead Scoring for Outbound Prospecting

When converting a raw lead dataset into an actionable prospecting shortlist,
use a weighted business-rule score with ML as a secondary signal only.

**Key principle:** With zero real-world conversion labels, business rules beat
ML. A model trained on synthetic data (ROC-AUC 0.679) clusters scores too tightly
for useful prioritization — 1003/1509 leads appear as "Segment A."

**Validated formula (100 pts):** No website (25%) + Has phone (15%) + Core zone
(15%) + Channel reachability (15%) + Business type (10%) + SocialPulse score
(10%) + ML score (5%) + Name specificity (5%).

**Result:** 1502 independent restaurants → 206 Segment A targets (walkable zone,
no website, callable). See `references/socialpulse-hybrid-lead-scoring.md` for
the full methodology, chain exclusion list, segmentation thresholds, and the
swap path to real labels.

## Productized Agency Pattern (SocialPulse × Menuo × Services)

When combining lead-scoring data (SocialPulse), a proprietary SaaS tool (Menuo/QR),
and 5 digital marketing services into a single business, use the **productized agency
flywheel** — not a flat service catalog.

### Flywheel Architecture

```
SocialPulse (ML + rules scoring)
    → prioritized prospect list (Segment A: ~200 targets)
    → in-person prospecting with pre-filled audit
    → Menuo (QR menu + ordering + reviews) = productized entry point
    → recurring services (GBP, content, ads, loyalty) = ARPU uplift
    → case study with real data
    → labels feed back into SocialPulse ML → better scoring → better prospecting
```

**Key insight**: the agency is NOT "5 services in a list." It's a productized system
where each asset reinforces the others. SocialPulse finds clients, Menuo delivers
value, services increase ARPU, and results improve the ML model.

### 3-Tier Pricing (FR-CH, validated July 2026)

| Tier | Setup FR / CH | Monthly FR / CH | Scope |
|------|---------------|-----------------|-------|
| **Essentiel** | 149€ / 149 CHF | 79€ / 89 CHF | QR menu + mobile page + stats |
| **Growth** ⭐ | 690€ / 790 CHF | 299€ / 349 CHF | + direct ordering + Google optimization + reviews + 8 social posts/mo + reporting |
| **Performance** | 1490€ / 1690 CHF | 690€ / 790 CHF | + 12 social posts + local ads + loyalty + priority support |
| **Founder Beta** | 299€ | 149€/mo (60 days) | Growth tier at reduced rate for 3 first clients, in exchange for testimonial + data + feedback |

### Commercial Kit Structure

A complete agency launch kit lives at `~/restaurant-qr/menuo-agency-kit/`:
- `ONE-PAGER.md` — printable PDF (3 tiers, pricing, CTA)
- `PITCH-3TIERS.md` — sales script by channel (in-person, phone, Instagram)
- `LANDING-CONTENT.md` — landing page structure + SEO local
- `OBJECTIONS-BANK.md` — 10 objections + ROI calculator vs Uber Eats 30% commission
- `AUDIT-TEMPLATE.md` — pre-filled mini-audit to bring to prospects
- `FOUNDER-PROGRAM.md` — beta offer terms (3 places)
- `CONTRACT-TERMS.md` — simplified CGV (FR/CH pricing, RGPD, DPA)
- `LOOM-SCRIPT.md` — 3-min demo video script

### SMMA Rebranding Analysis (CoachDydy Counter-Analysis)

When evaluating a "guru academy" (SMMA, digital marketing course, etc.), apply the
**5-layer critical analysis**:

1. **Model identification** — Is this SMMA rebranded with AI? (Iman Gadzhi lineage)
2. **Service reality check** — Are the services real? Yes. Are they easy? No — the
   difficulty is B2B sales, not technical execution.
3. **Funnel pattern** — Live free → academy → Systeme.io pages (scarcity) → payment
   screenshots (survivor bias). Distinguish marketing from substance.
4. **Legal gaps** — RGPD (lead re-sale requires specific consent), Bloctel, ePrivacy,
   business registration, TVA/URSSAF. If unaddressed = red flag.
5. **Cross-LLM validation** — Send the analysis to GPT-5.6 via OpenRouter for
   counter-analysis. Synthesize convergences (SMMA rebrand, real but oversimplified)
   and additions (scope creep risk, lead validity contracts, platform dependency).

**Key GPT-5.6 insight**: "Le modèle n'est pas une arnaque, c'est un vrai métier —
mais un métier de commercial B2B local, pas de technicien IA." The difficulty ranking
per service: Sites (low tech, medium biz) → NFC/Reviews (low/medium) → Loyalty (medium/medium-high)
→ Ads (medium-high/high) → Lead gen (medium/very high — compliance + disputes).

See `references/smma-counter-analysis.md` for the full cross-validated teardown.

### Sector Specialization First

**Rule**: Do NOT launch 5 services across all business types simultaneously. Start with
ONE sector + ONE promise. For Menuo: restaurants indépendants (pizza, kebab, grill, snack).
Menuo doesn't solve a problem for a hair salon or a lawyer — it solves a clear problem
for a restaurant: menu display, direct ordering, reviews, customer return.

### Pillars
- **Acquisition**: SocialPulse scoring → top 200 targets → in-person prospecting
- **Delivery**: Menuo (productized, not custom) → install in 48h → 3h max onboarding
- **ARPU uplift**: Services as add-on modules (reviews, content, ads, loyalty)
- **Data flywheel**: Real labels from prospecting → retrain ML after 50+ responses

## Pitfalls

- **Apify Google Maps scraper input schema**: The actor `ittechinnovators/google-maps-business-scraper` requires `searchingKeywords` (string) and `location` (string) as the ONLY required fields. Do NOT pass `category`, `city`, `country`, or `searchStrings` — those fields do not exist and will cause validation errors. Optional fields: `maxResults` (int, default 10), `minRating` (number), `leadFilter` (enum: ALL|HOT_ONLY|HOT_WARM).
- **Keyword choice affects yield**: "plombier chauffagiste" returns ~15 results per city, "electricien solaire" returns ~12. Broader keywords = more leads. Test one query first before batching.
- **GMB lacks employee count**: Use review count as proxy (200+ reviews → likely PME 50+, 50-200 → sweet spot, <50 → TPE). Adjust scoring accordingly.
- OpenRouter: 401 Unauthorized → Check OPENROUTER_API_KEY is set correctly
- OpenRouter: 429 Rate Limit → Add exponential backoff in retry logic

### Kie.ai Issues

**Problem**: Image generation timeout / polling never completes
```
Root cause: The status field in recordInfo responses is called "state", NOT "status".
Polling data.get("status") always returns None → infinite loop / timeout.

Solution: Use data.get("state") — values are "processing" or "success".
```

**Problem**: No image URL found in response
```
Root cause: The result is in resultJson, which is a JSON-ENCODED STRING (not a dict).
Trying data["outputs"] or data["url"] returns nothing.

Solution: json.loads(data["resultJson"])["resultUrls"][0]
```

**Problem**: Wrong API endpoint for model
```
Kie.ai has TWO API families:
  - Market Jobs API (/api/v1/jobs/): all image models + non-Veo video
  - Dedicated Veo API (/api/v1/veo/): Veo3 models ONLY

Using the wrong one returns 400.
```

**Problem**: .png URL serves JPEG content
```
Kie.ai temp URLs (tempfile.aiquickdraw.com) serve JPEG regardless of extension.
Don't rely on file extension for format detection.
```

For the complete validated API reference with all quirks, model catalogs, and real measurements, see **references/kieai-api-reference.md**.

### Validation Issues

**Problem**: Too many validation errors
```
Solution: Review validation rules, adjust severity levels
```

**Problem**: False positives
```
Solution: Tune regex patterns, add whitelist terms
```

## Expansion Ideas

### V2: More Platforms
- Instagram (visual-first)
- Facebook (longer posts)
- TikTok scripts

### V3: Advanced Features
- Batch generation (10+ posts at once)
- Scheduling (publish later)
- Analytics (track engagement)
- A/B testing (compare versions)

### V4: AI Agent Coordination
- Le Narrateur + Le Gardien + L'Oeil (trend analysis)
- Multi-agent workflow optimization
- Agent-specific expertise routing

## 3-Source Reconciliation Pattern (Invoice/Order Audit)

A reusable micro-service pattern: compare 3 data sources → flag discrepancies → generate HTML report. Proven on the **Invoice Reconciler** (`~/import-export-project/scripts/invoice_reconciler.py`) — a 900-line engine that audits e-commerce agent invoices against Shopify orders and a COGs pricing grid.

### Architecture

```
Source A (reality)     Source B (reference)     Source C (claimed)
Shopify Orders CSV  +  COGs Grid JSON       +  Agent Invoice CSV
         \                |                     /
          →  Reconciliation Engine (3 passes)  ←
                    |
              Discrepancy List
                    |
              HTML Report (dark theme)
```

### Discrepancy Types (generalizable)

| Type | Severity | Detection Logic |
|------|----------|----------------|
| PRICE_MISMATCH | CRITICAL (>2€) / WARNING | unit_price × qty ≠ expected from reference grid |
| MISSING_INVOICE | CRITICAL | order exists in Source A but not in Source C |
| EXTRA_INVOICE | WARNING | line in Source C with no match in Source A (phantom charges) |
| QUANTITY_MISMATCH | WARNING | qty differs between sources |
| UNKNOWN_REFERENCE | WARNING | item not in reference grid |

### Key Implementation Details

- **Multi-source matching**: index invoice by `order_id|sku` key, then fallback fuzzy match on unlinked lines
- **Country-aware pricing**: COGs grid supports `shipping_cost_by_country` overrides
- **Tolerance threshold**: configurable (default ±0.02€) — below = match, above = flag
- **Demo generator**: built-in synthetic data generator with 5 error-injection scenarios (clean, overcharge, missing, bundle_errors, all) — test before deploying on real data

### Reuse for Other Audit Micro-Services

The pattern (3-source compare → discrepancy flag → HTML report) applies to:
- **Vendor bill reconciliation** (any B2B: telecom, SaaS, logistics)
- **Inventory audit** (system A vs system B vs physical count)
- **Compliance drift detection** (policy document vs actual config vs log evidence)

Working implementation: `~/import-export-project/scripts/invoice_reconciler.py`

## Voice Agent Pattern (Réceptionniste IA / Assistant Vocal)

Interactive voice agents for PME FR-CH — proven with prototype `~/prototypes/receptionniste-ia/` (July 2026).

Pipeline: `Browser audio → STT → LLM (intent + reply) → TTS → Browser audio playback`

**Providers validated:**
- STT: Browser Web Speech API (free, zero-config) or Groq Whisper (server-side, ~$0.04/h)
- LLM: Z.ai glm-4.7 via `https://api.z.ai/api/coding/paas/v4/chat/completions`
- TTS: Edge TTS `fr-CH-ArianeNeural` (free, Swiss French female)

**⚠️ Z.ai coding endpoint does NOT support STT** — `/audio/transcriptions` returns error 1211. Use a different provider for speech-to-text.

Full architecture, provider matrix, and reference implementation: see `cortex-leman-video-brief/references/voice-agent-architecture.md`.

Use cases: réceptionniste médicale, support client vocal, assistant téléphonique PME. Aligns with "Clinique/Santé" vertical in Agent Implementation Service.

## References

- Cortex Leman Main: `~/.hermes/skills/cortex-leman/`
- Docker Infrastructure: `cortex-leman-docker-infrastructure` skill
- OpenRouter: https://openrouter.ai/docs
- Kie.ai: https://docs.kie.ai
- Next.js: https://nextjs.org/docs
- Vercel: https://vercel.com/docs
- **SocialPulse Annemasse v2 Pipeline**: `references/socialpulse-annemasse-v2-pipeline.md` — zero-cost builder/filmer pipeline, adapter pattern for orchestrator integration, f-string shell heredoc pitfalls
- **SocialPulse PITCHER v2**: `references/socialpulse-pitcher-v2-conversational-agent.md` — state machine conversationnelle (10 états), intent detection FR (8 types), no-show recovery double détection, RGPD compliance, persistence JSON
- **SocialPulse Voice Agent (xAI TTS)**: `references/socialpulse-voice-agent-xai-tts.md` — intégration xAI TTS pour messages vocaux WhatsApp/Instagram. Text-cleaning (strip markdown/emojis/RGPD footer), conformité AI Act Art. 50 (disclosure prefix), pattern PitcherV2 → audio, cost model $0.028/msg, zero-dependency
- **TabICLv2 (Tabular Foundation Model)**: `references/tabicl-tabular-foundation-model.md` — modèle de fondation INRIA pour données tabulaires. Scikit-learn API, bat XGBoost sans tuning sur 80% des datasets. Cas d'usage SocialPulse: lead scoring (2,382 leads, **0 conversion labellisée** → cold-start via dataset synthétique). Benchmark script: `scripts/tabicl_benchmark.py`. Pipeline SocialPulse: `annemasse-agency/ml/synthetic_data_generator.py` + `annemasse-agency/ml/lead_scorer.py`. **Pitfall host**: numpy>=2.3 échoue (X86_V2 non supporté) → pin `numpy<2.3`. **Mesuré**: ROC-AUC 0.818, 334s pour 400 samples sur CPU (batch-only, pas de real-time).

## Success Criteria

- ✅ Backend API returns 200 OK
- ✅ Frontend displays generated content
- ✅ Images generated successfully
- ✅ Validation passes (> 80% confidence)
- ✅ Full deployment on Docker + Vercel
- ✅ End-to-end user flow works (< 60s)

## Maintenance

Update this skill when:
- New API providers added
- New validation rules needed
- New platforms supported
- Architecture patterns improved
- Security vulnerabilities found

---

**Created by Cortex Leman Team**
**Version: 1.1.0**
**Last Updated: 2026-07-07**
