---
name: odoo-online-site-management
description: "Edit Odoo Online sites via browser automation."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [odoo, cms, browser-automation, website-builder, cloudflare-pages, static-migration]
---

# Odoo Online Site Management

Edit, theme, and manage websites hosted on Odoo Online (`company.odoo.com`) via Hermes browser tools, plus the decision framework for migrating to static hosting.

## When to Use

- Editing content on an Odoo Online website builder instance
- Cleaning up default theme blocks (pricing tables, stat counters, testimonials)
- Configuring theme colors via the builder UI
- Deciding whether to keep Odoo or migrate to static hosting (GitHub + Cloudflare Pages)

## Architecture

The Odoo website editor runs inside **two iframes**. The content iframe is at index 1:

```javascript
const ifr = document.querySelectorAll('iframe')[1];
const d = ifr.contentDocument;  // DOM
const w = ifr.contentWindow;    // Window (for Event constructor)
```

Editable content blocks are `#wrap [contenteditable="true"]` elements.
Snippets/blocks are identified by `data-snippet` and `data-name` attributes.

## The Change-Tracking Problem (CRITICAL)

Odoo's wysiwyg editor does **NOT** track raw DOM mutations. If you change `innerHTML` directly, Odoo won't detect the edit — the Save button stays disabled and changes are lost on next page load.

### Fix: Dispatch `input` Events

After ANY DOM change to a contenteditable element, dispatch an input event:

```javascript
(function() {
  const ifr = document.querySelectorAll('iframe')[1];
  const d = ifr.contentDocument;
  const w = ifr.contentWindow;
  const editables = d.querySelectorAll('#wrap [contenteditable="true"]');

  editables[0].innerHTML = '<h1>New Hero Title</h1><p>New subtitle</p>';

  // CRITICAL: trigger Odoo's change tracking
  editables[0].dispatchEvent(new w.Event('input', {bubbles: true}));
})()
```

After dispatching `input` events on all modified editables, the Save button becomes enabled. Click Save — changes persist across page reloads.

### Verify Save is Enabled

```javascript
const saveBtn = document.querySelector('[title="Sauver"]');
return { disabled: saveBtn?.disabled };
```

## Workflow

1. Navigate to `https://company.odoo.com/` (must be logged in)
2. Click **Modifier** (Edit) button to enter edit mode
3. Use `browser_console` to modify contenteditable blocks + dispatch `input` events
4. Verify Save button is enabled
5. Click **Sauver** (Save)
6. Navigate away and back to confirm changes survived

## Common Operations

### Delete Unwanted Blocks

Odoo themes ship with placeholder blocks (pricing tables, stat counters, testimonials). Remove them by snippet name:

```javascript
const ifr = document.querySelectorAll('iframe')[1];
const d = ifr.contentDocument;
const w = ifr.contentWindow;
const parent = d.querySelector('#wrap');

['s_three_columns', 's_comparisons', 's_pricing'].forEach(name => {
  const el = parent.querySelector(`[data-snippet="${name}"], [data-name*="${name}"]`);
  if (el) {
    el.remove();
    parent.dispatchEvent(new w.Event('input', {bubbles: true}));
  }
});
```

### Replace Stats/Numbers Blocks

Default stat counter blocks (e.g. "54% revenue growth") should be replaced with real content, not just emptied:

```javascript
editables[N].innerHTML = '<h2>Une approche simple</h2><p>Real content here...</p>';
editables[N].dispatchEvent(new w.Event('input', {bubbles: true}));
```

### Configure Theme Colors

Colors are set via the UI: **Thème** tab → hex inputs for primary/secondary colors. This is more reliable than CSS injection. Example values:
- Primary: `#000000` (black)
- Secondary/accent: `#E89560` (warm orange)

### Update Footer Content

Footer (address, phone, social links) is editable via contenteditable blocks in the `<footer>`/`<contentinfo>` section of the iframe.

## Pitfalls

### 1. CSS Injection via "Head/Body" UI Modal
The "Head/Body" button in theme settings often fails to open its modal. Workaround: inject a `<style>` tag via console into the iframe `<head>`.

### 2. Custom Fonts
Custom fonts (e.g. Josefin Sans, Playfair Display) require adding a `<link>` to Google Fonts in the iframe `<head>`. The theme font picker may not list them.

### 3. Session Expiry
Odoo sessions expire frequently. Every editing session may require fresh login before entering edit mode.

### 4. Refs Going Stale
Between `browser_snapshot` and `browser_type`, the Odoo editor's JS can re-render and invalidate ref IDs. Use `browser_console` with direct DOM manipulation instead of ref-based typing when this happens.

### 5. Save Resets DOM Changes
If you modify the DOM but Save was never truly enabled (event didn't fire correctly), clicking Save can RESET your changes. Always verify `saveBtn.disabled === false` before clicking Save.

### 6. Infomaniak Session Re-Authentication

When the Infomaniak session expires mid-DNS-task and you're redirected to login:

- **`form.submit()` resets the password field** — Angular's reactive form clears the value. Must set password AND click button in the **same JS execution** (see `references/infomaniak-dns-api.md` login section).
- **`browser_console` with `setTimeout` can cause `about:blank` navigation** — waiting inside `browser_console` via async Promises can trigger the browser to navigate to `about:blank`. Use sequential tool calls instead.
- **Odoo backend login ≠ Infomaniak login** — the Odoo instance (`company.odoo.com/web/login`) has its own credential set. Do not assume the Infomaniak password works for Odoo. Check vault/session history separately.

## Pointing a Domain to Odoo (DNS Migration)

To host a domain on Odoo (reverse of the static migration above), update the DNS records at the domain's registrar to point to Odoo:

1. **Resolve the Odoo instance IP**: `dig +short {subdomain}.odoo.com A`
2. **Update apex A record** to the Odoo IP
3. **Update `www` CNAME** to `{subdomain}.odoo.com`
4. **Neutralize AAAA** (Odoo is IPv4-only) — set to `::1` or remove
5. **Add the custom domain in Odoo**: Settings → Website → Domains
6. Odoo auto-generates the Let's Encrypt SSL cert once DNS propagates
7. The `noindex` meta tag Odoo shows for unverified custom domains disappears automatically after DNS propagation + Odoo cache refresh

### Diagnostic: DNS correct but Odoo not serving the site

When DNS is pointed to Odoo (A record → Odoo IP, CNAME → `*.odoo.com`) but the custom domain hasn't been added in Odoo's backend yet, Odoo exhibits these diagnostic signals:

- **HTTP 301 redirect** from custom domain → `{subdomain}.odoo.com` (served by `gunicorn`)
- **`noindex` meta tag** persists in the HTML `<head>`
- **404** when hitting the Odoo IP directly with `Host: custom-domain` header

Verification commands:
```bash
# Check for redirect (should NOT redirect to .odoo.com once configured)
curl -sIL https://custom-domain.ch 2>&1 | grep -i "HTTP\|location\|server"

# Check for noindex (should be absent once configured)
curl -sL https://custom-domain.ch 2>&1 | grep -i "noindex"

# Check authoritative DNS directly (Infomaniak NS = instant)
dig +short @ns11.infomaniak.ch custom-domain.ch A
```

If the redirect or `noindex` persists, the custom domain still needs to be added in Odoo backend (Settings → Website → Domains). DNS changes alone are not sufficient — Odoo must know about the domain to serve it directly.

### Infomaniak DNS API

For domains managed at Infomaniak, DNS records can be updated programmatically via the manager's internal API (faster than the Angular UI). See `references/infomaniak-dns-api.md` for the full API reference including CSRF token handling, endpoint patterns, and pitfalls (no DELETE support, cannot change record type via PUT).

## References

- `references/cloudflare-pages-migration.md` — Full end-to-end migration workflow (GitHub + Cloudflare Pages via Wrangler CLI), including collaborator setup and all pitfalls encountered in a real deployment.
- `references/infomaniak-dns-api.md` — Infomaniak DNS record management via internal manager API (browser session). CSRF pattern, endpoints, migration pattern to Odoo.
- `templates/deploy-cloudflare-pages.yml` — GitHub Actions workflow for auto-deploying to Cloudflare Pages on push. Requires repo secrets (`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`) set via API, and a PAT with `workflow` scope to push the file.

## When to Migrate to Static Hosting

Odoo Online is a closed CMS — no git deploy, no CI/CD, no collaborator workflow. If the site is a simple vitrine (no e-commerce, no Odoo modules), migrating to **GitHub + Cloudflare Pages** gives:

| Feature | Odoo Online | GitHub + Cloudflare Pages |
|---|---|---|
| Collaborator editing | Login sharing only | Git-based, branch reviews |
| Deploy speed | Manual UI clicks | Push → auto-deploy |
| Custom fonts | Hack via console | `<link>` in HTML |
| Cost | Subscription | Free |
| SSL | Included | Auto (Cloudflare) |
| Form handling | Built-in Odoo | FormSubmit.co or Formspree |

### Migration Steps

1. Export the final HTML from the design file (e.g. `variant-figma.html` → `index.html`)
2. Create GitHub repo: `curl -X POST -H "Authorization: token $TOKEN" https://api.github.com/user/repos -d '{"name":"site","public":true}'`
3. Push: `git remote add origin https://USER:TOKEN@github.com/USER/site.git && git push -u origin main`
4. Clean remote URL (remove embedded token): `git remote set-url origin https://github.com/USER/site.git`
5. Connect Cloudflare Pages to the repo (dashboard or Wrangler CLI)
6. Point custom domain DNS to Cloudflare

### Cloudflare Dashboard Anti-Bot

The Cloudflare dashboard (`dash.cloudflare.com`) runs Cloudflare Turnstile, which blocks headless browsers. Two approaches:
- **Wrangler CLI** (`npm install -g wrangler`): deploys to Pages without the dashboard. Requires a Cloudflare API token with **Pages Write** permission (see validated workflow below).
- **Manual**: user connects the repo in the dashboard (2 min, no automation needed).

### Validated Wrangler CLI Deployment (tested Aug 2026)

**Token requirements:** Custom token with permission **Account → Cloudflare Pages → Edit**. The "Edit Cloudflare Workers" template also works (includes Pages Write).

**Step 1 — Create the Pages project via REST API:**
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/pages/projects" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"site-name","production_branch":"main"}'
```
Note: `production_branch` is REQUIRED — omitting it returns error 8000033.

**Step 2 — Deploy via Wrangler:**
```bash
cd /path/to/site
CLOUDFLARE_API_TOKEN=$CF_API_TOKEN \
CLOUDFLARE_ACCOUNT_ID=$CF_ACCOUNT_ID \
wrangler pages deploy . --project-name=site-name --branch=main
```
Output confirms: `✨ Deployment complete! https://<hash>.site-name.pages.dev`

The project is also accessible at `https://site-name.pages.dev`.

### Pitfall: Cloudflare Token Verify Endpoint Is Unreliable

`GET /user/tokens/verify` may return `{"success":false,"errors":[{"code":1000,"message":"Invalid API Token"}]}` for a token that **actually works** on real API calls (e.g. `POST /accounts/{id}/pages/projects`). Do NOT trust the verify endpoint alone — test the token against the actual API endpoint you intend to use.

## GitHub PAT Scope Pitfalls

### `read:org` scope (for `gh` CLI)
When creating a GitHub PAT for repo automation, `gh auth login --with-token` requires `read:org` scope. Tokens with only `repo` scope fail with "missing required scope 'read:org'". The token still works for git operations and REST API calls via curl — bypass `gh` entirely:

### `workflow` scope (for CI/CD files — CRITICAL)
A PAT with only `repo` scope **CANNOT create or update files under `.github/workflows/`**. This restriction applies to ALL three methods:
1. **`git push`** → remote rejects: *"refusing to allow a Personal Access Token to create or update workflow without `workflow` scope"*
2. **Contents API** (`PUT /repos/{owner}/{repo}/contents/.github/workflows/deploy.yml`) → **404 Not Found** (even though the same API creates `README.md` fine)
3. **Git Data API** (blobs → trees → commits → refs) → tree creation **404 Not Found** for `.github/workflows/` paths

**Fix:** The user must add the `workflow` scope to their PAT at https://github.com/settings/tokens. There is no API workaround — this is a GitHub-enforced security boundary.

However, **GitHub Actions secrets CAN be set** with a `repo`-scope PAT (see below), so you can configure everything except the workflow file itself while waiting for the user to update the token.

## GitHub Actions Auto-Deploy Setup (Cloudflare Pages)

Once the workflow file is pushed (requires `workflow` scope), every `git push` to `main` auto-deploys to Cloudflare Pages. See `templates/deploy-cloudflare-pages.yml` for the workflow file.

### Setting Secrets via API (works with `repo`-scope PAT)

Install `pynacl`, get the repo's public key, encrypt each secret, and PUT it:

```python
import requests, base64
from nacl import public

GH_TOKEN = "ghp_..."
REPO = "user/repo"
headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# 1. Get repo public key
r = requests.get(f"https://api.github.com/repos/{REPO}/actions/secrets/public-key", headers=headers)
pk_data = r.json()
public_key = public.PublicKey(base64.b64decode(pk_data["key"]))
sealed_box = public.SealedBox(public_key)

# 2. Encrypt and set each secret
for name, value in [
    ("CLOUDFLARE_API_TOKEN", "cfat_..."),
    ("CLOUDFLARE_ACCOUNT_ID", "768e..."),
]:
    encrypted = sealed_box.encrypt(value.encode())
    requests.put(
        f"https://api.github.com/repos/{REPO}/actions/secrets/{name}",
        headers=headers,
        json={"encrypted_value": base64.b64encode(encrypted).decode(), "key_id": pk_data["key_id"]}
    )
```

Status 201 = secret created. The workflow file then references these as `${{ secrets.CLOUDFLARE_API_TOKEN }}`.

### Enabling Actions

If the repo is new, Actions may be disabled by default:
```bash
curl -X PUT -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/USER/REPO/actions/permissions" \
  -d '{"enabled":true,"allowed_actions":"all"}'
```

```bash
# Create repo via REST API (works with repo-only PAT)
curl -X POST -H "Authorization: token $TOKEN" \
  https://api.github.com/user/repos \
  -d '{"name":"site","public":true}'

# Push with embedded token
git remote add origin https://USER:$TOKEN@github.com/USER/site.git
git push -u origin main

# Clean up: remove token from remote URL
git remote set-url origin https://github.com/USER/site.git
```
