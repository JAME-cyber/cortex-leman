# Cloudflare Pages Migration — End-to-End Reference

Tested Aug 2026 on alconstdigital.ch migration from Odoo Online.

## Decision: When to Migrate

| Signal | Keep Odoo | Migrate to Static |
|---|---|---|
| Just a vitrine page (no shop, no CRM) | | ✅ |
| Need collaborator editing (non-technical) | ✅ (UI builder) | ✅ (GitHub web editor) |
| Need custom fonts / CSS | | ✅ |
| Need e-commerce / Odoo modules | ✅ | |
| Want auto-deploy from git | | ✅ |
| Budget = €0 | | ✅ |

## Full Migration Workflow

### 1. Local Prep
```bash
# Ensure index.html is the main page
cd /path/to/project
cp design-final.html index.html
git init -b main
git add index.html
git commit -m "Initial commit"
```

### 2. GitHub Repo via REST API (bypasses `gh` scope issues)

`gh auth login --with-token` requires `read:org` scope, which users rarely grant.
Bypass entirely — use REST API for repo creation, embed token in remote for push:

```bash
# Create repo (works with repo-only PAT)
curl -X POST -H "Authorization: token $GH_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"site-name","public":true}'

# Push with token embedded
git remote add origin https://USER:$GH_TOKEN@github.com/USER/site-name.git
git push -u origin main

# CRITICAL: remove token from remote URL
git remote set-url origin https://github.com/USER/site-name.git
```

### 3. Cloudflare Pages via Wrangler CLI

Dashboard is blocked by Turnstile (anti-bot). Use Wrangler.

**Token creation (user must do this in browser):**
- dash.cloudflare.com → Profile → API Tokens → Create Custom Token
- Permission: Account → Cloudflare Pages → Edit
- Copy token (starts with `cfat_`)

**Deploy:**
```bash
npm install -g wrangler  # if not installed

# Create project (production_branch REQUIRED)
curl -X POST "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/pages/projects" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"site-name","production_branch":"main"}'

# Deploy
CLOUDFLARE_API_TOKEN=$CF_API_TOKEN \
CLOUDFLARE_ACCOUNT_ID=$CF_ACCOUNT_ID \
wrangler pages deploy . --project-name=site-name --branch=main
```

Site is live at `https://site-name.pages.dev`.

### 4. Connect Custom Domain

Via REST API (requires DNS zone already in Cloudflare):
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/pages/projects/site-name/domains" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"alconstdigital.ch"}'
```

If domain is NOT yet on Cloudflare, user must add the zone in the dashboard first
(nameserver change at registrar). This step cannot be automated via Wrangler.

### 5. Collaborator Setup (for non-technical editors like "Alex")

GitHub web editor is the simplest for non-devs:
1. Share repo URL: `https://github.com/USER/site-name`
2. Invite as collaborator: Settings → Manage access → Add people
3. Editor workflow: click `index.html` → pencil icon → edit → Commit changes
4. For auto-deploy on push: connect GitHub repo to Cloudflare Pages in dashboard
   (one-time setup, user does it once)

Alternative: Formspree.co for contact forms (replaces Odoo's built-in form).

## Pitfalls Encountered

### GitHub Device Verification Loop
GitHub sends a device verification code on every login attempt. Codes expire in
~5 min. The headless browser loses page state (about:blank redirect) after failed
attempts, requiring re-login from scratch. **Solution: skip `gh` entirely, use
PAT + REST API.**

### Infomaniak DNS — Cannot Be Automated

Domains at Infomaniak (`ns11/ns12.infomaniak.ch`) cannot have DNS records created
via API or browser automation (tested Aug 2026):

- **REST API** (`api.infomaniak.com`): Requires a bearer token generated from the manager
  UI. Basic Auth, `/1/login`, and `/1/profile` all return 401. No programmatic token issuance.
- **Browser login**: `login.infomaniak.com` uses React with internal state validation.
  `browser_type`, `nativeInputValueSetter`, and `document.execCommand('insertText')` all
  fail — the password field's "Champ obligatoire" error persists even when value is set.
  The form is never submittable via automation.

**Resolution:** User logs into `manager.infomaniak.com` manually and creates a CNAME:
1. Domaine → select domain → DNS / Records
2. CNAME: `www` → `project-name.pages.dev`
3. If root CNAME unsupported, set up URL redirect `@` → `www`

### Pitfall: Cloudflare Token OCR from Screenshots
When the user sends a screenshot of the Cloudflare token, the vision fallback
(`or_vision.py`) may misread characters. The `cfat_` prefix helps, but always
ask the user to **copy-paste the token as text** if the OCR'd version fails.
Token values are long (~50 chars) and case-sensitive — OCR error rate is high.

### `tokens/verify` Returns "Invalid" for Working Tokens
`GET /user/tokens/verify` returned `{"success":false}` for a token that worked
on `POST /accounts/{id}/pages/projects`. Do not use the verify endpoint to
validate a Cloudflare token — test against the actual target endpoint.
