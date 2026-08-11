# Infomaniak DNS Management via Internal API

Manage DNS records programmatically through Infomaniak's manager API using the browser session. Faster and more reliable than the UI (which renders via Angular web components that are hard to automate).

## Prerequisites

- Logged into `manager.infomaniak.com` via browser
- Know `domain_id` — find via the URL when viewing the domain: `/v3/{account_id}/ng/domain/{domain_id}/dns/manage-zone`

## Login (Angular 17 Material)

Angular Material inputs need the native setter trick:

```javascript
(() => {
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  const e = document.getElementById('mat-input-0'); // email field
  const p = document.getElementById('mat-input-1'); // password field
  setter.call(e, 'email@example.com');
  e.dispatchEvent(new Event('input', {bubbles: true}));
  setter.call(p, 'PASSWORD');
  p.dispatchEvent(new Event('input', {bubbles: true}));
  p.dispatchEvent(new Event('blur', {bubbles: true}));
  const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Connexion'));
  btn.click();
})()
```

Wait ~3s for redirect, then navigate to the DNS zone URL.

## API Endpoints

Base: relative paths from `manager.infomaniak.com`

| Method | Path | Purpose | CSRF? |
|--------|------|---------|-------|
| `GET` | `/api/domain/{domain_id}/dns/record` | List all records | No |
| `POST` | `/api/domain/{domain_id}/dns/record` | Create a record | Yes |
| `PUT` | `/api/domain/{domain_id}/dns/record/{record_id}` | Update a record | Yes |
| `DELETE` | — | **NOT SUPPORTED** (404 method_not_found) | — |

### CSRF Token

Decode the `MANAGER-XSRF-TOKEN` cookie and send as `X-XSRF-TOKEN` header:

```javascript
const mt = document.cookie.split('; ').find(c => c.startsWith('MANAGER-XSRF-TOKEN='));
const csrf = decodeURIComponent(mt.substring('MANAGER-XSRF-TOKEN='.length));
```

## Full PUT Example

```javascript
(() => {
  const mt = document.cookie.split('; ').find(c => c.startsWith('MANAGER-XSRF-TOKEN='));
  const csrf = decodeURIComponent(mt.substring('MANAGER-XSRF-TOKEN='.length));
  return new Promise(resolve => {
    const xhr = new XMLHttpRequest();
    xhr.open('PUT', '/api/domain/{domain_id}/dns/record/{record_id}', true);
    xhr.withCredentials = true;
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-XSRF-TOKEN', csrf);
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4) resolve({status: xhr.status, response: xhr.responseText.substring(0, 300)});
    };
    xhr.send(JSON.stringify({
      source: '.',      // '.' = apex, 'www' = subdomain
      type: 'A',        // A, AAAA, CNAME, MX, TXT, SRV
      target: '1.2.3.4',
      ttl: 3600
    }));
  });
})()
```

## Key Behaviors

1. **Cannot change record TYPE via PUT** — `A → CNAME` returns HTTP 500. Create new + neutralize old.
2. **Cannot DELETE records** — API returns 404 `method_not_found`. Workaround: PUT to a neutral target (`::1` for AAAA, harmless IP for A).
3. **GET needs no CSRF** — safe to list anytime.
4. **Session expires** — if redirected to login, re-auth and navigate back.
5. **POST may create auxiliary TXT records** — creating apex CNAME via POST triggered Infomaniak redirect metadata TXT records. Always verify with GET after.
6. **Apex CNAME limitation** — RFC forbids CNAME at apex when SOA/NS/MX exist. Use A record → target's IP instead.

## Session Re-Authentication (tested Aug 2026)

Sessions expire mid-task. When redirected to login:

1. **`form.submit()` RESETS the password field** — Angular reactive forms clear on submit. Password shows "Champ obligatoire" error after a form.submit() call.
2. **Must set password + click in same IIFE** — separate calls fail because Angular clears state between executions.
3. **`browser_console` with async `setTimeout` Promises can trigger `about:blank`** — the browser navigates away. Use sequential `browser_snapshot` or separate synchronous `browser_console` calls instead.
4. **Odoo backend login ≠ Infomaniak login** — different credential sets. Check vault/session history for Odoo credentials separately.

Working re-auth pattern:

```javascript
(() => {
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  const e = document.getElementById('mat-input-0');
  const p = document.getElementById('mat-input-1');
  setter.call(e, 'email@example.com');
  e.dispatchEvent(new Event('input', {bubbles: true}));
  setter.call(p, 'PASSWORD');
  p.dispatchEvent(new Event('input', {bubbles: true}));
  p.dispatchEvent(new Event('blur', {bubbles: true}));
  const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Connexion'));
  btn.click();
})()
```

After ~3s, check `window.location.href` to confirm redirect to Manager succeeded.

## Migration Pattern: Point Domain to Odoo

For migrating an Infomaniak-managed `.ch` domain to Odoo hosting:

1. **Resolve target**: `dig +short alconstdigital.odoo.com A` → get Odoo IP (e.g. `162.19.60.151`)
2. **Update apex A record**: PUT to Odoo's IP
3. **Update www CNAME**: PUT target to `{subdomain}.odoo.com`
4. **Neutralize AAAA**: PUT target to `::1` (Odoo is IPv4-only)
5. **Verify propagation**:
   ```bash
   dig +short @ns11.infomaniak.ch example.ch A
   dig +short @8.8.8.8 example.ch A
   ```

Infomaniak NS apply changes **instantly**. Public resolvers update within minutes.
