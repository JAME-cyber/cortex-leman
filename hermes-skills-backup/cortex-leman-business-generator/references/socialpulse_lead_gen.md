---
name: socialpulse-lead-gen
category: cortex-leman
version: 4.0.0
description: |
  SocialPulse v4 — Infrastructure de confiance pour la prospection B2B.
  Moat: le seul pipeline lead gen avec Médiateur déterministe, journal WORM,
  arbitrage humain, guardrails LLM, et conformité RGPD by design.
  Apply ce que Cortex Leman v5 a prouvé: l'IA ne décide JAMAIS seule.
  
  Sources: Apify (Google Maps, Europages), Scrapling (annuaires CH/FR, site analysis),
  OpenRouter (personnalisation), Kie.ai (infographies).
  
  Triggers: socialpulse, lead generation, prospection, campagne, cibler entreprises.

prerequisites:
  - Apify API token (APIFY_TOKEN in .env)
  - OpenRouter API key (OPENROUTER_API_KEY in .env)
  - Scrapling skill (~/.pi/agent/skills/scrapling-official/)
  - Kie.ai API key (optional, for infographics)

---

# SocialPulse v4.0 — Moat de Confiance B2B

## ÉVOLUTION: POURQUOI v4 EST UN MOAT

SocialPulse n'est plus un pipeline de lead gen. C'est une **infrastructure de confiance** pour la prospection B2B régulée.

Ce qui fait un moat (défendabilité) :
1. **Médiateur déterministe** — 0% LLM dans les décisions critiques (même principe que Cortex Leman v5)
2. **Journal WORM** — Chaque lead, chaque email, chaque scoring est hash-chainé et auditable
3. **Arbitrage humain** — L'IA propose, l'humain décide. Jamais l'inverse.
4. **Guardrails LLM** — PII detection, topic control, output safety sur chaque personnalisation
5. **Conformité RGPD by design** — Base légale tracée, retention auto, opt-out intégré
6. **Compilation de connaissances** — Chaque batch enrichit le knowledge vault du vertical

**Aucun concurrent n'a ça.** Apollo, ZoomInfo, Lusha, Demoable — aucun n'a de journal inviolable, de médiateur déterministe, ou de guardrails sur la personnalisation.

### Pourquoi c'est incopiable

| Ce qu'on a | Pourquoi c'est un moat |
|------------|----------------------|
| Journal WORM |RGPD Art. 30 exige un registre. Le nôtre est hash-chainé, pas un log plat. |
| Médiateur JsonLogic |Les règles de conformité sont déterministes et auditables. Un wrapper LLM ne peut pas reproduire. |
| Serment numérique |L'agent SocialPulse a un serment: ne jamais contacter un lead gelé, ne jamais outrepasser le budget. |
| Compilation verticale |Chaque campagne enrichit les suivantes. Effet réseau des données. |
| Arbitrage humain |Scoring < threshold → gel automatique → humain arbitre. Compliance et qualité. |

## CONCEPT

```
1 campagne = 1 fichier YAML dans campaigns/
1 exécution = 1 batch avec journal WORM complet
1 lead = 1 carte avec audit trail vérifiable
```

## POSITIONNEMENT

**"Le seul pipeline lead gen avec journal d'audit inviolable."**

> Les autres scrapent et spamment. Nous scrapons, qualifions avec transparence, et chaque action est traçable.

**Pitch client:** "Votre prospection B2B est-elle conforme RGPD? Avec SocialPulse, chaque lead est tracé, chaque email est auditable, chaque scoring est déterministe."

## ARCHITECTURE v4

```
┌──────────────────────────────────────────────────────────────────┐
│                   SOCIALPULSE v4.0                               │
│           Infrastructure de Confiance B2B                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────┐            │
│  │              COUCHE CONFIANCE                     │            │
│  │  (Ce qui rend SocialPulse unique)                 │            │
│  │                                                   │            │
│  │  🛡️ Médiateur Déterministe (JsonLogic)           │            │
│  │     → Vérifie conformité RGPD de chaque action   │            │
│  │     → Gel automatique si violation détectée      │            │
│  │     → 0% LLM, 100% prédictible                   │            │
│  │                                                   │            │
│  │  📝 Journal WORM (SHA-256 hash-chain)            │            │
│  │     → Chaque discovery, enrichment, email loggé  │            │
│  │     → Append-only, immuable, vérifiable          │            │
│  │                                                   │            │
│  │  ⚖️ Arbitrage Humain                              │            │
│  │     → Scoring < threshold → gel → humain décide  │            │
│  │     → Budget dépassé → gel → humain autorise     │            │
│  │     → Lead sensible → gel → humain valide        │            │
│  │                                                   │            │
│  │  🔒 Guardrails LLM (3 couches)                   │            │
│  │     → PII detection (ne jamais exposer données)  │            │
│  │     → Topic control (rester dans le vertical)    │            │
│  │     → Output safety (pas de contenu risqué)      │            │
│  │                                                   │            │
│  │  🤖 Serment SocialPulse                          │            │
│  │     → Ne jamais contacter un lead gelé           │            │
│  │     → Ne jamais outrepasser le budget             │            │
│  │     → Ne jamais ignorer un opt-out               │            │
│  │     → Toujours tracer dans le journal             │            │
│  └─────────────────────────────────────────────────┘            │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────┐            │
│  │           PIPELINE D'EXÉCUTION                    │            │
│  │                                                   │            │
│  │  ÉTAPE 1: DISCOVERY                              │            │
│  │  ┌───────────────────────────────────┐           │            │
│  │  │ Apify Google Maps ──→ PME brute   │           │            │
│  │  │ Apify Europages   ──→ complément  │           │            │
│  │  │ Scrapling         ──→ annuaires   │           │            │
│  │  │   ├── directory_crawl (local.ch)  │           │            │
│  │  │   ├── directory_crawl (pjaunes)   │           │            │
│  │  │   └── directory_crawl (findit)    │           │            │
│  │  │                                   │           │            │
│  │  │ Médiateur: vérifie base légale    │           │            │
│  │  │ Journal: log chaque source        │           │            │
│  │  └──────────────┬────────────────────┘           │            │
│  │                 ▼                                 │            │
│  │  ÉTAPE 2: ENRICHMENT                            │            │
│  │  ┌───────────────────────────────────┐           │            │
│  │  │ Apify contact_enricher ──→ emails │           │            │
│  │  │ Apify LinkedIn     ──→ profils    │           │            │
│  │  │ Scrapling site_analysis:          │           │            │
│  │  │   ├── Chatbot/IA détecté?         │           │            │
│  │  │   ├── RGPD banner?                │           │            │
│  │  │   ├── Mentions légales?           │           │            │
│  │  │   └── Signaux IA?                 │           │            │
│  │  │                                   │           │            │
│  │  │ Médiateur: PII check              │           │            │
│  │  │ Guardrails: PII detection         │           │            │
│  │  │ Journal: log chaque enrichment    │           │            │
│  │  └──────────────┬────────────────────┘           │            │
│  │                 ▼                                 │            │
│  │  ÉTAPE 3: QUALIFICATION (Déterministe)          │            │
│  │  ┌───────────────────────────────────┐           │            │
│  │  │ Scoring JsonLogic (0-100)         │           │            │
│  │  │ → employee_count × 0.25           │           │            │
│  │  │ → sector           × 0.30         │           │            │
│  │  │ → risk_indicator   × 0.25         │           │            │
│  │  │ → location         × 0.20         │           │            │
│  │  │                                   │           │            │
│  │  │ Si score < threshold:             │           │            │
│  │  │   → GEL AUTOMATIQUE               │           │            │
│  │  │   → Arbitrage humain requis       │           │            │
│  │  │   → Journal: motif du gel         │           │            │
│  │  │                                   │           │            │
│  │  │ Médiateur: vérifie règles RGPD    │           │            │
│  │  │ Journal: score + justification    │           │            │
│  │  └──────────────┬────────────────────┘           │            │
│  │                 ▼                                 │            │
│  │  ÉTAPE 4: PERSONNALISATION (Guardrails LLM)     │            │
│  │  ┌───────────────────────────────────┐           │            │
│  │  │ OpenRouter: email d'approche      │           │            │
│  │  │ → Guardrails PII: ne pas fuite    │           │            │
│  │  │ → Guardrails Topic: rester métier │           │            │
│  │  │ → Guardrails Output: pas de risque│           │            │
│  │  │                                   │           │            │
│  │  │ Kie.ai: infographie (optionnel)   │           │            │
│  │  │ OpenRouter: post LinkedIn         │           │            │
│  │  │                                   │           │            │
│  │  │ Médiateur: vérifie opt-out list   │           │            │
│  │  │ Guardrails: scan chaque output    │           │            │
│  │  │ Journal: log chaque personnalisation│         │            │            │
│  │  └──────────────┬────────────────────┘           │            │
│  │                 ▼                                 │            │
│  │  ÉTAPE 5: OUTPUT + COMPILATION                   │            │
│  │  ┌───────────────────────────────────┐           │            │
│  │  │ Lead cards JSON (audit trail)      │           │            │
│  │  │ → ~/socialpulse-output/{slug}/     │           │            │
│  │  │ → Retention auto (campaign.output) │           │            │
│  │  │                                   │           │            │
│  │  │ Compilation:                      │           │            │
│  │  │ → sector-insights.md              │           │            │
│  │  │ → objection-map.md                │           │            │
│  │  │ → compliance-gaps.md              │           │            │
│  │  │ → pricing-sensitivity.md          │           │            │
│  │  │                                   │           │            │
│  │  │ Journal: hash de clôture du batch │           │            │
│  │  │ → Vérifiable par audit externe    │           │            │
│  │  └───────────────────────────────────┘           │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                  │
│  ┌─────────────────────────────────────────────────┐            │
│  │           BOUCLE DE COMPILATION                   │            │
│  │                                                   │            │
│  │  compiled/{campaign}/                             │            │
│  │  ├── sector-insights.md    → enrichit scoring    │            │
│  │  ├── objection-map.md      → enrichit emails     │            │
│  │  ├── compliance-gaps.md    → enrichit Gardien    │            │
│  │  └── pricing-sensitivity.md→ enrichit pricing    │            │
│  │                                                   │            │
│  │  → Chaque batch rend le suivant plus intelligent  │            │
│  │  → Effet réseau: plus de campagnes = meilleur moat│            │
│  └─────────────────────────────────────────────────┘            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## MÉDIATEUR SOCIALPULSE (JsonLogic)

Le Médiateur est **déterministe** (0% LLM). Il vérifie 12 règles avant chaque action:

### Règles Discovery

```json
[
  {"==": [{"var": "discovery.source.legal_basis"}, "interet_legitime"]},
  {"<=": [{"var": "discovery.results_count"}, {"var": "campaign.discovery.max_results"}]},
  {"==": [{"var": "discovery.region.country"}, {"var": "campaign.target.countries"}]}
]
```

### Règles Enrichment

```json
[
  {"!=": [{"var": "enrichment.pii_detected"}, true]},
  {"==": [{"var": "enrichment.consent_status"}, "not_required_b2b"]},
  {"<=": [{"var": "enrichment.data_points"}, 5]}
]
```

### Règles Qualification

```json
[
  {">=": [{"var": "lead.score"}, {"var": "campaign.scoring.threshold"}]},
  {"!=": [{"var": "lead.opt_out"}, true]},
  {"!=": [{"var": "lead.on_dnc_list"}, true]}
]
```

### Règles Personnalisation

```json
[
  {"<=": [{"var": "personalization.email.word_count"}, {"var": "campaign.personalization.email.max_words"}]},
  {"==": [{"var": "personalization.opt_out_mention"}, true]},
  {"<=": [{"var": "personalization.budget_used"}, {"var": "campaign.budget.max_per_batch_usd"}]}
]
```

### Comportement de gel

```
Si UNE règle échoue:
  → Action GELÉE
  → Journal: "GEL: motif=X, lead=Y, règle=Z"
  → Attente arbitrage humain
  → Humain peut: valider (lever le gel) ou rejeter (supprimer le lead)
```

## JOURNAL WORM SOCIALPULSE

Chaque batch produit un journal inviolable:

```json
{
  "batch_id": "sp-2026-05-03-rgpd-001",
  "entries": [
    {
      "seq": 1,
      "timestamp": "2026-05-03T10:00:00Z",
      "action": "discovery.google_maps",
      "actor": "apify",
      "details": {
        "query": "\"cabinet comptable\" + Genève",
        "results": 18,
        "cost_usd": 0.90
      },
      "hash": "sha256:abc123...",
      "prev_hash": "0000000000000000..."
    },
    {
      "seq": 2,
      "timestamp": "2026-05-03T10:02:15Z",
      "action": "discovery.scrapling",
      "actor": "scrapling",
      "details": {
        "source": "local.ch",
        "results": 12,
        "pages_crawled": 3,
        "cost_usd": 0.00
      },
      "hash": "sha256:def456...",
      "prev_hash": "sha256:abc123..."
    },
    {
      "seq": 3,
      "timestamp": "2026-05-03T10:05:00Z",
      "action": "enrichment.site_analysis",
      "actor": "scrapling",
      "lead": "Dupont & Associés",
      "details": {
        "url": "https://dupont-comptable.ch",
        "chatbot_detected": true,
        "rgpd_banner": true,
        "privacy_policy": true,
        "risk_indicator": "high"
      },
      "hash": "sha256:ghi789...",
      "prev_hash": "sha256:def456..."
    },
    {
      "seq": 4,
      "timestamp": "2026-05-03T10:08:00Z",
      "action": "qualification.scoring",
      "actor": "mediateur",
      "lead": "Dupont & Associés",
      "details": {
        "score": 82,
        "breakdown": {
          "employee_count": 25,
          "sector": 30,
          "risk_indicator": 25,
          "location": 20
        },
        "status": "QUALIFIED"
      },
      "hash": "sha256:jkl012...",
      "prev_hash": "sha256:ghi789..."
    },
    {
      "seq": 5,
      "timestamp": "2026-05-03T10:10:00Z",
      "action": "personalization.email",
      "actor": "openrouter",
      "lead": "Dupont & Associés",
      "details": {
        "model": "deepseek/deepseek-v4-flash",
        "guardrails": {
          "pii_detected": false,
          "topic_safe": true,
          "output_safe": true
        },
        "word_count": 142,
        "opt_out_mention": true
      },
      "hash": "sha256:mno345...",
      "prev_hash": "sha256:jkl012..."
    }
  ],
  "batch_summary": {
    "total_discovered": 30,
    "total_qualified": 12,
    "total_frozen": 2,
    "total_cost_usd": 8.50,
    "batch_hash": "sha256:final789..."
  }
}
```

### Vérification d'intégrité

```python
def verify_journal(journal):
    """Vérifie la chaîne de hash du journal WORM"""
    for i, entry in enumerate(journal["entries"]):
        expected_prev = "0000000000000000..." if i == 0 else journal["entries"][i-1]["hash"]
        assert entry["prev_hash"] == expected_prev, f"Chaîne brisée à seq {entry['seq']}"
        # Recalculer le hash
        payload = json.dumps({k: v for k, v in entry.items() if k != "hash"}, sort_keys=True)
        computed = "sha256:" + hashlib.sha256(payload.encode()).hexdigest()
        assert entry["hash"] == computed, f"Hash invalide à seq {entry['seq']}"
    return True  # Journal intègre
```

## SERMENT SOCIALPULSE

```
═══════════════════════════════════════════════
  SERMENT DE L'AGENT SOCIALPULSE v4
═══════════════════════════════════════════════

Je suis un agent de prospection B2B réglé.

1. Je ne contacterai JAMAIS un lead gelé par le Médiateur.
2. Je ne dépasserai JAMAIS le budget sans arbitrage humain.
3. Je ne contacterai JAMAIS un lead ayant formulé un opt-out.
4. Je ne fuitai JAMAIS de PII dans mes outputs LLM.
5. Je tracerai CHAQUE action dans le journal WORM.
6. Je ne prendrai JAMAIS de décision de scoring seule — 
   le Médiateur décide, l'humain arbitre.
7. Je supprimerai les données après la retention configurée.
8. Je respecterai robots.txt et les CGU des sources.

Si je viole ce serment, le Médiateur me gel automatiquement.
L'audit trail est immuable et vérifiable.
═══════════════════════════════════════════════
```

## UTILISATION

### Lancer une campagne existante

```
"SocialPulse: lance la campagne cortex-leman-rgpd"
"SocialPulse: campagne cortex-leman-rgpd, batch 30 leads"
```

### Créer une nouvelle campagne

```
"SocialPulse: crée une campagne immobilier, agences à Lausanne, 50-150 employés"
```

L'agent va:
1. Copier `campaign-template.yaml`
2. Remplir selon les specs
3. **Configurer les règles JsonLogic du Médiateur** pour le vertical
4. Sauver dans `campaigns/[slug].yaml`
5. Confirmer le config avant exécution

### Consulter le journal

```
"SocialPulse: montre le journal du dernier batch"
"SocialPulse: vérifie l'intégrité du journal cortex-leman-rgpd"
```

### Arbitrage

```
"SocialPulse: montre les leads gelés"
"SocialPulse: valide le lead Dupont & Associés"
"SocialPulse: rejette le lead XYZ, motif: hors périmètre"
```

## CAMPAIGN CONFIG SYSTEM

| Fichier | Rôle |
|---------|------|
| `campaign-template.yaml` | Template vierge avec sections Médiateur + Journal |
| `campaigns/cortex-leman-rgpd.yaml` | Campagne active avec toutes les règles |

### Structure YAML v4

```yaml
campaign:
  name: "slug-campagne"
  label: "Nom Affiché"
  version: "4.0"  # Version SocialPulse

target: ...
scoring: ...

# NOUVEAU v4: Médiateur
mediateur:
  enabled: true
  rules_file: "mediateur_rules.json"  # JsonLogic rules
  gel_on_violation: true
  require_arbitrage_on_gel: true
  log_all_decisions: true

# NOUVEAU v4: Journal WORM
journal:
  enabled: true
  hash_algorithm: "sha256"
  storage: "local"  # local, s3, database
  retention_days: 365
  verifiable: true

# NOUVEAU v4: Guardrails LLM
guardrails:
  pii_detection: true
  topic_control: true
  output_safety: true
  max_retry_on_violation: 2

# NOUVEAU v4: Serment
serment:
  enabled: true
  version: "1.0"

discovery: ...
enrichment: ...
personalization: ...
output: ...
schedule: ...
budget: ...
compliance: ...
```

## SCRAPLING USAGE

Scrapling est installé comme skill pi: `~/.pi/agent/skills/scrapling-official/`

### 3 modes d'utilisation

| Mode | Étape | Fetcher | Anti-bot | But |
|------|-------|---------|----------|-----|
| `directory_crawl` | Discovery | StealthyFetcher | Cloudflare bypass | Crawler local.ch, pagesjaunes, findit.ch |
| `site_analysis` | Enrichment | Fetcher | Headers stealth | Détecter chatbot/IA/RGPD sur site lead |
| `competitor_monitoring` | Recurring | StealthyFetcher | Complet | Surveiller les concurrents |

### Directory Crawl (Discovery)

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://www.local.ch/fr/q/cabinet+comptable/Gen%C3%A8ve',
    headless=True, solve_cloudflare=True
)

businesses = page.css('.search-result')
for b in businesses:
    lead = {
        'name': b.css('.entry-title::text').get(),
        'address': b.css('.address::text').get(),
        'phone': b.css('a[href^="tel:"]::attr(href)').get(),
        'website': b.css('a.website::attr(href)').get(),
    }
```

### Site Analysis (Enrichment)

```python
from scrapling.fetchers import Fetcher

def analyze_lead_site(url):
    page = Fetcher.get(url, stealthy_headers=True)
    
    analysis = {
        'url': url,
        'has_chatbot': bool(page.css('[class*="chat"], [id*="chat"], iframe[src*="chat"]')),
        'has_cookie_banner': bool(page.css('[class*="cookie"], [id*="cookie"]')),
        'has_privacy_policy': bool(page.css('a[href*="privacy"], a[href*="confidentialite"]')),
        'has_legal': bool(page.css('a[href*="mentions"], a[href*="legal"]')),
        'ai_signals': len(page.css('[class*="ai"], [class*="gpt"], [class*="assistant"]')),
    }
    
    if analysis['has_chatbot'] or analysis['ai_signals'] > 0:
        analysis['risk_indicator'] = 'high'
    elif analysis['has_cookie_banner']:
        analysis['risk_indicator'] = 'medium'
    else:
        analysis['risk_indicator'] = 'low'
    
    return analysis
```

### Spider (crawl à grande échelle)

```python
from scrapling.spiders import Spider, Response

class DirectorySpider(Spider):
    name = "local-ch-comptables"
    start_urls = [
        "https://www.local.ch/fr/q/cabinet+comptable/Gen%C3%A8ve",
        "https://www.local.ch/fr/q/cabinet+comptable/Lausanne",
    ]
    concurrent_requests = 5
    robots_txt_obey = True
    download_delay = 2
    
    async def parse(self, response: Response):
        for result in response.css('.search-result'):
            yield {
                'name': result.css('.entry-title::text').get(),
                'address': result.css('.address::text').get(),
                'website': result.css('a.website::attr(href)').get(),
            }
        next_page = response.css('.pagination .next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

result = DirectorySpider(crawldir="/tmp/crawl-checkpoints").start()
result.items.to_json("/tmp/comptables.json")
```

## EXECUTION DU PIPELINE

```
# 0. CHARGER LA CONFIG (OBLIGATOIRE)
# Lire campaigns/{slug}.yaml

# 1. Discovery
# Apify: Google Maps + Europages
# Scrapling: directory_crawl (annuaires CH/FR)
# → Médiateur: vérifie base légale
# → Journal: log chaque source

# 2. Enrichment
# Apify: contact_enricher + LinkedIn
# Scrapling: site_analysis (signaux IA/RGPD)
# → Médiateur: PII check
# → Guardrails: PII detection
# → Journal: log chaque enrichment

# 3. Qualification
# JsonLogic scoring (déterministe)
# Si score < threshold → GEL → arbitrage humain
# → Médiateur: vérifie règles
# → Journal: score + justification

# 4. Personnalisation
# OpenRouter: email (guardrails 3 couches)
# Kie.ai: infographie (optionnel)
# → Médiateur: vérifie opt-out list
# → Guardrails: scan chaque output
# → Journal: log chaque personnalisation

# 5. Output + Compilation
# Lead cards JSON avec audit trail
# compiled/{campaign}/ mise à jour
# → Journal: hash de clôture
```

### Mode cron

```
Cron: lit campaign.schedule.cron
Prompt auto: "SocialPulse campagne [slug], batch [batch_size], journal WORM activé"
Deliver: campaign.schedule.deliver_to
```

## COUT ESTIME PAR VERTICAL

| Vertical | Leads/batch | Apify | LLM | Scrapling | Total |
|----------|-------------|-------|-----|-----------|-------|
| RGPD-IA | 50 | ~$6 | ~$5 | $0 | ~$11 |
| Immobilier | 30 | ~$4 | ~$3 | $0 | ~$7 |
| Assurance | 40 | ~$5 | ~$4 | $0 | ~$9 |
| Formation | 25 | ~$3 | ~$2 | $0 | ~$5 |

Scrapling est **gratuit** (local, pas de proxy payant). C'est un avantage coût majeur.

## RGPD COMPLIANCE BY DESIGN

SocialPulse v4 est conforme RGPD **par architecture**, pas par add-on:

| Obligation RGPD | Implémentation SocialPulse |
|-----------------|---------------------------|
| Base légale (Art. 6) | Intérêt légitime B2B, vérifié par Médiateur |
| Registre (Art. 30) | Journal WORM, hash-chainé, exportable |
| Droit d'accès (Art. 15) | Lead cards consultables, audit trail |
| Droit d'effacement (Art. 17) | Retention auto configurable |
| Droit d'opposition (Art. 21) | Opt-out intégré dans chaque email |
| Minimisation (Art. 5) | Max 5 data points par lead (Médiateur) |
| Sécurité (Art. 32) | Guardrails PII, journal immuable |
| Données sensibles (Art. 9) | Interdites (Médiateur bloque) |

### Opt-out automatisé

```json
{
  "opt_out_list": [
    {"email": "xxx@yyy.ch", "date": "2026-05-01", "source": "email_reply"},
    {"domain": "zzz.ch", "date": "2026-05-02", "source": "website_request"}
  ],
  "auto_check": true,
  "mediateur_blocks_if_opted_out": true
}
```

## PITFALLS

- Google Maps: doublons → dédupliquer par URL/IDE/SIRET
- Contact enricher: ne trouve pas toujours le DM → fallback email générique
- Scrapling: certains sites bloquent même StealthyFetcher → fallback Apify
- Kie.ai: peut échouer → retry 2x, sinon placeholder
- Apify rate limits: max 3 acteurs simultanés
- Suisse: pas de SIRET, utiliser l'IDE
- Budget: Médiateur gèle si dépassé → arbitrage humain
- Opt-out: TOUJOURS vérifier avant envoi (Médiateur)

## MODE PRODUIT (SaaS)

SocialPulse peut être vendu comme service **certifiable**:

| Offre | Prix | Inclus | Moat |
|-------|------|--------|------|
| Starter | 500€/batch | 1 campagne, 50 leads, emails, journal WORM | Journal auditable |
| Business | 2'000€/mois | 3 campagnes, 200 leads/mois, full pipeline, Médiateur | Conformité RGPD |
| Enterprise | 5'000€/mois | Campagnes illimitées, 500 leads/mois, arbitrage, certification | Certifiable LSTI |

### Pourquoi Enterprise peut se faire certifier

Le journal WORM + le Médiateur déterministe + l'arbitrage humain = **tout ce qu'un auditeur RGPD vérifie**. SocialPulse Enterprise est le seul lead gen tool qui peut passer un audit CNIL/PPDT sans modification.

## ARGUMENT URGENCE

**Base:** Shapira, N. et al. (2026). "Agents of Chaos." arXiv:2602.20021

38 chercheurs ont red-team des agents IA autonomes. Résultat: vulnérabilités sécurité/vie privée/gouvernance documentées.

**SocialPulse v4 prévient exactement ces failles:**

| Vulnérabilité "Agents of Chaos" | Guardrail SocialPulse |
|--------------------------------|----------------------|
| Compliance non-autorisée | Médiateur: bloque action non-autorisée |
| Divulgation infos sensibles | Guardrails PII: 3 couches de détection |
| Actions destructrices | Serment: ne jamais outrepasser le budget |
| Consommation incontrôlée | Médiateur: gel si budget dépassé |
| Faux rapports | Journal WORM: immuable, vérifiable |
| Accountability gap | Audit trail: chaque action tracée |

**Argumentaire:** "38 chercheurs ont prouvé que les agents IA fuient des données et mentent sur l'état du système. Notre pipeline lead gen est le seul avec un journal inviolable et un médiateur déterministe. Prouvez votre conformité."

## PSYCHOLOGIE DE VENTE B2B

### "C'est trop cher" = peur, pas budget

Référence: Knutson et al. (2007) — prix élevé active l'insula (douleur physique).

**5 mécanismes adaptés:**

**#1 Aider à décider, pas convaincre**
- "Mon but: vous aider à savoir si vous êtes exposé"
- "Dans 6 mois, si vous n'avez rien fait et qu'un contrôle CNIL arrive?"

**#2 Structurer le parcours = signal premium**
- Email recap dans l'heure
- Chaque interaction réduit l'incertitude

**#3 Assumer le prix sans le justifier**
- Annoncer. Se taire 5-8 sec. Cadrer la valeur.
- JAMAIS: "Je sais c'est cher mais..."

**#4 Engagement progressif (3 tiers)**
1. Diagnostic gratuit (30min) = premier "oui"
2. Synthèse avec recommandations = deuxième "oui"
3. Proposition commerciale = "oui" final naturel

**#5 Quantifier la douleur AVANT le prix**
1. "Combien de traitements de données sensibles?"
2. "Amende CNIL: jusqu'à 4% du CA ou 20M EUR"
3. "Quel est votre CA annuel?" → il fait le calcul lui-même
4. L'audit à CHF 4'500 est dérisoire vs le cout de l'inaction

**Règle:** C'est le prospect qui doit dire le chiffre. On pose les questions, il arrive à la conclusion.

## AGENT IMPLEMENTATION UPSALE

SocialPulse est le point d'entrée du flywheel Cortex Leman.

### Pipeline de conversion

```
SocialPulse (lead gen avec journal WORM)
  │
  │ PME détectée avec IA non conforme
  │ Score >= threshold, risk_indicator = "high"
  │
  ▼
Email d'approche (guardrails LLM, opt-out intégré)
  │ "Votre IA n'est pas conforme. On peut la rendre conforme."
  │
  ▼
Audit RGPD-IA (diagnostic gratuit 30min)
  │ "Votre chatbot viole l'AI Act. Voici les risques."
  │
  ▼
Agent Implementation Service (service payant)
  │ CHF 3'000 / 8'000 / 15'000+
  │
  ▼
Conformité Continue (retention)
  │ Monitoring mensuel, guardrails updates
  │
  ▼
Flywheel: nouveau besoin → SocialPulse
```

### Pricing Agent Implementation

| Niveau | Contenu | Prix |
|--------|---------|------|
| **Starter** | 1 agent, 1 processus, RAG basique | CHF 3'000 |
| **Business** | 2-3 agents, multi-processus, CRM | CHF 8'000 |
| **Enterprise** | Architecture complète, monitoring | CHF 15'000+ |

## COMPILED KNOWLEDGE

Chaque sortie = entrée potentielle d'un autre pipeline.

### Structure

```
socialpulse-lead-gen/
├── campaigns/
├── compiled/
│   └── {campaign}/
│       ├── sector-insights.md      → enrichit scoring
│       ├── objection-map.md         → enrichit emails
│       ├── compliance-gaps.md       → enrichit Gardien des Normes
│       └── pricing-sensitivity.md   → enrichit pricing
├── journaux/                        ← NOUVEAU v4
│   └── {campaign}/
│       ├── batch-2026-05-03-001.json
│       └── batch-2026-05-05-002.json
└── opt-out-list.json                ← NOUVEAU v4
```

### Format fichiers compilés

```yaml
---
campaign: cortex-leman-rgpd
compiled_date: 2026-05-03
source_batches: 5
total_leads: 250
verified: true
journal_integrity: "sha256:final789..."
---

# Sector Insights - RGPD-IA

## Cabinet Comptable (score moyen: 78)
- Pattern: 90% utilisent un chatbot sans mention RGPD
- Gap fréquent: pas de registre de traitement IA
- Prix acceptable: CHF 3'000-4'500 pour Starter
```

## COMPARAISON CONCURRENTIELLE

| Fonctionnalité | SocialPulse v4 | Apollo | ZoomInfo | Lusha | Demoable |
|----------------|---------------|--------|----------|-------|----------|
| Lead gen B2B | ✓ | ✓ | ✓ | ✓ | ✗ |
| Journal WORM | ✓ | ✗ | ✗ | ✗ | ✗ |
| Médiateur déterministe | ✓ | ✗ | ✗ | ✗ | ✗ |
| Arbitrage humain | ✓ | ✗ | ✗ | ✗ | ✗ |
| Guardrails LLM | ✓ | ✗ | ✗ | ✗ | ✗ |
| RGPD by design | ✓ | — | — | — | — |
| Serment agent | ✓ | ✗ | ✗ | ✗ | ✗ |
| Scraping anti-bot | ✓ (Scrapling) | ✗ | ✗ | ✗ | ✗ |
| Compilation connaissances | ✓ | ✗ | ✗ | ✗ | ✗ |
| Certifiable | ✓ | ✗ | ✗ | ✗ | ✗ |
| Prix | 500-5000€/mois | 49-119$/mois | 15k$/an | 37$/mois | 0-949$/mois |

**Notre positionnement:** Pas le moins cher. Le **seul conforme**. Pour les professions régulées, le prix est secondaire. La certitude légale est première.

## FICHIERS

```
socialpulse-lead-gen/
├── SKILL.md                    ← Ce fichier (v4.0)
├── campaign-template.yaml      ← Template vierge v4
├── campaigns/
│   └── cortex-leman-rgpd.yaml  ← Campagne active
├── compiled/                   ← Knowledge compilée
│   └── cortex-leman-rgpd/
├── journaux/                   ← Journaux WORM
│   └── cortex-leman-rgpd/
└── opt-out-list.json           ← Liste opt-out
```
