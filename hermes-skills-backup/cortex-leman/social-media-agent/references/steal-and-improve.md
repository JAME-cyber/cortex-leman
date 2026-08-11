# Steal & Improve — Competitor Content Strategy Extraction

Methodology for reverse-engineering a competitor's content strategy and extracting actionable improvements for your own pipeline.

## When to Use

- User drops a YouTube/TikTok/Reels link and asks "what can we learn from this?"
- User drops an X/Twitter link and says "on vole" (steal it)
- You need to benchmark against a specific creator or brand
- Building a content strategy for a new Pilote IA client

## Methodology A — Video Analysis

### Step 1: Metadata Extraction
```bash
yt-dlp --no-warnings --print "%(title)s|||%(channel)s|||%(duration)s|||%(upload_date)s|||%(view_count)s|||%(like_count)s" "URL"
```
Extract: title, channel, duration, views, likes. Calculate engagement ratio (likes/views).

### Step 2: Visual Analysis
Download the video and extract frames at 2fps:
```bash
yt-dlp -f "worst[ext=mp4]" -o "/tmp/analysis.mp4" "URL"
ffmpeg -y -i /tmp/analysis.mp4 -vf "fps=2" -q:v 2 -vframes 20 frames_%02d.jpg
```
Analyze with vision model for:
- Style (AI-generated vs live vs 3D animation vs mixed)
- Transitions, text overlays, visual identity
- Production quality level

### Step 3: AI vs Human Detection
Key tells for AI-generated content:
- **NOT AI:** Perfect character stability across frames, readable text on objects, lip-sync precision, consistent caricatures
- **Likely AI:** Morphing between frames, text artifacts, inconsistent character features

### Step 4: Steal & Improve Matrix
For each element identified:

| Element | Can We Copy? | How? | Effort |
|---|---|---|---|
| Format (length, arc) | Usually yes | Adapt narrative structure | Low |
| Engagement hooks | Usually yes | Adapt for niche | Low |
| Visual style | Depends | May need different tools | Medium-High |
| Character consistency | Hard with AI | Reference photos + triple-lock prompting | High |
| Transitions | Yes | ffmpeg post-prod | Low |

### Step 5: Action Plan
Translate stealable elements into concrete recommendations:
1. What to copy immediately (low effort, high impact)
2. What to adapt (medium effort)
3. What requires new capabilities (investment decision)

## Methodology B — Tweet / Copywriting Pattern Extraction

Use when the user drops a tweet/X link. The goal is to extract the **narrative structure** (not the words) and regenerate adapted versions for the client's niche.

### Step 1: Extract Tweet Content
```bash
curl -sL "https://api.fxtwitter.com/<user>/status/<id>" | python3 -c "
import sys, json
d = json.load(sys.stdin)
t = d.get('tweet', {})
print(t.get('text', ''))
"
```
Fallback: scrape `og:description` meta tag from the HTML page if API returns null.

### Step 2: Decompose the Narrative Pattern
Identify the structural elements — NOT the words, the **shape**:

- **Opening hook:** What emotion/tension does it create? (contrast, surprise, outrage)
- **Cost anchor:** What number makes it concrete? (salary, price, time)
- **Process sequence:** Does it use visual markers (→ → →, bullet lists, numbers)?
- **Punchline:** How does it close? (irony, cost reversal, call to action)

Write out the pattern as a template: `[Persona reacts emotionally] + [cost of current method] + [AI does it faster/cheaper] + [→ process steps] + [punchline with number]`

### Step 3: Generate Adapted Posts
Send the decomposed pattern to GPT-5.6 with instructions to apply it to the client's niche. Key rules:
- FR-CH language (not français de France)
- Respect X character limit (280 chars)
- Keep the structural markers (arrows → are a visual signature)
- Each post MUST end with a concrete number (CHF, hours, %)
- NO hashtags if the original pattern doesn't use them — the absence is part of the aesthetic

### Step 4: Inject Into Calendar
Replace specific calendar slots with the stolen pattern posts. Mark them with `"format": "stolen-pattern"` for tracking.

```python
for day in cal["calendar"]:
    if day["day"] == target_day:
        for i, post in enumerate(stolen_posts):
            day["posts"][i] = {
                "platform": "x",
                "time": times[i],
                "content": post["content"],
                "format": "stolen-pattern",
                "angle": post["angle"]
            }
```

### Example: @RoundtableSpace Quant Agent Pattern (Aug 2026)

**Source tweet shape:** "Ken Griffin, CEO of Citadel, said he's fairly depressed watching AI do a week of PhD work in a few hours. Citadel pays $400,000 to $650,000 a year for that work."

**Decomposed pattern:**
1. Powerful person reacts emotionally (depressed, stunned, blêmi)
2. Exact cost of current method ($400k-650k salary)
3. AI does it in minutes
4. Process arrows: → → → (concrete steps)
5. Punchline: cost reversal

**Adapted for Pilote IA (FR-CH fiduciaires):**
> Le consultant a blêmi : 1'500 CHF/jour pour un audit répétitif. Un agent IA le traite en 90 s → collecte → analyse → synthèse → recommandations. 1 journée facturée pour 1 min 30 de traitement.

## Example: Le Monde Moderne Video Analysis (Aug 2026)

**"Brégançon Brawl"** — 103s satire politique, 15% engagement ratio.

Findings:
- 3D animation traditionnelle (Blender/Maya), NOT text-to-video AI
- Characters: caricatures sculptées manuellement, riggées, réutilisables
- Arc narratif complet: hook → escalation → punchline en 103s
- Key learning: the narrative arc (not the visual style) is the stealable element
- Improvement for our stack: apply same 3-act structure to AI-generated content (Seedance/Hailuo), where character consistency is our weak point but narrative structure is platform-independent

## Methodology C — Competitor Landing Page Analysis

Use when a competitor tweet reveals a product or service (not just a content pattern).
Goes beyond tweet structure: extracts the **positioning, copywriting, and go-to-market** strategy.

### Step 1: Tweet → Bio Link → Landing Page

```
Tweet → fxtwitter API extract → author bio → follow website URL → landing page
```

1. Extract tweet via fxtwitter API (Methodology B Step 1)
2. Read author `description` and `website` fields from the API response
3. Navigate to the website URL — this is usually the product/landing page
4. Extract full landing page copy via `browser_console` (`document.querySelector('main').innerText`)

### Step 2: Competitive Matrix

Build a comparison table against your own offering:

| Dimension | What to compare |
|---|---|
| Business model | Formation vs consulting vs SaaS |
| Audience | Freelances vs PME vs enterprise |
| Pricing tier | One-shot vs retainer vs subscription |
| Technical depth | Can they code? Or pure content? |
| Compliance | Mentioned? Operationalised? Absent? |
| Status | Pre-launch? Live? Scaling? |
| Engagement quality | Bookmark/follower ratio (not just raw numbers) |

### Step 3: Copywriting Pattern Extraction

Decompose the landing page copy the same way you decompose tweet structure:

- **Metaphors**: Physical, visceral images that make abstract pain concrete (e.g. "tu fais le facteur entre ChatGPT et ton business")
- **Anti-hype framing**: Explicitly rejecting competitor promises ("pas de promesse ridicule")
- **Tone markers**: Pragmatic vs enthusiastic, specific vs generic
- **Structure**: Problem → diagnosis → solution → proof

Write each pattern as a reusable template in a copywriting patterns file (see `references/pilote-ia-copywriting.md`).

### Step 4: Feed the Content Engine

For each competitor identified:
1. **Add to watchlist** — `scout-x` workspace `data/watchlist.yaml`, priority high, focus "CONCURRENT DIRECT"
2. **Create kanban signal** — `hermes kanban create "COMPETITOR: @handle - description" --assignee orchestrator --body "..."`
3. **Save to fact_store** — Competitor profile + any reusable patterns discovered
4. **Sync watchlist** to all profiles (orchestrator, researcher, ideator need the context)

### Example: @mathieuhq / Hermes Boost (Aug 2026)

**Trigger:** Tweet about CLI hardening for Hermes servers (134 bookmarks, 449 followers = 30% ratio)

**Landing page:** businessfreelance.fr — waitlist for "Hermes Boost" formation

**Key stealable patterns:**
- Metaphor "le facteur" (concrete image for the ChatGPT copy-paste workflow problem)
- Anti-hype tone ("pas de promesse ridicule sur une IA qui dirigera ton business toute seule")
- Minimalist landing (one page, one email field, one promise — 134 bookmarks with 449 followers)

**Strategic verdict:** Not a direct competitor (freelances FR vs PME FR-CH), but validates the Hermes consulting market in French and demonstrates the copywriting tone that works with FR audiences.

**Files produced:** `~/pilote-ia/copywriting-patterns.md` (3 patterns + meta-rules)

## Cross-References

- `le-narrateur-augmente` skill — premium reporting and multimodal design
- `cortex-leman-agent-patterns` — safe agent design patterns
- Seedance triple-lock pattern (memory) — for character consistency in AI video
- `pilote-ia-copywriting.md` — Pilote IA copywriting patterns library (FR-CH specific)
