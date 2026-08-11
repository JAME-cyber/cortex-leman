# Web Compliance Scanner — Reference

## What it is

A Python script (`scripts/web_compliance_scanner.py`) that scans any website URL and produces a structured RGPD-IA compliance report. Designed as a first-pass automated audit tool for Cortex Leman client engagements.

## When to use

- **Discovery phase (Jour 1-2)** of a client audit: run the scanner on the client's public-facing site to get an immediate compliance snapshot.
- **Lead qualification**: quick scan of a prospect's site to identify obvious RGPD gaps before the first meeting.
- **Pre/post comparison**: scan before and after a remediation engagement to measure improvement.

## The 7 checks

| # | Check | What it detects | RGPD/AI Act relevance |
|---|---|---|---|
| 1 | TLS / HTTPS | HTTP vs HTTPS, HSTS header | Art. 32 (security of processing) |
| 2 | Trackers & Analytics | 35+ trackers: GA, Meta Pixel, Hotjar, session recording, AI chatbots | Art. 7 (consent), Art. 44 (cross-border) |
| 3 | Bandeau cookies / CMP | 14 CMP platforms: Didomi, tarteaucitron, OneTrust, etc. | Art. 7 (consent), ePrivacy directive |
| 4 | Formulaires PII | Email, téléphone, nom, CB, SSN, file uploads | Art. 5 (minimization), Art. 13 (information) |
| 5 | Headers sécurité | CSP, HSTS, X-Frame-Options, etc. (8 headers) | Art. 32 (security) |
| 6 | Politique confidentialité | Links + text mentions (FR/EN/DE patterns) | Art. 13-14 (information obligations) |
| 7 | Mentions IA | Chatbot, IA, ML, GPT — triggers Art. 22 + AI Act assessment | Art. 22 (automated decisions), Art. 52 AI Act (transparency) |

## Usage

```bash
# Basic scan — text report to stdout
python scripts/web_compliance_scanner.py https://client.ch

# JSON output for API integration
python scripts/web_compliance_scanner.py https://client.ch --json

# Save to file
python scripts/web_compliance_scanner.py https://client.ch -o rapport.txt
```

Dependencies: `httpx`, `beautifulsoup4`, `lxml`

## Output format

The scanner produces a verdict: `CONFORME` / `CONFORME AVEC RÉSERVES` / `CONFORMITÉ PARTIELLE` / `NON-CONFORME`, with per-check status (pass/warn/fail/info) and actionable findings.

JSON output is structured for direct integration into the audit pipeline (`audit_generator.py`).

## Known limitations

1. **Static HTML only.** Sites that load trackers/consent banners via JavaScript (SPA, React, Vue) may show false negatives. The scanner sees the initial HTML payload only.
2. **Mitigation**: For JS-heavy sites, use a headless browser (Playwright/Puppeteer) to render the page first, then run the scanner on the rendered HTML. Not yet implemented.
3. **CMP detection is pattern-based.** Custom or obscure CMPs may be missed. The `cookie_text_present` flag helps catch these.
4. **Form PII detection is regex-based.** Dynamically rendered forms (React state, shadow DOM) won't be caught.
5. **No crawling.** Only scans the single URL provided. For multi-page audits, run per-page or integrate with a crawler.

## Integration with audit pipeline

The scanner is designed to be called by `core/compliance/audit_generator.py` as step 1 of the automated audit:

```
Client URL → web_compliance_scanner.py → JSON report
                                        → audit_generator.py (adds manual review items)
                                        → Gardien des Normes scoring (0-1)
                                        → Narrateur report (PDF)
```

## Test results (2026-07-01)

- `example.com`: correctly identified missing HSTS, missing CSP, missing privacy policy, missing CMP → verdict NON-CONFORME (expected for a placeholder page).
- `swisscom.ch`: detected HSTS + X-Content-Type-Options + Referrer-Policy, missing CSP. Trackers/CMP/privacy showed false negatives due to JS rendering — confirmed known limitation.
