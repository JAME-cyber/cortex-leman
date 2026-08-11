---
campaign: haute-savoie-74-agents-ia
batch: 001
date: 2026-07-01
status: discovery-complete
cost_usd: 1.80
---

# Haute-Savoie 74 — Batch 001 Discovery Results

## Campaign Config

- **YAML**: `templates/socialpulse/campaigns/haute-savoie-74-agents-ia.yaml`
- **Vertical**: Agents IA BTP/Services (speed-to-lead + quoting agents)
- **Target**: PME 5-200 employés, 18 villes du 74
- **8 secteurs**: Plombier/Chauffagiste, Électricien/Solaire, Rénovation énergétique, Garage auto, Paysagiste/Pisciniste, Immobilier/Syndic, Services à domicile, Hôtellerie/Restauration
- **Scoring threshold**: 55 (plus bas que campagne RGPD-IA car TPE ciblées)

## Batch 001 Stats

| Metric | Value |
|--------|-------|
| Total leads | 33 |
| Qualified (≥55) | 33 |
| With website | 32 |
| Plombier/Chauffagiste | 23 |
| Électricien/Solaire | 10 |
| Cost (Apify) | ~$1.80 |

## Apify Queries Used

| Query | Location | Results | Dataset ID |
|-------|----------|---------|------------|
| plombier chauffagiste | Annecy, Haute-Savoie | 15 | v0CODvJl4Co6eGoAD |
| electricien solaire | Annecy, Haute-Savoie | 12 | WZdBoVy40fEMqKuRm |
| plombier chauffagiste | Annemasse, Haute-Savoie | 9 | Em1a0rGJ3usZcCLCd |

## Top 10 Leads (by score)

| Score | Name | Sector | City | Website |
|-------|------|--------|------|---------|
| 92.5 | Gauthier Plomberie | Plombier/Chauffagiste | Annecy | gauthierplomberie.fr |
| 92.5 | C.S.P Chauffage | Plombier/Chauffagiste | Annecy | cspchauffage.fr |
| 92.5 | Savoie Plomberie (SPC) | Plombier/Chauffagiste | Annecy | annecyplomberiechauffage.fr |
| 92.5 | Plombier Martin 74 | Plombier/Chauffagiste | Annecy | plombiermartin.fr |
| 92.5 | BRIGNON CHAUFFAGE | Plombier/Chauffagiste | Annecy | brignon-chauffage.fr |
| 92.5 | Lissi Energie | Plombier/Chauffagiste | Annecy | lissi-energie.fr |
| 92.5 | GMM | Plombier/Chauffagiste | Annecy | gmm74.com |
| 91.8 | JHS PLOMBERIE CHAUFFAGE | Plombier/Chauffagiste | Annemasse | jhsplomberiechauffage.com |
| 91.8 | DEPANNAGE PLOMBIER 74 | Plombier/Chauffagiste | Annemasse | depannageplombier74.fr |
| 90.8 | Annecy Solaire Clim Chauffage | Électricien/Solaire | Annecy | solaireclimchauffage.fr |

## Scoring Proxy (no employee count from GMB)

| Reviews | Proxy Employee Bracket | Score |
|---------|----------------------|-------|
| >200 | PME 50+ | 70 |
| 50-200 | Sweet spot PME | 100 |
| <50 | TPE | 80 |

## Excluded

- **Garanka Annemasse** (1.8★, 311 reviews) — bad reputation, not a premium lead
- **Las Photovoltaïque** — Saint-Jorioz, borderline 74
- **AEGIS ELECTRICITE** — no website

## Output Files

- Leads JSON: `~/socialpulse-output/haute-savoie-74-agents-ia/leads-batch-001.json`
- Journal WORM: `~/socialpulse-output/haute-savoie-74-agents-ia/journaux/batch-2026-07-01-001.json`
- Campaign YAML: `~/.hermes/skills/cortex-leman-business-generator/templates/socialpulse/campaigns/haute-savoie-74-agents-ia.yaml`

## Next Steps (not yet done)

1. Enrichment: site_analysis sur top 10 (chatbot, formulaire devis, RGPD banner)
2. Personnalisation: emails via OpenRouter
3. Extension: garages auto, paysagistes, immobiliers 74
