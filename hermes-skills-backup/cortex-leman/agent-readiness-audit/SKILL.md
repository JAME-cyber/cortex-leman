---
name: agent-readiness-audit
category: cortex-leman
version: 0.1.0
author: James (james-cortex), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
description: Audit how AI assistants represent a FR-CH SME online.
triggers:
  - "audit agent readiness"
  - "agent readiness"
  - "que dit l'ia de"
  - "agent-readiness"
  - "visibilité ia"
  - "ai seo"
  - "comment l'ia me voit"
metadata:
  hermes:
    tags: [agent-readiness, ai-seo, cortex-leman, ai-act, rgpd, audit, llms-txt, mcp]
    related_skills: [cortex-leman-compliance-agent, seo-local-audit, plan-pricing]
---

# Agent-Readiness Audit Skill

Diagnostique comment les assistants IA (ChatGPT, Gemini, Claude, Perplexity) **parlent d'une PME FR-CH** : est-elle visible ? recommandée ? ses faits (services, prix, lieu) sont-ils corrects ? Puis croise avec **AI Act art. 50 (transparence) + RGPD art. 5.1.d (exactitude)** — ce qui transforme un « AI-SEO » générique en **produit compliance**. C'est le moat Cortex Leman.

**Stance :** la vente = le screenshot (« voici ce que l'IA dit de vous »). Déterministe sur la collecte, Cortex Leman sur le jugement compliance. Produit cash-flow jour 1.

## When to Use
- « que dit l'IA de [entreprise] », « agent readiness », « visibilité IA », « AI SEO »
- Audit pré-vente Cortex Leman, ouoffre autonome « Agent-Readiness PME FR-CH »
- Avant/un avec `seo-local-audit` (celui-ci = couche IA, pas moteur de recherche classique)

**Don't use for:** SEO Google classique pur (→ `seo-local-audit`), audit RGPD code/data (→ `cortex-leman-compliance-agent`).

## Prerequisites
- Cible : nom entreprise + site + segment (ex. fiduciaire, cabinet médical, artisan)
- `web_search` (approximation de l'indexation IA)
- `cua-driver` MCP — **pilotage navigateur** pour interroger réellement ChatGPT/Gemini/Claude/Perplexity et capturer les réponses (vérifier les noms d'outils au runtime)
- `terminal` + `curl` pour parser le site cible

## Procédure

### Phase 1 — Snapshot de visibilité (= le moment de vente)
Pour la catégorie + zone de la cible, lance **15–20 prompts d'intention d'achat**. Jeu minimum :
1. « meilleur [métier] à [ville] » · 2. « recommande-moi [service] en Suisse romande » · 3. « compare [entreprise] à ses concurrents » · 4. « combien coûte [service] chez [entreprise] » · 5. « [entreprise] avis / fiable ? » · 6. « pour qui [entreprise] est-elle faite ? » · 7. « risques de choisir [entreprise] » · 8. « [entreprise] vs [concurrent] »

Sources, par fiabilité décroissante :
1. **`cua-driver`** → interroge ChatGPT, Gemini, Claude, Perplexity en navigateur, capture réponse + screenshot
2. **`web_search`** → approximation de ce qui est indexé/cité

Capture par prompt : **apparaît ? recommandé ? faits corrects (nom, services, prix, lieu) ?** ⏸ montrer le snapshot au client = tout le pitch.

### Phase 2 — Scorecard agent-readiness
Parse le site cible (`terminal` curl + `read_file`) et score chaque item 0–2 (total /20) :
- `/llms.txt` + `/llms-full.txt` présents et à jour
- `robots.txt` : règles crawlers IA explicites (allow/block)
- **Schema.org** : `LocalBusiness`/`Organization`/`Service`/`Product`/`FAQPage` valides
- **Page pricing parsable** (prix lisible machine) vs « contactez-nous »
- Docs / centre d'aide structuré
- Pages de comparaison honnêtes et spécifiques
- FAQ structurée autour des vraies questions acheteur
- Endpoint MCP / search API (si data-rich) — sinon N/A

### Phase 3 — Croisement compliance (LE MOAT)
Applique l'expertise Cortex Leman :
- **AI Act art. 50 (transparence)** : ce que l'IA dit de l'entreprise ne doit pas induire en erreur. Si l'info publique est **périmée/fausse** → exposition. Si l'entreprise **déploie de l'IA** → obligations transparence déployeur.
- **RGPD art. 5.1.d (exactitude)** : données business/personnelles dérivées d'un site stale = principe violé.
- Drapeau explicite chaque écart : `⚠ RISQUE CONFORMITÉ` + article + correctif.

Sans cette phase, l'audit = AI-SEO générique. C'est elle qui justifie le prix Cortex Leman.

### Phase 4 — Feuille de route de correction (priorisée)
- **Quick wins** : `llms.txt`, règles `robots.txt`, schema markup, parsabilité pricing
- **Moyen terme** : pages comparaison, pages use-case, FAQ structurée
- **Avancé** : serveur MCP / endpoint search (si data-rich)
Chaque item : effort (h/m/j) + **rationale compliance**.

### Phase 5 — Livrable (un doc)
```
# Audit Agent-Readiness — <Entreprise> (<date>)

## Score global : <n>/20   ·   Visibilité IA : <Apparaît/Recommandé/Absent>

## 1. Snapshot IA (captures + citations)
| Prompt | ChatGPT | Gemini | Claude | Perplexity | Faits corrects ? |

## 2. Scorecard technique (/20)
| Critère | Score | Preuve |

## 3. ⚠ Risques conformité (AI Act / RGPD)
| Risque | Article | Correctif |

## 4. Feuille de route (priorisée, chiffrée)
```

## Tarification cible (cf. offre + `plan-pricing`)
- Audit one-shot : **1 500–3 500 CHF**
- Correctifs : sur devis
- Loop mensuelle (re-mesure) : **290–590 CHF/mois**
- Wedge GTM : vendre **aussi** aux fiduciaires/agences qui servent les PME (revente)

## Pitfalls
1. **Se limiter à `web_search`.** C'est une approximation ; `cua-driver` donne la vraie réponse des IA.
2. **Sauter la Phase 3.** Sans compliance, c'est du AI-SEO commodity.
3. **Prompts trop génériques.** Toujours ancrer catégorie + zone FR-CH.
4. **Confondre indexation Google et réponse IA.** L'IA peut citer un site mal indexé Google si son contenu est propre/structuré.
5. **« Contactez-nous » comme pricing.** Punir au score : l'IA ne peut pas comparer.

## Vérification
- [ ] ≥ 15 prompts lancés sur ≥ 3 outils IA
- [ ] Scorecard complète (/20) avec preuve par item
- [ ] ≥ 1 risque compliance AI Act/RGPD explicité (ou « aucun » motivé)
- [ ] Feuille de route chiffrée livrée
- [ ] Snapshot montrable au client (le pitch)
