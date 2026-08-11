# Market Data Analysis — Analyse quantitative d'actifs

> Méthode réutilisable pour comparer des actifs cotés (BTC, ETH, indices, actions) sur des données **réelles et gratuites**.
> Sert au volet crypto (analyses d'allocation, réponse bare-URL) ET au fact-checking de claims chiffrés dans les clips finance.

## Sources de données (gratuites, pas de clé)

| Source | Endpoint | Limite | Usage |
|---|---|---|---|
| **Yahoo Finance** | `https://query1.finance.yahoo.com/v8/finance/chart/<TICKER>?period1=<s>&period2=<s>&interval=1mo` | Aucune (5y+ OK) | **PRÉFÉRER** pour historique >1 an |
| CoinGecko gratuit | `api.coingecko.com/api/v3/coins/<id>/market_chart?vs_currency=usd&days=N` | **365 jours max** | OK pour court terme, sinon KO |

**Tickers Yahoo courants** :
- `%5EGSPC` = S&P 500 (`^GSPC` URL-encodé)
- `%5EGSPC`, `%5EDJI` (Dow Jones), `%5EVIX` (volatilité)
- `BTC-USD`, `ETH-USD`, `SOL-USD` (crypto)
- Tickers actions : `OVH.PA` (OVHcloud Euronext Paris), `ASML.AS` (ASML Amsterdam), `SOI.PA` (Soitec)

**Paramètres** :
- `interval` : `1d` / `1wk` / `1mo`
- `period1`/`period2` : timestamps Unix en secondes
- `User-Agent` header requis (sinon 403)

## Métriques à calculer systématiquement

Pour une comparaison rigoureuse, produire les 5 :

| Métrique | Formule | Interprétation |
|---|---|---|
| **Rendement total** | `P_end / P_start - 1` | Gain brut sur la période |
| **CAGR** | `(P_end / P_start)^(1/years) - 1` | Rendement annualisé composé |
| **Max drawdown** | max de `(P_t / peak_t - 1)` | Pire chute depuis un sommet |
| **Vol annualisée** | `stdev(log_returns_monthly) * sqrt(12)` | Risque (16% = actions, 50%+ = crypto) |
| **Sharpe (rf=4%)** | `(CAGR - 4) / vol` | Rendement ajusté du risque ; <0.5 = médiocre |

Optionnel mais puissant :
- **Corrélation** entre actifs (`statistics.correlation`) — diversification
- **Simulation portfolio rebalanced** (ex: 95% GSPC + 5% BTC) — démontre l'effet d'allocation

## Script de référence réutilisable

Toujours écrire dans un fichier `/tmp/<name>.py` (pas inline `python3 -c`) : les f-strings avec accolades cassent en inline, et c'est plus maintenable.

**Pattern** (voir `/tmp/compare.py` session 2026-07-18 pour référence) :
1. Fetch les deux séries via `curl` → fichiers JSON `/tmp/*.json`
2. Parse en dicts `{YYYY-MM: close}`
3. Aligne sur mois communs (`sorted(set(a) & set(b))`)
4. Calcule les 5 métriques + drawdown date + corrélation
5. Simule un portfolio rebalanced si pertinent
6. Affiche : tableau annuel YoY + tableau métriques + verdict 1 ligne

## Biais à éviter (sources d'erreur)

1. **Fenêtre de départ** : BTC acheté au sommet 2021 ≠ BTC acheté au creux 2018. Toujours préciser la fenêtre. Un actif cyclique (crypto, semi-conducteurs) a des performances radicalement différentes selon le point d'entrée.
2. **Confusion métrique** : installed base ≠ revenue ≠ unit shipments (cf. leçon ASML/TSMC). Toujours préciser ce qu'on mesure.
3. **Survivor bias** : comparer BTC (survivant) à 23000 cryptos mortes n'est pas représentatif.
4. **Corrélation != causalité** : BTC et S&P500 corrélés à 0.52 en bull market, peut diverger en bear market.
5. **Rate limit** : CoinGecko gratuit bloque à 365j, Yahoo pas de limite observée.

## Format de réponse pour analyse bare-URL crypto

Quand Thierry envoie un tweet/article crypto et demande analyse :

1. **Fetch le contenu** (vxtwitter pour X, rag_web_browser pour articles)
2. **Identifie les claims chiffrés** → si non sourcés, le dire
3. **Si comparaison d'actifs** : lancer le script market-data, produire tableau + verdict
4. **Pas de conseil en investissement** (le guardrail AMF s'applique aussi au volet crypto — reformuler en "dépend de l'horizon/profil")
5. **Insight final** : 1 conclusion honnête, même si elle contredit le narratif viral

Exemple validé (2026-07-18) : Raoul Pal tweete "never sell, accumulate crypto" → analyse BTC vs S&P500 5y montre BTC a sous-performé (CAGR 6.5% vs 10.5%) avec vol 3x supérieure. Mais 5% BTC dans un portefeuille 95% S&P500 améliore légèrement le rendement sans casser le drawdown. Conclusion : Pal a tort sur la conclusion (100% crypto), raison sur le principe (1-5% DCA).

## Outils utilisés

- `terminal` : `curl` pour fetch Yahoo/CoinGecko, `python3 /tmp/compare.py` pour les calculs
- `write_file` : script Python (`/tmp/compare.py`) — ne PAS inline `python3 -c` (f-strings cassent)
- Pas de pandas/numpy requis : `math` + `statistics` stdlib suffisent
