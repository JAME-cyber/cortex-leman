# Division du Travail — Tars vs OpenCode

> **Document de coordination inter-laptops.** Ce fichier vit dans le repo `cortex-leman`
> (syncé GitHub) pour être lisible depuis les deux machines. Il définit **qui fait quoi**
> pour ne pas gaspiller le travail structurel déjà effectué côté Tars.

**Date:** 2026-08-16
**Statut:** Actif — à mettre à jour à chaque nouveau projet

---

## 1. Principe fondateur

> **Tars produit le raisonnement. OpenCode produit le livrable visible.**

| | **Tars** (laptop tars — Hermes + Pi) | **OpenCode** (ce laptop) |
|---|---|---|
| **Domaine** | Structure, raisonnement, stratégie | Sites web, front, déploiement |
| **Produits** | Plans, audits, scoring, skills, pipelines, analyses | Pages, formulaires, dashboards, SEO, UX |
| **Force** | Avance structurelle (skills Cortex Leman, anti-sycophancie, 13 agents) | Exécution web directe, itération rapide, tests Playwright |
| **Stack** | Hermes Agent, Pi framework (v0.80.3), skills, SQLite | OpenCode, HTML/React/Vite, Playwright, n8n+GLM-4.5-flash |

**Règle d'or:** Un projet n'est jamais dupliqué. Chaque couche a un propriétaire unique.

---

## 2. Matrice des projets (qui fait quoi)

| Projet | Nature | Propriétaire STRUCTURE | Propriétaire WEB | Notes |
|---|---|---|---|---|
| **cortex-leman** | Système agentique + assets | 🔵 Tars | — | Skills, guardrails, anti-sycophancie, docs, vidéo Sankofa |
| **dropship-atom** | Pipeline agentic (7 agents) | 🔵 Tars | — | Scoring déterministe HUNTER→SCOUT→CREATOR — ne pas dupliquer |
| **compliance-skills** | 12 skills réglementaires | 🔵 Tars | — | RGPD, AI Act, secret professionnel |
| **alconst-website** | Site vitrine | — | 🟢 OpenCode | HTML, Cloudflare Pages, auto-deploy CI |
| **darkom-debarras** | Site métier | — | 🟢 OpenCode | React+TS+Vite, SEO/RGPD fait (07/07) |
| **idol-card-dreams** | App cards | — | 🟢 OpenCode | React+TS+Supabase, **stagnant depuis 03/03** → reprise prioritaire |
| **socialpulse-mvp** | Lead gen (7 agents) | 🔵 Tars | 🟢 OpenCode | Tars = agents Python + scoring ; OpenCode = pages HTML demo |
| **import-export-strategy** | Carte stratégique | 🔵 Tars | 🟢 OpenCode | Tars = stratégie multi-pays ; OpenCode = dashboard HTML |
| **12_agents** (D:\) | Pipeline n8n + GLM-4 | 🔵 Tars | 🟢 OpenCode | Structure du pipeline = Tars ; **couche d'exécution GLM-4.5-flash = active ici** |

---

## 3. Périmètre OpenCode (notre charge)

### 3.1 Sites vitrine / métier — maintenance + évolution
- **alconst-website** — évolutions : sections, formulaire, SEO
- **darkom-debarras** — évolutions : photos, zones, devis, RC Pro
- **idol-card-dreams** — **candidat n°1 reprise** (3 mois de stagnation)

### 3.2 Front des projets hybrides
- **socialpulse-mvp** : pages `demo/` + `annemasse-agency/` pendant que Tars gère les agents
- **import-export-strategy** : le dashboard multi-pays pendant que Tars affûte la stratégie

### 3.3 Couche d'exécution LLM
- **Pipeline n8n + GLM-4.5-flash** (12_agents) — génération de contenu réelle, validée (SWOT réel, HTTP 200)
- **Tests Playwright** — 22/22, config auto (webServer, retries CI)

---

## 4. Périmètre Tars (ne pas toucher)

- Skills Hermes Cortex Leman (Gardien des Normes, Narrateur, Oeil, Architecte)
- Anti-sycophancie (`anti_sycophancy.py`) et cost tracking (`hermes_cost_audit.py`)
- Scoring déterministe dropship-atom
- 12 skills compliance
- Tout raisonnement stratégique produit par Hermes/Pi sur tars

---

## 5. Interfaces entre les deux stacks

```
Tars (raisonnement)
    │  plans / audits / specs / scoring
    ▼
Cortex Leman repo (GitHub — point de sync)
    │  docs, briefs, decisions
    ▼
OpenCode (exécution web)
    │  pages, dashboards, formulaires, SEO
    ▼
Déploiement (Cloudflare Pages / Vercel)
```

**Pipeline de contenu (optionnel mais validé):**
```
n8n (13 agents) → GLM-4.5-flash → contenu structuré → alimente les sites OpenCode
```

---

## 6. Règles d'engagement

1. **Un propriétaire par couche** — si Tars a déjà un plan/audit/scoring pour un sujet, OpenCode l'utilise, ne le recrée pas.
2. **Le repo cortex-leman est le point de sync** — toute décision structurante y est documentée (lisible depuis les deux laptops).
3. **Demander avant de toucher** — un élément du périmètre Tars (skill, scoring, guardrail) ne se modifie pas sans accord.
4. **Preuve avant livraison** — OpenCode livre avec tests (Playwright) et evidence (logs, captures).
5. **Sécurité des clés** — jamais de clé API dans les repos publics (leçons apprises : clés ZAI/Kie exposées dans cortex-leman à révoquer).

---

## 7. Projets en attente / à cadrer

- [ ] Reprise **idol-card-dreams** (décision: relancer la partie front ?)
- [ ] Évolutions **alconst-website** (liste des sections à ajouter)
- [ ] Évolutions **darkom-debarras** (devis, photos, zones)
- [ ] Interface n8n→sites (brancher la génération GLM-4.5-flash sur un site réel)
- [ ] Révocation des clés API exposées (ZAI `c55159...`, Kie `00a891...`)

---

## 8. Historique

| Date | Événement |
|---|---|
| 2026-08-16 | Création du document — division Tars (structure) / OpenCode (web) actée |
