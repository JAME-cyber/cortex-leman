# Antibot Scraping pour LEC (fetch_source.py)

Récupérer du contenu sur des sources finance protégées par Cloudflare (IEA, parfois Euronext) SANS browser headless, SANS stealth-browser-mcp, SANS proxy. Python pur.

## Solution adoptée : curl_cffi

**curl_cffi** = bindings Python pour curl-impersonate, une version de curl qui mime l'empreinte TLS/JA3 de Chrome réel. Cloudflare voit un Chrome authentique dans le handshake TLS — pas un bot.

- Repo : `https://github.com/lexiforest/curl_cffi` (PyPI : `curl-cffi`)
- Install : `pip install curl-cffi` (déjà dans `~/crypto-project/.venv`)
- Aucune clé, aucun compte, aucun proxy
- Surface d'attaque : zéro (pas de `exec()`, pas de browser, pas de dépendances externes douteuses)

## Module : `scripts/fetch_source.py`

Usage (depuis `~/crypto-project/`) :

```bash
source .venv/bin/activate
python3 fetch_source.py "https://www.iea.org/reports/key-questions-on-energy-and-ai" -o research/iea.md
python3 fetch_source.py "https://www.digitimes.com/news/a20241113PD220.html"  # stdout
python3 fetch_source.py "https://..." --no-cache   # bypass cache
python3 fetch_source.py "https://..." --json       # structuré pour programme
```

**API programmatique** (depuis un autre script) :

```python
from fetch_source import fetch, to_markdown
data = fetch("https://www.iea.org/reports/...")
# data = {url, final_url, status, fetched_at, title, meta_description, html, len, blocks, paywall_signals}
print(to_markdown(data))
```

## Performance réelle (testé Jul 2026)

| Source | Résultat | Latence | Notes |
|---|---|---|---|
| **IEA** "Key Questions on Energy and AI" | ✅ 246 ko récupérés | 0.1s | Derrière Cloudflare — curl_cffi passe. Le widget Turnstile présent dans le HTML est juste un widget, pas un block |
| **DigiTimes** (article TSMC/TEL) | ⚠ Paywall | 1.9s | HTML récupéré (145 ko, titre + meta desc + sommaire) mais contenu article exige un compte. Pas un pb de bypass |
| **Euronext** (pages research/markets) | ✅ OK | 0.1s | CloudFront standard, pas d'antibot. `/markets/research` 404 (page déplacée, pas un block) |

## Profils d'impersonation

`fetch_source.py` utilise `chrome131` (le profil le plus récent au Jul 2026). Profils disponibles dans curl_cffi : `chrome`, `chrome131`, `safari17_0`, `edge99`, `firefox`. Pour ajout : passer `impersonate=` au `requests.get()`.

**Pas besoin de rotation** : un seul profil Chrome récent suffit. La rotation sert seulement quand le site fait du fingerprinting avancé (Datadome, PerimeterX) — pas le cas des sources LEC actuelles.

## Cache disque

- Emplacement : `~/crypto-project/research_cache/` (hash SHA256 de l'URL, fichiers `.json`)
- TTL par défaut : 7 jours (override via `--ttl`)
- Le cache stocke le HTML brut complet ; le texte est extrait à la volée à chaque appel
- Le 2e appel sur la même URL = instantané (0.00s)

## Détection de blocage (dans le module)

Le module détecte et signale en stderr :
- **Cloudflare challenge** (`jschl_vc`, `cf-mitigated`, `just a moment...`)
- **Cloudflare Turnstile** widget
- **Captcha** (hcaptcha, recaptcha)
- **Access denied** / 403 / Forbidden
- **Paywall** (5 patterns : "subscribe to read", "premium content", etc.)

⚠️ Un block détecté n'empêche pas l'output — il warn l'utilisateur. À l'agent de juger si le contenu est exploitable ou non (cf. IEA : Turnstile widget flagged mais contenu OK).

## Quand curl_cffi NE suffit PAS

| Cas | curl_cffi | Alternative |
|---|---|---|
| Cloudflare challenge JS (page interstitielle) | ❌ | Playwright + profil Chrome persistant |
| Datadome / PerimeterX (fingerprinting comportemental) | ❌ | Playwright + residential proxy + delays humains |
| Paywall (compte requis) | ❌ (récupère la page paywallée) | Compte enregistré ou source alternative |
| JS-rendered SPA (React/Vue apps) | ❌ (pas d'exec JS) | Playwright ou Apify RAG browser |
| PDF de rapport complet | ❌ (récupère la landing) | Télécharger le PDF + `pymupdf` pour extract |

**Pour LEC aujourd'hui (IEA, Euronext, DigiTimes, Reuters, Bloomberg) : curl_cffi suffit dans 90% des cas.** Les 10% restants = PDFs de rapports à télécharger séparément.

## Comparatif : pourquoi PAS stealth-browser-mcp ?

Le tweet de @0x0SojalSec (Jul 2026) présentait `vibheksoni/stealth-browser-mcp` (97 tools, bypass Cloudflare, MCP server). Audit complet dans `github-repository-analysis` skill (Phase 4.5). Verdict :

| Critère | curl_cffi | stealth-browser-mcp |
|---|---|---|
| LOC | 240 | 13 000 |
| Dépendances | 1 (curl_cffi) | 12 + 1 git-pinned non vérifiée |
| `exec()` arbitrary | 0 | 3 (1 unrestricted) |
| Surface d'attaque | nulle | élevée (Docker obligatoire) |
| Performance IEA | 0.1s, 246 ko | ~identique |
| Maintenance | curl_cffi stable | nodriver forks cassent tous les 2-6 mois |

**Conclusion** : stealth-browser-mcp est utile pour du **scraping DOM complexe** derrière antibot (cloner des éléments, intercepter du réseau). Pour LEC (lecture de pages articles), c'est overkill et risqué. curl_cffi couvre le besoin.

## Limites connues de `fetch_source.py`

- **Landing pages JS-heavy** (ex: IEA) → le HTML arrive mais le contenu riche du rapport est dans le PDF. Le module récupère le description/abstract ; pour le corps complet, download PDF séparément.
- **Pas de `--pdf` mode** pour l'instant (à ajouter : pymupdf extraction).
- **Troncature à 50 000 chars** dans la sortie markdown pour éviter de flood stdout. Le cache garde tout.
