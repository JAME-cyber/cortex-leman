# Workaround paywall DigiTimes

DigiTimes premium paywall bloque l'accès au corps des articles (~70% des URLs `digitimes.com/news/a*`). `fetch_source.py` retourne `status: 200` mais seul `title` + `meta_description` + 1-2 paragraphes d'intro sont extraits. Cela fait chuter Axe 2 (Densité chiffrée) à 0/2 au scoring scout et empêche tout fact-checking.

## Indicateurs de paywall confirmé

Dans le HTML cache (`~/crypto-project/research_cache/<hash>.json`) :

- `<div id="article-lock-inline">` présent
- Moins de 3 paragraphes `<p class="p1">` extraits
- `meta_description` tronquée par `...`
- Le corps `html` contient `Subscribe` / `Premium content` / `To continue reading`

## Stratégie de contournement (validée 2026-07-19, clip Trumpf)

L'article DigiTimes reste la **source du signal** (il donne l'angle et les acteurs), mais les **chiffres sourcés** doivent venir de sources ouvertes complémentaires.

### Étape 1 — Extraire les mots-clés du signal

Depuis `title` + `meta_description` (disponibles même paywallés) :
- Acteurs principaux (ex: "Trumpf", "ASML")
- Sujet (ex: "EUV laser", "Chinese competition")
- Dates / lieux (ex: "2026", "Dongguan")

### Étape 2 — Recherche via Apify rag_web_browser

`web_search` (Hermes built-in) nécessite Firecrawl configuré — souvent absent. Utiliser l'Actor Apify `apify/rag-web-browser` à la place via MCP :

```
mcp__apify__apify__rag_web_browser(query="<mots-clés>", maxResults=4)
```

Puis récupérer le contenu markdown :

```
mcp__apify__get_dataset_items(datasetId="<id>", fields="searchResult.title,searchResult.url,markdown", limit=3)
```

### Étape 3 — Sources ouvertes typiques (par sujet semi-conducteurs)

| Source | Type | Fiable pour |
|---|---|---|
| Sites corporate (`trumpf.com`, `asml.com`) | Communiqués presse | Chiffres officiels, dates, awards |
| EEJournal, TechPowerUp, AnandTech | Presse tech spécialisée | Specs techniques, contextes |
| Asia Times, Reuters, Nikkei Asia | Presse générale géo-stratégique | Analyses concurrence chinoise |
| SEC EDGAR, archives Euronext | Régulateur | Données financières cotées |

### Étape 4 — Scoring avec sources enrichies

Une fois 3-4 sources ouvertes récupérées :
- Re-scorer Axe 2 (Densité chiffrée) sur les **sources ouvertes**, pas sur DigiTimes
- Citer DigiTimes comme source du *signal*, les sources ouvertes comme sources des *chiffres*
- Le disclaimer AMF reste obligatoire si une valeur cotée est mentionnée

## Exemple concret (Trumpf, 2026-07-19)

Signal : `DigiTimes a20260717PD207` ("Trumpf recalibrates strategy as Chinese competition heats up")
- Paywall → Axe 2 = 0/2 initial
- Enrichissement Apify → trumpf.com press release (Supplier Award oct 2025, specs laser 450k pièces / 20t), EEJournal (CA 4,3 Md€, 18 300 employés), TechPowerUp (EUV LDP Huawei Dongguan)
- Re-scoring → Axe 2 = 2/2, score total 7/10 → GO
- Clip produit : `clip_trumpf_maillon_invisible.mp4`

## Limite

Si aucune source ouverte ne confirme les chiffres clés du signal, le score reste bas et le verdict doit être BORDERLINE ou NO-GO. Ne jamais inventer ou extrapoler des chiffres pour compenser le paywall.
