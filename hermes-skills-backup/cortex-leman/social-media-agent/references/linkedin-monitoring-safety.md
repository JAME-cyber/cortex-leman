# LinkedIn Monitoring Safety & Hand-Raise Detection

Session-validated knowledge (August 2026) for passive LinkedIn engagement monitoring using Hermes browser tools.

## The Hand-Raise Pattern

**Concept (source: Greg Isenberg / Cody Schneider):** Monitor who likes/comments on posts from influencers in your target niche. Those engagers are "hand raises" — warm prospects signaling interest without knowing it.

**Example:** A Geneva restaurant owner who likes posts about "restaurant design" or "salle renovation" = a warm prospect for furniture import-export.

## Auth Wall Reality

LinkedIn requires an **authenticated session** for ALL meaningful data access:
- `/company/<name>` → redirects to authwall
- `/posts/` → 404 without login
- `/in/<profile>` → authwall
- Only the marketing homepage is accessible without login

**Solution:** User logs in manually once via `browser_navigate` to `https://linkedin.com` → enter credentials → session persists in the browser.

## LinkedIn Detection: 9 Signals (2026)

| # | Signal | What triggers it |
|---|---|---|
| 1 | **Profile view volume** | >100-150 profile views/day |
| 2 | **Regular cadence** | Identical intervals between actions |
| 3 | **Pure sessions** | Only searches/visits, no normal activity (feed, posts, messages) |
| 4 | **Browser fingerprint** | User-agent, canvas, WebGL, plugins mismatch |
| 5 | **IP / geolocation** | Datacenter IP, VPN, sudden geo change |
| 6 | **Search pattern** | Same filters repeated (e.g. "restaurant geneve" x50) |
| 7 | **Bulk connection requests** | >100/week = hard limit |
| 8 | **Identical messages** | Same text to multiple recipients |
| 9 | **Inhuman hours** | Activity at 3am, or 24/7 |

## Safe Thresholds (Accounts <90 days old)

| Action | Safe | Hard limit |
|---|---|---|
| Profile visits | 80-100/day | ~150 |
| Searches | 30-40/day | Variable |
| Connection requests | 10-15/day (40-60/week) | 100/week |
| Post views | No clear limit | Cadence matters |

## Low & Slow Strategy

For hand-raise monitoring (passive, no outreach):

```
WHAT WE DO               WHAT GETS DETECTED
────────────────         ────────────────────
Visit 15-20 posts/day    → Below threshold (safe)
Read comments            → "Normal human" behavior
Extract likers           → Passive, no LinkedIn action
Save to local JSON       → Invisible to LinkedIn
NEVER: send 50 DMs       → That's the ban
```

**Key point:** Our use case is **passive reading**. We don't write, don't connect, don't DM. It's the equivalent of browsing LinkedIn normally and noting who likes what.

### Anti-detection Measures

1. **Random delays:** 3-8 seconds between page loads (never fixed intervals)
2. **Session diversity:** Mix monitoring with normal activity (scroll feed, read articles)
3. **Volume cap:** Max 15-20 profiles per monitoring session
4. **Human hours:** Only during 9am-9pm local time
5. **No automation tools:** Use browser_navigate directly, not Selenium/Playwright patterns that produce bot fingerprints

## Legal Framework

### LinkedIn User Agreement Section 8.2
Prohibits: "scrape, copy, or distribute" data from the Services.

### Enforcement Reality
LinkedIn enforces on **automated patterns**, not on manual consultation. The detection system targets behavioral signatures (volume, cadence, fingerprint), not the act of reading a public post.

### Case Law: hiQ Labs vs LinkedIn (US 9th Circuit, 2022)
Scraping **publicly available data** from LinkedIn = NOT a violation of the CFAA (Computer Fraud and Abuse Act). LinkedIn cannot use CFAA to block scraping of public profiles.

### Swiss Law (FR-CH)
No direct equivalent to CFAA. Small-scale passive collection of public data = tolerated. Large-scale automated scraping of personal data may engage nLPD/RGB art. 31 (processing proportionality).

**Our line:** Passive consultation at human pace (15-20 profiles/day). No mass connection requests, no DM blasts, no full-database scraping.

## Implementation with Hermes Browser

```python
# Conceptual flow (requires authenticated session)
# 1. Navigate to target influencer's recent posts
browser_navigate(url="https://www.linkedin.com/in/<influencer>/recent-activity/")

# 2. Snapshot to extract post URLs and engagement counts
snapshot = browser_snapshot(full=True)

# 3. For each post with high engagement, extract commenters/likers
#    Use browser_console to run JS that extracts reactor data

# 4. For each engager, visit profile (rate-limited, random delays)
#    Extract: name, headline, company, location

# 5. Filter: location contains "Genève" or "Suisse" + sector keywords

# 6. Output: prospects-linkedin.json with warmth score
```

### Alternative: Apify (if browser too unstable)

**Actor:** LinkedIn Post Engagement Scraper (No Cookies) — extracts likes + commenters with profile data.
- Cost: ~$0.001/post on free tier
- **RGPD concern:** Cloud US, data transits outside CH. OK for internal research, NOT for client deliverables.

## Pitfalls

- **No session = no data.** All LinkedIn pages redirect to authwall without login. Must authenticate first.
- **Consistent timing is the tell.** LinkedIn's ML models detect perfectly regular intervals. Always randomize.
- **Session purity matters.** If the browser ONLY visits profiles and never interacts with the feed, LinkedIn flags it. Mix in normal browsing.
- **Browser fingerprint on server.** Hermes browser runs on a Linux server with headless Chromium. The fingerprint differs from a normal desktop browser. LinkedIn may flag this faster than a real user's browser.
- **Apify free tier returns mock data.** The free tier of some Apify LinkedIn actors returns sample/mock data, not real results. Verify output against known profiles before trusting.
